"""Statistiques de rang communes à la campagne de mémoire matérielle.

L'implémentation est locale afin de ne pas ajouter SciPy comme dépendance. Les
ex æquo reçoivent leur rang moyen, conformément à la définition de Spearman.
"""
from __future__ import annotations

import numpy as np


def rangs_moyens(valeurs) -> np.ndarray:
    valeurs = np.asarray(valeurs, dtype=float)
    ordre = np.argsort(valeurs, kind="mergesort")
    tries = valeurs[ordre]
    rangs_tries = np.empty(valeurs.size, dtype=float)
    debut = 0
    while debut < valeurs.size:
        fin = debut + 1
        while fin < valeurs.size and tries[fin] == tries[debut]:
            fin += 1
        # Les rangs sont numérotés à partir de zéro ; le décalage n'affecte
        # pas la corrélation.
        rangs_tries[debut:fin] = (debut + fin - 1) / 2.0
        debut = fin
    rangs = np.empty(valeurs.size, dtype=float)
    rangs[ordre] = rangs_tries
    return rangs


def spearman(x, y) -> float:
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    garde = np.isfinite(x) & np.isfinite(y)
    x, y = x[garde], y[garde]
    if x.size < 3:
        return float("nan")
    rx, ry = rangs_moyens(x), rangs_moyens(y)
    if rx.std() == 0 or ry.std() == 0:
        return float("nan")
    return float(np.corrcoef(rx, ry)[0, 1])


def permuter_dans_strates(valeurs, strates, aleatoire) -> np.ndarray:
    """Permute les valeurs uniquement entre unités de la même strate."""
    valeurs = np.asarray(valeurs, dtype=float)
    strates = np.asarray(strates, dtype=object)
    resultat = valeurs.copy()
    for strate in dict.fromkeys(strates.tolist()):
        indices = np.flatnonzero(strates == strate)
        resultat[indices] = aleatoire.permutation(valeurs[indices])
    return resultat
