"""Seconde batterie sur données réelles : robustesse du verdict.

La première batterie mesurait des planchers d'interprétation. Celle-ci
attaque le verdict lui-même, sur quatre angles qui peuvent le renverser.

  G1  Validation croisée par blocs. Le verdict reposait sur un découpage
      unique à 1200 ka. Cinq blocs contigus donnent une distribution de gains
      au lieu d'un nombre, et disent si la fenêtre choisie était favorable.
  G2  Renversement temporel. Une mémoire physique est causale, donc
      asymétrique dans le temps. Un modèle dont la mémoire porte une
      information directionnelle doit ajuster la série vraie mieux que la
      série retournée. Un modèle sans mémoire doit être indifférent.
  G3  Convention d'insolation. 65°N au solstice est un choix. Le verdict
      survit-il à d'autres latitudes et à la moyenne annuelle ?
  G4  Distribution nulle par surrogates de Fourier. Le gain observé se
      distingue-t-il de celui qu'on obtient sur des séries de même spectre
      mais de phases aléatoires ?

Tous les tests comparent M2 à M1P, témoin de complexité égale.
"""

from __future__ import annotations

import json
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
    fourier_surrogate,
    moving_block_bootstrap_gain,
    rmse,
    simulate,
)
from oric_memory_tests.data import daily_mean_insolation, load_la2004, load_lr04

OUT = OUTPUT_ROOT / "tests_reels"
MODELES = ("M0", "M1", "M2", "M1P")
BUDGET = {"max_iterations": 600, "population_size": 16, "tol": 1e-8}
GRAINES = [729, 766, 803, 840]
DEBUT_KA = 2600.0


def charger(latitude: float = 65.0, longitude_solaire: float = np.pi / 2.0):
    """Grille commune à 1 ka sur 2,6 Ma, données réelles."""
    brut = PROJECT_ROOT / "data" / "raw"
    lr04 = load_lr04(brut / "lisiecki2005-d18o-stack-noaa.txt")
    orbital = load_la2004(brut / "INSOLN.LA2004.BTL.ASC").sort_values(
        "time_kyr_j2000"
    )
    age = np.arange(DEBUT_KA, -1.0, -1.0, dtype=float)
    temps = orbital["time_kyr_j2000"].to_numpy()
    demande = -age
    excentricite = np.interp(demande, temps, orbital["eccentricity"])
    obliquite = np.interp(demande, temps, orbital["obliquity_rad"])
    varpi = np.interp(demande, temps, orbital["varpi_rad"])
    insolation = daily_mean_insolation(
        latitude, longitude_solaire, excentricite, obliquite, varpi
    )
    return {
        "age": age,
        "observe": np.interp(age, lr04["age_calkaBP"], lr04["d18O_benthic"]),
        "forcage": insolation,
    }


def insolation_moyenne_annuelle(latitude: float = 65.0):
    """Moyenne sur douze longitudes solaires, autre convention de forçage."""
    parts = [
        charger(latitude, longitude)["forcage"]
        for longitude in np.linspace(0.0, 2.0 * np.pi, 12, endpoint=False)
    ]
    base = charger(latitude)
    base["forcage"] = np.mean(parts, axis=0)
    return base


def normaliser(observe, forcage, masque):
    o = (observe - observe[masque].mean()) / observe[masque].std()
    f = (forcage - forcage[masque].mean()) / forcage[masque].std()
    return o, f


def ajuster(observe, forcage, masque, modeles=MODELES):
    """Ajuste sur `masque` et renvoie la trajectoire complète simulée."""
    sortie = {}
    for modele in modeles:
        meilleur, _ = fit_best_of_seeds(
            modele, forcage, observe, masque, GRAINES,
            bounds_name="wide", **BUDGET,
        )
        sortie[modele] = simulate(modele, forcage, observe[0], meilleur.vector)
    return sortie


# --------------------------------------------------------------------------

