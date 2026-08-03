"""Invariants du modèle interventionnel, sans lecture du dossier publié.

Ces tests sont l'expression exécutable de la campagne de robustesse : ils
échouent si une modification du modèle casse une propriété démontrable.
"""
from __future__ import annotations

import numpy as np
import pytest

from modele_ori_c import (
    Parametres,
    croissance,
    etat_stationnaire,
    facteur_retention_analytique,
    jacobien,
    parametres_avec,
    perte_totale,
    relaxation,
    seuil_lavage,
    simuler,
)

FACTEUR_EXACT = 4.4439094848338945
GRAINE = 20260731


@pytest.fixture(scope="module")
def p() -> Parametres:
    return Parametres()


# --- Solution stationnaire -------------------------------------------------
def test_etat_stationnaire_annule_le_champ_de_vecteurs(p: Parametres) -> None:
    mu = croissance("monod", p)
    for leak in (p.leak_free, p.leak_membrane, 0.0, 0.5):
        S_eq, P_eq = etat_stationnaire(leak, p)
        dS = p.dilution * (p.S_in - S_eq) - float(mu(np.asarray(S_eq))) * P_eq
        dP = (float(mu(np.asarray(S_eq))) - perte_totale(leak, p)) * P_eq
        assert abs(dS) < 1e-12, f"dS/dt non nul à l'équilibre pour leak={leak}"
        assert abs(dP) < 1e-12, f"dP/dt non nul à l'équilibre pour leak={leak}"


@pytest.mark.parametrize("leak", [0.02, 0.25])
def test_integration_longue_rejoint_la_solution_close(p: Parametres, leak: float) -> None:
    S_eq, P_eq = etat_stationnaire(leak, p)
    _, S, P = simuler(leak, p, t_end=4000.0, n_points=40001, rtol=1e-12, atol=1e-14)
    assert abs(S[-1] - S_eq) / S_eq < 1e-9
    assert abs(P[-1] - P_eq) / P_eq < 1e-9


def test_facteur_de_retention_exact(p: Parametres) -> None:
    assert facteur_retention_analytique(p.leak_free, p.leak_membrane, p) == pytest.approx(
        FACTEUR_EXACT, rel=1e-12
    )


# --- Non-régression : la fenêtre de 80 unités était pré-asymptotique -------
FENETRE_HISTORIQUE = 80.0
FACTEUR_HISTORIQUE = 4.418075430275717


def test_une_fenetre_de_80_unites_serait_pre_asymptotique(p: Parametres) -> None:
    """Garde-fou : le défaut corrigé doit rester reproductible à la demande.

    Si ce test cessait d'échouer à reproduire le biais, c'est que le modèle
    aurait changé et que le diagnostic de la correction ne tiendrait plus.
    """
    from modele_ori_c import metriques_plateau

    _, _, P_libre = simuler(p.leak_free, p, t_end=FENETRE_HISTORIQUE)
    _, _, P_comp = simuler(p.leak_membrane, p, t_end=FENETRE_HISTORIQUE)
    mesure = metriques_plateau(P_comp)["mean"] / metriques_plateau(P_libre)["mean"]
    assert mesure == pytest.approx(FACTEUR_HISTORIQUE, rel=1e-6)
    biais = (mesure - FACTEUR_EXACT) / FACTEUR_EXACT
    assert biais < -1e-3, "Le biais pré-asymptotique attendu a disparu."


def test_l_horizon_corrige_atteint_l_etat_stationnaire(p: Parametres) -> None:
    """Avec t_end = 500, le plateau coïncide avec la solution exacte."""
    from modele_ori_c import metriques_plateau

    assert p.t_end == 500.0, "L'horizon corrigé du dossier est de 500 unités."
    _, _, P_libre = simuler(p.leak_free, p)
    _, _, P_comp = simuler(p.leak_membrane, p)
    mesure = metriques_plateau(P_comp)["mean"] / metriques_plateau(P_libre)["mean"]
    assert mesure == pytest.approx(FACTEUR_EXACT, rel=1e-9)


