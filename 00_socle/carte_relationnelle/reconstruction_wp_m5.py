"""Reconstruction de transitions masquées — WP-M5 du plan directeur.

« Masquer 20 % des transitions et tenter de les reconstruire avec ORI-C.
Comparer à une chronologie descriptive simple. »

Le WP-S3 a testé la prédiction de **liens** masqués. Celui-ci teste la
prédiction d'un **nœud** masqué : connaissant la carte privée d'une transition,
peut-on retrouver le régime auquel elle appartient ?

Trois prédicteurs, à information égale :

    ORI-C          régime médian des voisins dans le graphe
    chronologique  régime interpolé entre les transitions d'indice adjacent
    majoritaire    le régime le plus fréquent, témoin sans information

Le prédicteur chronologique est le témoin décisif. S'il n'est pas battu, la
structure de la carte n'ajoute rien à l'ordre des identifiants.

Exécution : `python reconstruction_wp_m5.py [--repetitions 500]`
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parent
DONNEES = RACINE / "data"
SORTIE = RACINE / "resultats_analyse"
SEPARATEUR = ";"


def charger():
    with (DONNEES / "noeuds_poc.csv").open(encoding="utf-8-sig",
                                           newline="") as flux:
        noeuds = {l["id"]: l for l in csv.DictReader(flux, delimiter=SEPARATEUR)}
    with (DONNEES / "relations_oric_47_provisoires.csv").open(
            encoding="utf-8-sig", newline="") as flux:
        liens = [(l["source"], l["target"])
                 for l in csv.DictReader(flux, delimiter=SEPARATEUR)]
    regimes = {i: int(n["regime_num"]) for i, n in noeuds.items()}
    voisins: dict[str, set[str]] = {i: set() for i in noeuds}
    for source, cible in liens:
        voisins[source].add(cible)
        voisins[cible].add(source)
    return regimes, voisins


def rang(identifiant: str) -> int:
    return int(identifiant.split("-")[1])


def predire_oric(cible, regimes_connus, voisins):
    """Régime médian des voisins encore visibles."""
    valeurs = [regimes_connus[v] for v in voisins[cible] if v in regimes_connus]
    if not valeurs:
        return None
    return float(np.median(valeurs))


def predire_chronologique(cible, regimes_connus):
    """Interpolation entre les identifiants adjacents encore visibles."""
    r = rang(cible)
    avant = [(rang(i), v) for i, v in regimes_connus.items() if rang(i) < r]
    apres = [(rang(i), v) for i, v in regimes_connus.items() if rang(i) > r]
    if not avant and not apres:
        return None
    if not avant:
        return float(min(apres)[1])
    if not apres:
        return float(max(avant)[1])
    return float((max(avant)[1] + min(apres)[1]) / 2.0)


def predire_majoritaire(regimes_connus):
    return float(Counter(regimes_connus.values()).most_common(1)[0][0])


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--repetitions", type=int, default=500)
    parseur.add_argument("--fraction", type=float, default=0.20)
    parseur.add_argument("--graine", type=int, default=20260801)
    arguments = parseur.parse_args()

    SORTIE.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(arguments.graine)
    regimes, voisins = charger()
    identifiants = sorted(regimes, key=rang)
    combien = max(1, int(round(arguments.fraction * len(identifiants))))

    erreurs = {"oric": [], "chronologique": [], "majoritaire": []}
    exacts = {"oric": [], "chronologique": [], "majoritaire": []}
    sans_voisin = 0

    for _ in range(arguments.repetitions):
        masques = [identifiants[i] for i in rng.choice(
            len(identifiants), combien, replace=False)]
        connus = {i: r for i, r in regimes.items() if i not in masques}
        for cible in masques:
            vrai = regimes[cible]
            predictions = {
                "oric": predire_oric(cible, connus, voisins),
                "chronologique": predire_chronologique(cible, connus),
                "majoritaire": predire_majoritaire(connus),
            }
            if predictions["oric"] is None:
                sans_voisin += 1
                # Repli explicite : sans voisin visible, ORI-C n'a rien à dire.
                predictions["oric"] = predictions["majoritaire"]
            for nom, valeur in predictions.items():
                erreurs[nom].append(abs(valeur - vrai))
                exacts[nom].append(abs(valeur - vrai) < 0.5)

    resume = {
        nom: {
            "erreur_absolue_moyenne": float(np.mean(valeurs)),
            "erreur_absolue_mediane": float(np.median(valeurs)),
            "taux_exact": float(np.mean(exacts[nom])),
        }
        for nom, valeurs in erreurs.items()
    }
    ecart = np.asarray(erreurs["oric"]) - np.asarray(erreurs["chronologique"])
    rapport = {
        "transitions": len(identifiants),
        "masquees_par_tirage": combien,
        "repetitions": arguments.repetitions,
        "cas_sans_voisin_visible": sans_voisin,
        "par_predicteur": resume,
        "oric_moins_chronologique": {
            "erreur_moyenne": float(ecart.mean()),
            "ic_2.5": float(np.percentile(ecart, 2.5)),
            "ic_97.5": float(np.percentile(ecart, 97.5)),
            "fraction_de_cas_ou_oric_fait_mieux": float(np.mean(ecart < 0)),
            "fraction_de_cas_egaux": float(np.mean(ecart == 0)),
        },
        "lecture": (
            "L'erreur est mesurée en numéros de régime. Le prédicteur "
            "chronologique n'utilise que l'ordre des identifiants ; le "
            "prédicteur ORI-C utilise les liens typés de la carte. Si le "
            "second ne bat pas le premier, la carte n'ajoute rien à la "
            "chronologie pour cette tâche."
        ),
    }
    (SORTIE / "reconstruction_wp_m5.json").write_text(
        json.dumps(rapport, indent=2, ensure_ascii=False, default=float),
        encoding="utf-8",
    )
    for nom, valeurs in resume.items():
        print(f"  {nom:14s} EAM {valeurs['erreur_absolue_moyenne']:.4f}  "
              f"exact {valeurs['taux_exact']:.4f}")
    e = rapport["oric_moins_chronologique"]
    print(f"  ORI-C - chronologique : {e['erreur_moyenne']:+.4f} "
          f"| ORI-C meilleur dans {e['fraction_de_cas_ou_oric_fait_mieux']:.3f} "
          f"| égaux {e['fraction_de_cas_egaux']:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
