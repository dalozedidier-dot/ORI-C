#!/usr/bin/env python3
"""Surrogats AAFT et IAAFT — témoins pour les critères sur séries temporelles.

Une permutation naïve détruit le spectre en même temps que la correspondance
temporelle. Sur une série autocorrélée, elle produit un témoin de bruit blanc et
donc un faux positif : c'est ce qui a invalidé `WP-CLIM-MEM-2026`, dont le
compartiment de mémoire avait une autocorrélation de +0,450 à 10 ka contre
+0,013 pour son témoin permuté.

Ce module fournit le témoin minimal acceptable pour ce genre de critère :

  AAFT   Amplitude Adjusted Fourier Transform. Préserve exactement
         l'histogramme des amplitudes et approximativement le spectre de
         puissance. Détruit la structure de phase et les dépendances non
         linéaires.

  IAAFT  Version itérative. Converge vers une préservation simultanée de
         l'histogramme et du spectre, meilleure que l'AAFT simple. C'est
         celle à utiliser par défaut.

Un signal qui ne dépasse pas la distribution obtenue sur ces surrogats n'est pas
distinguable de ce que produit une série linéaire de même spectre et de même
distribution.

Usage comme bibliothèque :

    from scripts.surrogats import iaaft
    surrogat = iaaft(serie, aleatoire=numpy.random.default_rng(20260808))

Usage en ligne de commande, pour contrôler la qualité sur une série réelle :

    python scripts/surrogats.py --serie <fichier.csv> --colonne <nom>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np


def aaft(serie: np.ndarray, aleatoire: np.random.Generator) -> np.ndarray:
    """Surrogat AAFT : histogramme exact, spectre approché.

    Le rang de la série est transporté sur un tirage gaussien, ce tirage est
    randomisé en phase, puis les amplitudes d'origine sont replacées selon le
    rang du résultat. L'histogramme est donc exactement celui de l'entrée.
    """
    n = serie.size
    gaussien = np.sort(aleatoire.standard_normal(n))
    rangs = np.argsort(np.argsort(serie))
    transporte = gaussien[rangs]

    spectre = np.fft.rfft(transporte)
    phases = aleatoire.uniform(0, 2 * np.pi, spectre.size)
    phases[0] = 0.0
    if n % 2 == 0:
        phases[-1] = 0.0
    randomise = np.fft.irfft(np.abs(spectre) * np.exp(1j * phases), n=n)

    amplitudes = np.sort(serie)
    return amplitudes[np.argsort(np.argsort(randomise))]


def iaaft(
    serie: np.ndarray,
    aleatoire: np.random.Generator,
    iterations: int = 200,
    tolerance: float = 1e-8,
) -> np.ndarray:
    """Surrogat IAAFT : histogramme exact et spectre préservé par itération.

    Alterne deux projections — imposer le spectre cible, puis réimposer
    l'histogramme cible — jusqu'à stabilisation. L'histogramme final est exact ;
    le spectre converge vers celui de l'entrée.
    """
    n = serie.size
    amplitudes = np.sort(serie)
    module_cible = np.abs(np.fft.rfft(serie))

    courant = aleatoire.permutation(serie)
    precedent = None
    for _ in range(iterations):
        spectre = np.fft.rfft(courant)
        phases = np.angle(spectre)
        courant = np.fft.irfft(module_cible * np.exp(1j * phases), n=n)
        courant = amplitudes[np.argsort(np.argsort(courant))]
        if precedent is not None and np.max(np.abs(courant - precedent)) < tolerance:
            break
        precedent = courant.copy()
    return courant


def qualite(serie: np.ndarray, surrogat: np.ndarray) -> dict[str, float]:
    """Mesure ce que le surrogat préserve et ce qu'il détruit."""
    def autocorrelation(x: np.ndarray, decalage: int) -> float:
        if decalage >= x.size:
            return float("nan")
        return float(np.corrcoef(x[decalage:], x[:-decalage])[0, 1])

    spectre_origine = np.abs(np.fft.rfft(serie - serie.mean()))
    spectre_surrogat = np.abs(np.fft.rfft(surrogat - surrogat.mean()))
    ecart_spectre = float(
        np.mean(np.abs(spectre_surrogat - spectre_origine))
        / max(np.mean(spectre_origine), 1e-12)
    )
    return {
        "histogramme_identique": bool(
            np.allclose(np.sort(serie), np.sort(surrogat))
        ),
        "ecart_relatif_moyen_du_spectre": ecart_spectre,
        "autocorrelation_origine_lag10": autocorrelation(serie, 10),
        "autocorrelation_surrogat_lag10": autocorrelation(surrogat, 10),
        "correlation_avec_l_origine": float(np.corrcoef(serie, surrogat)[0, 1]),
    }


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--serie", required=True, type=Path)
    analyseur.add_argument("--colonne", required=True)
    analyseur.add_argument("--tirages", type=int, default=20)
    analyseur.add_argument("--graine", type=int, default=20260808)
    arguments = analyseur.parse_args()

    import pandas as pd

    valeurs = pd.read_csv(arguments.serie)[arguments.colonne].dropna().to_numpy(float)
    aleatoire = np.random.default_rng(arguments.graine)
    print(f"série : {valeurs.size} points, colonne {arguments.colonne}")
    print()
    for nom, fonction in (("AAFT", aaft), ("IAAFT", iaaft)):
        mesures = [qualite(valeurs, fonction(valeurs, aleatoire))
                   for _ in range(arguments.tirages)]
        histogrammes = all(m["histogramme_identique"] for m in mesures)
        spectre = float(np.mean([m["ecart_relatif_moyen_du_spectre"] for m in mesures]))
        auto = float(np.mean([m["autocorrelation_surrogat_lag10"] for m in mesures]))
        correlation = float(np.mean([abs(m["correlation_avec_l_origine"]) for m in mesures]))
        print(f"{nom} sur {arguments.tirages} tirages")
        print(f"  histogramme exactement préservé   {histogrammes}")
        print(f"  écart relatif moyen du spectre    {spectre:.2e}")
        print(f"  autocorrélation à 10 ka           {auto:+.3f}   "
              f"(origine {mesures[0]['autocorrelation_origine_lag10']:+.3f})")
        print(f"  corrélation absolue à l'origine   {correlation:.3f}   "
              f"(doit être faible : la correspondance est détruite)")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
