#!/usr/bin/env python3
"""Construit le benchmark transversal depuis les artefacts réels, sans compléter les champs absents."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "resultats"
SELECTED = [
    "C-ANT-01", "C-VES-02", "C-VES-03", "C-MAT-MEM-05", "C-AST-01",
    "MPT-M2-01", "PID-ANT-01", "GCQ-T09", "GCQ-T10", "GCQ-T11",
    "GCQ-T12", "GCQ-T13", "GCQ-T14", "GCQ-T15", "GCQ-T16", "GCQ-T17",
    "GCQ-T18", "GCQ-T19", "GCQ-T20", "GCQ-T21", "EXO-DOM-01",
]
FIELDS = ["X", "H", "m", "Theta", "tau", "P_acc", "R"]

# Couverture déclarée à partir des protocoles et non inférée d'un verdict.
COVERAGE = {
    "C-ANT-01": {"X", "H", "Theta", "tau", "R"},
    "C-VES-02": {"X", "H", "m", "Theta", "tau", "P_acc", "R"},
    "C-VES-03": {"X", "H", "m", "Theta", "tau", "P_acc", "R"},
    "C-MAT-MEM-05": {"H", "m", "Theta", "tau", "R"},
    "C-AST-01": {"X", "H", "m", "Theta", "tau", "P_acc", "R"},
    "MPT-M2-01": {"X", "H", "Theta", "tau", "R"},
    "PID-ANT-01": {"X", "H", "m", "Theta", "tau", "P_acc", "R"},
    "GCQ-T09": {"X", "H", "m", "Theta", "tau", "P_acc", "R"},
    "EXO-DOM-01": {"X", "H", "m", "Theta", "tau", "P_acc", "R"},
}

SYSTEM_ID = {
    "C-ANT-01": "donofrio_antibiotic",
    "PID-ANT-01": "donofrio_antibiotic",
    "C-VES-02": "sokolskyi_baum_vesicles",
    "C-VES-03": "sokolskyi_baum_vesicles",
    "C-MAT-MEM-05": "material_memory_families",
    "C-AST-01": "solar_system_model",
    "MPT-M2-01": "paleoclimate_M2",
    "GCQ-T09": "cosmic_26Al",
    "EXO-DOM-01": "exoplanet_reduced_climate_direct_m",
}

SUPPLEMENTAL = {
    "C-VES-02": "03_branche_vivant/lignees_vesicules/resultats/RESULTAT.json",
    "C-VES-03": "03_branche_vivant/lignees_vesicules/resultats/RESULTAT.json",
    "PID-ANT-01": "03_branche_vivant/benchmark_histoire_antibiotique_2026/resultats/PID_X_M_A.json",
    "C-AST-01": "02_branche_systeme_solaire/tests_suivants/resultats/TRACE_ORBITALE_M.json",
    "GCQ-T09": "01_branche_matiere/genealogie_cosmique_quantitative/resultats/DISTRIBUTION_ACCESSIBILITE_26AL.json",
    "EXO-DOM-01": "02_branche_systeme_solaire/couche_memoire_historique/do_m_trace/resultats/RESULTAT_DO_M.json",
}

QUALITY = {
    "C-VES-02": {"m": "direct_parent_measurement", "P_acc": "retrospective_observed_support", "ablation": False},
    "C-VES-03": {"m": "targeted_parent_trace", "P_acc": "retrospective_observed_support_under_ablation_controls", "ablation": True},
    "PID-ANT-01": {"m": "historical_state_label_not_isolated_physical_trace", "P_acc": "retrospective_observed_MIC_support", "ablation": False},
    "C-AST-01": {"m": "retrospective_model_spectral_trace", "P_acc": "model_intervention_accessibility", "ablation": True},
    "GCQ-T09": {"m": "derived_continuous_radiogenic_inventory_from_empirical_ages", "P_acc": "thresholded_physical_inventory_accessibility", "ablation": False},
    "EXO-DOM-01": {"m": "direct_model_slow_state_targeted_reset", "P_acc": "model_future_challenge_accessibility", "ablation": True},
}

CAUSAL_CLASS = {
    "C-VES-02": "retrospective_lineage_observation",
    "C-VES-03": "m_ablation",
    "PID-ANT-01": "history_permutation",
    "C-AST-01": "architecture_intervention",
    "GCQ-T09": "retrospective_physical_history",
    "EXO-DOM-01": "m_ablation",
}

INV_A_ROLE = {
    "C-VES-02": "observational_support_not_direct_test",
    "C-VES-03": "direct_m_ablation_Pacc_test_negative_expected_direction",
    "PID-ANT-01": "information_proxy_m_not_physical_isolated",
    "C-AST-01": "architecture_causal_prototype_not_m_ablation",
    "GCQ-T09": "physical_history_trace_without_m_intervention",
    "EXO-DOM-01": "direct_model_m_reset_with_exact_X_Theta_A_matching",
}

TAU_QUALITY = {
    "C-VES-02": {"kind": "tau_obs", "tau_m_measured": False, "cross_domain_comparable": False},
    "C-VES-03": {"kind": "tau_obs", "tau_m_measured": False, "cross_domain_comparable": False},
    "PID-ANT-01": {"kind": "experimental_endpoint", "tau_m_measured": False, "cross_domain_comparable": False},
    "C-AST-01": {"kind": "observation_horizon", "tau_m_measured": False, "cross_domain_comparable": False},
    "GCQ-T09": {"kind": "tau_decay_local", "tau_m_measured": True, "cross_domain_comparable": False},
    "EXO-DOM-01": {"kind": "tau_m_local_effective", "tau_m_measured": True, "cross_domain_comparable": False},
}

NEXT_ACTION = {
    "C-ANT-01": "isoler une trace biologique m distincte de l'étiquette d'histoire et mesurer P_acc sur le panneau brut",
    "C-MAT-MEM-05": "obtenir un état X apparié et un P_acc après ablation sur au moins une famille matérielle complète",
    "MPT-M2-01": "ne pas prolonger M2; conserver le résultat négatif et déplacer l'effort vers PALEO-HISTORY",
}


def build() -> tuple[dict, dict]:
    registry_path = ROOT / "preuves/PREUVES.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    by_id = {entry["id"]: entry for entry in registry["entries"]}
    operationalization_path = HERE / "OPERATIONNALISATION_M_PACC_20_CAS.json"
    operationalization = json.loads(operationalization_path.read_text(encoding="utf-8"))
    op_by_id = {case["id"]: case for case in operationalization["cases"]}
    cases = []
    for case_id in SELECTED:
        entry = by_id[case_id]
        artifact = ROOT / entry["artefact"]
        present = artifact.is_file()
        covered = COVERAGE.get(case_id, {"X", "H", "Theta", "tau", "R"})
        op = op_by_id[case_id]
        missing = [field for field in FIELDS if field not in covered]
        supplemental_rel = SUPPLEMENTAL.get(case_id)
        supplemental = ROOT / supplemental_rel if supplemental_rel else None
        cases.append({
            "id": case_id,
            "system_id": SYSTEM_ID.get(case_id, case_id),
            "question": entry["question"],
            "verdict": entry["verdict"],
            "evidence_level": entry["niveau_preuve"],
            "scope": entry["portee"],
            "artifact": entry["artefact"],
            "artifact_present": present,
            "artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest() if present else None,
            "supplemental_measurement_artifact": supplemental_rel,
            "supplemental_measurement_sha256": hashlib.sha256(supplemental.read_bytes()).hexdigest() if supplemental and supplemental.is_file() else None,
            "m_operational_definition": op["m"],
            "P_acc_operational_definition": op["P_acc"],
            "m_P_acc_measurement_status": op["measurement_status"],
            "measurement_quality": QUALITY.get(case_id, {}),
            "causal_test_class": CAUSAL_CLASS.get(case_id, "not_classified_for_INV_A"),
            "inv_a_role": INV_A_ROLE.get(case_id, "not_directly_mapped"),
            "tau_quality": TAU_QUALITY.get(case_id, {"kind": "declared_tau_not_audited", "tau_m_measured": False, "cross_domain_comparable": False}),
            "replication_unit": SYSTEM_ID.get(case_id, case_id),
            "field_coverage": {field: field in covered for field in FIELDS},
            "field_completeness_fraction": len(covered) / len(FIELDS),
            "missing_fields": missing,
            "next_action": NEXT_ACTION.get(case_id, "aucune extension prioritaire sans nouvelle mesure indépendante" if not missing else f"mesurer d'abord {missing[0]} sans compléter les autres champs par hypothèse"),
            "eligible_for_common_invariant": not missing,
        })
    complete = [case for case in cases if case["eligible_for_common_invariant"]]
    complete_systems = sorted({case["system_id"] for case in complete})
    queue = sorted(
        (case for case in cases if case["missing_fields"]),
        key=lambda case: (len(case["missing_fields"]), case["id"]),
    )
    benchmark = {
        "schema": "oric.transversal-benchmark.v2",
        "selection": "21 cas réels ou résultats de modèle explicitement qualifiés; EXO-DOM-01 est une extension exploratoire postérieure explicitement étiquetée",
        "case_count": len(cases),
        "required_fields": FIELDS,
        "operational_definitions_complete": len(op_by_id) == len(SELECTED),
        "field_complete_case_count": len(complete),
        "field_complete_unique_system_count": len(complete_systems),
        "field_complete_unique_system_ids": complete_systems,
        "warning": "complétude des champs ne signifie ni indépendance des cas, ni chaîne mécanistique causale, ni comparabilité métrique entre domaines",
        "priority_completion_queue": [
            {"id": case["id"], "missing_fields": case["missing_fields"], "next_action": case["next_action"]}
            for case in queue[:10]
        ],
        "cases": cases,
    }
    eligible = [case["id"] for case in complete]
    invariants = {
        "schema": "oric.transversal-invariants-audit.v2",
        "cases_total": len(cases),
        "cases_complete_X_H_m_Theta_tau_Pacc_R": len(eligible),
        "eligible_case_ids": eligible,
        "unique_complete_systems": complete_systems,
        "tests": [
            {
                "id": "INV-A", "hypothesis": "Delta m -> Delta P_acc",
                "status": "exploratory_comparison_ready_not_confirmatory",
                "reason": "deux systèmes ont désormais une intervention directe sur m: le contraste vésiculaire ne soutient pas sa direction positive locale, tandis que EXO-DOM-01 produit un effet non nul au niveau modèle avec X/Theta/A appariés; cela ne constitue pas une réplication empirique transversale",
                "companion_audit": "resultats/AUDIT_INV_A.json",
            },
            {"id": "INV-B", "hypothesis": "tau_m/tau_T -> force historique", "status": "non_testable", "reason": "tau_m n'est pas mesuré de façon comparable"},
            {"id": "INV-C", "hypothesis": "transitions irréversibles ferment et ouvrent des possibles", "status": "partially_operationalized", "reason": "26Al et vésicules possèdent des partitions locales, mais L_t/G_t ne sont pas énumérés transversalement"},
            {"id": "INV-D", "hypothesis": "information historique décroît ou change de support", "status": "partial_nonconclusive", "reason": "l'analyse inter-étages cosmique est exécutée mais ne sépare pas l'association de l'échantillonnage par publication"},
            {"id": "INV-E", "hypothesis": "interfaces disproportionnées", "status": "non_testable"},
        ],
        "verdict": "la complétude opérationnelle progresse sur plusieurs systèmes, mais aucun invariant transversal général n'est validé",
        "rule": "l'hétérogénéité des métriques et la dépendance entre claims d'un même système ne sont pas masquées",
    }
    return benchmark, invariants


def main() -> int:
    OUT.mkdir(exist_ok=True)
    benchmark, invariants = build()
    for name, value in (("BENCHMARK_TRANSVERSAL.json", benchmark), ("AUDIT_INVARIANTS.json", invariants)):
        (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"{benchmark['case_count']} cas; {invariants['cases_complete_X_H_m_Theta_tau_Pacc_R']} complet(s); invariants={invariants['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
