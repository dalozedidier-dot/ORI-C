#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "MAG-PAIR-001.json"
EXEC = HERE / "MAG-PAIR-001.execution.json"
UNITS = HERE / "mag_pair_001_units.csv"
MEAS = HERE / "mag_pair_001_measurements.csv"
OUT = HERE / "mag_pair_001_analysis_ready.csv"


def f(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("non-finite MAG measurement")
    return number


def magnitude(row: dict[str, str]) -> float:
    return math.sqrt(f(row["remanence_x"]) ** 2 + f(row["remanence_y"]) ** 2 + f(row["remanence_z"]) ** 2)


def execution_config() -> dict[str, object]:
    """Exige seulement les paramètres nécessaires pour interpréter les mesures."""
    execution = json.loads(EXEC.read_text(encoding="utf-8"))
    fields = execution.get("frozen_fields", {})
    required = (
        "af_plateau_mT",
        "test_field_mT",
        "temperature_target_c",
        "temperature_tolerance_c",
    )
    missing = [name for name in required if fields.get(name) is None]
    if missing:
        raise SystemExit("MAG instrument parameters incomplete: " + ", ".join(missing))
    return execution


def prepare(
    units_path: Path = UNITS,
    measurements_path: Path = MEAS,
    out_path: Path = OUT,
) -> list[dict[str, object]]:
    execution = execution_config()
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    if not units_path.exists() or not measurements_path.exists():
        raise SystemExit("Raw MAG-PAIR-001 tables are absent.")

    units = list(csv.DictReader(units_path.open(encoding="utf-8-sig", newline="")))
    if len(units) < int(protocol["minimum_independent_units"]):
        raise ValueError("insufficient independent units")
    ids = [row["unit_id"] for row in units]
    if any(not unit_id for unit_id in ids) or len(ids) != len(set(ids)):
        raise ValueError("unit_id must be non-empty and unique")

    allowed_history = set(protocol["histories"])
    allowed_arm = {"ablation", "sham"}
    if any(row["history"] not in allowed_history or row["arm"] not in allowed_arm for row in units):
        raise ValueError("invalid history/arm")
    if any(not row.get("block_id") for row in units):
        raise ValueError("block_id is required for every independent unit")

    by_stratum: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in units:
        by_stratum[(row["block_id"], row["arm"])].add(row["history"])
    bad = [key for key, histories in by_stratum.items() if histories != allowed_history]
    if bad:
        raise ValueError(
            "each block×arm stratum must contain both histories: "
            + ", ".join(f"{block}/{arm}" for block, arm in bad[:10])
        )

    unit_by_id = {row["unit_id"]: row for row in units}
    measurements = list(csv.DictReader(measurements_path.open(encoding="utf-8-sig", newline="")))
    if any(row["unit_id"] not in unit_by_id for row in measurements):
        raise ValueError("measurement for unknown unit")

    by_unit: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(lambda: defaultdict(list))
    for row in measurements:
        by_unit[row["unit_id"]][row["stage"]].append(row)

    required_stages = {
        "trace_initial": 1,
        "trace_day7": 10,
        "trace_post_ablation": 1,
        "response_pre": 1,
        "response_post": 1,
    }
    output: list[dict[str, object]] = []
    fields = execution["frozen_fields"]
    target_temperature = float(fields["temperature_target_c"])
    tolerance = float(fields["temperature_tolerance_c"])
    af_plateau = float(fields["af_plateau_mT"])
    test_field = float(fields["test_field_mT"])

    for unit_id in ids:
        stages = by_unit[unit_id]
        for stage, count in required_stages.items():
            if len(stages.get(stage, [])) != count:
                raise ValueError(f"{unit_id}: {stage} requires {count} rows")

        day7 = sorted(stages["trace_day7"], key=lambda row: int(row["reading_index"]))
        if [int(row["reading_index"]) for row in day7] != list(range(1, 11)):
            raise ValueError(f"{unit_id}: trace_day7 reading_index must be 1..10")

        all_measurements = [row for stage_rows in stages.values() for row in stage_rows]
        if any(
            abs(f(row["temperature_c"]) - target_temperature) > tolerance
            for row in all_measurements
        ):
            raise ValueError(f"{unit_id}: temperature out of tolerance")

        for row in stages["response_pre"] + stages["response_post"]:
            if abs(f(row["test_field_mT"]) - test_field) > 1e-12:
                raise ValueError(f"{unit_id}: test field mismatch")

        post = stages["trace_post_ablation"][0]
        if unit_by_id[unit_id]["arm"] == "ablation":
            if abs(f(post["af_field_mT"]) - af_plateau) > 1e-12:
                raise ValueError(f"{unit_id}: AF plateau mismatch")
        elif abs(f(post["af_field_mT"])) > 1e-12:
            raise ValueError(f"{unit_id}: sham AF must be zero")

        initial = magnitude(stages["trace_initial"][0])
        post_magnitude = magnitude(post)
        persistent = sum(magnitude(row) for row in day7) / 10.0
        output.append(
            {
                "unit_id": unit_id,
                "block_id": unit_by_id[unit_id]["block_id"],
                "history": unit_by_id[unit_id]["history"],
                "arm": unit_by_id[unit_id]["arm"],
                "trace_initial_magnitude": initial,
                "trace_day7_mean_magnitude": persistent,
                "trace_post_ablation_magnitude": post_magnitude,
                "trace_reduction_fraction": (1.0 - post_magnitude / initial) if initial else "",
                "response_pre": f(stages["response_pre"][0]["response_projection"]),
                "response_post": f(stages["response_post"][0]["response_projection"]),
            }
        )

    fieldnames = list(output[0])
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output)
    print(f"MAG-PAIR-001 prepared: {len(output)} independent units -> {out_path}")
    return output


if __name__ == "__main__":
    prepare()
