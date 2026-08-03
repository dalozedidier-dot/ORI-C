from __future__ import annotations

from dataclasses import dataclass
import itertools
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GroupKFold, cross_val_predict


@dataclass(frozen=True)
class AntibioticAnalysis:
    metrics: dict[str, float]
    details: dict


def generate_exposure_histories(
    antibiotics: list[str],
    doses: list[float],
    cycles: int,
    replicates: int = 6,
    include_reversal: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    designs = []
    cycle_rows = []
    schedules = []
    for antibiotic in antibiotics:
        schedules.append([(antibiotic, dose) for dose in doses])
        schedules.append([(antibiotic, dose) for dose in reversed(doses)])
    if include_reversal and len(antibiotics) >= 2:
        schedules.append([(antibiotics[i % len(antibiotics)], doses[i % len(doses)]) for i in range(cycles)])
        schedules.append(list(reversed(schedules[-1])))
    for schedule_id, base in enumerate(schedules, start=1):
        expanded = list(itertools.islice(itertools.cycle(base), cycles))
        for replicate in range(replicates):
            lineage = f"L{schedule_id:03d}_R{replicate:02d}"
            designs.append({"arm_id": f"A{schedule_id:03d}", "species": "à_renseigner", "antibiotic": "+".join(sorted(set(a for a, _ in expanded))), "schedule": str(expanded), "dose": np.mean([d for _, d in expanded]), "replicates": replicates})
            for cycle, (antibiotic, dose) in enumerate(expanded, start=1):
                cycle_rows.append({"lineage_id": lineage, "cycle": cycle, "antibiotic": antibiotic, "dose": dose, "duration": 1.0, "recovery_duration": 1.0})
    return pd.DataFrame(designs).drop_duplicates("arm_id"), pd.DataFrame(cycle_rows)


def _hill(dose: np.ndarray, bottom: float, top: float, ec50: float, slope: float) -> np.ndarray:
    return bottom + (top - bottom) / (1.0 + (dose / max(ec50, 1e-12)) ** slope)


def estimate_mic(dose: np.ndarray, growth: np.ndarray, inhibition_fraction: float = 0.9) -> dict[str, float]:
    dose = np.asarray(dose, dtype=float)
    growth = np.asarray(growth, dtype=float)
    order = np.argsort(dose)
    dose, growth = dose[order], growth[order]
    p0 = [float(growth.min()), float(growth.max()), float(np.median(dose[dose > 0])) if np.any(dose > 0) else 1.0, 2.0]
    try:
        params, _ = curve_fit(_hill, dose, growth, p0=p0, maxfev=10000, bounds=([-np.inf, -np.inf, 1e-12, 0.05], [np.inf, np.inf, np.inf, 20]))
        grid = np.geomspace(max(dose[dose > 0].min(), 1e-12), max(dose.max(), 1e-12) * 10, 2000)
        pred = _hill(grid, *params)
        threshold = params[0] + (1 - inhibition_fraction) * (params[1] - params[0])
        mic = float(grid[np.argmin(np.abs(pred - threshold))])
        return {"mic": mic, "ec50": float(params[2]), "hill_slope": float(params[3])}
    except Exception:
        max_growth = max(float(np.max(growth)), 1e-12)
        candidates = dose[growth <= (1 - inhibition_fraction) * max_growth]
        return {"mic": float(candidates.min()) if len(candidates) else float("nan"), "ec50": float("nan"), "hill_slope": float("nan")}


def analyze_measurements(frame: pd.DataFrame) -> AntibioticAnalysis:
    f = frame.copy()
    numeric = ["cycle", "mic", "lag_time", "growth_rate", "survival", "persister_fraction", "fitness"]
    for col in numeric:
        f[col] = pd.to_numeric(f[col], errors="coerce")
    summaries = f.groupby("lineage_id").agg(
        mic_start=("mic", "first"), mic_end=("mic", "last"), fitness_end=("fitness", "last"),
        max_persistence=("persister_fraction", "max"), lag_end=("lag_time", "last")
    )
    mic_gain = summaries["mic_end"] / summaries["mic_start"].replace(0, np.nan)
    return AntibioticAnalysis(
        {
            "lineages": float(len(summaries)),
            "median_mic_fold_change": float(mic_gain.median(skipna=True) or 0.0),
            "median_final_fitness": float(summaries["fitness_end"].median(skipna=True) or 0.0),
            "median_max_persister_fraction": float(summaries["max_persistence"].median(skipna=True) or 0.0),
        },
        {"lineage_summary": summaries.reset_index().to_dict(orient="records")},
    )


def path_dependence_test(cycles: pd.DataFrame, measurements: pd.DataFrame) -> AntibioticAnalysis:
    histories = cycles.sort_values(["lineage_id", "cycle"]).groupby("lineage_id").apply(
        lambda g: "|".join(f"{a}:{d}" for a, d in zip(g["antibiotic"], g["dose"])), include_groups=False
    )
    final = measurements.sort_values(["lineage_id", "cycle"]).groupby("lineage_id").tail(1).set_index("lineage_id")
    joined = final.join(histories.rename("history"), how="inner")
    if len(joined) < 8 or joined["history"].nunique() < 2:
        return AntibioticAnalysis({"history_variance_fraction": float("nan")}, {"reason": "Données insuffisantes"})
    total_var = float(joined["mic"].var())
    within = float(joined.groupby("history")["mic"].var().fillna(0).mean())
    explained = max(total_var - within, 0.0) / max(total_var, 1e-12)
    return AntibioticAnalysis(
        {"history_variance_fraction": explained, "histories": float(joined["history"].nunique())},
        {"final_states": joined.reset_index().to_dict(orient="records")},
    )


def predictive_comparison(cycles: pd.DataFrame, measurements: pd.DataFrame, seed: int = 0) -> AntibioticAnalysis:
    merged = measurements.merge(cycles, on=["lineage_id", "cycle"], how="left")
    merged = merged.sort_values(["lineage_id", "cycle"])
    merged["cumulative_dose"] = merged.groupby("lineage_id")["dose"].cumsum()
    merged["previous_mic"] = merged.groupby("lineage_id")["mic"].shift(1)
    merged["target_next_mic"] = merged.groupby("lineage_id")["mic"].shift(-1)
    f = merged.dropna(subset=["target_next_mic", "mic", "dose", "cycle", "cumulative_dose"]).copy()
    if len(f) < 20 or f["lineage_id"].nunique() < 3:
        return AntibioticAnalysis({"gain_history_vs_instant": float("nan")}, {"reason": "Données insuffisantes"})
    groups = f["lineage_id"].astype("category").cat.codes.to_numpy()
    n_splits = min(5, f["lineage_id"].nunique())
    cv = GroupKFold(n_splits=n_splits)
    y = f["target_next_mic"].to_numpy(dtype=float)
    x_inst = f[["mic", "dose", "cycle"]].to_numpy(dtype=float)
    x_hist = f[["mic", "dose", "cycle", "cumulative_dose", "previous_mic"]].fillna(0).to_numpy(dtype=float)
    instant = Ridge(alpha=1.0)
    history = RandomForestRegressor(n_estimators=300, random_state=seed, min_samples_leaf=2)
    p_inst = cross_val_predict(instant, x_inst, y, groups=groups, cv=cv)
    p_hist = cross_val_predict(history, x_hist, y, groups=groups, cv=cv)
    r_inst = float(np.sqrt(mean_squared_error(y, p_inst)))
    r_hist = float(np.sqrt(mean_squared_error(y, p_hist)))
    gain = (r_inst - r_hist) / max(r_inst, 1e-12)
    return AntibioticAnalysis(
        {"instant_rmse": r_inst, "history_rmse": r_hist, "gain_history_vs_instant": gain},
        {"n": len(f), "lineages": int(f["lineage_id"].nunique())},
    )
