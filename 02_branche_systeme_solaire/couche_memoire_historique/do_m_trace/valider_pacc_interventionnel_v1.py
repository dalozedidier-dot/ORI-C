#!/usr/bin/env python3
"""Test de sanité de PACC-INT-CHALLENGE-V1 sur EXO-DOM-01.

Ce script réutilise exactement le jeu de défis, les seuils et l'intervention déjà
figés pour EXO-DOM-01. Il valide le comportement de l'estimateur commun sans
modifier le niveau de preuve du résultat : le cas reste E4_modele et ne compte
pas comme mesure empirique de P_acc pour le §XIV.
"""
from __future__ import annotations

import json
import sys
from itertools import product
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / "resultats"

sys.path.insert(0, str(ROOT))
import run_do_m as legacy  # noqa: E402
from methodologie_puissance.pacc_causal import estimate_matched_intervention_pacc  # noqa: E402
from oric_memory_tests.exoplanet import MATERIALITY_THRESHOLDS, TEST_VARIABLES  # noqa: E402


def build() -> dict[str, object]:
    protocol = json.loads((HERE / "PROTOCOLE.json").read_text(encoding="utf-8"))
    reference = json.loads((OUT / "RESULTAT_DO_M.json").read_text(encoding="utf-8"))
    parameters = legacy.exo_parameter_vector()
    end_states = legacy._history_end_states(protocol, parameters)

    anchors: list[np.ndarray] = []
    control_cube: list[list[np.ndarray]] = []
    intervention_cube: list[list[np.ndarray]] = []
    sham_cube: list[list[np.ndarray]] = []
    reset_m = np.array([0.5, 0.5], dtype=float)
    challenges = list(product(
        protocol["future_challenge_set"]["obliquity_deg"],
        protocol["future_challenge_set"]["eccentricity"],
    ))

    for outputs in end_states.values():
        for base in outputs:
            control_state = base[:5].copy()
            intervention_state = base[:5].copy()
            intervention_state[3:5] = reset_m
            sham_state = control_state.copy()

            anchors.append(base[legacy.R_INDEX].copy())
            control_rows = []
            intervention_rows = []
            sham_rows = []
            for obl, ecc in challenges:
                control_rows.append(
                    legacy._future_response(control_state, float(obl), float(ecc), protocol, parameters)[legacy.R_INDEX]
                )
                intervention_rows.append(
                    legacy._future_response(intervention_state, float(obl), float(ecc), protocol, parameters)[legacy.R_INDEX]
                )
                sham_rows.append(
                    legacy._future_response(sham_state, float(obl), float(ecc), protocol, parameters)[legacy.R_INDEX]
                )
            control_cube.append(control_rows)
            intervention_cube.append(intervention_rows)
            sham_cube.append(sham_rows)

    thresholds = np.array([MATERIALITY_THRESHOLDS[name] for name in TEST_VARIABLES], dtype=float)
    estimate = estimate_matched_intervention_pacc(
        X_anchor=np.asarray(anchors),
        control_response=np.asarray(control_cube),
        intervention_response=np.asarray(intervention_cube),
        sham_response=np.asarray(sham_cube),
        materiality_thresholds=thresholds,
        matching={
            "X_matched": True,
            "Theta_matched": True,
            "architecture_matched": True,
            "m_targeted_only": True,
            "independent_units": True,
            "challenge_set_predeclared": True,
            "thresholds_predeclared": True,
            "future_response_after_intervention": True,
        },
        sham_tolerance=protocol["decision_rule"]["numerical_tolerance"],
        bootstrap_repeats=protocol["decision_rule"]["bootstrap_draws"],
        seed=protocol["decision_rule"]["bootstrap_seed"],
    )

    old = reference["P_acc"]
    tolerance = 1e-12
    checks = {
        "control_matches_reference": abs(estimate["P_acc_control_median"] - old["control_median"]) <= tolerance,
        "intervention_matches_reference": abs(estimate["P_acc_intervention_median"] - old["do_m_median"]) <= tolerance,
        "delta_matches_reference": abs(estimate["Delta_P_acc_median"] - old["Delta_signed_median"]) <= tolerance,
        "sham_matches_reference": abs(float(estimate["sham"]["max_abs_Delta_vs_control"]) - old["sham_max_abs_Delta"]) <= tolerance,
        "strict_estimator_qualifies_internal_model_test": estimate["causal_qualified"] is True,
    }
    passed = all(checks.values())
    return {
        "schema": "oric.pacc.exo-dom-sanity.v1",
        "id": "PACC-SANITY-EXO-DOM-01",
        "definition_id": estimate["definition_id"],
        "status": "passed_model_sanity_check" if passed else "failed_model_sanity_check",
        "passed": passed,
        "scientific_scope": "validation technique de l'estimateur sur un modèle déjà exécuté; aucun relèvement de niveau de preuve",
        "evidence_level": "E4_modele",
        "counts_for_section_xiv_condition_9": False,
        "reference_result": "RESULTAT_DO_M.json",
        "reference_values": {
            "P_acc_control_median": old["control_median"],
            "P_acc_do_m_median": old["do_m_median"],
            "Delta_P_acc_signed_median": old["Delta_signed_median"],
            "sham_max_abs_Delta": old["sham_max_abs_Delta"],
        },
        "checks": checks,
        "estimate": estimate,
    }


def main() -> int:
    result = build()
    OUT.mkdir(exist_ok=True)
    path = OUT / "VALIDATION_PACC_INTERVENTIONNEL_V1.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(
        f"{result['id']}: status={result['status']}; "
        f"Pacc={result['estimate']['P_acc_control_median']:.3f}->"
        f"{result['estimate']['P_acc_intervention_median']:.3f}; "
        f"Delta={result['estimate']['Delta_P_acc_median']:.3f}"
    )
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
