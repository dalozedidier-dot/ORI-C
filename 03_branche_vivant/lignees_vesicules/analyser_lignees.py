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
GEN_RE = re.compile(r"G(\d+)", re.IGNORECASE)
CANONICAL_WELLS = [f"{row}{column}" for row in "ABCDEFGH" for column in range(1, 13)]


def locate(name: str) -> Path | None:
    matches = sorted(DATA.rglob(name))
    return matches[0] if matches else None


def well_labels(count: int) -> list[str]:
    return CANONICAL_WELLS[:count]


def normalized_well(value: object) -> str | None:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    text = str(value).strip().upper().rstrip("'")
    return text if text in CANONICAL_WELLS else None


def header_generation(value: object, arm_letter: str) -> int | None:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    text = re.sub(r"\s+", "", str(value).upper())
    if "PM" in text or "-F" in text or not text.endswith(arm_letter):
        return None
    matches = GEN_RE.findall(text)
    return int(matches[-1]) if matches else None


def _first_plate_rows(raw: pd.DataFrame) -> tuple[pd.DataFrame, list[str]] | None:
    """Retourne le premier bloc A1-H12, sans les blocs de calcul ajoutés plus bas."""
    if raw.shape[1] == 0:
        return None
    first_position: dict[str, int] = {}
    for position, value in enumerate(raw.iloc[:, 0]):
        label = normalized_well(value)
        if label is not None and label not in first_position:
            first_position[label] = position
    if not all(label in first_position for label in CANONICAL_WELLS):
        return None
    positions = [first_position[label] for label in CANONICAL_WELLS]
    return raw.iloc[positions].copy(), CANONICAL_WELLS.copy()


def _infer_missing_generation_columns(
    raw: pd.DataFrame,
    plate: pd.DataFrame,
    recognized: dict[int, int],
) -> dict[int, int]:
    """Complète les rares en-têtes absents à partir de la continuité de la plaque.

    Le fichier UR3 contient notamment une colonne G8 non étiquetée. L'inférence
    reste limitée aux générations encadrées par deux générations explicitement
    nommées et aux colonnes numériques remplies pour la plaque entière.
    """
    if len(recognized) < 2:
        return recognized
    result = dict(recognized)
    minimum, maximum = min(result), max(result)
    numeric_density: dict[int, int] = {
        column: int(pd.to_numeric(plate.iloc[:, column], errors="coerce").notna().sum())
        for column in range(1, raw.shape[1])
    }
    for generation in range(minimum, maximum + 1):
        if generation in result:
            continue
        previous = max((value for value in result if value < generation), default=None)
        following = min((value for value in result if value > generation), default=None)
        if previous is None or following is None:
            continue
        left, right = result[previous], result[following]
        expected = left + (right - left) * (generation - previous) / (following - previous)
        candidates = [
            column
            for column in range(left + 1, right)
            if column not in result.values() and numeric_density.get(column, 0) >= 90
        ]
        if candidates:
            result[generation] = min(candidates, key=lambda column: abs(column - expected))
    return result


def numeric_matrix(path: Path, sheet: str) -> pd.DataFrame:
    raw = pd.read_excel(path, sheet_name=sheet, header=None, dtype=object)
    plate_result = _first_plate_rows(raw)

    if plate_result is None:
        # Petit format synthétique utilisé par les tests unitaires.
        numeric = raw.apply(pd.to_numeric, errors="coerce")
        numeric = numeric.dropna(axis=0, how="all").dropna(axis=1, how="all")
        if len(numeric) > len(CANONICAL_WELLS):
            numeric = numeric.iloc[: len(CANONICAL_WELLS)]
        numeric.index = well_labels(len(numeric))
        numeric.columns = [f"g{index}" for index in range(numeric.shape[1])]
        return numeric

    plate, labels = plate_result
    arm_letter = "D" if sheet.lower().startswith("dr") else "S"
    headers = raw.iloc[0].tolist() if len(raw) else []
    recognized: dict[int, int] = {}
    for column in range(1, raw.shape[1]):
        generation = header_generation(headers[column] if column < len(headers) else None, arm_letter)
        if generation is not None and generation not in recognized:
            recognized[generation] = column

    if recognized:
        recognized = _infer_missing_generation_columns(raw, plate, recognized)
        selected = sorted(recognized.items())
    else:
        # FU2 et FU3 n'ont aucun en-tête, mais leurs colonnes sont déjà dans
        # l'ordre générationnel après la colonne des puits.
        numeric_columns = [
            column
            for column in range(1, raw.shape[1])
            if pd.to_numeric(plate.iloc[:, column], errors="coerce").notna().sum() >= 90
        ]
        selected = list(enumerate(numeric_columns))

    if len(selected) < 2:
        raise ValueError(f"moins de deux générations exploitables dans {path.name}:{sheet}")

    values = pd.DataFrame(
        {
            f"g{generation}": pd.to_numeric(plate.iloc[:, column], errors="coerce").to_numpy()
            for generation, column in selected
        },
        index=labels,
    )
    values = values.dropna(axis=1, how="all")
    if values.shape[1] < 2:
        raise ValueError(f"moins de deux générations numériques dans {path.name}:{sheet}")
    return values


