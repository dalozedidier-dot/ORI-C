"""Mémoire distribuée du climat sur GISTEMP réel — WP-CL1.

Le §13.1 du CODEBOOK affirme qu'un système conserve son passé dans plusieurs
compartiments de constantes de temps différentes, et qu'**une intégrale
temporelle unique ne représente pas cette mémoire**. Cette affirmation n'avait
jamais été testée : elle exigeait des observations climatiques que le dossier
ne contenait pas.

GISTEMP v4 les fournit. 146 années, quinze bandes de latitude, valeurs
mesurées par la NASA.

Trois tests, tous hors échantillon.

    CL1.2  Constantes de temps par compartiment. L'hémisphère sud est
           océanique, l'hémisphère nord continental. Le §13.1 prédit des
           constantes différentes. Prédiction falsifiable : tau(SH) > tau(NH).
    CL1.5  Modèle multi-mémoires contre intégrale cumulée unique, à budget
           égal, prédiction hors échantillon.
    Témoin Modèle de complexité égale : même nombre de paramètres, mémoires
           remplacées par des retards fixes sans structure de compartiment.

Calibration 1880-1970, prédiction 1971 à la fin de la série. Aucune donnée
n'est simulée : la cible et les entrées sont les anomalies observées.

    python memoire_distribuee_gistemp.py --data-dir <données>
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution

ANNEE_COUPURE = 1971
# Compartiments retenus : deux hémisphères de nature physique différente, plus
# les hautes latitudes nord, où l'amplification arctique est documentée.
COMPARTIMENTS = ["NHem", "SHem", "64N-90N"]
CIBLE = "Glob"


def charger(chemin: Path):
    with chemin.open(encoding="utf-8-sig", newline="") as flux:
        lignes = list(csv.DictReader(flux))
    par_region: dict[str, dict[int, float]] = {}
    for l in lignes:
        if not l["variable"].startswith("surface_temperature"):
            continue
        annee = int(l["time"][:4])
        try:
            par_region.setdefault(l["region"], {})[annee] = float(l["value"])
        except ValueError:
            continue
    return par_region


def noyau(serie: np.ndarray, tau: float) -> np.ndarray:
    """Convolution causale avec exp(-t/tau), récursive."""
    alpha = np.exp(-1.0 / max(tau, 1e-6))
    sortie = np.empty_like(serie)
    etat = serie[0]
    for i, v in enumerate(serie):
        etat = alpha * etat + (1.0 - alpha) * v
        sortie[i] = etat
    return sortie


def ajuster(entrees, cible, masque, forme, bornes, graine=20260801):
    def cout(theta):
        p = forme(theta, entrees)
        if not np.all(np.isfinite(p)):
            return 1e12
        return float(np.mean((p[masque] - cible[masque]) ** 2))

    r = differential_evolution(cout, bornes, maxiter=400, popsize=18,
                              tol=1e-10, seed=graine, polish=True)
    return r.x, forme(r.x, entrees)


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--data-dir", type=Path, required=True)
    parseur.add_argument("--sortie", type=Path, default=Path("."))
    arguments = parseur.parse_args()

    par_region = charger(arguments.data_dir / "modern_climate_timeseries.csv")
    annees = sorted(set.intersection(
        *(set(par_region[r]) for r in COMPARTIMENTS + [CIBLE])))
    t = np.array(annees, dtype=float)
    y = np.array([par_region[CIBLE][a] for a in annees])
    X = np.array([[par_region[r][a] for a in annees] for r in COMPARTIMENTS])
    masque = t < ANNEE_COUPURE
    prediction = ~masque
    print(f"{len(annees)} années, {int(masque.sum())} en calibration "
          f"({annees[0]}-{ANNEE_COUPURE - 1}), "
          f"{int(prediction.sum())} en prédiction "
          f"({ANNEE_COUPURE}-{annees[-1]})")

    def rmse(a, b):
        return float(np.sqrt(np.mean((a - b) ** 2)))

    resultats = {}

    # --- Intégrale cumulée unique : 2 paramètres -------------------------
    cumul = np.cumsum(X.mean(0)) / np.arange(1, len(t) + 1)

    def forme_integrale(theta, _):
        a, b = theta
        return a * cumul + b

    _, p_int = ajuster(X, y, masque, forme_integrale,
                       [(-10.0, 10.0), (-5.0, 5.0)])
    resultats["integrale_cumulee_unique"] = {
        "parametres": 2, "rmse": rmse(y[prediction], p_int[prediction])}

    # --- Multi-mémoires : un tau et un poids par compartiment ------------
    n = len(COMPARTIMENTS)

    def forme_multi(theta, entrees):
        taus, poids, decalage = theta[:n], theta[n:2 * n], theta[-1]
        return sum(poids[i] * noyau(entrees[i], taus[i])
                   for i in range(n)) + decalage

    bornes_multi = [(0.5, 200.0)] * n + [(-10.0, 10.0)] * n + [(-5.0, 5.0)]
    theta_multi, p_multi = ajuster(X, y, masque, forme_multi, bornes_multi)
    resultats["multi_memoires"] = {
        "parametres": 2 * n + 1,
        "rmse": rmse(y[prediction], p_multi[prediction]),
        "constantes_de_temps_ans": {
            COMPARTIMENTS[i]: float(theta_multi[i]) for i in range(n)},
        "poids": {COMPARTIMENTS[i]: float(theta_multi[n + i])
                  for i in range(n)},
    }

    # --- Témoin de complexité égale : mêmes paramètres, sans compartiment -
    # Les mémoires sont remplacées par des retards fixes appliqués à la
    # moyenne des régions : même nombre de degrés de liberté, aucune
    # structure de compartiment.
    moyenne = X.mean(0)

    def forme_temoin(theta, _):
        taus, poids, decalage = theta[:n], theta[n:2 * n], theta[-1]
        return sum(poids[i] * noyau(moyenne, taus[i])
                   for i in range(n)) + decalage

    _, p_tem = ajuster(X, y, masque, forme_temoin, bornes_multi)
    resultats["temoin_complexite_egale"] = {
        "parametres": 2 * n + 1,
        "rmse": rmse(y[prediction], p_tem[prediction])}

    reference = resultats["integrale_cumulee_unique"]["rmse"]
    temoin = resultats["temoin_complexite_egale"]["rmse"]
    multi = resultats["multi_memoires"]["rmse"]

    taus = resultats["multi_memoires"]["constantes_de_temps_ans"]
    rapport = {
        "source": "NASA GISTEMP v4, anomalies zonales observées",
        "cible": CIBLE, "compartiments": COMPARTIMENTS,
        "calibration": [annees[0], ANNEE_COUPURE - 1],
        "prediction": [ANNEE_COUPURE, annees[-1]],
        "resultats": resultats,
        "CL1_5_gain_sur_integrale_unique": 1.0 - multi / reference,
        "CL1_5_gain_sur_temoin_apparie": 1.0 - multi / temoin,
        "CL1_2_prediction_tau_SH_superieur_a_tau_NH": {
            "tau_SHem": taus["SHem"], "tau_NHem": taus["NHem"],
            "verifiee": bool(taus["SHem"] > taus["NHem"]),
        },
        "lecture": (
            "Le gain contre l'intégrale unique teste l'affirmation du §13.1. "
            "Le gain contre le témoin apparié teste si c'est la structure de "
            "compartiments qui apporte, et non le seul ajout de paramètres."
        ),
    }
    (arguments.sortie / "memoire_distribuee_gistemp.json").write_text(
        json.dumps(rapport, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n  intégrale cumulée unique   RMSE {reference:.4f}  (2 paramètres)")
    print(f"  témoin de complexité égale RMSE {temoin:.4f}  ({2 * n + 1} paramètres)")
    print(f"  multi-mémoires             RMSE {multi:.4f}  ({2 * n + 1} paramètres)")
    print(f"\n  gain sur l'intégrale unique  {1.0 - multi / reference:+.4f}")
    print(f"  gain sur le témoin apparié   {1.0 - multi / temoin:+.4f}")
    print("\n  constantes de temps ajustées, en années :")
    for r, v in taus.items():
        print(f"    {r:10s} {v:8.2f}")
    print(f"\n  prédiction tau(SH) > tau(NH) : "
          f"{rapport['CL1_2_prediction_tau_SH_superieur_a_tau_NH']['verifiee']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
