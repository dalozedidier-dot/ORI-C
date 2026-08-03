"""Campagne B (suite) — balayage du régime de forçage final.

Le protocole livré fait converger les deux histoires vers obliquité 23,5° et
excentricité 0,05. Sous ce forçage, l'EMIC réduit tombe dans un état
quasi totalement englacé (fraction de glace 0,9998), c'est-à-dire contre la
borne supérieure de la variable. La dépendance au chemin y est donc mesurée
entre deux états presque saturés.

Ce module pose la question maximale : existe-t-il un seul couple (obliquité
finale, excentricité finale) pour lequel

  a) l'EMIC réduit possède plus d'un attracteur (condition nécessaire d'une
     dépendance au chemin permanente), ou
  b) l'écart A−B franchit les seuils de matérialité préenregistrés et y reste
     après un palier long ?
"""

from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd

from core import (
    OUTPUT_ROOT,
    exo_initial_states,
    exo_parameter_vector,
    simulate_exo,
)
from oric_memory_tests.exoplanet import (
    MATERIALITY_THRESHOLDS,
    STATE_NAMES,
    TEST_VARIABLES,
    _smoothstep,
)

OUT = OUTPUT_ROOT / "exoplanet"
VARIABLE_INDEX = {name: index for index, name in enumerate(STATE_NAMES)}


def histories_to(final_obliquity, final_eccentricity, step_myr=0.02,
                 spinup_myr=10.0, history_myr=50.0, final_hold_myr=10.0):
    """Mêmes histoires A/B que le protocole livré, mais avec un point
    d'arrivée commun choisi."""
    time_myr = np.arange(
        -spinup_myr, history_myr + final_hold_myr + step_myr / 2.0, step_myr
    )
    progress = np.clip(time_myr / history_myr, 0.0, 1.0)
    remaining = 1.0 - _smoothstep(progress)
    excursion = 4.0 * progress * (1.0 - progress)

    obliquity_a = final_obliquity + (70.0 - final_obliquity) * remaining
    eccentricity_a = final_eccentricity + (0.30 - final_eccentricity) * remaining
    obliquity_b = (
        final_obliquity + (10.0 - final_obliquity) * remaining
        + (30.0 - 16.75) * excursion
    )
    eccentricity_b = (
        final_eccentricity + (0.01 - final_eccentricity) * remaining
        + (0.10 - 0.03) * excursion
    )

    before = time_myr < 0.0
    after = time_myr >= history_myr
    obliquity_a[before], eccentricity_a[before] = 70.0, 0.30
    obliquity_b[before], eccentricity_b[before] = 10.0, 0.01
    obliquity_a[after] = final_obliquity
    eccentricity_a[after] = final_eccentricity
    obliquity_b[after] = final_obliquity
    eccentricity_b[after] = final_eccentricity
    return time_myr, obliquity_a, eccentricity_a, obliquity_b, eccentricity_b


def attractor_probe(obliquity, eccentricity, parameters, probes, duration_myr,
                    seed=20260731):
    """Combien d'attracteurs sous un forçage constant ?"""
    step = 0.02
    time_myr = np.arange(0.0, duration_myr + step / 2.0, step)
    obliquity_series = np.full_like(time_myr, obliquity)
    eccentricity_series = np.full_like(time_myr, eccentricity)
    random = np.random.default_rng(seed)
    states = np.column_stack([
        random.uniform(-8.0, 8.0, probes),
        random.uniform(0.0, 1.0, probes),
        random.uniform(120.0, 900.0, probes),
        random.uniform(0.0, 1.0, probes),
        random.uniform(0.0, 2.0, probes),
    ])
    finals = np.empty((probes, len(STATE_NAMES)))
    for index, state in enumerate(states):
        finals[index] = simulate_exo(
            time_myr, obliquity_series, eccentricity_series, "M2",
            state, parameters
        )[-1]
    return finals


