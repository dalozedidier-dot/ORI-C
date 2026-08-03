from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from .archives import make_synthetic_archive
from .backends.rebound_backend import run_rebound
from .backends.surrogate import run_surrogate
from .climate import count_threshold_crossings, run_reduced_climate
from .insolation import build_insolation_frame
from .manifest import write_manifest
from .reporting import plot_insolation_climate, plot_orbital_series, plot_spectrum
from .spectral import analyze_regular_series


def _scenario_metrics(
    orbits: pd.DataFrame,
    earth: pd.DataFrame,
    peaks: pd.DataFrame,
    insolation: pd.DataFrame,
    climate: pd.DataFrame,
    ar1_phi: float,
) -> dict[str, Any]:
    dominant = peaks.iloc[0].to_dict() if not peaks.empty else {}
    completed = (
        orbits["elapsed_years"].max()
        if "elapsed_years" in orbits
        else orbits["time_years"].abs().max()
    )
    return {
        "completed_time_years": float(completed),
        "all_bodies_bound": bool(orbits["bound"].all()),
        "max_abs_energy_rel_error": float(orbits["energy_rel_error"].abs().max()),
        "max_abs_angmom_rel_error": float(orbits["angmom_rel_error"].abs().max()),
        "earth_eccentricity_mean": float(earth["eccentricity"].mean()),
        "earth_eccentricity_std": float(earth["eccentricity"].std()),
        "dominant_period_years": float(dominant.get("period_years", np.nan)),
        "dominant_peak_significant": bool(dominant.get("significant", False)),
        "ar1_phi": float(ar1_phi),
        "insolation_mean_w_m2": float(insolation["insolation_w_m2"].mean()),
        "insolation_std_w_m2": float(insolation["insolation_w_m2"].std()),
        "temperature_mean_c": float(climate["temperature_c"].mean()),
        "temperature_std_c": float(climate["temperature_c"].std()),
        "ice_fraction_mean": float(climate["ice_fraction"].mean()),
        "ice_threshold_crossings": count_threshold_crossings(
            climate["ice_fraction"].to_numpy(), 0.5
        ),
    }


