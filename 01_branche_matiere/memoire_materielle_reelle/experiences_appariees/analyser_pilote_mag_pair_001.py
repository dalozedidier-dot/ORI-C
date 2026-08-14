#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Mapping

import numpy as np

HERE = Path(__file__).resolve().parent
POS = "IRM_positive_saturee"
NEG = "IRM_negative_saturee"


def rows(path: Path | str) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def num(value: str) -> float:
    number = float(value)
    if not np.isfinite(number):
        raise ValueError("non-finite pilot value")
    return number


def analyse(af_path: Path | str, field_path: Path | str, output: Path | str | None = None) -> dict[str, object]:
    """Analyse uniquement les mesures réelles du pilote sacrificial."""
    af = rows(af_path)
    test_fields = rows(field_path)
    if not af or not test_fields:
        raise ValueError("pilot AF and test-field tables must both contain real measurements")

    levels = sorted({num(row["af_mT"]) for row in af})
    per_level = []
    chosen_af = None
    for level in levels:
        history_values: dict[str, float | None] = {}
        for history in (POS, NEG):
            reductions = []
            for row in af:
                if row["history"] == history and num(row["af_mT"]) == level:
                    before = abs(num(row["trace_before"]))
                    after = abs(num(row["trace_after"]))
                    if before > 0:
                        reductions.append(1.0 - after / before)
            history_values[history] = float(np.median(reductions)) if reductions else None
        passes = all(
            history_values[history] is not None and history_values[history] >= 0.80
            for history in (POS, NEG)
        )
        per_level.append(
            {
                "af_mT": level,
                "median_trace_reduction_by_history": history_values,
                "passes_inherited_80_percent_rule": passes,
            }
        )
        if passes and chosen_af is None:
            chosen_af = level

    field_rows = []
    for level in sorted({num(row["test_field_mT"]) for row in test_fields}):
        subset = [row for row in test_fields if num(row["test_field_mT"]) == level]
        overwrite = []
        signal_to_noise = []
        for row in subset:
            before = abs(num(row["trace_before_test"]))
            after = abs(num(row["trace_after_test"]))
            if before > 0:
                overwrite.append(abs(after - before) / before)
            noise = abs(num(row["instrument_noise_sd"]))
            if noise > 0:
                signal_to_noise.append(abs(num(row["response_projection"])) / noise)
        field_rows.append(
            {
                "test_field_mT": level,
                "median_trace_overwrite_fraction": float(np.median(overwrite)) if overwrite else None,
                "median_signal_to_noise": float(np.median(signal_to_noise)) if signal_to_noise else None,
                "n": len(subset),
            }
        )

    temperatures = [num(row["temperature_C"]) for row in [*af, *test_fields]]
    report = {
        "schema": "oric.mag-pair-001.pilot-report.v2",
        "confirmatory_credit": False,
        "recommended_af_plateau_mT_from_inherited_rule": chosen_af,
        "af_levels": per_level,
        "test_field_candidates_measured": field_rows,
        "observed_temperature_C": {
            "min": min(temperatures),
            "max": max(temperatures),
            "median": float(np.median(temperatures)),
        },
        "scope": "real sacrificial pilot only; parameters may be tuned here before confirmatory acquisition",
    }
    if output:
        Path(output).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


def propose_execution_parameters(report: Mapping[str, object], policy: Mapping[str, object]) -> dict[str, object]:
    """Sélectionne des paramètres à partir du pilote avant la campagne confirmatoire.

    Le pilote est justement la phase autorisée pour choisir ces paramètres. Les
    seuils instrumentaux sont fournis explicitement dans ``policy`` et enregistrés
    dans la proposition; aucun résultat confirmatoire n'est consulté.
    """
    required = (
        "max_median_trace_overwrite_fraction",
        "min_median_signal_to_noise",
        "temperature_target_C",
        "temperature_tolerance_C",
    )
    missing = [name for name in required if policy.get(name) is None]
    if missing:
        raise ValueError("missing pilot policy fields: " + ", ".join(missing))

    max_overwrite = float(policy["max_median_trace_overwrite_fraction"])
    min_snr = float(policy["min_median_signal_to_noise"])
    target = float(policy["temperature_target_C"])
    tolerance = float(policy["temperature_tolerance_C"])
    if not 0.0 <= max_overwrite < 1.0:
        raise ValueError("max_median_trace_overwrite_fraction must be in [0,1)")
    if min_snr <= 0.0 or tolerance <= 0.0:
        raise ValueError("min SNR and temperature tolerance must be > 0")

    eligible = []
    for candidate in report["test_field_candidates_measured"]:
        overwrite = candidate["median_trace_overwrite_fraction"]
        snr = candidate["median_signal_to_noise"]
        if overwrite is None or snr is None:
            continue
        if float(overwrite) <= max_overwrite and float(snr) >= min_snr:
            eligible.append(float(candidate["test_field_mT"]))
    selected_field = min(eligible) if eligible else None

    observed = report["observed_temperature_C"]
    temperature_passes = bool(
        float(observed["min"]) >= target - tolerance
        and float(observed["max"]) <= target + tolerance
    )
    af_level = report.get("recommended_af_plateau_mT_from_inherited_rule")
    ready = bool(af_level is not None and selected_field is not None and temperature_passes)

    return {
        "schema": "oric.mag-pair-001.execution-parameter-proposal.v2",
        "confirmatory_credit": False,
        "af_plateau_mT": af_level,
        "test_field_mT": selected_field,
        "eligible_test_fields_mT": sorted(eligible),
        "temperature_target_c": target,
        "temperature_tolerance_c": tolerance,
        "temperature_window_passes": temperature_passes,
        "pilot_policy": {
            "max_median_trace_overwrite_fraction": max_overwrite,
            "min_median_signal_to_noise": min_snr,
        },
        "ready_for_execution_freeze": ready,
        "status": "pilot_parameters_ready_for_execution_freeze" if ready else "pilot_parameters_not_ready",
        "selection_rule": "lowest measured test field satisfying pilot overwrite/SNR policy; AF uses inherited >=80% trace-reduction rule",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("af_sweep", type=Path)
    parser.add_argument("test_field_sweep", type=Path)
    parser.add_argument("--output", type=Path, default=HERE / "MAG-PAIR-001.pilot-report.json")
    parser.add_argument("--policy", type=Path)
    parser.add_argument("--proposal-output", type=Path, default=HERE / "MAG-PAIR-001.execution-proposal.json")
    args = parser.parse_args()

    report = analyse(args.af_sweep, args.test_field_sweep, args.output)
    if args.policy:
        policy = json.loads(args.policy.read_text(encoding="utf-8"))
        proposal = propose_execution_parameters(report, policy)
        args.proposal_output.write_text(
            json.dumps(proposal, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        report["execution_parameter_proposal"] = proposal
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
