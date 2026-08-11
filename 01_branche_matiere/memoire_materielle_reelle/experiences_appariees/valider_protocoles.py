#!/usr/bin/env python3
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REQUIRED = {
    "schema", "id", "family", "unit", "minimum_independent_units", "blocking",
    "histories", "trace_measurement", "persistence_test", "response", "ablation",
    "sham_ablation", "pairing", "blinding", "primary_endpoint", "success_rule",
    "raw_data_required", "status",
}


def validate(path: Path) -> list[str]:
    value = json.loads(path.read_text(encoding="utf-8"))
    errors = [f"champ absent: {key}" for key in sorted(REQUIRED - value.keys())]
    if len(value.get("histories", [])) < 2:
        errors.append("au moins deux histoires sont requises")
    if value.get("minimum_independent_units", 0) < 2:
        errors.append("unités indépendantes insuffisantes")
    if value.get("status") != "protocol_ready_physical_execution_required":
        errors.append("un protocole non exécuté ne peut pas porter un statut de résultat")
    return errors


def main() -> int:
    files = sorted(HERE.glob("*-PAIR-*.json"))
    failures = {p.name: validate(p) for p in files if validate(p)}
    print(json.dumps({"protocols": len(files), "failures": failures}, ensure_ascii=False))
    return 1 if failures or len(files) != 3 else 0


if __name__ == "__main__":
    raise SystemExit(main())
