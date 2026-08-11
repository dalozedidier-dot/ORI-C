from __future__ import annotations

import importlib.util
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "src/analyser_information_historique.py"
SPEC = importlib.util.spec_from_file_location("info_history", MODULE)
INFO = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(INFO)


def test_analyse_des_mesures_individuelles_sans_simulation() -> None:
    result = INFO.analyse()
    assert result["analysis"] == "retrospective"
    assert len(result["results"]) == 5
    assert any(row.get("n", 0) > 400 for row in result["results"])


def test_la_classification_est_hors_echantillon() -> None:
    labels = ["A", "A", "A", "B", "B", "B"]
    x = [[0.0], [0.1], [0.2], [10.0], [10.1], [10.2]]
    accuracy, decisions = INFO.loo_nearest_centroid(labels, x)
    assert accuracy == 1.0
    assert all(decisions)


def test_les_limites_interdisent_une_courbe_causale_fabriquee() -> None:
    result = INFO.analyse()
    assert any("aucune courbe" in limit for limit in result["limits"])
