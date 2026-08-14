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


def _branch(case: dict) -> str:
    artifact = case["artifact"]
    if artifact.startswith("01_branche_matiere/"):
        return "matiere"
    if artifact.startswith("02_branche_systeme_solaire/") or case["id"].startswith(("C-AST", "MPT", "EXO")):
        return "systeme_solaire"
    return "vivant"


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
    registry = json.loads((ROOT / "preuves/PREUVES.json").read_text(encoding="utf-8"))
    authority = {entry["id"]: entry for entry in registry["entries"]}
    items = []
    for case in benchmark["cases"]:
        evidence = authority[case["id"]]
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
        direct_intervention = causal in {"m_ablation", "architecture_intervention"}
        items.append({
            "id": case["id"],
            "branch": _branch(case),
            "system": case["system_id"],
            "dataset": evidence.get("source") or case["artifact"],
            "provenance": {
                "artifact": case["artifact"],
                "source": evidence.get("source"),
                "scope": case["scope"]
            },
            **fields,
            "intervention": {"class": causal} if direct_intervention else None,
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


def derive_views(bundle: dict) -> tuple[dict, dict]:
    branches = {}
    for branch in ("matiere", "systeme_solaire", "vivant"):
        rows = [item for item in bundle["items"] if item["branch"] == branch]
        branches[branch] = {
            "cases": len(rows),
            "field_complete_cases": sum(row["result"]["field_complete"] for row in rows),
            "systems": sorted({row["system"] for row in rows}),
            "direct_intervention_cases": [row["id"] for row in rows if row["intervention"] is not None],
            "missing_by_field": {
                field: [row["id"] for row in rows if row[field]["status"] == "missing"]
                for field in FIELDS
            },
        }
    matrix = {
        "schema": "oric.common-branch-matrix.v1",
        "source_schema": bundle["schema"],
        "branches": branches,
        "rule": "Les comptes de complétude ne fusionnent pas les niveaux de preuve ni les unités physiques."
    }
    proofs = {
        "schema": "oric.common-associated-evidence.v1",
        "items": [
            {
                "id": row["id"],
                "branch": row["branch"],
                "artifact": row["provenance"]["artifact"],
                "source": row["provenance"].get("source"),
                "sha256": row["sha256"],
                "verdict": row["verdict"],
                "field_complete": row["result"]["field_complete"]
            }
            for row in bundle["items"]
        ],
        "rule": "Chaque preuve reste reliée à son artefact d'autorité et à son empreinte; aucun nom de fichier ne décide seul du verdict."
    }
    return matrix, proofs


def main() -> int:
    bundle = build()
    matrix, proofs = derive_views(bundle)
    OUT.mkdir(exist_ok=True)
    for name, value in (
        ("RESULTATS_COMMUNS.json", bundle),
        ("MATRICE_BRANCHES_COMMUNE.json", matrix),
        ("PREUVES_ASSOCIEES_COMMUNES.json", proofs),
    ):
        (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"résultats communs: {bundle['counts']['field_complete_cases']}/{bundle['counts']['total']} cas complets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
