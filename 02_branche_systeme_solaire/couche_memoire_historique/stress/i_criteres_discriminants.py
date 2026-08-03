"""Critères discriminants de la couche mémoire — WP-C6 du plan directeur.

Le verdict de la couche mémoire repose sur une seule métrique : la RMSE hors
échantillon. Le plan directeur en demande quinze, mesurées séparément. Sept
sont exécutables sur les données présentes et n'ont jamais été calculées.

    C6.2  log-vraisemblance prédictive
    C6.3  calibration probabiliste
    C6.4  corrélation et phase
    C6.5  spectre 41, 100 et **405 ka** — cette dernière bande n'a jamais
          été regardée, alors qu'elle porte la modulation d'excentricité
          la plus stable du système solaire
    C6.6  chronologie des terminaisons
    C6.7  stabilité des paramètres entre sous-fenêtres
    C6.8  identifiabilité, dispersion entre graines

Un modèle peut être réfuté en RMSE et rester informatif sur l'une de ces
dimensions. L'inverse est aussi vrai. C'est ce que mesure ce script.

Exécution : `python i_criteres_discriminants.py`
"""

from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd
from scipy.signal import detrend, find_peaks

from core import (
    OUTPUT_ROOT,
    effective_sample_size,
    fit_best_of_seeds,
    rmse,
    simulate,
)
from g_tests_reels_2 import BUDGET, GRAINES, MODELES, charger, normaliser

OUT = OUTPUT_ROOT / "tests_reels"
BANDES = {"41_ka": (39.0, 43.0), "100_ka": (80.0, 120.0),
          "405_ka": (360.0, 450.0)}
MINIMUM_DE_POINTS = 3


def puissance_par_bande(serie: np.ndarray, pas: float = 1.0) -> dict:
    """Puissance intégrée dans chaque bande, et part du total."""
    n = len(serie)
    frequences = np.fft.rfftfreq(n, d=pas)
    centre = detrend(serie - serie.mean(), type="linear")
    spectre = np.abs(np.fft.rfft(centre)) ** 2 / n
    spectre[1:-1 if n % 2 == 0 else None] *= 2.0
    positifs = frequences > 0
    periodes = np.divide(1.0, frequences, out=np.full_like(frequences, np.inf),
                         where=positifs)
    total = float(np.trapezoid(spectre[positifs], frequences[positifs]))
    sortie = {}
    for nom, (bas, haut) in BANDES.items():
        masque = (periodes >= bas) & (periodes <= haut)
        points = int(masque.sum())
        # Une bande contenant moins de trois points de fréquence n'est pas
        # résolue par la fenêtre : sa puissance n'est pas une mesure. Le cas
        # se produit pour 405 ka sur toute fenêtre plus courte que ~2 Ma.
        if points > 1:
            puissance = float(
                np.trapezoid(spectre[masque], frequences[masque])
            )
        elif points == 1:
            puissance = float(
                spectre[masque][0] * (frequences[1] - frequences[0])
            )
        else:
            puissance = 0.0
        sortie[nom] = puissance
        sortie[f"part_{nom}"] = puissance / total if total > 0 else 0.0
        sortie[f"points_de_frequence_{nom}"] = points
        sortie[f"resolue_{nom}"] = bool(points >= MINIMUM_DE_POINTS)
    sortie["duree_de_la_fenetre_ka"] = float(n * pas)
    return sortie


def terminaisons(serie: np.ndarray, age: np.ndarray, nombre: int = 8) -> list:
    """Dates des plus fortes déglaciations : chutes rapides de d18O."""
    # La série est en âge décroissant ; une terminaison est une baisse brutale.
    pente = np.gradient(serie)
    pics, proprietes = find_peaks(-pente, distance=40,
                                 height=float(np.std(pente)))
    if len(pics) == 0:
        return []
    ordre = np.argsort(-proprietes["peak_heights"])[:nombre]
    return sorted(float(age[pics[i]]) for i in ordre)


