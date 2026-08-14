#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "preuves" / "CORE_RESULTS.json"
REG = ROOT / "preuves" / "PREUVES.json"


def main() -> int:
    core = json.loads(CORE.read_text(encoding="utf-8"))
    reg = json.loads(REG.read_text(encoding="utf-8"))
    if core.get("schema") != "oric.core-results.v1":
        raise SystemExit("schéma CORE_RESULTS inattendu")
    items = core.get("items", [])
    if not 15 <= len(items) <= 20:
        raise SystemExit(f"le noyau externe doit contenir 15 à 20 résultats, trouvé {len(items)}")
    if core.get("count") != len(items):
        raise SystemExit("compteur CORE_RESULTS incohérent")
    ids = [x["id"] for x in items]
    if len(ids) != len(set(ids)):
        raise SystemExit("ID dupliqué dans CORE_RESULTS")
    if [x["rank"] for x in items] != list(range(1, len(items) + 1)):
        raise SystemExit("rangs CORE_RESULTS non continus")

    authority = {x["id"]: x for x in reg["entries"]}
    for x in items:
        if x["id"] not in authority:
            raise SystemExit(f"ID absent de PREUVES.json : {x['id']}")
        a = authority[x["id"]]
        for key in ("statut", "verdict", "niveau_preuve", "portee", "artefact", "empreinte_sortie"):
            if x.get(key) != a.get(key):
                raise SystemExit(f"{x['id']}: {key} diverge de PREUVES.json")
        if not (ROOT / x["artefact"]).is_file():
            raise SystemExit(f"artefact absent : {x['artefact']}")
        if x["branch"] not in {"matiere", "systeme_solaire", "vivant"}:
            raise SystemExit(f"branche inconnue : {x['branch']}")
        if not x.get("why_core", "").strip():
            raise SystemExit(f"motif de sélection absent : {x['id']}")

    branches = {x["branch"] for x in items}
    if branches != {"matiere", "systeme_solaire", "vivant"}:
        raise SystemExit(f"couverture de branches incomplète : {branches}")
    if not any(x["statut"] == "resultat_negatif" or x["verdict"] == "does_not_support" for x in items):
        raise SystemExit("aucun résultat négatif dans le noyau")
    if not any(x["statut"] == "non_concluant" for x in items):
        raise SystemExit("aucun résultat non concluant dans le noyau")
    if sum(x["statut"] == "certifie" and x["verdict"] == "supports" for x in items) < 3:
        raise SystemExit("moins de trois résultats certifiés positifs dans le noyau")
    print(f"CORE_RESULTS: {len(items)} résultats, 3 branches, statuts positifs/négatifs/non concluants présents")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