def code_matrix(path: Path, sheet: str) -> pd.DataFrame:
    raw = pd.read_excel(path, sheet_name=sheet, header=None, dtype=object)
    raw = raw.dropna(axis=0, how="all").dropna(axis=1, how="all")
    if raw.empty:
        return raw

    first_row = raw.iloc[0].tolist()
    has_generation_header = any(GEN_RE.search(str(value)) for value in first_row if pd.notna(value))
    if has_generation_header:
        headers = [str(value) if pd.notna(value) else "" for value in first_row]
        data = raw.iloc[1:].reset_index(drop=True).copy()
    else:
        headers = [""] * raw.shape[1]
        data = raw.reset_index(drop=True).copy()
    data.columns = [f"c{index}" for index in range(data.shape[1])]
    data.attrs["generation_headers"] = headers
    return data


def tokens(value: object) -> list[str]:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return []
    return [match.upper() for match in WELL_RE.findall(str(value))]


def _code_generation(value: object) -> int | None:
    matches = GEN_RE.findall(str(value)) if value is not None else []
    return int(matches[-1]) if matches else None


def map_transfer(
    code: pd.DataFrame,
    offspring_generation: int,
    recipient_labels: list[str],
) -> list[tuple[str, str]]:
    """Reconstruit les couples donneur-receveur d'une génération à la suivante.

    Dans les fichiers Dryad réels, chaque génération possède une colonne de
    puits sélectionnés et une colonne contenant les couples explicites. La
    colonne de couples est prioritaire. Les formats simplifiés à un seul puits
    par cellule restent acceptés pour les tests et les anciens fichiers.
    """
    if code.empty:
        return []

    headers = code.attrs.get("generation_headers", [])
    candidate_columns = [
        index for index, header in enumerate(headers) if _code_generation(header) == offspring_generation
    ]
    if not candidate_columns:
        transition = max(offspring_generation - 1, 0)
        for value in (2 * transition + 1, transition + 1, 2 * transition, transition):
            if 0 <= value < code.shape[1] and value not in candidate_columns:
                candidate_columns.append(value)

    def candidate_score(column: int) -> tuple[int, int]:
        counts = [len(tokens(value)) for value in code.iloc[:, column]]
        return sum(count >= 2 for count in counts), sum(count >= 1 for count in counts)

    candidate_columns.sort(key=candidate_score, reverse=True)
    for column in candidate_columns:
        current: list[tuple[str, str]] = []
        for row_index in range(len(code)):
            found = tokens(code.iat[row_index, column])
            if len(found) >= 2:
                current.append((found[0], found[1]))
            elif len(found) == 1 and row_index < len(recipient_labels):
                current.append((found[0], recipient_labels[row_index]))
        if len(current) >= 8:
            return current
    return []


def _generation(column: object) -> int:
    match = re.fullmatch(r"g(\d+)", str(column))
    if match is None:
        raise ValueError(f"colonne générationnelle invalide: {column}")
    return int(match.group(1))


def pairs(path: Path, condition: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for data_sheet, code_sheet, arm in ARMS:
        data = numeric_matrix(path, data_sheet)
        code = code_matrix(path, code_sheet)
        labels = list(data.index)
        columns = list(data.columns)
        for left_column, right_column in zip(columns, columns[1:]):
            parent_generation = _generation(left_column)
            offspring_generation = _generation(right_column)
            if offspring_generation != parent_generation + 1:
                # Une génération absente ne peut pas être transformée en filiation directe.
                continue
            mappings = map_transfer(code, offspring_generation, labels)
            mapping_mode = "coded_lineage"
            if not mappings:
                mappings = [(label, label) for label in labels]
                mapping_mode = "same_well_fallback"
            for donor, recipient in mappings:
                if donor not in data.index or recipient not in data.index:
                    continue
                parent = data.at[donor, left_column]
                offspring = data.at[recipient, right_column]
                if pd.isna(parent) or pd.isna(offspring):
                    continue
                rows.append(
                    {
                        "condition": condition,
                        "arm": arm,
                        "transition": parent_generation,
                        "donor": donor,
                        "recipient": recipient,
                        "parent": float(parent),
                        "offspring": float(offspring),
                        "mapping_mode": mapping_mode,
                    }
                )
    return pd.DataFrame(rows)


def lineage_permutation_test(data: pd.DataFrame, repeats: int = 2000) -> dict[str, float]:
    """Permute la descendance dans chaque condition, bras et transition.

    Le calcul est identique à la version par ``groupby.transform``, mais évite
    de recopier les 11 000 lignes et de reconstruire les groupes 2 000 fois.
    """
    rng = np.random.default_rng(20260805)
    valid = data[["parent", "offspring"]].notna().all(axis=1).to_numpy()
    parent = data.loc[valid, "parent"].to_numpy(dtype=float)
    offspring = data.loc[valid, "offspring"].to_numpy(dtype=float)
    groups_frame = data.loc[valid, ["condition", "arm", "transition"]].reset_index(drop=True)
    group_indices = [
        group.index.to_numpy(dtype=int)
        for _, group in groups_frame.groupby(["condition", "arm", "transition"], observed=False, sort=False)
    ]
    observed = float(np.corrcoef(parent, offspring)[0, 1])
    null_values = np.empty(repeats, dtype=float)
    for repeat in range(repeats):
        shuffled = offspring.copy()
        for indices in group_indices:
            shuffled[indices] = rng.permutation(offspring[indices])
        null_values[repeat] = float(np.corrcoef(parent, shuffled)[0, 1])
    finite = null_values[np.isfinite(null_values)]
    p_value = (1 + int(np.sum(finite >= observed))) / (1 + len(finite))
    return {
        "observed_parent_offspring_r": observed,
        "null_mean_r": float(np.mean(finite)),
        "permutation_p_one_sided": float(p_value),
        "permutations": int(len(finite)),
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