def g1_validation_croisee_par_blocs(nb_blocs: int = 5) -> dict:
    """Le verdict dépend-il du découpage unique à 1200 ka ?"""
    donnees = charger()
    observe_brut, forcage_brut = donnees["observe"], donnees["forcage"]
    n = len(observe_brut)
    frontieres = np.linspace(0, n, nb_blocs + 1).astype(int)

    lignes = []
    for bloc in range(nb_blocs):
        test = np.zeros(n, dtype=bool)
        test[frontieres[bloc]:frontieres[bloc + 1]] = True
        entrainement = ~test
        observe, forcage = normaliser(observe_brut, forcage_brut, entrainement)
        predits = ajuster(observe, forcage, entrainement)
        o = observe[test]
        ligne = {
            "bloc": bloc,
            "age_debut_ka": float(donnees["age"][frontieres[bloc]]),
            "age_fin_ka": float(donnees["age"][frontieres[bloc + 1] - 1]),
            "points": int(test.sum()),
        }
        for modele in MODELES:
            ligne[f"rmse_{modele}"] = rmse(o, predits[modele][test])
        lignes.append(ligne)
        print(f"   bloc {bloc} : {ligne['age_debut_ka']:.0f}-"
              f"{ligne['age_fin_ka']:.0f} ka fait", flush=True)

    frame = pd.DataFrame(lignes)
    frame["gain_relatif_M2_sur_M1"] = 1.0 - frame.rmse_M2 / frame.rmse_M1
    frame["gain_relatif_M2_sur_M1P"] = 1.0 - frame.rmse_M2 / frame.rmse_M1P
    frame.to_csv(OUT / "g1_validation_croisee.csv", index=False)

    gains_m1p = frame["gain_relatif_M2_sur_M1P"].to_numpy()
    gains_m1 = frame["gain_relatif_M2_sur_M1"].to_numpy()
    return {
        "nb_blocs": nb_blocs,
        "par_bloc": frame.to_dict("records"),
        "gain_M2_sur_M1P": {
            "moyen": float(gains_m1p.mean()),
            "median": float(np.median(gains_m1p)),
            "min": float(gains_m1p.min()),
            "max": float(gains_m1p.max()),
            "blocs_favorables_a_M2": int((gains_m1p > 0).sum()),
        },
        "gain_M2_sur_M1": {
            "moyen": float(gains_m1.mean()),
            "blocs_favorables_a_M2": int((gains_m1 > 0).sum()),
        },
        "lecture": (
            "Un verdict qui change de signe selon le bloc n'est pas un verdict. "
            "Le compte de blocs favorables est la quantité décisive."
        ),
    }


def g2_renversement_temporel() -> dict:
    """Une mémoire causale doit distinguer le sens du temps."""
    donnees = charger()
    n = len(donnees["observe"])
    masque = np.zeros(n, dtype=bool)
    masque[: int(0.55 * n)] = True   # même proportion dans les deux sens

    resultat = {}
    for sens in ("avant", "arriere"):
        if sens == "avant":
            obs_brut, for_brut = donnees["observe"], donnees["forcage"]
        else:
            obs_brut = donnees["observe"][::-1].copy()
            for_brut = donnees["forcage"][::-1].copy()
        observe, forcage = normaliser(obs_brut, for_brut, masque)
        predits = ajuster(observe, forcage, masque)
        resultat[sens] = {
            modele: rmse(observe[masque], predits[modele][masque])
            for modele in MODELES
        }
        print(f"   sens {sens} fait", flush=True)

    asymetrie = {
        modele: resultat["arriere"][modele] - resultat["avant"][modele]
        for modele in MODELES
    }
    return {
        "rmse_ajustement": resultat,
        "asymetrie_temporelle": asymetrie,
        "asymetrie_relative": {
            m: float(asymetrie[m] / resultat["avant"][m]) for m in MODELES
        },
        "M2_plus_directionnel_que_M1P": bool(
            asymetrie["M2"] > asymetrie["M1P"]
        ),
        "lecture": (
            "L'asymétrie est mesurée sur l'ajustement, pas sur la prédiction : "
            "la question est de savoir si la structure du modèle capte une "
            "information de direction, pas s'il prédit mieux. Une asymétrie "
            "de M2 non supérieure à celle de M1P signifie que sa mémoire ne "
            "porte pas d'information directionnelle propre."
        ),
    }


