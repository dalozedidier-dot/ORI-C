from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution

from .data import prepare_mpt_dataset
from .fastcore import COMPILED, MODEL_CODE, simulate_ice
from .metrics import (
    best_lag_correlation,
    contiguous_block_scores,
    correlation,
    effective_sample_size,
    event_timing_mae,
    information_criteria,
    lag1_autocorrelation,
    log_ratio_error,
    moving_block_bootstrap_gain,
    mpt_power_ratio,
    paired_wilcoxon_greater,
    rmse,
    termination_events,
)


@dataclass(frozen=True)
class ParameterSpec:
    name: str
    lower: float
    upper: float
    logarithmic: bool = False

    @property
    def optimization_bounds(self) -> tuple[float, float]:
        if self.logarithmic:
            return float(np.log(self.lower)), float(np.log(self.upper))
        return self.lower, self.upper

    def decode(self, value: float) -> float:
        return float(np.exp(value) if self.logarithmic else value)


# Bornes. La première version du protocole plaçait quatre paramètres de M2 sur
# une borne à l'optimum, ce qui signifie que la boîte, et non les données,
# fixait une partie de la solution. Les bornes ci-dessous sont élargies d'au
# moins un ordre de grandeur sur chaque paramètre concerné.
#
# Symétrie exacte retirée. `carbon_offset` déplace l'équilibre de l'état lent
# de C d'une constante ; comme cet état n'agit sur la glace qu'à travers
# `carbon_feedback_gain` × C, tout décalage delta de `carbon_offset` est
# exactement compensé par un décalage -gain × delta de `forcing_offset`. La
# trajectoire de glace est identique à 3e-16 près. Le protocole initial laissait
# les deux paramètres libres : M2 n'avait donc que huit degrés de liberté
# identifiables sur neuf.
#
# Cette symétrie n'était pas seulement redondante, elle rendait le test
# d'ablation carbone indéterminé. Annuler le couplage supprime un terme dont la
# moyenne est absorbée différemment en chaque point de l'orbite de symétrie :
# deux ajustements équivalents de M2 donnent la même prédiction et des ablations
# qui diffèrent de plusieurs unités de RMSE. Le décalage est donc fixé à zéro
# par définition, comme l'étaient déjà les échelles de R et de C, et
# `forcing_offset` porte seul le niveau. Le même traitement s'applique à
# `slow_forcing_offset` dans M1P, pour garder les deux modèles appariés.
MODEL_SPECS: dict[str, tuple[ParameterSpec, ...]] = {
    "M0": (
        ParameterSpec("forcing_gain", -6.0, 6.0),
        ParameterSpec("forcing_offset", -4.0, 4.0),
        ParameterSpec("tau_ice_kyr", 1.0, 500.0, True),
    ),
    "M1": (
        ParameterSpec("forcing_gain", -6.0, 6.0),
        ParameterSpec("forcing_offset", -4.0, 4.0),
        ParameterSpec("tau_fast_kyr", 1.0, 200.0, True),
        ParameterSpec("tau_memory_gain_kyr", 0.01, 2000.0, True),
        ParameterSpec("regolith_scale", 0.001, 50.0, True),
        ParameterSpec("tau_regolith_kyr", 20.0, 25000.0, True),
    ),
    "M2": (
        ParameterSpec("forcing_gain", -6.0, 6.0),
        ParameterSpec("forcing_offset", -4.0, 4.0),
        ParameterSpec("tau_fast_kyr", 1.0, 200.0, True),
        ParameterSpec("tau_memory_gain_kyr", 0.01, 2000.0, True),
        ParameterSpec("regolith_scale", 0.001, 50.0, True),
        ParameterSpec("tau_regolith_kyr", 20.0, 25000.0, True),
        ParameterSpec("carbon_feedback_gain", -20.0, 20.0),
        ParameterSpec("tau_carbon_kyr", 20.0, 25000.0, True),
    ),
    # Témoin à nombre de paramètres égal. M1P ajoute à M1 exactement autant de
    # degrés de liberté que M2, et une constante de temps lente supplémentaire,
    # mais son état lent est un filtre du FORÇAGE EXTERNE, non une inscription
    # de la réponse passée du système. Comparer M2 à M1 seul mesure de la
    # flexibilité ; comparer M2 à M1P isole ce qu'ORI-C revendique réellement.
    "M1P": (
        ParameterSpec("forcing_gain", -6.0, 6.0),
        ParameterSpec("forcing_offset", -4.0, 4.0),
        ParameterSpec("tau_fast_kyr", 1.0, 200.0, True),
        ParameterSpec("tau_memory_gain_kyr", 0.01, 2000.0, True),
        ParameterSpec("regolith_scale", 0.001, 50.0, True),
        ParameterSpec("tau_regolith_kyr", 20.0, 25000.0, True),
        ParameterSpec("slow_forcing_gain", -20.0, 20.0),
        ParameterSpec("tau_slow_forcing_kyr", 20.0, 25000.0, True),
    ),
}

