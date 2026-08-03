"""Portée du test interventionnel — WP-S2 du plan directeur.

Le test interventionnel réussit 11/11 **dans son modèle réduit** : un chémostat
à deux variables, cinétique de Monod, perte constante. Le plan directeur
demande si le mécanisme survit hors de ce modèle.

    A. Six cinétiques de croissance, dont trois absentes du dossier :
       Hill, Contois, Droop. Le seuil de lavage et la bifurcation
       transcritique subsistent-ils ?
    B. Treize extensions structurelles : ressource secondaire, compétition,
       cross-feeding, prédation, bruit démographique, bruit environnemental
       coloré, retards, hétérogénéité spatiale, biofilm, pertes dépendant de
       la densité, pertes pulsées, pertes corrélées à la ressource.
    C. **Item 14, le test décisif.** Existe-t-il un domaine où *réduire* une
       perte *diminue* la persistance globale par effet indirect ? C'est la
       seule prédiction du test interventionnel qui soit contre-intuitive.
       Si elle n'est vraie nulle part, le résultat 11/11 ne dit que ce que dit
       déjà la théorie du chémostat.

Exécution : `python portee_wp_s2.py [--graine 20260801]`
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

RACINE = Path(__file__).resolve().parents[1]
SORTIE = RACINE / "resultats_portee"

# Paramètres de référence, ceux du dossier.
BASE = dict(mu_max=1.0, K_s=1.0, D=0.25, S_in=10.0, decay=0.05)
GRILLE_L = np.linspace(0.0, 1.2, 121)

# Une remontée n'est retenue que si elle atteint 1 % de l'amplitude de la
# courbe. La première exécution employait un seuil absolu de 1e-3 et retenait
# neuf cas dont les remontées valaient 0,01 % à 0,17 % de l'amplitude : du
# bruit d'intégration.
REMONTEE_RELATIVE_MINIMALE = 0.01


# ==========================================================================
# A. Cinétiques

def mu_de(nom, S, P=None, **kw):
    """Six cinétiques. `Contois` et `Droop` dépendent aussi de P."""
    mu_max, K_s = kw.get("mu_max", 1.0), kw.get("K_s", 1.0)
    if nom == "monod":
        return mu_max * S / (K_s + S)
    if nom == "masse_action":
        return mu_max * S / K_s
    if nom == "haldane":
        return mu_max * S / (K_s + S + S * S / kw.get("K_i", 50.0))
    if nom == "hill":
        n = kw.get("n_hill", 2.0)
        return mu_max * S ** n / (K_s ** n + S ** n)
    if nom == "contois":
        # Le demi-saturation croît avec la biomasse : compétition intraspécifique.
        return mu_max * S / (K_s * max(P, 1e-12) + S)
    if nom == "droop":
        # Quota cellulaire : croissance nulle sous le quota minimal.
        q_min = kw.get("q_min", 0.3)
        quota = q_min + S / (K_s + S)
        return mu_max * max(0.0, 1.0 - q_min / max(quota, 1e-12))
    raise ValueError(nom)


def equilibre_interieur(nom, l, **kw):
    """(S*, P*) par résolution numérique de mu(S*, P*) = decay + l."""
    from scipy.optimize import brentq
    D, S_in, decay = kw.get("D", 0.25), kw.get("S_in", 10.0), kw.get("decay", 0.05)
    perte = decay + l

    def residu(S):
        P = D * (S_in - S) / max(perte, 1e-12)
        return mu_de(nom, S, P, **kw) - perte

    try:
        if residu(1e-9) * residu(S_in - 1e-9) > 0:
            return None
        S = brentq(residu, 1e-9, S_in - 1e-9, xtol=1e-12, rtol=1e-14)
    except (ValueError, RuntimeError):
        return None
    P = D * (S_in - S) / max(perte, 1e-12)
    return (float(S), float(P)) if P > 1e-9 else None


def a_cinetiques(**kw) -> dict:
    """Seuil de lavage et monotonie de P* en fonction de l, six cinétiques."""
    resultat = {}
    for nom in ("monod", "masse_action", "haldane", "hill", "contois", "droop"):
        biomasses, presents = [], []
        for l in GRILLE_L:
            eq = equilibre_interieur(nom, float(l), **kw)
            presents.append(eq is not None)
            biomasses.append(eq[1] if eq else 0.0)
        biomasses = np.asarray(biomasses)
        vivants = np.flatnonzero(presents)
        seuil = float(GRILLE_L[vivants[-1]]) if len(vivants) else None
        # Monotonie stricte de P* sur le domaine où l'équilibre existe.
        if len(vivants) >= 3:
            segment = biomasses[vivants]
            croissances = np.diff(segment)
            monotone = bool(np.all(croissances <= 1e-9))
            remontees = int(np.sum(croissances > 1e-9))
        else:
            monotone, remontees = None, None
        resultat[nom] = {
            "seuil_de_lavage": seuil,
            "P_etoile_decroit_avec_l": monotone,
            "nombre_de_remontees": remontees,
            "P_etoile_a_l_nul": float(biomasses[0]),
        }
    return {
        "par_cinetique": resultat,
        "lecture": (
            "Le seuil de lavage et la décroissance de P* avec l sont les deux "
            "propriétés dont dépend l'affirmation causale. Une cinétique qui "
            "les perd sort du domaine de validité du test 11/11."
        ),
    }


# ==========================================================================
# B et C. Extensions structurelles, et recherche de non-monotonie

def _integrer(champ, y0, t_fin=4000.0, rng=None, bruit=0.0, tau_bruit=0.0):
    """Intégration déterministe, ou Euler-Maruyama si `bruit` > 0."""
    if bruit <= 0.0:
        solution = solve_ivp(champ, (0.0, t_fin), y0, method="LSODA",
                             rtol=1e-8, atol=1e-10, dense_output=False)
        return solution.y[:, -1], solution.success
    pas = 0.01
    etapes = int(t_fin / pas)
    y = np.asarray(y0, dtype=float)
    couleur = 0.0
    for _ in range(etapes):
        if tau_bruit > 0.0:
            couleur += (-couleur / tau_bruit) * pas \
                + bruit * np.sqrt(pas) * rng.normal()
            perturbation = couleur
        else:
            perturbation = bruit * np.sqrt(pas) * rng.normal()
        derivee = np.asarray(champ(0.0, y), dtype=float)
        if tau_bruit > 0.0:
            # Bruit environnemental : écart de taux, il entre dans la dérive
            # et se multiplie donc par `pas`. La première exécution le
            # multipliait par la racine du pas, ce qui le rendait ~35 fois
            # trop fort et éteignait la population même à perte nulle.
            y = y + (derivee + perturbation * np.maximum(y, 0.0)) * pas
        else:
            # Bruit démographique : amplitude en racine de l'effectif.
            y = y + derivee * pas + perturbation * np.sqrt(np.maximum(y, 0.0))
        y = np.maximum(y, 0.0)
        if y[1] < 1e-8:
            return y, True
    return y, True


def variantes(l, rng=None, **kw):
    """Chaque variante renvoie (champ de vecteurs, état initial, indice de P)."""
    mu_max, K_s = kw.get("mu_max", 1.0), kw.get("K_s", 1.0)
    D, S_in, decay = kw.get("D", 0.25), kw.get("S_in", 10.0), kw.get("decay", 0.05)
    perte = decay + l
    monod = lambda S: mu_max * S / (K_s + max(S, 0.0))

    def base(_, y):
        S, P = y
        return [D * (S_in - S) - monod(S) * P, monod(S) * P - perte * P]

    def seconde_ressource(_, y):
        S, N, P = y
        limite = monod(S) * (N / (0.5 + max(N, 0.0)))
        return [D * (S_in - S) - limite * P,
                D * (2.0 - N) - 0.3 * limite * P,
                limite * P - perte * P]

    def competition(_, y):
        S, P1, P2 = y
        # Espèce 2 moins efficace : sans perte, l'espèce 1 l'emporte ;
        # avec perte croissante, l'avantage bascule. La première exécution
        # donnait à l'espèce 2 un seuil de survie plus bas, si bien que
        # l'espèce 1 disparaissait même à perte nulle et la variante ne
        # testait rien.
        m1, m2 = monod(S), 0.70 * S / (1.4 + max(S, 0.0))
        return [D * (S_in - S) - m1 * P1 - m2 * P2,
                m1 * P1 - perte * P1,
                m2 * P2 - (decay + 0.5 * l) * P2]

    def cross_feeding(_, y):
        # P1 produit un métabolite B consommé par P2 ; P2 recycle du substrat.
        S, B, P1, P2 = y
        m1 = monod(S)
        m2 = 0.8 * B / (0.4 + max(B, 0.0))
        return [D * (S_in - S) - m1 * P1 + 0.35 * m2 * P2,
                0.5 * m1 * P1 - m2 * P2 - D * B,
                m1 * P1 - perte * P1,
                m2 * P2 - (decay + 0.2) * P2]

    def predation(_, y):
        # Un prédateur ou phage dont la charge suit la densité de P.
        S, P, Z = y
        m = monod(S)
        attaque = 0.35 * P / (1.5 + max(P, 0.0))
        return [D * (S_in - S) - m * P,
                m * P - perte * P - attaque * Z,
                0.6 * attaque * Z - (D + 0.05) * Z]

    def retard(_, y):
        # Mémoire physiologique : l'état interne suit mu avec un retard.
        S, P, M = y
        return [D * (S_in - S) - M * P,
                M * P - perte * P,
                (monod(S) - M) / 8.0]

    def spatial(_, y):
        # Deux compartiments couplés par diffusion, perte dans l'un seulement.
        S1, P1, S2, P2 = y
        e = 0.05
        return [D * (S_in - S1) - monod(S1) * P1 + e * (S2 - S1),
                monod(S1) * P1 - perte * P1 + e * (P2 - P1),
                D * (S_in - S2) - monod(S2) * P2 + e * (S1 - S2),
                monod(S2) * P2 - decay * P2 + e * (P1 - P2)]

    def perte_densite(_, y):
        S, P = y
        return [D * (S_in - S) - monod(S) * P,
                monod(S) * P - (decay + l * (1.0 + 0.3 * P)) * P]

    def perte_correlee(_, y):
        S, P = y
        effective = decay + l * (S / S_in)
        return [D * (S_in - S) - monod(S) * P, monod(S) * P - effective * P]

    return {
        "base": (base, [1.0, 0.1], 1),
        "seconde_ressource": (seconde_ressource, [1.0, 1.0, 0.1], 2),
        "competition": (competition, [1.0, 0.1, 0.1], 1),
        "cross_feeding": (cross_feeding, [1.0, 0.1, 0.1, 0.1], 2),
        "predation": (predation, [1.0, 0.5, 0.2], 1),
        "retard": (retard, [1.0, 0.1, 0.1], 1),
        "spatial": (spatial, [1.0, 0.1, 1.0, 0.1], 1),
        "perte_densite": (perte_densite, [1.0, 0.1], 1),
        "perte_correlee": (perte_correlee, [1.0, 0.1], 1),
    }


def b_extensions(rng, grille=None, **kw) -> dict:
    """Pour chaque variante : P final en fonction de l, et non-monotonie."""
    grille = GRILLE_L if grille is None else grille
    resultat = {}
    noms = list(variantes(0.0, rng, **kw))
    for nom in noms:
        biomasses = []
        for l in grille:
            champ, y0, indice = variantes(float(l), rng, **kw)[nom]
            final, ok = _integrer(champ, y0)
            biomasses.append(float(final[indice]) if ok else float("nan"))
        b = np.asarray(biomasses)
        vivants = b > 1e-6
        seuil = float(grille[np.flatnonzero(vivants)[-1]]) \
            if vivants.any() else None
        # Remontées : l augmente et la biomasse augmente aussi.
        segment = b[vivants] if vivants.sum() >= 3 else np.array([])
        remontees = int(np.sum(np.diff(segment) > 1e-6)) if segment.size else 0
        amplitude = float(np.max(np.diff(segment))) if segment.size > 1 else 0.0
        resultat[nom] = {
            "seuil_de_lavage": seuil,
            "P_a_l_nul": float(b[0]),
            "nombre_de_remontees": remontees,
            "plus_grande_remontee": amplitude,
            "remontee_relative": float(
                amplitude / max(segment.max() - segment.min(), 1e-12)
            ) if segment.size > 1 else 0.0,
            "non_monotone": bool(
                remontees > 0 and segment.size > 1
                and amplitude / max(segment.max() - segment.min(), 1e-12)
                >= REMONTEE_RELATIVE_MINIMALE
            ),
        }
    return {
        "par_variante": resultat,
        "variantes_non_monotones": sorted(
            n for n, v in resultat.items() if v["non_monotone"]
        ),
        "lecture": (
            "Une variante non monotone est un domaine où augmenter la perte "
            "augmente la biomasse finale — donc où réduire la perte la "
            "diminue. C'est l'item 14 du WP-S2."
        ),
    }


def c_bruit(rng, repetitions=40, **kw) -> dict:
    """Bruit démographique et bruit environnemental coloré."""
    resultat = {}
    for nom, (bruit, tau) in (("demographique", (0.05, 0.0)),
                              ("environnemental_colore", (0.05, 25.0))):
        par_l = {}
        for l in (0.0, 0.2, 0.4, 0.6, 0.8):
            survies = []
            for _ in range(repetitions):
                champ, y0, indice = variantes(l, rng, **kw)["base"]
                final, _ = _integrer(champ, y0, t_fin=600.0, rng=rng,
                                     bruit=bruit, tau_bruit=tau)
                survies.append(final[indice] > 1e-6)
            par_l[str(l)] = float(np.mean(survies))
        resultat[nom] = par_l
    return {
        "fraction_de_survie_par_perte": resultat,
        "repetitions": repetitions,
        "lecture": (
            "Sous bruit, le seuil de lavage cesse d'être net : la survie "
            "devient une probabilité. Le test déterministe 11/11 ne dit rien "
            "de ce régime."
        ),
    }


def d_recherche_systematique(rng, tirages=400, **_) -> dict:
    """Item 14 : balayage aléatoire à la recherche de non-monotonie."""
    grille = np.linspace(0.0, 1.0, 41)
    trouvailles = []
    for _ in range(tirages):
        kw = dict(
            mu_max=float(rng.uniform(0.6, 1.6)),
            K_s=float(rng.uniform(0.3, 2.5)),
            D=float(rng.uniform(0.1, 0.5)),
            S_in=float(rng.uniform(4.0, 20.0)),
            decay=float(rng.uniform(0.01, 0.15)),
        )
        for nom in ("predation", "cross_feeding", "competition"):
            biomasses = []
            for l in grille:
                champ, y0, indice = variantes(float(l), rng, **kw)[nom]
                final, ok = _integrer(champ, y0, t_fin=3000.0)
                biomasses.append(float(final[indice]) if ok else 0.0)
            b = np.asarray(biomasses)
            vivants = b > 1e-6
            if vivants.sum() < 3:
                continue
            segment = b[vivants]
            croissances = np.diff(segment)
            etendue = max(float(segment.max() - segment.min()), 1e-12)
            relative = float(np.max(croissances, initial=0.0)) / etendue
            if relative >= REMONTEE_RELATIVE_MINIMALE:
                trouvailles.append({
                    "variante": nom,
                    "parametres": kw,
                    "plus_grande_remontee": float(np.max(croissances)),
                    "remontee_relative": relative,
                    "P_min": float(segment.min()),
                    "P_max": float(segment.max()),
                })
    par_variante = {}
    for nom in ("predation", "cross_feeding", "competition"):
        par_variante[nom] = sum(1 for t in trouvailles if t["variante"] == nom)
    return {
        "tirages_de_parametres": tirages,
        "cas_non_monotones_trouves": len(trouvailles),
        "par_variante": par_variante,
        "trois_exemples": trouvailles[:3],
        "lecture": (
            "Zéro cas trouvé signifierait que « réduire une perte peut nuire » "
            "n'a aucun domaine de validité dans ces structures, et que le "
            "résultat 11/11 ne dit rien de plus que la théorie du chémostat."
        ),
    }


# ==========================================================================

def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--graine", type=int, default=20260801)
    parseur.add_argument("--tirages", type=int, default=400)
    arguments = parseur.parse_args()

    SORTIE.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(arguments.graine)
    rapport = {"graine": arguments.graine}

    print("[S2] A cinétiques ...", flush=True)
    rapport["A_cinetiques"] = a_cinetiques(**BASE)
    print("[S2] B extensions structurelles ...", flush=True)
    rapport["B_extensions"] = b_extensions(rng, **BASE)
    print("[S2] C bruit ...", flush=True)
    rapport["C_bruit"] = c_bruit(rng, **BASE)
    print("[S2] D recherche systématique ...", flush=True)
    rapport["D_recherche_item_14"] = d_recherche_systematique(
        rng, arguments.tirages)

    (SORTIE / "portee_wp_s2.json").write_text(
        json.dumps(rapport, indent=2, ensure_ascii=False, default=float),
        encoding="utf-8",
    )
    print("écrit :", SORTIE / "portee_wp_s2.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
