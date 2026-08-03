"""Vérifie que le noyau compilé reproduit exactement les modèles de référence.

Aucun résultat de la campagne de stress n'a de valeur si le simulateur rapide
diverge du simulateur livré. Ce contrôle est exécuté avant toute campagne.
"""

from __future__ import annotations

import json
import time

import numpy as np

from core import (
    OUTPUT_ROOT,
    PARAMETER_NAMES,
    controlled_histories,
    exo_initial_states,
    exo_parameter_vector,
    simulate,
    simulate_exo,
)
from oric_memory_tests.exoplanet import simulate_reduced_climate
from oric_memory_tests.mpt import simulate_mpt


def check_mpt(rng) -> dict:
    forcing = rng.normal(size=2601)
    worst = {"M0": 0.0, "M1": 0.0, "M2": 0.0, "M2A": 0.0}
    for _ in range(40):
        parameters = {
            "forcing_gain": rng.uniform(-3, 3),
            "forcing_offset": rng.uniform(-2, 2),
            "tau_ice_kyr": rng.uniform(3, 120),
            "tau_fast_kyr": rng.uniform(3, 60),
            "tau_memory_gain_kyr": rng.uniform(0.1, 200),
            "regolith_scale": rng.uniform(0.05, 5),
            "tau_regolith_kyr": rng.uniform(200, 2500),
            "carbon_feedback_gain": rng.uniform(-2, 2),
            "tau_carbon_kyr": rng.uniform(200, 2500),
            "carbon_offset": rng.uniform(-2, 2),
        }
        initial = float(rng.normal())
        for model in ("M0", "M1", "M2"):
            names = PARAMETER_NAMES[model]
            values = np.array([parameters[name] for name in names])
            fast = simulate(model, forcing, initial, values)
            slow = simulate_mpt(model, forcing, initial, parameters)["ice"]
            worst[model] = max(
                worst[model], float(np.max(np.abs(fast - slow)))
            )
        # M2A doit reproduire l'ablation carbone du paquet livré.
        names = PARAMETER_NAMES["M2"]
        values = np.array([parameters[name] for name in names])
        fast = simulate("M2A", forcing, initial, values)
        slow = simulate_mpt(
            "M2", forcing, initial, parameters, carbon_ablation=True
        )["ice"]
        worst["M2A"] = max(worst["M2A"], float(np.max(np.abs(fast - slow))))
    return worst


def check_exo(rng) -> dict:
    history = controlled_histories(step_myr=0.02)
    time_myr = history["time_myr"]
    parameters = exo_parameter_vector()
    states = exo_initial_states(729, 3)
    worst = {}
    for mode in ("classic", "ablated", "M2"):
        largest = 0.0
        for state in states:
            for trajectory in ("A", "B"):
                fast = simulate_exo(
                    time_myr,
                    history[f"obliquity_{trajectory}_deg"],
                    history[f"eccentricity_{trajectory}"],
                    mode,
                    state,
                    parameters,
                )
                slow = simulate_reduced_climate(
                    time_myr,
                    history[f"obliquity_{trajectory}_deg"],
                    history[f"eccentricity_{trajectory}"],
                    mode,
                    state,
                )
                scale = np.maximum(np.abs(slow).max(axis=0), 1e-12)
                largest = max(
                    largest,
                    float(np.max(np.abs(fast - slow) / scale)),
                )
        worst[mode] = largest
    return worst


def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20260731)

    started = time.perf_counter()
    mpt_error = check_mpt(rng)
    exo_error = check_exo(rng)
    elapsed = time.perf_counter() - started

    # Mesure de gain de vitesse
    forcing = rng.normal(size=2601)
    values = np.array([-0.79, -0.06, 10.5, 0.54, 0.05, 2500.0, -2.0, 1180.0, -0.32])
    reference_parameters = dict(zip(PARAMETER_NAMES["M2"], values))

    t0 = time.perf_counter()
    for _ in range(20):
        simulate_mpt("M2", forcing, 0.0, reference_parameters)
    slow_time = (time.perf_counter() - t0) / 20

    simulate("M2", forcing, 0.0, values)
    t0 = time.perf_counter()
    for _ in range(200):
        simulate("M2", forcing, 0.0, values)
    fast_time = (time.perf_counter() - t0) / 200

    report = {
        "mpt_max_absolute_difference": mpt_error,
        "exoplanet_max_relative_difference": exo_error,
        "mpt_reference_seconds_per_call": slow_time,
        "mpt_compiled_seconds_per_call": fast_time,
        "speedup": slow_time / fast_time,
        "verification_seconds": elapsed,
        "mpt_bit_identical": all(value == 0.0 for value in mpt_error.values()),
        "exoplanet_within_1e-12": all(
            value < 1e-12 for value in exo_error.values()
        ),
    }
    path = OUTPUT_ROOT / "00_core_verification.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
