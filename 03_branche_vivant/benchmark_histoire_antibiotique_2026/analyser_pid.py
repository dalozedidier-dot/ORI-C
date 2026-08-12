#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from methodologie_informationnelle.pid import pid_imin

DATA = ROOT / "donnees_externes/histoire_antibiotique_donofrio_2026/extracted/Figure_3_N-lim_Expt_MIC_Raw_Data.csv"
OUT = Path(__file__).resolve().parent / "resultats/PID_X_M_A.json"


def canonicalize_numbers(value: object, significant_digits: int = 13) -> object:
    if isinstance(value, (float, np.floating)):
        number = float(value)
        if not np.isfinite(number):
            return number
        return float(format(number, f".{significant_digits}g"))
    if isinstance(value, dict):
        return {key: canonicalize_numbers(item, significant_digits) for key, item in value.items()}
    if isinstance(value, list):
        return [canonicalize_numbers(item, significant_digits) for item in value]
    if isinstance(value, tuple):
        return [canonicalize_numbers(item, significant_digits) for item in value]
    return value


def pacc_from_frame(df: pd.DataFrame) -> dict[str, object]:
    """Support MIC rétrospectif conditionné par l'état et l'histoire.

    Pour chaque état présent X=(limitation, antibiotique), le dénominateur est
    l'ensemble des classes MIC effectivement observées dans cet état. Pour
    chaque histoire H=ancêtre, P_acc est la fraction de ce support qui reste
    occupée après conditionnement par H. Il s'agit donc d'un proxy de support
    empirique observé, pas de l'ensemble contrefactuel complet des futurs.
    """
    required = {"Limitation", "Antibiotic", "Ancestor", "Strain", "MIC (ug/mL)"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise KeyError(f"colonnes manquantes pour P_acc antibiotique: {missing}")

    work = df.copy()
    work["MIC (ug/mL)"] = pd.to_numeric(work["MIC (ug/mL)"], errors="coerce")
    work = work.dropna(subset=list(required)).copy()
    work["MIC_class"] = work["MIC (ug/mL)"].map(lambda x: f"{float(x):g}")

    rows: list[dict[str, object]] = []
    for (limitation, antibiotic), state in work.groupby(["Limitation", "Antibiotic"], sort=True):
        state_classes = sorted(state["MIC_class"].unique(), key=float)
        denominator = len(state_classes)
        for ancestor, history in state.groupby("Ancestor", sort=True):
            occupied = sorted(history["MIC_class"].unique(), key=float)
            rows.append({
                "limitation": str(limitation),
                "antibiotic": str(antibiotic),
                "ancestor": str(ancestor),
                "rows": int(len(history)),
                "state_support_classes": state_classes,
                "history_occupied_classes": occupied,
                "state_support_size": denominator,
                "history_support_size": len(occupied),
                "P_acc": len(occupied) / denominator if denominator else 0.0,
            })

    observed_mean = float(np.mean([row["P_acc"] for row in rows]))
    observed_median = float(np.median([row["P_acc"] for row in rows]))

    # Contrôle de même complexité : l'ancêtre est permuté au niveau Strain à
    # l'intérieur de chaque limitation. Les répétitions techniques d'une même
    # souche restent ensemble et les effectifs par ancêtre sont préservés.
    #
    # Les 2 000 permutations utilisent des codes entiers et une table
    # d'occupation état × histoire × classe MIC. C'est strictement le même
    # objet statistique que les groupby pandas initiaux, sans recopier le
    # DataFrame à chaque permutation.
    groups = (
        work[["Strain", "Limitation", "Ancestor"]]
        .drop_duplicates()
        .sort_values(["Limitation", "Strain"])
        .reset_index(drop=True)
    )
    group_key = {
        (strain, str(limitation)): index
        for index, (strain, limitation) in enumerate(zip(groups["Strain"], groups["Limitation"]))
    }
    row_group = np.asarray(
        [group_key[(strain, str(limitation))] for strain, limitation in zip(work["Strain"], work["Limitation"])],
        dtype=np.int64,
    )
    ancestor_levels = sorted(work["Ancestor"].astype(str).unique())
    ancestor_lookup = {value: index for index, value in enumerate(ancestor_levels)}
    group_ancestor = np.asarray(
        [ancestor_lookup[value] for value in groups["Ancestor"].astype(str)],
        dtype=np.int64,
    )
    state_pairs = sorted({(str(l), str(a)) for l, a in zip(work["Limitation"], work["Antibiotic"])})
    state_lookup = {value: index for index, value in enumerate(state_pairs)}
    state_codes = np.asarray(
        [state_lookup[(str(l), str(a))] for l, a in zip(work["Limitation"], work["Antibiotic"])],
        dtype=np.int64,
    )
    mic_levels = sorted(work["MIC_class"].unique(), key=float)
    mic_lookup = {value: index for index, value in enumerate(mic_levels)}
    mic_codes = np.asarray([mic_lookup[value] for value in work["MIC_class"]], dtype=np.int64)
    n_states, n_ancestors, n_mic = len(state_pairs), len(ancestor_levels), len(mic_levels)
    denominators = np.asarray(
        [work.loc[state_codes == index, "MIC_class"].nunique() for index in range(n_states)],
        dtype=float,
    )
    limitation_values = groups["Limitation"].astype(str).to_numpy()
    limitation_groups = [
        np.flatnonzero(limitation_values == limitation)
        for limitation in sorted(set(limitation_values))
    ]

    rng = np.random.default_rng(20260812)
    repeats = 2000
    null = np.empty(repeats, dtype=float)
    flat_size = n_states * n_ancestors * n_mic
    present_size = n_states * n_ancestors
    for repeat in range(repeats):
        permuted_group_ancestor = group_ancestor.copy()
        for ids in limitation_groups:
            values = permuted_group_ancestor[ids].copy()
            rng.shuffle(values)
            permuted_group_ancestor[ids] = values
        row_ancestor = permuted_group_ancestor[row_group]
        flat = (state_codes * n_ancestors + row_ancestor) * n_mic + mic_codes
        occupied = (np.bincount(flat, minlength=flat_size) > 0).reshape(n_states, n_ancestors, n_mic)
        support = occupied.sum(axis=2)
        present = (
            np.bincount(state_codes * n_ancestors + row_ancestor, minlength=present_size) > 0
        ).reshape(n_states, n_ancestors)
        values = support / denominators[:, None]
        null[repeat] = float(np.mean(values[present]))

    p_lower = float((1 + np.sum(null <= observed_mean)) / (repeats + 1))
    null_mean = float(np.mean(null))
    return {
        "definition": "pour X=(limitation, antibiotique), fraction des classes MIC observées sous X encore occupées après conditionnement par H=ancêtre",
        "status": "empirical_retrospective_support_proxy",
        "rows": rows,
        "strata_count": len(rows),
        "global_observed_MIC_classes": sorted(work["MIC_class"].unique(), key=float),
        "mean_P_acc": observed_mean,
        "median_P_acc": observed_median,
        "mean_contraction_fraction": 1.0 - observed_mean,
        "same_complexity_history_permutation": {
            "unit": "Strain within Limitation",
            "permutations": repeats,
            "seed": 20260812,
            "null_mean_P_acc": null_mean,
            "null_q025": float(np.quantile(null, 0.025)),
            "null_q975": float(np.quantile(null, 0.975)),
            "p_one_sided_observed_support_narrower_than_shuffled": p_lower,
            "relative_support_contraction_vs_null_percent": 100.0 * (null_mean - observed_mean) / null_mean,
        },
        "interpretation": "Le véritable regroupement historique concentre le support MIC observé davantage qu'un étiquetage d'histoire permuté de même complexité si le p unilatéral est petit.",
        "limitation": "P_acc mesure le support empirique rétrospectif dans le panneau MIC observé; ce n'est ni une probabilité naturelle, ni une prédiction prospective, ni l'ensemble contrefactuel complet des réponses possibles.",
    }


def main() -> dict[str, object]:
    df = pd.read_csv(DATA)
    X = (df["Limitation"].astype(str) + "|" + df["Antibiotic"].astype(str)).tolist()
    M = df["Ancestor"].astype(str).tolist()
    Y = df["MIC (ug/mL)"].astype(str).tolist()
    obs = pid_imin(X, M, Y)

    groups = (
        df[["Strain", "Limitation", "Ancestor"]]
        .drop_duplicates()
        .sort_values(["Limitation", "Strain"])
        .reset_index(drop=True)
    )
    group_key = {(int(row.Strain), str(row.Limitation)): i for i, row in groups.iterrows()}
    row_group = np.array(
        [group_key[(int(strain), str(limitation))] for strain, limitation in zip(df.Strain, df.Limitation)],
        dtype=int,
    )
    ancestor_by_group = groups["Ancestor"].astype(str).to_numpy()
    strata = []
    limitation_values = groups["Limitation"].astype(str).to_numpy()
    for limitation in sorted(set(limitation_values)):
        strata.append(np.flatnonzero(limitation_values == limitation))

    rng = np.random.default_rng(20260810)
    nperm = 2000
    keys = ["unique_M_history_bits", "synergy_XM_bits", "I_XM_Y_bits"]
    null = {key: np.empty(nperm) for key in keys}
    for i in range(nperm):
        perm = ancestor_by_group.copy()
        for ids in strata:
            perm[ids] = rng.permutation(perm[ids])
        result_perm = pid_imin(X, perm[row_group].tolist(), Y)
        for key in keys:
            null[key][i] = result_perm[key]

    result: dict[str, object] = {
        "status": "exploratory_additional_analysis",
        "method": "Williams-Beer I_min PID on discretely observed variables",
        "scope": "Does not alter C-ANT-01 certification; X=Limitation|Antibiotic, M=Ancestor, Y=observed MIC level.",
        "rows": len(df),
        "strain_groups": int(df["Strain"].nunique()),
        "permutations": nperm,
        "seed": 20260810,
        "observed": obs,
        "null": {},
        "P_acc_retrospective": pacc_from_frame(df),
        "complete_case_X_H_m_Theta_tau_Pacc_R": {
            "X": "limitation présente et antibiotique testé",
            "H": "ascendance expérimentale de la lignée",
            "m": "étiquette d'état historique de lignée utilisée dans le PID; trace biologique physique distincte non isolée",
            "Theta": "panneau MIC, limitation et protocole expérimental publiés",
            "tau": "endpoint expérimental MIC du jeu publié",
            "P_acc": "support MIC empirique rétrospectif conditionné par X,H; voir P_acc_retrospective",
            "R": "niveau MIC observé",
            "status": "complete_retrospective_information_case_with_proxy_Pacc",
            "limitation": "m est ici un état historique de lignée utilisé comme variable informationnelle, pas une trace physique isolée ni ablatable; P_acc est un support observé rétrospectif et ne démontre pas une médiation causale.",
        },
        "warning": "PID I_min is one redundancy definition among several; results are exploratory and discretization-specific.",
    }
    for key, values in null.items():
        result["null"][key] = {
            "mean": float(values.mean()),
            "q025": float(np.quantile(values, 0.025)),
            "q975": float(np.quantile(values, 0.975)),
            "p_one_sided_ge_observed": float((1 + np.sum(values >= obs[key])) / (nperm + 1)),
        }

    result = canonicalize_numbers(result)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    main()
