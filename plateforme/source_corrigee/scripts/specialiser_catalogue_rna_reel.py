"""Affecte uniquement les questions couvertes par les fréquences ARN expérimentales."""
from __future__ import annotations
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = {"V2-006", "V2-012", "V2-024", "V2-025", "V2-027", "V2-030", "V4-014", "V5-004", "V5-007", "V5-008", "V6-001"}
JSON_PATHS = [ROOT / "catalogue" / "catalogue_tests.json", ROOT / "src" / "oric_full" / "resources" / "catalogue_tests.json"]
CSV_PATHS = [ROOT / "catalogue" / "catalogue_tests.csv", ROOT / "src" / "oric_full" / "resources" / "catalogue_tests.csv"]

def update(item: dict) -> None:
    if item.get("test_id") in TESTS:
        item["engine"] = "prebiotic_rna_evolution"
        item["required_datasets"] = ["prebiotic_rna_evolution"] if isinstance(item.get("required_datasets"), list) else "prebiotic_rna_evolution"

def main() -> None:
    for path in JSON_PATHS:
        rows = json.loads(path.read_text(encoding="utf-8"))
        for row in rows: update(row)
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for path in CSV_PATHS:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream); rows = list(reader); fields = reader.fieldnames
        for row in rows: update(row)
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"tests_specialises": len(TESTS), "test_ids": sorted(TESTS)}))

if __name__ == "__main__": main()
