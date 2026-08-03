from __future__ import annotations

from dataclasses import dataclass
import json
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from statsmodels.formula.api import mixedlm, ols


@dataclass(frozen=True)
class PlanetaryAnalysis:
    metrics: dict[str, float]
    details: dict


def provenance_clustering(frame: pd.DataFrame, seed: int = 0) -> PlanetaryAnalysis:
    pivot = frame.pivot_table(index="sample_id", columns="tracer", values="value", aggfunc="mean")
    pivot = pivot.fillna(pivot.mean()).fillna(0.0)
    x = StandardScaler().fit_transform(pivot.to_numpy())
    if len(pivot) < 4 or x.shape[1] == 0:
        return PlanetaryAnalysis({"silhouette": float("nan")}, {"reason": "Données insuffisantes"})
    gmm = GaussianMixture(n_components=2, random_state=seed).fit(x)
    labels = gmm.predict(x)
    score = silhouette_score(x, labels) if len(set(labels)) > 1 else float("nan")
    return PlanetaryAnalysis(
        {"silhouette": float(score), "bic": float(gmm.bic(x)), "samples": float(len(pivot))},
        {"assignments": dict(zip(pivot.index.astype(str), labels.astype(int).tolist()))},
    )


def _al26_heat(time_myr: float, al26_ratio: float, scale: float = 3.0e-7) -> float:
    half_life = 0.717
    decay = np.log(2) / half_life
    return scale * al26_ratio * np.exp(-decay * time_myr)


def simulate_planetesimal_thermal(
    radius_km: float,
    porosity: float,
    formation_time_myr: float,
    al26_ratio: float,
    *,
    t_end_myr: float = 10.0,
) -> dict[str, float]:
    radius = radius_km * 1000.0
    rho = 3300.0 * (1.0 - np.clip(porosity, 0.0, 0.8))
    cp = 1000.0
    k = 2.0 * max(1.0 - porosity, 0.1)
    surface_t = 180.0

    def rhs(t: float, y: np.ndarray) -> np.ndarray:
        temp = y[0]
        conduction = -3.0 * k * (temp - surface_t) / max(rho * cp * radius * radius, 1e-12)
        heating = _al26_heat(t + formation_time_myr, al26_ratio) / cp
        seconds_per_myr = 365.25 * 86400 * 1e6
        return np.array([(conduction + heating) * seconds_per_myr])

    sol = solve_ivp(rhs, (0, t_end_myr), [surface_t], max_step=0.02, rtol=1e-7, atol=1e-8)
    peak = float(np.max(sol.y[0]))
    return {
        "peak_temperature_k": peak,
        "melted_silicate": float(peak >= 1400.0),
        "differentiated_metal": float(peak >= 1250.0),
    }


def thermal_population(bodies: pd.DataFrame) -> PlanetaryAnalysis:
    outputs = []
    for row in bodies.itertuples(index=False):
        result = simulate_planetesimal_thermal(
            float(row.radius_km), float(row.porosity), float(row.formation_time_myr), float(row.al26_ratio)
        )
        outputs.append(result)
    peaks = np.array([x["peak_temperature_k"] for x in outputs])
    return PlanetaryAnalysis(
        {
            "median_peak_temperature_k": float(np.median(peaks)) if len(peaks) else float("nan"),
            "melt_fraction": float(np.mean([x["melted_silicate"] for x in outputs])) if outputs else 0.0,
            "differentiate_fraction": float(np.mean([x["differentiated_metal"] for x in outputs])) if outputs else 0.0,
        },
        {"body_outputs": outputs},
    )


def partition_meta_regression(frame: pd.DataFrame) -> PlanetaryAnalysis:
    f = frame.copy()
    for col in ["pressure_gpa", "temperature_k", "delta_iw", "logD", "uncertainty"]:
        f[col] = pd.to_numeric(f[col], errors="coerce")
    f = f.dropna(subset=["logD", "pressure_gpa", "temperature_k", "delta_iw"])
    if len(f) < 8:
        return PlanetaryAnalysis({"r2": float("nan")}, {"reason": "Données insuffisantes"})
    model = ols("logD ~ pressure_gpa + temperature_k + delta_iw + C(element)", data=f).fit()
    return PlanetaryAnalysis(
        {"r2": float(model.rsquared), "rmse": float(np.sqrt(np.mean(model.resid**2))), "n": float(len(f))},
        {"parameters": {k: float(v) for k, v in model.params.items()}},
    )


