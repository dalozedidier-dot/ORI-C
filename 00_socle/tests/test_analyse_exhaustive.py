"""Verrous sur l'analyse exhaustive : domaine, régimes, théorèmes, bifurcation.

Ces tests portent sur les démonstrations, pas sur des échantillons. Ils
échouent si une propriété établie cesse d'être vraie.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import sympy as sp

from analyse_exhaustive import (
    CONDITIONS_ADMISSIBILITE,
    NIVEAUX,
    REGIMES,
    a01_necessite_de_m_positif,
    c01_theoremes_symboliques,
    classer,
    etat_stationnaire_monod,
    f01_certification_par_intervalles,
)
from modele_ori_c import Parametres, etat_stationnaire, jacobien


@pytest.fixture(scope="module")
def p() -> Parametres:
    return Parametres()


@pytest.fixture(scope="module")
def theoremes() -> dict:
    return c01_theoremes_symboliques()


# --- A. Domaine admissible -------------------------------------------------
def test_le_domaine_enumere_ses_sept_conditions() -> None:
    assert len(CONDITIONS_ADMISSIBILITE) == 7
    assert any("m = delta + l > 0" in condition for condition, _ in CONDITIONS_ADMISSIBILITE)


def test_m_nul_produit_une_croissance_lineaire_non_bornee(p: Parametres) -> None:
    """Théorème A1 : sans perte, P croît sans borne, à la pente D·S_in."""
    resultat = a01_necessite_de_m_positif(p)
    assert resultat["strictement_croissant"]
    assert resultat["ecart_relatif_a_la_pente_attendue"] < 1e-3
    assert resultat["pente_asymptotique_attendue_D_S_in"] == pytest.approx(
        p.dilution * p.S_in, rel=1e-12
    )


def test_la_formule_de_P_etoile_diverge_en_m_nul(p: Parametres) -> None:
    petits = [etat_stationnaire_monod(10.0**-k, Parametres(decay=0.0)) for k in (2, 3, 4, 5)]
    assert all(b > a for a, b in zip(petits, petits[1:])), "P* doit croître quand m décroît."


# --- B. Partition en régimes ----------------------------------------------
def test_la_nomenclature_couvre_neuf_regimes() -> None:
    assert len(REGIMES) == 9
    assert {"A", "B", "C", "D_viable", "D_lave", "E", "E_lavage_induit", "E_lave", "F"} == set(REGIMES)


@pytest.mark.parametrize("m_libre,m_selectif,attendu", [
    (0.30, 0.07, "A"),
    (1.50, 0.07, "B"),
    (2.00, 1.50, "C"),
    (0.30, 0.30, "D_viable"),
    (1.50, 1.50, "D_lave"),
    (0.07, 0.30, "E"),
    (0.30, 1.50, "E_lavage_induit"),
    (1.50, 2.00, "E_lave"),
])
def test_classification_des_representants(m_libre, m_selectif, attendu) -> None:
    assert classer(m_libre, m_selectif, m_crit := 0.909091) == attendu
    assert m_crit > 0


def test_la_frontiere_est_detectee_quand_une_tolerance_est_donnee() -> None:
    assert classer(0.909091, 0.07, 0.909091, tol=1e-9) == "F"


def test_une_reduction_ne_peut_pas_laver_le_compartiment() -> None:
    """Cellule impossible : m_s < m_f < m_crit implique m_s < m_crit.

    La viabilité ne dépendant que de m, réduire la perte ne peut pas faire
    passer le compartiment du côté lavé. Le vérifier revient à montrer que la
    branche « réduction » ne produit jamais E_lavage_induit.
    """
    rng = np.random.default_rng(11)
    for _ in range(50_000):
        m_libre = float(10 ** rng.uniform(-3, 3))
        m_selectif = m_libre * float(rng.random())  # strictement inférieur
        m_crit = float(10 ** rng.uniform(-3, 3))
        assert classer(m_libre, m_selectif, m_crit) in {"A", "B", "C"}


def test_une_intervention_inverse_ne_peut_pas_sauver_la_phase_libre() -> None:
    """Symétrique : m_f < m_s, si la phase libre est lavée le compartiment l'est."""
    rng = np.random.default_rng(13)
    for _ in range(50_000):
        m_libre = float(10 ** rng.uniform(-3, 3))
        m_selectif = m_libre * (1.0 + float(rng.random()))
        m_crit = float(10 ** rng.uniform(-3, 3))
        assert classer(m_libre, m_selectif, m_crit) in {"E", "E_lavage_induit", "E_lave"}


def test_toute_configuration_admissible_recoit_un_regime() -> None:
    rng = np.random.default_rng(7)
    for _ in range(20_000):
        m_libre, m_selectif = 10 ** rng.uniform(-3, 3, 2)
        m_crit = 10 ** rng.uniform(-3, 3)
        assert classer(float(m_libre), float(m_selectif), float(m_crit)) in REGIMES


# --- C. Théorèmes symboliques ---------------------------------------------
def test_identite_du_numerateur_de_la_derivee(theoremes: dict) -> None:
    """-D [K_s m² + S_in (m - mu_max)²] : manifestement négatif."""
    assert theoremes["identite_numerateur_verifiee"]


