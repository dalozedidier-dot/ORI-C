from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("seuil_xiv", HERE / "evaluer_seuil_xiv.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_seuil_xiv_reproduit_le_diagnostic_canonique() -> None:
    audit, _ = MODULE.build()
    assert audit["conditions_total"] == 12
    assert audit["passed_count"] == 7
    assert audit["passed_ids"] == [1, 2, 5, 6, 7, 8, 12]
    assert audit["missing_ids"] == [3, 4, 9, 10, 11]
    assert audit["first_threshold_satisfied"] is False


def test_aucune_validation_croisee_retrospective_ne_compte_comme_prediction_prospective() -> None:
    prediction = MODULE.prediction_audit()
    assert prediction["strict_success_count"] == 0
    assert prediction["all_branches_have_success"] is False
    assert all(row["result_present"] is False for row in prediction["predictions"])


def test_pacc_strict_refuse_proxy_et_modele_comme_preuve_empirique() -> None:
    pacc = MODULE.pacc_strict_audit()
    assert pacc["strict_definition_id_for_future_tests"] == "PACC-INT-CHALLENGE-V1"
    assert pacc["qualified_branch_count"] == 0
    assert pacc["condition_9_satisfied"] is False
    by_id = {row["id"]: row for row in pacc["candidates"]}
    assert by_id["PACC-VES-RETRO-01"]["empirical"] is True
    assert by_id["PACC-VES-RETRO-01"]["causal_Pacc_qualified"] is False
    assert by_id["PACC-EXO-DOM-01"]["empirical"] is False
    assert by_id["PACC-DONOFRIO-PID-01"]["m_intervention_present"] is False


def test_replication_externe_reste_une_condition_independante() -> None:
    audit = MODULE.replication_audit()
    assert audit["strict_reproduced_result_count"] == 0
    assert audit["condition_10_satisfied"] is False
    assert audit["card2019"]["verdict"] == "does_not_support"


def test_aucune_redefinition_ne_peut_fermer_la_condition_11() -> None:
    pacc = MODULE.pacc_strict_audit()
    cross = MODULE.cross_branch_audit(pacc)
    assert cross["condition_11_satisfied"] is False
    assert cross["common_qualified_definitions"] == {}


def test_les_deux_benchmarks_antibiotiques_ne_sont_pas_confondus() -> None:
    audit = MODULE.antibiotic_specification_audit()
    assert audit["same_dataset"] is False
    assert audit["donofrio"]["rows"] == 288
    assert audit["donofrio"]["permutation_p"] == 0.004975124378109
    assert audit["legacy_amikacin_longitudinal"]["prediction_rows"] == 358
    assert audit["legacy_amikacin_longitudinal"]["paired_history_vs_equal_complexity_p"] == 0.2265625
