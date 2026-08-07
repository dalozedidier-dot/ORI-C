from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from oric_full.domains.matter import analyze_condensation
from oric_full.domains.planetary import late_accretion_mixture, volatile_closure
from oric_full.models import ExecutionMode, Outcome, TestSpec
from oric_full.runner import RunOptions, run_campaign
from oric_full.synthetic_data import generate_all


def spec(test_id: str, engine: str, dataset: str) -> TestSpec:
    return TestSpec(
        test_id=test_id,
        wp="TEST",
        section="empirical",
        ordinal=1,
        description="portée empirique",
        mode=ExecutionMode.DATA_REQUIRED,
        engine=engine,
        required_datasets=(dataset,),
        confirmatory=False,
        priority=1,
        source_line=1,
    )


def write_coverage(data_dir: Path, dataset: str, *, eligible: bool, allowed: list[str]) -> None:
    payload = {
        "schema_version": 2,
        "datasets": {
            dataset: {
                "data_kind": "empirical_observation",
                "eligible_for_empirical_proof": eligible,
                "scope_mode": "allow_list",
                "supported_test_ids": allowed,
                "limitations": "fixture",
            }
        },
    }
    (data_dir / "REAL_DATA_COVERAGE.json").write_text(json.dumps(payload), encoding="utf-8")


def test_real_mode_is_fail_closed_when_dataset_is_not_registered(tmp_path: Path):
    data_dir = tmp_path / "data"
    generate_all(data_dir, seed=1)
    campaign = run_campaign(
        [spec("M4-001", "condensation", "thermochemical_phases")],
        RunOptions(data_dir=data_dir, real_data_only=True),
    )
    assert campaign.results[0].outcome == Outcome.BLOCKED
    assert campaign.results[0].details["coverage_gaps"][0]["reason"] == "absent_du_registre_empirique"


def test_real_mode_requires_explicit_empirical_eligibility(tmp_path: Path):
    data_dir = tmp_path / "data"
    generate_all(data_dir, seed=2)
    write_coverage(data_dir, "thermochemical_phases", eligible=False, allowed=["M4-001"])
    campaign = run_campaign(
        [spec("M4-001", "condensation", "thermochemical_phases")],
        RunOptions(data_dir=data_dir, real_data_only=True),
    )
    assert campaign.results[0].outcome == Outcome.BLOCKED
    assert campaign.results[0].details["coverage_gaps"][0]["reason"] == "non_admissible_comme_preuve_empirique"


def test_allow_list_never_unlocks_sibling_test(tmp_path: Path):
    data_dir = tmp_path / "data"
    generate_all(data_dir, seed=3)
    write_coverage(data_dir, "antibiotic_design", eligible=True, allowed=["R1-005"])
    campaign = run_campaign(
        [
            spec("R1-005", "antibiotic_design", "antibiotic_design"),
            spec("R1-006", "antibiotic_design", "antibiotic_design"),
        ],
        RunOptions(data_dir=data_dir, real_data_only=True),
    )
    outcomes = {r.test_id: r.outcome for r in campaign.results}
    assert outcomes["R1-005"] == Outcome.PASS
    assert outcomes["R1-006"] == Outcome.BLOCKED


def test_volatile_missing_compartment_is_not_zero():
    frame = pd.DataFrame(
        [
            {
                "sample_id": "x",
                "volatile": "C",
                "initial_mass": 100.0,
                "core_mass": 30.0,
                "mantle_mass": 20.0,
                "atmosphere_mass": np.nan,
                "lost_mass": np.nan,
            }
        ]
    )
    result = volatile_closure(frame)
    assert result.metrics["complete_budget_rows"] == 0.0
    assert result.metrics["incomplete_budget_rows"] == 1.0
    assert np.isnan(result.metrics["median_exact_mass_balance_error"])
    assert result.details["row_audit"][0]["known_retained_fraction_lower_bound"] == 0.5


def test_late_accretion_is_a_compilation_audit_not_a_mixing_model():
    rows = []
    for tracer in ["Mo", "Ru", "W", "Os", "Ir", "Au"]:
        rows.append(
            {
                "sample_id": "sample-1",
                "tracer": tracer,
                "final_value": 1.0,
                "uncertainty": np.nan,
                "candidate_source": "rock | setting",
                "unit": "ppm",
                "compilation": "fixture",
                "reference": "ref",
            }
        )
    result = late_accretion_mixture(pd.DataFrame(rows))
    assert result.metrics["required_tracer_coverage_fraction"] == 1.0
    assert result.metrics["unit_inconsistency_count"] == 0.0
    assert "pôle de mélange" in result.details["interpretation_limit"]
    assert "source_means" not in result.details


def test_thermochemical_grid_does_not_claim_equilibrium():
    frame = pd.DataFrame(
        [
            {"phase": "A", "temperature": 300.0, "pressure": 1.0, "gibbs_energy": -10.0, "composition": "X"},
            {"phase": "A", "temperature": 300.0, "pressure": 10.0, "gibbs_energy": -9.0, "composition": "X"},
            {"phase": "B", "temperature": 300.0, "pressure": 1.0, "gibbs_energy": -20.0, "composition": "Y"},
        ]
    )
    result = analyze_condensation(frame)
    assert result.metrics["phase_count"] == 2.0
    assert "stable_phase_count" not in result.metrics
    assert "Aucun équilibre de condensation" in result.details["interpretation_limit"]
