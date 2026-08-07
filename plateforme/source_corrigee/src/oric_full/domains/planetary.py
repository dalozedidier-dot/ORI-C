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
        return PlanetaryAnalysis(
            {"r2": float("nan"), "rmse": float("nan"), "n": float(len(f))},
            {
                "reason": "Données insuffisantes pour la méta-régression",
                "minimum_required": 8,
                "interpretation_limit": "La compilation et l'harmonisation restent auditables; aucun ajustement n'est revendiqué.",
            },
        )
    model = ols("logD ~ pressure_gpa + temperature_k + delta_iw + C(element)", data=f).fit()
    return PlanetaryAnalysis(
        {"r2": float(model.rsquared), "rmse": float(np.sqrt(np.mean(model.resid**2))), "n": float(len(f))},
        {"parameters": {k: float(v) for k, v in model.params.items()}},
    )


def volatile_closure(frame: pd.DataFrame) -> PlanetaryAnalysis:
    """Audit d'inventaires volatils sans transformer l'absence de mesure en zéro.

    Une fermeture de masse exacte n'est calculée que si la masse initiale et les
    quatre compartiments (noyau, manteau, atmosphère, pertes) sont tous publiés.
    Les lignes incomplètes restent informatives comme bornes inférieures de masse
    conservée, mais elles ne sont jamais déclarées fermées.
    """
    f = frame.copy()
    compartments = ["core_mass", "mantle_mass", "atmosphere_mass", "lost_mass"]
    cols = ["initial_mass", *compartments]
    for col in cols:
        f[col] = pd.to_numeric(f[col], errors="coerce")

    negative_cells = int((f[cols] < 0).sum().sum())
    known_retained = f[["core_mass", "mantle_mass", "atmosphere_mass"]].sum(
        axis=1, min_count=1
    )
    lower_bound = known_retained / f["initial_mass"].where(f["initial_mass"] > 0)

    complete = f[["initial_mass", *compartments]].notna().all(axis=1) & (f["initial_mass"] > 0)
    if complete.any():
        recovered = f.loc[complete, compartments].sum(axis=1)
        rel_error = (recovered - f.loc[complete, "initial_mass"]).abs() / f.loc[complete, "initial_mass"].abs()
        median_exact_error = float(rel_error.median())
        max_exact_error = float(rel_error.max())
    else:
        rel_error = pd.Series(dtype=float)
        median_exact_error = float("nan")
        max_exact_error = float("nan")

    rows = []
    for idx, row in f.iterrows():
        rows.append({
            "sample_id": str(row.get("sample_id", idx)),
            "volatile": str(row.get("volatile", "")),
            "initial_mass_published": bool(pd.notna(row.get("initial_mass"))),
            "known_retained_compartments": int(sum(pd.notna(row.get(c)) for c in ["core_mass", "mantle_mass", "atmosphere_mass"])),
            "lost_mass_published": bool(pd.notna(row.get("lost_mass"))),
            "exact_closure_computable": bool(complete.loc[idx]),
            "known_retained_fraction_lower_bound": (
                float(lower_bound.loc[idx]) if pd.notna(lower_bound.loc[idx]) else None
            ),
        })

    return PlanetaryAnalysis(
        {
            "rows": float(len(f)),
            "rows_with_initial_mass": float(f["initial_mass"].notna().sum()),
            "complete_budget_rows": float(complete.sum()),
            "incomplete_budget_rows": float((~complete).sum()),
            "negative_mass_cells": float(negative_cells),
            "median_exact_mass_balance_error": median_exact_error,
            "max_exact_mass_balance_error": max_exact_error,
            "median_known_retained_fraction_lower_bound": float(lower_bound.median(skipna=True)) if lower_bound.notna().any() else float("nan"),
        },
        {
            "row_audit": rows,
            "interpretation_limit": (
                "Les compartiments absents restent inconnus. Une somme partielle est seulement une borne "
                "inférieure de masse conservée; aucune fermeture n'est inférée tant que lost_mass et les "
                "autres compartiments requis ne sont pas tous publiés."
            ),
        },
    )


def late_accretion_mixture(frame: pd.DataFrame) -> PlanetaryAnalysis:
    """Audit de compilation HSE/Mo-W, sans prétendre résoudre un mélange tardif.

    ``candidate_source`` est conservé comme famille géologique documentée par la
    source. Il n'est jamais traité comme un pôle de mélange planétaire.
    """
    f = frame.copy()
    f["tracer"] = f["tracer"].astype(str).str.upper().str.strip()
    f["final_value"] = pd.to_numeric(f["final_value"], errors="coerce")
    f["uncertainty"] = pd.to_numeric(f.get("uncertainty"), errors="coerce")
    f = f[f["final_value"].notna() & (f["final_value"] > 0)].copy()

    required = {"MO", "RU", "W", "OS", "IR", "AU"}
    observed = set(f["tracer"].unique())
    counts = f["tracer"].value_counts().sort_index()
    per_sample = f.groupby("sample_id")["tracer"].nunique()
    unit_counts = (
        f.groupby("tracer")["unit"].nunique(dropna=True)
        if "unit" in f.columns else pd.Series(dtype=int)
    )
    inconsistent_units = sorted(unit_counts[unit_counts > 1].index.astype(str).tolist())

    return PlanetaryAnalysis(
        {
            "rows": float(len(f)),
            "samples": float(f["sample_id"].nunique()),
            "tracers": float(len(observed)),
            "required_tracer_coverage_fraction": float(len(required & observed) / len(required)),
            "samples_with_two_or_more_tracers": float((per_sample >= 2).sum()),
            "uncertainty_coverage": float(f["uncertainty"].notna().mean()),
            "candidate_source_families": float(f["candidate_source"].nunique()),
            "unit_inconsistency_count": float(len(inconsistent_units)),
        },
        {
            "tracer_counts": {str(k): int(v) for k, v in counts.items()},
            "required_tracers": sorted(required),
            "missing_required_tracers": sorted(required - observed),
            "inconsistent_unit_tracers": inconsistent_units,
            "compilations": sorted(f.get("compilation", pd.Series(dtype=str)).dropna().astype(str).unique().tolist()),
            "interpretation_limit": (
                "Audit de couverture d'une compilation géochimique mesurée. candidate_source décrit une "
                "famille rocheuse/tectonique GEOROC, pas un pôle de mélange d'accrétion. Aucune date, masse "
                "d'apport, histoire d'impact ou fraction de mélange n'est inférée."
            ),
        },
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
