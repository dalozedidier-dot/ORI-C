"""Campagne C — indépendance, identifiabilité et capacité structurelle.

Étapes :
  C1  Robustesse à la définition du forçage. LR04 est accordé à l'insolation
      du 21 juin à 65°N. On refait le test avec d'autres définitions calculées
      depuis le même fichier La2004 : latitudes, saisons, énergie estivale
      intégrée, et composantes orbitales séparées.
  C2  Profil de vraisemblance : chaque paramètre de M2 est fixé sur une grille
      et les autres sont réoptimisés. Les paramètres de mémoire sont-ils
      identifiés ou plats ?
  C3  Stabilité des paramètres ajustés entre fenêtres et graines.
  C4  Capacité structurelle : en optimisant directement le rapport spectral
      100/41 ka au lieu de la RMSE, M2 peut-il seulement l'atteindre ?
  C5  Inversion du sens de prédiction : ajustement sur 1,2–0 Ma, prédiction sur
      2,6–1,2 Ma.
"""

from __future__ import annotations

import argparse
import json
import math
import time

import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution

from core import (
    BOUNDS_SETS,
    MODEL_CODE,
    OUTPUT_ROOT,
    PARAMETER_NAMES,
    PROJECT_ROOT,
    PowerRatio,
    _simulate_core,
    decode,
    effective_sample_size,
    fit_best_of_seeds,
    information_criteria,
    optimization_bounds,
    rmse,
    simulate,
)
from oric_memory_tests.data import daily_mean_insolation, load_la2004, load_lr04
from oric_memory_tests.metrics import correlation, log_ratio_error, mpt_power_ratio

OUT = OUTPUT_ROOT / "independence"
MODELS = ("M0", "M1", "M2", "M1P")
BUDGET = {"max_iterations": 500, "population_size": 16, "tol": 1e-8}
BUDGET_LIGHT = {"max_iterations": 250, "population_size": 12, "tol": 1e-7}


# --------------------------------------------------------------------------
# Forçages alternatifs
# --------------------------------------------------------------------------

def build_forcings(start_age_kyr=2600, end_age_kyr=0):
    raw = PROJECT_ROOT / "data" / "raw"
    lr04 = load_lr04(raw / "lisiecki2005-d18o-stack-noaa.txt")
    orbital = load_la2004(raw / "INSOLN.LA2004.BTL.ASC").sort_values("time_kyr_j2000")

    age = np.arange(start_age_kyr, end_age_kyr - 1, -1, dtype=float)
    orbital_time = orbital["time_kyr_j2000"].to_numpy()
    requested = -age
    eccentricity = np.interp(requested, orbital_time, orbital["eccentricity"])
    obliquity = np.interp(requested, orbital_time, orbital["obliquity_rad"])
    varpi = np.interp(requested, orbital_time, orbital["varpi_rad"])
    observed = np.interp(age, lr04["age_calkaBP"], lr04["d18O_benthic"])

    def insolation(latitude, solar_longitude):
        return daily_mean_insolation(
            latitude, solar_longitude, eccentricity, obliquity, varpi
        )

    forcings = {
        # Définition livrée : celle qui a servi à accorder la chronologie LR04.
        "juin65N_livre": insolation(65.0, np.pi / 2.0),
        "juin45N": insolation(45.0, np.pi / 2.0),
        "juin55N": insolation(55.0, np.pi / 2.0),
        "juin75N": insolation(75.0, np.pi / 2.0),
        "juin65S": insolation(-65.0, np.pi / 2.0),
        "decembre65N": insolation(65.0, 3.0 * np.pi / 2.0),
        "equinoxe_mars_65N": insolation(65.0, 0.0),
        # Énergie estivale intégrée à 65°N sur la moitié claire de l'année.
        "energie_estivale_65N": np.mean(
            [insolation(65.0, angle)
             for angle in np.linspace(0.0, np.pi, 25)], axis=0
        ),
        # Composantes orbitales nues, sans passage par l'insolation.
        "obliquite_seule": np.rad2deg(obliquity),
        "excentricite_seule": eccentricity,
        "precession_climatique": eccentricity * np.sin(varpi),
    }
    return age, observed, forcings


