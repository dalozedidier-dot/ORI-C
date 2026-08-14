#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
P = HERE / "PROTOCOLE_PACC_CAUSAL_PROSPECTIF_V1.json"
A = HERE / "analyser_ves_pacc_int_01.py"
R = HERE / "VES-PACC-INT-01.registration.json"
E = HERE / "VES-PACC-INT-01.execution.json"
INPUT = HERE / "ves_pacc_int_01_analysis_ready.npz"
META = HERE / "ves_pacc_int_01_analysis_ready.metadata.json"
RESULT = HERE / "resultats" / "RESULTAT_VES_PACC_INT_01.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if not P.exists() or not A.exists() or not E.exists():
        raise SystemExit("VES code gate incomplete: protocol, analyser or execution file missing")
    json.loads(P.read_text(encoding="utf-8"))
    json.loads(E.read_text(encoding="utf-8"))

    if INPUT.exists() != META.exists():
        raise SystemExit("VES analysis bundle incomplete: NPZ and metadata JSON must appear together")
    if RESULT.exists() and not (INPUT.exists() and META.exists()):
        raise SystemExit("VES result present without its analysis-ready real-data bundle")
    if META.exists():
        meta = json.loads(META.read_text(encoding="utf-8"))
        if meta.get("protocol_sha256") != sha(P):
            raise SystemExit("VES analysis-ready metadata point to another protocol SHA-256")

    registration = json.loads(R.read_text(encoding="utf-8")) if R.exists() else {}
    registration_complete = bool(
        registration.get("status") == "publicly_registered"
        and registration.get("public_url")
        and registration.get("registered_at")
    )
    print(
        "VES-PACC-INT-01 code/data gate valid: "
        f"analysis_bundle={'present' if INPUT.exists() else 'absent'}, "
        f"result={'present' if RESULT.exists() else 'absent'}, "
        f"external_registration={'complete' if registration_complete else 'not blocking'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
