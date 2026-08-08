#!/usr/bin/env python3
"""WP-CLIM-MEM-2026 — exécution du protocole gelé.

Ce script applique la règle de décision écrite dans `PROTOCOLE.md`, sans la
réinterpréter. Il est scellé par empreinte dans `GEL.json` avant sa première
exécution.

    python executer.py

Il ne rend qu'un verdict parmi trois : soutient, ne soutient pas, indéterminé.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ICI = Path(__file__).resolve().parent
TABLE = ICI.parent / "data" / "processed" / "memoire_climatique_bintanja_insolation.csv"
GEL = ICI / "GEL.json"
SORTIE = ICI / "RESULTAT.json"

CIBLE = "ice_volume_total_sle"
FORCAGES = ["insolation_65N_jul_Wm2", "obliquity_deg", "precession", "eccentricity"]
DECALAGES_KA = [10, 20, 40]
BLOCS = 10
PERMUTATIONS = 2000
ALPHA = 0.05
BLOCS_MINIMUM = 8
GRAINE = 20260808


def empreinte(chemin: Path) -> str:
    return hashlib.sha256(chemin.read_bytes()).hexdigest()


def ajuster_et_predire(entrainement_X, entrainement_y, test_X):
    """Moindres carrés ordinaires avec constante, sans régularisation."""
    X = np.column_stack([np.ones(len(entrainement_X)), entrainement_X])
    coefficients, *_ = np.linalg.lstsq(X, entrainement_y, rcond=None)
    Xt = np.column_stack([np.ones(len(test_X)), test_X])
    return Xt @ coefficients


def rmse(observe, predit) -> float:
    return float(np.sqrt(np.mean((observe - predit) ** 2)))


def construire(cadre: pd.DataFrame):
    """Décalages du compartiment, calculés sur l'axe des âges croissants."""
    cadre = cadre.sort_values("age_ka_bp").reset_index(drop=True)
    for decalage in DECALAGES_KA:
        cadre[f"memoire_{decalage}"] = cadre[CIBLE].shift(decalage)
    return cadre.dropna().reset_index(drop=True)


def evaluer(cadre: pd.DataFrame, aleatoire, permuter: bool) -> float:
    """RMSE agrégée sur les blocs contigus de test."""
    colonnes_memoire = [f"memoire_{d}" for d in DECALAGES_KA]
    n = len(cadre)
    bornes = np.linspace(0, n, BLOCS + 1).astype(int)
    observes, predits = [], []
    for i in range(BLOCS):
        debut, fin = bornes[i], bornes[i + 1]
        masque_test = np.zeros(n, dtype=bool)
        masque_test[debut:fin] = True
        entrainement, test = cadre[~masque_test], cadre[masque_test]
        if len(entrainement) < 50 or len(test) < 10:
            continue
        memoire_entrainement = entrainement[colonnes_memoire].to_numpy()
        memoire_test = test[colonnes_memoire].to_numpy()
        if permuter:
            # Le témoin apparié : mêmes colonnes, même nombre de paramètres,
            # correspondance temporelle détruite par permutation de blocs.
            ordre = aleatoire.permutation(len(memoire_entrainement))
            memoire_entrainement = memoire_entrainement[ordre]
            ordre_test = aleatoire.permutation(len(memoire_test))
            memoire_test = memoire_test[ordre_test]
        X_entrainement = np.column_stack(
            [entrainement[FORCAGES].to_numpy(), memoire_entrainement]
        )
        X_test = np.column_stack([test[FORCAGES].to_numpy(), memoire_test])
        prediction = ajuster_et_predire(
            X_entrainement, entrainement[CIBLE].to_numpy(), X_test
        )
        observes.append(test[CIBLE].to_numpy())
        predits.append(prediction)
    if not observes:
        return float("nan")
    return rmse(np.concatenate(observes), np.concatenate(predits))


