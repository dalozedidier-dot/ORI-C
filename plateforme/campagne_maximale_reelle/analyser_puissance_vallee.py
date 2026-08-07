#!/usr/bin/env python3
"""Puissance du critère de la vallée des rayons.

`vallee_des_rayons_exoplanetes.py` conclut `reussi: false` : le creux observé
n'atteint pas le quantile 0,95 exigé contre les permutations. Ce script répond à
la question que ce verdict ne pose pas : **ce critère peut-il seulement être
satisfait ?**

Il mesure la puissance empiriquement, par sous-échantillonnage du catalogue
réel. Pour chaque taille, il tire des sous-échantillons, applique exactement la
détection et le témoin du script d'origine — importés, non réécrits — et compte
la fraction qui franchit le seuil.

Il ne produit aucun verdict scientifique. Il dit si la question posée peut
recevoir une réponse.

    python plateforme/campagne_maximale_reelle/analyser_puissance_vallee.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ICI = Path(__file__).resolve().parent
SOURCE = ICI / "vallee_des_rayons_exoplanetes.py"
DONNEES = ICI / "data" / "exoplanet_observations.csv"
SORTIE = ICI / "resultats_consolides" / "PUISSANCE_VALLEE_DES_RAYONS.json"
TAILLES = (200, 400, 800, 1600)
TIRAGES_PAR_TAILLE = 40
PERMUTATIONS = 200
GRAINE = 20260808


def charger_module():
    """Importe le script d'origine pour réutiliser sa détection à l'identique."""
    specification = importlib.util.spec_from_file_location("vallee_source", SOURCE)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def main() -> int:
    source = charger_module()
    lignes = source.charger(DONNEES)
    rayons = []
    for ligne in lignes:
        try:
            rayon = float(ligne["radius_earth"])
        except (ValueError, KeyError):
            continue
        if source.BORNES[0] <= rayon <= source.BORNES[1]:
            rayons.append(rayon)
    rayons = np.array(rayons)

    fenetre = source.CRITERES["fenetre_du_creux_rayons_terrestres"]
    seuil = source.CRITERES["quantile_minimal_contre_permutations"]
    grille = np.logspace(
        np.log10(source.BORNES[0]), np.log10(source.BORNES[1]), 400
    )
    aleatoire = np.random.default_rng(GRAINE)

    def quantile(echantillon: np.ndarray) -> float:
        """Quantile du creux observé contre la nulle lisse, comme à l'origine."""
        _, profondeur = source.creux(
            grille, source.densite_lissee(echantillon, grille), fenetre
        )
        logs = np.log10(echantillon)
        nulles = []
        for _ in range(PERMUTATIONS):
            tirage = 10 ** aleatoire.uniform(logs.min(), logs.max(), len(echantillon))
            nulles.append(
                source.creux(grille, source.densite_lissee(tirage, grille), fenetre)[1]
            )
        return float((np.array(nulles) < profondeur).mean())

    _, profondeur_totale = source.creux(
        grille, source.densite_lissee(rayons, grille), fenetre
    )
    mesures = []
    print(f"{len(rayons)} planètes dans [{source.BORNES[0]}, {source.BORNES[1]}] R⊕")
    print(f"profondeur du creux sur le catalogue entier : {profondeur_totale:.6f}")
    print(f"seuil exigé : quantile >= {seuil}")
    print()
    for taille in TAILLES:
        if taille > len(rayons):
            continue
        succes = 0
        for _ in range(TIRAGES_PAR_TAILLE):
            echantillon = aleatoire.choice(rayons, taille, replace=False)
            if quantile(echantillon) >= seuil:
                succes += 1
        puissance = succes / TIRAGES_PAR_TAILLE
        mesures.append(
            {"taille": taille, "tirages": TIRAGES_PAR_TAILLE, "succes": succes,
             "puissance": puissance}
        )
        print(f"  n={taille:5d} : {succes:2d}/{TIRAGES_PAR_TAILLE} succès  "
              f"-> puissance {puissance:.2f}")

    atteignable = any(m["puissance"] > 0 for m in mesures)
    rapport = {
        "protocol_id": "VALLEE-DES-RAYONS-PUISSANCE",
        "genere_par": "plateforme/campagne_maximale_reelle/analyser_puissance_vallee.py",
        "source_de_la_detection": "vallee_des_rayons_exoplanetes.py, fonctions importées telles quelles",
        "planetes_retenues": int(len(rayons)),
        "profondeur_du_creux_catalogue_entier": profondeur_totale,
        "seuil_exige": seuil,
        "permutations_par_evaluation": PERMUTATIONS,
        "graine": GRAINE,
        "mesures": mesures,
        "critere_atteignable": atteignable,
        "conclusion": (
            "Le critère est franchi au moins une fois."
            if atteignable
            else "Le critère n'est franchi à aucune taille disponible. Le verdict "
                 "`reussi: false` du test d'origine ne mesure donc pas l'absence "
                 "de vallée des rayons : il constate qu'un seuil inatteignable "
                 "n'a pas été atteint."
        ),
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    with SORTIE.open("w", encoding="utf-8", newline="") as flux:
        flux.write(json.dumps(rapport, ensure_ascii=False, indent=2) + "\n")
    print()
    print(rapport["conclusion"])
    print(f"écrit : {SORTIE.relative_to(ICI.parents[1])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
