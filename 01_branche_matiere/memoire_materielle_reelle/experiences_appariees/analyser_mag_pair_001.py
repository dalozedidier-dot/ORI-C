#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "MAG-PAIR-001.json"
EXEC = HERE / "MAG-PAIR-001.execution.json"
INPUT = HERE / "mag_pair_001_analysis_ready.csv"
OUT = HERE / "MAG-PAIR-001.result.json"
POS = "IRM_positive_saturee"
NEG = "IRM_negative_saturee"
ARMS = ("ablation", "sham")


def execution_metadata() -> dict[str, object]:
    execution = json.loads(EXEC.read_text(encoding="utf-8"))
    fields = execution.get("frozen_fields", {})
    required_analysis = ("permutation_seed", "permutation_draws")
    missing = [name for name in required_analysis if fields.get(name) is None]
    if missing:
        raise SystemExit("Analysis configuration incomplete: " + ", ".join(missing))
    registration = execution.get("registration", {})
    return {
        "execution": execution,
        "registration_complete": bool(registration.get("public_url") and registration.get("registered_at")),
    }


def _finite(value: str, field: str) -> float:
    number = float(value)
    if not np.isfinite(number):
        raise ValueError(f"non-finite {field}")
    return number


def validate_analysis_rows(rows: list[dict[str, str]], minimum_units: int) -> None:
    required = {
        "unit_id",
        "block_id",
        "history",
        "arm",
        "trace_reduction_fraction",
        "response_pre",
        "response_post",
    }
    if not rows:
        raise ValueError("empty MAG-PAIR-001 analysis-ready table")
    missing = required - set(rows[0])
    if missing:
        raise ValueError("missing analysis-ready columns: " + ", ".join(sorted(missing)))
    if len(rows) < minimum_units:
        raise ValueError("insufficient independent units")

    ids = [row["unit_id"] for row in rows]
    if any(not value for value in ids) or len(ids) != len(set(ids)):
        raise ValueError("unit_id must be non-empty and unique")
    if any(row["history"] not in {POS, NEG} for row in rows):
        raise ValueError("invalid magnetic history")
    if any(row["arm"] not in set(ARMS) for row in rows):
        raise ValueError("invalid MAG arm")

    by_stratum: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in rows:
        by_stratum[(row["block_id"], row["arm"])].add(row["history"])
        _finite(row["response_pre"], "response_pre")
        _finite(row["response_post"], "response_post")
    bad = [key for key, histories in by_stratum.items() if histories != {POS, NEG}]
    if bad:
        raise ValueError(
            "each block×arm stratum must contain both magnetic histories; invalid strata: "
            + ", ".join(f"{block}/{arm}" for block, arm in bad[:10])
        )


def gap(rows: list[dict[str, str]], arm: str, field: str) -> float:
    positive = [_finite(row[field], field) for row in rows if row["arm"] == arm and row["history"] == POS]
    negative = [_finite(row[field], field) for row in rows if row["arm"] == arm and row["history"] == NEG]
    if not positive or not negative:
        raise ValueError(f"missing cells for {arm}/{field}")
    return float(np.mean(positive) - np.mean(negative))


def interaction_stat(rows: list[dict[str, str]]) -> float:
    """Différence des changements pré→post entre histoires et entre bras."""
    def change(arm: str, history: str) -> float:
        values = [
            _finite(row["response_post"], "response_post") - _finite(row["response_pre"], "response_pre")
            for row in rows
            if row["arm"] == arm and row["history"] == history
        ]
        if not values:
            raise ValueError("empty interaction cell")
        return float(np.mean(values))

    return (change("ablation", POS) - change("ablation", NEG)) - (
        change("sham", POS) - change("sham", NEG)
    )


def permutation_p(rows: list[dict[str, str]], draws: int, seed: int) -> float:
    """Permute l'histoire dans chaque bloc à bras constant.

    La randomisation conserve ainsi le bras ablation/sham et la structure de bloc,
    au lieu de produire des cellules histoire×bras vides qui seraient ensuite jetées.
    """
    if draws < 100:
        raise ValueError("permutation_draws must be >= 100")
    observed = abs(interaction_stat(rows))
    rng = np.random.default_rng(seed)
    strata: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        strata[(row["block_id"], row["arm"])].append(index)

    ge = 0
    for _ in range(draws):
        permuted = [dict(row) for row in rows]
        for indices in strata.values():
            labels = [permuted[index]["history"] for index in indices]
            rng.shuffle(labels)
            for index, label in zip(indices, labels):
                permuted[index]["history"] = label
        statistic = abs(interaction_stat(permuted))
        ge += statistic >= observed - 1e-15
    return float((ge + 1) / (draws + 1))


def analyze(path: Path = INPUT) -> dict[str, object]:
    meta = execution_metadata()
    execution = meta["execution"]
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    if not path.exists():
        raise SystemExit("Analysis-ready MAG-PAIR-001 table absent.")

    rows = list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))
    validate_analysis_rows(rows, int(protocol["minimum_independent_units"]))

    d0 = gap(rows, "ablation", "response_pre")
    d1 = gap(rows, "ablation", "response_post")
    normalized_ablation = 1.0 - abs(d1) / abs(d0) if d0 else float("-inf")

    s0 = gap(rows, "sham", "response_pre")
    s1 = gap(rows, "sham", "response_post")
    normalized_sham = 1.0 - abs(s1) / abs(s0) if s0 else None
    sham_does_not_reproduce_drop = bool(normalized_sham is not None and normalized_sham < 0.50)

    fields = execution["frozen_fields"]
    p_value = permutation_p(rows, int(fields["permutation_draws"]), int(fields["permutation_seed"]))
    trace_reduction = [
        _finite(row["trace_reduction_fraction"], "trace_reduction_fraction")
        for row in rows
        if row["arm"] == "ablation" and row["trace_reduction_fraction"] != ""
    ]
    trace_target = bool(trace_reduction and float(np.mean(trace_reduction)) >= 0.80)

    components = {
        "pre_ablation_history_gap_nonzero": bool(d0 != 0.0),
        "normalized_ablation_at_least_0p50": bool(normalized_ablation >= 0.50),
        "interaction_permutation_p_at_most_0p05": bool(p_value <= 0.05),
        "trace_reduction_target_ge_0p80": trace_target,
        "sham_does_not_reproduce_ge_0p50_drop": sham_does_not_reproduce_drop,
    }
    success = bool(all(components.values()))

    registration = execution.get("registration", {})
    result = {
        "schema": "oric.mag-pair-001.result.v2",
        "protocol_id": "MAG-PAIR-001",
        "n_independent_units": len(rows),
        "delta_R_before": d0,
        "delta_R_after": d1,
        "A_normalized": normalized_ablation,
        "sham_delta_R_before": s0,
        "sham_delta_R_after": s1,
        "sham_A_normalized": normalized_sham,
        "interaction_statistic": interaction_stat(rows),
        "interaction_permutation_scheme": "history permuted within block×arm strata",
        "interaction_permutation_p_two_sided": p_value,
        "mean_trace_reduction_fraction_true_ablation": float(np.mean(trace_reduction)) if trace_reduction else None,
        "decision_components": components,
        "prediction_success": success,
        "external_registration": {
            "url": registration.get("public_url"),
            "registered_at": registration.get("registered_at"),
            "complete": meta["registration_complete"],
            "blocks_analysis": False,
        },
        "scope": "result computed from supplied real measurements; external registration metadata are reported separately",
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    analyze()
