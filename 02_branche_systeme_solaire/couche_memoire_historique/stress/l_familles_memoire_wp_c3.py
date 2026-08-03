"""Familles alternatives de mémoire — WP-C3 du plan directeur.

M2 place sa mémoire dans un seul mécanisme. Le WP-C3 en énumère seize et
demande que chacun reçoive : un témoin instantané, un témoin de complexité
égale, une ablation, une prédiction hors échantillon et une fenêtre longue.

Sept mécanismes sont implémentables sur LR04 et l'insolation seules. Les neuf
autres — carbone océanique, circulation, sédiments, poussières, méthane,
végétation, plateformes glaciaires — exigent des séries que le dossier ne
contient pas.

Structure commune, pour que la comparaison soit à structure égale :

    dy/dt = (gain · forçage − y) / tau_rapide + beta · s
    ds/dt = (moteur − s) / tau_lent

Seul `moteur` change d'un mécanisme à l'autre. Trois variantes par mécanisme :

    complet     `moteur` dépend de la réponse passée — mémoire ORI-C
    ablation    beta = 0, la mémoire est débranchée
    apparie     `moteur` est une fonction du forçage externe, **normalisée
                pour occuper la même plage d'exploitation** que le moteur
                qu'elle remplace

La normalisation est calculée sur la fenêtre de calibration, indépendamment du
point testé, et les plages sont publiées. C'est l'exigence du §6.1 du
`PROTOCOLE_DONNEES.md`, née du témoin mal apparié du test prospectif.

Exécution : `python l_familles_memoire_wp_c3.py`
"""

from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution

from core import OUTPUT_ROOT, effective_sample_size, rmse
from g_tests_reels_2 import charger, normaliser

OUT = OUTPUT_ROOT / "tests_reels"
BUDGET_DE = {"maxiter": 300, "popsize": 14, "tol": 1e-8, "seed": 20260801,
             "polish": True}

# gain, tau_rapide, beta, tau_lent, echelle_moteur, decalage
BORNES = [(-4.0, 4.0), (1.0, 60.0), (-2.0, 2.0), (5.0, 600.0),
          (-4.0, 4.0), (-3.0, 3.0)]

MECANISMES = {
    "volume_de_glace": "y",
    "erosion_du_regolithe": "|dy|",
    "alteration_continentale": "cumul(y)",
    "isostasie": "retard(y)",
    "seuil_de_calotte": "max(y,0)",
    "delais_distribues": "moyenne(y)",
    "couplage_etat_dependant": "y*|dy|",
}


def moteur_de(nom, y, y_precedent, cumul, lent_auxiliaire):
    """Valeur instantanée du moteur du mécanisme, à partir de la réponse."""
    if nom == "volume_de_glace":
        return y
    if nom == "erosion_du_regolithe":
        return abs(y - y_precedent)
    if nom == "alteration_continentale":
        return cumul
    if nom == "isostasie":
        return lent_auxiliaire
    if nom == "seuil_de_calotte":
        return max(y, 0.0)
    if nom == "delais_distribues":
        return lent_auxiliaire
    if nom == "couplage_etat_dependant":
        return y * abs(y - y_precedent)
    raise ValueError(nom)


def simuler(nom, variante, theta, forcage, y0, echelle_apparie=None):
    """Renvoie (trajectoire, plage d'exploitation du moteur)."""
    gain, tau_r, beta, tau_l, echelle, decalage = theta
    if variante == "ablation":
        beta = 0.0
    n = len(forcage)
    y = np.empty(n)
    etat = y0
    s = 0.0
    auxiliaire = 0.0
    cumul = 0.0
    precedent = y0
    moteurs = np.empty(n)

    alpha_r = np.exp(-1.0 / max(tau_r, 1e-6))
    alpha_l = np.exp(-1.0 / max(tau_l, 1e-6))
    alpha_aux = np.exp(-1.0 / 30.0)

    for t in range(n):
        if variante == "apparie":
            # Moteur externe : fonction du forçage seul, remise à l'échelle
            # sur la plage mesurée du moteur qu'elle remplace.
            brut = echelle * forcage[t] + decalage
            if echelle_apparie is not None:
                centre, etendue = echelle_apparie
                brut = centre + etendue * np.tanh(brut)
            moteur = brut
        else:
            moteur = echelle * moteur_de(nom, etat, precedent, cumul,
                                         auxiliaire) + decalage
        moteurs[t] = moteur
        s = alpha_l * s + (1.0 - alpha_l) * moteur
        precedent = etat
        # La rétroaction est un **taux**, pas un incrément : sans le facteur
        # (1 - alpha_r) elle s'accumule à chaque pas et quatre mécanismes
        # sur sept divergeaient dès que beta était positif.
        etat = alpha_r * etat + (1.0 - alpha_r) * (gain * forcage[t] + beta * s)
        auxiliaire = alpha_aux * auxiliaire + (1.0 - alpha_aux) * etat
        cumul = 0.999 * cumul + 0.001 * etat
        y[t] = etat
        if not np.isfinite(etat) or abs(etat) > 1e6:
            return np.full(n, np.nan), (np.nan, np.nan)
    return y, (float(np.median(moteurs)), float(np.ptp(moteurs)))


