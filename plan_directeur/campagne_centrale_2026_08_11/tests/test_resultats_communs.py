from __future__ import annotations

import importlib.util
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]


def load_module():
    path = HERE / "construire_resultats_communs.py"
    spec = importlib.util.spec_from_file_location("oric_common_results_test", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_common_results_are_complete_without_filling_missing_measurements():
    bundle = load_module().build()
    assert len(bundle["items"]) == 21
    assert bundle["counts"]["field_complete_cases"] == 6
    by_id = {item["id"]: item for item in bundle["items"]}
    assert by_id["C-MAT-MEM-05"]["P_acc"]["status"] == "missing"
    assert by_id["C-AST-01"]["result"]["field_complete"] is True
    assert by_id["C-AST-01"]["result"]["evidence_level"] == "E4_modele"
    assert {item["branch"] for item in bundle["items"]} == {"matiere", "systeme_solaire", "vivant"}
    matrix, proofs = load_module().derive_views(bundle)
    assert set(matrix["branches"]) == {"matiere", "systeme_solaire", "vivant"}
    assert len(proofs["items"]) == 21
    assert "PID-ANT-01" not in matrix["branches"]["vivant"]["direct_intervention_cases"]
