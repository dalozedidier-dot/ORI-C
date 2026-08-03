"""Batterie de tests sur données réelles, avec témoin de complexité égale.

Quatre tests que le dossier n'avait jamais exécutés, tous sur archives réelles
et non sur modèle interne.

  T1  Plancher d'incertitude de LR04. La pile publie une colonne d'erreur
      jamais utilisée. Un gain de RMSE inférieur à cette erreur n'est pas
      interprétable.
  T2  Enregistrement complet. LR04 couvre 5,32 Ma ; le protocole n'en
      utilisait que 2,6. Calibration sur 5,32-2,6 Ma, prédiction sur 2,6-0 Ma,
      la transition entière devenant hors échantillon.
  T3  Plancher de dispersion orbitale. Les quatre solutions La2010 sont toutes
      admissibles. Leur dispersion donne un plancher d'incertitude en entrée.
  T4  Chronologie spectrale. Le rapport 100/41 ka en fenêtre glissante mesure
      la date de la transition. Les modèles la placent-ils au bon endroit ?

Chaque test compare M2 à M1P, témoin de complexité égale.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd

from core import (
    OUTPUT_ROOT,
    PROJECT_ROOT,
    PowerRatio,
    effective_sample_size,
    fit_best_of_seeds,
    moving_block_bootstrap_gain,
    rmse,
    simulate,
)
from oric_memory_tests.data import daily_mean_insolation, load_la2004, load_lr04

OUT = OUTPUT_ROOT / "tests_reels"
MODELES = ("M0", "M1", "M2", "M1P")
BUDGET = {"max_iterations": 600, "population_size": 16, "tol": 1e-8}
GRAINES = [729, 766, 803, 840]


def charger(debut_ka: float, fin_ka: float = 0.0):
    """Grille commune à 1 ka sur la fenêtre demandée, données réelles."""
    brut = PROJECT_ROOT / "data" / "raw"
    lr04 = load_lr04(brut / "lisiecki2005-d18o-stack-noaa.txt")
    orbital = load_la2004(brut / "INSOLN.LA2004.BTL.ASC").sort_values(
        "time_kyr_j2000"
    )
    age = np.arange(debut_ka, fin_ka - 1, -1, dtype=float)
    temps = orbital["time_kyr_j2000"].to_numpy()
    demande = -age
    excentricite = np.interp(demande, temps, orbital["eccentricity"])
    obliquite = np.interp(demande, temps, orbital["obliquity_rad"])
    varpi = np.interp(demande, temps, orbital["varpi_rad"])
    insolation = daily_mean_insolation(
        65.0, np.pi / 2.0, excentricite, obliquite, varpi
    )
    return {
        "age": age,
        "observe": np.interp(age, lr04["age_calkaBP"], lr04["d18O_benthic"]),
        "erreur": np.interp(age, lr04["age_calkaBP"], lr04["d18O_error"]),
        "forcage": insolation,
        "excentricite": excentricite,
    }


def normaliser(observe, forcage, masque):
    o = (observe - observe[masque].mean()) / observe[masque].std()
    f = (forcage - forcage[masque].mean()) / forcage[masque].std()
    return o, f


def ajuster(observe, forcage, masque, modeles=MODELES):
    resultat = {}
    for modele in modeles:
        meilleur, _ = fit_best_of_seeds(
            modele, forcage, observe, masque, GRAINES,
            bounds_name="wide", **BUDGET,
        )
        resultat[modele] = simulate(modele, forcage, observe[0], meilleur.vector)
    return resultat


# --------------------------------------------------------------------------

def t1_plancher_incertitude() -> dict:
    """Le gain est-il plus grand que l'incertitude publiée de l'archive ?"""
    donnees = charger(2600.0)
    masque = donnees["age"] >= 1200
    prediction = ~masque
    observe, forcage = normaliser(donnees["observe"], donnees["forcage"], masque)
    echelle = float(donnees["observe"][masque].std())

    # L'erreur publiée, ramenée à l'échelle standardisée du test.
    erreur = donnees["erreur"][prediction] / echelle
    predits = ajuster(observe, forcage, masque)
    o = observe[prediction]

    lignes = []
    for modele in MODELES:
        lignes.append({
            "modele": modele,
            "rmse": rmse(o, predits[modele][prediction]),
        })
    frame = pd.DataFrame(lignes).set_index("modele")
    gain_m1 = frame.loc["M1", "rmse"] - frame.loc["M2", "rmse"]
    gain_m1p = frame.loc["M1P", "rmse"] - frame.loc["M2", "rmse"]

    return {
        "erreur_publiee_moyenne_standardisee": float(erreur.mean()),
        "erreur_publiee_mediane_standardisee": float(np.median(erreur)),
        "rmse_par_modele": frame["rmse"].to_dict(),
        "amelioration_absolue_M2_sur_M1": float(gain_m1),
        "amelioration_absolue_M2_sur_M1P": float(gain_m1p),
        "gain_M2_sur_M1_depasse_l_incertitude": bool(gain_m1 > erreur.mean()),
        "rapport_gain_sur_incertitude": float(gain_m1 / erreur.mean()),
        "lecture": (
            "Un écart de RMSE plus petit que l'incertitude publiée de l'archive "
            "ne peut pas être attribué au modèle."
        ),
    }


def t2_enregistrement_complet() -> dict:
    """LR04 couvre 5,32 Ma. Calibrer avant la transition, la prédire entière."""
    donnees = charger(5300.0)
    masque = donnees["age"] >= 2600
    prediction = ~masque
    observe, forcage = normaliser(donnees["observe"], donnees["forcage"], masque)
    predits = ajuster(observe, forcage, masque)
    o = observe[prediction]
    ratio = PowerRatio(int(prediction.sum()))
    cible = ratio(o)

    lignes = []
    for modele in MODELES:
        p = predits[modele][prediction]
        residu = o - p
        lignes.append({
            "modele": modele,
            "rmse": rmse(o, p),
            "correlation": float(np.corrcoef(o, p)[0, 1]),
            "rapport_100_41": float(ratio(p)),
            "n_eff": float(effective_sample_size(residu)),
        })
    frame = pd.DataFrame(lignes).set_index("modele")
    frame.to_csv(OUT / "t2_enregistrement_complet.csv")

    aleatoire = np.random.default_rng(11)
    bornes = {}
    for temoin in ("M1", "M1P"):
        tirages = moving_block_bootstrap_gain(
            o, predits[temoin][prediction], predits["M2"][prediction],
            block_length=170, draws=20000, rng=aleatoire,
        )
        bornes[temoin] = {
            "gain": float(1.0 - frame.loc["M2", "rmse"] / frame.loc[temoin, "rmse"]),
            "ic_2.5": float(np.percentile(tirages, 2.5)),
            "ic_97.5": float(np.percentile(tirages, 97.5)),
        }

    return {
        "calibration_ka": [5300, 2600],
        "prediction_ka": [2600, 0],
        "points_calibration": int(masque.sum()),
        "points_prediction": int(prediction.sum()),
        "metriques": frame.to_dict("index"),
        "rapport_100_41_observe": float(cible),
        "gains": bornes,
        "lecture": (
            "La transition du Pléistocène moyen est ici entièrement hors "
            "échantillon, ce que la fenêtre 2,6-1,2 Ma ne permettait pas."
        ),
    }


def t3_plancher_orbital() -> dict:
    """Dispersion entre quatre solutions orbitales toutes admissibles."""
    dossier = (
        PROJECT_ROOT.parent / "couche_astronomique" / "code"
        / "ORI-C_Systeme_solaire_tests" / "data" / "reference" / "la2010"
    )
    if not dossier.is_dir():
        return {"disponible": False, "motif": f"répertoire absent : {dossier}"}

    solutions = {}
    for nom in ("La2010a_ecc3.dat", "La2010b_ecc3.dat",
                "La2010c_ecc3.dat", "La2010d_ecc3.dat"):
        chemin = dossier / nom
        if not chemin.exists():
            continue
        valeurs = np.loadtxt(chemin)
        solutions[nom[:8]] = valeurs

    if len(solutions) < 2:
        return {"disponible": False, "motif": "moins de deux solutions lisibles"}

    # Fenêtre commune, 0 à 2600 ka, colonne 0 = temps en ka, colonne 1 = e.
    longueur = min(len(v) for v in solutions.values())
    fenetre = min(longueur, 2601)
    empilees = np.vstack([v[:fenetre, 1] for v in solutions.values()])
    dispersion = empilees.max(axis=0) - empilees.min(axis=0)

    return {
        "disponible": True,
        "solutions": sorted(solutions),
        "points_compares": int(fenetre),
        "dispersion_moyenne": float(dispersion.mean()),
        "dispersion_max": float(dispersion.max()),
        "excentricite_moyenne": float(empilees.mean()),
        "dispersion_relative_moyenne": float(
            dispersion.mean() / empilees.mean()
        ),
        "lecture": (
            "Quatre solutions orbitales également admissibles diffèrent de "
            "cette quantité. Aucun résultat dont l'effet est plus petit que "
            "cette dispersion ne peut être attribué à l'astronomie."
        ),
    }


def t4_chronologie_spectrale() -> dict:
    """Où les modèles placent-ils la transition, en fenêtre glissante ?"""
    donnees = charger(5300.0)
    masque = donnees["age"] >= 2600
    observe, forcage = normaliser(donnees["observe"], donnees["forcage"], masque)
    predits = ajuster(observe, forcage, masque)

    largeur = 800  # ka, assez large pour résoudre la bande de 100 ka
    pas = 50
    age = donnees["age"]
    ratio = PowerRatio(largeur + 1)

    lignes = []
    for debut in range(0, len(age) - largeur, pas):
        tranche = slice(debut, debut + largeur + 1)
        ligne = {"age_centre_ka": float(age[tranche].mean())}
        ligne["LR04"] = float(ratio(observe[tranche]))
        for modele in MODELES:
            ligne[modele] = float(ratio(predits[modele][tranche]))
        lignes.append(ligne)
    frame = pd.DataFrame(lignes)
    frame.to_csv(OUT / "t4_chronologie_spectrale.csv", index=False)

    def date_de_transition(colonne):
        """Âge où le rapport franchit 1 en remontant vers le présent."""
        valeurs = frame[colonne].to_numpy()
        ages = frame["age_centre_ka"].to_numpy()
        ordre = np.argsort(-ages)  # du plus ancien au plus récent
        v, a = valeurs[ordre], ages[ordre]
        franchissements = np.where((v[:-1] < 1.0) & (v[1:] >= 1.0))[0]
        return float(a[franchissements[0] + 1]) if len(franchissements) else None

    dates = {c: date_de_transition(c) for c in ["LR04", *MODELES]}
    return {
        "largeur_fenetre_ka": largeur,
        "pas_ka": pas,
        "date_de_transition_ka": dates,
        "rapport_max_par_serie": {
            c: float(frame[c].max()) for c in ["LR04", *MODELES]
        },
        "lecture": (
            "La date de franchissement du rapport 1 mesure la chronologie de la "
            "transition. Un modèle qui ne franchit jamais 1 ne la produit pas."
        ),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rapport = {}
    for nom, fonction in (
        ("T1_plancher_incertitude", t1_plancher_incertitude),
        ("T2_enregistrement_complet", t2_enregistrement_complet),
        ("T3_plancher_orbital", t3_plancher_orbital),
        ("T4_chronologie_spectrale", t4_chronologie_spectrale),
    ):
        depart = time.perf_counter()
        print(f"[réel] {nom} ...", flush=True)
        rapport[nom] = fonction()
        print(f"[réel] {nom} terminé en {time.perf_counter() - depart:.0f} s",
              flush=True)
        (OUT / "f_tests_reels.json").write_text(
            json.dumps(rapport, indent=2, ensure_ascii=False, default=float),
            encoding="utf-8",
        )
    print(json.dumps(rapport, indent=2, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