def standardise_pair(observed_raw, forcing_raw, training_mask):
    observed = (observed_raw - observed_raw[training_mask].mean()) / observed_raw[
        training_mask
    ].std()
    forcing = (forcing_raw - forcing_raw[training_mask].mean()) / forcing_raw[
        training_mask
    ].std()
    return observed, forcing


# --------------------------------------------------------------------------

def stage_forcings(age, observed_raw, forcings, seeds) -> dict:
    """C1 : le verdict dépend-il de la définition du forçage ?"""
    training_mask = age >= 1200
    prediction_mask = ~training_mask
    rows = []
    for name, forcing_raw in forcings.items():
        observed, forcing = standardise_pair(observed_raw, forcing_raw, training_mask)
        row = {"forcing": name}
        predictions = {}
        for model in MODELS:
            best, _ = fit_best_of_seeds(
                model, forcing, observed, training_mask, seeds,
                bounds_name="wide", **BUDGET,
            )
            predictions[model] = simulate(model, forcing, observed[0], best.vector)
            row[f"rmse_{model}"] = rmse(
                observed[prediction_mask], predictions[model][prediction_mask]
            )
        row["gain_M2_vs_M1"] = 1.0 - row["rmse_M2"] / row["rmse_M1"]
        row["gain_M2_vs_M1P"] = 1.0 - row["rmse_M2"] / row["rmse_M1P"]
        row["gain_M2_vs_M0"] = 1.0 - row["rmse_M2"] / row["rmse_M0"]
        row["correlation_M2"] = correlation(
            observed[prediction_mask], predictions["M2"][prediction_mask]
        )
        row["power_ratio_M2"] = mpt_power_ratio(predictions["M2"][prediction_mask])
        row["power_ratio_observed"] = mpt_power_ratio(observed[prediction_mask])
        rows.append(row)
        print(f"  {name}: gain/M1={row['gain_M2_vs_M1']:+.4f} "
              f"gain/M1P={row['gain_M2_vs_M1P']:+.4f} "
              f"r={row['correlation_M2']:.3f}", flush=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(OUT / "c_forcing_robustness.csv", index=False)
    return {
        "forcings_tested": len(rows),
        "gain_vs_M1_min": float(frame["gain_M2_vs_M1"].min()),
        "gain_vs_M1_max": float(frame["gain_M2_vs_M1"].max()),
        "count_gain_above_5pct_vs_M1": int((frame["gain_M2_vs_M1"] >= 0.05).sum()),
        "count_gain_above_5pct_vs_M1P": int((frame["gain_M2_vs_M1P"] >= 0.05).sum()),
        "best_correlation_M2": float(frame["correlation_M2"].max()),
        "best_correlation_forcing": str(
            frame.loc[frame["correlation_M2"].idxmax(), "forcing"]
        ),
        "max_power_ratio_M2": float(frame["power_ratio_M2"].max()),
    }


# --------------------------------------------------------------------------

def fit_with_fixed(model, forcing, observed, training_mask, fixed_index,
                   fixed_value, seed, budget):
    """Ajuste `model` avec un paramètre gelé à `fixed_value` (échelle décodée)."""
    spec = BOUNDS_SETS["wide"][model]
    all_bounds = optimization_bounds(model, "wide")
    free = [index for index in range(len(spec)) if index != fixed_index]
    bounds = [all_bounds[index] for index in free]
    code = MODEL_CODE[model]
    training_index = np.flatnonzero(training_mask)
    forcing = np.ascontiguousarray(forcing, dtype=float)
    observed = np.ascontiguousarray(observed, dtype=float)

    def objective(vector):
        decoded = np.zeros(9)
        for position, index in enumerate(free):
            value = vector[position]
            decoded[index] = math.exp(value) if spec[index][2] else value
        decoded[fixed_index] = fixed_value
        predicted = _simulate_core(code, forcing, observed[0], decoded)
        if not np.all(np.isfinite(predicted)) or np.max(np.abs(predicted)) > 20.0:
            return 1e6
        residual = observed[training_index] - predicted[training_index]
        return float(np.sqrt(np.mean(residual * residual)))

    result = differential_evolution(
        objective, bounds, seed=seed, polish=True, workers=1,
        updating="immediate", init="sobol",
        maxiter=budget["max_iterations"], popsize=budget["population_size"],
        tol=budget["tol"],
    )
    decoded = np.zeros(9)
    for position, index in enumerate(free):
        value = result.x[position]
        decoded[index] = math.exp(value) if spec[index][2] else value
    decoded[fixed_index] = fixed_value
    return float(result.fun), decoded[: len(spec)]


def stage_profile(age, observed_raw, forcings, seed, grid_size) -> dict:
    """C2 : profil de RMSE d'apprentissage paramètre par paramètre."""
    training_mask = age >= 1200
    prediction_mask = ~training_mask
    observed, forcing = standardise_pair(
        observed_raw, forcings["juin65N_livre"], training_mask
    )
    best, _ = fit_best_of_seeds(
        "M2", forcing, observed, training_mask, [seed, seed + 37, seed + 74],
        bounds_name="wide", max_iterations=1200, population_size=20, tol=1e-9,
    )
    baseline = best.training_rmse
    names = PARAMETER_NAMES["M2"]
    spec = BOUNDS_SETS["wide"]["M2"]
    rows = []
    for index, name in enumerate(names):
        lower, upper, logarithmic = spec[index]
        grid = (
            np.geomspace(lower, upper, grid_size)
            if logarithmic
            else np.linspace(lower, upper, grid_size)
        )
        for value in grid:
            training_rmse, vector = fit_with_fixed(
                "M2", forcing, observed, training_mask, index, float(value),
                seed, BUDGET_LIGHT,
            )
            predicted = simulate("M2", forcing, observed[0], vector)
            rows.append({
                "parameter": name,
                "fixed_value": float(value),
                "training_rmse": training_rmse,
                "excess_over_best": training_rmse - baseline,
                "relative_excess": (training_rmse - baseline) / baseline,
                "prediction_rmse": rmse(
                    observed[prediction_mask], predicted[prediction_mask]
                ),
            })
        print(f"  profil {name} terminé", flush=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(OUT / "c_profile_likelihood.csv", index=False)

    summary = {"best_training_rmse": baseline,
               "best_parameters": best.parameters, "parameters": {}}
    for name in names:
        subset = frame.loc[frame["parameter"] == name]
        # Un paramètre est jugé identifié si geler sa valeur sur la grille
        # dégrade la RMSE d'apprentissage d'au moins 1 % quelque part.
        within = subset.loc[subset["relative_excess"] <= 0.01, "fixed_value"]
        summary["parameters"][name] = {
            "max_relative_excess": float(subset["relative_excess"].max()),
            "flat_fraction_within_1pct": float(
                (subset["relative_excess"] <= 0.01).mean()
            ),
            "identified_range_low": float(within.min()) if len(within) else None,
            "identified_range_high": float(within.max()) if len(within) else None,
            "identified": bool(subset["relative_excess"].max() > 0.01
                               and (subset["relative_excess"] <= 0.01).mean() < 0.5),
        }
    return summary


# --------------------------------------------------------------------------

def stage_capacity(age, observed_raw, forcings, seed) -> dict:
    """C4 : M2 peut-il produire le régime de 100 ka, et à quel prix ?

    Test de capacité structurelle, pas de validation : la fenêtre de prédiction
    est ici utilisée comme oracle. La question posée est « la classe de modèles
    est-elle seulement capable du régime cible ? ». Deux formes :

    1. Capacité libre : on minimise la seule erreur logarithmique sur le rapport
       de puissance 100/41 ka. Si la cible est inatteignable, l'échec spectral
       est structurel.
    2. Front de compromis : on impose en plus un plafond de RMSE hors
       échantillon et on cherche le meilleur rapport spectral compatible. Cela
       mesure le coût, en qualité d'ajustement, d'un déplacement vers la bande
       de 100 ka.
    """
    training_mask = age >= 1200
    prediction_mask = ~training_mask
    observed, forcing = standardise_pair(
        observed_raw, forcings["juin65N_livre"], training_mask
    )
    ratio_of = PowerRatio(int(prediction_mask.sum()))
    target_ratio = ratio_of(observed[prediction_mask])
    lower_target = target_ratio / 2.0

    # Référence honnête : RMSE hors échantillon obtenue par ajustement normal.
    honest = {}
    for model in ("M1", "M2", "M1P"):
        best, _ = fit_best_of_seeds(
            model, forcing, observed, training_mask, [seed, seed + 37, seed + 74],
            bounds_name="wide", **BUDGET,
        )
        predicted = simulate(model, forcing, observed[0], best.vector)
        honest[model] = {
            "prediction_rmse": rmse(
                observed[prediction_mask], predicted[prediction_mask]
            ),
            "power_ratio": float(ratio_of(predicted[prediction_mask])),
        }

    results = {
        "observed_power_ratio": float(target_ratio),
        "factor_2_lower_bound": float(lower_target),
        "honest_fit": honest,
        "note": (
            "Test de capacité : la fenêtre de prédiction sert d'oracle. "
            "Un succès ici ne vaut pas validation, un échec vaut réfutation "
            "structurelle."
        ),
    }

    def make_objective(model, rmse_cap):
        spec = BOUNDS_SETS["wide"][model]
        code = MODEL_CODE[model]

        def objective(vector):
            decoded = np.zeros(9)
            for index, (_, _, logarithmic) in enumerate(spec):
                decoded[index] = (
                    math.exp(vector[index]) if logarithmic else vector[index]
                )
            predicted = _simulate_core(code, forcing, observed[0], decoded)
            if not np.all(np.isfinite(predicted)) or np.max(np.abs(predicted)) > 20.0:
                return 1e6
            window = predicted[prediction_mask]
            if np.std(window) < 1e-6:
                return 1e6
            penalty = 0.0
            if rmse_cap is not None:
                excess = rmse(observed[prediction_mask], window) / rmse_cap - 1.0
                if excess > 0.0:
                    penalty = 50.0 * excess
            return log_ratio_error(ratio_of(window), target_ratio) + penalty

        return objective

    rows = []
    for model in ("M1", "M2", "M1P"):
        bounds = optimization_bounds(model, "wide")
        reference_rmse = honest["M1"]["prediction_rmse"]
        caps = [None] + [
            reference_rmse * factor for factor in (1.00, 1.05, 1.15, 1.30, 1.60, 2.00)
        ]
        for cap in caps:
            result = differential_evolution(
                make_objective(model, cap), bounds, seed=seed, maxiter=400,
                popsize=14, tol=1e-9, polish=True, workers=1,
                updating="immediate", init="sobol",
            )
            values = decode(model, result.x, "wide")
            predicted = simulate(model, forcing, observed[0], values)
            achieved = float(ratio_of(predicted[prediction_mask]))
            achieved_rmse = rmse(
                observed[prediction_mask], predicted[prediction_mask]
            )
            rows.append({
                "model": model,
                "rmse_cap": float("nan") if cap is None else float(cap),
                "rmse_cap_ratio_to_M1": (
                    float("nan") if cap is None else float(cap / reference_rmse)
                ),
                "achieved_power_ratio": achieved,
                "achieved_prediction_rmse": achieved_rmse,
                "cap_respected": bool(cap is None or achieved_rmse <= cap * 1.001),
                "reaches_factor_2_band": bool(
                    lower_target <= achieved <= target_ratio * 2.0
                ),
            })
        best_free = rows[-len(caps)]
        print(f"  capacité {model}: ratio libre max = "
              f"{best_free['achieved_power_ratio']:.4g} "
              f"(cible {target_ratio:.4g}, RMSE à ce point "
              f"{best_free['achieved_prediction_rmse']:.3f})", flush=True)

    frame = pd.DataFrame(rows)
    frame.to_csv(OUT / "c_spectral_tradeoff.csv", index=False)
    results["tradeoff"] = {}
    for model in ("M1", "M2", "M1P"):
        subset = frame.loc[frame["model"] == model]
        free = subset.loc[subset["rmse_cap"].isna()].iloc[0]
        feasible = subset.loc[
            subset["reaches_factor_2_band"] & subset["cap_respected"]
            & subset["rmse_cap"].notna()
        ]
        results["tradeoff"][model] = {
            "free_best_power_ratio": float(free["achieved_power_ratio"]),
            "free_prediction_rmse": float(free["achieved_prediction_rmse"]),
            "structurally_capable": bool(free["reaches_factor_2_band"]),
            "min_rmse_ratio_reaching_band": (
                float(feasible["rmse_cap_ratio_to_M1"].min())
                if len(feasible) else None
            ),
            "reaches_band_without_degrading_below_M1": bool(
                len(feasible) and feasible["rmse_cap_ratio_to_M1"].min() <= 1.0
            ),
        }
    return results


# --------------------------------------------------------------------------

def stage_reverse(age, observed_raw, forcings, seeds) -> dict:
    """C5 : ajustement sur la fenêtre récente, prédiction du passé ancien."""
    training_mask = age < 1200          # 1,2–0 Ma sert à l'ajustement
    prediction_mask = ~training_mask    # 2,6–1,2 Ma est prédit
    observed, forcing = standardise_pair(
        observed_raw, forcings["juin65N_livre"], training_mask
    )
    output = {}
    predictions = {}
    for model in MODELS:
        best, _ = fit_best_of_seeds(
            model, forcing, observed, training_mask, seeds,
            bounds_name="wide", **BUDGET,
        )
        predictions[model] = simulate(model, forcing, observed[0], best.vector)
        residual = observed[prediction_mask] - predictions[model][prediction_mask]
        output[model] = {
            "prediction_rmse": rmse(
                observed[prediction_mask], predictions[model][prediction_mask]
            ),
            "correlation": correlation(
                observed[prediction_mask], predictions[model][prediction_mask]
            ),
            "bic_effective": information_criteria(
                residual, len(PARAMETER_NAMES[model]),
                sample_size=effective_sample_size(residual),
            )["bic"],
        }
    output["gain_M2_vs_M1"] = 1.0 - (
        output["M2"]["prediction_rmse"] / output["M1"]["prediction_rmse"]
    )
    output["gain_M2_vs_M1P"] = 1.0 - (
        output["M2"]["prediction_rmse"] / output["M1P"]["prediction_rmse"]
    )
    output["delta_bic_effective_M2_vs_M1"] = (
        output["M2"]["bic_effective"] - output["M1"]["bic_effective"]
    )
    return output


def stage_parameter_stability(age, observed_raw, forcings, seeds) -> dict:
    """C3 : les paramètres de mémoire de M2 sont-ils stables ?"""
    rows = []
    for split in (1000, 1100, 1200, 1300, 1400):
        training_mask = age >= split
        observed, forcing = standardise_pair(
            observed_raw, forcings["juin65N_livre"], training_mask
        )
        for seed in seeds:
            from core import fit_model
            fit = fit_model(
                "M2", forcing, observed, training_mask, seed=seed,
                bounds_name="wide", **BUDGET,
            )
            rows.append({"split_age_kyr": split, "seed": seed,
                         "training_rmse": fit.training_rmse, **fit.parameters})
        print(f"  stabilité split {split} terminée", flush=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(OUT / "c_parameter_stability.csv", index=False)
    summary = {}
    for name in PARAMETER_NAMES["M2"]:
        values = frame[name].to_numpy(dtype=float)
        summary[name] = {
            "min": float(values.min()),
            "max": float(values.max()),
            "median": float(np.median(values)),
            "orders_of_magnitude_spanned": float(
                math.log10(max(abs(values).max(), 1e-300)
                           / max(abs(values).min(), 1e-300))
            ),
            "sign_changes": bool(values.min() < 0 < values.max()),
        }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stages", default="forcings,capacity,reverse,stability,profile")
    parser.add_argument("--seeds", type=int, default=4)
    parser.add_argument("--grid", type=int, default=13)
    arguments = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    age, observed_raw, forcings = build_forcings()
    seeds = [729 + 37 * k for k in range(arguments.seeds)]
    report = {"forcing_definitions": list(forcings)}

    for stage in [s.strip() for s in arguments.stages.split(",") if s.strip()]:
        started = time.perf_counter()
        print(f"[C] étape {stage} ...", flush=True)
        if stage == "forcings":
            report["forcings"] = stage_forcings(age, observed_raw, forcings, seeds)
        elif stage == "profile":
            report["profile"] = stage_profile(
                age, observed_raw, forcings, seeds[0], arguments.grid
            )
        elif stage == "capacity":
            report["capacity"] = stage_capacity(age, observed_raw, forcings, seeds[0])
        elif stage == "reverse":
            report["reverse"] = stage_reverse(age, observed_raw, forcings, seeds)
        elif stage == "stability":
            report["stability"] = stage_parameter_stability(
                age, observed_raw, forcings, seeds
            )
        print(f"[C] {stage} terminé en {time.perf_counter() - started:.1f} s",
              flush=True)
        (OUT / "c_report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False, default=float),
            encoding="utf-8",
        )
    print(json.dumps(report, indent=2, ensure_ascii=False, default=float)[:6000])


if __name__ == "__main__":
    main()