FITTED_MODELS = ("M0", "M1", "M2", "M1P")


def decode_parameters(model: str, vector: np.ndarray) -> dict[str, float]:
    specs = MODEL_SPECS[model]
    return {spec.name: spec.decode(value) for spec, value in zip(specs, vector)}


def simulate_mpt(
    model: str,
    forcing: np.ndarray,
    initial_ice: float,
    parameters: dict[str, float],
    carbon_ablation: bool = False,
) -> dict[str, np.ndarray]:
    forcing = np.asarray(forcing, dtype=float)
    ice = np.empty(len(forcing), dtype=float)
    ice[0] = initial_ice

    if model == "M0":
        tau = parameters["tau_ice_kyr"]
        for index in range(1, len(forcing)):
            target = (
                parameters["forcing_gain"] * forcing[index - 1]
                + parameters["forcing_offset"]
            )
            ice[index] = ice[index - 1] + (target - ice[index - 1]) / tau
        return {"ice": ice}

    regolith = np.empty(len(forcing), dtype=float)
    regolith[0] = max(initial_ice, 0.0)
    auxiliary = np.zeros(len(forcing), dtype=float)
    if model == "M2":
        auxiliary[0] = initial_ice + parameters.get("carbon_offset", 0.0)
    elif model == "M1P":
        auxiliary[0] = forcing[0] + parameters.get("slow_forcing_offset", 0.0)

    for index in range(1, len(forcing)):
        previous_regolith = max(regolith[index - 1], 0.0)
        tau = parameters["tau_fast_kyr"] + parameters[
            "tau_memory_gain_kyr"
        ] * (1.0 - np.exp(-previous_regolith / parameters["regolith_scale"]))
        target = (
            parameters["forcing_gain"] * forcing[index - 1]
            + parameters["forcing_offset"]
        )
        if model == "M2" and not carbon_ablation:
            target += parameters["carbon_feedback_gain"] * auxiliary[index - 1]
        elif model == "M1P":
            target += parameters["slow_forcing_gain"] * auxiliary[index - 1]
        ice[index] = ice[index - 1] + (target - ice[index - 1]) / tau
        regolith[index] = regolith[index - 1] + (
            max(ice[index - 1], 0.0) - regolith[index - 1]
        ) / parameters["tau_regolith_kyr"]
        if model == "M2":
            carbon_target = ice[index - 1] + parameters.get("carbon_offset", 0.0)
            auxiliary[index] = auxiliary[index - 1] + (
                carbon_target - auxiliary[index - 1]
            ) / parameters["tau_carbon_kyr"]
        elif model == "M1P":
            slow_target = forcing[index - 1] + parameters.get("slow_forcing_offset", 0.0)
            auxiliary[index] = auxiliary[index - 1] + (
                slow_target - auxiliary[index - 1]
            ) / parameters["tau_slow_forcing_kyr"]

    result = {"ice": ice, "regolith": regolith}
    if model == "M2":
        result["carbon"] = auxiliary
    elif model == "M1P":
        result["slow_forcing"] = auxiliary
    return result