def test_l_ancien_critere_de_stabilite_etait_trop_permissif(p: Parametres) -> None:
    """cv < 1e-2 et dérive < 1e-2 étaient satisfaits hors de l'état stationnaire.

    C'est la raison pour laquelle le défaut avait passé la vérification : le
    critère mesurait la platitude locale, pas la convergence.
    """
    from modele_ori_c import metriques_plateau

    _, _, P_comp = simuler(p.leak_membrane, p, t_end=FENETRE_HISTORIQUE)
    metriques = metriques_plateau(P_comp)
    assert metriques["cv"] < 0.01
    assert metriques["relative_drift"] < 0.01
    cible = etat_stationnaire(p.leak_membrane, p)[1]
    assert abs(metriques["mean"] - cible) / cible > 1e-3


def test_le_nouveau_critere_rejette_la_fenetre_historique(p: Parametres) -> None:
    """Le critère corrigé, lui, doit refuser un plateau pré-asymptotique."""
    from modele_ori_c import metriques_plateau

    cible = etat_stationnaire(p.leak_membrane, p)[1]
    _, _, P_court = simuler(p.leak_membrane, p, t_end=FENETRE_HISTORIQUE)
    _, _, P_long = simuler(p.leak_membrane, p)
    assert abs(metriques_plateau(P_court)["mean"] - cible) / cible > 1e-6
    assert abs(metriques_plateau(P_long)["mean"] - cible) / cible < 1e-6


def test_horizon_recommande_par_la_stabilite_lineaire(p: Parametres) -> None:
    info = relaxation(p.leak_membrane, p)
    assert info["stable"]
    assert info["tau_lent"] == pytest.approx(14.37, rel=1e-2)
    assert info["t_requis_1e9"] > FENETRE_HISTORIQUE * 3
    assert p.t_end > info["t_requis_1e9"], "L'horizon retenu doit couvrir la relaxation."


# --- Stabilité linéaire ----------------------------------------------------
@pytest.mark.parametrize("leak", [0.0, 0.02, 0.1, 0.25, 0.5, 0.8])
def test_equilibre_interieur_localement_stable(p: Parametres, leak: float) -> None:
    assert leak < seuil_lavage(p)
    valeurs = np.linalg.eigvals(jacobien(leak, p))
    assert np.all(valeurs.real < 0), f"Équilibre instable pour leak={leak}"


# --- Invariance ------------------------------------------------------------
@pytest.mark.parametrize("methode", ["LSODA", "Radau", "BDF", "DOP853", "RK45"])
def test_invariance_au_solveur(p: Parametres, methode: str) -> None:
    _, _, P_libre = simuler(p.leak_free, p, t_end=1000.0, n_points=20001, methode=methode)
    _, _, P_comp = simuler(p.leak_membrane, p, t_end=1000.0, n_points=20001, methode=methode)
    assert float(P_comp[-1] / P_libre[-1]) == pytest.approx(FACTEUR_EXACT, rel=1e-5)


@pytest.mark.parametrize("n_points", [201, 2001, 20001])
def test_invariance_a_la_discretisation(p: Parametres, n_points: int) -> None:
    _, _, P_libre = simuler(p.leak_free, p, t_end=1000.0, n_points=n_points)
    _, _, P_comp = simuler(p.leak_membrane, p, t_end=1000.0, n_points=n_points)
    assert float(P_comp[-1] / P_libre[-1]) == pytest.approx(FACTEUR_EXACT, rel=1e-6)


@pytest.mark.parametrize("S0,P0", [(1e-4, 1e-6), (0.5, 0.1), (10.0, 1.0), (50.0, 100.0)])
def test_invariance_aux_conditions_initiales(p: Parametres, S0: float, P0: float) -> None:
    cible = etat_stationnaire(p.leak_membrane, p)[1]
    _, _, P = simuler(p.leak_membrane, p, t_end=3000.0, n_points=6001,
                      y0=(S0, P0), rtol=1e-11, atol=1e-13)
    assert abs(P[-1] - cible) / cible < 1e-6


# --- Conservation ----------------------------------------------------------
@pytest.mark.parametrize("leak", [0.02, 0.25])
def test_bilan_de_matiere(p: Parametres, leak: float) -> None:
    t, S, P = simuler(leak, p, t_end=1000.0, n_points=100001, rtol=1e-12, atol=1e-14)
    apport = np.trapezoid(p.dilution * (p.S_in - S), t)
    pertes = np.trapezoid(perte_totale(leak, p) * P, t)
    variation = (S[-1] + P[-1]) - (S[0] + P[0])
    assert abs(variation - (apport - pertes)) / max(abs(apport), 1e-12) < 1e-7
    assert np.all(S > 0) and np.all(P > 0)
    assert np.all(S <= p.S_in + 1e-9)