def appariement(observees: list, predites: list, tolerance: float = 20.0) -> dict:
    """Combien de terminaisons observées ont une prédite à moins de `tolerance`."""
    if not observees or not predites:
        return {"appariees": 0, "sur": len(observees), "ecart_median": None}
    ecarts = []
    appariees = 0
    for cible in observees:
        distance = min(abs(cible - p) for p in predites)
        ecarts.append(distance)
        if distance <= tolerance:
            appariees += 1
    return {
        "appariees": appariees,
        "sur": len(observees),
        "ecart_median": float(np.median(ecarts)),
        "tolerance_ka": tolerance,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    donnees = charger()
    age = donnees["age"]
    masque = age >= 1200
    prediction = ~masque
    observe, forcage = normaliser(donnees["observe"], donnees["forcage"],
                                  masque)

    rapport = {"fenetre_calibration_ka": [2600, 1200],
               "fenetre_prediction_ka": [1200, 0]}

    # --- Ajustement de référence, et dispersion entre graines (C6.8) ---
    print("[C6] ajustement de référence ...", flush=True)
    ajustes, dispersions = {}, {}
    for modele in MODELES:
        depart = time.perf_counter()
        meilleur, essais = fit_best_of_seeds(
            modele, forcage, observe, masque, GRAINES,
            bounds_name="wide", **BUDGET,
        )
        ajustes[modele] = simulate(modele, forcage, observe[0], meilleur.vector)
        vecteurs = np.array([e.vector for e in essais])
        etendue = vecteurs.max(axis=0) - vecteurs.min(axis=0)
        amplitude = np.abs(vecteurs).max(axis=0)
        relative = etendue / np.where(amplitude > 0, amplitude, 1.0)
        dispersions[modele] = {
            "graines": len(essais),
            "rmse_entrainement_min": float(min(e.training_rmse for e in essais)),
            "rmse_entrainement_max": float(max(e.training_rmse for e in essais)),
            "dispersion_relative_max": float(relative.max()),
            "dispersion_relative_mediane": float(np.median(relative)),
            "parametres_identifiables": bool(relative.max() < 0.10),
        }
        print(f"     {modele} en {time.perf_counter() - depart:.0f} s",
              flush=True)
    rapport["C6_8_identifiabilite"] = dispersions

    # --- C6.2 à C6.4 : vraisemblance, calibration, corrélation, phase ---
    o = observe[prediction]
    lignes = []
    for modele in MODELES:
        p = ajustes[modele][prediction]
        residu = o - p
        n_eff = effective_sample_size(residu)
        variance = float(np.var(residu, ddof=1))
        # Log-vraisemblance gaussienne, pénalisée par la taille efficace.
        log_v = -0.5 * n_eff * (np.log(2 * np.pi * variance) + 1.0)
        # Calibration : fraction des observations dans l'intervalle à 90 %.
        borne = 1.645 * np.sqrt(variance)
        couverture = float(np.mean(np.abs(residu) <= borne))
        # Phase : décalage maximisant la corrélation croisée.
        centre_o = o - o.mean()
        centre_p = p - p.mean()
        croisee = np.correlate(centre_o, centre_p, mode="full")
        decalage = int(np.argmax(croisee) - (len(o) - 1))
        lignes.append({
            "modele": modele,
            "rmse": rmse(o, p),
            "correlation": float(np.corrcoef(o, p)[0, 1]),
            "n_eff": float(n_eff),
            "log_vraisemblance_predictive": float(log_v),
            "couverture_a_90_pourcent": couverture,
            "ecart_de_calibration": abs(couverture - 0.90),
            "decalage_de_phase_ka": decalage,
        })
    frame = pd.DataFrame(lignes).set_index("modele")
    frame.to_csv(OUT / "i_criteres_discriminants.csv")
    rapport["C6_2_a_4_vraisemblance_calibration_phase"] = frame.to_dict("index")

    # --- C6.5 : trois bandes, dont 405 ka ---
    spectres = {"LR04": puissance_par_bande(o)}
    for modele in MODELES:
        spectres[modele] = puissance_par_bande(ajustes[modele][prediction])
    rapport["C6_5_bandes_spectrales"] = spectres

    # La bande de 405 ka n'est pas résolue par une fenêtre de 1200 ka. On la
    # remesure sur les 2600 ka complets, en signalant que la série y est
    # partiellement en échantillon.
    complets = {"LR04": puissance_par_bande(observe)}
    for modele in MODELES:
        complets[modele] = puissance_par_bande(ajustes[modele])
    rapport["C6_5_bandes_sur_fenetre_complete"] = {
        "avertissement": (
            "Fenêtre de 2600 ka : elle inclut la calibration. Ces valeurs ne "
            "sont pas hors échantillon et servent seulement à savoir si la "
            "bande de 405 ka est résolvable."
        ),
        "par_serie": complets,
    }

    # --- C6.6 : chronologie des terminaisons ---
    age_prediction = age[prediction]
    observees = terminaisons(o, age_prediction)
    chronologies = {"LR04": observees}
    appariements = {}
    for modele in MODELES:
        predites = terminaisons(ajustes[modele][prediction], age_prediction)
        chronologies[modele] = predites
        appariements[modele] = appariement(observees, predites)
    rapport["C6_6_terminaisons"] = {
        "dates_ka": chronologies,
        "appariement": appariements,
    }

    # --- C6.7 : stabilité des paramètres entre sous-fenêtres ---
    print("[C6] stabilité des paramètres ...", flush=True)
    bornes = [(2600, 2250), (2250, 1900), (1900, 1550), (1550, 1200)]
    stabilite = {}
    for modele in MODELES:
        vecteurs = []
        for haut, bas in bornes:
            sous = (age <= haut) & (age >= bas)
            o_sous, f_sous = normaliser(donnees["observe"], donnees["forcage"],
                                        sous)
            meilleur, _ = fit_best_of_seeds(
                modele, f_sous, o_sous, sous, GRAINES[:2],
                bounds_name="wide", **BUDGET,
            )
            vecteurs.append(meilleur.vector)
        vecteurs = np.array(vecteurs)
        etendue = vecteurs.max(axis=0) - vecteurs.min(axis=0)
        amplitude = np.abs(vecteurs).max(axis=0)
        relative = etendue / np.where(amplitude > 0, amplitude, 1.0)
        stabilite[modele] = {
            "sous_fenetres": len(bornes),
            "derive_relative_max": float(relative.max()),
            "derive_relative_mediane": float(np.median(relative)),
            "parametres_stables": bool(relative.max() < 0.25),
        }
        print(f"     {modele} fait", flush=True)
    rapport["C6_7_stabilite_des_parametres"] = stabilite

    (OUT / "i_criteres_discriminants.json").write_text(
        json.dumps(rapport, indent=2, ensure_ascii=False, default=float),
        encoding="utf-8",
    )
    print("écrit :", OUT / "i_criteres_discriminants.json")


if __name__ == "__main__":
    main()
