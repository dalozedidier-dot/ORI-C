#!/usr/bin/env python3
"""Valide et matérialise le noyau probant sans modifier le catalogue canonique."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATALOGUE = ROOT / "catalogue_tests.csv"
POLITIQUE = ROOT / "POLITIQUE_NOYAU_PROBANT.csv"
ATTENDU_TOTAL = 683
ATTENDU_GARDER = 366
ATTENDU_VIRER = 317
CHAMPS_POLITIQUE = ["test_id", "decision", "destination", "rang_action", "motif_code"]
DECISIONS = {"GARDER", "VIRER"}
DESTINATIONS = {"GARDER": "noyau_probant", "VIRER": "qa_exploratoire"}
RANGS = {"1", "2", "3"}
MOTIFS_GARDER = {
    "CONFIRMATOIRE",
    "PREDICTION_HORS_ECHANTILLON",
    "REPLICATION_INDEPENDANTE",
    "INTERVENTION_HISTOIRE",
    "CONTROLE_ANTI_FAUX_POSITIF",
    "DOMAINE_ACCESSIBLE",
    "INTEGRITE_CONFIRMATOIRE",
    "VALEUR_PREDICTIVE",
    "SOUS_TEST_NECESSAIRE",
}
MOTIFS_VIRER = {
    "QA_REPRODUCTIBILITE_NUMERIQUE",
    "INVENTAIRE_NON_DISCRIMINANT",
    "REDONDANCE_MODELES_CONCURRENTS",
    "BENCHMARK_NON_EMPIRIQUE",
    "COMPRESSION_NON_PROBANTE",
    "QA_SIMULATION",
    "PREPARATION_DOCUMENTATION",
    "ROBUSTESSE_PARAMETRIQUE",
    "APPARIEMENT_INTEGRE",
    "REDONDANCE_SOUS_ANALYSE",
}


def lire_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        lecteur = csv.DictReader(f)
        return list(lecteur.fieldnames or []), list(lecteur)


def valider(catalogue: list[dict[str, str]], politique: list[dict[str, str]], champs: list[str]) -> dict:
    if champs != CHAMPS_POLITIQUE:
        raise ValueError(f"colonnes de politique inattendues : {champs}")

    ids_catalogue = [r["test_id"] for r in catalogue]
    ids_politique = [r["test_id"] for r in politique]
    if len(catalogue) != ATTENDU_TOTAL or len(set(ids_catalogue)) != ATTENDU_TOTAL:
        raise ValueError("catalogue canonique différent des 683 IDs uniques attendus")
    if len(politique) != ATTENDU_TOTAL or len(set(ids_politique)) != ATTENDU_TOTAL:
        raise ValueError("politique incomplète ou IDs dupliqués")
    if set(ids_catalogue) != set(ids_politique):
        manque = sorted(set(ids_catalogue) - set(ids_politique))
        surplus = sorted(set(ids_politique) - set(ids_catalogue))
        raise ValueError(f"politique non bijective : manque={manque[:5]}, surplus={surplus[:5]}")

    for ligne in politique:
        decision = ligne["decision"]
        if decision not in DECISIONS:
            raise ValueError(f"décision inconnue pour {ligne['test_id']} : {decision}")
        destination = ligne["destination"]
        if destination != DESTINATIONS[decision]:
            raise ValueError(f"destination incohérente pour {ligne['test_id']} : {destination}")
        rang = ligne["rang_action"]
        motif = ligne["motif_code"]
        if decision == "GARDER":
            if rang not in RANGS:
                raise ValueError(f"rang_action invalide pour {ligne['test_id']} : {rang}")
            if motif not in MOTIFS_GARDER:
                raise ValueError(f"motif GARDER invalide pour {ligne['test_id']} : {motif}")
        else:
            if rang:
                raise ValueError(f"un test VIRER ne doit pas porter de rang_action : {ligne['test_id']}")
            if motif not in MOTIFS_VIRER:
                raise ValueError(f"motif VIRER invalide pour {ligne['test_id']} : {motif}")

    decisions = Counter(r["decision"] for r in politique)
    attendu = Counter({"GARDER": ATTENDU_GARDER, "VIRER": ATTENDU_VIRER})
    if decisions != attendu:
        raise ValueError(f"compteurs de tri inattendus : {dict(decisions)}")

    par_id = {r["test_id"]: r for r in politique}
    confirmatoires = [
        r["test_id"] for r in catalogue
        if r["confirmatory"].strip().lower() == "true"
    ]
    retires = [tid for tid in confirmatoires if par_id[tid]["decision"] != "GARDER"]
    if retires:
        raise ValueError(f"tests confirmatoires exclus du noyau probant : {retires}")

    return {
        "schema": "oric.evidence-core-policy.v2",
        "catalogue_total": len(catalogue),
        "noyau_probant": ATTENDU_GARDER,
        "qa_exploratoire": ATTENDU_VIRER,
        "confirmatoires_total": len(confirmatoires),
        "confirmatoires_conserves": len(confirmatoires),
        "regle": (
            "Le tri organise les cibles de preuve ; il ne constitue ni un verdict scientifique "
            "ni une modification des 683 entrées canoniques."
        ),
    }


def ecrire_noyau(catalogue: list[dict[str, str]], politique: list[dict[str, str]], sortie: Path) -> None:
    garder = {r["test_id"] for r in politique if r["decision"] == "GARDER"}
    lignes = [r for r in catalogue if r["test_id"] in garder]
    sortie.parent.mkdir(parents=True, exist_ok=True)
    with sortie.open("w", encoding="utf-8", newline="") as f:
        ecrivain = csv.DictWriter(f, fieldnames=catalogue[0].keys())
        ecrivain.writeheader()
        ecrivain.writerows(lignes)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sortie-csv", type=Path)
    parser.add_argument("--sortie-json", type=Path)
    args = parser.parse_args()

    _, catalogue = lire_csv(CATALOGUE)
    champs, politique = lire_csv(POLITIQUE)
    resume = valider(catalogue, politique, champs)
    if args.sortie_csv:
        ecrire_noyau(catalogue, politique, args.sortie_csv)
    if args.sortie_json:
        args.sortie_json.parent.mkdir(parents=True, exist_ok=True)
        args.sortie_json.write_text(
            json.dumps(resume, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(resume, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