# --- Contrôles négatifs ----------------------------------------------------
def test_controle_negatif_intervention_nulle(p: Parametres) -> None:
    assert facteur_retention_analytique(p.leak_free, p.leak_free, p) == 1.0


def test_controle_de_signe_intervention_inverse(p: Parametres) -> None:
    leak_haut = min(p.leak_free * 2.0, seuil_lavage(p) * 0.9)
    assert facteur_retention_analytique(p.leak_free, leak_haut, p) < 1.0


@pytest.mark.parametrize("y0", [(1.0, 10.0), (1.0, 0.0001), (10.0, 0.1)])
def test_placebo_les_conditions_initiales_ne_deplacent_pas_le_plateau(
    p: Parametres, y0: tuple[float, float]
) -> None:
    cible = etat_stationnaire(p.leak_membrane, p)[1]
    _, _, P = simuler(p.leak_membrane, p, t_end=3000.0, n_points=6001,
                      y0=y0, rtol=1e-11, atol=1e-13)
    assert abs(P[-1] - cible) / cible < 1e-8


# --- Monotonie et domaine de validité --------------------------------------
def test_plateau_strictement_decroissant_en_perte(p: Parametres) -> None:
    fuites = np.linspace(0.0, seuil_lavage(p) * 0.999, 400)
    plateaux = np.array([etat_stationnaire(float(l), p)[1] for l in fuites])
    assert np.all(np.diff(plateaux) < 0)


def test_seuil_de_lavage_borne_le_domaine(p: Parametres) -> None:
    seuil = seuil_lavage(p)
    assert seuil == pytest.approx(p.mu_max * p.S_in / (p.K_s + p.S_in) - p.decay, rel=1e-12)
    assert etat_stationnaire(seuil * 0.99, p)[1] > 0.0
    assert etat_stationnaire(seuil * 1.01, p)[1] == 0.0
    assert p.leak_free < seuil, "Le jeu publié doit rester dans le domaine viable."


# --- Sensibilité globale ---------------------------------------------------
def test_sensibilite_globale_sans_contre_exemple() -> None:
    """20 000 tirages sur sept paramètres : aucun facteur <= 1 n'est admissible."""
    rng = np.random.default_rng(GRAINE)
    n = 20_000
    mu_max = rng.uniform(0.1, 5.0, n)
    K_s = 10 ** rng.uniform(-2, 1, n)
    dilution = 10 ** rng.uniform(-2, 0.5, n)
    S_in = 10 ** rng.uniform(-1, 2.5, n)
    decay = 10 ** rng.uniform(-3, 0, n)
    u, v = rng.uniform(0, 1, n), rng.uniform(0, 1, n)
    leak_libre, leak_comp = np.maximum(u, v) * 2.0, np.minimum(u, v) * 2.0

    def plateau(leak: np.ndarray) -> np.ndarray:
        l = decay + leak
        viable = l < mu_max
        S_eq = np.where(viable, K_s * l / np.where(viable, mu_max - l, 1.0), np.inf)
        interieur = viable & (S_eq < S_in)
        return np.where(interieur, dilution * (S_in - S_eq) / l, 0.0)

    P_libre, P_comp = plateau(leak_libre), plateau(leak_comp)
    admissible = (P_libre > 0) & (P_comp > 0) & (leak_comp < leak_libre)
    assert admissible.sum() > 5_000, "Échantillon viable trop maigre pour conclure."
    ratios = P_comp[admissible] / P_libre[admissible]
    assert np.all(ratios > 1.0)


# --- Robustesse structurelle ----------------------------------------------
@pytest.mark.parametrize("cinetique", ["monod", "masse_action", "haldane"])
def test_effet_positif_pour_toutes_les_cinetiques(p: Parametres, cinetique: str) -> None:
    assert facteur_retention_analytique(p.leak_free, p.leak_membrane, p, cinetique) > 1.0


def test_le_modele_refuse_une_cinetique_inconnue(p: Parametres) -> None:
    with pytest.raises(ValueError):
        croissance("inexistante", p)  # type: ignore[arg-type]


def test_parametres_avec_ne_mute_pas_l_original(p: Parametres) -> None:
    modifie = parametres_avec(p, leak_free=0.9)
    assert modifie.leak_free == 0.9
    assert p.leak_free == 0.25
