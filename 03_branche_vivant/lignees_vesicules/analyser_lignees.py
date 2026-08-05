from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "donnees_externes/vesicules_sokolskyi_baum_2026/extracted"
OUT = HERE / "resultats"
ARMS = (("drdata", "drcode", "drift"), ("seldata", "selcode", "selection"))
WELL_RE = re.compile(r"\b([A-H](?:1[0-2]|[1-9]))\b", re.IGNORECASE)


def locate(name: str) -> Path | None:
    matches = sorted(DATA.rglob(name))
    return matches[0] if matches else None


def well_labels(count: int) -> list[str]:
    canonical = [f"{row}{column}" for row in "ABCDEFGH" for column in range(1, 13)]
    return canonical[:count]


def numeric_matrix(path: Path, sheet: str) -> pd.DataFrame:
    raw = pd.read_excel(path, sheet_name=sheet, header=None)
    numeric = raw.apply(pd.to_numeric, errors="coerce")
    numeric = numeric.dropna(axis=0, how="all").dropna(axis=1, how="all")
    numeric.index = well_labels(len(numeric))
    numeric.columns = [f"g{index}" for index in range(numeric.shape[1])]
    return numeric


def code_matrix(path: Path, sheet: str, rows: int, columns: int) -> pd.DataFrame:
    raw = pd.read_excel(path, sheet_name=sheet, header=None, dtype=str)
    raw = raw.dropna(axis=0, how="all").dropna(axis=1, how="all")
    raw = raw.iloc[:rows, : max(columns, 1)].copy()
    raw.index = well_labels(len(raw))
    raw.columns = [f"c{index}" for index in range(raw.shape[1])]
    return raw


def tokens(value: object) -> list[str]:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return []
    return [match.upper() for match in WELL_RE.findall(str(value))]


def map_transfer(
    code: pd.DataFrame,
    transition: int,
    recipient_labels: list[str],
) -> list[tuple[str, str]]:
    """Reconstruit donor-recipient en acceptant les formats Dryad courants.

    Une cellule avec un seul puits est lue comme donneur pour le puits de sa ligne.
    Une cellule avec deux puits est lue comme donneur puis receveur. Les colonnes
    peuvent coder soit chaque transition, soit les paires donor/recipient.
    """
    candidate_columns: list[int] = []
    for value in (transition, transition + 1, 2 * transition, 2 * transition + 1):
        if 0 <= value < code.shape[1] and value not in candidate_columns:
            candidate_columns.append(value)
    mappings: list[tuple[str, str]] = []
    for column in candidate_columns:
        current: list[tuple[str, str]] = []
        for row_index, recipient_default in enumerate(recipient_labels[: len(code)]):
            found = tokens(code.iat[row_index, column])
            if len(found) >= 2:
                current.append((found[0], found[1]))
            elif len(found) == 1:
                current.append((found[0], recipient_default))
        if len(current) >= 8:
            mappings = current
            break
    return mappings