def ajuster(nom, variante, forcage, observe, masque, echelle_apparie=None):
    y0 = float(observe[0])

    def cout(theta):
        predit, _ = simuler(nom, variante, theta, forcage, y0, echelle_apparie)
        if not np.all(np.isfinite(predit)):
            return 1e12
        return float(np.mean((predit[masque] - observe[masque]) ** 2))

    resultat = differential_evolution(cout, BORNES, **BUDGET_DE)
    predit, plage = simuler(nom, variante, resultat.x, forcage, y0,
                            echelle_apparie)
    return resultat.x, predit, plage


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    donnees = charger()
    age = donnees["age"]
    masque = age >= 1200
    prediction = ~masque
    observe, forcage = normaliser(donnees["observe"], donnees["forcage"],
                                  masque)
    o = observe[prediction]

    lignes = []
    plages = {}
    for nom in MECANISMES:
        depart = time.perf_counter()
        # 1. complet — la mémoire dépend de la réponse passée
        theta, predit, plage = ajuster(nom, "complet", forcage, observe, masque)
        plages[nom] = {"complet": {"mediane": plage[0], "etendue": plage[1]}}
        lignes.append({"mecanisme": nom, "variante": "complet",
                       "rmse": rmse(o, predit[prediction]),
                       "correlation": float(np.corrcoef(o, predit[prediction])[0, 1]),
                       "n_eff": float(effective_sample_size(o - predit[prediction]))})

        # 2. ablation — beta = 0
        _, predit_a, _ = ajuster(nom, "ablation", forcage, observe, masque)
        lignes.append({"mecanisme": nom, "variante": "ablation",
                       "rmse": rmse(o, predit_a[prediction]),
                       "correlation": float(np.corrcoef(o, predit_a[prediction])[0, 1]),
                       "n_eff": float(effective_sample_size(o - predit_a[prediction]))})

        # 3. apparié — moteur externe, plage imposée par celle du complet,
        #    mesurée sur la calibration seule.
        _, predit_c, plage_calib = ajuster(
            nom, "complet", forcage, observe, masque)
        cible = (plage_calib[0], max(plage_calib[1], 1e-6) / 2.0)
        _, predit_p, plage_p = ajuster(nom, "apparie", forcage, observe,
                                       masque, echelle_apparie=cible)
        plages[nom]["apparie"] = {"mediane": plage_p[0], "etendue": plage_p[1]}
        plages[nom]["rapport_des_etendues"] = (
            float(plage_p[1] / plage[1]) if plage[1] > 0 else None
        )
        lignes.append({"mecanisme": nom, "variante": "apparie",
                       "rmse": rmse(o, predit_p[prediction]),
                       "correlation": float(np.corrcoef(o, predit_p[prediction])[0, 1]),
                       "n_eff": float(effective_sample_size(o - predit_p[prediction]))})
        print(f"[C3] {nom} en {time.perf_counter() - depart:.0f} s", flush=True)

    frame = pd.DataFrame(lignes)
    pivot = frame.pivot(index="mecanisme", columns="variante", values="rmse")
    pivot["gain_sur_ablation"] = 1.0 - pivot.complet / pivot.ablation
    pivot["gain_sur_apparie"] = 1.0 - pivot.complet / pivot.apparie
    pivot = pivot.sort_values("gain_sur_apparie", ascending=False)
    pivot.to_csv(OUT / "l_familles_memoire_wp_c3.csv")

    rapport = {
        "mecanismes": {nom: MECANISMES[nom] for nom in MECANISMES},
        "fenetre_calibration_ka": [2600, 1200],
        "fenetre_prediction_ka": [1200, 0],
        "resultats": pivot.reset_index().to_dict("records"),
        "plages_d_exploitation": plages,
        "mecanismes_battant_leur_temoin_apparie": sorted(
            pivot.index[pivot.gain_sur_apparie > 0].tolist()
        ),
        "mecanismes_battant_leur_ablation": sorted(
            pivot.index[pivot.gain_sur_ablation > 0].tolist()
        ),
        "lecture": (
            "Un mécanisme n'est retenu que s'il bat à la fois son ablation et "
            "son témoin apparié. Les plages d'exploitation sont publiées pour "
            "que l'appariement soit vérifiable, conformément au §6.1 du "
            "PROTOCOLE_DONNEES."
        ),
    }
    (OUT / "l_familles_memoire_wp_c3.json").write_text(
        json.dumps(rapport, indent=2, ensure_ascii=False, default=float),
        encoding="utf-8",
    )
    print("\n" + pivot.to_string())


if __name__ == "__main__":
    main()
