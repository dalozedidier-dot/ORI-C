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
    interstage = load("01_branche_matiere/genealogie_cosmique_quantitative/resultats/INFORMATION_INTERETAGES.json")
    pid_antibiotic = load("03_branche_vivant/benchmark_histoire_antibiotique_2026/resultats/PID_X_M_A.json")
    vesicles = load("03_branche_vivant/lignees_vesicules/resultats/RESULTAT.json")
    orbital_trace = load("02_branche_systeme_solaire/tests_suivants/resultats/TRACE_ORBITALE_M.json")
    h011 = load("01_branche_matiere/tests_causaux/resultats/H011_RESULTAT.json")
    exoplanet = load("02_branche_systeme_solaire/couche_memoire_historique/results_stress/exoplanet/b_report.json")

    pacc_ant = pid_antibiotic["P_acc_retrospective"]
    pacc_ves_ablation = vesicles["P_acc_ablation_test"]
    measures = {
        "schema": "oric.common-measures.v2",
        "comparability_status": "multiple_local_measurements_available_but_no_common_cross_domain_scale",
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
                "id": "M-ORB-01", "domain": "orbital_model", "metric": "m_spectral_trace",
                "value": orbital_trace["distance_summary"], "bands": orbital_trace["bands"],
                "interventions": orbital_trace["intervention_count"],
                "scope": "retrospective model spectral fingerprint distinct from P_acc; not a natural-history reconstruction",
            },
            {
                "id": "PACC-26AL-01", "domain": "cosmic_chronology", "metric": "P_acc_partition",
                "value": {event["event"]: event["reservoir_scenarios"]["canonique_homogene"]["accessible_thresholds_robust_q025"] for event in al26["events"]},
                "partition": al26["threshold_partition"], "H": al26["reservoir_history_model"],
                "tau": "time after CAI with published sigma", "uncertainty": "q025-q975 analytic age propagation",
                "scope": "physical inventory accessibility; not thermal response probability",
            },
            {
                "id": "M-26AL-01", "domain": "cosmic_chronology", "metric": "m_continuous_radiogenic_inventory",
                "value": al26["m_trace"]["canonical_reservoir_trace"],
                "scope": al26["m_trace"]["limitation"],
            },
            {
                "id": "DELTA-H-ANT-01", "domain": "living_antibiotic", "metric": "history_predictive_gain",
                "value_percent": antibiotic["history_gain_percent"], "X": "present limitation + antibiotic",
                "H": "ancestor/history label", "R": "MIC", "tau": "experimental endpoint",
                "model_state_only_rmse": antibiotic["rmse_state_only"],
                "model_history_rmse": antibiotic["rmse_state_plus_history"],
                "permutation_p": antibiotic["permutation_p_history_better_than_shuffled"],
                "P_acc": pacc_ant["mean_P_acc"], "scope": "predictive gain plus retrospective observed MIC-support proxy",
            },
            {
                "id": "PACC-ANT-01", "domain": "living_antibiotic", "metric": "P_acc_retrospective_MIC_support",
                "value": pacc_ant["mean_P_acc"], "median": pacc_ant["median_P_acc"],
                "history_shuffled_null_mean": pacc_ant["same_complexity_history_permutation"]["null_mean_P_acc"],
                "p_narrower_than_shuffled": pacc_ant["same_complexity_history_permutation"]["p_one_sided_observed_support_narrower_than_shuffled"],
                "relative_contraction_vs_null_percent": pacc_ant["same_complexity_history_permutation"]["relative_support_contraction_vs_null_percent"],
                "scope": pacc_ant["limitation"],
            },
            {
                "id": "PACC-VES-ABL-01", "domain": "living_vesicles", "metric": "P_acc_ablation_contrast",
                "value": pacc_ves_ablation["mechanism_P_acc_ablation_contrast"],
                "bootstrap_q025": pacc_ves_ablation["bootstrap_transitions"]["q025"],
                "bootstrap_q975": pacc_ves_ablation["bootstrap_transitions"]["q975"],
                "verdict": pacc_ves_ablation["verdict"],
                "scope": pacc_ves_ablation["limitation"],
            },
            {
                "id": "TAU-26AL-01", "domain": "cosmic_chronology", "metric": "tau_decay",
                "value_myr": al26["half_life_myr"],
                "trace": "26Al radiogenic inventory",
                "tau_m_cross_domain_comparable": False,
                "scope": "échelle de décroissance physique locale; ne définit pas à elle seule une persistance universelle de m",
            },
            {
                "id": "TAU-EXO-RELAX-01", "domain": "exoplanet_history_model", "metric": "tau_relax",
                "values_myr": {key: value["efolding_myr"] for key, value in exoplanet["relaxation"].items()},
                "retained_fraction_at_longest_hold": {key: value["retained_fraction"] for key, value in exoplanet["relaxation"].items()},
                "tau_m_cross_domain_comparable": False,
                "scope": "temps de relaxation local d'une différence historique; la convergence vers zéro exclut une mémoire persistante sur l'horizon long de ce modèle",
            },
            {
                "id": "I-H-COSMOS-01", "domain": "cosmic_isotopes", "metric": "decodable_historical_information",
                "value": [{"dataset": r["dataset"], "status": r["status"], "loo_accuracy": r.get("loo_accuracy"), "normalized_mi_mean": r.get("normalized_mi_mean")} for r in information["results"]],
                "scope": "within-stage provenance decoding; no same-carrier full cosmic genealogy",
            },
            {
                "id": "I-H-COSMOS-INTERSTAGE-01", "domain": "cosmic_isotopes", "metric": "same_carrier_interstage_information_robustness",
                "value": [
                    {
                        "dataset": row["dataset"],
                        "normalized_I": row["normalized_I_stellar_type_host"],
                        "publication_stratified_p": row["publication_stratified_permutation_p"],
                        "loo_min": row["publication_robustness"]["leave_one_publication_out"]["min_normalized_I"],
                        "loo_max": row["publication_robustness"]["leave_one_publication_out"]["max_normalized_I"],
                        "largest_publication_fraction": row["publication_robustness"]["sampling_concentration"]["largest_publication_fraction"],
                    }
                    for row in interstage["results"]
                ],
                "scope": "association inter-étages mesurée mais non séparable de la stratégie d'échantillonnage par publication",
            },
        ],
        "field_complete_systems_now": ["sokolskyi_baum_vesicles", "donofrio_antibiotic", "solar_system_model", "cosmic_26Al"],
        "missing_for_transversal_test": [
            "common finite P_acc partition or explicit mapping between local partitions",
            "physical m distinct from H in the antibiotic information case",
            "tau_m measured on a comparable basis; local tau_decay and tau_relax are now inventoried but not equated",
            "paired causal ablation in at least three independent empirical domains",
            "independent replication of the living positive systems",
        ],
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
