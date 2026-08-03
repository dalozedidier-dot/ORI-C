"""Campagne A — durcissement du test MPT.

Étapes :
  A1  Reproduction du budget livré (référence).
  A2  Optimisation à budget élevé, multi-graines, bornes de référence.
  A3  Optimisation à budget élevé, bornes élargies (audit des bornes touchées).
  A4  Contrôle M1P : mêmes 9 paramètres que M2, mais l'état lent est piloté
      par le forçage externe et non par la réponse passée.
  A5  Statistiques robustes : autocorrélation, n_eff, BIC corrigé,
      bootstrap par blocs mobiles.
  A6  Sensibilité à la fenêtre de séparation calibration/prédiction.
  A7  Nuls par surrogates : cible à phases aléatoires et forçage à phases
      aléatoires.
  A8  Ablation de la mémoire carbone de M2.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd

from core import (
    OUTPUT_ROOT,
    PARAMETER_COUNT,
    PARAMETER_NAMES,
    PROJECT_ROOT,
    effective_sample_size,
    fit_best_of_seeds,
    fit_model,
    fourier_surrogate,
    information_criteria,
    lag1_autocorrelation,
    moving_block_bootstrap_gain,
    moving_block_bootstrap_gain as _mbb,
    paired_wilcoxon_greater,
    rmse,
    simulate,
)
from oric_memory_tests.data import prepare_mpt_dataset
from oric_memory_tests.metrics import (
    contiguous_block_scores,
    correlation,
    event_timing_mae,
    log_ratio_error,
    mpt_power_ratio,
    termination_events,
)

OUT = OUTPUT_ROOT / "mpt"
MODELS = ("M0", "M1", "M2", "M1P")

# Budget « livré » et budget « maximal ».
BUDGET_DELIVERED = {"max_iterations": 30, "population_size": 6, "tol": 1e-5}
BUDGET_HIGH = {"max_iterations": 1200, "population_size": 20, "tol": 1e-9}
BUDGET_MEDIUM = {"max_iterations": 400, "population_size": 14, "tol": 1e-8}


def load_dataset():
    dataset, quality = prepare_mpt_dataset(PROJECT_ROOT / "data" / "raw", None)
    return dataset, quality


def standardise(dataset, split_age_kyr: int):
    training_mask = dataset["age_kyr_bp"].to_numpy() >= split_age_kyr
    observed_raw = dataset["d18o_permil"].to_numpy()
    forcing_raw = dataset["insolation_65n_june_wm2"].to_numpy()
    observed = (observed_raw - observed_raw[training_mask].mean()) / observed_raw[
        training_mask
    ].std()
    forcing = (forcing_raw - forcing_raw[training_mask].mean()) / forcing_raw[
        training_mask
    ].std()
    return observed, forcing, training_mask


def evaluate(observed, predicted, elapsed, mask, parameter_count,
             observed_ratio) -> dict:
    o = observed[mask]
    p = predicted[mask]
    residual = o - p
    ratio = mpt_power_ratio(p)
    n_eff = effective_sample_size(residual)
    naive = information_criteria(residual, parameter_count)
    corrected = information_criteria(residual, parameter_count, sample_size=n_eff)
    return {
        "rmse": rmse(o, p),
        "correlation": correlation(o, p),
        "power_ratio_100k_41k": ratio,
        "power_ratio_log_error": log_ratio_error(ratio, observed_ratio),
        "termination_timing_mae_kyr": event_timing_mae(
            termination_events(o, elapsed[mask]),
            termination_events(p, elapsed[mask]),
        ),
        "residual_lag1_autocorrelation": lag1_autocorrelation(residual),
        "effective_sample_size": n_eff,
        "sample_size": int(mask.sum()),
        "bic_naive": naive["bic"],
        "bic_effective": corrected["bic"],
        "aic_naive": naive["aic"],
        "aic_effective": corrected["aic"],
    }


_FIT_CACHE: dict = {}


def _cache_key(model, observed, forcing, training_mask, seeds, budget, bounds_name):
    digest = hash((
        observed.tobytes(), forcing.tobytes(), training_mask.tobytes(),
    ))
    return (model, digest, tuple(seeds), tuple(sorted(budget.items())), bounds_name)


def fit_all(observed, forcing, training_mask, models, seeds, budget,
            bounds_name="reference"):
    """Ajuste chaque modèle en repartant de plusieurs graines indépendantes.

    Les résultats sont mémorisés : plusieurs étapes réutilisent exactement le
    même ajustement, il ne doit jamais être recalculé différemment.
    """
    fits = {}
    runs = {}
    for model in models:
        key = _cache_key(model, observed, forcing, training_mask, seeds,
                         budget, bounds_name)
        if key not in _FIT_CACHE:
            _FIT_CACHE[key] = fit_best_of_seeds(
                model, forcing, observed, training_mask, seeds,
                bounds_name=bounds_name, **budget,
            )
        best, all_runs = _FIT_CACHE[key]
        fits[model] = best
        runs[model] = all_runs
    return fits, runs


def assemble(dataset, observed, forcing, training_mask, fits, label):
    elapsed = dataset["elapsed_kyr"].to_numpy()
    prediction_mask = ~training_mask
    observed_ratio = mpt_power_ratio(observed[prediction_mask])
    rows = []
    predictions = {}
    for model, fit in fits.items():
        predicted = simulate(model, forcing, observed[0], fit.vector)
        predictions[model] = predicted
        for interval, mask in (
            ("calibration", training_mask), ("prediction", prediction_mask)
        ):
            reference_ratio = mpt_power_ratio(observed[mask])
            row = {
                "campaign": label,
                "model": model,
                "interval": interval,
                "parameter_count": PARAMETER_COUNT[model],
                "training_rmse": fit.training_rmse,
                "optimizer_converged": fit.converged,
                "optimizer_iterations": fit.iterations,
                "optimizer_evaluations": fit.evaluations,
                "boundary_hits": ";".join(fit.boundary_hits) or "aucun",
                "observed_power_ratio": reference_ratio,
            }
            row.update(
                evaluate(observed, predicted, elapsed, mask,
                         PARAMETER_COUNT[model], reference_ratio)
            )
            rows.append(row)
    return pd.DataFrame(rows), predictions, observed_ratio


def gain(metrics: pd.DataFrame, reference: str, candidate: str) -> dict:
    frame = metrics.set_index(["interval", "model"])
    ref = frame.loc[("prediction", reference)]
    cand = frame.loc[("prediction", candidate)]
    return {
        "reference": reference,
        "candidate": candidate,
        "rmse_reference": float(ref["rmse"]),
        "rmse_candidate": float(cand["rmse"]),
        "rmse_gain": float(1.0 - cand["rmse"] / ref["rmse"]),
        "delta_bic_naive": float(cand["bic_naive"] - ref["bic_naive"]),
        "delta_bic_effective": float(cand["bic_effective"] - ref["bic_effective"]),
        "correlation_candidate": float(cand["correlation"]),
        "power_ratio_candidate": float(cand["power_ratio_100k_41k"]),
    }


# --------------------------------------------------------------------------

def stage_budget(dataset, seeds_high, out: Path) -> dict:
    """A1 + A2 + A3 + A4 : budget livré, budget élevé, bornes élargies, M1P."""
    observed, forcing, training_mask = standardise(dataset, 1200)
    results = {}
    frames = []

    started = time.perf_counter()
    fits, _ = fit_all(observed, forcing, training_mask, ("M0", "M1", "M2"),
                      [729, 730, 731], BUDGET_DELIVERED)
    metrics, _, _ = assemble(dataset, observed, forcing, training_mask, fits,
                             "budget_livre")
    frames.append(metrics)
    results["budget_livre"] = {
        "gains": [gain(metrics, "M1", "M2")],
        "seconds": time.perf_counter() - started,
    }

    for bounds_name in ("reference", "wide"):
        started = time.perf_counter()
        fits, runs = fit_all(observed, forcing, training_mask, MODELS,
                             seeds_high, BUDGET_HIGH, bounds_name=bounds_name)
        label = f"budget_maximal_bornes_{bounds_name}"
        metrics, predictions, _ = assemble(
            dataset, observed, forcing, training_mask, fits, label
        )
        frames.append(metrics)

        spread = {}
        for model, model_runs in runs.items():
            values = np.array([run.training_rmse for run in model_runs])
            spread[model] = {
                "training_rmse_min": float(values.min()),
                "training_rmse_max": float(values.max()),
                "training_rmse_std": float(values.std()),
                "relative_spread": float((values.max() - values.min())
                                         / max(values.min(), 1e-12)),
                "converged_count": int(sum(run.converged for run in model_runs)),
                "seed_count": len(model_runs),
            }
        results[label] = {
            "gains": [
                gain(metrics, "M1", "M2"),
                gain(metrics, "M1P", "M2"),
                gain(metrics, "M0", "M1"),
                gain(metrics, "M0", "M2"),
            ],
            "multi_seed_spread": spread,
            "parameters": {m: f.parameters for m, f in fits.items()},
            "boundary_hits": {m: f.boundary_hits for m, f in fits.items()},
            "seconds": time.perf_counter() - started,
        }
        if bounds_name == "wide":
            frame = pd.DataFrame({
                "age_kyr_bp": dataset["age_kyr_bp"].to_numpy(),
                "observed_standardized": observed,
                "forcing_standardized": forcing,
                **{model: predictions[model] for model in MODELS},
            })
            frame.to_csv(out / "a_predictions_wide.csv", index=False)

    pd.concat(frames).to_csv(out / "a_budget_metrics.csv", index=False)
    return results


def stage_robust(dataset, seeds_high, out: Path) -> dict:
    """A5 : statistiques robustes sur le meilleur ajustement à bornes élargies."""
    observed, forcing, training_mask = standardise(dataset, 1200)
    prediction_mask = ~training_mask
    fits, _ = fit_all(observed, forcing, training_mask, MODELS, seeds_high,
                      BUDGET_HIGH, bounds_name="wide")
    predictions = {
        model: simulate(model, forcing, observed[0], fit.vector)
        for model, fit in fits.items()
    }
    o = observed[prediction_mask]
    rng = np.random.default_rng(4242)

    residual_reference = o - predictions["M1"][prediction_mask]
    rho = lag1_autocorrelation(residual_reference)
    decorrelation_kyr = -1.0 / math.log(abs(rho)) if 0 < abs(rho) < 1 else float("inf")

    output = {
        "residual_lag1_autocorrelation_M1": rho,
        "decorrelation_time_kyr": decorrelation_kyr,
        "n_actual": int(prediction_mask.sum()),
        "n_effective_M1": effective_sample_size(residual_reference),
        "comparisons": [],
    }

    for reference in ("M0", "M1", "M1P"):
        gains = moving_block_bootstrap_gain(
            o, predictions[reference][prediction_mask],
            predictions["M2"][prediction_mask],
            block_length=int(max(10, round(5 * decorrelation_kyr))),
            draws=20000, rng=rng,
        )
        blocks = pd.DataFrame(contiguous_block_scores(
            o,
            {reference: predictions[reference][prediction_mask],
             "M2": predictions["M2"][prediction_mask]},
            block_size=50,
        ))
        p_block = paired_wilcoxon_greater(
            blocks[f"rmse_{reference}"].to_numpy(), blocks["rmse_M2"].to_numpy()
        )
        point = 1.0 - rmse(o, predictions["M2"][prediction_mask]) / rmse(
            o, predictions[reference][prediction_mask]
        )
        output["comparisons"].append({
            "reference": reference,
            "rmse_gain_point": float(point),
            "bootstrap_block_length_kyr": int(max(10, round(5 * decorrelation_kyr))),
            "rmse_gain_ci_2.5": float(np.percentile(gains, 2.5)),
            "rmse_gain_ci_97.5": float(np.percentile(gains, 97.5)),
            "bootstrap_probability_gain_below_5pct": float(np.mean(gains < 0.05)),
            "bootstrap_probability_gain_negative": float(np.mean(gains < 0.0)),
            "blockwise_wilcoxon_p": float(p_block),
            "blockwise_block_count": int(len(blocks)),
        })
    return output


def stage_split(dataset, seeds, out: Path) -> dict:
    """A6 : la fenêtre de séparation change-t-elle le verdict ?"""
    rows = []
    for split in (800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600):
        observed, forcing, training_mask = standardise(dataset, split)
        fits, _ = fit_all(observed, forcing, training_mask, MODELS, seeds,
                          BUDGET_MEDIUM, bounds_name="wide")
        metrics, predictions, _ = assemble(
            dataset, observed, forcing, training_mask, fits, f"split_{split}"
        )
        prediction_mask = ~training_mask
        o = observed[prediction_mask]
        row = {
            "split_age_kyr": split,
            "calibration_points": int(training_mask.sum()),
            "prediction_points": int(prediction_mask.sum()),
        }
        for model in MODELS:
            row[f"rmse_{model}"] = rmse(o, predictions[model][prediction_mask])
        row["gain_M2_vs_M1"] = 1.0 - row["rmse_M2"] / row["rmse_M1"]
        row["gain_M2_vs_M1P"] = 1.0 - row["rmse_M2"] / row["rmse_M1P"]
        row["gain_M2_vs_M0"] = 1.0 - row["rmse_M2"] / row["rmse_M0"]
        frame = metrics.set_index(["interval", "model"])
        row["delta_bic_effective_M2_vs_M1"] = float(
            frame.loc[("prediction", "M2"), "bic_effective"]
            - frame.loc[("prediction", "M1"), "bic_effective"]
        )
        row["correlation_M2"] = float(frame.loc[("prediction", "M2"), "correlation"])
        row["power_ratio_M2"] = float(
            frame.loc[("prediction", "M2"), "power_ratio_100k_41k"]
        )
        row["power_ratio_observed"] = float(
            frame.loc[("prediction", "M2"), "observed_power_ratio"]
        )
        rows.append(row)
        print(f"  split {split}: gain vs M1 = {row['gain_M2_vs_M1']:+.4f}, "
              f"vs M1P = {row['gain_M2_vs_M1P']:+.4f}", flush=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(out / "a_split_sensitivity.csv", index=False)
    return {
        "splits_tested": len(rows),
        "gain_vs_M1_min": float(frame["gain_M2_vs_M1"].min()),
        "gain_vs_M1_max": float(frame["gain_M2_vs_M1"].max()),
        "gain_vs_M1_median": float(frame["gain_M2_vs_M1"].median()),
        "splits_with_gain_above_5pct_vs_M1": int((frame["gain_M2_vs_M1"] >= 0.05).sum()),
        "gain_vs_M1P_min": float(frame["gain_M2_vs_M1P"].min()),
        "gain_vs_M1P_max": float(frame["gain_M2_vs_M1P"].max()),
        "gain_vs_M1P_median": float(frame["gain_M2_vs_M1P"].median()),
        "splits_with_gain_above_5pct_vs_M1P": int(
            (frame["gain_M2_vs_M1P"] >= 0.05).sum()
        ),
        "power_ratio_M2_max": float(frame["power_ratio_M2"].max()),
        "power_ratio_observed_min": float(frame["power_ratio_observed"].min()),
    }


def stage_surrogate(dataset, draws: int, out: Path) -> dict:
    """A7 : distribution nulle du gain de M2 sur M1 et M1P.

    Deux nuls sont construits :
      * cible à phases aléatoires — même spectre que LR04, structure temporelle
        détruite ; aucune mémoire réelle à retrouver ;
      * forçage à phases aléatoires — LR04 intact, mais l'insolation La2004 est
        remplacée par un signal de même spectre sans relation de phase.
    """
    observed, forcing, training_mask = standardise(dataset, 1200)
    prediction_mask = ~training_mask
    rng = np.random.default_rng(31337)
    rows = []
    seeds = [11, 12]
    for kind in ("cible", "forcage"):
        for draw in range(draws):
            if kind == "cible":
                target = fourier_surrogate(observed, rng)
                drive = forcing
            else:
                target = observed
                drive = fourier_surrogate(forcing, rng)
            fits, _ = fit_all(target, drive, training_mask, ("M1", "M1P", "M2"),
                              seeds, BUDGET_MEDIUM, bounds_name="wide")
            predictions = {
                model: simulate(model, drive, target[0], fit.vector)
                for model, fit in fits.items()
            }
            t = target[prediction_mask]
            row = {"null_kind": kind, "draw": draw}
            for model in ("M1", "M1P", "M2"):
                row[f"rmse_{model}"] = rmse(t, predictions[model][prediction_mask])
            row["gain_M2_vs_M1"] = 1.0 - row["rmse_M2"] / row["rmse_M1"]
            row["gain_M2_vs_M1P"] = 1.0 - row["rmse_M2"] / row["rmse_M1P"]
            rows.append(row)
        print(f"  nul {kind}: {draws} tirages terminés", flush=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(out / "a_surrogate_null.csv", index=False)

    summary = {"draws_per_kind": draws}
    for kind in ("cible", "forcage"):
        subset = frame.loc[frame["null_kind"] == kind]
        summary[kind] = {
            "gain_M2_vs_M1_mean": float(subset["gain_M2_vs_M1"].mean()),
            "gain_M2_vs_M1_p95": float(subset["gain_M2_vs_M1"].quantile(0.95)),
            "gain_M2_vs_M1_max": float(subset["gain_M2_vs_M1"].max()),
            "fraction_above_5pct": float((subset["gain_M2_vs_M1"] >= 0.05).mean()),
            "gain_M2_vs_M1P_mean": float(subset["gain_M2_vs_M1P"].mean()),
            "gain_M2_vs_M1P_p95": float(subset["gain_M2_vs_M1P"].quantile(0.95)),
            "fraction_above_5pct_vs_M1P": float(
                (subset["gain_M2_vs_M1P"] >= 0.05).mean()
            ),
        }
    return summary


def stage_ablation(dataset, seeds, out: Path) -> dict:
    """A8 : la mémoire carbone porte-t-elle réellement le gain ?"""
    observed, forcing, training_mask = standardise(dataset, 1200)
    prediction_mask = ~training_mask
    fits, _ = fit_all(observed, forcing, training_mask, ("M1", "M2"), seeds,
                      BUDGET_HIGH, bounds_name="wide")
    o = observed[prediction_mask]
    m2 = fits["M2"]
    base = simulate("M2", forcing, observed[0], m2.vector)
    frozen = simulate("M2A", forcing, observed[0], m2.vector)
    m1 = simulate("M1", forcing, observed[0], fits["M1"].vector)

    # Ablation par ré-ajustement : M2 avec couplage carbone imposé nul.
    refit, _ = fit_best_of_seeds(
        "M2A", forcing, observed, training_mask, seeds,
        bounds_name="wide", **BUDGET_HIGH,
    )
    refit_prediction = simulate("M2A", forcing, observed[0], refit.vector)

    reference_rmse = rmse(o, m1[prediction_mask])
    return {
        "carbon_feedback_gain_fitted": m2.parameters["carbon_feedback_gain"],
        "tau_carbon_kyr_fitted": m2.parameters["tau_carbon_kyr"],
        "rmse_M1": reference_rmse,
        "rmse_M2": rmse(o, base[prediction_mask]),
        "rmse_M2_couplage_gele": rmse(o, frozen[prediction_mask]),
        "rmse_M2_reajuste_sans_carbone": rmse(o, refit_prediction[prediction_mask]),
        "gain_M2_vs_M1": 1.0 - rmse(o, base[prediction_mask]) / reference_rmse,
        "gain_M2_gele_vs_M1": 1.0 - rmse(o, frozen[prediction_mask]) / reference_rmse,
        "gain_M2_reajuste_sans_carbone_vs_M1": 1.0
        - rmse(o, refit_prediction[prediction_mask]) / reference_rmse,
        "fraction_du_gain_portee_par_la_memoire_carbone": float(
            1.0
            - (1.0 - rmse(o, refit_prediction[prediction_mask]) / reference_rmse)
            / max(1.0 - rmse(o, base[prediction_mask]) / reference_rmse, 1e-12)
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stages", default="budget,robust,split,ablation,surrogate")
    parser.add_argument("--seeds", type=int, default=12)
    parser.add_argument("--surrogate-draws", type=int, default=60)
    arguments = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    dataset, quality = load_dataset()
    seeds_high = [729 + 37 * k for k in range(arguments.seeds)]
    seeds_medium = seeds_high[: max(3, arguments.seeds // 3)]

    report = {"data_quality": quality, "seeds_high": seeds_high}
    stages = [item.strip() for item in arguments.stages.split(",") if item.strip()]

    for stage in stages:
        started = time.perf_counter()
        print(f"[A] étape {stage} ...", flush=True)
        if stage == "budget":
            report["budget"] = stage_budget(dataset, seeds_high, OUT)
        elif stage == "robust":
            report["robust"] = stage_robust(dataset, seeds_high, OUT)
        elif stage == "split":
            report["split"] = stage_split(dataset, seeds_medium, OUT)
        elif stage == "ablation":
            report["ablation"] = stage_ablation(dataset, seeds_high, OUT)
        elif stage == "surrogate":
            report["surrogate"] = stage_surrogate(
                dataset, arguments.surrogate_draws, OUT
            )
        print(f"[A] {stage} terminé en {time.perf_counter() - started:.1f} s",
              flush=True)
        (OUT / "a_report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False, default=float),
            encoding="utf-8",
        )

    print(json.dumps(report, indent=2, ensure_ascii=False, default=float)[:4000])


if __name__ == "__main__":
    main()
