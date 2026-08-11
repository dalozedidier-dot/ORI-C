from __future__ import annotations

import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("q26", HERE / "src/analyser_distribution_26al.py")
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


def result() -> dict:
    complete = json.loads((HERE / "resultats/RESULTATS_QUANTITATIFS_COMPLETS.json").read_text(encoding="utf-8"))
    return MOD.analyse(complete)


def test_distribution_analytique_sans_pseudo_probabilite_de_reservoir() -> None:
    value = result()
    assert len(value["events"]) == 4
    assert "not probabilities" in value["reservoir_history_model"]
    assert any("reste ouverte" in limit for limit in value["limits"])


def test_accessibilite_decroit_avec_l_histoire_temporelle() -> None:
    events = result()["events"]
    medians = [event["reservoir_scenarios"]["canonique_homogene"]["remaining_fraction_median"] for event in events]
    assert medians == sorted(medians, reverse=True)
    assert medians[0] > 0.25
    assert medians[-1] < 0.10
