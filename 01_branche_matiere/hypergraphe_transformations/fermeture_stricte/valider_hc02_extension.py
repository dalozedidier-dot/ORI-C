#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED_DOIS = {
    "10.3389/feart.2018.00180",
    "10.1029/2021GC009827",
    "10.1038/s41467-026-71130-7",
}
EXPECTED_COMPONENTS = {"interface", "fluid_chemistry", "gradients", "catalysis"}

def main() -> int:
    cfg = json.loads((HERE / "HC02_CROUTE_HYDROSPHERE_INTERFACE.json").read_text(encoding="utf-8"))
    with (HERE / "HC02_EVIDENCE_MATRIX.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter=";"))
    assert cfg["id"] == "HC02"
    assert cfg["extension_id"] == "HC02-E1"
    assert cfg["status"] == "evidence_qualified_extension"
    assert cfg["canonical_change"] is False
    assert cfg["inputs"] == ["N051", "N028"]
    assert cfg["outputs"] == ["N030"]
    assert cfg["mathematical_closure_if_added"] == "53/53"
    assert {r["component"] for r in rows} == EXPECTED_COMPONENTS
    assert all(r["verdict"] == "supported" for r in rows)
    assert EXPECTED_DOIS <= {r["doi"] for r in rows}
    diag = json.loads((HERE / "resultats" / "diagnostic_fermeture.json").read_text(encoding="utf-8"))
    assert diag["baseline_reachable"] == 46
    ext = diag["evidence_qualified_extension"]
    assert ext["id"] == "HC02-E1"
    assert ext["reachable"] == 53 and ext["total"] == 53 and ext["strictly_closed"] is True
    assert ext["frozen_baseline_reachable"] == 46
    print("HC02-E1: 4/4 semantic components supported; extension 53/53; frozen baseline 46/53")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