def volatile_closure(frame: pd.DataFrame) -> PlanetaryAnalysis:
    f = frame.copy()
    cols = ["initial_mass", "core_mass", "mantle_mass", "atmosphere_mass", "lost_mass"]
    for col in cols:
        f[col] = pd.to_numeric(f[col], errors="coerce").fillna(0.0)
    recovered = f[["core_mass", "mantle_mass", "atmosphere_mass", "lost_mass"]].sum(axis=1)
    rel_error = (recovered - f["initial_mass"]).abs() / f["initial_mass"].abs().replace(0, np.nan)
    retained = (f["core_mass"] + f["mantle_mass"] + f["atmosphere_mass"]) / f["initial_mass"].replace(0, np.nan)
    return PlanetaryAnalysis(
        {"median_mass_balance_error": float(rel_error.median(skipna=True) or 0.0), "median_retained_fraction": float(retained.median(skipna=True) or 0.0)},
        {"rows": len(f)},
    )


def late_accretion_mixture(frame: pd.DataFrame) -> PlanetaryAnalysis:
    f = frame.copy()
    f["final_value"] = pd.to_numeric(f["final_value"], errors="coerce")
    source_means = f.groupby("candidate_source")["final_value"].mean().sort_values()
    spread = float(source_means.max() - source_means.min()) if len(source_means) else 0.0
    return PlanetaryAnalysis(
        {"candidate_sources": float(len(source_means)), "between_source_spread": spread},
        {"source_means": source_means.to_dict()},
    )


def incremental_history_value(frame: pd.DataFrame) -> PlanetaryAnalysis:
    f = frame.copy()
    layers = ["initial_composition", "provenance", "accretion_time", "thermal_history", "redox_history", "losses", "late_inputs"]
    target = f["final_partition"].astype(str)
    scores = {}
    # Information proxy: conditional uniqueness of target for progressively richer histories.
    for i in range(1, len(layers) + 1):
        keys = layers[:i]
        grouped = f.groupby(keys, dropna=False)["final_partition"].nunique()
        scores[f"layers_{i}"] = float((grouped == 1).mean()) if len(grouped) else 0.0
    gains = np.diff([0.0] + list(scores.values()))
    return PlanetaryAnalysis(
        {"final_determinism": float(list(scores.values())[-1] if scores else 0.0), "max_incremental_gain": float(max(gains, default=0.0))},
        {"layer_scores": scores},
    )


def exoplanet_observational_demography(frame: pd.DataFrame) -> PlanetaryAnalysis:
    """Audit descriptif de mesures publiées, sans imputation ni classification physique."""
    f = frame.copy()
    numeric = [
        "discovery_year", "orbital_period_days", "radius_earth", "mass_earth",
        "density_g_cm3", "equilibrium_temperature_k", "stellar_teff_k",
        "stellar_radius_solar", "stellar_mass_solar", "system_planet_count",
    ]
    for column in numeric:
        f[column] = pd.to_numeric(f[column], errors="coerce")
    n = len(f)
    if n == 0 or f["planet_name"].astype(str).duplicated().any():
        return PlanetaryAnalysis({"rows": float(n), "unique_planet_fraction": 0.0}, {"reason": "Jeu vide ou plusieurs solutions pour une même planète"})
    coverage = {column: float(f[column].notna().mean()) for column in numeric}
    joint = f.dropna(subset=["radius_earth", "mass_earth", "density_g_cm3"])
    if len(joint):
        density_from_mass_radius = 5.514 * joint["mass_earth"] / joint["radius_earth"].pow(3)
        relative_error = (density_from_mass_radius - joint["density_g_cm3"]).abs() / joint["density_g_cm3"].abs()
        median_density_error = float(relative_error.replace([np.inf, -np.inf], np.nan).median())
    else:
        median_density_error = float("nan")
    method_counts = f["discovery_method"].fillna("non_renseignée").value_counts().to_dict()
    return PlanetaryAnalysis(
        {"rows": float(n), "unique_planet_fraction": 1.0, "mass_radius_density_joint_coverage": float(len(joint) / n), "median_published_density_consistency_error": median_density_error, "discovery_methods": float(len(method_counts))},
        {"coverage": coverage, "discovery_method_counts": {str(k): int(v) for k, v in method_counts.items()}, "joint_mass_radius_density_rows": int(len(joint)), "interpretation_limit": "Audit descriptif; aucune valeur manquante imputée, aucune simulation, aucune inférence d'habitabilité."},
    )
