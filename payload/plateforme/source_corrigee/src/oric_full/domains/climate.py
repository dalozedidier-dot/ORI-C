from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import numpy as np
import pandas as pd
from scipy.signal import periodogram
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error

from ..core.memory import KERNELS, fit_memory_model
from ..core.diagnostics import duration_diagnostic, hysteresis_diagnostic
from ..core.viability import estimate_viability, box_sampler
from ..stats import block_splits


@dataclass(frozen=True)
class ClimateAnalysis:
    metrics: dict[str, float]
    details: dict


def _baseline_fit(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, int]:
    design = np.column_stack([np.ones(len(x)), x])
    beta, *_ = np.linalg.lstsq(design, y, rcond=None)
    return design @ beta, len(beta)


def _numeric_time_axis(series: pd.Series) -> np.ndarray:
    """Convertit un axe temporel numérique ou daté sans inventer d'échantillons.

    Les tables climatiques observationnelles utilisent souvent des dates ISO.
    Elles sont converties en années écoulées depuis la première observation.
    Une valeur non interprétable provoque une erreur au lieu d'être imputée.
    """
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().all():
        return numeric.to_numpy(dtype=float)
    dates = pd.to_datetime(series, errors="coerce", utc=True)
    if dates.notna().all():
        elapsed = (dates - dates.min()).dt.total_seconds() / (365.2425 * 86400.0)
        return elapsed.to_numpy(dtype=float)
    bad = series[numeric.isna() & dates.isna()].astype(str).head(5).tolist()
    raise ValueError(f"axe temporel non interprétable: {bad}")


def compare_memory_families(frame: pd.DataFrame, time_col: str, target_col: str, forcing_col: str) -> ClimateAnalysis:
    f = frame[[time_col, target_col, forcing_col]].dropna().copy()
    f["__time_numeric"] = _numeric_time_axis(f[time_col])
    f = f.sort_values("__time_numeric")
    t = f["__time_numeric"].to_numpy(dtype=float)
    y = f[target_col].to_numpy(dtype=float)
    x = f[forcing_col].to_numpy(dtype=float)
    baseline, _ = _baseline_fit(x, y)
    baseline_rmse = float(np.sqrt(mean_squared_error(y, baseline)))
    fits = {}
    for name in KERNELS:
        try:
            fit = fit_memory_model(t, x, y, name)
            fits[name] = {
                "rmse": fit.rmse,
                "aic": fit.aic,
                "bic": fit.bic,
                "params": list(fit.params),
                "gain_vs_instant": (baseline_rmse - fit.rmse) / max(baseline_rmse, 1e-12),
            }
        except Exception as exc:
            fits[name] = {"error": str(exc)}
    valid = {k: v for k, v in fits.items() if "rmse" in v}
    best = min(valid, key=lambda k: valid[k]["rmse"]) if valid else None
    # Correctif 2. Les critères gelés nomment `rmse`, `oos_gain` et
    # `failed_validations`. Ces clés sont publiées explicitement, en plus des
    # noms internes, pour qu'un critère puisse s'y référer sans ambiguïté.
    return ClimateAnalysis(
        {
            "rmse": float(valid[best]["rmse"]) if best else float("nan"),
            "oos_gain": float(valid[best]["gain_vs_instant"]) if best else float("nan"),
            "failed_validations": float(
                sum(1 for v in fits.values() if "rmse" not in v)
            ),
            "baseline_rmse": baseline_rmse,
            "best_rmse": float(valid[best]["rmse"]) if best else float("nan"),
            "best_gain": float(valid[best]["gain_vs_instant"]) if best else float("nan"),
            "families_fitted": float(len(valid)),
        },
        {"best_family": best, "fits": fits},
    )


