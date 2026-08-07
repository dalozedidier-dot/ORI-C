from __future__ import annotations

import json
from pathlib import Path

from oric_full.models import ExecutionMode, Outcome, TestSpec as Spec
from oric_full.runner import RunOptions, run_campaign
from oric_full.synthetic_data import generate_all


def _spec(test_id: str, engine: str, dataset: str, mode: ExecutionMode = ExecutionMode.DATA_REQUIRED) -> Spec:
    return Spec(
        test_id=test_id,
        wp="TEST",
        section="scope",
        ordinal=1,
        description="test de portée",
        mode=mode,
        engine=engine,
        required_datasets=(dataset,),
        confirmatory=False,
        priority=1,
        source_line=1,
    )


def test_partial_real_table_only_unlocks_allow_list(tmp_path: Path):
    data_dir = tmp_path / "data"
    generate_all(data_dir, seed=3)
    coverage = {
        "schema_version": 2,
        "datasets": {
            "prebiotic_design": {
                "data_kind": "empirical_derived",
                "eligible_for_empirical_proof": True,
                "scope_mode": "allow_list",
                "supported_test_ids": ["V1-001"],
                "limitations": "portée volontairement partielle",
            }
        },
    }
    (data_dir / "REAL_DATA_COVERAGE.json").write_text(json.dumps(coverage), encoding="utf-8")
    campaign = run_campaign(
        [
            _spec("V1-001", "prebiotic_design", "prebiotic_design"),
            _spec("V1-002", "prebiotic_design", "prebiotic_design"),
        ],
        RunOptions(data_dir=data_dir, real_data_only=True),
    )
    outcomes = {result.test_id: result.outcome for result in campaign.results}
    assert outcomes["V1-001"] == Outcome.PASS
    assert outcomes["V1-002"] == Outcome.BLOCKED
    blocked = next(result for result in campaign.results if result.test_id == "V1-002")
    assert blocked.details["scientific_scope"] == "blocage empirique fail-closed"


def test_noncomputational_protocol_is_not_marked_as_generator_failure(tmp_path: Path):
    data_dir = tmp_path / "data"
    generate_all(data_dir, seed=4)
    spec = _spec("V1-010", "prebiotic_design", "prebiotic_design", ExecutionMode.HUMAN_REVIEW)
    campaign = run_campaign([spec], RunOptions(data_dir=data_dir, real_data_only=True))
    assert campaign.results[0].outcome == Outcome.NOT_RUN
