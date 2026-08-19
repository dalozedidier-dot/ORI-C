#!/usr/bin/env python3
"""Revue sémantique indépendante de la qualification 4/4 de HC02-E1.

`valider_hc02_extension.py` contrôle la comptabilité de l'extension : identifiants,
DOI présents, nombres de fermeture, et `verdict == "supported"` sur chaque ligne.
Il fait donc confiance au champ `verdict` au lieu de l'éprouver, et n'ouvre jamais
la sémantique. Cette revue examine ce qu'il ne regarde pas.

Elle n'a aucune autorité pour promouvoir quoi que ce soit. Elle peut seulement
lever des objections, et toute objection fait retomber l'extension en fail-closed
sans toucher au baseline scellé 46/53, conformément à la règle 7 de
`POLITIQUE_EXTENSION_EMPIRIQUE.md`.

Quatre contrôles, tous textuels et vérifiables à la main :

A. uniformité de la force des qualificatifs déclarés dans le JSON ;
B. correspondance entre les composantes du JSON et celles de la matrice CSV ;
C. nature du lien de chaque composante aux entrées déclarées : production ou
   simple compatibilité ;
D. absence d'état intermédiaire non déclaré (règle 3 de la politique).
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ICI = Path(__file__).resolve().parent

# Marqueurs d'un lien de production à l'entrée déclarée, par opposition à un
# simple rapport de compatibilité ou de plausibilité.
PRODUCTION = re.compile(r"issue de|produite? par|à l[' ]interface|resultant de|issus? de", re.I)
COMPATIBILITE = re.compile(r"compatibles? avec|analogues? de|pertinentes? pour|plausibles?", re.I)


def charger():
    cfg = json.loads((ICI / "HC02_CROUTE_HYDROSPHERE_INTERFACE.json").read_text(encoding="utf-8"))
    with (ICI / "HC02_EVIDENCE_MATRIX.csv").open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f, delimiter=";"))
    return cfg, rows


def main() -> int:
    cfg, rows = charger()
    composantes = cfg["semantic_target"]["components"]
    objections: list[dict] = []

    # A. force des qualificatifs
    forts = {k: v for k, v in composantes.items() if v.startswith("supported_directly")}
    faibles = {k: v for k, v in composantes.items() if not v.startswith("supported_directly")}
    if faibles:
        objections.append({
            "controle": "A_uniformite_des_qualificatifs",
            "constat": (f"{len(forts)}/{len(composantes)} composantes sont déclarées "
                        f"'supported_directly'; {len(faibles)} ne l'est pas"),
            "composantes": {k: v for k, v in faibles.items()},
            "portee": ("la matrice CSV rend pourtant un verdict 'supported' identique pour toutes, "
                       "ce qui efface une différence de force que le JSON déclare lui-même"),
        })

    # B. correspondance JSON <-> CSV
    noms_csv = {r["component"] for r in rows}
    noms_json = set(composantes)
    if len(noms_csv) != len(noms_json):
        objections.append({"controle": "B_correspondance", "constat": "cardinalités différentes",
                           "csv": sorted(noms_csv), "json": sorted(noms_json)})
    elif not (noms_csv & noms_json):
        objections.append({
            "controle": "B_correspondance",
            "constat": "aucune correspondance de nom entre le JSON et la matrice CSV",
            "csv": sorted(noms_csv), "json": sorted(noms_json),
            "portee": ("rien ne vérifie par machine que les deux décrivent les mêmes quatre "
                       "composantes; l'appariement n'existe que dans la lecture humaine"),
        })

    # C. nature du lien aux entrées déclarées
    for r in rows:
        sem = r["required_semantics"]
        prod, compat = bool(PRODUCTION.search(sem)), bool(COMPATIBILITE.search(sem))
        if compat and not prod:
            objections.append({
                "controle": "C_lien_aux_entrees",
                "composante": r["component"],
                "semantique_exigee": sem,
                "constat": ("la sémantique exigée établit une compatibilité, pas une production "
                            "par les entrées déclarées N051+N028"),
                "source": f"{r['primary_source']} ({r['doi']})",
                "portee": ("la règle 2 de la politique demande que chaque composante indispensable "
                           "du nœud de sortie soit reliée à une source primaire; une phase "
                           "seulement compatible avec l'altération primitive n'établit pas que la "
                           "capacité catalytique est portée par le produit de N051+N028"),
            })

    # D. état intermédiaire non déclaré
    sources = {r["primary_source"] for r in rows}
    if len(sources) > 1:
        hors_chaine = [r["component"] for r in rows
                       if r["primary_source"] not in
                       {x for x in sources if any(y["primary_source"] == x and
                                                  PRODUCTION.search(y["required_semantics"])
                                                  for y in rows)}]
        if hors_chaine:
            objections.append({
                "controle": "D_etat_intermediaire",
                "composantes": hors_chaine,
                "constat": ("ces composantes reposent sur une source qui ne documente aucune "
                            "production à partir des entrées déclarées"),
                "portee": ("règle 3 : l'enchaînement doit rester dans une même classe physique "
                           "sans introduire d'état intermédiaire non déclaré"),
            })

    verdict = "fail_closed" if objections else "qualification_confirmee"
    rapport = {
        "schema": "oric.hc02-independent-semantic-review.v1",
        "date": "2026-08-19",
        "objet": "HC02-E1",
        "methode": ("revue indépendante du contenu sémantique; ne rejoue pas les contrôles "
                    "structurels de valider_hc02_extension.py"),
        "composantes_examinees": len(composantes),
        "objections": objections,
        "verdict": verdict,
        "effet": ("aucun" if not objections else
                  "l'extension HC02-E1 retombe en fail-closed; le baseline scellé 46/53 est "
                  "inchangé et reste l'état publié"),
        "baseline_intouche": "46/53",
        "regle_appliquee": "POLITIQUE_EXTENSION_EMPIRIQUE.md, règles 2, 3 et 7",
    }
    (ICI / "resultats" / "REVUE_SEMANTIQUE_HC02_2026-08-19.json").write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="")
    print(json.dumps(rapport, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
