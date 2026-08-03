"""Campagne de robustesse du test interventionnel ORI-C.

Le script historique `test_interventionnel_ori_c.py` exécute *une* intégration
et rapporte *un* nombre. Cette campagne pousse ce test jusqu'à ses limites :
elle cherche activement les conditions dans lesquelles la conclusion causale
tomberait, et borne explicitement son domaine de validité.

Quatorze contrôles, du plus contraignant au plus exploratoire :

  C01  Solution stationnaire en forme close, confrontée au calcul numérique.
  C02  Convergence temporelle : le plateau à t_end = 80 est-il l'état final ?
  C03  Stabilité linéaire : spectre du jacobien et temps de relaxation.
  C04  Invariance au solveur et aux tolérances.
  C05  Invariance à la discrétisation temporelle.
  C06  Bilan de matière le long de la trajectoire.
  C07  Invariance aux conditions initiales, sur tout le quadrant positif.
  C08  Balayage continu de l'intervention et monotonie de P*.
  C09  Contrôle négatif : intervention nulle -> facteur exactement 1.
  C10  Contrôle de signe : intervention inverse -> facteur < 1.
  C11  Placebo : intervention sur une variable sans effet stationnaire.
  C12  Seuil de lavage : borne supérieure du domaine de validité.
  C13  Sensibilité globale : 200 000 tirages sur les sept paramètres.
  C14  Robustesse structurelle et stochastique : cinétiques alternatives, bruit.

Sorties dans `03_test_interventionnel/resultats_robustesse/`. Aucun fichier
du dossier publié n'est modifié.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from modele_ori_c import (  # noqa: E402
    Parametres,
    croissance,
    etat_stationnaire,
    facteur_retention_analytique,
    metriques_plateau,
    parametres_avec,
    perte_totale,
    relaxation,
    seuil_lavage,
    simuler,
)

GRAINE = 20260731
# Fenêtre d'intégration de la version antérieure du dossier. Elle n'est plus
# utilisée pour produire un résultat : elle sert à reproduire le biais
# pré-asymptotique qui a motivé la correction de l'horizon.
FENETRE_HISTORIQUE = 80.0


def dossier_sortie() -> Path:
    chemin = Path(__file__).resolve().parent.parent / "resultats_robustesse"
    chemin.mkdir(parents=True, exist_ok=True)
    return chemin


# --------------------------------------------------------------------------
# C01 - Solution stationnaire en forme close
# --------------------------------------------------------------------------
def c01_solution_analytique(p: Parametres) -> dict:
    """L'équilibre intérieur admet une expression exacte ; on la valide.

    mu(S*) = delta + l  =>  S* = K_s (delta + l) / (mu_max - delta - l)
    D (S_in - S*) = (delta + l) P*  =>  P* = D (S_in - S*) / (delta + l)
    """
    lignes = {}
    ecart_max = 0.0
    for nom, leak in (("libre", p.leak_free), ("compartiment", p.leak_membrane)):
        S_eq, P_eq = etat_stationnaire(leak, p)
        # Intégration longue et très serrée, indépendante du script historique.
        _, S, P = simuler(leak, p, t_end=4000.0, n_points=40001, rtol=1e-12, atol=1e-14)
        ecart_S = abs(S[-1] - S_eq) / S_eq
        ecart_P = abs(P[-1] - P_eq) / P_eq
        ecart_max = max(ecart_max, ecart_S, ecart_P)
        # Résidu du champ de vecteurs au point analytique : doit être nul.
        mu = croissance("monod", p)
        residu_S = p.dilution * (p.S_in - S_eq) - float(mu(np.asarray(S_eq))) * P_eq
        residu_P = (float(mu(np.asarray(S_eq))) - perte_totale(leak, p)) * P_eq
        lignes[nom] = {
            "leak": leak,
            "S_etoile": S_eq,
            "P_etoile": P_eq,
            "P_numerique_t4000": float(P[-1]),
            "ecart_relatif_S": float(ecart_S),
            "ecart_relatif_P": float(ecart_P),
            "residu_champ_S": float(residu_S),
            "residu_champ_P": float(residu_P),
        }
    ratio = facteur_retention_analytique(p.leak_free, p.leak_membrane, p)
    return {
        "etats": lignes,
        "facteur_retention_exact": float(ratio),
        "ecart_relatif_max": float(ecart_max),
        "reussi": bool(ecart_max < 1e-9),
    }


# --------------------------------------------------------------------------
# C02 - Convergence temporelle
# --------------------------------------------------------------------------
def c02_convergence_temporelle(p: Parametres) -> dict:
    """La fenêtre de 80 unités du script publié est-elle asymptotique ?"""
    exact = facteur_retention_analytique(p.leak_free, p.leak_membrane, p)
    horizons = [40, 80, 120, 160, 240, 320, 500, 800, 1200, 2000, 4000]
    serie = []
    for t_end in horizons:
        n = max(2001, int(t_end * 25))
        _, _, P_libre = simuler(p.leak_free, p, t_end=float(t_end), n_points=n)
        _, _, P_comp = simuler(p.leak_membrane, p, t_end=float(t_end), n_points=n)
        libre = metriques_plateau(P_libre)
        comp = metriques_plateau(P_comp)
        ratio = comp["mean"] / libre["mean"]
        serie.append(
            {
                "t_end": t_end,
                "plateau_libre": libre["mean"],
                "plateau_compartiment": comp["mean"],
                "facteur_retention": ratio,
                "biais_relatif_vs_exact": (ratio - exact) / exact,
                "cv_compartiment": comp["cv"],
                "derive_compartiment": comp["relative_drift"],
                "critere_stabilite_historique": bool(
                    comp["cv"] < 0.01 and comp["relative_drift"] < 0.01
                ),
            }
        )
    historique = next(item for item in serie if item["t_end"] == int(FENETRE_HISTORIQUE))
    courant = next(item for item in serie if item["t_end"] == int(p.t_end))
    premier_convergent = next(
        (item["t_end"] for item in serie if abs(item["biais_relatif_vs_exact"]) < 1e-6),
        None,
    )
    return {
        "facteur_retention_exact": float(exact),
        "serie": serie,
        "fenetre_historique": FENETRE_HISTORIQUE,
        "facteur_fenetre_historique": historique["facteur_retention"],
        "biais_relatif_fenetre_historique": historique["biais_relatif_vs_exact"],
        "critere_historique_satisfait_a_tort": historique["critere_stabilite_historique"],
        "fenetre_courante": p.t_end,
        "facteur_fenetre_courante": courant["facteur_retention"],
        "biais_relatif_fenetre_courante": courant["biais_relatif_vs_exact"],
        "t_end_minimal_pour_1e-6": premier_convergent,
        "diagnostic": (
            "Le critère de stabilité historique (cv < 1e-2 et dérive < 1e-2) était "
            f"satisfait à t_end = {FENETRE_HISTORIQUE:.0f} alors que le compartiment "
            "sélectif n'avait pas atteint son état stationnaire : le seuil était trop "
            f"permissif d'environ trois ordres de grandeur. L'horizon corrigé de "
            f"{p.t_end:.0f} unités ramène le biais sous 1e-9."
        ),
        "reussi": bool(
            historique["critere_stabilite_historique"]
            and abs(historique["biais_relatif_vs_exact"]) > 1e-3
            and abs(courant["biais_relatif_vs_exact"]) < 1e-9
        ),
    }


# --------------------------------------------------------------------------
# C03 - Stabilité linéaire
# --------------------------------------------------------------------------
def c03_stabilite_lineaire(p: Parametres) -> dict:
    """Le spectre du jacobien explique quantitativement le biais de C02."""
    detail = {}
    for nom, leak in (("libre", p.leak_free), ("compartiment", p.leak_membrane)):
        info = relaxation(leak, p)
        info["nombre_de_tau_fenetre_historique"] = FENETRE_HISTORIQUE / info["tau_lent"]
        info["residu_attendu_fenetre_historique"] = float(
            np.exp(-FENETRE_HISTORIQUE / info["tau_lent"])
        )
        info["nombre_de_tau_fenetre_courante"] = p.t_end / info["tau_lent"]
        info["residu_attendu_fenetre_courante"] = float(np.exp(-p.t_end / info["tau_lent"]))
        detail[nom] = info
    recommande = max(detail["libre"]["t_requis_1e9"], detail["compartiment"]["t_requis_1e9"])
    return {
        "equilibres": detail,
        "explication": (
            "Le mode lent du compartiment sélectif a un temps de relaxation "
            f"tau = {detail['compartiment']['tau_lent']:.2f} unités, contre "
            f"{detail['libre']['tau_lent']:.2f} en phase libre. La fenêtre historique de "
            f"{FENETRE_HISTORIQUE:.0f} unités ne couvrait que "
            f"{detail['compartiment']['nombre_de_tau_fenetre_historique']:.1f} tau, "
            "d'où un résidu transitoire de l'ordre de "
            f"{detail['compartiment']['residu_attendu_fenetre_historique']:.1e}, "
            f"compatible avec le biais mesuré. L'horizon courant de {p.t_end:.0f} unités "
            f"couvre {detail['compartiment']['nombre_de_tau_fenetre_courante']:.1f} tau."
        ),
        "t_end_recommande": recommande,
        "t_end_courant": p.t_end,
        "horizon_courant_suffisant": bool(p.t_end >= recommande),
        "reussi": bool(
            detail["libre"]["stable"] and detail["compartiment"]["stable"]
            and p.t_end >= recommande
        ),
    }


# --------------------------------------------------------------------------
# C04 - Invariance au solveur
# --------------------------------------------------------------------------
def c04_invariance_solveur(p: Parametres) -> dict:
    exact = facteur_retention_analytique(p.leak_free, p.leak_membrane, p)
    resultats = []
    for methode in ("LSODA", "Radau", "BDF", "DOP853", "RK45"):
        for rtol, atol in ((1e-6, 1e-9), (1e-9, 1e-11), (1e-12, 1e-14)):
            try:
                _, _, P_libre = simuler(
                    p.leak_free, p, t_end=1000.0, n_points=20001,
                    methode=methode, rtol=rtol, atol=atol,
                )
                _, _, P_comp = simuler(
                    p.leak_membrane, p, t_end=1000.0, n_points=20001,
                    methode=methode, rtol=rtol, atol=atol,
                )
            except RuntimeError as erreur:
                resultats.append(
                    {"methode": methode, "rtol": rtol, "atol": atol, "echec": str(erreur)}
                )
                continue
            ratio = float(P_comp[-1] / P_libre[-1])
            resultats.append(
                {
                    "methode": methode,
                    "rtol": rtol,
                    "atol": atol,
                    "facteur_retention": ratio,
                    "ecart_relatif_vs_exact": (ratio - exact) / exact,
                }
            )
    valides = [r for r in resultats if "facteur_retention" in r]
    ecarts = [abs(r["ecart_relatif_vs_exact"]) for r in valides]
    return {
        "facteur_retention_exact": float(exact),
        "configurations": resultats,
        "nombre_configurations": len(resultats),
        "nombre_echecs": len(resultats) - len(valides),
        "ecart_relatif_max": float(max(ecarts)) if ecarts else float("nan"),
        "dispersion_relative": float(
            (max(r["facteur_retention"] for r in valides) - min(r["facteur_retention"] for r in valides))
            / exact
        )
        if valides
        else float("nan"),
        "reussi": bool(ecarts and max(ecarts) < 1e-5 and len(valides) == len(resultats)),
    }


# --------------------------------------------------------------------------
# C05 - Invariance à la discrétisation
# --------------------------------------------------------------------------
def c05_invariance_discretisation(p: Parametres) -> dict:
    """`t_eval` ne doit pas influencer le résultat : ce n'est qu'un rééchantillonnage."""
    exact = facteur_retention_analytique(p.leak_free, p.leak_membrane, p)
    serie = []
    for n in (201, 501, 2001, 8001, 40001):
        _, _, P_libre = simuler(p.leak_free, p, t_end=1000.0, n_points=n)
        _, _, P_comp = simuler(p.leak_membrane, p, t_end=1000.0, n_points=n)
        ratio = float(P_comp[-1] / P_libre[-1])
        serie.append({"n_points": n, "facteur_retention": ratio,
                      "ecart_relatif_vs_exact": (ratio - exact) / exact})
    ecarts = [abs(item["ecart_relatif_vs_exact"]) for item in serie]
    return {"serie": serie, "ecart_relatif_max": float(max(ecarts)),
            "reussi": bool(max(ecarts) < 1e-6)}


# --------------------------------------------------------------------------
# C06 - Bilan de matière
# --------------------------------------------------------------------------
def c06_bilan_matiere(p: Parametres) -> dict:
    """d(S+P)/dt = D (S_in - S) - (delta + l) P doit être vérifié à chaque pas.

    On contrôle le résidu de la forme intégrale, ce qui teste le solveur
    indépendamment de la formulation du membre de droite.
    """
    detail = {}
    for nom, leak in (("libre", p.leak_free), ("compartiment", p.leak_membrane)):
        t, S, P = simuler(leak, p, t_end=1000.0, n_points=100001, rtol=1e-12, atol=1e-14)
        l = perte_totale(leak, p)
        production = np.trapezoid(p.dilution * (p.S_in - S), t)
        perte = np.trapezoid(l * P, t)
        variation = (S[-1] + P[-1]) - (S[0] + P[0])
        residu = variation - (production - perte)
        echelle = max(abs(production), abs(perte), 1e-12)
        detail[nom] = {
            "variation_S_plus_P": float(variation),
            "integrale_apport": float(production),
            "integrale_pertes": float(perte),
            "residu_absolu": float(residu),
            "residu_relatif": float(abs(residu) / echelle),
            "P_toujours_positif": bool(np.all(P > 0)),
            "S_toujours_positif": bool(np.all(S > 0)),
            "S_borne_par_S_in": bool(np.all(S <= p.S_in + 1e-9)),
        }
    return {
        "trajectoires": detail,
        "residu_relatif_max": float(max(v["residu_relatif"] for v in detail.values())),
        "reussi": bool(
            all(v["residu_relatif"] < 1e-7 and v["P_toujours_positif"] and v["S_toujours_positif"]
                for v in detail.values())
        ),
    }


# --------------------------------------------------------------------------
# C07 - Invariance aux conditions initiales
# --------------------------------------------------------------------------
def c07_conditions_initiales(p: Parametres) -> dict:
    """L'équilibre intérieur doit être atteint depuis tout le quadrant positif."""
    exact_libre = etat_stationnaire(p.leak_free, p)[1]
    exact_comp = etat_stationnaire(p.leak_membrane, p)[1]
    grille_S = [1e-4, 0.01, 0.5, 1.0, 5.0, 10.0, 50.0]
    grille_P = [1e-6, 1e-3, 0.1, 1.0, 10.0, 100.0]
    ecarts = []
    non_convergents = []
    for S0 in grille_S:
        for P0 in grille_P:
            _, _, P_libre = simuler(p.leak_free, p, t_end=3000.0, n_points=6001,
                                    y0=(S0, P0), rtol=1e-11, atol=1e-13)
            _, _, P_comp = simuler(p.leak_membrane, p, t_end=3000.0, n_points=6001,
                                   y0=(S0, P0), rtol=1e-11, atol=1e-13)
            e_libre = abs(P_libre[-1] - exact_libre) / exact_libre
            e_comp = abs(P_comp[-1] - exact_comp) / exact_comp
            ecarts.append(max(e_libre, e_comp))
            if max(e_libre, e_comp) > 1e-6:
                non_convergents.append({"S0": S0, "P0": P0,
                                        "ecart_libre": float(e_libre),
                                        "ecart_compartiment": float(e_comp)})
    return {
        "nombre_conditions_initiales": len(grille_S) * len(grille_P),
        "ecart_relatif_max": float(max(ecarts)),
        "conditions_non_convergentes": non_convergents,
        "note": "P0 = 0 est exclu : c'est l'équilibre trivial de lavage, non un contre-exemple.",
        "reussi": bool(not non_convergents),
    }