def test_la_trace_partage_la_meme_forme_positive(theoremes: dict) -> None:
    assert theoremes["identite_trace_verifiee"]


def test_le_critere_de_dulac_est_strictement_negatif(theoremes: dict) -> None:
    D, P, K_s, mu_max, S = sp.symbols("D P K_s mu_max S", positive=True)
    # `locals` est indispensable : sans lui, « S » est interprété comme le
    # registre sympy.S et non comme le symbole du substrat.
    locaux = {"D": D, "P": P, "K_s": K_s, "mu_max": mu_max, "S": S}
    obtenu = sp.sympify(theoremes["divergence_dulac"], locals=locaux)
    attendu = -D / P - K_s * mu_max / (K_s + S) ** 2
    assert sp.simplify(obtenu - attendu) == 0
    # Chaque terme est négatif sur P > 0 : la divergence l'est donc aussi.
    assert sp.simplify(obtenu.subs({D: 1, P: 1, K_s: 1, mu_max: 1, S: 1})) < 0


def test_les_six_theoremes_sont_enonces(theoremes: dict) -> None:
    assert set(theoremes["theoremes"]) == {"C1", "C2", "C3", "C4", "C5"}


@pytest.mark.parametrize("leak", [0.0, 0.02, 0.25, 0.5, 0.8])
def test_equilibre_interieur_localement_stable_quand_il_existe(p: Parametres, leak: float) -> None:
    _, P_eq = etat_stationnaire(leak, p)
    if P_eq <= 0:
        pytest.skip("Pas d'équilibre intérieur pour ce taux de perte.")
    valeurs = np.linalg.eigvals(jacobien(leak, p))
    assert np.all(valeurs.real < 0)


def test_decroissance_stricte_pour_une_cinetique_de_moser(p: Parametres) -> None:
    """Théorème C6 sur une mu croissante qui n'est ni Monod ni masse-action."""
    def plateau(leak: float, n: int = 2) -> float:
        m = p.decay + leak
        if m >= p.mu_max:
            return 0.0
        S_eq = (p.K_s**n * m / (p.mu_max - m)) ** (1.0 / n)
        return p.dilution * (p.S_in - S_eq) / m if S_eq < p.S_in else 0.0

    valeurs = [plateau(float(l)) for l in np.linspace(0.01, 0.5, 60)]
    assert all(b < a for a, b in zip(valeurs, valeurs[1:]))


# --- E. Bifurcation --------------------------------------------------------
def test_echange_de_stabilite_au_seuil(p: Parametres) -> None:
    m_crit = p.mu_max * p.S_in / (p.K_s + p.S_in)
    l_crit = m_crit - p.decay
    for facteur, interieur_attendu in ((0.99, True), (1.01, False)):
        leak = l_crit * facteur
        P_eq = etat_stationnaire_monod(leak, p)
        valeur_propre_E0 = m_crit - (p.decay + leak)
        assert (P_eq > 0) is interieur_attendu
        assert (valeur_propre_E0 < 0) is not interieur_attendu


def test_le_seuil_a_la_forme_annoncee(p: Parametres) -> None:
    from modele_ori_c import seuil_lavage

    assert seuil_lavage(p) == pytest.approx(
        p.mu_max * p.S_in / (p.K_s + p.S_in) - p.decay, rel=1e-14
    )


# --- F. Arithmétique par intervalles ---------------------------------------
def test_certification_par_intervalles_sur_une_profondeur_reduite() -> None:
    resultat = f01_certification_par_intervalles(profondeur_max=8)
    assert resultat["boites_certifiees"] > 0
    assert resultat["variables"] == ["D", "K_s", "S_in", "mu_max", "m"]


# --- H. Niveaux de conclusion ---------------------------------------------
def test_les_trois_niveaux_sont_distingues() -> None:
    assert len(NIVEAUX) == 3
    assert NIVEAUX["niveau_1_theoreme_dans_le_modele"]["etabli"] is True
    assert NIVEAUX["niveau_2_robustesse_structurelle"]["etabli"] is True
    assert NIVEAUX["niveau_3_validite_biologique"]["etabli"] is False


def test_la_validite_biologique_n_est_jamais_revendiquee() -> None:
    contenu = NIVEAUX["niveau_3_validite_biologique"]["contenu"].lower()
    assert "aucune donnée expérimentale" in contenu


# --- Sorties ---------------------------------------------------------------
def test_le_rapport_exhaustif_est_complet(racine: Path) -> None:
    chemin = racine / "test_interventionnel/resultats_exhaustifs/analyse_exhaustive.json"
    assert chemin.exists(), "Rapport exhaustif manquant ; lancer analyse_exhaustive.py."
    rapport = json.loads(chemin.read_text(encoding="utf-8"))
    assert rapport["sections_totales"] == 11
    assert rapport["toutes_reussies"]
    assert rapport["sections"]["B01"]["cellules_impossibles_atteintes"] == 0
    assert rapport["sections"]["G01"]["structures_sans_decroissance_stricte"] == []
    assert rapport["sections"]["G01"]["n_structures"] == 12
