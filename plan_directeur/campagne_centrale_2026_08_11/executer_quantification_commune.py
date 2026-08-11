#!/usr/bin/env python3
"""Construit les mesures ORI-C réellement calculables sans homogénéisation arbitraire."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "resultats"


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def build() -> tuple[dict, dict]:
    orbital = load("02_branche_systeme_solaire/tests_suivants/resultats/PACC_ASTRONOMIQUE.json")
    al26 = load("01_branche_matiere/genealogie_cosmique_quantitative/resultats/DISTRIBUTION_ACCESSIBILITE_26AL.json")
    antibiotic = load("03_branche_vivant/benchmark_histoire_antibiotique_2026/resultats/RESULTAT.json")
    information = load("01_branche_matiere/genealogie_cosmique_quantitative/resultats/INFORMATION_HISTORIQUE.json")
    h011 = load("01_branche_matiere/tests_causaux/resultats/H011_RESULTAT.json")

    measures = {
        "schema": "oric.common-measures.v1",
        "comparability_status": "local_definitions_only_not_cross_domain_invariant",
        "measures": [
            {
                "id": "PACC-ORB-01", "domain": "orbital_model", "metric": "P_acc",
                "value": orbital["Pacc_dimensions"], "numerator": orbital["accessible_dimension_cells"],
                "denominator": orbital["total_dimension_cells"], "X": orbital["baseline"],
                "H": "intervention on architecture", "Theta": orbital["reference_variants"],
                "tau": "2 Myr", "uncertainty": orbital["reference_envelope"],
                "scope": "fraction of computed intervention-metric cells, not a natural probability",
            },
            {
                "id": "PACC-26AL-01", "domain": "cosmic_chronology", "metric": "P_acc_partition",
                "value": {event["event"]: event["reservoir_scenarios"]["canonique_homogene"]["accessible_thresholds_robust_q025"] for event in al26["events"]},
                "partition": al26["threshold_partition"], "H": al26["reservoir_history_model"],
                "tau": "time after CAI with published sigma", "uncertainty": "q025-q975 analytic age propagation",
                "scope": "physical inventory accessibility; not thermal response probability",
            },
            {
                "id": "DELTA-H-ANT-01", "domain": "living_antibiotic", "metric": "history_predictive_gain",
                "value_percent": antibiotic["history_gain_percent"], "X": "present limitation + antibiotic",
                "H": "ancestor/history label", "R": "MIC", "tau": "experimental endpoint",
                "model_state_only_rmse": antibiotic["rmse_state_only"],
                "model_history_rmse": antibiotic["rmse_state_plus_history"],
                "permutation_p": antibiotic["permutation_p_history_better_than_shuffled"],
                "P_acc": None, "scope": "future response information, not an accessible-set measure",
            },
            {
                "id": "I-H-COSMOS-01", "domain": "cosmic_isotopes", "metric": "decodable_historical_information",
                "value": [{"dataset": r["dataset"], "status": r["status"], "loo_accuracy": r.get("loo_accuracy"), "normalized_mi_mean": r.get("normalized_mi_mean")} for r in information["results"]],
                "scope": "within-stage provenance decoding; no same-carrier inter-stage information curve",
            },
        ],
        "missing_for_transversal_test": ["common finite P_acc partition", "measured m in all cases", "tau_m in all cases", "paired ablation A in at least three domains"],
    }

    bifurcations = {
        "schema": "oric.bifurcation-register.v1",
        "entries": [
            {
                "id": "BIF-MAT-H011", "domain": "matter_model", "control_variable": "turbulence",
                "threshold_measure": "critical metallicity", "history": "simulation initial conditions",
                "after_state": "mechanistic threshold crossed", "threshold_ratio_high_low": h011["threshold_ratio_high_low_turbulence"],
                "reversibility": "not tested", "relaxation_time": None,
                "evidence": h011["h011_status"], "natural_measurement": False,
            },
            {
                "id": "BIF-COS-26AL", "domain": "cosmic_chronology", "control_variable": "time after CAI",
                "threshold_measure": al26["threshold_partition"],
                "after_state": "lower radiogenic-inventory accessibility class", "history": al26["reservoir_history_model"],
                "reversibility": "irreversible radioactive decay", "relaxation_time": al26["half_life_myr"],
                "evidence": al26["status"], "natural_measurement": True,
            },
            {
                "id": "BIF-ORB-INTERVENTIONS", "domain": "orbital_model", "control_variable": "planet mass or semimajor axis",
                "threshold_measure": "reference numerical envelope exceeded on >=2 metrics",
                "after_state": "different accessible orbital response class", "history": "architecture intervention",
                "reversibility": "not a natural intervention", "relaxation_time": "2 Myr observation horizon",
                "evidence": orbital["status"], "natural_measurement": False,
            },
        ],
        "unmeasured_fields": ["L_t and G_t as enumerated physical sets", "relaxation time after paired histories", "cross-domain normalized threshold"],
    }
    return measures, bifurcations


def main() -> int:
    measures, bifurcations = build()
    OUT.mkdir(exist_ok=True)
    for name, value in (("MESURES_COMMUNES_EXECUTEES.json", measures), ("REGISTRE_BIFURCATIONS.json", bifurcations)):
        (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(measures['measures'])} mesures locales; {len(bifurcations['entries'])} bifurcations documentées")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
