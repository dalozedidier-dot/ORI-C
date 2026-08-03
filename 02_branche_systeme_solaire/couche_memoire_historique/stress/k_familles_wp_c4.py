"""Familles de modèles à budget égal — WP-C4 du plan directeur.

« Comparer chaque famille à complexité, budget d'optimisation et données
égales. »

Le verdict de la couche mémoire oppose M2 à trois modèles de la même famille.
Le WP-C4 demande de le confronter à des familles entièrement différentes. Sept
sont exécutables sur les données présentes.

    lineaire_AR1        filtre linéaire à un retard
    lineaire_ARX2       deux retards
    retards_distribues  trois noyaux exponentiels, constantes ajustées
    espace_etat         deux états latents linéaires
    seuils              coefficient de forçage commuté par un seuil
    bilan_energetique   relaxation unique vers l'équilibre radiatif
    persistance         y[t] = y[t-1], témoin trivial

Toutes sont ajustées sur la même fenêtre, avec le même budget d'optimisation,
et **prédisent en roue libre** hors échantillon — sans réinjecter
l'observation, exactement comme M0 à M1P. Sans cela la comparaison serait
truquée en faveur des modèles autorégressifs.

Exécution : `python k_familles_wp_c4.py`
"""

from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution

from core import OUTPUT_ROOT, effective_sample_size, fit_best_of_seeds, rmse, simulate
from g_tests_reels_2 import BUDGET, GRAINES, MODELES, charger, normaliser

OUT = OUTPUT_ROOT / "tests_reels"
BUDGET_DE = {"maxiter": 400, "popsize": 16, "tol": 1e-8, "seed": 20260801,
             "polish": True}


# --------------------------------------------------------------------------
# Les sept familles. Chacune renvoie la trajectoire complète en roue libre.

def _noyau_exponentiel(forcage, tau):
    """Convolution causale avec exp(-t/tau), calculée récursivement."""
    sortie = np.empty_like(forcage)
    etat = 0.0
    alpha = np.exp(-1.0 / max(tau, 1e-6))
    for i, valeur in enumerate(forcage):
        etat = alpha * etat + (1.0 - alpha) * valeur
        sortie[i] = etat
    return sortie


def simuler_famille(nom, theta, forcage, y0):
    n = len(forcage)
    y = np.empty(n)

    if nom == "lineaire_AR1":
        a, b, c = theta
        y[0] = y0
        for t in range(1, n):
            y[t] = a * y[t - 1] + b * forcage[t] + c
        return y

    if nom == "lineaire_ARX2":
        a1, a2, b, c = theta
        y[0] = y[1] = y0
        for t in range(2, n):
            y[t] = a1 * y[t - 1] + a2 * y[t - 2] + b * forcage[t] + c
        return y

    if nom == "retards_distribues":
        t1, t2, t3, w1, w2, w3, c = theta
        return (w1 * _noyau_exponentiel(forcage, t1)
                + w2 * _noyau_exponentiel(forcage, t2)
                + w3 * _noyau_exponentiel(forcage, t3) + c)

    if nom == "espace_etat":
        a1, a2, b1, b2, c1, c2, d = theta
        x1 = x2 = 0.0
        for t in range(n):
            x1 = a1 * x1 + b1 * forcage[t]
            x2 = a2 * x2 + b2 * forcage[t]
            y[t] = c1 * x1 + c2 * x2 + d
        return y

    if nom == "seuils":
        a, b_bas, b_haut, seuil, c = theta
        y[0] = y0
        for t in range(1, n):
            b = b_bas if y[t - 1] < seuil else b_haut
            y[t] = a * y[t - 1] + b * forcage[t] + c
        return y

    if nom == "bilan_energetique":
        tau, gain, c = theta
        etat = y0
        alpha = np.exp(-1.0 / max(tau, 1e-6))
        for t in range(n):
            etat = alpha * etat + (1.0 - alpha) * (gain * forcage[t] + c)
            y[t] = etat
        return y

    if nom == "persistance":
        return np.full(n, y0)

    raise ValueError(nom)


BORNES = {
    "lineaire_AR1": [(-1.2, 1.2), (-5.0, 5.0), (-5.0, 5.0)],
    "lineaire_ARX2": [(-1.5, 1.5), (-1.5, 1.5), (-5.0, 5.0), (-5.0, 5.0)],
    "retards_distribues": [(1.0, 20.0), (20.0, 120.0), (120.0, 800.0),
                           (-5.0, 5.0), (-5.0, 5.0), (-5.0, 5.0), (-5.0, 5.0)],
    "espace_etat": [(0.0, 0.999), (0.0, 0.999), (-2.0, 2.0), (-2.0, 2.0),
                    (-5.0, 5.0), (-5.0, 5.0), (-5.0, 5.0)],
    "seuils": [(-1.2, 1.2), (-5.0, 5.0), (-5.0, 5.0), (-3.0, 3.0), (-5.0, 5.0)],
    "bilan_energetique": [(1.0, 500.0), (-5.0, 5.0), (-5.0, 5.0)],
    "persistance": [],
}


