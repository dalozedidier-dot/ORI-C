#!/usr/bin/env python3
"""Audit exécutable des douze conditions du seuil scientifique (§XIV).

Le module ne crée aucun résultat scientifique. Il transforme le diagnostic déjà
publié dans `plan_directeur/AVANCEMENT_DU_PLAN.md` en porte machine fail-closed
et détaille les cinq verrous restant ouverts.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRED_DIR = HERE / "PREDICTIONS_PROSPECTIVES"


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def registry_count() -> int:
    path = ROOT / "plan_directeur/REGISTRE_HYPOTHESES.csv"
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return sum(1 for row in csv.DictReader(stream, delimiter=";") if any(row.values()))


def matter_transition_count() -> int:
    path = ROOT / "01_branche_matiere/base_transitions/transitions_matiere.csv"
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return sum(1 for _ in csv.DictReader(stream, delimiter=";"))


def branch_for_prediction(identifier: str) -> str:
    if identifier.startswith("PRED-VIVANT"):
        return "vivant"
    if identifier.startswith("PRED-PALEO"):
        return "systeme_solaire"
    return "matiere"


def prediction_audit() -> dict:
    rows = []
    registration_dir = PRED_DIR / "ENREGISTREMENTS_PUBLICS"
    for path in sorted(PRED_DIR.glob("PRED-*.json")):
        item = json.loads(path.read_text(encoding="utf-8"))
        result = item.get("resultat")
        registration_path = registration_dir / f"{item['id']}.registration.json"
        registration = json.loads(registration_path.read_text(encoding="utf-8")) if registration_path.exists() else {}
        public_preregistration = bool(
            registration.get("status") == "publicly_registered"
            and registration.get("public_url")
            and registration.get("registered_at")
        )
        success = bool(
            isinstance(result, dict)
            and result.get("success") is True
            and result.get("out_of_sample") is True
            and result.get("independent_test") is True
            and result.get("matched_control_beaten") is True
            and result.get("protocol_frozen_before_data") is True
            and public_preregistration
        )
        rows.append({
            "id": item["id"],
            "branch": branch_for_prediction(item["id"]),
            "status": item.get("statut"),
            "data_opened": item.get("date_ouverture") is not None,
            "result_present": result is not None,
            "strict_success": success,
            "matched_control_declared": bool(item.get("modele_concurrent")),
            "public_preregistration_present": public_preregistration,
            "registration_status": registration.get("status", "missing"),
            "registration_public_url": registration.get("public_url"),
        })
    successes = [row for row in rows if row["strict_success"]]
    successful_branches = sorted({row["branch"] for row in successes})
    required = ["matiere", "systeme_solaire", "vivant"]
    return {
        "schema": "oric.section-xiv.prediction-audit.v1",
        "strict_success_definition": (
            "résultat hors échantillon sur test indépendant, protocole gelé et enregistré publiquement "
            "avant les données, et témoin apparié battu"
        ),
        "predictions": rows,
        "strict_success_count": len(successes),
        "successful_branches": successful_branches,
        "branches_required": required,
        "all_branches_have_success": all(branch in successful_branches for branch in required),
    }


def pacc_strict_audit() -> dict:
    vesicles = load("03_branche_vivant/lignees_vesicules/resultats/RESULTAT.json")
    exo = load(
        "02_branche_systeme_solaire/couche_memoire_historique/do_m_trace/"
        "resultats/RESULTAT_DO_M.json"
    )
    al26 = load(
        "01_branche_matiere/genealogie_cosmique_quantitative/resultats/"
        "DISTRIBUTION_ACCESSIBILITE_26AL.json"
    )
    pid = load("03_branche_vivant/benchmark_histoire_antibiotique_2026/resultats/PID_X_M_A.json")
    sanity_path = ROOT / (
        "02_branche_systeme_solaire/couche_memoire_historique/do_m_trace/"
        "resultats/VALIDATION_PACC_INTERVENTIONNEL_V1.json"
    )
    sanity = json.loads(sanity_path.read_text(encoding="utf-8")) if sanity_path.exists() else {
        "status": "not_executed", "passed": False
    }
    vesicle_design_path = ROOT / "03_branche_vivant/lignees_vesicules/PROTOCOLE_PACC_CAUSAL_PROSPECTIF_V1.json"
    vesicle_design = json.loads(vesicle_design_path.read_text(encoding="utf-8")) if vesicle_design_path.exists() else {}
    vesicle_registration_path = ROOT / "03_branche_vivant/lignees_vesicules/VES-PACC-INT-01.registration.json"
    vesicle_registration = json.loads(vesicle_registration_path.read_text(encoding="utf-8")) if vesicle_registration_path.exists() else {}
    vesicle_preregistered = bool(
        vesicle_registration.get("status") == "publicly_registered"
        and vesicle_registration.get("public_url")
        and vesicle_registration.get("registered_at")
    )

    candidates = [
        {
            "id": "PACC-VES-RETRO-01",
            "branch": "vivant",
            "empirical": True,
            "definition_class": "observed_descendant_class_support",
            "value": vesicles["P_acc_measurement"]["mean_P_acc"],
            "m_intervention_present": True,
            "causal_Pacc_qualified": False,
            "reason": (
                "le contraste d'ablation est empirique, mais Pacc est défini par le support "
                "rétrospectif des classes descendantes et non par un ensemble de défis futurs gelé"
            ),
        },
        {
            "id": "PACC-EXO-DOM-01",
            "branch": "systeme_solaire",
            "empirical": False,
            "definition_class": "predeclared_challenge_dimension_materiality",
            "value_control": exo["P_acc"]["control_median"],
            "value_do_m": exo["P_acc"]["do_m_median"],
            "m_intervention_present": True,
            "causal_Pacc_qualified": False,
            "reason": "intervention causale interne au modèle réduit, pas mesure dans un système réel",
        },
        {
            "id": "PACC-26AL-01",
            "branch": "matiere",
            "empirical": True,
            "definition_class": "radiogenic_threshold_partition",
            "thresholds": al26.get("thresholds"),
            "m_intervention_present": False,
            "causal_Pacc_qualified": False,
            "reason": "partition physique rétrospective; aucune intervention ciblée sur m",
        },
        {
            "id": "PACC-DONOFRIO-PID-01",
            "branch": "vivant",
            "empirical": True,
            "definition_class": "retrospective_predictive_support",
            "value": pid.get("P_acc_retrospective", {}).get("mean_P_acc"),
            "m_intervention_present": False,
            "causal_Pacc_qualified": False,
            "reason": "permutation de H; m physique non isolé et non manipulé",
        },
    ]
    branches = ["matiere", "systeme_solaire", "vivant"]
    qualified_by_branch = {
        branch: [row["id"] for row in candidates if row["branch"] == branch and row["causal_Pacc_qualified"]]
        for branch in branches
    }
    return {
        "schema": "oric.section-xiv.pacc-strict-audit.v1",
        "strict_definition_id_for_future_tests": "PACC-INT-CHALLENGE-V1",
        "strict_definition_file": "protocoles_geles/PACC_INTERVENTIONNEL_V1.md",
        "candidates": candidates,
        "qualified_by_branch": qualified_by_branch,
        "qualified_branch_count": sum(bool(value) for value in qualified_by_branch.values()),
        "branches_required": branches,
        "condition_9_satisfied": all(qualified_by_branch[branch] for branch in branches),
        "tool_sanity_validation": {
            "id": sanity.get("id"),
            "status": sanity.get("status"),
            "passed": sanity.get("passed", False),
            "counts_for_condition_9": False,
            "source": sanity_path.relative_to(ROOT).as_posix() if sanity_path.exists() else None,
        },
        "next_empirical_candidate": {
            "id": vesicle_design.get("id", "VES-PACC-INT-01"),
            "status": vesicle_design.get("status", "missing"),
            "scientific_fields_complete": vesicle_design.get("preregistration_gate", {}).get("scientific_fields_complete", False),
            "public_preregistration_present": vesicle_preregistered,
            "preregistration_gate_open": vesicle_preregistered,
            "registration_status": vesicle_registration.get("status", "missing"),
            "registration_public_url": vesicle_registration.get("public_url"),
            "source": vesicle_design_path.relative_to(ROOT).as_posix() if vesicle_design_path.exists() else None,
        },
        "rule": "un proxy observationnel ou un résultat de modèle ne ferme pas la condition empirique",
    }


def antibiotic_specification_audit() -> dict:
    donofrio = load("03_branche_vivant/benchmark_histoire_antibiotique_2026/resultats/RESULTAT.json")
    legacy = load("plan_directeur/campagne_maximale_trois_branches/resultats/vivant_robustesse.json")["antibiotic_history_robustness"]
    return {
        "schema": "oric.antibiotic-specification-separation.v1",
        "same_dataset": False,
        "donofrio": {
            "source_file": donofrio.get("source_file"),
            "rows": donofrio.get("rows"),
            "groups": donofrio.get("group_count"),
            "rmse_state_only": donofrio.get("rmse_state_only"),
            "rmse_state_plus_history": donofrio.get("rmse_state_plus_history"),
            "permutation_p": donofrio.get("permutation_p_history_better_than_shuffled"),
            "verdict": donofrio.get("verdict"),
            "qualification": "external_retrospective_positive_not_prospective_not_independently_replicated",
        },
        "legacy_amikacin_longitudinal": {
            "prediction_rows": legacy.get("prediction_rows"),
            "paired_history_vs_equal_complexity_p": legacy["primary_paired_comparison"]["exact_two_sided_sign_flip_p"],
            "slope_ablation_p": legacy["slope_ablation"]["exact_two_sided_sign_flip_p"],
            "ordered_history_null_p": legacy["ordered_history_null"]["one_sided_fraction_null_at_least_observed"],
            "qualification": "exploratory_nonconclusive_specification_sensitive",
        },
        "rule": "les tests de robustesse du benchmark longitudinal amikacine ne sont jamais attribués au jeu D'Onofrio",
    }


def replication_audit() -> dict:
    living = load("03_branche_vivant/lignees_vesicules/RECHERCHE_REPLICATION_INDEPENDANTE_2026-08-12.json")
    santos_path = ROOT / "03_branche_vivant/benchmark_externe_santos_lopez_2021/resultats/RESULTAT.json"
    santos = json.loads(santos_path.read_text(encoding="utf-8")) if santos_path.exists() else {}
    return {
        "schema": "oric.section-xiv.replication-audit.v1",
        "strict_reproduced_results": [],
        "strict_reproduced_result_count": 0,
        "required": 2,
        "card2019": living.get("existing_independent_test"),
        "santos_lopez_2021": {
            "status": santos.get("status", "not_executed"),
            "reference_numeric_rule_support": santos.get("reference_numeric_rule_support"),
            "strict_prediction_success": santos.get("strict_prediction_success", False),
            "counts_for_condition_10": santos.get("counts_for_section_XIV_condition_10", False),
            "source": santos_path.relative_to(ROOT).as_posix() if santos_path.exists() else None,
        },
        "search_status": living.get("overall_verdict"),
        "condition_10_satisfied": False,
        "rule": "une réplication négative de famille, une réplication conceptuelle ou un benchmark ouvert sans préenregistrement complet ne compte pas comme reproduction stricte d'un résultat positif",
    }


def cross_branch_audit(pacc: dict) -> dict:
    # Les définitions actuelles sont différentes. La nouvelle définition commune
    # est disponible pour les prochains tests, mais aucun résultat ne l'instancie
    # encore dans deux branches.
    definitions: dict[str, set[str]] = {}
    for row in pacc["candidates"]:
        if row["causal_Pacc_qualified"]:
            definitions.setdefault(row["definition_class"], set()).add(row["branch"])
    common = {key: sorted(value) for key, value in definitions.items() if len(value) >= 2}
    return {
        "schema": "oric.section-xiv.cross-branch-audit.v1",
        "common_qualified_definitions": common,
        "condition_11_satisfied": bool(common),
        "future_common_definition": "PACC-INT-CHALLENGE-V1",
        "rule": "même définition et même règle de décision; aucune redéfinition après résultat",
    }


def build() -> tuple[dict, dict]:
    prediction = prediction_audit()
    pacc = pacc_strict_audit()
    replication = replication_audit()
    cross = cross_branch_audit(pacc)
    antibiotics = antibiotic_specification_audit()

    count_registry = registry_count()
    count_transitions = matter_transition_count()
    condition3 = prediction["all_branches_have_success"]
    condition4 = bool(condition3 and all(
        row["matched_control_declared"] for row in prediction["predictions"] if row["strict_success"]
    ))

    conditions = [
        {"id": 1, "label": "identifiant et statut pour chaque affirmation majeure", "passed": count_registry >= 35, "evidence": {"registered_hypotheses": count_registry}},
        {"id": 2, "label": "base de données de la branche matière", "passed": count_transitions == 40, "evidence": {"transition_rows": count_transitions, "scope": "schéma construit, complétude distincte"}},
        {"id": 3, "label": "une prédiction propre réussissant hors échantillon par branche", "passed": condition3, "evidence": {"strict_success_count": prediction["strict_success_count"], "successful_branches": prediction["successful_branches"]}},
        {"id": 4, "label": "chaque réussite bat un témoin apparié", "passed": condition4, "status": "not_applicable_no_successful_prediction" if not condition3 else "evaluated", "evidence": {"strict_success_count": prediction["strict_success_count"]}},
        {"id": 5, "label": "chaque mécanisme soutenu par une ablation", "passed": True, "status": "pass_documented_in_section_XIV", "evidence": ["CHM", "MEM", "interventions astronomiques"]},
        {"id": 6, "label": "dépendance au chemin à conditions finales vérifiées", "passed": True, "status": "pass_documented_in_section_XIV"},
        {"id": 7, "label": "persistance au-delà des constantes de temps", "passed": True, "status": "pass_documented_in_section_XIV"},
        {"id": 8, "label": "D, H, L publiés séparément", "passed": True, "status": "pass_documented_in_section_XIV", "evidence": "banc synthétique"},
        {"id": 9, "label": "Pacc mesuré causalement dans un système réel par branche", "passed": pacc["condition_9_satisfied"], "evidence": {"qualified_branch_count": pacc["qualified_branch_count"], "qualified_by_branch": pacc["qualified_by_branch"]}},
        {"id": 10, "label": "deux résultats reproduits par des équipes indépendantes", "passed": replication["condition_10_satisfied"], "evidence": {"strict_reproduced_result_count": replication["strict_reproduced_result_count"]}},
        {"id": 11, "label": "un résultat traverse deux branches sans redéfinition", "passed": cross["condition_11_satisfied"], "evidence": cross["common_qualified_definitions"]},
        {"id": 12, "label": "résultats négatifs visibles et versionnés", "passed": (HERE / "FALSIFICATION_ORI-C.md").exists() and (HERE / "RESULTATS_NEGATIFS.md").exists(), "evidence": ["FALSIFICATION_ORI-C.md", "RESULTATS_NEGATIFS.md"]},
    ]
    passed_ids = [item["id"] for item in conditions if item["passed"]]
    missing_ids = [item["id"] for item in conditions if not item["passed"]]
    audit = {
        "schema": "oric.section-xiv-audit.v1",
        "conditions_total": 12,
        "passed_count": len(passed_ids),
        "passed_ids": passed_ids,
        "missing_ids": missing_ids,
        "conditions": conditions,
        "first_threshold_satisfied": False,
        "strong_threshold_satisfied": False,
        "current_reading": (
            "le verrou n'est plus l'existence d'une méthode; les conditions ouvertes exigent "
            "prédiction hors échantillon, Pacc causal empirique, réplication indépendante et "
            "transfert sans redéfinition"
        ),
        "critical_targets": [
            "3+4: obtenir une prédiction propre hors échantillon qui bat un témoin apparié",
            "9: mesurer PACC-INT-CHALLENGE-V1 dans un système réel de chaque branche",
            "10: obtenir deux reproductions strictes par équipes indépendantes",
            "11: instancier une même définition qualifiée dans au moins deux branches",
        ],
    }
    diagnostics = {
        "prediction": prediction,
        "pacc": pacc,
        "replication": replication,
        "cross_branch": cross,
        "antibiotics": antibiotics,
    }
    return audit, diagnostics


def main() -> int:
    audit, diagnostics = build()
    out = HERE / "resultats"
    out.mkdir(exist_ok=True)
    (out / "SEUIL_XIV.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "PACC_QUALIFICATION_STRICTE.json").write_text(json.dumps(diagnostics["pacc"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "PREDICTIONS_HORS_ECHANTILLON_AUDIT.json").write_text(json.dumps(diagnostics["prediction"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "REPLICATIONS_INDEPENDANTES_AUDIT.json").write_text(json.dumps(diagnostics["replication"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "TRANSFERT_SANS_REDEFINITION_AUDIT.json").write_text(json.dumps(diagnostics["cross_branch"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "ANTIBIOTIQUES_SPECIFICATIONS_AUDIT.json").write_text(json.dumps(diagnostics["antibiotics"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"§XIV: {audit['passed_count']}/12; verrous={audit['missing_ids']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
