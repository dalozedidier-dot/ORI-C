#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "donnees" / "pbio.2001586.s018.xlsx"
OUT = HERE / "resultats" / "RESULTAT.json"

MAPPING = {
    "Control": ("LB", "LB"),
    "PIPR": ("PIP", "PIP"),
    "TOBR": ("TOB", "TOB"),
    "CIPR": ("CIP", "CIP"),
    "PIPRTOBR": ("PIP", "TOB"),
    "TOBRPIPR": ("TOB", "PIP"),
    "PIPRCIPR": ("PIP", "CIP"),
    "TOBRCIPR": ("TOB", "CIP"),
    "CIPRTOBR": ("CIP", "TOB"),
    "CIPRPIPR": ("CIP", "PIP"),
    "PIPRLB": ("PIP", "LB"),
    "TOBRLB": ("TOB", "LB"),
    "CIPRLB": ("CIP", "LB"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_source(path: Path) -> list[dict]:
    raw = pd.read_excel(path, sheet_name="DataForFig2andS4", header=None)
    blocks = {
        "PIP": {"group_row": 2, "rep_row": 3, "data_start": 5, "data_end": 44},
        "TOB": {"group_row": 48, "rep_row": 49, "data_start": 51, "data_end": 90},
        "CIP": {"group_row": 94, "rep_row": 95, "data_start": 97, "data_end": 136},
    }
    rows_long: list[tuple[str, int, str, int, float]] = []
    for assay, block in blocks.items():
        labels = []
        current = None
        for value in raw.iloc[block["group_row"]].tolist():
            if pd.notna(value):
                current = str(value).strip()
            labels.append(current)
        reps = raw.iloc[block["rep_row"]].tolist()
        for ri in range(block["data_start"], block["data_end"] + 1):
            day = raw.iat[ri, 0]
            if not isinstance(day, (int, float, np.integer, np.floating)) or pd.isna(day):
                continue
            for col in range(1, min(53, raw.shape[1])):
                group_label = labels[col]
                rep = reps[col]
                value = raw.iat[ri, col]
                if group_label is None or pd.isna(rep) or pd.isna(value):
                    continue
                rows_long.append((assay, int(day), group_label, int(rep), float(value)))

    init_group = {"LB": "Control", "PIP": "PIPR", "TOB": "TOBR", "CIP": "CIPR"}
    baseline: dict[tuple[str, str, int], float] = {}
    for assay, day, group_label, rep, value in rows_long:
        if day != 20:
            continue
        for history, initial_label in init_group.items():
            if group_label == initial_label:
                baseline[(assay, history, rep)] = value

    future: list[dict] = []
    for assay, day, group_label, rep, value in rows_long:
        if day < 21:
            continue
        history, current = MAPPING[group_label]
        before = baseline.get((assay, history, rep))
        if before is None:
            continue
        future.append({
            "assay": assay,
            "day": day,
            "phase2_day": day - 20,
            "group_label": group_label,
            "history": history,
            "current": current,
            "rep": rep,
            "branch_group": f"{history}-r{rep}",
            "baseline_log2mic": before,
            "outcome_log2mic": value,
        })
    return future


def predictions(X: np.ndarray, y: np.ndarray, groups: np.ndarray, categorical: list[int], numeric: list[int]) -> np.ndarray:
    pre = ColumnTransformer([
        ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical),
        ("numeric", StandardScaler(), numeric),
    ])
    model = Pipeline([("preprocessor", pre), ("model", Ridge(alpha=1.0))])
    return cross_val_predict(model, X, y, groups=groups, cv=GroupKFold(n_splits=5))


def rmse(y: np.ndarray, pred: np.ndarray) -> float:
    return float(mean_squared_error(y, pred) ** 0.5)


def gain(y: np.ndarray, state: np.ndarray, history: np.ndarray) -> float:
    r0 = rmse(y, state)
    return 100.0 * (r0 - rmse(y, history)) / r0


def bootstrap_gain(y, state, history, groups, repeats=5000, seed=20260812):
    unique = np.unique(groups)
    by_group = {g: np.flatnonzero(groups == g) for g in unique}
    rng = np.random.default_rng(seed)
    values = np.empty(repeats)
    for i in range(repeats):
        sampled = rng.choice(unique, size=len(unique), replace=True)
        idx = np.concatenate([by_group[g] for g in sampled])
        values[i] = gain(y[idx], state[idx], history[idx])
    return [float(x) for x in np.quantile(values, [0.025, 0.975])]


def permutation_p(future, y, groups, rmse_state, *, include_baseline=False, repeats=1000, seed=20260813):
    unique = np.unique(groups)
    group_history = {r["branch_group"]: r["history"] for r in future}
    histories = np.array([group_history[g] for g in unique], dtype=object)
    current = np.array([r["current"] for r in future], dtype=object)
    assay = np.array([r["assay"] for r in future], dtype=object)
    phase2_day = np.array([float(r["phase2_day"]) for r in future], dtype=object)
    baseline = np.array([float(r["baseline_log2mic"]) for r in future], dtype=object)

    rng = np.random.default_rng(seed)
    observed_features = (
        np.column_stack([current, assay, phase2_day, baseline, np.array([r["history"] for r in future], dtype=object)])
        if include_baseline
        else np.column_stack([current, assay, phase2_day, np.array([r["history"] for r in future], dtype=object)])
    )
    observed_pred = predictions(observed_features, y, groups, [0, 1, 4] if include_baseline else [0, 1, 3], [2, 3] if include_baseline else [2])
    observed_gain = 100.0 * (rmse_state - rmse(y, observed_pred)) / rmse_state

    null = np.empty(repeats)
    for i in range(repeats):
        shuffled = histories.copy()
        rng.shuffle(shuffled)
        mapping = dict(zip(unique, shuffled))
        histcol = np.array([mapping[g] for g in groups], dtype=object)
        X = (
            np.column_stack([current, assay, phase2_day, baseline, histcol])
            if include_baseline
            else np.column_stack([current, assay, phase2_day, histcol])
        )
        pred = predictions(X, y, groups, [0, 1, 4] if include_baseline else [0, 1, 3], [2, 3] if include_baseline else [2])
        null[i] = 100.0 * (rmse_state - rmse(y, pred)) / rmse_state
    p = float((1 + np.sum(null >= observed_gain)) / (1 + repeats))
    return observed_gain, p


def build() -> dict:
    future = parse_source(SOURCE)
    y = np.array([r["outcome_log2mic"] for r in future], dtype=float)
    groups = np.array([r["branch_group"] for r in future], dtype=object)
    current = np.array([r["current"] for r in future], dtype=object)
    assay = np.array([r["assay"] for r in future], dtype=object)
    day = np.array([float(r["phase2_day"]) for r in future], dtype=object)
    hist = np.array([r["history"] for r in future], dtype=object)
    baseline = np.array([float(r["baseline_log2mic"]) for r in future], dtype=object)

    X_state = np.column_stack([current, assay, day])
    X_hist = np.column_stack([current, assay, day, hist])
    ps = predictions(X_state, y, groups, [0, 1], [2])
    ph = predictions(X_hist, y, groups, [0, 1, 3], [2])
    rs = rmse(y, ps)
    rh = rmse(y, ph)
    primary_gain = 100.0 * (rs - rh) / rs
    primary_ci = bootstrap_gain(y, ps, ph, groups, seed=20260812)
    _, primary_p = permutation_p(future, y, groups, rs, include_baseline=False, seed=20260813)

    X_state_rich = np.column_stack([current, assay, day, baseline])
    X_hist_rich = np.column_stack([current, assay, day, baseline, hist])
    psb = predictions(X_state_rich, y, groups, [0, 1], [2, 3])
    phb = predictions(X_hist_rich, y, groups, [0, 1, 4], [2, 3])
    rsb = rmse(y, psb)
    rhb = rmse(y, phb)
    rich_gain = 100.0 * (rsb - rhb) / rsb
    rich_ci = bootstrap_gain(y, psb, phb, groups, seed=20260814)
    _, rich_p = permutation_p(future, y, groups, rsb, include_baseline=True, seed=20260815)

    return {
        "schema": "oric.external-benchmark.v1",
        "benchmark_id": "YEN-PAPIN-2017-HISTORY-MIC",
        "source": {
            "doi": "10.1371/journal.pbio.2001586",
            "file": SOURCE.name,
            "sha256": sha256(SOURCE),
            "sheet": "DataForFig2andS4",
        },
        "mapping": {
            "analysis_window": "days 21-40 after switch",
            "rows": len(future),
            "independent_units": int(len(np.unique(groups))),
            "grouping": "phase-1 treatment × replicate; all descendant phase-2 branches from the same phase-1 replicate remain in the same CV group",
            "outcome": "raw log2 MIC to PIP/TOB/CIP",
            "present_state_primary": ["phase-2 treatment", "assayed antibiotic", "days since switch"],
            "history": "phase-1 treatment",
            "model": "Ridge(alpha=1), 5-fold GroupKFold",
            "threshold_percent": 5.0,
            "bootstrap_repeats": 5000,
            "permutation_repeats": 1000,
        },
        "primary_result": {
            "rmse_state_only": rs,
            "rmse_state_plus_history": rh,
            "history_gain_percent": primary_gain,
            "bootstrap_gain_95pct": primary_ci,
            "permutation_p": primary_p,
            "decision_components": {
                "gain_at_least_5_percent": bool(primary_gain >= 5.0),
                "bootstrap_gain_strictly_positive": bool(primary_ci[0] > 0.0),
                "permutation_p_at_most_0_05": bool(primary_p <= 0.05),
            },
            "pred_vivant_histoire_001_success": False,
        },
        "strict_state_sensitivity": {
            "present_state_added": "Day-20 MIC immediately before phase-2 branching",
            "rmse_state_only": rsb,
            "rmse_state_plus_history": rhb,
            "history_gain_percent": rich_gain,
            "bootstrap_gain_95pct": rich_ci,
            "permutation_p": rich_p,
            "interpretation": "Once measured Day-20 MIC is part of X, the residual history contribution is not supported.",
        },
        "classification": {
            "external_real_dataset": True,
            "retrospective": True,
            "public_preregistration_before_opening": False,
            "counts_for_strict_section_XIV": False,
            "thresholds_moved": False,
            "verdict": "negative_for_frozen_5_percent_prediction_but_positive_weak_retrospective_history_signal_without_day20_state",
        },
    }


if __name__ == "__main__":
    result = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