def _fit_once(
    model: str,
    forcing: np.ndarray,
    observed: np.ndarray,
    training_index: np.ndarray,
    seed: int,
    max_iterations: int,
    population_size: int,
    tolerance: float,
) -> tuple[dict[str, float], dict]:
    specs = MODEL_SPECS[model]
    bounds = [spec.optimization_bounds for spec in specs]
    code = MODEL_CODE[model]
    forcing = np.ascontiguousarray(forcing, dtype=float)
    observed = np.ascontiguousarray(observed, dtype=float)
    initial_ice = float(observed[0])
    packed = np.zeros(9)

    def objective(vector: np.ndarray) -> float:
        packed[:] = 0.0
        for index, spec in enumerate(specs):
            packed[index] = spec.decode(vector[index])
        predicted = simulate_ice(code, forcing, initial_ice, packed)
        if not np.all(np.isfinite(predicted)) or np.max(np.abs(predicted)) > 20.0:
            return 1e6
        residual = observed[training_index] - predicted[training_index]
        return float(np.sqrt(np.mean(residual * residual)))

    result = differential_evolution(
        objective,
        bounds,
        seed=seed,
        maxiter=max_iterations,
        popsize=population_size,
        tol=tolerance,
        polish=True,
        workers=1,
        updating="immediate",
        init="sobol",
    )
    parameters = decode_parameters(model, result.x)
    optimization = {
        "success": bool(result.success),
        "message": str(result.message),
        "objective_training_rmse": float(result.fun),
        "function_evaluations": int(result.nfev),
        "iterations": int(result.nit),
        "seed": int(seed),
    }
    return parameters, optimization


def _fit_model(
    model: str,
    forcing: np.ndarray,
    observed: np.ndarray,
    training_mask: np.ndarray,
    seed: int,
    max_iterations: int,
    population_size: int,
    restarts: int = 4,
    tolerance: float = 1e-8,
) -> tuple[dict[str, float], dict]:
    """Ajuste un modèle en repartant de plusieurs graines indépendantes.

    Le protocole initial n'utilisait qu'un seul départ, avec un budget que son
    propre journal signalait comme épuisé. Un témoin mal ajusté produit un
    avantage apparent pour le modèle testé ; plusieurs redémarrages et un
    critère de convergence explicite retirent cette source d'erreur.
    """
    training_index = np.flatnonzero(training_mask)
    runs = []
    for offset in range(max(1, restarts)):
        parameters, optimization = _fit_once(
            model, forcing, observed, training_index, seed + 1009 * offset,
            max_iterations, population_size, tolerance,
        )
        runs.append((parameters, optimization))
    best_parameters, best_optimization = min(
        runs, key=lambda item: item[1]["objective_training_rmse"]
    )
    values = [run[1]["objective_training_rmse"] for run in runs]
    best_optimization = {
        **best_optimization,
        "max_iterations": int(max_iterations),
        "population_size": int(population_size),
        "restarts": int(max(1, restarts)),
        "tolerance": float(tolerance),
        "restart_training_rmse_min": float(np.min(values)),
        "restart_training_rmse_max": float(np.max(values)),
        "restart_training_rmse_relative_spread": float(
            (np.max(values) - np.min(values)) / max(np.min(values), 1e-12)
        ),
        "restarts_converged": int(sum(run[1]["success"] for run in runs)),
        "compiled_kernel": bool(COMPILED),
    }
    return best_parameters, best_optimization