def ajuster_famille(nom, forcage, observe, masque):
    y0 = float(observe[0])
    bornes = BORNES[nom]
    if not bornes:
        return np.array([]), simuler_famille(nom, [], forcage, y0)

    def cout(theta):
        predit = simuler_famille(nom, theta, forcage, y0)
        if not np.all(np.isfinite(predit)):
            return 1e12
        return float(np.mean((predit[masque] - observe[masque]) ** 2))

    resultat = differential_evolution(cout, bornes, **BUDGET_DE)
    return resultat.x, simuler_famille(nom, resultat.x, forcage, y0)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    donnees = charger()
    age = donnees["age"]
    masque = age >= 1200
    prediction = ~masque
    observe, forcage = normaliser(donnees["observe"], donnees["forcage"],
                                  masque)
    o = observe[prediction]
    n = int(prediction.sum())

    lignes = []

    # --- Les quatre modèles ORI-C, pour référence ---
    print("[C4] modèles ORI-C ...", flush=True)
    for modele in MODELES:
        meilleur, _ = fit_best_of_seeds(
            modele, forcage, observe, masque, GRAINES,
            bounds_name="wide", **BUDGET,
        )
        p = simulate(modele, forcage, observe[0], meilleur.vector)[prediction]
        lignes.append({
            "famille": f"ORI-C {modele}",
            "parametres": len(meilleur.vector),
            "rmse": rmse(o, p),
            "correlation": float(np.corrcoef(o, p)[0, 1]),
            "n_eff": float(effective_sample_size(o - p)),
        })
        print(f"     {modele} fait", flush=True)

    # --- Les sept familles concurrentes ---
    for nom in BORNES:
        depart = time.perf_counter()
        theta, complet = ajuster_famille(nom, forcage, observe, masque)
        p = complet[prediction]
        correlation = (float(np.corrcoef(o, p)[0, 1])
                       if np.std(p) > 1e-12 else float("nan"))
        lignes.append({
            "famille": nom,
            "parametres": len(theta),
            "rmse": rmse(o, p),
            "correlation": correlation,
            "n_eff": float(effective_sample_size(o - p)),
        })
        print(f"[C4] {nom} en {time.perf_counter() - depart:.0f} s "
              f"— RMSE {lignes[-1]['rmse']:.4f}", flush=True)

    frame = pd.DataFrame(lignes)
    frame["bic"] = n * np.log(np.maximum(frame.rmse ** 2, 1e-30)) \
        + frame.parametres * np.log(n)
    reference = float(frame.loc[frame.famille == "ORI-C M1P", "rmse"].iloc[0])
    frame["gain_sur_M1P"] = 1.0 - frame.rmse / reference
    frame = frame.sort_values("rmse")
    frame.to_csv(OUT / "k_familles_wp_c4.csv", index=False)

    meilleure = frame.iloc[0]
    rang_m2 = int(np.flatnonzero(frame.famille.to_numpy() == "ORI-C M2")[0]) + 1
    rapport = {
        "fenetre_calibration_ka": [2600, 1200],
        "fenetre_prediction_ka": [1200, 0],
        "familles": frame.to_dict("records"),
        "meilleure_famille": meilleure.famille,
        "rmse_meilleure": float(meilleure.rmse),
        "rang_de_M2_sur": [rang_m2, len(frame)],
        "M2_bat_une_famille_concurrente": bool(
            (frame.loc[frame.famille == "ORI-C M2", "rmse"].iloc[0]
             < frame.loc[~frame.famille.str.startswith("ORI-C"), "rmse"]).any()
        ),
        "lecture": (
            "Toutes les familles prédisent en roue libre sur la même fenêtre, "
            "avec le même budget. Le rang de M2 dans ce classement dit ce que "
            "la comparaison interne aux quatre modèles ORI-C ne pouvait pas "
            "dire."
        ),
    }
    (OUT / "k_familles_wp_c4.json").write_text(
        json.dumps(rapport, indent=2, ensure_ascii=False, default=float),
        encoding="utf-8",
    )
    print("\n" + frame.to_string(index=False))


if __name__ == "__main__":
    main()