# --------------------------------------------------------------------------
# C08 - Balayage de l'intervention
# --------------------------------------------------------------------------
def c08_balayage_intervention(p: Parametres) -> dict:
    """P* doit être strictement décroissant en `leak` sur tout le domaine viable."""
    seuil = seuil_lavage(p)
    fuites = np.linspace(0.0, seuil * 0.999, 400)
    plateaux = np.array([etat_stationnaire(float(l), p)[1] for l in fuites])
    differences = np.diff(plateaux)
    ratios = plateaux / etat_stationnaire(p.leak_free, p)[1]
    # Contrôle numérique indépendant sur un sous-échantillon.
    # L'horizon est adapté au temps de relaxation local : tau diverge quand
    # `leak` approche le seuil de lavage, un horizon fixe y serait trompeur.
    indices = np.linspace(0, len(fuites) - 1, 15).astype(int)
    ecart_numerique = 0.0
    verifications = []
    horizon_max = 200_000.0
    for i in indices:
        leak = float(fuites[i])
        tau = relaxation(leak, p)["tau_lent"]
        horizon = max(2000.0, 30.0 * tau) if np.isfinite(tau) else float("inf")
        if plateaux[i] <= 1e-9 or horizon > horizon_max:
            verifications.append({
                "leak": leak, "P_etoile": float(plateaux[i]), "tau_lent": float(tau),
                "horizon_requis": float(horizon),
                "statut": "hors_portee_numerique",
            })
            continue
        _, _, P = simuler(leak, p, t_end=horizon, n_points=4001, rtol=1e-11, atol=1e-13)
        ecart = abs(P[-1] - plateaux[i]) / plateaux[i]
        ecart_numerique = max(ecart_numerique, ecart)
        verifications.append({
            "leak": leak, "P_etoile": float(plateaux[i]), "tau_lent": float(tau),
            "horizon_utilise": float(horizon), "ecart_relatif": float(ecart),
            "statut": "verifie",
        })
    n_verifies = sum(1 for v in verifications if v["statut"] == "verifie")
    return {
        "verifications_numeriques": verifications,
        "n_points_verifies_numeriquement": n_verifies,
        "n_points_hors_portee_numerique": len(verifications) - n_verifies,
        "note_hors_portee": (
            "Au voisinage du seuil de lavage, le mode lent tend vers zéro et le "
            "temps de relaxation diverge : ces points restent établis "
            "analytiquement mais ne sont pas intégrables en temps fini."
        ),
        "seuil_lavage": float(seuil),
        "nombre_points": len(fuites),
        "strictement_decroissant": bool(np.all(differences < 0)),
        "difference_positive_max": float(np.max(differences)),
        "facteur_min_sous_leak_free": float(np.min(ratios[fuites < p.leak_free])),
        "tous_facteurs_superieurs_a_1_sous_leak_free": bool(
            np.all(ratios[fuites < p.leak_free] > 1.0)
        ),
        "ecart_numerique_max": float(ecart_numerique),
        "courbe": [{"leak": float(l), "P_etoile": float(v)}
                   for l, v in zip(fuites[::10], plateaux[::10])],
        "reussi": bool(
            np.all(differences < 0)
            and np.all(ratios[fuites < p.leak_free] > 1.0)
            and n_verifies >= 10
            and ecart_numerique < 1e-6
        ),
    }


