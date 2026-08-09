from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVE = ROOT / "derive"


def load(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def test_iodp_ne_revandique_plus_c01_c02_c04() -> None:
    result = load("derive/RESULTATS_C_MAT_MEM_01_02_04.json")

    for criterion in ("C-MAT-MEM-01", "C-MAT-MEM-02", "C-MAT-MEM-04"):
        assert result["criteres"][criterion]["verdict"] == "non_testable_avec_ce_jeu"
        assert "resultat_partiel" in result["criteres"][criterion]

    assert result["criteres"]["C-MAT-MEM-02"]["rattachement_correct"].startswith(
        "diagnostic d'ablation"
    )


def test_matrice_separe_preuve_partielle_et_admission_complete() -> None:
    matrix = load("derive/MATRICE_TRANSVERSALE.json")

    assert matrix["comptes"]["schema_complet_histoire_trace_reponse"] == 0
    assert matrix["comptes"]["persistance"] == 0
    assert all(
        family["admission_chaine_complete"] is False
        for family in matrix["familles"].values()
    )
    assert matrix["controles_negatifs"]["physiques"]
    assert matrix["controles_negatifs"]["statistiques"]


def test_combinaison_oriente_chaque_effet_selon_la_physique() -> None:
    combined = load("derive/RESULTAT_TEST_COMBINE.json")

    assert "effets orientés" in combined["principe"]
    for relation in combined["relations"].values():
        for game in relation["jeux_detail"]:
            assert game["signe_attendu"] in (-1, 1)
            assert game["justification_signe"]
            assert game["effet_oriente"] == round(
                game["rho"] * game["signe_attendu"], 4
            )


def test_c05_reste_negatif() -> None:
    campaign = load("derive/execution/CAMPAGNE.json")

    assert campaign["transversalite"]["familles_au_schema_complet"] == 0
    assert campaign["transversalite"]["verdict"] == "ne_soutient_pas"

