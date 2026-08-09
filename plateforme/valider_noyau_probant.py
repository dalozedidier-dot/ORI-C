#!/usr/bin/env python3
"""Valide et matérialise le noyau probant actif sans altérer le catalogue canonique des 683 tests."""
from __future__ import annotations
import argparse, csv, json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATALOGUE = ROOT / "catalogue_tests.csv"
POLITIQUE = ROOT / "POLITIQUE_NOYAU_PROBANT.csv"
ATTENDU_TOTAL = 683
ATTENDU_GARDER = 366
ATTENDU_VIRER = 317


def lire_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def valider(catalogue: list[dict[str, str]], politique: list[dict[str, str]]) -> dict:
    ids_catalogue = [r["test_id"] for r in catalogue]
    ids_politique = [r["test_id"] for r in politique]
    if len(catalogue) != ATTENDU_TOTAL or len(set(ids_catalogue)) != ATTENDU_TOTAL:
        raise ValueError("catalogue canonique différent des 683 IDs uniques attendus")
    if len(politique) != ATTENDU_TOTAL or len(set(ids_politique)) != ATTENDU_TOTAL:
        raise ValueError("politique incomplète ou IDs dupliqués")
    if set(ids_catalogue) != set(ids_politique):
        manque = sorted(set(ids_catalogue) - set(ids_politique))
        surplus = sorted(set(ids_politique) - set(ids_catalogue))
        raise ValueError(f"politique non bijective avec le catalogue: manque={manque[:5]}, surplus={surplus[:5]}")
    decisions = Counter(r["decision"] for r in politique)
    if decisions != Counter({"GARDER": ATTENDU_GARDER, "VIRER": ATTENDU_VIRER}):
        raise ValueError(f"compteurs de tri inattendus: {dict(decisions)}")
    par_id = {r["test_id"]: r for r in politique}
    confirmatoires = [r["test_id"] for r in catalogue if r["confirmatory"].strip().lower() == "true"]
    retires = [tid for tid in confirmatoires if par_id[tid]["decision"] != "GARDER"]
    if retires:
        raise ValueError(f"tests confirmatoires exclus du noyau probant: {retires}")
    destinations = Counter(r["destination"] for r in politique)
    if destinations != Counter({"noyau_probant": ATTENDU_GARDER, "qa_exploratoire": ATTENDU_VIRER}):
        raise ValueError(f"destinations incohérentes: {dict(destinations)}")
    return {
        "schema": "oric.evidence-core-policy.v1",
        "catalogue_total": len(catalogue),
        "noyau_probant": ATTENDU_GARDER,
        "qa_exploratoire": ATTENDU_VIRER,
        "confirmatoires_total": len(confirmatoires),
        "confirmatoires_conserves": len(confirmatoires),
        "regle": "Le tri organise les cibles de preuve; il ne constitue ni un verdict scientifique ni une modification des 683 entrées canoniques.",
    }


def ecrire_noyau(catalogue, politique, sortie: Path) -> None:
    keep = {r["test_id"] for r in politique if r["decision"] == "GARDER"}
    lignes = [r for r in catalogue if r["test_id"] in keep]
    sortie.parent.mkdir(parents=True, exist_ok=True)
    with sortie.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=catalogue[0].keys())
        w.writeheader(); w.writerows(lignes)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--sortie-csv", type=Path)
    p.add_argument("--sortie-json", type=Path)
    args = p.parse_args()
    catalogue, politique = lire_csv(CATALOGUE), lire_csv(POLITIQUE)
    resume = valider(catalogue, politique)
    if args.sortie_csv:
        ecrire_noyau(catalogue, politique, args.sortie_csv)
    if args.sortie_json:
        args.sortie_json.parent.mkdir(parents=True, exist_ok=True)
        args.sortie_json.write_text(json.dumps(resume, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(resume, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
