#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXEC = HERE / "MAG-PAIR-001.execution.json"
UNITS = HERE / "mag_pair_001_units.csv"
MEASUREMENTS = HERE / "mag_pair_001_measurements.csv"
READY = HERE / "mag_pair_001_analysis_ready.csv"
RESULT = HERE / "MAG-PAIR-001.result.json"


def main() -> int:
    execution = json.loads(EXEC.read_text(encoding="utf-8"))
    fields = execution.get("frozen_fields", {})
    instrument_required = (
        "af_plateau_mT",
        "test_field_mT",
        "temperature_target_c",
        "temperature_tolerance_c",
    )
    missing_instrument = [name for name in instrument_required if fields.get(name) is None]

    if UNITS.exists() != MEASUREMENTS.exists():
        raise SystemExit("MAG raw bundle incomplete: units and measurements files must appear together")
    if (UNITS.exists() or READY.exists() or RESULT.exists()) and missing_instrument:
        raise SystemExit(
            "MAG real data are present but required instrument parameters are missing: "
            + ", ".join(missing_instrument)
        )
    if RESULT.exists() and not READY.exists():
        raise SystemExit("MAG result present without the analysis-ready real-data table")

    registration = execution.get("registration", {})
    registration_complete = bool(registration.get("public_url") and registration.get("registered_at"))
    print(
        "MAG-PAIR-001 code/data gate valid: "
        f"instrument_freeze={'complete' if not missing_instrument else 'awaiting real pilot'}, "
        f"raw_bundle={'present' if UNITS.exists() else 'absent'}, "
        f"analysis_ready={'present' if READY.exists() else 'absent'}, "
        f"result={'present' if RESULT.exists() else 'absent'}, "
        f"external_registration={'complete' if registration_complete else 'not blocking'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
