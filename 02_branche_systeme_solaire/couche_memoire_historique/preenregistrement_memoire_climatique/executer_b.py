#!/usr/bin/env python3
"""WP-CLIM-MEM-2026-B — exécution du protocole gelé, témoin IAAFT.

Scellé par empreinte dans `GEL_B.json` avant sa première exécution.

    python executer_b.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ICI = Path(__file__).resolve().parent
RACINE = ICI.parents[2]
sys.path.insert(0, str(RACINE))
from scripts.surrogats import iaaft  # noqa: E402

TABLE = ICI.parent / "data" / "processed" / "memoire_climatique_bintanja_insolation.csv"
GEL = ICI / "GEL_B.json"
SORTIE = ICI / "RESULTAT_B.json"

CIBLE = "ice_volume_total_sle"
FORCAGES = ["insolation_65N_jul_Wm2", "obliquity_deg", "precession", "eccentricity"]
DECALAGES = [10, 20, 40]
EMBARGO = 40
BLOCS = 10
SURROGATS = 500
GRAINE = 20260808
ALPHA = 0.05
BLOCS_MINIMUM = 8


def empreinte(chemin: Path) -> str:
    return hashlib.sha256(chemin.read_bytes()).hexdigest()


def rmse(observe, predit) -> float:
    return float(np.sqrt(np.mean((observe - predit) ** 2)))


def ajuster(Xa, ya, Xt):
    X = np.column_stack([np.ones(len(Xa)), Xa])
    coefficients, *_ = np.linalg.lstsq(X, ya, rcond=None)
    return np.column_stack([np.ones(len(Xt)), Xt]) @ coefficients


def evaluer(forcages, cible, memoire, blocs=BLOCS):
    """RMSE agrégée sur blocs contigus, avec embargo de part et d'autre du test."""
    n = len(cible)
    bornes = np.linspace(0, n, blocs + 1).astype(int)
    observes, predits, utilises = [], [], 0
    for i in range(blocs):
        debut, fin = bornes[i], bornes[i + 1]
        test = np.zeros(n, dtype=bool)
        test[debut:fin] = True
        exclu = np.zeros(n, dtype=bool)
        exclu[max(0, debut - EMBARGO):min(n, fin + EMBARGO)] = True
        entrainement = ~exclu
        if entrainement.sum() < 50 or test.sum() < 10:
            continue
        utilises += 1
        if memoire is None:
            Xa, Xt = forcages[entrainement], forcages[test]
        else:
            Xa = np.column_stack([forcages[entrainement], memoire[entrainement]])
            Xt = np.column_stack([forcages[test], memoire[test]])
        observes.append(cible[test])
        predits.append(ajuster(Xa, cible[entrainement], Xt))
    if not observes:
        return float("nan"), 0
    return rmse(np.concatenate(observes), np.concatenate(predits)), utilises


def decalages_de(serie: np.ndarray) -> np.ndarray:
    """Matrice des décalages, alignée sur la série fournie."""
    colonnes = []
    for decalage in DECALAGES:
        decalee = np.full(serie.size, np.nan)
        decalee[decalage:] = serie[:-decalage]
        colonnes.append(decalee)
    return np.column_stack(colonnes)


def main() -> int:
    gel = json.loads(GEL.read_text(encoding="utf-8"))
    for cle, chemin in [
        ("protocole", ICI / "PROTOCOLE_B.md"),
        ("code", Path(__file__)),
        ("surrogats", RACINE / "scripts" / "surrogats.py"),
        ("table", TABLE),
    ]:
        if empreinte(chemin) != gel["empreintes"][cle]:
            print(f"Empreinte divergente pour {chemin.name}. Protocole invalidé.")
            return 2

    cadre = pd.read_csv(TABLE).sort_values("age_ka_bp").reset_index(drop=True)
    serie = cadre[CIBLE].to_numpy(float)
    memoire = decalages_de(serie)
    valides = ~np.isnan(memoire).any(axis=1)

    forcages = cadre[FORCAGES].to_numpy(float)[valides]
    cible = serie[valides]
    memoire_reelle = memoire[valides]

    rmse_etat, blocs = evaluer(forcages, cible, None)
    rmse_histoire, _ = evaluer(forcages, cible, memoire_reelle)

    aleatoire = np.random.default_rng(GRAINE)
    rmse_temoins = []
    for indice in range(SURROGATS):
        surrogat = iaaft(serie, aleatoire)
        memoire_surrogat = decalages_de(surrogat)[valides]
        valeur, _ = evaluer(forcages, cible, memoire_surrogat)
        if np.isfinite(valeur):
            rmse_temoins.append(valeur)
        if (indice + 1) % 100 == 0:
            print(f"  {indice + 1} / {SURROGATS} surrogats")
    rmse_temoins = np.array(rmse_temoins)

    valeur_p = float((rmse_temoins <= rmse_histoire).mean())
    percentile_5 = float(np.percentile(rmse_temoins, 5))

    if blocs < BLOCS_MINIMUM:
        verdict, motif = "indetermine", f"{blocs} blocs exploitables"
    elif rmse_histoire < rmse_etat and valeur_p <= ALPHA:
        verdict, motif = "soutient", "les deux conditions de la règle sont remplies"
    else:
        echecs = []
        if not rmse_histoire < rmse_etat:
            echecs.append("l'histoire ne bat pas l'état seul")
        if valeur_p > ALPHA:
            echecs.append(f"p = {valeur_p:.4f} > {ALPHA} contre le témoin IAAFT")
        verdict, motif = "ne_soutient_pas", " ; ".join(echecs)

    rapport = {
        "protocol_id": "WP-CLIM-MEM-2026-B",
        "gele_le": gel["gele_le"],
        "predecesseur": "WP-CLIM-MEM-2026, clos sur invalide",
        "blocs_utilises": blocs,
        "embargo_ka": EMBARGO,
        "rmse_etat_seul": rmse_etat,
        "rmse_etat_plus_histoire": rmse_histoire,
        "temoin_iaaft": {
            "surrogats": int(rmse_temoins.size),
            "rmse_moyenne": float(rmse_temoins.mean()),
            "rmse_percentile_5": percentile_5,
            "rmse_minimale": float(rmse_temoins.min()),
        },
        "p_unilaterale": valeur_p,
        "alpha": ALPHA,
        "verdict": verdict,
        "motif": motif,
        "statut_epistemique": (
            "Sources dérivées de modèle. Verdict sur une reconstruction, pas une "
            "preuve empirique primaire."
        ),
    }
    with SORTIE.open("w", encoding="utf-8", newline="") as flux:
        flux.write(json.dumps(rapport, ensure_ascii=False, indent=2) + "\n")

    print()
    print(f"blocs utilisés : {blocs}, embargo {EMBARGO} ka")
    print(f"  RMSE état seul            {rmse_etat:.6f}")
    print(f"  RMSE état + histoire      {rmse_histoire:.6f}")
    print(f"  témoin IAAFT, moyenne     {rmse_temoins.mean():.6f}")
    print(f"  témoin IAAFT, 5e centile  {percentile_5:.6f}")
    print(f"  témoin IAAFT, minimum     {rmse_temoins.min():.6f}")
    print(f"  p unilatérale             {valeur_p:.6f}   ({rmse_temoins.size} surrogats)")
    print()
    print(f"VERDICT : {verdict}")
    print(f"  {motif}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