def _model_metrics(
    observed: np.ndarray,
    predicted: np.ndarray,
    elapsed: np.ndarray,
    mask: np.ndarray,
    parameter_count: int,
    observed_power_ratio: float,
) -> dict:
    observed_part = observed[mask]
    predicted_part = predicted[mask]
    elapsed_part = elapsed[mask]
    residual = observed_part - predicted_part
    ratio = mpt_power_ratio(predicted_part)
    lag, lag_correlation = best_lag_correlation(observed_part, predicted_part)
    observed_events = termination_events(observed_part, elapsed_part)
    predicted_events = termination_events(predicted_part, elapsed_part)
    sample_size = effective_sample_size(residual)
    naive = information_criteria(residual, parameter_count)
    corrected = information_criteria(residual, parameter_count, sample_size)
    return {
        "rmse_standardized": rmse(observed_part, predicted_part),
        "correlation": correlation(observed_part, predicted_part),
        "best_lag_kyr": lag,
        "best_lag_correlation": lag_correlation,
        "power_ratio_100k_to_41k": ratio,
        "power_ratio_log_error": log_ratio_error(ratio, observed_power_ratio),
        "termination_count": int(len(predicted_events)),
        "termination_timing_mae_kyr": event_timing_mae(
            observed_events, predicted_events
        ),
        "residual_lag1_autocorrelation": lag1_autocorrelation(residual),
        "sample_size": int(len(residual)),
        "effective_sample_size": sample_size,
        "aic_naive": naive["aic"],
        "bic_naive": naive["bic"],
        "aic": corrected["aic"],
        "bic": corrected["bic"],
        "aicc": corrected["aicc"],
    }


