from __future__ import annotations

import importlib.util
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
    assert result["present_count"] == 4
    assert set(result["missing"]) == {
        "pile_benthique_independante", "proxy_niveau_marin_independant",
        "EPICA_poussieres", "insolation_convention_1", "insolation_convention_2",
    }


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


def test_aucune_prediction_retrospective_n_est_fabriquee() -> None:
    directory = HERE / "PREDICTIONS_PROSPECTIVES"
    assert {p.name for p in directory.iterdir()} == {"README.md", "SCHEMA_PREDICTION.json"}

