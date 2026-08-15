"""Petrungaro 2026 : phenotype initial, fond genetique et futurs evolutifs.

Toutes les observations viennent des tableaux sources publies. Les
permutations ne creent qu'une distribution nulle et ne remplacent jamais une
observation scientifique.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCES = ROOT / "donnees_externes/petrungaro_2026"
ARCHIVE = SOURCES / "41467_2026_76025_MOESM7_ESM.zip"
MUTATIONS = SOURCES / "41467_2026_76025_MOESM3_ESM.csv"
OUT = HERE / "resultats"
SEED = 20260815
N_BOOT = 5000
N_PERM = 499


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def source_workbook() -> Path:
    with zipfile.ZipFile(ARCHIVE) as archive:
        name = next(n for n in archive.namelist() if n.endswith("SourceData_MainFigures.xlsx"))
        target = Path(tempfile.gettempdir()) / "oric_petrungaro_main_figures.xlsx"
        target.write_bytes(archive.read(name))
    return target


def populations(workbook: Path) -> pd.DataFrame:
    frame = pd.read_excel(workbook, sheet_name="Fig2a_violin")
    frame = frame.rename(columns={"strain": "genetic_background", "ab": "antibiotic", "time[h]_final": "final_time_h"})
    keep = ["genetic_background", "antibiotic", "plate", "well", "final_time_h", "IC50", "fold_increase"]
    frame = frame[keep].dropna().copy()
    frame["population_id"] = frame.antibiotic.astype(str) + "_" + frame.plate.astype(str) + "_" + frame.well.astype(str)
    frame["initial_IC50"] = frame.IC50.astype(float) / frame.fold_increase.astype(float)
    frame["initial_log10_IC50"] = np.log10(frame.initial_IC50)
    frame["future_log10_IC50"] = np.log10(frame.IC50.astype(float))
    frame["resistance_change_log10"] = frame.future_log10_IC50 - frame.initial_log10_IC50
    if frame.population_id.duplicated().any():
        raise ValueError("population_id non unique dans Fig2a_violin")
    return frame.sort_values(["antibiotic", "genetic_background", "plate", "well"]).reset_index(drop=True)


def design(train: pd.DataFrame, test: pd.DataFrame, include_background: bool) -> tuple[np.ndarray, np.ndarray]:
    mean = float(train.initial_log10_IC50.mean())
    scale = float(train.initial_log10_IC50.std(ddof=0)) or 1.0
    a = [np.ones((len(train), 1)), ((train[["initial_log10_IC50"]].to_numpy() - mean) / scale)]
    b = [np.ones((len(test), 1)), ((test[["initial_log10_IC50"]].to_numpy() - mean) / scale)]
    if include_background:
        levels = sorted(train.genetic_background.astype(str).unique())
        a.append(np.column_stack([(train.genetic_background.astype(str) == level).to_numpy(float) for level in levels]))
        b.append(np.column_stack([(test.genetic_background.astype(str) == level).to_numpy(float) for level in levels]))
    return np.column_stack(a), np.column_stack(b)


def folds(frame: pd.DataFrame) -> np.ndarray:
    # Repetitions d'un meme fond reparties entre trois plis.
    return frame.groupby("genetic_background", sort=True).cumcount().to_numpy() % 3


def predict(frame: pd.DataFrame, include_background: bool, split: np.ndarray | None = None) -> np.ndarray:
    y = frame.future_log10_IC50.to_numpy(float)
    if split is None:
        split = folds(frame)
    result = np.empty(len(frame))
    for fold in range(3):
        mask = split == fold
        train, test = frame.loc[~mask], frame.loc[mask]
        x_train, x_test = design(train, test, include_background)
        penalty = np.eye(x_train.shape[1])
        penalty[0, 0] = 0
        beta = np.linalg.solve(x_train.T @ x_train + penalty, x_train.T @ y[~mask])
        result[mask] = x_test @ beta
    return result


def performance(frame: pd.DataFrame, rng: np.random.Generator) -> dict[str, object]:
    y = frame.future_log10_IC50.to_numpy(float)
    split = folds(frame)
    px = predict(frame, False, split)
    pxm = predict(frame, True, split)
    rmse_x = float(np.sqrt(np.mean((y - px) ** 2)))
    rmse_xm = float(np.sqrt(np.mean((y - pxm) ** 2)))
    gain = 100 * (rmse_x - rmse_xm) / rmse_x
    boot = []
    for _ in range(N_BOOT):
        idx = rng.integers(0, len(frame), len(frame))
        ax = np.sqrt(np.mean((y[idx] - px[idx]) ** 2))
        axm = np.sqrt(np.mean((y[idx] - pxm[idx]) ** 2))
        boot.append(100 * (ax - axm) / ax)
    null = []
    bins = pd.qcut(frame.initial_log10_IC50, q=min(5, frame.initial_log10_IC50.nunique()), duplicates="drop")
    groups = frame.groupby(bins, observed=True).indices
    for _ in range(N_PERM):
        shuffled = frame.copy()
        for indices in groups.values():
            values = shuffled.iloc[indices].genetic_background.to_numpy(copy=True)
            rng.shuffle(values)
            shuffled.iloc[indices, shuffled.columns.get_loc("genetic_background")] = values
        # Le plan de validation reste exactement celui du test observé. Le
        # recalculer après permutation changerait simultanément les plis et m.
        pp = predict(shuffled, True, split)
        null_rmse = np.sqrt(np.mean((y - pp) ** 2))
        null.append(100 * (rmse_x - null_rmse) / rmse_x)
    return {
        "n_populations": len(frame),
        "n_genetic_backgrounds": int(frame.genetic_background.nunique()),
        "rmse_X_log10_IC50": rmse_x,
        "rmse_X_plus_m_log10_IC50": rmse_xm,
        "relative_gain_percent": gain,
        "bootstrap_gain_q025_percent": float(np.quantile(boot, 0.025)),
        "bootstrap_gain_q975_percent": float(np.quantile(boot, 0.975)),
        "background_permutation_p_one_sided": float((1 + np.sum(np.asarray(null) >= gain)) / (N_PERM + 1)),
    }


def temporal_trajectories(workbook: Path) -> pd.DataFrame:
    raw = pd.read_excel(workbook, sheet_name="Fig4bcd", header=None)
    records: list[dict[str, object]] = []
    for col in range(1, raw.shape[1] - 1, 2):
        antibiotic = raw.iat[0, col]
        background = raw.iat[1, col]
        time_header = str(raw.iat[2, col])
        value_header = str(raw.iat[2, col + 1])
        if pd.isna(antibiotic) or pd.isna(background) or "time" not in time_header:
            continue
        population_id = value_header
        for row in range(4, raw.shape[0]):
            time_h, response = raw.iat[row, col], raw.iat[row, col + 1]
            if pd.isna(time_h) or pd.isna(response):
                continue
            records.append({"population_id": population_id, "genetic_background": str(background), "antibiotic": str(antibiotic), "time_h": float(time_h), "selection_response": float(response)})
    return pd.DataFrame(records)


def mutation_pathways(pop: pd.DataFrame, rng: np.random.Generator) -> tuple[pd.DataFrame, dict[str, object]]:
    raw = pd.read_csv(MUTATIONS)
    raw = raw.dropna(subset=["title", "treatment", "mutated_gene_name", "gene_deletion_in_ancestor"]).copy()
    raw["population_id"] = raw.title.astype(str)
    raw["genetic_background"] = raw.gene_deletion_in_ancestor.astype(str)
    raw["antibiotic"] = raw.treatment.astype(str)
    sets = raw.groupby(["population_id", "genetic_background", "antibiotic", "ini_IC50"], as_index=False).agg(
        mutation_genes=("mutated_gene_name", lambda x: "|".join(sorted(set(map(str, x))))),
        n_mutations=("mutated_gene_name", "size"),
    )
    per_ab: dict[str, object] = {}
    for antibiotic, group in sets.groupby("antibiotic"):
        genes = [set(x.split("|")) for x in group.mutation_genes]
        backgrounds = group.genetic_background.to_numpy()
        pairs = [(i, j) for i in range(len(group)) for j in range(i + 1, len(group))]
        similarities = np.array([len(genes[i] & genes[j]) / len(genes[i] | genes[j]) for i, j in pairs])
        same = np.array([backgrounds[i] == backgrounds[j] for i, j in pairs])
        observed = float(similarities[same].mean() - similarities[~same].mean()) if same.any() and (~same).any() else float("nan")
        bins = pd.qcut(group.ini_IC50, q=min(5, group.ini_IC50.nunique()), duplicates="drop")
        strata = group.groupby(bins, observed=True).indices
        null = []
        for _ in range(N_PERM):
            labels = backgrounds.copy()
            for indices in strata.values():
                labels[indices] = rng.permutation(labels[indices])
            perm_same = np.array([labels[i] == labels[j] for i, j in pairs])
            if perm_same.any() and (~perm_same).any():
                null.append(similarities[perm_same].mean() - similarities[~perm_same].mean())
        per_ab[str(antibiotic)] = {
            "n_sequenced_populations": len(group),
            "same_minus_different_background_jaccard": observed,
            "permutation_p_one_sided_controlling_initial_IC50_bins": float((1 + np.sum(np.asarray(null) >= observed)) / (len(null) + 1)) if null else None,
        }
    return sets, per_ab


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    workbook = source_workbook()
    pop = populations(workbook)
    trajectories = temporal_trajectories(workbook)
    rng = np.random.default_rng(SEED)
    phenotype = {ab: performance(group.reset_index(drop=True), rng) for ab, group in pop.groupby("antibiotic", sort=True)}
    mutation_table, mutations = mutation_pathways(pop, rng)
    pop.to_csv(OUT / "PETRUNGARO_POPULATIONS.csv", index=False, lineterminator="\n")
    trajectories.to_csv(OUT / "PETRUNGARO_TEMPORAL_TRAJECTORIES.csv", index=False, lineterminator="\n")
    mutation_table.to_csv(OUT / "PETRUNGARO_MUTATION_PATHWAYS.csv", index=False, lineterminator="\n")
    result = {
        "schema": "oric.petrungaro-2026-real-evolution.v1",
        "status": "analysed_real_external_population_data",
        "sources": {
            "source_data_archive_sha256": sha256(ARCHIVE),
            "mutation_table_sha256": sha256(MUTATIONS),
            "sequencing_accession": "PRJEB103832",
        },
        "mapping": {
            "independent_unit": "independently evolved plate-well population",
            "X": "initial log10 IC50 reconstructed from published endpoint IC50/fold increase",
            "m": "initial gene-deletion genetic background",
            "Theta": "antibiotic MEC, NIT or TMP",
            "R": "future endpoint log10 IC50",
            "growth_trajectory": "published selection-response time series, retained separately and not substituted for IC50",
        },
        "phenotype_by_antibiotic": phenotype,
        "mutation_pathways_by_antibiotic": mutations,
        "n_temporal_measurements": len(trajectories),
        "qualification": {
            "real_data": True,
            "synthetic_or_simulated_scientific_data": False,
            "retrospective": True,
            "not_a_direct_do_m_ablation": True,
            "initial_growth_covariate_complete": False,
            "reason_initial_growth": "no population-level initial-growth field is paired to every Fig2a endpoint; it is not invented or imputed",
        },
    }
    write_json(OUT / "RESULTAT_PETRUNGARO_2026.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
