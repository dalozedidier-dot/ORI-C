from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DERIVE = ROOT / "derive"
sys.path.insert(0, str(ROOT))

from statistiques_rangs import permuter_dans_strates, spearman


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
    campaign = load("derive/SYNTHESE_CAMPAGNE.json")

    assert campaign["transversalite"]["familles_au_schema_complet"] == 0
    assert campaign["transversalite"]["verdict"] == "ne_soutient_pas"


def test_spearman_attribue_des_rangs_moyens_aux_ex_aequo() -> None:
    x = [1, 1, 2, 3]
    y = [1, 2, 3, 4]
    # Valeur de référence obtenue avec scipy.stats.spearmanr.
    assert np.isclose(spearman(x, y), 0.9486832980505139)


def test_permutation_ne_traverse_jamais_les_strates() -> None:
    valeurs = np.array([1, 2, 10, 20], dtype=float)
    strates = ["A", "A", "B", "B"]
    permutees = permuter_dans_strates(
        valeurs, strates, np.random.default_rng(20260809)
    )
    assert set(permutees[:2]) == {1, 2}
    assert set(permutees[2:]) == {10, 20}


def test_matrice_documente_les_permutations_stratifiees() -> None:
    matrix = load("derive/MATRICE_TRANSVERSALE.json")
    for family in matrix["familles"].values():
        for relation in family.values():
            if isinstance(relation, dict) and relation.get("rho") is not None:
                if relation.get("p") is not None:
                    assert relation["permutation"] == "dans_les_strates"


def test_valeurs_avec_ex_aequo_sont_regenerees() -> None:
    matrix = load("derive/MATRICE_TRANSVERSALE.json")["familles"]
    assert np.isclose(
        matrix["verre_relaxation"]["histoire_vers_reponse"]["rho"], -0.4696209717
    )
    assert np.isclose(
        matrix["transition_de_phase"]["histoire_vers_trace"]["rho"], -0.0071314958
    )
    assert np.isclose(
        matrix["reconstruction_de_surface"]["histoire_vers_reponse"]["rho"],
        -0.4961389384,
    )
    assert np.isclose(
        matrix["aciers_a_outils"]["histoire_vers_trace"]["rho"], -0.8366600265
    )


def test_iodp_ne_revandique_pas_c03_complet() -> None:
    result = load("derive/RESULTAT_C_MAT_MEM_03.json")
    matrix = load("derive/MATRICE_TRANSVERSALE.json")
    assert result["verdict"] == "soutient"
    assert result["verdict_C03_complet"] == "non_testable_avec_ce_jeu"
    assert matrix["comptes"]["C_MAT_MEM_03_complet"] == 0
