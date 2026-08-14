#!/usr/bin/env python3
"""Évalue INV-A sans homogénéiser artificiellement les domaines."""
from __future__ import annotations

import importlib.util
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "resultats"


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def benchmark() -> dict:
    path = HERE / "construire_benchmark_transversal.py"
    spec = importlib.util.spec_from_file_location("oric_benchmark_for_invariant", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    result, _ = module.build()
    return result


def common_results() -> dict:
    path = HERE / "construire_resultats_communs.py"
    spec = importlib.util.spec_from_file_location("oric_common_results_for_invariant", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.build()


def build() -> tuple[dict, dict]:
    spec = json.loads((HERE / "INVARIANT_TRANSVERSAL_INV_A.json").read_text(encoding="utf-8"))
    bench = benchmark()
    common = common_results()
    by_id = {case["id"]: case for case in bench["cases"]}

    vesicles = load("03_branche_vivant/lignees_vesicules/resultats/RESULTAT.json")
    antibiotic = load("03_branche_vivant/benchmark_histoire_antibiotique_2026/resultats/PID_X_M_A.json")
    orbital = load("02_branche_systeme_solaire/tests_suivants/resultats/PACC_ASTRONOMIQUE.json")
    al26 = load("01_branche_matiere/genealogie_cosmique_quantitative/resultats/DISTRIBUTION_ACCESSIBILITE_26AL.json")
    exoplanet = load("02_branche_systeme_solaire/couche_memoire_historique/results_stress/exoplanet/b_report.json")
    exo_do_m = load("02_branche_systeme_solaire/couche_memoire_historique/do_m_trace/resultats/RESULTAT_DO_M.json")

    ant = antibiotic["P_acc_retrospective"]
    ant_null = ant["same_complexity_history_permutation"]
    ant_delta = ant["mean_P_acc"] - ant_null["null_mean_P_acc"]

    ves = vesicles["P_acc_ablation_test"]
    ves_delta = ves["mechanism_P_acc_ablation_contrast"]
    ves_q025 = ves["bootstrap_transitions"]["q025"]
    ves_q975 = ves["bootstrap_transitions"]["q975"]

    orbital_ratios = [
        value
        for row in orbital["detail"]
        for value in row["effect_over_reference_envelope"].values()
    ]

    al_trace = al26["m_trace"]["canonical_reservoir_trace"]
    robust_threshold_counts = {
        event["event"]: len(event["reservoir_scenarios"]["canonique_homogene"]["accessible_thresholds_robust_q025"])
        for event in al26["events"]
    }

    contrasts = {
        "schema": "oric.local-accessibility-contrasts.inv-a.v1",
        "invariant_id": "INV-A",
        "rule": "contrastes calculés dans l'échelle locale; aucune comparaison de magnitude interdomaines",
        "cross_domain_magnitude_comparison_allowed": False,
        "entries": [
            {
                "claim_id": "PID-ANT-01",
                "system_id": "donofrio_antibiotic",
                "control_class": "history_permutation",
                "target_lever": "H_label_proxy_not_physical_m",
                "P_acc_observed": ant["mean_P_acc"],
                "P_acc_reference": ant_null["null_mean_P_acc"],
                "Delta_acc_signed": ant_delta,
                "relative_Delta_acc_vs_reference": ant_delta / ant_null["null_mean_P_acc"],
                "permutation_p": ant_null["p_one_sided_observed_support_narrower_than_shuffled"],
                "direct_INV_A_m_ablation": False,
                "interpretation": "non-réductibilité informationnelle et contraction rétrospective du support; m physique non isolé",
            },
            {
                "claim_id": "C-VES-03",
                "system_id": "sokolskyi_baum_vesicles",
                "branch": "vivant",
                "empirical": True,
                "control_class": "m_ablation",
                "target_lever": "parental_trace",
                "Delta_acc_signed": ves_delta,
                "bootstrap_q025": ves_q025,
                "bootstrap_q975": ves_q975,
                "zero_in_bootstrap_interval": ves_q025 <= 0.0 <= ves_q975,
                "predeclared_expected_direction": ves["direction_expected_if_complete_regime_opens_more_classes"],
                "verdict": ves["verdict"],
                "direct_INV_A_m_ablation": True,
                "direct_INV_A_support": False,
                "interpretation": "test direct de P_acc sous ablation; la direction positive attendue n'est pas soutenue",
            },
            {
                "claim_id": "C-AST-01",
                "system_id": "solar_system_model",
                "control_class": "architecture_intervention",
                "target_lever": "A",
                "P_acc_dimensions": orbital["Pacc_dimensions"],
                "effect_over_local_reference_envelope_min": min(orbital_ratios),
                "effect_over_local_reference_envelope_median": statistics.median(orbital_ratios),
                "effect_over_local_reference_envelope_max": max(orbital_ratios),
                "direct_INV_A_m_ablation": False,
                "interpretation": "prototype causal d'intervention architecturale; ne compte pas comme réplication de do(m)",
            },
            {
                "claim_id": "GCQ-T09",
                "system_id": "cosmic_26Al",
                "control_class": "retrospective_physical_history",
                "target_lever": "derived_radiogenic_trace",
                "m_trace": al_trace,
                "robust_accessible_threshold_count_by_event": robust_threshold_counts,
                "direct_INV_A_m_ablation": False,
                "interpretation": "relation physique temporelle et partition locale sans intervention sur m",
            },
            {
                "claim_id": "EXO-DOM-01",
                "system_id": "exoplanet_reduced_climate_direct_m",
                "branch": "systeme_solaire",
                "empirical": False,
                "evidence_level": exo_do_m["evidence_level"],
                "control_class": "m_ablation",
                "target_lever": "regolith_fraction_and_carbon_memory",
                "P_acc_control": exo_do_m["P_acc"]["control_median"],
                "P_acc_do_m": exo_do_m["P_acc"]["do_m_median"],
                "Delta_acc_signed": exo_do_m["P_acc"]["Delta_signed_median"],
                "D_acc_abs": exo_do_m["P_acc"]["abs_Delta_median"],
                "epsilon_acc": exo_do_m["P_acc"]["epsilon_acc"],
                "bootstrap_abs_q025": exo_do_m["P_acc"]["abs_Delta_bootstrap_q025"],
                "bootstrap_abs_q975": exo_do_m["P_acc"]["abs_Delta_bootstrap_q975"],
                "sham_max_abs_Delta": exo_do_m["P_acc"]["sham_max_abs_Delta"],
                "X_exact_by_construction": exo_do_m["matching"]["X_exact_by_construction"],
                "same_architecture": exo_do_m["matching"]["same_architecture"],
                "same_future_forcing": exo_do_m["matching"]["same_future_forcing"],
                "direct_INV_A_m_ablation": True,
                "direct_INV_A_support": exo_do_m["direct_INV_A_support"],
                "interpretation": "intervention directe ponctuelle sur m dans le modèle réduit; effet local non nul sans transfert au Système solaire réel",
            },
            {
                "claim_id": "C-VES-02",
                "system_id": "sokolskyi_baum_vesicles",
                "control_class": "retrospective_lineage_observation",
                "target_lever": "none",
                "P_acc_mean": vesicles["P_acc_measurement"]["mean_P_acc"],
                "P_acc_min": vesicles["P_acc_measurement"]["min_P_acc"],
                "P_acc_max": vesicles["P_acc_measurement"]["max_P_acc"],
                "direct_INV_A_m_ablation": False,
                "interpretation": "support observé et trace parentale directe; pas d'intervention P_acc propre à ce claim",
            },
        ],
        "normalization": {
            "definition": "C_acc = Delta_acc / B_acc uniquement si B_acc est défini indépendamment",
            "C_acc_current_cross_domain_values": None,
            "reason": "les témoins locaux ne fournissent pas encore un B_acc construit de manière comparable dans tous les domaines",
        },
    }

    tau_inventory = [
        {
            "id": "TAU-26AL-01",
            "system_id": "cosmic_26Al",
            "kind": "tau_decay",
            "value_myr": al26["half_life_myr"],
            "physical_trace": "26Al inventory",
            "tau_m_cross_domain_comparable": False,
        },
        {
            "id": "TAU-EXO-DOM-01",
            "system_id": "exoplanet_reduced_climate_direct_m",
            "kind": "tau_m_local_effective",
            "values_myr": {
                key: value["efolding_myr"] for key, value in exo_do_m["tau_m"].items()
            },
            "retained_fraction_at_240_myr": {
                key: value["retained_fraction_at_240_myr"] for key, value in exo_do_m["tau_m"].items()
            },
            "tau_m_cross_domain_comparable": False,
            "interpretation": "persistance locale de la trace ciblée mesurée directement après do(m) dans le modèle",
        },
        {
            "id": "TAU-EXO-RELAX-01",
            "system_id": "exoplanet_history_model",
            "kind": "tau_relax",
            "values_myr": {
                key: value["efolding_myr"]
                for key, value in exoplanet["relaxation"].items()
            },
            "retained_fraction_at_longest_hold": {
                key: value["retained_fraction"]
                for key, value in exoplanet["relaxation"].items()
            },
            "tau_m_cross_domain_comparable": False,
            "interpretation": "temps de relaxation local d'une différence historique, pas preuve d'une mémoire persistante commune",
        },
    ]

    complete_ids = set(bench["field_complete_unique_system_ids"])
    direct_entries = [entry for entry in contrasts["entries"] if entry["direct_INV_A_m_ablation"]]
    direct_systems = sorted({entry["system_id"] for entry in direct_entries})
    direct_support = [entry for entry in direct_entries if entry.get("direct_INV_A_support") is True]
    direct_support_systems = sorted({entry["system_id"] for entry in direct_support})
    direct_branches = sorted({entry.get("branch") for entry in direct_entries if entry.get("branch")})
    empirical_direct = [entry for entry in direct_entries if entry.get("empirical") is True]
    empirical_support = [entry for entry in direct_support if entry.get("empirical") is True]

    roles = {
        "direct_m_ablation": direct_systems,
        "direct_supporting_m_ablation": direct_support_systems,
        "direct_empirical_m_ablation": sorted({entry["system_id"] for entry in empirical_direct}),
        "direct_supporting_empirical_m_ablation": sorted({entry["system_id"] for entry in empirical_support}),
        "information_only_or_proxy": ["donofrio_antibiotic"],
        "architecture_intervention_prototype": ["solar_system_model"],
        "retrospective_physical_history": ["cosmic_26Al"],
        "observational_lineage_support": ["sokolskyi_baum_vesicles"],
    }

    gate_failures = []
    if len(direct_systems) < spec["future_transversal_gate"]["independent_systems_min"]:
        gate_failures.append("fewer_than_3_independent_direct_m_ablation_systems")
    if len(direct_branches) < spec["future_transversal_gate"]["branches_required"]:
        gate_failures.append("three_branches_not_replicated_with_do_m")
    if len({entry["system_id"] for entry in empirical_support}) < spec["future_transversal_gate"]["empirical_systems_min"]:
        gate_failures.append("fewer_than_2_supporting_empirical_direct_m_ablation_systems")
    gate_failures.extend([
        "future_or_reserved_validation_data_still_required",
        "tau_m_not_comparable_cross_domain",
        "no_common_validated_B_acc_construction",
    ])

    audit = {
        "schema": "oric.transversal-invariant-audit.inv-a.v2",
        "invariant": spec,
        "common_result_bundle_schema": common["schema"],
        "common_result_items_read": common["counts"]["total"],
        "common_result_field_complete_cases": common["counts"]["field_complete_cases"],
        "field_complete_claim_count": bench["field_complete_case_count"],
        "field_complete_unique_system_count": bench["field_complete_unique_system_count"],
        "field_complete_unique_system_ids": sorted(complete_ids),
        "replication_unit": "independent_system_not_claim",
        "roles": roles,
        "direct_m_ablation_system_count": len(direct_systems),
        "direct_supporting_m_ablation_system_count": len(direct_support_systems),
        "direct_positive_m_ablation_system_count": len(direct_support_systems),
        "direct_empirical_m_ablation_system_count": len({entry["system_id"] for entry in empirical_direct}),
        "direct_supporting_empirical_m_ablation_system_count": len({entry["system_id"] for entry in empirical_support}),
        "direct_m_ablation_branches": direct_branches,
        "future_gate_satisfied": len(gate_failures) == 0,
        "gate_failures": gate_failures,
        "tau_inventory": tau_inventory,
        "current_status": "candidate_operationalized_exploratory_not_validated",
        "current_verdict": "INV-A possède maintenant deux tests directs de do(m): le test vésiculaire ne soutient pas son contraste P_acc local, tandis que EXO-DOM-01 soutient un effet non nul au niveau modèle avec X/Theta/A appariés; la réplication empirique transversale reste ouverte",
        "rule": "un succès modèle ne remplace pas une réplication empirique; les résultats négatifs et les effets signés restent conservés",
    }
    return contrasts, audit


def main() -> int:
    contrasts, audit = build()
    OUT.mkdir(exist_ok=True)
    for name, value in (
        ("CONTRASTES_ACCESSIBILITE_INV_A.json", contrasts),
        ("AUDIT_INV_A.json", audit),
    ):
        (OUT / name).write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(
        f"INV-A: {audit['field_complete_unique_system_count']} systèmes 7/7; "
        f"do(m) direct={audit['direct_m_ablation_system_count']}; "
        f"do(m) positif={audit['direct_positive_m_ablation_system_count']}; "
        f"statut={audit['current_status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
