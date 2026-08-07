#!/usr/bin/env python3
"""Recense les critères de décision inatteignables par construction.

Un test à statistique discrète ne peut pas produire n'importe quelle valeur de
`p`. Un test de signe sur dix plis n'en produit que onze, dont la plus petite
vaut 2/2¹⁰. Un test de permutation à deux cents tirages ne descend pas sous
1/201. Quand le seuil de décision est plus exigeant que la plus petite valeur
que le test peut produire, **le critère ne peut pas être satisfait, quelle que
soit l'ampleur réelle de l'effet**. Le résultat n'est alors ni positif ni
négatif : il est vide.

Ce script parcourt les résultats du dépôt, retrouve chaque test discret nommé,
calcule ce qu'il peut atteindre, et classe le critère :

  atteignable            le seuil est franchissable dans des conditions usuelles
  atteignable_fragile    franchissable seulement à l'unanimité ou presque
  inatteignable          aucune configuration ne franchit le seuil

Il ne juge aucun résultat scientifique. Il dit si la question posée peut
recevoir une réponse.

    python scripts/auditer_atteignabilite_criteres.py
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "ATTEIGNABILITE_CRITERES.json"
ALPHA = 0.05
EXCLUS = {".git", "__pycache__", ".pytest_cache"}


def p_signe_bilateral(favorables: int, total: int) -> float:
    queue = sum(math.comb(total, i) for i in range(favorables, total + 1))
    return min(1.0, 2 * queue / 2 ** total)


def audit_signe(combinaisons: int, alpha: float) -> dict[str, object]:
    """Test de signe exact sur `n` plis, soit `2**n` combinaisons."""
    n = int(round(math.log2(combinaisons)))
    minimum = p_signe_bilateral(n, n)
    requis = next(
        (k for k in range(n // 2 + 1, n + 1) if p_signe_bilateral(k, n) <= alpha), None
    )
    if requis is None:
        classe = "inatteignable"
    elif requis >= n:
        classe = "atteignable_fragile"
    elif requis / n >= 0.9:
        classe = "atteignable_fragile"
    else:
        classe = "atteignable"
    return {
        "famille": "test de signe exact",
        "unites": n,
        "p_minimal_atteignable": minimum,
        "unites_favorables_requises": requis,
        "classe": classe,
        "lecture": (
            f"Sur {n} unités, il faut au moins {requis} unités favorables pour "
            f"descendre à p <= {alpha}."
            if requis is not None
            else f"Sur {n} unités, aucune configuration ne descend à p <= {alpha}."
        ),
    }


def audit_permutation(tirages: int, alpha: float) -> dict[str, object]:
    """Test de permutation ou de bootstrap à `tirages` répétitions."""
    minimum = 1.0 / (tirages + 1)
    if minimum > alpha:
        classe = "inatteignable"
    elif minimum > alpha / 5:
        classe = "atteignable_fragile"
    else:
        classe = "atteignable"
    return {
        "famille": "test de permutation",
        "tirages": tirages,
        "p_minimal_atteignable": minimum,
        "classe": classe,
        "lecture": (
            f"Avec {tirages} tirages, la plus petite valeur de p vaut "
            f"{minimum:.2e}."
        ),
    }


CLES_SIGNE = ("sign_flip_combinations",)
CLES_PERMUTATION = ("permutations", "bootstrap_draws", "tirages", "n_tirages")


def parcourir(objet, chemin: str = ""):
    if isinstance(objet, dict):
        for cle, valeur in objet.items():
            yield from parcourir(valeur, f"{chemin}/{cle}")
    elif isinstance(objet, (int, float)) and not isinstance(objet, bool):
        yield chemin, objet


def main() -> int:
    constats: list[dict[str, object]] = []
    for dossier, sous, fichiers in os.walk(RACINE):
        sous[:] = [d for d in sous if d not in EXCLUS]
        for fichier in fichiers:
            if not fichier.endswith(".json"):
                continue
            chemin = Path(dossier) / fichier
            try:
                donnees = json.loads(chemin.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                continue
            relatif = str(chemin.relative_to(RACINE)).replace(os.sep, "/")
            for emplacement, valeur in parcourir(donnees):
                nom = emplacement.rsplit("/", 1)[-1]
                if nom in CLES_SIGNE and valeur >= 2:
                    constat = audit_signe(int(valeur), ALPHA)
                elif nom in CLES_PERMUTATION and valeur >= 1:
                    constat = audit_permutation(int(valeur), ALPHA)
                else:
                    continue
                constat |= {"fichier": relatif, "emplacement": emplacement}
                constats.append(constat)

    par_classe: dict[str, int] = {}
    for constat in constats:
        classe = str(constat["classe"])
        par_classe[classe] = par_classe.get(classe, 0) + 1

    rapport = {
        "genere_par": "scripts/auditer_atteignabilite_criteres.py",
        "alpha": ALPHA,
        "principe": (
            "Un test à statistique discrète ne peut produire qu'un nombre fini "
            "de valeurs de p. Si le seuil de décision est plus exigeant que la "
            "plus petite valeur atteignable, le critère ne peut pas être "
            "satisfait et son résultat ne porte aucune information."
        ),
        "constats": len(constats),
        "par_classe": par_classe,
        "detail": sorted(constats, key=lambda c: (c["classe"], c["fichier"])),
        "limite": (
            "Ce balayage couvre les tests discrets dont la taille est inscrite "
            "dans les résultats. Il ne couvre pas les critères dont "
            "l'atteignabilité dépend de la distribution des données, comme le "
            "quantile de la vallée des rayons : ceux-là demandent une mesure "
            "empirique par sous-échantillonnage."
        ),
    }
    with SORTIE.open("w", encoding="utf-8", newline="") as flux:
        flux.write(json.dumps(rapport, ensure_ascii=False, indent=2) + "\n")

    print(f"{len(constats)} critères discrets audités, alpha = {ALPHA}")
    for classe, nombre in sorted(par_classe.items()):
        print(f"  {classe:24s} {nombre}")
    print()
    for constat in rapport["detail"]:
        if constat["classe"] != "atteignable":
            print(f"  [{constat['classe']}] {constat['fichier']}")
            print(f"      {constat['emplacement']}")
            print(f"      {constat['lecture']}")
    print(f"\nécrit : {SORTIE.relative_to(RACINE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
