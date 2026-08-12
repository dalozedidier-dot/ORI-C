#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
MEMORY = HERE.parent
ROOT = HERE.parents[3]
OUT = HERE / "resultats"

sys.path.insert(0, str(MEMORY / "stress"))
sys.path.insert(0, str(MEMORY / "src"))

from core import controlled_histories, exo_initial_states, exo_parameter_vector, simulate_exo  # noqa: E402
from oric_memory_tests.exoplanet import MATERIALITY_THRESHOLDS, STATE_NAMES, TEST_VARIABLES  # noqa: E402

VARIABLE_INDEX = {name: index for index, name in enumerate(STATE_NAMES)}
M_INDEX = np.array([VARIABLE_INDEX["regolith_fraction"], VARIABLE_INDEX["carbon_memory"]])
R_INDEX = np.array([VARIABLE_INDEX[name] for name in TEST_VARIABLES])


def _bootstrap_interval(values: np.ndarray, draws: int, seed: int) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    n = len(values)
    medians = np.empty(draws, dtype=float)
    for index in range(draws):
        medians[index] = np.median(values[rng.integers(0, n, n)])
    return float(np.quantile(medians, 0.025)), float(np.quantile(medians, 0.975))


def _history_end_states(protocol: dict, parameters: np.ndarray) -> dict[str, np.ndarray]:
    settings = protocol["history_generation"]
    histories = controlled_histories(
        step_myr=settings["step_myr"],
        history_myr=settings["history_myr"],
        final_hold_myr=0.0,
    )
    initial_states = exo_initial_states(settings["ensemble_seed"], settings["ensemble_size"])
    result: dict[str, np.ndarray] = {}
    for label in settings["histories"]:
        rows = []
        for state in initial_states:
            simulation = simulate_exo(
                histories["time_myr"],
                histories[f"obliquity_{label}_deg"],
                histories[f"eccentricity_{label}"],
                "M2",
                state,
                parameters,
            )
            rows.append(simulation[-1])
        result[label] = np.asarray(rows)
    return result


def _future_response(initial_state: np.ndarray, obl: float, ecc: float, protocol: dict, parameters: np.ndarray) -> np.ndarray:
    challenge = protocol["future_challenge_set"]
    step = protocol["history_generation"]["step_myr"]
    horizon = challenge["horizon_myr"]
    time = np.arange(0.0, horizon + step / 2.0, step)
    obliquity = np.full_like(time, obl)
    eccentricity = np.full_like(time, ecc)
    simulation = simulate_exo(time, obliquity, eccentricity, "M2", initial_state, parameters)
    mask = time >= horizon - challenge["final_window_myr"]
    return simulation[mask].mean(axis=0)


def _pacc_for_state(base_output: np.ndarray, initial_state: np.ndarray, protocol: dict, parameters: np.ndarray) -> tuple[float, list[dict]]:
    thresholds = np.array([MATERIALITY_THRESHOLDS[name] for name in TEST_VARIABLES], dtype=float)
    base_response = base_output[R_INDEX]
    accessible = 0
    rows = []
    for obl in protocol["future_challenge_set"]["obliquity_deg"]:
        for ecc in protocol["future_challenge_set"]["eccentricity"]:
            response = _future_response(initial_state, float(obl), float(ecc), protocol, parameters)
            delta = response[R_INDEX] - base_response
            mask = np.abs(delta) >= thresholds
            accessible += int(mask.sum())
            rows.append({
                "obliquity_deg": float(obl),
                "eccentricity": float(ecc),
                "response": {name: float(response[VARIABLE_INDEX[name]]) for name in TEST_VARIABLES},
                "accessible": {name: bool(mask[index]) for index, name in enumerate(TEST_VARIABLES)},
            })
    denominator = protocol["P_acc"]["denominator"]
    return accessible / denominator, rows


def _tau_m(protocol: dict, end_states: dict[str, np.ndarray], parameters: np.ndarray) -> dict:
    step = 0.1
    horizon = 240.0
    time = np.arange(0.0, horizon + step / 2.0, step)
    obliquity = np.full_like(time, 23.5)
    eccentricity = np.full_like(time, 0.05)
    reference_m = np.array([0.5, 0.5])
    traces = {"regolith_fraction": [], "carbon_memory": []}
    for label, outputs in end_states.items():
        per_variable = {name: [] for name in traces}
        for base in outputs:
            control = base[:5].copy()
            intervention = base[:5].copy()
            intervention[3:5] = reference_m
            a = simulate_exo(time, obliquity, eccentricity, "M2", control, parameters)
            b = simulate_exo(time, obliquity, eccentricity, "M2", intervention, parameters)
            for name in traces:
                idx = VARIABLE_INDEX[name]
                per_variable[name].append(np.abs(a[:, idx] - b[:, idx]))
        for name in traces:
            traces[name].append(np.median(np.asarray(per_variable[name]), axis=0))
    result = {}
    for name, history_curves in traces.items():
        curve = np.median(np.asarray(history_curves), axis=0)
        initial = float(curve[0])
        positive = curve > max(initial * 1e-6, 1e-15)
        efolding = None
        if initial > 0 and positive.sum() >= 3:
            fit = np.polyfit(time[positive], np.log(curve[positive]), 1)
            if fit[0] < 0:
                efolding = float(-1.0 / fit[0])
        result[name] = {
            "initial_abs_trace_difference": initial,
            "abs_trace_difference_at_240_myr": float(curve[-1]),
            "retained_fraction_at_240_myr": float(curve[-1] / max(initial, 1e-300)),
            "efolding_myr": efolding,
        }
    return result


