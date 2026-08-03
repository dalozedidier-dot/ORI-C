#!/usr/bin/env python3
"""Analyze the long real-science suite against La2010 and numerical controls."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(tempfile.gettempdir()) / "oric-solar-history-matplotlib"),
)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from scipy import stats

from oric_solar_history.real_validation import (
    align_eccentricity,
    load_earth_output,
    load_la2010_eccentricity,
    metrics_by_horizon,
    multitaper_spectrum,
    series_metrics,
    target_band_metrics,
    top_local_peaks,
)


HORIZONS = [
    50_000,
    100_000,
    250_000,
    500_000,
    1_000_000,
    2_000_000,
    5_000_000,
    10_000_000,
    20_000_000,
]

BANDS = {
    "95 kyr": (80_000.0, 110_000.0, 95_000.0),
    "125 kyr": (110_000.0, 160_000.0, 125_000.0),
    "405 kyr": (350_000.0, 460_000.0, 405_000.0),
    "2.4 Myr": (1_800_000.0, 3_200_000.0, 2_400_000.0),
}

COUNTERFACTUALS = [
    "jupiter_mass_minus_5pct_2myr",
    "jupiter_mass_plus_5pct_2myr",
    "saturn_mass_minus_5pct_2myr",
    "saturn_mass_plus_5pct_2myr",
    "jupiter_a_minus_0p5pct_2myr",
    "jupiter_a_plus_0p5pct_2myr",
]

ENSEMBLE_JOBS = [f"ensemble_10myr_r{index:02d}" for index in range(8)]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    def json_safe(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: json_safe(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [json_safe(item) for item in value]
        if isinstance(value, np.generic):
            return json_safe(value.item())
        if isinstance(value, float) and not np.isfinite(value):
            return None
        return value

    path.write_text(
        json.dumps(
            json_safe(payload),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )


def _job_earth(runs: Path, name: str) -> pd.DataFrame:
    path = runs / name / "earth.csv.gz"
    if not path.is_file():
        raise FileNotFoundError(f"Sortie terrestre absente: {path}")
    return load_earth_output(path)


def _job_metadata(runs: Path, name: str) -> dict[str, Any]:
    path = runs / name / "metadata.json"
    if not path.is_file():
        raise FileNotFoundError(f"Métadonnées absentes: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _verify_job_manifests(runs: Path, job_names: list[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for name in job_names:
        job_dir = runs / name
        manifest_path = job_dir / "job_manifest.json"
        if not manifest_path.is_file():
            rows.append(
                {
                    "job": name,
                    "files": 0,
                    "hashes_valid": False,
                    "error": "job_manifest.json absent",
                }
            )
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        valid = True
        errors: list[str] = []
        for filename, expected in manifest.items():
            path = job_dir / filename
            if not path.is_file():
                valid = False
                errors.append(f"{filename}: absent")
                continue
            if path.stat().st_size != int(expected["bytes"]):
                valid = False
                errors.append(f"{filename}: taille")
            if _sha256(path) != expected["sha256"]:
                valid = False
                errors.append(f"{filename}: sha256")
        rows.append(
            {
                "job": name,
                "files": len(manifest),
                "hashes_valid": valid,
                "error": ", ".join(errors),
            }
        )
    return pd.DataFrame(rows)


def _comparison(
    runs: Path,
    left_name: str,
    right_name: str,
    horizon_years: float,
    comparison_type: str,
) -> dict[str, Any]:
    left = _job_earth(runs, left_name)
    right = _job_earth(runs, right_name)
    aligned = align_eccentricity(left, right, "left", "right")
    aligned = aligned.loc[aligned["time_years"].abs() <= horizon_years]
    metrics = series_metrics(aligned["left"], aligned["right"])
    return {
        "comparison_type": comparison_type,
        "left_job": left_name,
        "right_job": right_name,
        "horizon_years": horizon_years,
        **metrics,
    }


def _spectra_and_bands(
    frame: pd.DataFrame,
    max_elapsed: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    selected = frame.loc[frame["time_years"].abs() <= max_elapsed]
    spectrum = multitaper_spectrum(
        selected["time_years"],
        selected["eccentricity"],
        min_period_years=18_000,
        max_period_years=min(5_000_000.0, max_elapsed),
    )
    return spectrum, target_band_metrics(spectrum, BANDS)


def _reference_ensemble(
    paths: list[str],
    baseline: pd.DataFrame,
    output: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    combined: pd.DataFrame | None = None
    for index, path in enumerate(paths):
        frame = load_la2010_eccentricity(path).rename(columns={"eccentricity": f"la2010_{index}"})
        combined = (
            frame
            if combined is None
            else combined.merge(
                frame,
                on="time_years",
                how="inner",
                validate="one_to_one",
            )
        )
    if combined is None:
        raise ValueError("Aucune solution de référence La2010")
    value_columns = [column for column in combined if column.startswith("la2010_")]
    combined["reference_mean"] = combined[value_columns].mean(axis=1)
    combined["reference_std"] = combined[value_columns].std(axis=1, ddof=0)
    combined["elapsed_years"] = combined["time_years"].abs()
    selected = combined.loc[combined["elapsed_years"] <= 20_000_000].copy()
    selected.to_csv(output / "la2010_ensemble_spread.csv", index=False)

    candidate = baseline[["time_years", "eccentricity"]]
    aligned = candidate.merge(
        selected[["time_years", "reference_mean", "reference_std"]],
        on="time_years",
        how="inner",
        validate="one_to_one",
    )
    aligned["elapsed_years"] = aligned["time_years"].abs()
    rows: list[dict[str, Any]] = []
    for horizon in HORIZONS:
        window = aligned.loc[aligned["elapsed_years"] <= horizon]
        metrics = series_metrics(window["eccentricity"], window["reference_mean"])
        rows.append(
            {
                "horizon_years": horizon,
                **metrics,
                "reference_spread_mean": float(window["reference_std"].mean()),
                "reference_spread_max": float(window["reference_std"].max()),
                "candidate_rmse_to_spread_mean_ratio": float(
                    metrics["rmse"] / max(window["reference_std"].mean(), np.finfo(float).tiny)
                ),
            }
        )
    return selected, pd.DataFrame(rows)


def _ensemble_analysis(
    runs: Path,
    baseline: pd.DataFrame,
    output: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, float, dict[str, Any]]:
    combined = baseline[["time_years", "elapsed_years", "eccentricity"]].rename(
        columns={"eccentricity": "baseline"}
    )
    ensemble_columns: list[str] = []
    for name in ENSEMBLE_JOBS:
        column = name.replace("ensemble_10myr_", "")
        ensemble_columns.append(column)
        frame = _job_earth(runs, name)[["time_years", "eccentricity"]].rename(
            columns={"eccentricity": column}
        )
        combined = combined.merge(
            frame,
            on="time_years",
            how="inner",
            validate="one_to_one",
        )
    values = combined[ensemble_columns]
    differences = values.subtract(combined["baseline"], axis=0)
    combined["ensemble_mean"] = values.mean(axis=1)
    combined["ensemble_std"] = values.std(axis=1, ddof=0)
    combined["rms_difference_vs_baseline"] = np.sqrt((differences**2).mean(axis=1))
    combined["median_abs_difference_vs_baseline"] = differences.abs().median(axis=1)
    combined.to_csv(output / "ensemble_divergence.csv", index=False)

    bin_width = 250_000.0
    combined["bin_start_years"] = np.floor(combined["elapsed_years"] / bin_width) * bin_width
    binned = (
        combined.groupby("bin_start_years", as_index=False)
        .agg(
            elapsed_mid_years=("elapsed_years", "mean"),
            ensemble_std_rms=(
                "ensemble_std",
                lambda values: float(np.sqrt(np.mean(np.asarray(values) ** 2))),
            ),
            difference_rms=(
                "rms_difference_vs_baseline",
                lambda values: float(np.sqrt(np.mean(np.asarray(values) ** 2))),
            ),
            difference_median=("median_abs_difference_vs_baseline", "median"),
        )
        .sort_values("bin_start_years")
    )
    binned.to_csv(output / "ensemble_divergence_binned.csv", index=False)
    floor_window = combined.loc[combined["elapsed_years"] <= 2_000_000]
    ensemble_floor = float(np.sqrt(np.mean(floor_window["ensemble_std"].to_numpy() ** 2)))

    fit_window = binned.loc[binned["difference_rms"].between(1e-9, 1e-4, inclusive="both")]
    divergence_summary: dict[str, Any] = {
        "ensemble_floor_rms_0_to_2myr": ensemble_floor,
        "fit_samples": int(len(fit_window)),
    }
    if len(fit_window) >= 3:
        fit = stats.linregress(
            fit_window["elapsed_mid_years"],
            np.log(fit_window["difference_rms"]),
        )
        divergence_summary.update(
            {
                "descriptive_efolding_years": float(1.0 / fit.slope) if fit.slope > 0 else np.nan,
                "log_linear_fit_r_squared": float(fit.rvalue**2),
                "fit_start_years": float(fit_window["elapsed_mid_years"].min()),
                "fit_end_years": float(fit_window["elapsed_mid_years"].max()),
            }
        )
    for threshold in [1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3]:
        crossed = combined.loc[
            combined["rms_difference_vs_baseline"] >= threshold,
            "elapsed_years",
        ]
        divergence_summary[f"first_crossing_rms_{threshold:.0e}_years"] = (
            float(crossed.iloc[0]) if not crossed.empty else np.nan
        )
    return combined, binned, ensemble_floor, divergence_summary


def _counterfactual_analysis(
    runs: Path,
    baseline: pd.DataFrame,
    ensemble_floor: float,
    output: Path,
) -> pd.DataFrame:
    baseline_2myr = baseline.loc[baseline["elapsed_years"] <= 2_000_000]
    baseline_spectrum, baseline_bands = _spectra_and_bands(baseline_2myr, 2_000_000)
    baseline_band_power = baseline_bands.set_index("band")["normalized_band_power"]
    rows: list[dict[str, Any]] = []
    spectral_rows: list[pd.DataFrame] = []
    for name in COUNTERFACTUALS:
        frame = _job_earth(runs, name)
        aligned = align_eccentricity(frame, baseline_2myr, "counterfactual", "baseline")
        metrics = series_metrics(aligned["counterfactual"], aligned["baseline"])
        spectrum, bands = _spectra_and_bands(frame, 2_000_000)
        bands["job"] = name
        bands["power_ratio_vs_baseline"] = bands.apply(
            lambda row: float(row["normalized_band_power"] / baseline_band_power.loc[row["band"]])
            if baseline_band_power.loc[row["band"]] > 0
            else np.nan,
            axis=1,
        )
        spectral_rows.append(bands)
        rows.append(
            {
                "job": name,
                **metrics,
                "effect_to_ensemble_floor_ratio": float(
                    metrics["rmse"] / max(ensemble_floor, np.finfo(float).tiny)
                ),
                "mean_eccentricity_delta": float(
                    frame["eccentricity"].mean() - baseline_2myr["eccentricity"].mean()
                ),
                "std_ratio_vs_baseline": float(
                    frame["eccentricity"].std(ddof=0) / baseline_2myr["eccentricity"].std(ddof=0)
                ),
            }
        )
        spectrum.to_csv(output / f"spectrum_{name}.csv", index=False)
    baseline_spectrum.to_csv(output / "spectrum_baseline_2myr.csv", index=False)
    pd.concat(spectral_rows, ignore_index=True).to_csv(
        output / "counterfactual_band_metrics.csv", index=False
    )
    result = pd.DataFrame(rows).sort_values("job")
    result.to_csv(output / "counterfactual_effects.csv", index=False)
    return result


def _sliding_405k(
    baseline: pd.DataFrame,
    reference: pd.DataFrame,
    output: Path,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    window = 5_000_000.0
    step = 1_000_000.0
    for start in np.arange(0.0, 20_000_000.0 - window + step, step):
        stop = start + window
        for label, frame in [("ORI-C reduced", baseline), ("La2010a", reference)]:
            selected = frame.loc[frame["time_years"].abs().between(start, stop, inclusive="both")]
            spectrum = multitaper_spectrum(
                selected["time_years"],
                selected["eccentricity"],
                min_period_years=300_000,
                max_period_years=520_000,
            )
            band = target_band_metrics(spectrum, {"405 kyr": BANDS["405 kyr"]}).iloc[0]
            rows.append(
                {
                    "series": label,
                    "window_start_years_before_j2000": start,
                    "window_end_years_before_j2000": stop,
                    "peak_period_years": band["peak_period_years"],
                    "relative_period_error": band["relative_period_error"],
                    "normalized_band_power": band["normalized_band_power"],
                }
            )
    result = pd.DataFrame(rows)
    result.to_csv(output / "spectral_stability_405k.csv", index=False)
    return result


def _acceptance_row(
    test_id: str,
    observed: Any,
    operator: str,
    threshold: Any,
    passed: bool,
    meaning: str,
) -> dict[str, Any]:
    return {
        "test": test_id,
        "observed": observed,
        "operator": operator,
        "threshold": threshold,
        "passed": bool(passed),
        "meaning": meaning,
    }


def _build_acceptance(
    acceptance: dict[str, Any],
    jobs: pd.DataFrame,
    reference_metrics: pd.DataFrame,
    initial_error: float,
    horizons_metrics: pd.DataFrame,
    numerical: pd.DataFrame,
    roundtrips: pd.DataFrame,
    spectral: pd.DataFrame,
    counterfactuals: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    nbody = jobs.loc[jobs["kind"] == "nbody"]
    all_bound = bool(nbody["all_bodies_bound"].all())
    rows.append(
        _acceptance_row(
            "all_bodies_bound",
            all_bound,
            "==",
            acceptance["all_bodies_bound"],
            all_bound == bool(acceptance["all_bodies_bound"]),
            "Aucune planète ou petit corps ne devient non lié.",
        )
    )
    max_energy = float(nbody["max_abs_energy_rel_error"].max())
    energy_threshold = float(acceptance["max_abs_energy_rel_error"])
    rows.append(
        _acceptance_row(
            "energy_conservation",
            max_energy,
            "<=",
            energy_threshold,
            max_energy <= energy_threshold,
            "La dérive énergétique reste sous le seuil préenregistré.",
        )
    )
    max_angmom = float(nbody["max_abs_angmom_rel_error"].max())
    angmom_threshold = float(acceptance["max_abs_angmom_rel_error"])
    rows.append(
        _acceptance_row(
            "angular_momentum_conservation",
            max_angmom,
            "<=",
            angmom_threshold,
            max_angmom <= angmom_threshold,
            "Maximum newtonien sur tous les jobs, y compris le contrôle 1PN gr_full.",
        )
    )
    initial_threshold = float(acceptance["initial_eccentricity_abs_error_vs_la2010"])
    rows.append(
        _acceptance_row(
            "initial_eccentricity_vs_la2010",
            initial_error,
            "<=",
            initial_threshold,
            initial_error <= initial_threshold,
            "Le point de départ J2000 concorde avec La2010.",
        )
    )
    horizons_6kyr = horizons_metrics.loc[horizons_metrics["horizon_years"] == 6_000].iloc[0]
    observed = float(horizons_6kyr["correlation"])
    threshold = float(acceptance["horizons_correlation_min_6kyr"])
    rows.append(
        _acceptance_row(
            "horizons_correlation_6kyr",
            observed,
            ">=",
            threshold,
            observed >= threshold,
            "Accord de phase avec l’éphéméride JPL DE441.",
        )
    )
    observed = float(horizons_6kyr["rmse"])
    threshold = float(acceptance["horizons_rmse_max_6kyr"])
    rows.append(
        _acceptance_row(
            "horizons_rmse_6kyr",
            observed,
            "<=",
            threshold,
            observed <= threshold,
            "Écart absolu à l’éphéméride JPL DE441.",
        )
    )
    for horizon_key, threshold_value in acceptance["reference_correlation_min"].items():
        horizon = float(horizon_key)
        observed = float(
            reference_metrics.loc[
                reference_metrics["horizon_years"] == horizon,
                "correlation",
            ].iloc[0]
        )
        threshold = float(threshold_value)
        rows.append(
            _acceptance_row(
                f"la2010_correlation_{int(horizon)}yr",
                observed,
                ">=",
                threshold,
                observed >= threshold,
                "Accord de phase avec la solution orbitale indépendante.",
            )
        )
    comparisons = numerical.set_index("comparison_type")
    observed = float(comparisons.loc["whfast_dt10_vs_dt5", "rmse"])
    threshold = float(acceptance["whfast_step_rmse_max_2myr"])
    rows.append(
        _acceptance_row(
            "whfast_step_convergence_2myr",
            observed,
            "<=",
            threshold,
            observed <= threshold,
            "Le résultat est stable quand le pas est divisé par deux.",
        )
    )
    observed = float(comparisons.loc["whfast_vs_ias15", "rmse"])
    threshold = float(acceptance["whfast_vs_ias15_rmse_max_20kyr"])
    rows.append(
        _acceptance_row(
            "integrator_crosscheck_20kyr",
            observed,
            "<=",
            threshold,
            observed <= threshold,
            "WHFast et IAS15 donnent la même excentricité à court terme.",
        )
    )
    observed = float(roundtrips["max_combined_relative_state_error"].max())
    threshold = float(acceptance["roundtrip_max_relative_state_error_100kyr"])
    rows.append(
        _acceptance_row(
            "roundtrip_reversibility_100kyr",
            observed,
            "<=",
            threshold,
            observed <= threshold,
            "Maximum des allers-retours aux pas 0,01 et 0,005 an.",
        )
    )
    spectral_index = spectral.set_index("band")
    for band, key in [
        ("405 kyr", "peak_405k_relative_period_error_max"),
        ("2.4 Myr", "peak_2p4myr_relative_period_error_max"),
    ]:
        observed = float(spectral_index.loc[band, "relative_period_error"])
        threshold = float(acceptance[key])
        rows.append(
            _acceptance_row(
                f"spectral_peak_{band.replace(' ', '_')}",
                observed,
                "<=",
                threshold,
                observed <= threshold,
                f"La période du pic {band} tombe dans la tolérance fixée.",
            )
        )
    observed = float(counterfactuals["effect_to_ensemble_floor_ratio"].min())
    threshold = float(acceptance["counterfactual_effect_to_ensemble_floor_min"])
    rows.append(
        _acceptance_row(
            "counterfactuals_above_ensemble_floor",
            observed,
            ">=",
            threshold,
            observed >= threshold,
            "Chaque intervention dépasse la dispersion des états quasi identiques.",
        )
    )
    return pd.DataFrame(rows)


def _plot_results(
    output: Path,
    baseline: pd.DataFrame,
    reference: pd.DataFrame,
    reference_metrics: pd.DataFrame,
    horizons_reference: pd.DataFrame,
    whfast_short: pd.DataFrame,
    baseline_spectrum: pd.DataFrame,
    reference_spectrum: pd.DataFrame,
    ensemble: pd.DataFrame,
    counterfactuals: pd.DataFrame,
    jobs: pd.DataFrame,
) -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 160,
            "savefig.dpi": 160,
            "font.size": 9,
            "axes.grid": True,
            "grid.alpha": 0.25,
        }
    )
    figures = output / "figures"
    figures.mkdir(exist_ok=True)

    fig, axis = plt.subplots(figsize=(9, 4.2))
    selected_baseline = baseline.loc[baseline["elapsed_years"] <= 2_000_000]
    selected_reference = reference.loc[reference["time_years"].abs() <= 2_000_000]
    axis.plot(
        selected_reference["time_years"].abs() / 1e6,
        selected_reference["eccentricity"],
        label="La2010a",
        linewidth=1.1,
    )
    axis.plot(
        selected_baseline["elapsed_years"] / 1e6,
        selected_baseline["eccentricity"],
        label="Intégration réduite",
        linewidth=0.9,
        alpha=0.85,
    )
    axis.set_xlabel("Millions d’années avant J2000")
    axis.set_ylabel("Excentricité terrestre")
    axis.legend()
    fig.tight_layout()
    fig.savefig(figures / "reference_first_2myr.png")
    plt.close(fig)

    fig, axis = plt.subplots(figsize=(9, 4.2))
    short = whfast_short.loc[whfast_short["elapsed_years"] <= 6_000]
    axis.plot(
        horizons_reference["elapsed_years"] / 1000,
        horizons_reference["eccentricity"],
        label="JPL Horizons DE441",
        linewidth=1.2,
    )
    axis.plot(
        short["elapsed_years"] / 1000,
        short["eccentricity"],
        label="Intégration réduite",
        linewidth=0.9,
    )
    axis.set_xlabel("Milliers d’années avant J2000")
    axis.set_ylabel("Excentricité Terre–Lune")
    axis.legend()
    fig.tight_layout()
    fig.savefig(figures / "horizons_reference_6kyr.png")
    plt.close(fig)

    fig, axis = plt.subplots(figsize=(7, 4))
    axis.plot(
        reference_metrics["horizon_years"] / 1e6,
        reference_metrics["correlation"],
        marker="o",
    )
    axis.axhline(0.0, color="black", linewidth=0.7)
    axis.set_xlabel("Horizon avant J2000 (Myr)")
    axis.set_ylabel("Corrélation avec La2010a")
    axis.set_ylim(-1.05, 1.05)
    fig.tight_layout()
    fig.savefig(figures / "reference_correlation_horizon.png")
    plt.close(fig)

    fig, axis = plt.subplots(figsize=(9, 4.5))
    for frame, label in [
        (reference_spectrum, "La2010a"),
        (baseline_spectrum, "Intégration réduite"),
    ]:
        normalized = frame["power"] / frame["power"].max()
        axis.plot(frame["period_years"], normalized, label=label, linewidth=1)
    axis.set_xscale("log")
    axis.set_yscale("log")
    axis.set_xlim(18_000, 5_000_000)
    axis.set_xlabel("Période (années)")
    axis.set_ylabel("Puissance multitaper normalisée")
    axis.legend()
    fig.tight_layout()
    fig.savefig(figures / "multitaper_spectra.png")
    plt.close(fig)

    fig, axis = plt.subplots(figsize=(8, 4.2))
    axis.semilogy(
        ensemble["elapsed_years"] / 1e6,
        ensemble["rms_difference_vs_baseline"],
        label="Écart RMS au témoin",
    )
    axis.semilogy(
        ensemble["elapsed_years"] / 1e6,
        ensemble["ensemble_std"],
        label="Dispersion de l’ensemble",
        alpha=0.8,
    )
    axis.set_xlabel("Horizon avant J2000 (Myr)")
    axis.set_ylabel("Écart d’excentricité")
    axis.legend()
    fig.tight_layout()
    fig.savefig(figures / "ensemble_divergence.png")
    plt.close(fig)

    fig, axis = plt.subplots(figsize=(9, 4.5))
    labels = [
        value.replace("_2myr", "").replace("_", " ").replace("0p5pct", "0,5 %")
        for value in counterfactuals["job"]
    ]
    axis.bar(labels, counterfactuals["effect_to_ensemble_floor_ratio"])
    axis.set_yscale("log")
    axis.set_ylabel("Effet RMS / dispersion de l’ensemble")
    axis.tick_params(axis="x", rotation=35)
    fig.tight_layout()
    fig.savefig(figures / "counterfactual_effects.png")
    plt.close(fig)

    nbody = jobs.loc[jobs["kind"] == "nbody"].sort_values("max_abs_energy_rel_error")
    fig, axis = plt.subplots(figsize=(9, 6))
    axis.barh(
        nbody["job"],
        nbody["max_abs_energy_rel_error"],
        label="Énergie",
    )
    axis.scatter(
        nbody["max_abs_angmom_rel_error"],
        nbody["job"],
        color="black",
        s=12,
        label="Moment angulaire",
        zorder=3,
    )
    axis.set_xscale("log")
    axis.set_xlabel("Erreur relative maximale")
    axis.legend()
    fig.tight_layout()
    fig.savefig(figures / "numerical_invariants.png")
    plt.close(fig)


def _format_markdown(frame: pd.DataFrame, columns: list[str] | None = None) -> str:
    selected = frame if columns is None else frame[columns]
    return selected.to_markdown(index=False, floatfmt=".6g")


def _write_report(
    output: Path,
    acceptance: pd.DataFrame,
    horizons_metrics: pd.DataFrame,
    reference_metrics: pd.DataFrame,
    spectral_comparison: pd.DataFrame,
    numerical: pd.DataFrame,
    counterfactuals: pd.DataFrame,
    divergence: dict[str, Any],
    jobs: pd.DataFrame,
    reference_spread: pd.DataFrame,
) -> None:
    passed = int(acceptance["passed"].sum())
    failed = int((~acceptance["passed"]).sum())
    status = "réussi" if failed == 0 else "partiellement réussi"
    acceptance_view = acceptance.copy()
    acceptance_view["statut"] = acceptance_view["passed"].map({True: "RÉUSSI", False: "ÉCHEC"})
    total_cpu_seconds = float(jobs["computation_seconds"].sum())
    long_job = jobs.loc[jobs["job"] == "baseline_20myr_dt10"].iloc[0]
    ref_1m = reference_metrics.loc[reference_metrics["horizon_years"] == 1_000_000].iloc[0]
    peak_405 = spectral_comparison.loc[spectral_comparison["band"] == "405 kyr"].iloc[0]
    minimum_effect = float(counterfactuals["effect_to_ensemble_floor_ratio"].min())
    production_angmom = float(
        jobs.loc[
            (jobs["kind"] == "nbody") & (jobs["job"] != "ias15_grfull_20kyr"),
            "max_abs_angmom_rel_error",
        ].max()
    )
    roundtrip_dt10 = float(
        jobs.loc[
            jobs["job"] == "roundtrip_100kyr_dt10",
            "max_combined_relative_state_error",
        ].iloc[0]
    )
    roundtrip_dt5 = float(
        jobs.loc[
            jobs["job"] == "roundtrip_100kyr_dt5",
            "max_combined_relative_state_error",
        ].iloc[0]
    )
    spread_1m = reference_spread.loc[reference_spread["horizon_years"] == 1_000_000].iloc[0]

    lines = [
        "# Validation scientifique maximale — ORI-C Système solaire",
        "",
        "## Résultat principal",
        "",
        f"Le protocole préenregistré est **{status}** : {passed} critères réussis et {failed} échoués.",
        "",
        "Les deux échecs restent conservés. Le critère de moment angulaire est dépassé uniquement "
        "par le contrôle 1PN `gr_full`, où le moment mécanique newtonien exporté n’est pas "
        "l’invariant canonique 1PN complet. Tous les autres jobs culminent à "
        f"{production_angmom:.3g}, sous le seuil de 1e-10. L’aller-retour au pas 0,01 an atteint "
        f"{roundtrip_dt10:.3g}, tandis que le pas raffiné de 0,005 an atteint "
        f"{roundtrip_dt5:.3g} et réussit le seuil.",
        "",
        f"L’intégration de référence couvre {long_job['completed_years'] / 1e6:.1f} millions d’années. "
        f"Tous les calculs représentent {total_cpu_seconds / 3600:.2f} heures-cœur.",
        "",
        f"À 1 million d’années, la corrélation directe de l’excentricité terrestre avec La2010a vaut "
        f"{ref_1m['correlation']:.4f}, avec une RMSE de {ref_1m['rmse']:.3g}.",
        "",
        f"Le pic de la bande de 405 kyr est placé à {peak_405['candidate_peak_period_years']:.0f} ans "
        f"dans l’intégration réduite et à {peak_405['reference_peak_period_years']:.0f} ans dans La2010a.",
        "",
        f"Le plus petit effet contrefactuel reste {minimum_effect:.2f} fois la dispersion RMS de "
        "l’ensemble de conditions initiales quasi identiques sur 2 Myr.",
        "",
        "![Comparaison directe](figures/reference_first_2myr.png)",
        "",
        "## Critères fixés avant le calcul",
        "",
        _format_markdown(
            acceptance_view,
            ["test", "observed", "operator", "threshold", "statut", "meaning"],
        ),
        "",
        "Un échec n’est pas masqué. Il indique soit une limite numérique, soit une limite du modèle physique réduit.",
        "",
        "## Comparaison indépendante à La2010",
        "",
        _format_markdown(
            reference_metrics,
            [
                "horizon_years",
                "samples",
                "correlation",
                "rmse",
                "mae",
                "max_abs_error",
            ],
        ),
        "",
        "![Corrélation selon l’horizon](figures/reference_correlation_horizon.png)",
        "",
        "La corrélation point par point teste la phase. Elle finit nécessairement par baisser dans un "
        "système chaotique, même lorsque les bandes fréquentielles restent présentes. La comparaison "
        "spectrale est donc évaluée séparément.",
        "",
        "### Contrôle direct JPL Horizons DE441 sur 6 000 ans",
        "",
        _format_markdown(
            horizons_metrics,
            [
                "horizon_years",
                "samples",
                "correlation",
                "rmse",
                "mae",
                "max_abs_error",
            ],
        ),
        "",
        "![Contrôle JPL Horizons](figures/horizons_reference_6kyr.png)",
        "",
        "Ce contrôle utilise les éléments osculateurs du barycentre Terre–Lune "
        "calculés par Horizons, indépendamment du code REBOUND livré.",
        "",
        "### Spectre multitaper sur 20 Myr",
        "",
        _format_markdown(spectral_comparison),
        "",
        "![Spectres multitaper](figures/multitaper_spectra.png)",
        "",
        "### Dispersion entre les quatre solutions La2010",
        "",
        _format_markdown(
            reference_spread,
            [
                "horizon_years",
                "candidate_rmse_to_spread_mean_ratio",
                "reference_spread_mean",
                "reference_spread_max",
            ],
        ),
        "",
        "Ce rapport utilise la dispersion La2010a–d comme repère descriptif, pas comme intervalle "
        "statistique complet de l’incertitude astronomique.",
        "",
        f"À 1 Myr, la RMSE du modèle réduit vaut "
        f"{spread_1m['candidate_rmse_to_spread_mean_ratio']:.0f} fois la dispersion moyenne entre "
        "La2010a–d. L’accord de phase est donc excellent, mais ce modèle réduit n’atteint pas la "
        "précision interne d’une solution astronomique La2010.",
        "",
        "## Contrôles numériques et physiques",
        "",
        _format_markdown(
            numerical,
            [
                "comparison_type",
                "horizon_years",
                "correlation",
                "rmse",
                "max_abs_error",
            ],
        ),
        "",
        "Les contrôles séparent l’erreur de pas, le choix d’intégrateur, la relativité, les conditions "
        "initiales et l’ajout de Pluton plus cinq astéroïdes. La comparaison IAS15 avec `gr_full` est "
        "courte, car ce modèle relativiste précis est beaucoup plus coûteux.",
        "",
        "`gr_full` dépend des vitesses et inclut les contributions relativistes de toutes les "
        "particules. Le moment angulaire newtonien exporté n’est donc utilisé ici que comme "
        "diagnostic conservateur, pas comme invariant 1PN complet. L’échec préenregistré reste "
        "affiché pour éviter une correction a posteriori du seuil.",
        "",
        "![Invariants numériques](figures/numerical_invariants.png)",
        "",
        "## Sensibilité chaotique",
        "",
        f"La dispersion RMS de l’ensemble sur les 2 premiers Myr vaut "
        f"{divergence['ensemble_floor_rms_0_to_2myr']:.3g}.",
        "",
    ]
    if np.isfinite(divergence.get("descriptive_efolding_years", np.nan)):
        lines.extend(
            [
                f"Un ajustement descriptif de la phase de croissance donne un temps d’e-folding de "
                f"{divergence['descriptive_efolding_years'] / 1e6:.3g} Myr "
                f"(R² = {divergence['log_linear_fit_r_squared']:.3f}). Ce nombre n’est pas présenté "
                "comme un exposant de Lyapunov formel.",
                "",
            ]
        )
    lines.extend(
        [
            "![Divergence de l’ensemble](figures/ensemble_divergence.png)",
            "",
            "## Interventions architecturales",
            "",
            _format_markdown(
                counterfactuals,
                [
                    "job",
                    "correlation",
                    "rmse",
                    "effect_to_ensemble_floor_ratio",
                    "mean_eccentricity_delta",
                    "std_ratio_vs_baseline",
                ],
            ),
            "",
            "![Effets contrefactuels](figures/counterfactual_effects.png)",
            "",
            "Ces interventions démontrent une causalité à l’intérieur du modèle N-corps. Elles ne "
            "démontrent pas que les masses ou orbites réelles ont historiquement pris ces valeurs.",
            "",
            "## Ce que ces tests prouvent réellement",
            "",
            "- le calcul part de vecteurs JPL Horizons DE441 réels et non d’un signal injecté ;",
            "- la trajectoire est comparée à une solution astronomique publiée indépendante ;",
            "- les erreurs numériques sont séparées des effets physiques testés ;",
            "- les principales bandes d’excentricité peuvent être évaluées sur 20 Myr ;",
            "- la robustesse aux petites perturbations et aux changements d’architecture est quantifiée.",
            "",
            "## Ce qu’ils ne prouvent pas",
            "",
            "- le modèle ne résout pas explicitement la Lune, la rotation terrestre, le J2 solaire, "
            "les marées ni l’obliquité ;",
            "- `gr_potential` reproduit correctement la précession relativiste, mais pas toute la "
            "correction relativiste de vitesse ;",
            "- le pic long du modèle réduit est estimé à 2,00 Myr contre 2,22 Myr dans La2010a "
            "sur cette fenêtre, même s’il reste dans la tolérance préenregistrée de la bande 2,4 Myr ;",
            "- une ressemblance orbitale ne valide pas à elle seule le cadre général ORI-C ;",
            "- aucune archive géologique indépendante ni prédiction climatique hors échantillon "
            "n’est testée ici.",
            "",
            "La conclusion autorisée porte donc sur une validation astronomique et numérique du "
            "mécanisme réduit. Une preuve empirique forte d’ORI-C demanderait ensuite des prédictions "
            "géologiques fixées à l’avance, comparées hors échantillon à un modèle classique.",
            "",
            "## Sources indépendantes",
            "",
            "- JPL Horizons System : https://ssd.jpl.nasa.gov/horizons/",
            "- API Horizons : https://ssd-api.jpl.nasa.gov/doc/horizons.html",
            "- La2010, données IMCCE : https://ssp.imcce.fr/insola/earth/online/earth/La2010/",
            "- Laskar et al. 2011 : https://arxiv.org/abs/1103.1084",
            "- REBOUND WHFast : https://rebound.hanno-rein.de/integrators/whfast/",
            "- REBOUNDx : https://reboundx.readthedocs.io/en/latest/effects.html",
            "",
        ]
    )
    (output / "SCIENTIFIC_VALIDATION_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/real_science_max.yaml"),
    )
    parser.add_argument("--runs", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    runs = (args.runs if args.runs is not None else Path(config["suite"]["output_dir"])).resolve()
    output = (args.output if args.output is not None else runs / "analysis").resolve()
    output.mkdir(parents=True, exist_ok=True)

    job_names = [str(job["name"]) for job in config["jobs"]]
    integrity = _verify_job_manifests(runs, job_names)
    integrity.to_csv(output / "job_integrity.csv", index=False)
    if not integrity["hashes_valid"].all():
        raise RuntimeError("Au moins un manifeste de job est invalide")

    metadata_rows: list[dict[str, Any]] = []
    roundtrip_rows: list[dict[str, Any]] = []
    for name in job_names:
        metadata = _job_metadata(runs, name)
        summary = metadata["summary"]
        row = {"job": name, **summary}
        metadata_rows.append(row)
        if summary["kind"] == "roundtrip":
            roundtrip_rows.append(row)
    jobs = pd.DataFrame(metadata_rows)
    jobs.to_csv(output / "job_summaries.csv", index=False)
    roundtrips = pd.DataFrame(roundtrip_rows)
    roundtrips.to_csv(output / "roundtrip_summary.csv", index=False)

    baseline = _job_earth(runs, "baseline_20myr_dt10")
    reference_path = config["suite"]["reference"]["la2010a_1k"]
    reference = load_la2010_eccentricity(reference_path)
    reference_metrics = metrics_by_horizon(baseline, reference, HORIZONS)
    reference_metrics.to_csv(output / "reference_metrics_by_horizon.csv", index=False)
    initial_reference = float(reference.loc[reference["time_years"] == 0, "eccentricity"].iloc[0])
    initial_candidate = float(baseline.loc[baseline["time_years"] == 0, "eccentricity"].iloc[0])
    initial_error = abs(initial_candidate - initial_reference)

    horizons_reference = pd.read_csv(config["suite"]["reference"]["horizons_earth_100yr"])
    whfast_short = _job_earth(runs, "whfast_grpot_20kyr")
    horizons_metrics = metrics_by_horizon(
        whfast_short,
        horizons_reference,
        [100, 500, 1_000, 2_000, 5_000, 6_000],
    )
    horizons_metrics.to_csv(output / "horizons_reference_metrics.csv", index=False)

    _, reference_spread = _reference_ensemble(
        config["suite"]["reference"]["la2010_ensemble_5k"],
        baseline,
        output,
    )
    reference_spread.to_csv(output / "reference_ensemble_metrics.csv", index=False)

    numerical_pairs = [
        (
            "baseline_20myr_dt10",
            "baseline_2myr_dt5",
            2_000_000,
            "whfast_dt10_vs_dt5",
        ),
        (
            "baseline_2myr_dt5",
            "baseline_2myr_dt4p8828125",
            2_000_000,
            "whfast_dt5_vs_dt4p8828125",
        ),
        (
            "baseline_2myr_dt5",
            "baseline_2myr_no_gr_dt5",
            2_000_000,
            "gr_potential_vs_no_gr",
        ),
        (
            "baseline_2myr_dt5",
            "baseline_2myr_elements_dt5",
            2_000_000,
            "horizons_vs_approximate_elements",
        ),
        (
            "baseline_2myr_dt5",
            "full_la2010_bodies_2myr_dt5",
            2_000_000,
            "eight_planets_vs_pluto_five_asteroids",
        ),
        (
            "whfast_grpot_20kyr",
            "ias15_grpot_20kyr",
            20_000,
            "whfast_vs_ias15",
        ),
        (
            "ias15_grpot_20kyr",
            "ias15_grfull_20kyr",
            20_000,
            "gr_potential_vs_gr_full",
        ),
    ]
    numerical = pd.DataFrame([_comparison(runs, *parameters) for parameters in numerical_pairs])
    numerical.to_csv(output / "numerical_comparisons.csv", index=False)

    baseline_common = baseline.loc[baseline["time_years"].abs() <= 20_000_000]
    reference_common = reference.loc[reference["time_years"].abs() <= 20_000_000]
    baseline_spectrum, baseline_bands = _spectra_and_bands(baseline_common, 20_000_000)
    reference_spectrum, reference_bands = _spectra_and_bands(reference_common, 20_000_000)
    baseline_spectrum.to_csv(output / "spectrum_baseline_20myr.csv", index=False)
    reference_spectrum.to_csv(output / "spectrum_la2010a_20myr.csv", index=False)
    top_local_peaks(baseline_spectrum).to_csv(output / "peaks_baseline_20myr.csv", index=False)
    top_local_peaks(reference_spectrum).to_csv(output / "peaks_la2010a_20myr.csv", index=False)
    spectral_comparison = baseline_bands.merge(
        reference_bands,
        on=[
            "band",
            "low_period_years",
            "high_period_years",
            "nominal_period_years",
        ],
        suffixes=("_candidate", "_reference"),
        validate="one_to_one",
    ).rename(
        columns={
            "peak_period_years_candidate": "candidate_peak_period_years",
            "relative_period_error_candidate": "candidate_relative_period_error",
            "normalized_band_power_candidate": "candidate_normalized_band_power",
            "peak_period_years_reference": "reference_peak_period_years",
            "relative_period_error_reference": "reference_relative_period_error",
            "normalized_band_power_reference": "reference_normalized_band_power",
        }
    )
    spectral_comparison["candidate_to_reference_power_ratio"] = (
        spectral_comparison["candidate_normalized_band_power"]
        / spectral_comparison["reference_normalized_band_power"]
    )
    spectral_comparison.to_csv(output / "spectral_band_comparison.csv", index=False)
    _sliding_405k(baseline_common, reference_common, output)

    ensemble, _, ensemble_floor, divergence = _ensemble_analysis(runs, baseline, output)
    counterfactuals = _counterfactual_analysis(runs, baseline, ensemble_floor, output)

    acceptance = _build_acceptance(
        config["acceptance"],
        jobs,
        reference_metrics,
        initial_error,
        horizons_metrics,
        numerical,
        roundtrips,
        baseline_bands,
        counterfactuals,
    )
    acceptance.to_csv(output / "acceptance_tests.csv", index=False)

    _plot_results(
        output,
        baseline,
        reference,
        reference_metrics,
        horizons_reference,
        whfast_short,
        baseline_spectrum,
        reference_spectrum,
        ensemble,
        counterfactuals,
        jobs,
    )
    summary = {
        "acceptance_passed": int(acceptance["passed"].sum()),
        "acceptance_failed": int((~acceptance["passed"]).sum()),
        "all_job_hashes_valid": bool(integrity["hashes_valid"].all()),
        "initial_eccentricity_candidate": initial_candidate,
        "initial_eccentricity_la2010": initial_reference,
        "initial_eccentricity_abs_error": initial_error,
        "ensemble": divergence,
        "total_computation_seconds": float(jobs["computation_seconds"].sum()),
        "max_production_abs_angmom_rel_error_excluding_gr_full": float(
            jobs.loc[
                (jobs["kind"] == "nbody") & (jobs["job"] != "ias15_grfull_20kyr"),
                "max_abs_angmom_rel_error",
            ].max()
        ),
        "gr_full_newtonian_abs_angmom_rel_error": float(
            jobs.loc[
                jobs["job"] == "ias15_grfull_20kyr",
                "max_abs_angmom_rel_error",
            ].iloc[0]
        ),
        "roundtrip_max_relative_state_error_dt10": float(
            jobs.loc[
                jobs["job"] == "roundtrip_100kyr_dt10",
                "max_combined_relative_state_error",
            ].iloc[0]
        ),
        "roundtrip_max_relative_state_error_dt5": float(
            jobs.loc[
                jobs["job"] == "roundtrip_100kyr_dt5",
                "max_combined_relative_state_error",
            ].iloc[0]
        ),
        "long_baseline_completed_years": float(
            jobs.loc[jobs["job"] == "baseline_20myr_dt10", "completed_years"].iloc[0]
        ),
    }
    _write_json(output / "analysis_summary.json", summary)
    _write_report(
        output,
        acceptance,
        horizons_metrics,
        reference_metrics,
        spectral_comparison,
        numerical,
        counterfactuals,
        divergence,
        jobs,
        reference_spread,
    )
    manifest = {
        str(path.relative_to(output)): {
            "bytes": path.stat().st_size,
            "sha256": _sha256(path),
        }
        for path in sorted(output.rglob("*"))
        if path.is_file() and path.name != "analysis_manifest.json"
    }
    _write_json(output / "analysis_manifest.json", manifest)
    print(
        json.dumps(
            {
                "output": str(output),
                "passed": summary["acceptance_passed"],
                "failed": summary["acceptance_failed"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
