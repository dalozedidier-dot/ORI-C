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


def test_benchmark_transversal_sans_remplissage_des_champs_absents() -> None:
    benchmark, invariants = MODULE.benchmark_transversal()
    assert 20 <= benchmark["case_count"] <= 30
    assert all(case["artifact_present"] for case in benchmark["cases"])
    assert invariants["cases_complete_X_H_m_Theta_tau_Pacc_R"] == 0
    assert all(test["status"] == "non_testable" for test in invariants["tests"])


def test_aucune_prediction_retrospective_n_est_fabriquee() -> None:
    directory = HERE / "PREDICTIONS_PROSPECTIVES"
    assert {p.name for p in directory.iterdir()} == {"README.md", "SCHEMA_PREDICTION.json"}


def test_les_nouvelles_sources_paleo_sont_scellees() -> None:
    source_dir = MODULE.ROOT / "donnees_externes/paleo_history_01"
    manifest = json.loads((source_dir / "SOURCES.json").read_text(encoding="utf-8"))
    for source in manifest["sources"]:
        actual = hashlib.sha256((source_dir / source["file"]).read_bytes()).hexdigest()
        assert actual == source["sha256"]
