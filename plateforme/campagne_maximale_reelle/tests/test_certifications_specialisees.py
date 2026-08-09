from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "certifications", ROOT / "certifier_resultats_specialises.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def configuration() -> dict:
    return json.loads((ROOT / "CERTIFICATIONS_SPECIALISEES.json").read_text(
        encoding="utf-8"
    ))


def test_les_resultats_specialises_sont_certifies_par_criterion_id() -> None:
    rapport = MODULE.certifier(configuration())
    verdicts = {r["criterion_id"]: r["verdict"] for r in rapport["resultats"]}
    assert verdicts == {
        "C-ANT-01": "supports",
        "C-VES-02": "supports",
        "C-VES-03": "supports",
        "C-MAT-MEM-05": "does_not_support",
        "C-AST-01": "supports",
    }
    assert rapport["comptes"] == {"does_not_support": 1, "supports": 4}
    niveaux = {r["criterion_id"]: r["niveau_preuve"] for r in rapport["resultats"]}
    assert niveaux["C-ANT-01"] == "E2"
    assert niveaux["C-VES-03"] == "E4"


def test_astronomie_reste_explicitement_un_resultat_de_modele() -> None:
    rapport = MODULE.certifier(configuration())
    astronomie = next(
        r for r in rapport["resultats"] if r["criterion_id"] == "C-AST-01"
    )
    assert astronomie["portee"] == "modele_physique_reduit_valide"
    assert astronomie["mesures"]["criteres_passes"] == 13


def test_matiere_conserve_le_verdict_negatif_et_la_limite_de_provenance() -> None:
    rapport = MODULE.certifier(configuration())
    matiere = next(
        r for r in rapport["resultats"] if r["criterion_id"] == "C-MAT-MEM-05"
    )
    assert matiere["verdict"] == "does_not_support"
    assert matiere["mesures"]["familles_completes"] == 0
    assert matiere["limite_provenance"]


def test_une_empreinte_divergente_est_refusee() -> None:
    config = configuration()
    config["certifications"][0]["artefact_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="empreinte artefact divergente"):
        MODULE.certifier(config)