# --------------------------------------------------------------------------
# C09 / C10 / C11 - Contrôles négatifs
# --------------------------------------------------------------------------
def c09_controle_nul(p: Parametres) -> dict:
    """Intervention nulle : le facteur doit valoir exactement 1."""
    ratio_exact = facteur_retention_analytique(p.leak_free, p.leak_free, p)
    _, _, P_a = simuler(p.leak_free, p, t_end=1000.0, n_points=20001)
    _, _, P_b = simuler(p.leak_free, p, t_end=1000.0, n_points=20001)
    ratio_numerique = float(P_b[-1] / P_a[-1])
    return {
        "facteur_analytique": float(ratio_exact),
        "facteur_numerique": ratio_numerique,
        "ecart_a_1": float(abs(ratio_numerique - 1.0)),
        "reussi": bool(ratio_exact == 1.0 and abs(ratio_numerique - 1.0) < 1e-12),
    }


def c10_controle_signe(p: Parametres) -> dict:
    """Intervention inverse : augmenter la perte doit réduire P*."""
    leak_haut = min(p.leak_free * 2.0, seuil_lavage(p) * 0.9)
    ratio = facteur_retention_analytique(p.leak_free, leak_haut, p)
    _, _, P_ref = simuler(p.leak_free, p, t_end=2000.0, n_points=20001)
    _, _, P_haut = simuler(leak_haut, p, t_end=2000.0, n_points=20001)
    ratio_num = float(P_haut[-1] / P_ref[-1])
    return {
        "leak_augmente": float(leak_haut),
        "facteur_analytique": float(ratio),
        "facteur_numerique": ratio_num,
        "reussi": bool(ratio < 1.0 and ratio_num < 1.0),
    }


