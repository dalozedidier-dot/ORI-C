#!/usr/bin/env python3
"""Scelle PALEO-HISTORY-02, une fois et seulement une fois.

Le scellement est un acte : il fige le critère avant que la cible ne soit ouverte.
Ce script refuse donc de sceller tant qu'une décision reste ouverte, tant que le
contrôle négatif n'est pas acquis, ou si un gel existe déjà.

    python sceller.py            # controle et refuse si un prealable manque
    python sceller.py --appliquer
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCELLES = ("PROTOCOLE.md", "SCHEMA_DONNEES.json", "PLAN_ANALYSE.json")
GEL = HERE / "GEL_PALEO_HISTORY_02.json"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def prealables() -> list[str]:
    """Ce qui doit être réglé avant que le scellement ait un sens."""
    manques = []
    if GEL.is_file():
        manques.append("un gel existe deja; modifier un fichier scelle exige un nouveau numero")
    plan = json.loads((HERE / "PLAN_ANALYSE.json").read_text(encoding="utf-8"))
    schema = json.loads((HERE / "SCHEMA_DONNEES.json").read_text(encoding="utf-8"))
    if plan.get("decisions_a_trancher_avant_scellement"):
        for d in plan["decisions_a_trancher_avant_scellement"]:
            manques.append(f"decision ouverte: {d}")
    if plan.get("realisations_chronologiques", {}).get("graine") is None:
        manques.append("graine des realisations chronologiques non declaree")
    cn = schema.get("controle_negatif_reel", {})
    if cn.get("statut_acquisition") != "acquis":
        manques.append("controle negatif reel non acquis")
    if "projet_non_scelle" in (plan.get("statut", ""), schema.get("statut", "")):
        manques.append("statut encore 'projet_non_scelle' dans PLAN_ANALYSE ou SCHEMA_DONNEES")
    return manques


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--appliquer", action="store_true", help="ecrit le gel")
    args = ap.parse_args()

    manques = prealables()
    if manques:
        print("Scellement refuse. Prealables non satisfaits :")
        for m in manques:
            print(f"  - {m}")
        return 1
    if not args.appliquer:
        print("Prealables satisfaits. Relancer avec --appliquer pour sceller.")
        return 0

    gel = {
        "campaign_id": "PALEO-HISTORY-02",
        "status": "gele_avant_execution",
        "frozen_on": datetime.date.today().isoformat(),
        "herite_de": "PALEO-HISTORY-01",
        "regle": (
            "Toute modification d'un fichier scelle exige un nouveau numero de protocole "
            "et une justification publique ; les resultats anterieurs ne peuvent pas etre "
            "requalifies retroactivement."
        ),
        "fichiers": {nom: sha256(HERE / nom) for nom in SCELLES},
    }
    GEL.write_text(json.dumps(gel, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8", newline="")
    print(f"PALEO-HISTORY-02 scelle : {len(SCELLES)} fichiers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
