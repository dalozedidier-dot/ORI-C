#!/usr/bin/env python3
"""Adapte les artefacts d'autorité au format transversal sans inventer de mesure."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "resultats"
SCHEMA_PATH = HERE / "SCHEMA_RESULTAT_COMMUN.json"
FIELDS = ["X", "H", "m", "Theta", "tau", "P_acc", "R"]


def _benchmark() -> dict:
    path = HERE / "construire_benchmark_transversal.py"
    spec = importlib.util.spec_from_file_location("oric_benchmark_for_common_results", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.build()[0]


def _definition(case: dict, field: str) -> str | None:
    if field == "m":
        return case["m_operational_definition"]
    if field == "P_acc":
        return case["P_acc_operational_definition"]
    defaults = {
        "X": "état présent apparié défini par le protocole source",
        "H": "histoire antérieure définie par le protocole source",
        "Theta": "conditions et paramètres du protocole source",
        "tau": case["tau_quality"]["kind"],
        "R": "réponse ou résultat défini par l'artefact d'autorité",
    }
    return defaults.get(field)


def build() -> dict:
    benchmark = _benchmark()
    items = []
    for case in benchmark["cases"]:
        fields = {}
        for field in FIELDS:
            covered = case["field_coverage"][field]
            if not covered:
                status = "missing"
            elif field in {"m", "P_acc"} and "derived" in case["measurement_quality"].get(field, ""):
                status = "derived"
            else:
                status = "measured"
            fields[field] = {"status": status, "definition": _definition(case, field) if covered else None}
        causal = case["causal_test_class"]
        items.append({
            "id": case["id"],
            "system": case["system_id"],
            "dataset": case["artifact"],
            "provenance": {"artifact": case["artifact"], "scope": case["scope"]},
            **fields,
            "intervention": None if causal.startswith("retrospective") or causal == "not_classified_for_INV_A" else {"class": causal},
            "control": None if causal == "not_classified_for_INV_A" else {"class": causal},
            "independent_unit": case["replication_unit"],
            "frozen_threshold": None,
            "result": {
                "evidence_level": case["evidence_level"],
                "measurement_status": case["m_P_acc_measurement_status"],
                "field_complete": case["eligible_for_common_invariant"],
                "measurement_quality": case["measurement_quality"],
            },
            "verdict": case["verdict"],
            "sha256": case["artifact_sha256"],
        })

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = []
    for item in items:
        errors.extend(f"{item['id']}: {error.message}" for error in validator.iter_errors(item))
    if errors:
        raise ValueError("invalid common results:\n" + "\n".join(errors))
    return {
        "schema": "oric.common-results-bundle.v1",
        "item_schema": "SCHEMA_RESULTAT_COMMUN.json",
        "items": items,
        "counts": {
            "total": len(items),
            "field_complete_cases": sum(item["result"]["field_complete"] for item in items),
            "field_complete_unique_systems": len({item["system"] for item in items if item["result"]["field_complete"]}),
            "empirical_or_model_levels_preserved": True
        },
        "rule": "Une propriété obligatoire peut rester status=missing; le schéma interdit de transformer une définition ou une préparation en mesure."
    }


def main() -> int:
    bundle = build()
    OUT.mkdir(exist_ok=True)
    (OUT / "RESULTATS_COMMUNS.json").write_text(
        json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"résultats communs: {bundle['counts']['field_complete_cases']}/{bundle['counts']['total']} cas complets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