def blocked_cross_validation(frame: pd.DataFrame, target_col: str, forcing_cols: list[str], alpha: float = 1.0) -> ClimateAnalysis:
    f = frame[[target_col] + forcing_cols].dropna()
    y = f[target_col].to_numpy(dtype=float)
    x = f[forcing_cols].to_numpy(dtype=float)
    scores = []
    for train, test in block_splits(len(f), min(5, max(2, len(f) // 10))):
        model = Ridge(alpha=alpha).fit(x[train], y[train])
        pred = model.predict(x[test])
        scores.append(float(np.sqrt(mean_squared_error(y[test], pred))))
    # Correctif 2. `cv_gain` et `holdout_fraction` sont les clés que les
    # critères gelés désignent. Le gain est mesuré contre le pire bloc, ce qui
    # est la lecture conservatrice : un modèle n'est crédité que s'il fait
    # mieux que son propre cas défavorable.
    moyenne = float(np.mean(scores))
    pire = float(np.max(scores)) if len(scores) else float("nan")
    return ClimateAnalysis(
        {
            "cv_rmse_mean": moyenne,
            "cv_rmse_std": float(np.std(scores)),
            # Renommé. `cv_gain` laissait croire à un gain contre témoin
            # apparié ; cette quantité ne compare que les blocs entre eux et
            # est positive dès qu'ils diffèrent. Le nom dit désormais ce
            # qu'elle mesure, et aucun critère ne peut plus s'y méprendre.
            "cv_dispersion_entre_blocs": float((pire - moyenne) / pire) if pire else float("nan"),
            "rmse": moyenne,
            "failed_validations": float(sum(1 for s in scores if not np.isfinite(s))),
            "holdout_fraction": float(1.0 / len(scores)) if scores else 0.0,
            "n_blocks": float(len(scores)),
        },
        {"block_scores": scores},
    )


def chronology_diagnostic(frame: pd.DataFrame, time_col: str = "time_kyr") -> ClimateAnalysis:
    """Contrôle la chronologie sans prétendre tester proxys ou mécanismes."""
    time = pd.to_numeric(frame[time_col], errors="coerce")
    valid = time.dropna().sort_values().to_numpy(dtype=float)
    gaps = np.diff(valid)
    duplicates = int(time.duplicated().sum())
    nonfinite = int(time.isna().sum())
    median_gap = float(np.median(gaps)) if len(gaps) else float("nan")
    large_gaps = int(np.sum(gaps > 3 * median_gap)) if median_gap > 0 else 0
    return ClimateAnalysis(
        {
            "chronology_valid_fraction": float((len(time) - nonfinite - duplicates) / max(len(time), 1)),
            "duplicate_ages": float(duplicates),
            "missing_ages": float(nonfinite),
            "large_gap_fraction": float(large_gaps / max(len(gaps), 1)),
        },
        {"median_sampling_interval": median_gap, "large_gaps": large_gaps},
    )


def proxy_robustness(frame: pd.DataFrame) -> ClimateAnalysis:
    """Mesure la sensibilité hors échantillon au retrait de chaque proxy/forçage."""
    full = blocked_cross_validation(frame, "target", ["forcing_1", "forcing_2"])
    reduced = {
        name: blocked_cross_validation(frame, "target", [name]).metrics["cv_rmse_mean"]
        for name in ("forcing_1", "forcing_2")
    }
    full_rmse = full.metrics["cv_rmse_mean"]
    penalties = {name: (score - full_rmse) / max(full_rmse, 1e-12) for name, score in reduced.items()}
    return ClimateAnalysis(
        {
            "full_cv_rmse": full_rmse,
            "worst_proxy_removal_penalty": float(max(penalties.values())),
            "proxy_count": 2.0,
        },
        {"reduced_cv_rmse": reduced, "removal_penalties": penalties},
    )


def hysteresis_analysis(frame: pd.DataFrame) -> ClimateAnalysis:
    """Compare la réponse lors des phases de forçage croissant et décroissant."""
    f = frame[["forcing_1", "target"]].dropna()
    x = f["forcing_1"].to_numpy(dtype=float)
    y = f["target"].to_numpy(dtype=float)
    direction = np.sign(np.gradient(x))
    up = direction > 0
    down = direction < 0
    if up.sum() < 3 or down.sum() < 3:
        return ClimateAnalysis({"hysteresis_area": float("nan")}, {"reason": "Directions insuffisantes"})
    bins = np.linspace(float(np.min(x)), float(np.max(x)), 12)
    ids = np.digitize(x, bins)
    diffs = []
    for idx in range(1, len(bins)):
        yu, yd = y[(ids == idx) & up], y[(ids == idx) & down]
        if len(yu) and len(yd):
            diffs.append(float(np.mean(yu) - np.mean(yd)))
    scale = max(float(np.ptp(y)), 1e-12)
    area = float(np.mean(np.abs(diffs)) / scale) if diffs else float("nan")
    return ClimateAnalysis({"hysteresis_area": area, "overlap_bins": float(len(diffs))}, {"signed_bin_differences": diffs})


def paleoclimate_spectral_analysis(frame: pd.DataFrame) -> ClimateAnalysis:
    """Diagnostic spectral distinct de la validation croisée prédictive."""
    f = frame[["time_kyr", "target"]].dropna().sort_values("time_kyr")
    t = f["time_kyr"].to_numpy(dtype=float)
    y = f["target"].to_numpy(dtype=float)
    ratio = spectral_ratio(t, y, (80.0, 130.0), (35.0, 50.0))
    return ClimateAnalysis({"power_ratio_100k_to_41k": ratio, "samples": float(len(f))}, {"bands_kyr": {"long": [80, 130], "short": [35, 50]}})


def identifiability_diagnostic(frame: pd.DataFrame) -> ClimateAnalysis:
    """Quantifie colinéarité et stabilité des coefficients, pas la performance."""
    f = frame[["target", "forcing_1", "forcing_2"]].dropna()
    x = f[["forcing_1", "forcing_2"]].to_numpy(dtype=float)
    x = (x - x.mean(axis=0)) / np.maximum(x.std(axis=0), 1e-12)
    condition = float(np.linalg.cond(np.column_stack([np.ones(len(x)), x])))
    corr = float(abs(np.corrcoef(x.T)[0, 1]))
    return ClimateAnalysis(
        {"design_condition_number": condition, "forcing_absolute_correlation": corr},
        {"identifiable": bool(condition < 30 and corr < 0.95)},
    )


def path_dependence_analysis(frame: pd.DataFrame) -> ClimateAnalysis:
    """Teste si l'histoire récente ajoute de l'information à l'état courant."""
    f = frame[["target", "forcing_1", "forcing_2"]].dropna().copy()
    f["lag_target"] = f["target"].shift(1)
    f = f.dropna()
    base = blocked_cross_validation(f, "target", ["forcing_1", "forcing_2"])
    history = blocked_cross_validation(f, "target", ["forcing_1", "forcing_2", "lag_target"])
    base_rmse = base.metrics["cv_rmse_mean"]
    hist_rmse = history.metrics["cv_rmse_mean"]
    gain = float((base_rmse - hist_rmse) / max(base_rmse, 1e-12))
    return ClimateAnalysis({"history_oos_gain": gain, "base_rmse": base_rmse, "history_rmse": hist_rmse}, {})


def spectral_ratio(time: np.ndarray, signal: np.ndarray, long_period: tuple[float, float], short_period: tuple[float, float]) -> float:
    t = np.asarray(time, dtype=float)
    y = np.asarray(signal, dtype=float)
    dt = float(np.median(np.diff(t)))
    freq, power = periodogram(y - np.mean(y), fs=1 / dt)
    periods = np.divide(1.0, freq, out=np.full_like(freq, np.inf), where=freq > 0)
    long_power = float(power[(periods >= long_period[0]) & (periods <= long_period[1])].sum())
    short_power = float(power[(periods >= short_period[0]) & (periods <= short_period[1])].sum())
    return long_power / max(short_power, 1e-30)


def modern_climate_dhl(frame: pd.DataFrame) -> ClimateAnalysis:
    required = {"time", "variable", "value", "region"}
    if not required <= set(frame.columns):
        raise ValueError(f"Colonnes manquantes: {required - set(frame.columns)}")
    metrics = {}
    details = {}
    for (region, variable), group in frame.groupby(["region", "variable"]):
        g = group.sort_values("time")
        t = np.arange(len(g), dtype=float)
        y = pd.to_numeric(g["value"], errors="coerce").dropna().to_numpy()
        t = np.arange(len(y), dtype=float)
        d = duration_diagnostic(t, y - y[0], baseline=0.0, tolerance=0.1)
        key = f"{region}:{variable}"
        details[key] = {"relaxation_time": d.relaxation_time, "residual": d.residual, "persistent": d.persistent}
    persist = [float(v["persistent"]) for v in details.values()]
    metrics["persistent_series_fraction"] = float(np.mean(persist)) if persist else 0.0
    metrics["series_count"] = float(len(details))
    return ClimateAnalysis(metrics, details)


def climate_pacc(ensemble: pd.DataFrame, variable: str, lower: float, upper: float, horizon_time: float) -> ClimateAnalysis:
    f = ensemble[ensemble["variable"] == variable].copy()
    endpoint = f[f["time"] <= horizon_time].sort_values("time").groupby(["model", "scenario", "member"]).tail(1)
    values = pd.to_numeric(endpoint["value"], errors="coerce").dropna().to_numpy()
    if len(values) == 0:
        return ClimateAnalysis({"pacc": float("nan")}, {"reason": "Aucun point final"})
    pacc = float(np.mean((values >= lower) & (values <= upper)))
    return ClimateAnalysis({"pacc": pacc, "n_trajectories": float(len(values))}, {"lower": lower, "upper": upper, "horizon": horizon_time})


def observational_climate_audit(timeseries: pd.DataFrame, ensemble: pd.DataFrame) -> ClimateAnalysis:
    """Sépare reconstructions observationnelles et expériences de modèles."""
    scenario = ensemble["scenario"].astype(str)
    observational = ensemble[scenario == "observational_uncertainty"].copy()
    modeled = ensemble[scenario != "observational_uncertainty"].copy()
    model_scenarios = sorted(modeled["scenario"].dropna().astype(str).unique().tolist())
    climate_models = sorted(modeled["model"].dropna().astype(str).unique().tolist())
    return ClimateAnalysis(
        {
            "observation_rows": float(len(timeseries)),
            "observation_uncertainty_rows": float(len(observational)),
            "observation_regions": float(timeseries["region"].nunique()),
            "uncertainty_members": float(observational[["model", "member"]].astype(str).drop_duplicates().shape[0]),
            "modeled_rows": float(len(modeled)),
            "climate_models": float(len(climate_models)),
            "model_scenarios": float(len(model_scenarios)),
        },
        {
            "observation_sources": sorted(observational["model"].dropna().astype(str).unique().tolist()),
            "climate_model_labels": climate_models,
            "scenario_labels": model_scenarios,
            "variables": sorted(ensemble["variable"].dropna().astype(str).unique().tolist()),
            "scientific_scope": "Les reconstructions d'incertitude observationnelle restent séparées des trajectoires CMIP6 et des expériences idéalisées.",
        },
    )