def _plot_mpt_timeseries(predictions: pd.DataFrame, output_path: Path) -> None:
    figure, axis = plt.subplots(figsize=(12, 6.5))
    axis.axvspan(2.6, 1.2, color="#E9EEF5", alpha=0.75, label="Calibration")
    axis.axvspan(1.2, 0.0, color="#FFF4DA", alpha=0.65, label="Prédiction")
    axis.plot(
        predictions["age_kyr_bp"] / 1000.0,
        predictions["observed_standardized"],
        color="#222222",
        linewidth=1.4,
        label="LR04",
    )
    colors = {
        "M0": "#A7A9AC", "M1": "#2B6CB0", "M2": "#D97706", "M1P": "#8A5CF6"
    }
    styles = {"M0": "--", "M1": "-", "M2": "-", "M1P": "--"}
    for model in FITTED_MODELS:
        axis.plot(
            predictions["age_kyr_bp"] / 1000.0,
            predictions[model],
            color=colors[model],
            linestyle=styles[model],
            linewidth=1.25,
            label=model,
        )
    axis.set_xlim(2.6, 0.0)
    axis.set_xlabel("Âge (Ma avant le présent)")
    axis.set_ylabel("δ18O / état glaciaire standardisé")
    axis.set_title("Prédictions MPT avec paramètres figés à 1,2 Ma")
    axis.legend(ncol=6, frameon=False, loc="upper right")
    axis.grid(axis="y", color="#D9DDE3", linewidth=0.7)
    figure.tight_layout()
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def _plot_mpt_power(metrics: pd.DataFrame, output_path: Path) -> None:
    subset = metrics.loc[metrics["interval"] == "prediction"].copy()
    labels = ["LR04", *subset["model"].tolist()]
    values = [
        float(subset["observed_power_ratio"].iloc[0]),
        *subset["power_ratio_100k_to_41k"].tolist(),
    ]
    colors = ["#222222", "#A7A9AC", "#2B6CB0", "#D97706", "#8A5CF6"][
        : len(labels)
    ]
    figure, axis = plt.subplots(figsize=(8.2, 5.2))
    bars = axis.bar(labels, values, color=colors, edgecolor="#333333", linewidth=0.5)
    axis.set_yscale("log")
    axis.set_ylabel("Puissance 80–120 ka / puissance 39–43 ka")
    axis.set_title("Rapport spectral sur la période de prédiction")
    axis.grid(axis="y", which="both", color="#D9DDE3", linewidth=0.7)
    for bar, value in zip(bars, values):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            value * 1.15,
            f"{value:.3g}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    figure.tight_layout()
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def run_mpt_test(
    project_root: Path,
    seed: int = 729,
    split_age_kyr: int = 1200,
    max_iterations: int = 800,
    population_size: int = 18,
    restarts: int = 4,
    bootstrap_draws: int = 20000,
) -> dict:
    raw_dir = project_root / "data" / "raw"
    processed_path = project_root / "data" / "processed" / "mpt_lr04_la2004.csv"
    output_dir = project_root / "results" / "mpt"
    figure_dir = output_dir / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)

    dataset, quality = prepare_mpt_dataset(raw_dir, processed_path)
    training_mask = dataset["age_kyr_bp"].to_numpy() >= split_age_kyr
    prediction_mask = ~training_mask
    observed_raw = dataset["d18o_permil"].to_numpy()
    forcing_raw = dataset["insolation_65n_june_wm2"].to_numpy()

    observed_mean = float(observed_raw[training_mask].mean())
    observed_scale = float(observed_raw[training_mask].std())
    forcing_mean = float(forcing_raw[training_mask].mean())
    forcing_scale = float(forcing_raw[training_mask].std())
    observed = (observed_raw - observed_mean) / observed_scale
    forcing = (forcing_raw - forcing_mean) / forcing_scale

    parameters: dict[str, dict] = {}
    optimizations: dict[str, dict] = {}
    simulations: dict[str, np.ndarray] = {}
    for offset, model in enumerate(FITTED_MODELS):
        parameters[model], optimizations[model] = _fit_model(
            model=model,
            forcing=forcing,
            observed=observed,
            training_mask=training_mask,
            seed=seed + offset,
            max_iterations=max_iterations,
            population_size=population_size,
            restarts=restarts,
        )
        simulations[model] = simulate_mpt(
            model, forcing, observed[0], parameters[model]
        )["ice"]

    simulations["M2_ablation"] = simulate_mpt(
        "M2",
        forcing,
        observed[0],
        parameters["M2"],
        carbon_ablation=True,
    )["ice"]

    prediction_observed_ratio = mpt_power_ratio(observed[prediction_mask])
    metric_rows = []
    parameter_counts = {"M0": 3, "M1": 6, "M2": 8, "M1P": 8, "M2_ablation": 7}
    for interval, mask in (
        ("calibration", training_mask),
        ("prediction", prediction_mask),
    ):
        observed_ratio = mpt_power_ratio(observed[mask])
        for model, predicted in simulations.items():
            row = {
                "interval": interval,
                "model": model,
                "parameter_count": parameter_counts[model],
                "observed_power_ratio": observed_ratio,
            }
            row.update(
                _model_metrics(
                    observed,
                    predicted,
                    dataset["elapsed_kyr"].to_numpy(),
                    mask,
                    parameter_counts[model],
                    observed_ratio,
                )
            )
            metric_rows.append(row)
    metrics = pd.DataFrame(metric_rows)

    test_observed = observed[prediction_mask]
    test_predictions = {
        model: values[prediction_mask] for model, values in simulations.items()
    }
    block_rows = contiguous_block_scores(
        test_observed, test_predictions, block_size=50
    )
    blocks = pd.DataFrame(block_rows)

    prediction_metrics = metrics.set_index(["interval", "model"])
    m2 = prediction_metrics.loc[("prediction", "M2")]

    # Les cinq critères sont évalués deux fois : contre M1, le témoin
    # historique, et contre M1P, qui possède le même nombre de paramètres que
    # M2 sans mémoire d'état. Le second est le seul qui isole la revendication
    # propre à ORI-C. Le verdict global exige les deux.
    acceptance_rows = []
    comparisons = {}
    for reference in ("M1", "M1P"):
        control = prediction_metrics.loc[("prediction", reference)]
        rmse_improvement = 1.0 - (
            m2["rmse_standardized"] / control["rmse_standardized"]
        )
        delta_bic = float(m2["bic"] - control["bic"])
        delta_bic_naive = float(m2["bic_naive"] - control["bic_naive"])
        p_block = paired_wilcoxon_greater(
            blocks[f"rmse_{reference}"].to_numpy(), blocks["rmse_M2"].to_numpy()
        )
        bootstrap = moving_block_bootstrap_gain(
            test_observed,
            test_predictions[reference],
            test_predictions["M2"],
            block_length=int(max(10, round(5 * float(
                -1.0 / np.log(min(abs(float(control[
                    "residual_lag1_autocorrelation"
                ])), 0.999999))
            )))),
            draws=bootstrap_draws,
            seed=seed,
        )
        comparisons[reference] = {
            "rmse_gain": float(rmse_improvement),
            "delta_bic_effective": delta_bic,
            "delta_bic_naive": delta_bic_naive,
            "blockwise_wilcoxon_p": float(p_block),
            "rmse_gain_ci_low": float(np.percentile(bootstrap, 2.5)),
            "rmse_gain_ci_high": float(np.percentile(bootstrap, 97.5)),
            "probability_gain_below_threshold": float(np.mean(bootstrap < 0.05)),
        }
        acceptance_rows.extend([
            {
                "reference": reference,
                "criterion": "forecast_rmse_gain_at_least_5pct",
                "value": float(rmse_improvement),
                "threshold": 0.05,
                "passed": bool(rmse_improvement >= 0.05),
            },
            {
                "reference": reference,
                "criterion": "forecast_delta_bic_at_most_minus_10",
                "value": delta_bic,
                "threshold": -10.0,
                "passed": bool(delta_bic <= -10.0),
            },
            {
                "reference": reference,
                "criterion": "100k_regime_within_factor_2_and_closer_than_control",
                "value": float(m2["power_ratio_100k_to_41k"]),
                "threshold": float(prediction_observed_ratio / 2.0),
                "passed": bool(
                    prediction_observed_ratio / 2.0
                    <= m2["power_ratio_100k_to_41k"]
                    <= prediction_observed_ratio * 2.0
                    and m2["power_ratio_log_error"]
                    < control["power_ratio_log_error"]
                ),
            },
            {
                "reference": reference,
                "criterion": "chronology_correlation_and_termination_timing",
                "value": float(m2["correlation"]),
                "threshold": 0.4,
                "passed": bool(
                    m2["correlation"] >= 0.4
                    and m2["termination_timing_mae_kyr"] <= 25.0
                ),
            },
            {
                "reference": reference,
                "criterion": "blockwise_wilcoxon_M2_better_than_control",
                "value": float(p_block),
                "threshold": 0.05,
                "passed": bool(p_block < 0.05),
            },
        ])
    acceptance = pd.DataFrame(acceptance_rows)
    overall_pass = bool(acceptance["passed"].all())

    # Ablation : le couplage carbone aide-t-il réellement la prédiction ?
    # On compare les RMSE brutes plutôt qu'une part de gain : lorsque l'ablation
    # améliore la prédiction, un rapport de gains n'a pas de sens.
    ablation_rmse = rmse(test_observed, test_predictions["M2_ablation"])
    m2_rmse = rmse(test_observed, test_predictions["M2"])
    control_rmse = rmse(test_observed, test_predictions["M1"])
    ablation_gain = 1.0 - ablation_rmse / control_rmse

    predictions = dataset.copy()
    predictions["observed_standardized"] = observed
    predictions["forcing_standardized"] = forcing
    for model, values in simulations.items():
        predictions[model] = values
        predictions[f"{model}_d18o_permil"] = values * observed_scale + observed_mean

    predictions.to_csv(output_dir / "predictions.csv", index=False)
    metrics.to_csv(output_dir / "metrics.csv", index=False)
    blocks.to_csv(output_dir / "block_scores.csv", index=False)
    acceptance.to_csv(output_dir / "acceptance_tests.csv", index=False)
    (output_dir / "parameters.json").write_text(
        json.dumps(parameters, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (output_dir / "optimization.json").write_text(
        json.dumps(optimizations, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (output_dir / "data_quality.json").write_text(
        json.dumps(quality, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    _plot_mpt_timeseries(predictions, figure_dir / "mpt_predictions.png")
    _plot_mpt_power(metrics, figure_dir / "mpt_power_ratio.png")

    boundary_hits: dict[str, list[str]] = {}
    for model, fitted in parameters.items():
        hits = []
        for spec in MODEL_SPECS[model]:
            value = fitted[spec.name]
            tolerance = max(1e-9, 0.001 * (spec.upper - spec.lower))
            if abs(value - spec.lower) <= tolerance:
                hits.append(f"{spec.name}=borne_basse")
            elif abs(value - spec.upper) <= tolerance:
                hits.append(f"{spec.name}=borne_haute")
        boundary_hits[model] = hits

    summary = {
        "test": "MPT",
        "status": "passed" if overall_pass else "not_passed",
        "overall_pass": overall_pass,
        "calibration_window_kyr_bp": [2600, split_age_kyr],
        "prediction_window_kyr_bp": [split_age_kyr, 0],
        "models": {
            "M0": "réponse fixe",
            "M1": "mémoire classique du régolithe",
            "M2": "M1 enrichi d'une mémoire carbone ORI-C",
            "M1P": (
                "témoin à nombre de paramètres égal : M1 plus un filtre lent du "
                "forçage externe, sans mémoire de la réponse passée"
            ),
        },
        "comparisons": comparisons,
        "rmse_improvement_M2_vs_M1": comparisons["M1"]["rmse_gain"],
        "rmse_improvement_M2_vs_M1P": comparisons["M1P"]["rmse_gain"],
        "delta_bic_M2_vs_M1": comparisons["M1"]["delta_bic_effective"],
        "delta_bic_M2_vs_M1P": comparisons["M1P"]["delta_bic_effective"],
        "observed_power_ratio_100k_to_41k": float(prediction_observed_ratio),
        "M2_power_ratio_100k_to_41k": float(
            m2["power_ratio_100k_to_41k"]
        ),
        "M2_prediction_correlation": float(m2["correlation"]),
        "M2_residual_lag1_autocorrelation": float(
            m2["residual_lag1_autocorrelation"]
        ),
        "prediction_sample_size": int(m2["sample_size"]),
        "prediction_effective_sample_size": float(m2["effective_sample_size"]),
        "carbon_ablation_rmse": float(ablation_rmse),
        "carbon_ablation_gain_vs_M1": float(ablation_gain),
        "carbon_coupling_helps_prediction": bool(m2_rmse < ablation_rmse),
        "carbon_coupling_rmse_effect": float(ablation_rmse - m2_rmse),
        "passed_criteria": int(acceptance["passed"].sum()),
        "total_criteria": int(len(acceptance)),
        "passed_criteria_vs_M1": int(
            acceptance.loc[acceptance["reference"] == "M1", "passed"].sum()
        ),
        "passed_criteria_vs_M1P": int(
            acceptance.loc[acceptance["reference"] == "M1P", "passed"].sum()
        ),
        "optimizer_converged": {
            model: bool(details["success"])
            for model, details in optimizations.items()
        },
        "optimizer_restart_spread": {
            model: details["restart_training_rmse_relative_spread"]
            for model, details in optimizations.items()
        },
        "compiled_kernel": bool(COMPILED),
        "parameter_boundary_hits": boundary_hits,
        "important_caveat": (
            "La chronologie LR04 est accordée orbitalement à une insolation du "
            "21 juin à 65°N. Employer La2004 contre cette chronologie crée une "
            "dépendance méthodologique : ce test n'est pas une validation "
            "indépendante du forçage astronomique."
        ),
        "normalization_note": (
            "Les échelles de R et C sont fixées par définition. Cela supprime les "
            "symétries exactes alpha/R* et beta/gamma du protocole initial."
        ),
        "control_note": (
            "M2 est comparé à deux témoins. M1 n'a que six paramètres : un "
            "avantage de M2 sur M1 peut venir de trois degrés de liberté "
            "supplémentaires. M1P en possède neuf comme M2, avec un état lent "
            "piloté par le forçage externe au lieu de la réponse passée. Seul "
            "l'écart M2 contre M1P mesure l'inscription revendiquée par ORI-C."
        ),
        "statistical_note": (
            "Les résidus sur grille de 1 ka sont fortement autocorrélés. Le BIC "
            "rapporté utilise la taille d'échantillon efficace ; bic_naive "
            "conserve le compte brut à titre de comparaison. L'intervalle de "
            "confiance du gain provient d'un bootstrap par blocs mobiles."
        ),
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return summary