def c11_placebo(p: Parametres) -> dict:
    """Interventions qui ne doivent produire aucun effet stationnaire.

    P0, S0 et n_points ne figurent pas dans l'expression de P*. Si l'un d'eux
    déplaçait le plateau, le protocole serait confondu par une variable non
    contrôlée.
    """
    reference = etat_stationnaire(p.leak_membrane, p)[1]
    essais = []
    for nom, kwargs in (
        ("P0 x 100", {"y0": (p.S0, p.P0 * 100)}),
        ("P0 / 1000", {"y0": (p.S0, p.P0 / 1000)}),
        ("S0 = S_in", {"y0": (p.S_in, p.P0)}),
        ("n_points x 10", {"n_points": 20001}),
    ):
        _, _, P = simuler(p.leak_membrane, p, t_end=3000.0,
                          n_points=kwargs.pop("n_points", 6001),
                          rtol=1e-11, atol=1e-13, **kwargs)
        ecart = abs(P[-1] - reference) / reference
        essais.append({"intervention_placebo": nom, "plateau": float(P[-1]),
                       "ecart_relatif": float(ecart)})
    return {
        "plateau_de_reference": float(reference),
        "essais": essais,
        "ecart_relatif_max": float(max(e["ecart_relatif"] for e in essais)),
        "reussi": bool(all(e["ecart_relatif"] < 1e-8 for e in essais)),
    }