def build() -> dict:
    protocol = json.loads((HERE / "PROTOCOLE.json").read_text(encoding="utf-8"))
    parameters = exo_parameter_vector()
    end_states = _history_end_states(protocol, parameters)
    reset_m = np.array([0.5, 0.5], dtype=float)
    units = []
    sham_max = 0.0
    matching_max = {"temperature_k": 0.0, "ice_fraction": 0.0, "co2_ppm": 0.0}

    for history_label, outputs in end_states.items():
        for replicate, base in enumerate(outputs):
            control_state = base[:5].copy()
            do_m_state = base[:5].copy()
            do_m_state[3:5] = reset_m
            sham_state = base[:5].copy()

            for name in ("temperature_k", "ice_fraction", "co2_ppm"):
                idx = VARIABLE_INDEX[name]
                matching_max[name] = max(matching_max[name], abs(control_state[idx] - do_m_state[idx]))

            p_control, _ = _pacc_for_state(base, control_state, protocol, parameters)
            p_do_m, _ = _pacc_for_state(base, do_m_state, protocol, parameters)
            p_sham, _ = _pacc_for_state(base, sham_state, protocol, parameters)
            sham_max = max(sham_max, abs(p_sham - p_control))
            units.append({
                "history": history_label,
                "replicate": replicate,
                "m_control": {
                    "regolith_fraction": float(control_state[3]),
                    "carbon_memory": float(control_state[4]),
                },
                "m_do": {"regolith_fraction": 0.5, "carbon_memory": 0.5},
                "P_acc_control": float(p_control),
                "P_acc_do_m": float(p_do_m),
                "Delta_P_acc_signed": float(p_do_m - p_control),
                "abs_Delta_P_acc": float(abs(p_do_m - p_control)),
                "P_acc_sham": float(p_sham),
            })

    signed = np.array([row["Delta_P_acc_signed"] for row in units], dtype=float)
    absolute = np.abs(signed)
    rule = protocol["decision_rule"]
    q025, q975 = _bootstrap_interval(absolute, rule["bootstrap_draws"], rule["bootstrap_seed"])
    epsilon = protocol["P_acc"]["epsilon_acc"]
    support = bool(
        np.median(absolute) >= epsilon
        and q025 >= epsilon
        and sham_max <= rule["numerical_tolerance"]
    )

    result = {
        "schema": "oric.exoplanet-direct-m-intervention.result.v1",
        "id": protocol["id"],
        "status": protocol["status"],
        "evidence_level": protocol["evidence_level"],
        "system_id": protocol["system_id"],
        "matching": {
            "X_exact_by_construction": all(value <= rule["numerical_tolerance"] for value in matching_max.values()),
            "max_abs_X_difference_control_vs_do_m": matching_max,
            "same_architecture": True,
            "same_future_forcing": True,
            "targeted_variables_only": ["regolith_fraction", "carbon_memory"],
        },
        "P_acc": {
            "definition": protocol["P_acc"]["definition"],
            "denominator": protocol["P_acc"]["denominator"],
            "resolution": protocol["P_acc"]["resolution"],
            "epsilon_acc": epsilon,
            "control_median": float(np.median([row["P_acc_control"] for row in units])),
            "do_m_median": float(np.median([row["P_acc_do_m"] for row in units])),
            "Delta_signed_median": float(np.median(signed)),
            "Delta_signed_mean": float(np.mean(signed)),
            "abs_Delta_median": float(np.median(absolute)),
            "abs_Delta_bootstrap_q025": q025,
            "abs_Delta_bootstrap_q975": q975,
            "fraction_nonzero": float(np.mean(absolute > 0)),
            "sham_max_abs_Delta": float(sham_max),
        },
        "tau_m": _tau_m(protocol, end_states, parameters),
        "direct_INV_A_m_intervention": True,
        "direct_INV_A_support": support,
        "signed_direction": "decrease" if np.median(signed) < 0 else "increase" if np.median(signed) > 0 else "zero",
        "interpretation": (
            "do(m) modifie localement P_acc dans le modèle à X/Theta/A appariés; le signe est publié sans être universalisé"
            if support else
            "le do(m) propre n'atteint pas la règle locale gelée de soutien à INV-A"
        ),
        "scope": "intervention causale interne au modèle réduit; aucune intervention sur le vrai Système solaire et aucune réplication empirique",
        "units": units,
    }
    return result


def main() -> int:
    result = build()
    OUT.mkdir(exist_ok=True)
    path = OUT / "RESULTAT_DO_M.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    p = result["P_acc"]
    print(
        f"{result['id']}: X_match={result['matching']['X_exact_by_construction']}; "
        f"Pacc={p['control_median']:.3f}->{p['do_m_median']:.3f}; "
        f"median|Delta|={p['abs_Delta_median']:.3f}; support={result['direct_INV_A_support']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
