#!/usr/bin/env python3
"""Contrôle que le gel PALEO-HISTORY-02 est intact.

Tant que `sceller.py --appliquer` n'a pas tourné, il n'y a pas de gel : le script
le dit et sort en 0, parce qu'un projet non scellé n'est pas une anomalie.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
GEL = HERE / "GEL_PALEO_HISTORY_02.json"


def main() -> int:
    if not GEL.is_file():
        print("PALEO-HISTORY-02 : projet non scelle, aucun gel a verifier")
        return 0
    gel = json.loads(GEL.read_text(encoding="utf-8"))
    divergences = []
    for nom, attendu in gel["fichiers"].items():
        reel = hashlib.sha256((HERE / nom).read_bytes()).hexdigest()
        if reel != attendu:
            divergences.append({"fichier": nom, "attendu": attendu, "reel": reel})
    if divergences:
        print(json.dumps(divergences, ensure_ascii=False, indent=2))
        return 1
    print(f"PALEO-HISTORY-02 : gel intact, {len(gel['fichiers'])} fichiers conformes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
