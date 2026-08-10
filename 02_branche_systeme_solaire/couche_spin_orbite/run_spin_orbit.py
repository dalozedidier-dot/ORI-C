#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from spin_orbit import (
    ALPHA_SOLAR_ONLY_ARCSEC_PER_YEAR,
    ALPHA_WITH_MOON_ARCSEC_PER_YEAR,
    circular_difference,
    daily_mean_insolation,
    dominant_period_years,
    integrate_spin_batch,
    moving_perihelion_longitude,
    write_results_manifest,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASTRO = ROOT / "02_branche_systeme_solaire" / "couche_astronomique" / "resultats" / "real_science_max"
LA2004 = ROOT / "02_branche_systeme_solaire" / "couche_memoire_historique" / "data" / "raw" / "INSOLN.LA2004.BTL.ASC"
DEFAULT_OUT = HERE / "resultats"

INTERVENTIONS = [
    "jupiter_mass_minus_5pct_2myr",
    "jupiter_mass_plus_5pct_2myr",
    "saturn_mass_minus_5pct_2myr",
    "saturn_mass_plus_5pct_2myr",
    "jupiter_a_minus_0p5pct_2myr",
    "jupiter_a_plus_0p5pct_2myr",
]
ENSEMBLE = [f"ensemble_10myr_r{index:02d}" for index in range(8)]


def load_earth(job: str, horizon: float | None = None) -> pd.DataFrame:
    frame = pd.read_csv(ASTRO / job / "earth.csv.gz")
    if horizon is not None:
        frame = frame[frame["elapsed_years"] <= horizon]
    return frame.reset_index(drop=True)


def load_la2004(horizon: float) -> pd.DataFrame:
    rows = []
    with LA2004.open(encoding="utf-8") as handle:
        for raw in handle:
            fields = raw.replace("D", "E").split()
            if len(fields) != 4:
                continue
            time_years = float(fields[0]) * 1000.0
            if abs(time_years) > horizon:
                break
            rows.append(
                {
                    "time_years": time_years,
                    "elapsed_years": -time_years,
                    "eccentricity": float(fields[1]),
                    "obliquity_rad": float(fields[2]),
                    "long_peri_moving_rad": float(fields[3]),
                }
            )
    return pd.DataFrame(rows)


def rms(values: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(values))))


def validation_metrics(model: pd.DataFrame, reference: pd.DataFrame, horizon: float) -> dict:
    count = int(horizon / 1000.0) + 1
    model = model.iloc[:count]
    reference = reference.iloc[:count]
    eps_ref = np.degrees(reference["obliquity_rad"].to_numpy())
    eps_model = model["obliquity_deg"].to_numpy()
    q_ref = daily_mean_insolation(
        reference["eccentricity"].to_numpy(),
        reference["long_peri_moving_rad"].to_numpy(),
        eps_ref,
    )
    q_model = model["insolation_65n_solstice_w_m2"].to_numpy()
    p_diff = circular_difference(
        model["long_peri_moving_rad"].to_numpy(),
        reference["long_peri_moving_rad"].to_numpy(),
    )
    return {
        "horizon_years": int(horizon),
        "samples": count,
        "obliquity_rmse_deg": rms(eps_model - eps_ref),
        "obliquity_correlation": float(np.corrcoef(eps_model, eps_ref)[0, 1]),
        "moving_perihelion_circular_rmse_rad": rms(p_diff),
        "insolation_rmse_w_m2": rms(q_model - q_ref),
        "insolation_correlation": float(np.corrcoef(q_model, q_ref)[0, 1]),
    }


