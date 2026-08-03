"""Sépare les contrôles techniques des soutiens scientifiques à ORI-C."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "resultats" / "results.csv"
OUTPUT = ROOT / "resultats" / "classification_soutiens.json"

POSITIVE_CONTROLS = {"A1-003", "A5-001", "A5-002", "A5-004"}
PROTOCOL_CHECKS = {"C5-009"}
NON_COMPARABLE = {"C6-001"}


def category(test_id: str, verdict: str) -> str:
    if test_id in POSITIVE_CONTROLS:
        return "controle_positif_astronomique"
    if test_id in PROTOCOL_CHECKS:
        return "controle_de_protocole"
    if test_id in NON_COMPARABLE:
        return "comparaison_non_interpretable"
    if verdict == "supports":
        return "soutien_oric_a_examiner"
    return "hors_soutiens"


def main() -> int:
    with RESULTS.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    classified = []
    for row in rows:
        label = category(row["test_id"], row["scientific_verdict"])
        if row["scientific_verdict"] == "supports":
            classified.append({
                "test_id": row["test_id"],
                "verdict_brut": row["scientific_verdict"],
                "categorie": label,
                "soutien_scientifique_oric_defendable": label == "soutien_oric_a_examiner",
            })
    counts = Counter(item["categorie"] for item in classified)
    report = {
        "supports_bruts": len(classified),
        "soutiens_scientifiques_oric_defendables": sum(
            item["soutien_scientifique_oric_defendable"] for item in classified
        ),
        "comptes_par_categorie": dict(sorted(counts.items())),
        "details": classified,
        "note": (
            "C5-009 contrôle une fraction de holdout. C6-001 compare des RMSE "
            "issues de modèles et procédures non comparables. Ils ne valident pas ORI-C."
        ),
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
