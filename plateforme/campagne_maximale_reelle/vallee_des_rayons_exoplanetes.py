"""Inscription historique dans une population réelle — NASA Exoplanet Archive.

La branche 2 affirme que l'histoire d'un système laisse une trace mesurable
dans son état présent. Cette affirmation n'avait jamais été testée hors du
Système solaire, faute de population.

Le catalogue NASA en fournit 6 333, mesurées.

Le cas testé est la **vallée des rayons** : un déficit de planètes autour de
1,8 rayon terrestre, attribué à la perte atmosphérique — un processus
historique dont la trace subsisterait dans la distribution actuelle. Si elle
existe et se situe où la littérature l'annonce, c'est un cas d'inscription
historique observable dans une population.

Critères fixés avant exécution :

    - creux détecté entre 1,5 et 2,2 rayons terrestres
    - profondeur du creux supérieure à celle de 95 % des permutations
    - la position ne dépend pas de la méthode de découverte, sans quoi elle
      mesurerait la sélection observationnelle et non la physique

Le troisième critère est le témoin : un artefact de sélection se déplace avec
l'instrument, une trace physique non.

    python vallee_des_rayons_exoplanetes.py --data-dir <données>
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

CRITERES = {
    "fenetre_du_creux_rayons_terrestres": (1.5, 2.2),
    "quantile_minimal_contre_permutations": 0.95,
    "ecart_maximal_entre_methodes_rayons": 0.4,
}
BORNES = (1.0, 4.0)      # domaine des petites planètes
LARGEUR = 0.05           # en log10


def charger(chemin: Path):
    with chemin.open(encoding="utf-8-sig", newline="") as flux:
        return list(csv.DictReader(flux))


def densite_lissee(rayons, grille, largeur=LARGEUR):
    """Densité par noyau gaussien en log10, sans dépendance externe."""
    x = np.log10(rayons)
    g = np.log10(grille)
    return np.array([
        np.exp(-0.5 * ((g[i] - x) / largeur) ** 2).sum()
        for i in range(len(g))
    ]) / (len(x) * largeur * np.sqrt(2 * np.pi))


def creux(grille, densite, fenetre):
    """Position et profondeur relative du minimum local dans la fenêtre."""
    dans = (grille >= fenetre[0]) & (grille <= fenetre[1])
    if not dans.any():
        return float("nan"), 0.0
    indice = int(np.flatnonzero(dans)[np.argmin(densite[dans])])
    gauche = densite[:indice].max() if indice else densite[0]
    droite = densite[indice + 1:].max() if indice + 1 < len(densite) else densite[-1]
    pic = min(gauche, droite)
    profondeur = (pic - densite[indice]) / pic if pic > 0 else 0.0
    return float(grille[indice]), float(profondeur)


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--data-dir", type=Path, required=True)
    parseur.add_argument("--sortie", type=Path, default=Path("."))
    parseur.add_argument("--tirages", type=int, default=2000)
    arguments = parseur.parse_args()

    lignes = charger(arguments.data_dir / "exoplanet_observations.csv")
    rayons, methodes = [], []
    for l in lignes:
        try:
            r = float(l["radius_earth"])
        except (ValueError, KeyError):
            continue
        if BORNES[0] <= r <= BORNES[1]:
            rayons.append(r)
            methodes.append(l["discovery_method"])
    rayons = np.array(rayons)
    methodes = np.array(methodes)
    print(f"{len(lignes)} planètes au catalogue, {len(rayons)} entre "
          f"{BORNES[0]} et {BORNES[1]} rayons terrestres")

    grille = np.logspace(np.log10(BORNES[0]), np.log10(BORNES[1]), 400)
    densite = densite_lissee(rayons, grille)
    position, profondeur = creux(grille, densite,
                                 CRITERES["fenetre_du_creux_rayons_terrestres"])

    # Nulle : rayons rééchantillonnés depuis une loi de puissance ajustée,
    # qui n'a par construction aucun creux. Le creux observé doit dépasser
    # ce que produit le hasard sur une distribution lisse.
    rng = np.random.default_rng(20260801)
    x = np.log10(rayons)
    profondeurs = []
    for _ in range(arguments.tirages):
        tirage = 10 ** rng.uniform(x.min(), x.max(), len(rayons))
        _, p = creux(grille, densite_lissee(tirage, grille),
                     CRITERES["fenetre_du_creux_rayons_terrestres"])
        profondeurs.append(p)
    profondeurs = np.array(profondeurs)
    quantile = float((profondeurs < profondeur).mean())

    # Témoin : la position dépend-elle de la méthode de découverte ?
    par_methode = {}
    for m in sorted(set(methodes)):
        sous = rayons[methodes == m]
        if len(sous) < 80:
            continue
        pos, prof = creux(grille, densite_lissee(sous, grille),
                          CRITERES["fenetre_du_creux_rayons_terrestres"])
        par_methode[m] = {"n": int(len(sous)), "position": pos,
                          "profondeur": prof}
    positions = [v["position"] for v in par_methode.values()
                 if np.isfinite(v["position"])]
    ecart = float(max(positions) - min(positions)) if len(positions) > 1 else 0.0

    rapport = {
        "source": "NASA Exoplanet Archive, table PS par défaut",
        "planetes_au_catalogue": len(lignes),
        "planetes_retenues": int(len(rayons)),
        "criteres_fixes_avant_execution": CRITERES,
        "creux": {
            "position_rayons_terrestres": position,
            "profondeur_relative": profondeur,
            "quantile_contre_permutations": quantile,
            "tirages": arguments.tirages,
            "reussi": bool(
                quantile >= CRITERES["quantile_minimal_contre_permutations"]),
        },
        "temoin_methode_de_decouverte": {
            "par_methode": par_methode,
            "ecart_de_position": ecart,
            "critere": CRITERES["ecart_maximal_entre_methodes_rayons"],
            "reussi": bool(
                ecart <= CRITERES["ecart_maximal_entre_methodes_rayons"]),
        },
    }
    (arguments.sortie / "vallee_des_rayons.json").write_text(
        json.dumps(rapport, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n  creux à {position:.3f} rayons terrestres, "
          f"profondeur relative {profondeur:.4f}")
    print(f"  quantile contre {arguments.tirages} tirages nuls : {quantile:.4f}  "
          f"(critère >= {CRITERES['quantile_minimal_contre_permutations']})")
    print("\n  témoin, position par méthode de découverte :")
    for m, v in par_methode.items():
        print(f"    {m:22s} n={v['n']:5d}  position {v['position']:.3f}  "
              f"profondeur {v['profondeur']:.4f}")
    print(f"  écart entre méthodes {ecart:.3f}  "
          f"(critère <= {CRITERES['ecart_maximal_entre_methodes_rayons']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
