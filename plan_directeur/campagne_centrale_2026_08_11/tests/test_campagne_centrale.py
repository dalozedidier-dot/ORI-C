from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("central", HERE / "run_all.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_paleo_refuse_une_execution_partielle() -> None:
    result = MODULE.admission_paleo()
    assert result["verdict"] == "non_testable"
    assert result["required_count"] == 9
    assert result["present_count"] == 9
    assert result["missing"] == []
    assert result["normalized_dataset_count"] == 9
    assert any("chronologique" in issue for issue in result["schema_issues"])
    assert any("contrôle négatif" in issue for issue in result["schema_issues"])


def test_les_30_axes_ont_un_statut() -> None:
    plan = json.loads((HERE / "PLAN_CENTRAL.json").read_text(encoding="utf-8"))
    assert [axis["id"] for axis in plan["axes"]] == list(range(1, 31))
    assert all(axis.get("statut") for axis in plan["axes"])


def test_la_matrice_ne_presente_pas_un_deblocage_comme_un_resultat() -> None:
    matrix = MODULE.dataset_matrix()
    assert matrix["rows"]
    assert all("borne supérieure" in row["warning"] for row in matrix["rows"])
    scores = [row["score_levier"] for row in matrix["rows"]]
    assert scores == sorted(scores, reverse=True)


def test_benchmark_transversal_distingue_completude_et_validation() -> None:
    benchmark, invariants = MODULE.benchmark_transversal()
    assert 20 <= benchmark["case_count"] <= 30
    assert all(case["artifact_present"] for case in benchmark["cases"])
    assert invariants["cases_complete_X_H_m_Theta_tau_Pacc_R"] == 5
    assert invariants["eligible_case_ids"] == ["C-VES-02", "C-VES-03", "C-AST-01", "PID-ANT-01", "GCQ-T09"]
    assert benchmark["field_complete_unique_system_count"] == 4
    assert invariants["tests"][0]["status"] == "exploratory_comparison_ready_not_confirmatory"
    assert invariants["tests"][1]["status"] == "non_testable"
    assert invariants["verdict"].startswith("la complétude opérationnelle progresse")
    # La présence des sept champs ne doit jamais être assimilée à une preuve causale commune.
    pid = next(case for case in benchmark["cases"] if case["id"] == "PID-ANT-01")
    assert pid["measurement_quality"]["m"] == "historical_state_label_not_isolated_physical_trace"


def test_aucune_prediction_retrospective_n_est_fabriquee() -> None:
    directory = HERE / "PREDICTIONS_PROSPECTIVES"
    predictions = [json.loads(p.read_text(encoding="utf-8")) for p in directory.glob("PRED-*.json")]
    assert predictions
    assert all(p["resultat"] is None and p["date_ouverture"] is None for p in predictions)
    assert all(p["statut"] == "frozen_locally_awaiting_external_data" for p in predictions)
    for prediction in predictions:
        declared = prediction.pop("empreinte_avant_ouverture")
        canonical = json.dumps(prediction, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        assert declared == "sha256:" + hashlib.sha256(canonical).hexdigest()


def test_quantification_commune_ne_fabrique_pas_un_invariant() -> None:
    measures, bifurcations = MODULE.quantification_commune()
    assert len(measures["measures"]) >= 4
    assert measures["comparability_status"] == "multiple_local_measurements_available_but_no_common_cross_domain_scale"
    assert len(bifurcations["entries"]) >= 3
    assert bifurcations["unmeasured_fields"]


def test_les_nouvelles_sources_paleo_sont_scellees() -> None:
    source_dir = MODULE.ROOT / "donnees_externes/paleo_history_01"
    manifest = json.loads((source_dir / "SOURCES.json").read_text(encoding="utf-8"))
    for source in manifest["sources"]:
        actual = hashlib.sha256((source_dir / source["file"]).read_bytes()).hexdigest()
        assert actual == source["sha256"]


def test_inv_a_separe_les_leviers_et_compte_les_systemes() -> None:
    contrasts, audit = MODULE.invariant_transversal()
    entries = {entry["claim_id"]: entry for entry in contrasts["entries"]}
    assert contrasts["cross_domain_magnitude_comparison_allowed"] is False
    assert entries["C-VES-03"]["control_class"] == "m_ablation"
    assert entries["C-VES-03"]["direct_INV_A_m_ablation"] is True
    assert entries["C-VES-03"]["direct_INV_A_support"] is False
    assert entries["PID-ANT-01"]["control_class"] == "history_permutation"
    assert entries["PID-ANT-01"]["direct_INV_A_m_ablation"] is False
    assert entries["C-AST-01"]["control_class"] == "architecture_intervention"
    assert entries["C-AST-01"]["direct_INV_A_m_ablation"] is False
    assert audit["replication_unit"] == "independent_system_not_claim"
    assert audit["field_complete_unique_system_count"] == 4
    assert audit["direct_m_ablation_system_count"] == 1
    assert audit["direct_positive_m_ablation_system_count"] == 0
    assert audit["future_gate_satisfied"] is False
    assert audit["current_status"] == "candidate_operationalized_exploratory_not_validated"


def test_tau_m_ne_se_confond_pas_avec_un_horizon() -> None:
    benchmark, _ = MODULE.benchmark_transversal()
    cases = {case["id"]: case for case in benchmark["cases"]}
    assert cases["C-AST-01"]["tau_quality"]["kind"] == "observation_horizon"
    assert cases["C-AST-01"]["tau_quality"]["tau_m_measured"] is False
    assert cases["PID-ANT-01"]["tau_quality"]["tau_m_measured"] is False
    assert cases["GCQ-T09"]["tau_quality"]["kind"] == "tau_decay_local"
    assert cases["GCQ-T09"]["tau_quality"]["cross_domain_comparable"] is False


def test_formalisme_inv_a_refuse_l_homogeneisation_forcee() -> None:
    formalism = json.loads((HERE / "FORMALISME_QUANTITATIF.json").read_text(encoding="utf-8"))
    spec = json.loads((HERE / "INVARIANT_TRANSVERSAL_INV_A.json").read_text(encoding="utf-8"))
    assert formalism["schema"] == "oric.quantitative-history.v2"
    assert formalism["intervention_classes"]["history_permutation"].startswith("contrôle informationnel")
    assert spec["status"] == "candidate_operationalized_not_validated"
    assert spec["local_contrast"]["cross_domain_magnitude_comparison_allowed"] is False
    assert spec["future_transversal_gate"]["independent_systems_min"] == 3
    assert spec["future_transversal_gate"]["branches_required"] == 3
    assert spec["future_transversal_gate"]["current_results_cannot_be_retroactively_preregistered"] is True