def build_spin_frame(orbit: pd.DataFrame, obliquity: np.ndarray, spins: np.ndarray, normals: np.ndarray) -> pd.DataFrame:
    moving = moving_perihelion_longitude(orbit, spins, normals)
    q = daily_mean_insolation(
        orbit["eccentricity"].to_numpy(dtype=float),
        moving,
        obliquity,
    )
    return pd.DataFrame(
        {
            "time_years": orbit["time_years"].to_numpy(),
            "elapsed_years": orbit["elapsed_years"].to_numpy(),
            "eccentricity": orbit["eccentricity"].to_numpy(),
            "obliquity_deg": obliquity,
            "long_peri_moving_rad": moving,
            "insolation_65n_solstice_w_m2": q,
            "spin_x": spins[:, 0],
            "spin_y": spins[:, 1],
            "spin_z": spins[:, 2],
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    figures = out / "figures"
    figures.mkdir(exist_ok=True)

    baseline_long = load_earth("baseline_20myr_dt10")
    # Deux scénarios identiques orbitalement, seule la constante de précession change.
    obl_long, spins_long, normals_long = integrate_spin_batch(
        [baseline_long, baseline_long],
        np.array([ALPHA_WITH_MOON_ARCSEC_PER_YEAR, ALPHA_SOLAR_ONLY_ARCSEC_PER_YEAR]),
        substeps_per_orbital_sample=5,
    )
    with_moon_long = build_spin_frame(baseline_long, obl_long[0], spins_long[0], normals_long[0])
    no_moon_long = build_spin_frame(baseline_long, obl_long[1], spins_long[1], normals_long[1])
    with_moon_long.to_csv(out / "baseline_with_moon_20myr.csv", index=False)
    no_moon_long.to_csv(out / "baseline_no_moon_20myr.csv", index=False)

    # Comparaison à la solution publiée La2004 sur la fenêtre commune de 20 Ma.
    la2004 = load_la2004(20_000_000.0)
    validation_rows = [
        validation_metrics(with_moon_long, la2004, horizon)
        for horizon in (100_000.0, 500_000.0, 1_000_000.0, 2_000_000.0, 5_000_000.0, 10_000_000.0, 20_000_000.0)
    ]
    validation = pd.DataFrame(validation_rows)
    validation.to_csv(out / "validation_la2004.csv", index=False)

    # Propagation des six interventions architecturales et de l'ensemble de bruit orbital.
    jobs = ["baseline_20myr_dt10", *INTERVENTIONS, *ENSEMBLE]
    frames = [load_earth(job, 2_000_000.0) for job in jobs]
    obl, spins, normals = integrate_spin_batch(
        frames,
        ALPHA_WITH_MOON_ARCSEC_PER_YEAR,
        substeps_per_orbital_sample=10,
    )
    spin_frames = [build_spin_frame(frame, obl[k], spins[k], normals[k]) for k, frame in enumerate(frames)]
    baseline = spin_frames[0]

    ensemble_indices = range(1 + len(INTERVENTIONS), len(jobs))
    ensemble_obliquity = np.vstack([spin_frames[k]["obliquity_deg"].to_numpy() for k in ensemble_indices])
    ensemble_insolation = np.vstack(
        [spin_frames[k]["insolation_65n_solstice_w_m2"].to_numpy() for k in ensemble_indices]
    )
    obliquity_floor = rms(ensemble_obliquity - ensemble_obliquity.mean(axis=0, keepdims=True))
    insolation_floor = rms(ensemble_insolation - ensemble_insolation.mean(axis=0, keepdims=True))

    intervention_rows = []
    for offset, job in enumerate(INTERVENTIONS, start=1):
        candidate = spin_frames[offset]
        eps_effect = rms(candidate["obliquity_deg"].to_numpy() - baseline["obliquity_deg"].to_numpy())
        q_effect = rms(
            candidate["insolation_65n_solstice_w_m2"].to_numpy()
            - baseline["insolation_65n_solstice_w_m2"].to_numpy()
        )
        intervention_rows.append(
            {
                "job": job,
                "obliquity_rmse_vs_baseline_deg": eps_effect,
                "obliquity_effect_to_ensemble_floor": eps_effect / obliquity_floor,
                "insolation_rmse_vs_baseline_w_m2": q_effect,
                "insolation_effect_to_ensemble_floor": q_effect / insolation_floor,
            }
        )
    interventions = pd.DataFrame(intervention_rows)
    interventions.to_csv(out / "interventions_spin_insolation.csv", index=False)

    # Convergence numérique : 100 ans (10 sous-pas) contre 50 ans (20 sous-pas) sur 2 Ma.
    baseline_2myr = frames[0]
    obl_coarse, _, _ = integrate_spin_batch(
        [baseline_2myr, baseline_2myr],
        np.array([ALPHA_WITH_MOON_ARCSEC_PER_YEAR, ALPHA_SOLAR_ONLY_ARCSEC_PER_YEAR]),
        substeps_per_orbital_sample=10,
    )
    obl_fine, spins_fine, normals_fine = integrate_spin_batch(
        [baseline_2myr, baseline_2myr],
        np.array([ALPHA_WITH_MOON_ARCSEC_PER_YEAR, ALPHA_SOLAR_ONLY_ARCSEC_PER_YEAR]),
        substeps_per_orbital_sample=20,
    )
    eps_coarse_moon = obl_coarse[0]
    eps_coarse_no = obl_coarse[1]
    convergence = {
        "coarse_substep_years": 100.0,
        "fine_substep_years": 50.0,
        "with_moon_obliquity_rmse_deg": rms(eps_coarse_moon - obl_fine[0]),
        "with_moon_obliquity_max_abs_deg": float(np.max(np.abs(eps_coarse_moon - obl_fine[0]))),
        "no_moon_obliquity_rmse_deg": rms(eps_coarse_no - obl_fine[1]),
        "no_moon_obliquity_max_abs_deg": float(np.max(np.abs(eps_coarse_no - obl_fine[1]))),
    }

    # Résumé des deux architectures de spin sur 2 Ma et 20 Ma.
    def state_metrics(frame: pd.DataFrame, horizon: float) -> dict:
        view = frame[frame["elapsed_years"] <= horizon]
        eps = view["obliquity_deg"].to_numpy()
        q = view["insolation_65n_solstice_w_m2"].to_numpy()
        return {
            "horizon_years": int(horizon),
            "obliquity_min_deg": float(eps.min()),
            "obliquity_max_deg": float(eps.max()),
            "obliquity_range_deg": float(eps.max() - eps.min()),
            "obliquity_std_deg": float(eps.std()),
            "dominant_obliquity_period_years": dominant_period_years(eps, 1000.0, 20_000.0, 500_000.0),
            "insolation_min_w_m2": float(q.min()),
            "insolation_max_w_m2": float(q.max()),
            "insolation_std_w_m2": float(q.std()),
        }

    moon_2 = state_metrics(with_moon_long, 2_000_000.0)
    nomoon_2 = state_metrics(no_moon_long, 2_000_000.0)
    moon_20 = state_metrics(with_moon_long, 20_000_000.0)
    nomoon_20 = state_metrics(no_moon_long, 20_000_000.0)

    summary = {
        "status": "executed_reduced_secular_spin_model",
        "scope": "model-level; lunar torque effective, Moon orbit and tides not resolved",
        "orbital_forcing": "ORI-C real_science_max eight-planet N-body Earth output",
        "reference": "La2004 INSOLN.LA2004.BTL.ASC",
        "alpha_with_moon_arcsec_per_year": ALPHA_WITH_MOON_ARCSEC_PER_YEAR,
        "alpha_solar_only_arcsec_per_year": ALPHA_SOLAR_ONLY_ARCSEC_PER_YEAR,
        "initial_obliquity_deg": 23.43929111,
        "with_moon_2myr": moon_2,
        "no_moon_2myr": nomoon_2,
        "with_moon_20myr": moon_20,
        "no_moon_20myr": nomoon_20,
        "ensemble_floor_2myr": {
            "obliquity_rms_deg": obliquity_floor,
            "insolation_rms_w_m2": insolation_floor,
            "realizations": 8,
        },
        "minimum_intervention_effect_to_ensemble_floor": {
            "obliquity": float(interventions["obliquity_effect_to_ensemble_floor"].min()),
            "insolation": float(interventions["insolation_effect_to_ensemble_floor"].min()),
        },
        "convergence": convergence,
        "la2004_validation": validation_rows,
        "interpretation": (
            "Le couple lunaire effectif stabilise fortement l'obliquité dans ce modèle séculaire réduit. "
            "L'ablation lunaire augmente fortement l'amplitude de l'obliquité et de l'insolation. "
            "Les six interventions Jupiter/Saturne restent mesurables après propagation jusqu'au spin et à l'insolation. "
            "Ce résultat ne remplace pas une intégration Terre-Lune explicite avec marées."
        ),
    }
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "convergence.json").write_text(json.dumps(convergence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Figures simples et reproductibles.
    plt.figure(figsize=(10, 5.5))
    sel = with_moon_long["elapsed_years"] <= 2_000_000.0
    x = -with_moon_long.loc[sel, "elapsed_years"].to_numpy() / 1e6
    plt.plot(x, with_moon_long.loc[sel, "obliquity_deg"], label="avec couple lunaire effectif")
    plt.plot(x, no_moon_long.loc[sel, "obliquity_deg"], label="ablation lunaire")
    plt.xlabel("Temps depuis J2000 (Ma)")
    plt.ylabel("Obliquité (°)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures / "obliquite_avec_sans_lune_2myr.png", dpi=180)
    plt.close()

    plt.figure(figsize=(10, 5.5))
    plt.plot(x, with_moon_long.loc[sel, "insolation_65n_solstice_w_m2"], label="avec couple lunaire effectif")
    plt.plot(x, no_moon_long.loc[sel, "insolation_65n_solstice_w_m2"], label="ablation lunaire")
    plt.xlabel("Temps depuis J2000 (Ma)")
    plt.ylabel("Insolation journalière 65°N, solstice (W/m²)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures / "insolation_65n_avec_sans_lune_2myr.png", dpi=180)
    plt.close()

    report = [
        "# Résultat exécuté — spin, obliquité et ablation lunaire",
        "",
        "## Statut",
        "",
        "Cette couche est **calculée**. Elle n'est plus une simple feuille de route. Elle reste un modèle séculaire réduit : le couple lunaire est représenté par la constante de précession effective, sans orbite lunaire explicite ni évolution tidale.",
        "",
        "## Chaîne calculée",
        "",
        "`architecture N-corps → plan orbital terrestre → spin → obliquité → équinoxe mobile → insolation à 65°N`",
        "",
        "Une ablation architecturale est calculée en remplaçant `α = 54,93″/an` par la valeur solaire seule `α ≈ 20″/an`, toutes les séries orbitales étant identiques.",
        "",
        "## Validation La2004",
        "",
        validation.to_markdown(index=False),
        "",
        "## Avec et sans couple lunaire",
        "",
        pd.DataFrame([
            {"configuration": "avec Lune effective", **moon_2},
            {"configuration": "sans Lune", **nomoon_2},
        ]).to_markdown(index=False),
        "",
        "## Propagation des interventions Jupiter/Saturne",
        "",
        interventions.to_markdown(index=False),
        "",
        "## Bruit et convergence",
        "",
        f"Dispersion RMS de l'ensemble orbital propagé au spin : `{obliquity_floor:.6g}°` ; propagée à l'insolation : `{insolation_floor:.6g} W/m²`.",
        "",
        f"Le plus petit rapport effet intervention / dispersion d'ensemble vaut `{interventions['obliquity_effect_to_ensemble_floor'].min():.3g}` pour l'obliquité et `{interventions['insolation_effect_to_ensemble_floor'].min():.3g}` pour l'insolation.",
        "",
        f"La convergence 100 ans → 50 ans donne une RMSE d'obliquité de `{convergence['with_moon_obliquity_rmse_deg']:.3g}°` avec Lune effective.",
        "",
        "## Limite qui reste ouverte",
        "",
        "Cette exécution établit le chaînage dynamique jusqu'à l'obliquité et à l'insolation **dans un modèle séculaire de spin comparé à La2004**. Elle ne constitue pas encore une intégration Terre-Lune explicite : l'orbite lunaire, les marées et l'évolution de la distance Terre-Lune restent à traiter dans une extension longue durée distincte.",
        "",
    ]
    (out / "RAPPORT.md").write_text("\n".join(report), encoding="utf-8")

    write_results_manifest(out)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
