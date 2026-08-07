#!/usr/bin/env python3
"""WP-EXO-PACC-2026 — vérification du préenregistrement exoplanétaire.

Ce script est **gelé**. Son empreinte SHA-256 est inscrite dans `PROTOCOLE.json`
avant toute acquisition de données nouvelles. Le modifier invalide le
préenregistrement : il faudrait alors ouvrir un nouveau protocole.

Il ne s'exécute pas au moment du gel. Il s'exécutera à la date de vérification,
sur un instantané du NASA Exoplanet Archive postérieur au gel, pour départager
l'hypothèse et son témoin.

    python verifier_bande_accessible.py --candidat <instantane_posterieur.csv>

Aucune donnée n'est imputée. Les planètes sans période mesurée sont exclues et
comptées séparément.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ICI = Path(__file__).resolve().parent
PROTOCOLE = ICI / "PROTOCOLE.json"
REFERENCE = ICI / "reference" / "NASA_Exoplanet_Archive_PS_2026-08-07.csv"


def empreinte(chemin: Path) -> str:
    return hashlib.sha256(chemin.read_bytes()).hexdigest()


def paires_voisines(cadre: pd.DataFrame) -> dict[str, list[float]]:
    """Rapport de période entre voisins immédiats, par système."""
    resultat: dict[str, list[float]] = {}
    valides = cadre[cadre["pl_orbper"].notna() & (cadre["pl_orbper"] > 0)]
    for hote, groupe in valides.groupby("hostname"):
        periodes = np.sort(groupe["pl_orbper"].to_numpy(dtype=float))
        if periodes.size >= 2:
            resultat[str(hote)] = (periodes[1:] / periodes[:-1]).tolist()
    return resultat


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--candidat", required=True, type=Path)
    analyseur.add_argument("--sortie", type=Path, default=ICI / "RESULTAT.json")
    arguments = analyseur.parse_args()

    protocole = json.loads(PROTOCOLE.read_text(encoding="utf-8"))
    bas = float(protocole["bande_accessible"]["borne_basse"])
    haut = float(protocole["bande_accessible"]["borne_haute"])
    taux_nul = float(protocole["temoin"]["taux_attendu_sous_le_nul"])
    alpha = float(protocole["alpha"])

    empreinte_reference = empreinte(REFERENCE)
    if empreinte_reference != protocole["reference"]["sha256"]:
        print("L'instantané de référence ne correspond plus à son empreinte gelée.")
        return 2

    reference = pd.read_csv(REFERENCE, comment="#", low_memory=False).drop_duplicates("pl_name")
    candidat = pd.read_csv(arguments.candidat, comment="#", low_memory=False).drop_duplicates("pl_name")

    connues = set(reference["pl_name"].astype(str))
    hotes_connus = set(reference["hostname"].astype(str))

    # Événements retenus : planète absente du gel, sur un hôte déjà connu au gel.
    nouvelles = candidat[~candidat["pl_name"].astype(str).isin(connues)]
    evenements = nouvelles[nouvelles["hostname"].astype(str).isin(hotes_connus)]
    sans_periode = int((evenements["pl_orbper"].isna() | (evenements["pl_orbper"] <= 0)).sum())

    # Pour chaque événement, rapport au voisin immédiat dans le système complété.
    rapports: list[dict[str, object]] = []
    for hote, groupe in evenements.groupby("hostname"):
        systeme = candidat[candidat["hostname"].astype(str) == str(hote)]
        periodes = systeme[systeme["pl_orbper"].notna() & (systeme["pl_orbper"] > 0)]
        if len(periodes) < 2:
            continue
        triees = periodes.sort_values("pl_orbper")
        valeurs = triees["pl_orbper"].to_numpy(dtype=float)
        noms = triees["pl_name"].astype(str).to_numpy()
        for nom in groupe["pl_name"].astype(str):
            position = int(np.where(noms == nom)[0][0]) if nom in set(noms) else -1
            if position < 0:
                continue
            voisins = []
            if position > 0:
                voisins.append(valeurs[position] / valeurs[position - 1])
            if position + 1 < valeurs.size:
                voisins.append(valeurs[position + 1] / valeurs[position])
            if not voisins:
                continue
            rapport = float(min(voisins))  # le voisin le plus contraignant
            rapports.append(
                {
                    "planete": nom,
                    "hote": str(hote),
                    "rapport_de_periode": rapport,
                    "dans_la_bande": bool(bas <= rapport <= haut),
                }
            )

    n = len(rapports)
    succes = sum(1 for r in rapports if r["dans_la_bande"])
    if n == 0:
        print("Aucun événement exploitable. Vérification reportée.")
        verdict, valeur_p = "indetermine_faute_d_evenements", None
    else:
        valeur_p = float(stats.binomtest(succes, n, taux_nul, alternative="greater").pvalue)
        seuil_atteint = valeur_p <= alpha
        seuil_effectif = int(stats.binom.ppf(1 - alpha, n, taux_nul)) + 1
        verdict = (
            "bande_accessible_soutenue_contre_le_nul"
            if seuil_atteint
            else "non_soutenue"
        )

    rapport_final = {
        "protocol_id": protocole["protocol_id"],
        "gele_le": protocole["gele_le"],
        "verifie_le": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "reference_sha256": empreinte_reference,
        "candidat": str(arguments.candidat),
        "candidat_sha256": empreinte(arguments.candidat),
        "evenements": n,
        "evenements_sans_periode_exclus": sans_periode,
        "succes_dans_la_bande": succes,
        "taux_observe": (succes / n) if n else None,
        "taux_attendu_sous_le_nul": taux_nul,
        "seuil_de_succes_requis": (seuil_effectif if n else None),
        "p_unilateral": valeur_p,
        "alpha": alpha,
        "verdict": verdict,
        "detail": rapports,
        "limite": (
            "Le test porte sur les planètes ajoutées à des hôtes déjà connus au "
            "gel. Il ne dit rien des systèmes entièrement nouveaux, ni des "
            "planètes dont la période reste non mesurée."
        ),
    }
    arguments.sortie.write_text(
        json.dumps(rapport_final, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"événements={n} succès={succes} p={valeur_p} verdict={verdict}")
    print(f"écrit : {arguments.sortie}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