def pairs(path: Path, condition: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for data_sheet, code_sheet, arm in ARMS:
        data = numeric_matrix(path, data_sheet)
        code = code_matrix(path, code_sheet, len(data), data.shape[1])
        labels = list(data.index)
        for transition in range(data.shape[1] - 1):
            mappings = map_transfer(code, transition, labels)
            mapping_mode = "coded_lineage"
            if not mappings:
                mappings = [(label, label) for label in labels]
                mapping_mode = "same_well_fallback"
            for donor, recipient in mappings:
                if donor not in data.index or recipient not in data.index:
                    continue
                parent = data.iloc[data.index.get_loc(donor), transition]
                offspring = data.iloc[data.index.get_loc(recipient), transition + 1]
                if pd.isna(parent) or pd.isna(offspring):
                    continue
                rows.append(
                    {
                        "condition": condition,
                        "arm": arm,
                        "transition": transition,
                        "donor": donor,
                        "recipient": recipient,
                        "parent": float(parent),
                        "offspring": float(offspring),
                        "mapping_mode": mapping_mode,
                    }
                )
    return pd.DataFrame(rows)


def lineage_permutation_test(data: pd.DataFrame, repeats: int = 2000) -> dict[str, float]:
    rng = np.random.default_rng(20260805)
    observed = float(data["parent"].corr(data["offspring"]))
    null_values: list[float] = []
    for _ in range(repeats):
        shuffled = data.copy()
        shuffled["offspring"] = shuffled.groupby(
            ["condition", "arm", "transition"], observed=False
        )["offspring"].transform(lambda values: rng.permutation(values.to_numpy()))
        value = shuffled["parent"].corr(shuffled["offspring"])
        if pd.notna(value):
            null_values.append(float(value))
    p_value = (1 + sum(value >= observed for value in null_values)) / (1 + len(null_values))
    return {
        "observed_parent_offspring_r": observed,
        "null_mean_r": float(np.mean(null_values)),
        "permutation_p_one_sided": float(p_value),
        "permutations": len(null_values),
    }


def main() -> dict[str, object]:
    files = {
        condition: [path for replicate in (1, 2, 3) if (path := locate(f"{condition}{replicate}_log.xlsx"))]
        for condition in ("FR", "FU", "UR", "UU")
    }
    missing = [condition for condition, paths in files.items() if len(paths) < 3]
    if missing:
        result = {
            "status": "waiting_for_external_data",
            "missing_complete_replicate_sets": missing,
            "found_files": {condition: [str(path) for path in paths] for condition, paths in files.items()},
        }
    else:
        frames = [pairs(path, condition) for condition, paths in files.items() for path in paths]
        data = pd.concat(frames, ignore_index=True)
        if data.empty:
            raise ValueError("aucune paire parent-descendant extraite")
        stats: dict[str, dict[str, object]] = {}
        for (condition, arm), group in data.groupby(["condition", "arm"], observed=False):
            stats[f"{condition}_{arm}"] = {
                "n": int(len(group)),
                "parent_offspring_r": float(group["parent"].corr(group["offspring"])),
                "offspring_mean": float(group["offspring"].mean()),
                "coded_lineage_fraction": float((group["mapping_mode"] == "coded_lineage").mean()),
            }
        selection_response = {
            condition: stats[f"{condition}_selection"]["offspring_mean"]
            - stats[f"{condition}_drift"]["offspring_mean"]
            for condition in ("FR", "FU", "UR", "UU")
        }
        ablation_controls = [selection_response[key] for key in ("FU", "UR", "UU")]
        mechanism_contrast = float(selection_response["FR"] - np.mean(ablation_controls))
        lineage_test = lineage_permutation_test(data)
        result = {
            "status": "analysed",
            "pairs": int(len(data)),
            "stats": stats,
            "selection_response": selection_response,
            "mechanism_ablation_contrast": mechanism_contrast,
            "lineage_permutation_test": lineage_test,
            "decision_components": {
                "selection_response_FR_positive": selection_response["FR"] > 0,
                "FR_exceeds_ablation_mean": mechanism_contrast > 0,
                "lineage_signal_above_permuted": lineage_test["permutation_p_one_sided"] < 0.05,
                "coded_lineage_majority": float((data["mapping_mode"] == "coded_lineage").mean()) > 0.5,
            },
            "interpretation": (
                "La réponse à la sélection, la filiation et l'ablation sont testées séparément. "
                "Un succès global exige les quatre composantes, sans confondre moyenne de population "
                "et transmission parent-descendant."
            ),
        }
        result["global_verdict"] = (
            "all_pre_registered_components_supported"
            if all(result["decision_components"].values())
            else "one_or_more_components_not_supported"
        )
    OUT.mkdir(exist_ok=True)
    (OUT / "RESULTAT.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


if __name__ == "__main__":
    main()
