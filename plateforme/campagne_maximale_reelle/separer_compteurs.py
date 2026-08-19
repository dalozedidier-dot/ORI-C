#!/usr/bin/env python3
"""Sépare le compteur de la campagne en deux, empirique et modèle.

`documentation/historique/ERRATUM_SCIENTIFIQUE_v0.9.4_2026-08-07.md` rappelle en prose que les
intégrations N-corps, H011 et les autres expériences numériques sont des
résultats de **modèle**, jamais des observations, et qu'ils ne doivent pas être
lus comme les résultats sur données réelles. Tant que la campagne n'émet qu'un
seul compteur, cette distinction dépend de la vigilance du lecteur.

Ce script la rend structurelle. Il relit les résultats de la campagne, retrouve
le moteur de chaque entrée, et le classe d'après `EMPIRICAL_POLICY.json`, qui
porte déjà `data_kind` et `eligible_for_empirical_proof` pour chaque jeu. Il
produit **deux compteurs distincts, jamais additionnés**.

    python plateforme/campagne_maximale_reelle/separer_compteurs.py

Il ne modifie aucun résultat et ne rend aucun verdict scientifique.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ICI = Path(__file__).resolve().parent
POLITIQUE = ICI / "EMPIRICAL_POLICY.json"
RESULTATS = ICI / "resultats_integration_maximale" / "results.json"
SORTIE = ICI / "resultats_integration_maximale" / "COMPTEURS_SEPARES.json"

# Un moteur qui simule, propage ou intègre produit un résultat de modèle, quelle
# que soit la qualité des données qui l'alimentent. Les conditions initiales de
# JPL Horizons sont mesurées ; la trajectoire qu'on en tire ne l'est pas.
PREFIXES_MODELE = ("astronomy_", "core_", "intervention", "planetesimal_")
MOTS_MODELE = ("simulation", "surrogate", "nbody", "integration", "propagation")


def classe_du_moteur(moteur: str, politique: dict) -> str:
    """« empirique » si le moteur lit des mesures, « modele » s'il en produit."""
    if not moteur:
        return "indetermine"
    if moteur.startswith(PREFIXES_MODELE) or any(m in moteur for m in MOTS_MODELE):
        return "modele"
    jeu = politique["datasets"].get(moteur)
    if jeu is not None:
        return "empirique" if jeu.get("eligible_for_empirical_proof") else "modele"
    # Fail closed. Un moteur absent de EMPIRICAL_POLICY.json n'est pas empirique
    # par defaut : il est indetermine. Le defaut inverse gonflait le compteur
    # empirique de 439 entrees sur 479, dont l'admissibilite n'avait jamais ete
    # declaree nulle part. Un depot qui se reclame du fail closed ne peut pas
    # classer par optimisme ce qu'il n'a pas verifie.
    return "indetermine"


def main() -> int:
    politique = json.loads(POLITIQUE.read_text(encoding="utf-8"))
    donnees = json.loads(RESULTATS.read_text(encoding="utf-8"))
    entrees = donnees["results"]

    compteurs: dict[str, Counter] = {
        "empirique": Counter(),
        "modele": Counter(),
        "indetermine": Counter(),
    }
    verdicts: dict[str, Counter] = {
        "empirique": Counter(),
        "modele": Counter(),
        "indetermine": Counter(),
    }
    moteurs: dict[str, Counter] = {c: Counter() for c in compteurs}

    for entree in entrees:
        details = entree.get("details") or {}
        classe = classe_du_moteur(str(details.get("engine") or ""), politique)
        compteurs[classe][str(entree.get("outcome"))] += 1
        verdicts[classe][str(entree.get("scientific_verdict"))] += 1
        moteurs[classe][str(details.get("engine") or "sans moteur")] += 1

    rapport = {
        "genere_par": "plateforme/campagne_maximale_reelle/separer_compteurs.py",
        "source": "resultats_integration_maximale/results.json",
        "regle": (
            "Les deux compteurs ne doivent jamais être additionnés. Un résultat "
            "de modèle et une mesure ne portent pas la même charge de preuve, et "
            "leur somme n'a pas de sens."
        ),
        "entrees_totales": len(entrees),
        "empirique": {
            "definition": "moteurs lisant des jeux déclarés admissibles comme preuve empirique dans EMPIRICAL_POLICY.json",
            "technique": dict(compteurs["empirique"]),
            "scientifique": dict(verdicts["empirique"]),
            "moteurs": dict(moteurs["empirique"].most_common()),
        },
        "modele": {
            "definition": "moteurs qui simulent, propagent ou intègrent, et jeux non admissibles comme preuve empirique",
            "technique": dict(compteurs["modele"]),
            "scientifique": dict(verdicts["modele"]),
            "moteurs": dict(moteurs["modele"].most_common()),
        },
        "indetermine": {
            "technique": dict(compteurs["indetermine"]),
            "moteurs": dict(moteurs["indetermine"].most_common()),
        },
    }
    with SORTIE.open("w", encoding="utf-8", newline="") as flux:
        flux.write(json.dumps(rapport, ensure_ascii=False, indent=2) + "\n")

    print(f"{len(entrees)} entrées réparties, sans addition entre les deux colonnes.")
    for classe in ("empirique", "modele", "indetermine"):
        total = sum(compteurs[classe].values())
        if not total:
            continue
        detail = ", ".join(
            f"{v} {k}" for k, v in sorted(compteurs[classe].items(), key=lambda kv: -kv[1])
        )
        print(f"  {classe:12s} {total:4d} entrées  ({detail})")
    print(f"écrit : {SORTIE.relative_to(ICI.parents[1])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