# --------------------------------------------------------------------------
# C12 - Seuil de lavage
# --------------------------------------------------------------------------
def c12_seuil_lavage(p: Parametres) -> dict:
    """Borne supérieure du domaine où l'affirmation causale a un sens."""
    seuil = seuil_lavage(p)
    points = []
    for facteur in (0.90, 0.99, 1.0, 1.01, 1.10, 2.00):
        leak = seuil * facteur
        _, P_analytique = etat_stationnaire(leak, p)
        _, _, P = simuler(leak, p, t_end=6000.0, n_points=12001, rtol=1e-11, atol=1e-13)
        points.append({
            "leak": float(leak),
            "leak_sur_seuil": facteur,
            "P_etoile_analytique": float(P_analytique),
            "P_numerique_t6000": float(P[-1]),
            "extinction": bool(P[-1] < 1e-3),
        })
    au_dessus = [pt for pt in points if pt["leak_sur_seuil"] > 1.0]
    en_dessous = [pt for pt in points if pt["leak_sur_seuil"] < 1.0]
    return {
        "seuil_lavage": float(seuil),
        "formule": "leak_crit = mu_max S_in / (K_s + S_in) - delta",
        "points": points,
        "domaine_de_validite": f"0 <= leak < {seuil:.6f}",
        "marge_du_dossier": float(seuil / p.leak_free),
        "reussi": bool(
            all(pt["P_etoile_analytique"] == 0.0 for pt in au_dessus)
            and all(pt["P_etoile_analytique"] > 0.0 for pt in en_dessous)
        ),
    }


