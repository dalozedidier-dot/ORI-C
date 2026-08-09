from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "priorites", ROOT / "prioriser_donnees_manquantes.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def rapport() -> dict:
    source = json.loads(
        (ROOT / "resultats_integration_maximale/results.json").read_text(
            encoding="utf-8"
        )
    )
    return MODULE.construire(source)


def test_compteurs_de_campagne_ne_sont_pas_un_score_scientifique() -> None:
    r = rapport()
    assert r["campagne"] == {
        "tests_catalogues": 683,
        "bloques": 626,
        "non_executes_automatiquement": 48,
        "executes_techniquement": 9,
        "echecs_techniques": 0,
        "erreurs_informatiques": 0,
    }
    assert "pas tableau de score scientifique" in r["lecture"]


def test_occurrences_et_tests_distincts_sont_separes() -> None:
    causes = rapport()["causes"]
    assert causes["test_hors_portee_mesuree"]["occurrences"] == 343
    assert causes["test_hors_portee_mesuree"]["tests_distincts"] == 320
    assert causes["non_admissible_comme_preuve_empirique"]["occurrences"] == 300
    assert causes["non_admissible_comme_preuve_empirique"]["tests_distincts"] == 255
    assert causes["aucun_jeu_empirique_declare"]["occurrences"] == 63


def test_classement_dedoublonne_les_tests_par_dataset() -> None:
    priorites = rapport()["priorites"]
    premiers = {
        bloc["dataset_cible"]: bloc["tests_distincts_potentiellement_debloquables"]
        for bloc in priorites[:7]
    }
    assert premiers == {
        "paleoclimate_timeseries": 89,
        "prebiotic_lineages": 85,
        "aucun_dataset_declare": 63,
        "benchmark_cases": 48,
        "orbital_initial_conditions": 47,
        "antibiotic_measurements": 41,
        "antibiotic_cycles": 34,
    }
    assert all(
        len(bloc["test_ids"]) == len(set(bloc["test_ids"])) for bloc in priorites
    )
