"""Analyse longitudinale de Lamrabet et al. 2019 sur MIC reelles.

L'unite inferentielle est toujours la lignee LTEE (n=12). Les repetitions
techniques servent uniquement a construire la mediane MIC d'une cellule
lignee x generation x antibiotique.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "donnees_externes/lamrabet_2019/mbio.00189-19-sd001.xls"
OUT = HERE / "resultats"
SEED = 20260815
N_PERMUTATIONS = 10_000
N_BOOTSTRAPS = 5_000


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def normalize_lineage(value: object) -> str:
    return str(value).replace("−", "-").replace("–", "-").replace("�", "-")


def extract_long() -> pd.DataFrame:
    wide = pd.read_excel(SOURCE, sheet_name="MIC replicates", engine="xlrd")
    wide = wide.dropna(subset=["Population", "Generation"]).copy()
    wide["lineage"] = wide["Population"].map(normalize_lineage)
    wide["generation"] = wide["Generation"].astype(int)
    records: list[dict[str, object]] = []
    for _, row in wide.iterrows():
        for column in wide.columns:
            if "-" not in str(column):
                continue
            antibiotic, repetition = str(column).rsplit("-", 1)
            if not repetition.isdigit() or pd.isna(row[column]):
                continue
            records.append(
                {
                    "lineage": row["lineage"],
                    "generation": int(row["generation"]),
                    "antibiotic": antibiotic,
                    "replicate": int(repetition),
                    "MIC": float(row[column]),
                }
            )
    long = pd.DataFrame(records).sort_values(
        ["antibiotic", "lineage", "generation", "replicate"]
    ).reset_index(drop=True)
    if len(long) != 1125:
        raise ValueError(f"1125 mesures MIC attendues, obtenu {len(long)}")
    if set(long.loc[long.lineage != "Ancestor", "generation"]) != {2000, 50000}:
        raise ValueError("generations LTEE inattendues")
    if long.loc[long.lineage != "Ancestor", "lineage"].nunique() != 12:
        raise ValueError("12 lignees independantes attendues")
    return long


def safe_spearman(x: np.ndarray, y: np.ndarray) -> float:
    # Rangs moyens obligatoires pour les nombreux ex aequo des dilutions MIC.
    xr = pd.Series(x).rank(method="average").to_numpy(float)
    yr = pd.Series(y).rank(method="average").to_numpy(float)
    if np.std(xr) == 0 or np.std(yr) == 0:
        return 0.0
    value = np.corrcoef(xr, yr)[0, 1]
    return float(value) if np.isfinite(value) else 0.0


def analyse(long: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    med = (
        long.groupby(["lineage", "generation", "antibiotic"], as_index=False)["MIC"]
        .median()
        .rename(columns={"MIC": "MIC_median"})
    )
    ancestor = med.loc[med.lineage == "Ancestor", ["antibiotic", "MIC_median"]].rename(
        columns={"MIC_median": "MIC_ancestor"}
    )
    evolved = med.loc[med.lineage != "Ancestor"].merge(ancestor, on="antibiotic", validate="many_to_one")
    evolved["log2_change_vs_ancestor"] = np.log2(evolved.MIC_median / evolved.MIC_ancestor)
    profiles = evolved.pivot(index=["lineage", "antibiotic"], columns="generation", values="log2_change_vs_ancestor").reset_index()
    profiles.columns.name = None
    profiles = profiles.rename(columns={2000: "change_gen_2000", 50000: "change_gen_50000"})
    profiles["change_2000_to_50000"] = profiles.change_gen_50000 - profiles.change_gen_2000
    profiles["same_direction_from_ancestor"] = (
        np.sign(profiles.change_gen_2000) == np.sign(profiles.change_gen_50000)
    )
    profiles["direction_inverted"] = (
        (np.sign(profiles.change_gen_2000) != 0)
        & (np.sign(profiles.change_gen_50000) != 0)
        & (np.sign(profiles.change_gen_2000) != np.sign(profiles.change_gen_50000))
    )

    rng = np.random.default_rng(SEED)
    rows: list[dict[str, object]] = []
    for antibiotic, group in profiles.groupby("antibiotic", sort=True):
        x = group.change_gen_2000.to_numpy(float)
        y = group.change_gen_50000.to_numpy(float)
        rho = safe_spearman(x, y)
        null = np.array([safe_spearman(x, rng.permutation(y)) for _ in range(N_PERMUTATIONS)])
        boot = np.array([
            safe_spearman(x[idx], y[idx])
            for idx in rng.integers(0, len(x), size=(N_BOOTSTRAPS, len(x)))
        ])
        rows.append(
            {
                "antibiotic": antibiotic,
                "n_lineages": len(group),
                "spearman_persistence_2000_50000": rho,
                "bootstrap_q025": float(np.quantile(boot, 0.025)),
                "bootstrap_q975": float(np.quantile(boot, 0.975)),
                "permutation_p_two_sided": float((1 + np.sum(np.abs(null) >= abs(rho))) / (N_PERMUTATIONS + 1)),
                "sd_log2_change_50000": float(np.std(y, ddof=1)),
                "range_log2_change_50000": float(np.ptp(y)),
                "same_direction_fraction": float(group.same_direction_from_ancestor.mean()),
                "inversion_fraction": float(group.direction_inverted.mean()),
                "median_change_2000_to_50000": float(np.median(group.change_2000_to_50000)),
            }
        )
    by_antibiotic = pd.DataFrame(rows)

    lineages = sorted(profiles.lineage.unique())
    antibiotics = sorted(profiles.antibiotic.unique())
    xmat = profiles.pivot(index="lineage", columns="antibiotic", values="change_gen_2000").loc[lineages, antibiotics].to_numpy()
    ymat = profiles.pivot(index="lineage", columns="antibiotic", values="change_gen_50000").loc[lineages, antibiotics].to_numpy()
    observed = safe_spearman(xmat.ravel(), ymat.ravel())
    global_null = np.array([
        safe_spearman(xmat.ravel(), ymat[rng.permutation(len(lineages)), :].ravel())
        for _ in range(N_PERMUTATIONS)
    ])
    boot_global = []
    for _ in range(N_BOOTSTRAPS):
        idx = rng.integers(0, len(lineages), len(lineages))
        boot_global.append(safe_spearman(xmat[idx, :].ravel(), ymat[idx, :].ravel()))

    result: dict[str, object] = {
        "schema": "oric.lamrabet-2019-longitudinal-real.v1",
        "status": "analysed_real_external_longitudinal_dataset",
        "source": "donnees_externes/lamrabet_2019/mbio.00189-19-sd001.xls",
        "source_sha256": sha256(SOURCE),
        "independent_unit": "LTEE lineage",
        "n_independent_units": 12,
        "n_antibiotics": len(antibiotics),
        "n_raw_MIC_measurements": len(long),
        "generations": [0, 2000, 50000],
        "method": {
            "cell_summary": "median of three MIC replicates",
            "effect_scale": "log2 MIC ratio relative to shared ancestor",
            "persistence": "Spearman across the 12 lineages between generations 2000 and 50000",
            "permutation": "whole 50000-generation lineage profiles permuted; antibiotics never treated as independent units",
            "bootstrap": "LTEE lineages resampled as complete antibiotic profiles",
            "seed": SEED,
        },
        "global": {
            "spearman_profile_persistence": observed,
            "bootstrap_q025": float(np.quantile(boot_global, 0.025)),
            "bootstrap_q975": float(np.quantile(boot_global, 0.975)),
            "permutation_p_two_sided": float((1 + np.sum(np.abs(global_null) >= abs(observed))) / (N_PERMUTATIONS + 1)),
            "antibiotics_with_nonzero_50k_divergence": int((by_antibiotic.sd_log2_change_50000 > 0).sum()),
            "antibiotics_with_at_least_twofold_50k_range": int((by_antibiotic.range_log2_change_50000 >= 1).sum()),
            "same_direction_fraction_all_cells": float(profiles.same_direction_from_ancestor.mean()),
            "inversion_fraction_all_cells": float(profiles.direction_inverted.mean()),
        },
        "verdict": "lineages_from_the_same_ancestor_remain_divergent_but_cross_antibiotic_long_term_persistence_requires_the_reported_permutation_result",
        "qualification": {
            "real_data": True,
            "synthetic_or_simulated_scientific_data": False,
            "causal_history_intervention": False,
            "reason": "lineage identity indexes realized evolutionary histories; it was not experimentally assigned as a trace ablation",
        },
    }
    return by_antibiotic, result


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    long = extract_long()
    by_antibiotic, result = analyse(long)
    long.to_csv(OUT / "LAMRABET_MIC_LONG.csv", index=False, lineterminator="\n")
    by_antibiotic.to_csv(OUT / "LAMRABET_PAR_ANTIBIOTIQUE.csv", index=False, lineterminator="\n")
    write_json(OUT / "RESULTAT_LAMRABET_2019.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