# --------------------------------------------------------------------------
# C13 - Sensibilité globale
# --------------------------------------------------------------------------
def c13_sensibilite_globale(p: Parametres, n_tirages: int = 200_000) -> dict:
    """La conclusion tient-elle hors du jeu de paramètres choisi ?

    Tirage uniforme sur sept paramètres, en n'imposant que la contrainte du
    protocole (leak_compartiment < leak_libre) et la viabilité des deux
    systèmes. Toute réalisation avec facteur <= 1 réfuterait l'affirmation.
    """
    rng = np.random.default_rng(GRAINE)
    mu_max = rng.uniform(0.1, 5.0, n_tirages)
    K_s = 10 ** rng.uniform(-2, 1, n_tirages)
    dilution = 10 ** rng.uniform(-2, 0.5, n_tirages)
    S_in = 10 ** rng.uniform(-1, 2.5, n_tirages)
    decay = 10 ** rng.uniform(-3, 0, n_tirages)
    u = rng.uniform(0.0, 1.0, n_tirages)
    v = rng.uniform(0.0, 1.0, n_tirages)
    leak_libre = np.maximum(u, v) * 2.0
    leak_comp = np.minimum(u, v) * 2.0

    def plateau(leak: np.ndarray) -> np.ndarray:
        l = decay + leak
        viable = l < mu_max
        S_eq = np.where(viable, K_s * l / np.where(viable, mu_max - l, 1.0), np.inf)
        interieur = viable & (S_eq < S_in)
        return np.where(interieur, dilution * (S_in - S_eq) / l, 0.0)

    P_libre = plateau(leak_libre)
    P_comp = plateau(leak_comp)
    strict = leak_comp < leak_libre
    viable = (P_libre > 0) & (P_comp > 0) & strict
    ratios = np.where(viable, P_comp / np.maximum(P_libre, 1e-300), np.nan)
    ratios_viables = ratios[viable]
    contre_exemples = int(np.sum(ratios_viables <= 1.0))

    # Cas où le système libre est lavé mais le compartiment survit : l'effet
    # est alors qualitatif (0 -> P* > 0) et non exprimable en facteur.
    sauvetage = int(np.sum(strict & (P_libre <= 0) & (P_comp > 0)))
    perte_des_deux = int(np.sum(strict & (P_libre <= 0) & (P_comp <= 0)))

    return {
        "n_tirages": n_tirages,
        "graine": GRAINE,
        "n_viables": int(np.sum(viable)),
        "n_sauvetage_qualitatif": sauvetage,
        "n_deux_systemes_laves": perte_des_deux,
        "contre_exemples_facteur_inferieur_ou_egal_1": contre_exemples,
        "facteur_min": float(np.min(ratios_viables)),
        "facteur_median": float(np.median(ratios_viables)),
        "facteur_p99": float(np.percentile(ratios_viables, 99)),
        "facteur_max": float(np.max(ratios_viables)),
        "conclusion": (
            "Aucun contre-exemple : sur le domaine viable, réduire la perte de P "
            "augmente strictement son état stationnaire. L'affirmation causale du "
            "modèle n'est pas un artefact du jeu de paramètres publié."
            if contre_exemples == 0 else
            f"{contre_exemples} contre-exemples : l'affirmation est conditionnelle."
        ),
        "reussi": bool(contre_exemples == 0),
    }


# --------------------------------------------------------------------------
# C14 - Robustesse structurelle et stochastique
# --------------------------------------------------------------------------
def c14_robustesse_structurelle(p: Parametres, n_replicas: int = 400) -> dict:
    """Le résultat dépend-il de la forme de mu(S) ou de l'absence de bruit ?"""
    structurel = {}
    for cinetique in ("monod", "masse_action", "haldane"):
        try:
            ratio = facteur_retention_analytique(p.leak_free, p.leak_membrane, p, cinetique)
            _, P_libre = etat_stationnaire(p.leak_free, p, cinetique)
            _, P_comp = etat_stationnaire(p.leak_membrane, p, cinetique)
            structurel[cinetique] = {
                "P_libre": float(P_libre), "P_compartiment": float(P_comp),
                "facteur_retention": float(ratio), "effet_positif": bool(ratio > 1.0),
            }
        except (ValueError, ZeroDivisionError) as erreur:
            structurel[cinetique] = {"echec": str(erreur), "effet_positif": False}

    # Euler-Maruyama, bruit multiplicatif sur les deux variables.
    # Le pas est choisi bien sous 2/|lambda_rapide| pour rester stable.
    rng = np.random.default_rng(GRAINE)
    dt, t_max, sigma, fenetre = 0.01, 400.0, 0.05, 100.0
    n_pas = int(t_max / dt)
    debut_moyenne = n_pas - int(fenetre / dt)
    mu = croissance("monod", p)

    def trajectoires(leak: float) -> np.ndarray:
        """Moyenne temporelle de P sur la dernière fenêtre, par réplica."""
        l = perte_totale(leak, p)
        S = np.full(n_replicas, p.S0)
        P = np.full(n_replicas, p.P0)
        somme = np.zeros(n_replicas)
        compte = 0
        racine = np.sqrt(dt)
        for pas in range(n_pas):
            reaction = mu(S) * P
            dS = (p.dilution * (p.S_in - S) - reaction) * dt
            dP = (reaction - l * P) * dt
            S = np.maximum(S + dS + sigma * S * racine * rng.standard_normal(n_replicas), 1e-12)
            P = np.maximum(P + dP + sigma * P * racine * rng.standard_normal(n_replicas), 1e-12)
            if pas >= debut_moyenne:
                somme += P
                compte += 1
        return somme / compte

    P_libre_stoch = trajectoires(p.leak_free)
    P_comp_stoch = trajectoires(p.leak_membrane)
    ratios = P_comp_stoch / P_libre_stoch
    bootstrap = rng.choice(ratios, size=(4000, n_replicas), replace=True).mean(axis=1)
    ic_bas, ic_haut = np.percentile(bootstrap, [2.5, 97.5])

    return {
        "cinetiques_alternatives": structurel,
        "effet_positif_pour_toutes_les_cinetiques": bool(
            all(v.get("effet_positif") for v in structurel.values())
        ),
        "stochastique": {
            "n_replicas": n_replicas,
            "sigma_bruit_multiplicatif": sigma,
            "pas_de_temps": dt,
            "facteur_moyen": float(np.mean(ratios)),
            "facteur_median": float(np.median(ratios)),
            "ic95_bootstrap": [float(ic_bas), float(ic_haut)],
            "fraction_replicas_avec_effet_positif": float(np.mean(ratios > 1.0)),
            "borne_inferieure_ic_superieure_a_1": bool(ic_bas > 1.0),
        },
        "reussi": bool(
            all(v.get("effet_positif") for v in structurel.values())
            and ic_bas > 1.0
            and float(np.mean(ratios > 1.0)) > 0.99
        ),
    }


