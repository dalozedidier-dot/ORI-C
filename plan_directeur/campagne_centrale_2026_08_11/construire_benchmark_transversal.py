#!/usr/bin/env python3
"""Construit le benchmark transversal depuis les artefacts réels, sans compléter les champs absents."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "resultats"
SELECTED = [
    "C-ANT-01", "C-VES-02", "C-VES-03", "C-MAT-MEM-05", "C-AST-01",
    "MPT-M2-01", "PID-ANT-01", "GCQ-T09", "GCQ-T10", "GCQ-T11",
    "GCQ-T12", "GCQ-T13", "GCQ-T14", "GCQ-T15", "GCQ-T16", "GCQ-T17",
    "GCQ-T18", "GCQ-T19", "GCQ-T20", "GCQ-T21",
]
FIELDS = ["X", "H", "m", "Theta", "tau", "P_acc", "R"]

# Couverture déclarée à partir des protocoles et non inférée d'un verdict.
COVERAGE = {
    "C-ANT-01": {"X", "H", "Theta", "tau", "R"},
    "C-VES-02": {"X", "H", "m", "Theta", "tau", "P_acc", "R"},
    "C-VES-03": {"X", "H", "m", "Theta", "tau", "R"},
    "C-MAT-MEM-05": {"H", "m", "Theta", "tau", "R"},
    "C-AST-01": {"X", "H", "Theta", "tau", "P_acc", "R"},
    "MPT-M2-01": {"X", "H", "Theta", "tau", "R"},
    "PID-ANT-01": {"X", "H", "m", "Theta", "tau", "R"},
    "GCQ-T09": {"X", "H", "Theta", "tau", "P_acc", "R"},
}


def build() -> tuple[dict, dict]:
    registry_path = ROOT / "preuves/PREUVES.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    by_id = {entry["id"]: entry for entry in registry["entries"]}
    operationalization_path = HERE / "OPERATIONNALISATION_M_PACC_20_CAS.json"
    operationalization = json.loads(operationalization_path.read_text(encoding="utf-8"))
    op_by_id = {case["id"]: case for case in operationalization["cases"]}
    cases = []
    for case_id in SELECTED:
        entry = by_id[case_id]
        artifact = ROOT / entry["artefact"]
        present = artifact.is_file()
        covered = COVERAGE.get(case_id, {"X", "H", "Theta", "tau", "R"})
        op = op_by_id[case_id]
        cases.append({
            "id": case_id,
            "question": entry["question"],
            "verdict": entry["verdict"],
            "evidence_level": entry["niveau_preuve"],
            "scope": entry["portee"],
            "artifact": entry["artefact"],
            "artifact_present": present,
            "artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest() if present else None,
            "m_operational_definition": op["m"],
            "P_acc_operational_definition": op["P_acc"],
            "m_P_acc_measurement_status": op["measurement_status"],
            "field_coverage": {field: field in covered for field in FIELDS},
            "missing_fields": [field for field in FIELDS if field not in covered],
            "eligible_for_common_invariant": all(field in covered for field in FIELDS),
        })
    benchmark = {
        "schema": "oric.transversal-benchmark.v1",
        "selection": "20 cas réels ou résultats de modèle explicitement qualifiés, sélectionnés avant tout test transversal",
        "case_count": len(cases),
        "required_fields": FIELDS,
        "operational_definitions_complete": len(op_by_id) == len(SELECTED),
        "warning": "définition opérationnelle complète ne signifie pas mesure disponible",
        "cases": cases,
    }
    eligible = [case["id"] for case in cases if case["eligible_for_common_invariant"]]
    invariants = {
        "schema": "oric.transversal-invariants-audit.v1",
        "cases_total": len(cases),
        "cases_complete_X_H_m_Theta_tau_Pacc_R": len(eligible),
        "eligible_case_ids": eligible,
        "tests": [
            {"id": "INV-A", "hypothesis": "Delta m -> Delta P_acc", "status": "non_testable"},
            {"id": "INV-B", "hypothesis": "tau_m/tau_T -> force historique", "status": "non_testable"},
            {"id": "INV-C", "hypothesis": "transitions irréversibles ferment et ouvrent des possibles", "status": "non_testable"},
            {"id": "INV-D", "hypothesis": "information historique décroît ou change de support", "status": "non_testable"},
            {"id": "INV-E", "hypothesis": "interfaces disproportionnées", "status": "non_testable"},
        ],
        "verdict": "un premier cas empirique rétrospectif est complet; aucun invariant transversal n'est testable sur un cas unique",
        "rule": "l'hétérogénéité des métriques n'est pas masquée par une standardisation arbitraire",
    }
    return benchmark, invariants


def main() -> int:
    OUT.mkdir(exist_ok=True)
    benchmark, invariants = build()
    for name, value in (("BENCHMARK_TRANSVERSAL.json", benchmark), ("AUDIT_INVARIANTS.json", invariants)):
        (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"{benchmark['case_count']} cas; {invariants['cases_complete_X_H_m_Theta_tau_Pacc_R']} complet(s); invariants={invariants['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
