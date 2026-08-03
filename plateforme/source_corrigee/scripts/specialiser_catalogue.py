"""Affecte les questions paléoclimatiques à des moteurs sémantiquement adaptés."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATHS = [ROOT / "catalogue" / "catalogue_tests.csv"]
JSON_PATHS = [
    ROOT / "catalogue" / "catalogue_tests.json",
    ROOT / "src" / "oric_full" / "resources" / "catalogue_tests.json",
]

RULES = [
    ("climate_chronology", r"chronolog|incertitudes? d.age|datation|âge"),
    ("climate_proxy_robustness", r"prox(?:y|ys)|pile benthique|niveau marin|CO2|température|poussi"),
    ("climate_hysteresis", r"hystér|multistab|bifurcation|seuil"),
    ("climate_spectra", r"spectr|fréquen|périod|bande"),
    ("climate_identifiability", r"identifi|coliné|paramètre|normalisation"),
    ("climate_path_dependence", r"dépendance au chemin|chemin|irrévers|renversement temporel"),
]
ELIGIBLE = {
    "paleoclimate_replication", "paleoclimate_prospective", "memory_families",
    "climate_models", "climate_data", "climate_discrimination", "climate_mechanisms",
}


def choose(item: dict) -> str:
    if item.get("engine") not in ELIGIBLE:
        return item.get("engine", "")
    text = f"{item.get('section', '')} {item.get('description', '')}"
    for engine, pattern in RULES:
        if re.search(pattern, text, re.I):
            return engine
    return item["engine"]


def main() -> int:
    changes = []
    for path in JSON_PATHS:
        items = json.loads(path.read_text(encoding="utf-8"))
        for item in items:
            old, new = item.get("engine", ""), choose(item)
            if new != old:
                item["engine"] = new
                changes.append((item["test_id"], old, new))
        path.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for path in CSV_PATHS:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
            fields = stream.seek(0) or list(rows[0])
        for item in rows:
            item["engine"] = choose(item)
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    unique = sorted(set(changes))
    report = {"affectations_uniques": len(unique), "changements": [dict(test_id=a, ancien=b, nouveau=c) for a, b, c in unique]}
    (ROOT / "audit" / "moteurs_specialises.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
