from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "plateforme/source_corrigee/src/oric_full/resources/catalogue_tests.csv"
COVERAGE = ROOT / "plateforme/campagne_maximale_reelle/data/REAL_DATA_COVERAGE.json"
QUARANTINED = {"condensation", "volatile_budget", "late_accretion", "planetary_value"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.results.read_text(encoding="utf-8"))
    if not payload.get("metadata", {}).get("real_data_only"):
        raise SystemExit("résultat non produit avec --real-data-only")

    with CATALOGUE.open(encoding="utf-8", newline="") as handle:
        specs = {row["test_id"]: row for row in csv.DictReader(handle)}
    coverage = json.loads(COVERAGE.read_text(encoding="utf-8")).get("datasets", {})

    errors: list[str] = []
    for result in payload.get("results", []):
        if result.get("outcome") != "pass":
            continue
        test_id = result.get("test_id", "")
        spec = specs.get(test_id)
        if spec is None:
            errors.append(f"PASS inconnu: {test_id}")
            continue
        engine = spec.get("engine", "")
        if engine in QUARANTINED:
            errors.append(f"{test_id}: PASS interdit avec moteur en quarantaine {engine}")
        required = [item for item in spec.get("required_datasets", "").split(";") if item]
        for dataset in required:
            scope = coverage.get(dataset)
            if not scope:
                errors.append(f"{test_id}: dataset {dataset} absent du registre réel")
                continue
            if scope.get("scope_mode") != "allow_list":
                errors.append(f"{test_id}: dataset {dataset} non fail-closed")
                continue
            if test_id not in set(scope.get("supported_test_ids", [])):
                errors.append(f"{test_id}: dataset {dataset} ne couvre pas explicitement ce test")

    if errors:
        print("VALIDATION EXECUTION REELLE STRICTE: ECHEC")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALIDATION EXECUTION REELLE STRICTE: OK")
    print(json.dumps(payload.get("counts", {}), ensure_ascii=False, sort_keys=True))
    print(json.dumps(payload.get("scientific_counts", {}), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