# --------------------------------------------------------------------------
# Figures
# --------------------------------------------------------------------------
def figures(p: Parametres, resultats: dict, sortie: Path) -> None:
    exact = resultats["C01"]["facteur_retention_exact"]
    fig, axes = plt.subplots(2, 2, figsize=(11.7, 8.3))

    ax = axes[0, 0]
    serie = resultats["C02"]["serie"]
    ax.plot([s["t_end"] for s in serie], [s["facteur_retention"] for s in serie],
            marker="o", linewidth=1.6, label="Facteur mesuré")
    ax.axhline(exact, linestyle="--", linewidth=1.2, color="#B22222",
               label=f"Valeur exacte {exact:.6f}")
    ax.axvline(FENETRE_HISTORIQUE, linestyle=":", linewidth=1.2, color="#4A4A4A",
               label=f"Fenêtre historique t = {FENETRE_HISTORIQUE:.0f}")
    ax.axvline(p.t_end, linestyle="-.", linewidth=1.2, color="#1F6F4A",
               label=f"Horizon corrigé t = {p.t_end:.0f}")
    ax.set_xscale("log")
    ax.set_xlabel("Horizon d'intégration, unités du modèle")
    ax.set_ylabel("Facteur de rétention")
    ax.set_title("C02 — Convergence temporelle du facteur")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, fontsize=8)

    ax = axes[0, 1]
    courbe = resultats["C08"]["courbe"]
    fuites = [c["leak"] for c in courbe]
    plateaux = [c["P_etoile"] for c in courbe]
    ax.plot(fuites, plateaux, linewidth=2.0)
    ax.axvline(p.leak_free, linestyle="--", linewidth=1.2, color="#B22222", label="Phase libre")
    ax.axvline(p.leak_membrane, linestyle="--", linewidth=1.2, color="#1F6F4A",
               label="Compartiment sélectif")
    ax.axvline(resultats["C12"]["seuil_lavage"], linestyle=":", linewidth=1.4,
               color="#4A4A4A", label="Seuil de lavage")
    ax.set_yscale("log")
    ax.set_xlabel("Taux de perte de P")
    ax.set_ylabel("Plateau P* (échelle log)")
    ax.set_title("C08/C12 — Monotonie et domaine de validité")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 0]
    for nom, leak, style in (("Phase libre", p.leak_free, "--"),
                             ("Compartiment sélectif", p.leak_membrane, "-")):
        t, _, P = simuler(leak, p, t_end=600.0, n_points=12001)
        cible = etat_stationnaire(leak, p)[1]
        ax.plot(t, np.abs(P - cible) / cible, linestyle=style, linewidth=1.7, label=nom)
    ax.axvline(FENETRE_HISTORIQUE, linestyle=":", linewidth=1.2, color="#4A4A4A")
    ax.axvline(p.t_end, linestyle="-.", linewidth=1.2, color="#1F6F4A")
    ax.set_yscale("log")
    ax.set_xlabel("Temps, unités du modèle")
    ax.set_ylabel("Écart relatif à P*")
    ax.set_title("C03 — Relaxation vers l'équilibre")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 1]
    conf = [c for c in resultats["C04"]["configurations"] if "facteur_retention" in c]
    etiquettes = [f"{c['methode']}\n{c['rtol']:.0e}" for c in conf]
    ax.plot(range(len(conf)), [abs(c["ecart_relatif_vs_exact"]) for c in conf],
            marker="s", linestyle="none")
    ax.set_yscale("log")
    ax.set_xticks(range(len(conf)))
    ax.set_xticklabels(etiquettes, fontsize=5.5, rotation=90)
    ax.set_ylabel("|écart relatif| à la valeur exacte")
    ax.set_title("C04 — Invariance solveur et tolérances")
    ax.grid(alpha=0.25)

    fig.suptitle("Campagne de robustesse du test interventionnel ORI-C", fontsize=12)
    fig.tight_layout(rect=(0, 0.02, 1, 0.97))
    fig.savefig(sortie / "robustesse_test_interventionnel.png", dpi=220, bbox_inches="tight",
                metadata={"Software": None})
    fig.savefig(sortie / "robustesse_test_interventionnel.pdf", bbox_inches="tight",
                metadata={"CreationDate": None, "Producer": None, "Creator": None})
    plt.close(fig)


