from __future__ import annotations

import importlib.util
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "valider_noyau_probant.py"
SPEC = importlib.util.spec_from_file_location("valider_noyau_probant", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def charger():
    _, catalogue = MODULE.lire_csv(MODULE.CATALOGUE)
    champs, politique = MODULE.lire_csv(MODULE.POLITIQUE)
    return catalogue, champs, politique


def test_politique_canonique_est_bijective_et_fail_closed():
    catalogue, champs, politique = charger()
    resume = MODULE.valider(catalogue, politique, champs)
    assert resume["catalogue_total"] == 683
    assert resume["noyau_probant"] == 366
    assert resume["qa_exploratoire"] == 317
    assert resume["confirmatoires_total"] == 27
    assert resume["confirmatoires_conserves"] == 27


def test_un_id_duplique_est_refuse():
    catalogue, champs, politique = charger()
    corrompue = deepcopy(politique)
    corrompue[-1]["test_id"] = corrompue[0]["test_id"]
    with pytest.raises(ValueError, match="dupliqués"):
        MODULE.valider(catalogue, corrompue, champs)


def test_une_decision_inconnue_est_refusee():
    catalogue, champs, politique = charger()
    corrompue = deepcopy(politique)
    corrompue[0]["decision"] = "PEUT_ETRE"
    with pytest.raises(ValueError, match="décision inconnue"):
        MODULE.valider(catalogue, corrompue, champs)


def test_un_confirmatoire_ne_peut_pas_sortir_du_noyau():
    catalogue, champs, politique = charger()
    corrompue = deepcopy(politique)
    par_id = {r["test_id"]: r for r in corrompue}
    confirmatoire = next(
        r["test_id"] for r in catalogue if r["confirmatory"].strip().lower() == "true"
    )
    non_confirmatoire_vire = next(
        r["test_id"] for r in catalogue
        if r["confirmatory"].strip().lower() != "true" and par_id[r["test_id"]]["decision"] == "VIRER"
    )
    par_id[confirmatoire].update(
        decision="VIRER", destination="qa_exploratoire", rang_action="", motif_code="REDONDANCE_SOUS_ANALYSE"
    )
    par_id[non_confirmatoire_vire].update(
        decision="GARDER", destination="noyau_probant", rang_action="3", motif_code="SOUS_TEST_NECESSAIRE"
    )
    with pytest.raises(ValueError, match="confirmatoires exclus"):
        MODULE.valider(catalogue, corrompue, champs)