def evaluer_etat_seul(cadre: pd.DataFrame) -> tuple[float, int]:
    n = len(cadre)
    bornes = np.linspace(0, n, BLOCS + 1).astype(int)
    observes, predits, utilises = [], [], 0
    for i in range(BLOCS):
        debut, fin = bornes[i], bornes[i + 1]
        masque = np.zeros(n, dtype=bool)
        masque[debut:fin] = True
        entrainement, test = cadre[~masque], cadre[masque]
        if len(entrainement) < 50 or len(test) < 10:
            continue
        utilises += 1
        prediction = ajuster_et_predire(
            entrainement[FORCAGES].to_numpy(),
            entrainement[CIBLE].to_numpy(),
            test[FORCAGES].to_numpy(),
        )
        observes.append(test[CIBLE].to_numpy())
        predits.append(prediction)
    return rmse(np.concatenate(observes), np.concatenate(predits)), utilises


def main() -> int:
    gel = json.loads(GEL.read_text(encoding="utf-8"))
    for cle, chemin in [("protocole", ICI / "PROTOCOLE.md"), ("code", Path(__file__))]:
        if empreinte(chemin) != gel["empreintes"][cle]:
            print(f"Empreinte divergente pour {chemin.name}. Protocole invalidé.")
            return 2
    if empreinte(TABLE) != gel["empreintes"]["table"]:
        print("La table de données a changé depuis le gel. Protocole invalidé.")
        return 2

    cadre = construire(pd.read_csv(TABLE))
    aleatoire = np.random.default_rng(GRAINE)

    rmse_etat, blocs_utilises = evaluer_etat_seul(cadre)
    rmse_histoire = evaluer(cadre, aleatoire, permuter=False)
    permutations = [evaluer(cadre, aleatoire, permuter=True) for _ in range(PERMUTATIONS)]
    permutations = np.array([p for p in permutations if np.isfinite(p)])
    rmse_permutee = float(np.mean(permutations))
    valeur_p = float((permutations <= rmse_histoire).mean())

    if blocs_utilises < BLOCS_MINIMUM:
        verdict = "indetermine"
        motif = f"{blocs_utilises} blocs exploitables, minimum {BLOCS_MINIMUM}"
    elif (
        rmse_histoire < rmse_etat
        and rmse_histoire < rmse_permutee
        and valeur_p <= ALPHA
    ):
        verdict, motif = "soutient", "les trois conditions de la règle sont remplies"
    else:
        echecs = []
        if not rmse_histoire < rmse_etat:
            echecs.append("l'histoire ne bat pas l'état seul")
        if not rmse_histoire < rmse_permutee:
            echecs.append("l'histoire ne bat pas le témoin permuté")
        if valeur_p > ALPHA:
            echecs.append(f"p = {valeur_p:.4f} > {ALPHA}")
        verdict, motif = "ne_soutient_pas", " ; ".join(echecs)

    rapport = {
        "protocol_id": gel["protocol_id"],
        "gele_le": gel["gele_le"],
        "lignes_apres_decalages": len(cadre),
        "blocs_utilises": blocs_utilises,
        "rmse_etat_seul": rmse_etat,
        "rmse_etat_plus_histoire": rmse_histoire,
        "rmse_histoire_permutee_moyenne": rmse_permutee,
        "permutations": int(len(permutations)),
        "p_unilaterale": valeur_p,
        "alpha": ALPHA,
        "verdict": verdict,
        "motif": motif,
        "statut_epistemique": (
            "Sources dérivées de modèle. Ce verdict porte sur une reconstruction "
            "largement acceptée, pas sur une mesure directe. Il ne constitue pas "
            "une preuve empirique primaire."
        ),
    }
    with SORTIE.open("w", encoding="utf-8", newline="") as flux:
        flux.write(json.dumps(rapport, ensure_ascii=False, indent=2) + "\n")

    print(f"lignes après décalages : {len(cadre)}, blocs utilisés : {blocs_utilises}")
    print(f"  RMSE état seul          {rmse_etat:.6f}")
    print(f"  RMSE état + histoire    {rmse_histoire:.6f}")
    print(f"  RMSE histoire permutée  {rmse_permutee:.6f}   ({len(permutations)} tirages)")
    print(f"  p unilatérale           {valeur_p:.6f}")
    print()
    print(f"VERDICT : {verdict}")
    print(f"  {motif}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