def run_experiment(config: dict[str, Any], overwrite: bool = False) -> Path:
    exp = config["experiment"]
    run_dir = Path(exp["output_dir"])
    if run_dir.exists():
        if not overwrite:
            raise FileExistsError(
                f"Le dossier {run_dir} existe déjà. Utilisez --overwrite pour le remplacer."
            )
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "resolved_config.yaml").write_text(
        yaml.safe_dump({k: v for k, v in config.items() if not k.startswith("_")}, sort_keys=False),
        encoding="utf-8",
    )

    backend = exp["backend"]
    duration = float(exp["duration_years"])
    output_step = float(exp["output_step_years"])
    seed = int(exp.get("seed", 0))
    ensemble_size = int(exp.get("ensemble_size", 1))
    initial_sigma = float(exp.get("initial_angle_sigma_rad", 0.0))
    comparison_rows: list[dict[str, Any]] = []

    for scenario in config["scenarios"]:
        scenario_name = scenario["name"]
        scenario_dir = run_dir / scenario_name
        scenario_dir.mkdir(parents=True)
        figures_dir = scenario_dir / "figures"
        figures_dir.mkdir()
        realization_metrics = []

        for realization in range(ensemble_size):
            if backend == "surrogate":
                orbits = run_surrogate(
                    duration, output_step, scenario, seed=seed, realization=realization
                )
            else:
                orbits = run_rebound(
                    duration,
                    output_step,
                    scenario,
                    seed=seed,
                    rebound_cfg=config["rebound"],
                    realization=realization,
                    initial_angle_sigma_rad=initial_sigma,
                )

            realization_dir = (
                scenario_dir if ensemble_size == 1 else scenario_dir / f"r{realization:03d}"
            )
            realization_dir.mkdir(exist_ok=True)
            orbits.to_csv(realization_dir / "orbits.csv", index=False)
            target = str(config["spectrum"].get("target_body", "Earth"))
            earth = (
                orbits[orbits["body"] == target].sort_values("time_years").reset_index(drop=True)
            )
            if earth.empty:
                raise RuntimeError(f"Corps cible absent: {target}")
            variable = str(config["spectrum"].get("variable", "eccentricity"))
            spectral = analyze_regular_series(
                earth["time_years"].to_numpy(),
                earth[variable].to_numpy(),
                min_period_years=float(config["spectrum"]["min_period_years"]),
                max_period_years=float(config["spectrum"]["max_period_years"]),
                peak_count=int(config["spectrum"].get("peak_count", 8)),
                red_noise_surrogates=int(config["spectrum"].get("red_noise_surrogates", 100)),
                confidence=float(config["spectrum"].get("confidence", 0.95)),
                seed=seed + realization,
            )
            spectral.spectrum.to_csv(realization_dir / "spectrum.csv", index=False)
            spectral.peaks.to_csv(realization_dir / "peaks.csv", index=False)
            insolation = build_insolation_frame(earth, config["insolation"])
            insolation.to_csv(realization_dir / "insolation.csv", index=False)
            climate = run_reduced_climate(insolation, config["climate"])
            climate.to_csv(realization_dir / "climate.csv", index=False)

            metrics = _scenario_metrics(
                orbits, earth, spectral.peaks, insolation, climate, spectral.ar1_phi
            )
            metrics["realization"] = realization
            (realization_dir / "metrics.json").write_text(
                json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            realization_metrics.append(metrics)

            if realization == 0:
                plot_orbital_series(earth, figures_dir / "earth_eccentricity.png")
                plot_spectrum(spectral.spectrum, figures_dir / "spectrum.png")
                plot_insolation_climate(insolation, climate, figures_dir / "insolation_climate.png")
                if bool(config.get("archive", {}).get("enabled", False)):
                    archive_cfg = config["archive"]
                    archive = make_synthetic_archive(
                        insolation,
                        sampling_step_years=float(archive_cfg["sampling_step_years"]),
                        age_jitter_years=float(archive_cfg["age_jitter_years"]),
                        noise_std=float(archive_cfg["noise_std"]),
                        seed=seed,
                    )
                    archive.to_csv(realization_dir / "synthetic_archive.csv", index=False)

        metrics_frame = pd.DataFrame(realization_metrics)
        metrics_frame.to_csv(scenario_dir / "ensemble_metrics.csv", index=False)
        row = {"scenario": scenario_name, "realizations": ensemble_size}
        for column in metrics_frame.select_dtypes(include=[np.number]).columns:
            row[f"{column}_mean"] = float(metrics_frame[column].mean())
            row[f"{column}_std"] = float(metrics_frame[column].std(ddof=0))
        row["all_bodies_bound"] = bool(metrics_frame["all_bodies_bound"].all())
        comparison_rows.append(row)

    comparison = pd.DataFrame(comparison_rows)
    baseline = comparison[comparison["scenario"] == "baseline"].iloc[0]
    for column in [c for c in comparison.columns if c.endswith("_mean")]:
        if column in {"realization_mean"}:
            continue
        comparison[f"delta_vs_baseline__{column}"] = comparison[column] - baseline[column]
    comparison.to_csv(run_dir / "comparison.csv", index=False)
    _write_report(run_dir, config, comparison)
    write_manifest(run_dir, config)
    return run_dir


def _write_report(run_dir: Path, config: dict, comparison: pd.DataFrame) -> None:
    exp = config["experiment"]
    lines = [
        f"# Rapport — {exp['name']}",
        "",
        f"- Backend : `{exp['backend']}`",
        f"- Durée demandée : {exp['duration_years']} ans",
        f"- Pas de sortie : {exp['output_step_years']} ans",
        f"- Nombre de scénarios : {len(config['scenarios'])}",
        f"- Taille d'ensemble : {exp.get('ensemble_size', 1)}",
        "",
        "## Avertissement d'interprétation",
        "",
    ]
    if exp["backend"] == "surrogate":
        lines.append(
            "Ce run vérifie uniquement la chaîne logicielle. Les signaux sont synthétiques et ne constituent aucune preuve physique."
        )
    else:
        rebound = config["rebound"]
        lines.extend(
            [
                "Ce run utilise une intégration gravitationnelle N-corps.",
                f"Conditions initiales : `{rebound.get('initial_conditions', 'elements_j2000')}`. "
                f"Relativité : `{rebound.get('general_relativity', 'none')}`. "
                f"Direction : `{rebound.get('time_direction', 'forward')}`.",
                "L'obliquité reste prescrite et la Terre est représentée par le barycentre Terre-Lune.",
                "Toute conclusion doit être précédée de contrôles du pas, de l'intégrateur, de l'horizon temporel et de la dispersion entre conditions initiales.",
            ]
        )
    lines.extend(["", "## Comparaison", "", comparison.to_markdown(index=False), ""])
    lines.extend(
        [
            "## Lecture ORI-C autorisée",
            "",
            "Le rapport permet de mesurer si une modification explicite de l'architecture change les séries orbitales, leur spectre, le forçage radiatif réduit et la réponse d'un récepteur paramétré.",
            "Il ne permet pas à lui seul de conclure que le cadre ORI-C est validé, nécessaire ou exclusif.",
            "",
        ]
    )
    (run_dir / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