def path_probe(obliquity, eccentricity, parameters, states, holds):
    """Écart médian |A − B| de M2 pour plusieurs durées de palier."""
    output = {}
    for hold in holds:
        (time_myr, obliquity_a, eccentricity_a,
         obliquity_b, eccentricity_b) = histories_to(
            obliquity, eccentricity, final_hold_myr=float(hold)
        )
        mask = time_myr >= 50.0 + hold - 2.0
        deltas = np.empty((len(states), len(STATE_NAMES)))
        for index, state in enumerate(states):
            a = simulate_exo(time_myr, obliquity_a, eccentricity_a, "M2",
                             state, parameters)[mask].mean(axis=0)
            b = simulate_exo(time_myr, obliquity_b, eccentricity_b, "M2",
                             state, parameters)[mask].mean(axis=0)
            deltas[index] = np.abs(a - b)
        output[hold] = np.median(deltas, axis=0)
    return output


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    parameters = exo_parameter_vector()
    states = exo_initial_states(729, 40)

    obliquities = (5.0, 12.0, 18.0, 23.5, 30.0, 40.0, 50.0, 60.0, 70.0)
    eccentricities = (0.0, 0.02, 0.05, 0.10, 0.18, 0.30)
    holds = (10, 50, 200)

    rows = []
    started = time.perf_counter()
    for obliquity in obliquities:
        for eccentricity in eccentricities:
            finals = attractor_probe(
                obliquity, eccentricity, parameters, probes=150,
                duration_myr=400.0,
            )
            paths = path_probe(obliquity, eccentricity, parameters, states, holds)
            row = {
                "final_obliquity_deg": obliquity,
                "final_eccentricity": eccentricity,
                "attractor_ice_mean": float(finals[:, 1].mean()),
                "attractor_temperature_mean": float(finals[:, 0].mean()),
            }
            for variable in TEST_VARIABLES:
                position = VARIABLE_INDEX[variable]
                row[f"attractor_spread_{variable}"] = float(np.ptp(finals[:, position]))
                for hold in holds:
                    row[f"delta{hold}_{variable}"] = float(paths[hold][position])
            rows.append(row)
        print(f"  obliquité finale {obliquity}° : "
              f"{time.perf_counter() - started:.0f} s cumulées", flush=True)

    frame = pd.DataFrame(rows)
    frame.to_csv(OUT / "b_final_regime_scan.csv", index=False)

    summary = {
        "grid_points": len(frame),
        "obliquities_deg": list(obliquities),
        "eccentricities": list(eccentricities),
        "attractor_probes_per_point": 150,
        "attractor_duration_myr": 400.0,
        "variables": {},
    }
    for variable in TEST_VARIABLES:
        threshold = MATERIALITY_THRESHOLDS[variable]
        summary["variables"][variable] = {
            "threshold": threshold,
            "max_attractor_spread": float(frame[f"attractor_spread_{variable}"].max()),
            "points_with_multiple_attractors": int(
                (frame[f"attractor_spread_{variable}"] >= threshold).sum()
            ),
            "max_delta_10myr": float(frame[f"delta10_{variable}"].max()),
            "max_delta_200myr": float(frame[f"delta200_{variable}"].max()),
            "points_material_at_10myr": int(
                (frame[f"delta10_{variable}"] >= threshold).sum()
            ),
            "points_material_at_200myr": int(
                (frame[f"delta200_{variable}"] >= threshold).sum()
            ),
        }
    best = frame.loc[frame["delta10_temperature_k"].idxmax()]
    summary["best_temperature_point"] = {
        key: float(value) for key, value in best.items()
    }
    ice_free = frame.loc[frame["attractor_ice_mean"] < 0.9]
    summary["non_snowball_points"] = int(len(ice_free))
    if len(ice_free):
        summary["non_snowball_max_delta10_temperature_k"] = float(
            ice_free["delta10_temperature_k"].max()
        )
        summary["non_snowball_max_delta200_temperature_k"] = float(
            ice_free["delta200_temperature_k"].max()
        )
    (OUT / "b_final_regime_report.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=float),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