def g3_convention_insolation() -> dict:
    """Le verdict survit-il au choix de latitude et de saison ?"""
    conventions = {
        "60N_solstice": lambda: charger(60.0),
        "65N_solstice": lambda: charger(65.0),
        "70N_solstice": lambda: charger(70.0),
        "65N_moyenne_annuelle": lambda: insolation_moyenne_annuelle(65.0),
    }
    lignes = []
    for nom, source in conventions.items():
        donnees = source()
        masque = donnees["age"] >= 1200
        prediction = ~masque
        observe, forcage = normaliser(donnees["observe"], donnees["forcage"],
                                      masque)
        predits = ajuster(observe, forcage, masque)
        o = observe[prediction]
        ligne = {"convention": nom}
        for modele in MODELES:
            ligne[f"rmse_{modele}"] = rmse(o, predits[modele][prediction])
        ligne["gain_M2_sur_M1P"] = 1.0 - ligne["rmse_M2"] / ligne["rmse_M1P"]
        ligne["gain_M2_sur_M1"] = 1.0 - ligne["rmse_M2"] / ligne["rmse_M1"]
        lignes.append(ligne)
        print(f"   convention {nom} faite", flush=True)

    frame = pd.DataFrame(lignes)
    frame.to_csv(OUT / "g3_convention_insolation.csv", index=False)
    signes = np.sign(frame["gain_M2_sur_M1P"].to_numpy())
    return {
        "par_convention": frame.to_dict("records"),
        "verdict_stable": bool(len(set(signes.tolist())) == 1),
        "conventions_favorables_a_M2": int((signes > 0).sum()),
        "lecture": (
            "Si le signe du gain change avec la latitude ou la saison, le "
            "résultat mesure la convention et non le modèle."
        ),
    }


def g4_distribution_nulle(nb_surrogates: int = 12) -> dict:
    """Le gain observé sort-il de la distribution nulle de même spectre ?"""
    donnees = charger()
    masque = donnees["age"] >= 1200
    prediction = ~masque
    observe, forcage = normaliser(donnees["observe"], donnees["forcage"],
                                  masque)
    duo = ("M2", "M1P")
    predits = ajuster(observe, forcage, masque, duo)
    o = observe[prediction]
    gain_observe = 1.0 - (
        rmse(o, predits["M2"][prediction])
        / rmse(o, predits["M1P"][prediction])
    )

    aleatoire = np.random.default_rng(4242)
    gains = []
    for tirage in range(nb_surrogates):
        cible = fourier_surrogate(observe, aleatoire)
        cible = (cible - cible[masque].mean()) / cible[masque].std()
        faux = ajuster(cible, forcage, masque, duo)
        c = cible[prediction]
        gains.append(1.0 - (
            rmse(c, faux["M2"][prediction]) / rmse(c, faux["M1P"][prediction])
        ))
        print(f"   surrogate {tirage + 1}/{nb_surrogates} : "
              f"gain {gains[-1]:+.4f}", flush=True)

    gains = np.asarray(gains)
    return {
        "nb_surrogates": nb_surrogates,
        "gain_observe": float(gain_observe),
        "nulle_moyenne": float(gains.mean()),
        "nulle_ecart_type": float(gains.std(ddof=1)),
        "nulle_min": float(gains.min()),
        "nulle_max": float(gains.max()),
        "p_unilaterale_gain_superieur": float(
            (np.sum(gains >= gain_observe) + 1) / (nb_surrogates + 1)
        ),
        "gains_nuls": gains.tolist(),
        "lecture": (
            "La cible est remplacée par une série de même spectre et de phases "
            "aléatoires. Si le gain observé tombe dans cette distribution, il "
            "ne provient pas de la structure temporelle de l'archive."
        ),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fichier = OUT / "g_tests_reels_2.json"
    rapport = {}
    for nom, fonction in (
        ("G1_validation_croisee", g1_validation_croisee_par_blocs),
        ("G2_renversement_temporel", g2_renversement_temporel),
        ("G3_convention_insolation", g3_convention_insolation),
        ("G4_distribution_nulle", g4_distribution_nulle),
    ):
        depart = time.perf_counter()
        print(f"[réel-2] {nom} ...", flush=True)
        rapport[nom] = fonction()
        print(f"[réel-2] {nom} terminé en "
              f"{time.perf_counter() - depart:.0f} s", flush=True)
        fichier.write_text(
            json.dumps(rapport, indent=2, ensure_ascii=False, default=float),
            encoding="utf-8",
        )
    print(json.dumps(rapport, indent=2, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