# --------------------------------------------------------------------------
def main() -> int:
    p = Parametres()
    sortie = dossier_sortie()

    controles = [
        ("C01", "Solution stationnaire en forme close", lambda: c01_solution_analytique(p)),
        ("C02", "Convergence temporelle", lambda: c02_convergence_temporelle(p)),
        ("C03", "Stabilité linéaire", lambda: c03_stabilite_lineaire(p)),
        ("C04", "Invariance au solveur", lambda: c04_invariance_solveur(p)),
        ("C05", "Invariance à la discrétisation", lambda: c05_invariance_discretisation(p)),
        ("C06", "Bilan de matière", lambda: c06_bilan_matiere(p)),
        ("C07", "Invariance aux conditions initiales", lambda: c07_conditions_initiales(p)),
        ("C08", "Balayage de l'intervention", lambda: c08_balayage_intervention(p)),
        ("C09", "Contrôle négatif, intervention nulle", lambda: c09_controle_nul(p)),
        ("C10", "Contrôle de signe, intervention inverse", lambda: c10_controle_signe(p)),
        ("C11", "Placebo, variables sans effet stationnaire", lambda: c11_placebo(p)),
        ("C12", "Seuil de lavage", lambda: c12_seuil_lavage(p)),
        ("C13", "Sensibilité globale", lambda: c13_sensibilite_globale(p)),
        ("C14", "Robustesse structurelle et stochastique", lambda: c14_robustesse_structurelle(p)),
    ]

    resultats: dict[str, dict] = {}
    resume = []
    for code, titre, fonction in controles:
        print(f"[{code}] {titre} ...", flush=True)
        bloc = fonction()
        bloc["titre"] = titre
        resultats[code] = bloc
        resume.append((code, titre, bool(bloc.get("reussi", False))))

    exact = resultats["C01"]["facteur_retention_exact"]
    historique = resultats["C02"]["facteur_fenetre_historique"]
    courant = resultats["C02"]["facteur_fenetre_courante"]

    rapport = {
        "statut": "campagne_de_robustesse",
        "parametres": {
            "mu_max": p.mu_max, "K_s": p.K_s, "dilution": p.dilution, "S_in": p.S_in,
            "decay": p.decay, "leak_free": p.leak_free, "leak_membrane": p.leak_membrane,
            "S0": p.S0, "P0": p.P0, "t_end": p.t_end, "n_points": p.n_points,
        },
        "facteur_retention_exact": exact,
        "facteur_retention_courant": courant,
        "biais_relatif_courant": (courant - exact) / exact,
        "facteur_retention_fenetre_historique": historique,
        "biais_relatif_fenetre_historique": (historique - exact) / exact,
        "controles": resultats,
        "controles_reussis": sum(1 for _, _, ok in resume if ok),
        "controles_totaux": len(resume),
        "tous_reussis": all(ok for _, _, ok in resume),
        "portee": (
            "Contrôle de robustesse interne d'un modèle déterministe défini. "
            "Aucune portée probante empirique sur le vivant."
        ),
    }

    (sortie / "robustesse_test_interventionnel.json").write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2, default=float) + "\n",
        encoding="utf-8", newline="\n",
    )

    lignes = [
        "CAMPAGNE DE ROBUSTESSE — TEST INTERVENTIONNEL ORI-C",
        "=" * 72,
        "",
        f"Facteur de rétention exact (état stationnaire)   : {exact:.10f}",
        f"Facteur mesuré, horizon courant t_end = {p.t_end:.0f}      : {courant:.10f}",
        f"Biais relatif de la valeur courante              : {(courant - exact) / exact:+.2e}",
        "",
        f"Rappel du défaut corrigé, fenêtre t_end = {FENETRE_HISTORIQUE:.0f}    : {historique:.10f}",
        f"Biais relatif de la fenêtre historique           : "
        f"{(historique - exact) / exact:+.4%}",
        "",
        f"Horizon minimal pour un biais < 1e-6             : "
        f"{resultats['C02']['t_end_minimal_pour_1e-6']} unités",
        f"Horizon requis pour un biais < 1e-9              : "
        f"{resultats['C03']['t_end_recommande']:.1f} unités",
        f"Temps de relaxation du compartiment sélectif     : "
        f"{resultats['C03']['equilibres']['compartiment']['tau_lent']:.3f} unités",
        f"Domaine de validité de l'affirmation causale     : "
        f"{resultats['C12']['domaine_de_validite']}",
        f"Tirages de sensibilité globale sans contre-exemple : "
        f"{resultats['C13']['n_viables']} / {resultats['C13']['n_tirages']}",
        "",
        "-" * 72,
        "",
    ]
    for code, titre, ok in resume:
        lignes.append(f"  {code}  {'RÉUSSI ' if ok else 'ÉCHOUÉ '}  {titre}")
    lignes += [
        "",
        "-" * 72,
        f"Bilan : {rapport['controles_reussis']} / {rapport['controles_totaux']} contrôles réussis.",
        "",
        "Portée : cohérence interne d'un modèle déterministe défini, sans portée",
        "probante générale sur le vivant.",
    ]
    (sortie / "rapport_robustesse.txt").write_text(
        "\n".join(lignes) + "\n", encoding="utf-8", newline="\n"
    )

    figures(p, resultats, sortie)
    print("\n".join(lignes))
    return 0 if rapport["tous_reussis"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
