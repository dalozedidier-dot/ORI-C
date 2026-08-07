from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from oric_full.data_registry import DataRegistry
from oric_full.domains.matter import analyze_condensation
from oric_full.domains.planetary import late_accretion_mixture, volatile_closure
from oric_full.engines import evaluate_engine
from oric_full.models import ExecutionMode, Outcome, TestSpec as Spec
from oric_full.runner import RunOptions, run_campaign


def _spec(test_id: str, engine: str, dataset: str) -> Spec:
    return Spec(
        test_id=test_id,
        wp="FIREWALL",
        section="science",
        ordinal=1,
        description="test barrière scientifique",
        mode=ExecutionMode.DATA_REQUIRED,
        engine=engine,
        required_datasets=(dataset,),
        confirmatory=False,
        priority=1,
        source_line=1,
    )


def test_real_data_mode_is_fail_closed_for_unregistered_dataset(tmp_path: Path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    pd.DataFrame(
        [{
            "sample_id": "X", "volatile": "H", "initial_mass": 1.0,
            "core_mass": 0.2, "mantle_mass": 0.3, "atmosphere_mass": 0.1,
            "lost_mass": 0.4,
        }]
    ).to_csv(data_dir / "volatile_inventory.csv", index=False)
    (data_dir / "REAL_DATA_COVERAGE.json").write_text(
        json.dumps({"schema_version": 1, "datasets": {}}), encoding="utf-8"
    )
    campaign = run_campaign(
        [_spec("P4-001", "volatile_budget", "volatile_inventory")],
        RunOptions(data_dir=data_dir, real_data_only=True),
    )
    result = campaign.results[0]
    assert result.outcome == Outcome.BLOCKED
    assert result.details["coverage_gaps"][0]["reason"] == "dataset_not_registered_for_real_data"


def test_quarantined_engine_stays_blocked_even_when_dataset_is_registered(tmp_path: Path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    pd.DataFrame(
        [{
            "sample_id": "X", "volatile": "H", "initial_mass": 1.0,
            "core_mass": 0.2, "mantle_mass": 0.3, "atmosphere_mass": 0.1,
            "lost_mass": 0.4,
        }]
    ).to_csv(data_dir / "volatile_inventory.csv", index=False)
    coverage = {
        "schema_version": 1,
        "datasets": {
            "volatile_inventory": {
                "scope_mode": "allow_list",
                "supported_test_ids": ["P4-001"],
                "limitations": "fixture",
            }
        },
    }
    (data_dir / "REAL_DATA_COVERAGE.json").write_text(json.dumps(coverage), encoding="utf-8")
    campaign = run_campaign(
        [_spec("P4-001", "volatile_budget", "volatile_inventory")],
        RunOptions(data_dir=data_dir, real_data_only=True),
    )
    result = campaign.results[0]
    assert result.outcome == Outcome.BLOCKED
    assert "quarantaine" in result.message.lower()
    assert result.details["scientific_scope"] == "aucun verdict empirique autorisé"


def test_volatile_missing_values_are_never_zero_imputed():
    frame = pd.DataFrame(
        [
            {
                "sample_id": "incomplete", "volatile": "H", "initial_mass": 10.0,
                "core_mass": 2.0, "mantle_mass": 3.0, "atmosphere_mass": np.nan,
                "lost_mass": 5.0,
            },
            {
                "sample_id": "complete", "volatile": "C", "initial_mass": 10.0,
                "core_mass": 2.0, "mantle_mass": 3.0, "atmosphere_mass": 1.0,
                "lost_mass": 4.0,
            },
        ]
    )
    result = volatile_closure(frame)
    assert result.details["complete_rows"] == 1
    assert result.details["incomplete_rows"] == 1
    assert result.metrics["median_mass_balance_error"] == 0.0
    assert result.details["rule"] == "complete_cases_only_no_zero_imputation"


def test_late_accretion_never_averages_raw_values_across_tracers():
    frame = pd.DataFrame(
        [
            {"sample_id": "a1", "tracer": "Mo", "final_value": 1.0, "uncertainty": 0.1, "candidate_source": "NC"},
            {"sample_id": "a2", "tracer": "Mo", "final_value": 1.2, "uncertainty": 0.1, "candidate_source": "NC"},
            {"sample_id": "b1", "tracer": "Mo", "final_value": 2.0, "uncertainty": 0.1, "candidate_source": "CC"},
            {"sample_id": "b2", "tracer": "Mo", "final_value": 2.2, "uncertainty": 0.1, "candidate_source": "CC"},
            # Echelle volontairement 10^6 fois plus grande pour Ru.
            {"sample_id": "c1", "tracer": "Ru", "final_value": 1_000_000.0, "uncertainty": 1000.0, "candidate_source": "NC"},
            {"sample_id": "c2", "tracer": "Ru", "final_value": 1_200_000.0, "uncertainty": 1000.0, "candidate_source": "NC"},
            {"sample_id": "d1", "tracer": "Ru", "final_value": 2_000_000.0, "uncertainty": 1000.0, "candidate_source": "CC"},
            {"sample_id": "d2", "tracer": "Ru", "final_value": 2_200_000.0, "uncertainty": 1000.0, "candidate_source": "CC"},
        ]
    )
    result = late_accretion_mixture(frame)
    assert result.details["analysis_valid"] is True
    assert result.metrics["tracers_compared"] == 2.0
    assert np.isfinite(result.metrics["median_standardized_source_spread"])
    assert result.details["rule"] == "never_average_raw_values_across_different_tracers"
    assert "source_means" not in result.details  # aucune moyenne globale inter-traceurs


def test_condensation_table_is_only_descriptive_not_equilibrium():
    frame = pd.DataFrame(
        [
            {"phase": "A", "temperature": 1000, "pressure": 1, "gibbs_energy": -10, "composition": "X"},
            {"phase": "B", "temperature": 1000, "pressure": 1, "gibbs_energy": -1000, "composition": "Y"},
        ]
    )
    result = analyze_condensation(frame)
    assert result.details["equilibrium_valid"] is False
    assert result.metrics["equilibrium_valid"] == 0.0
    assert "stable_phase_counts" not in result.details


def test_engines_that_used_invalid_proxies_do_not_pass(tmp_path: Path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    pd.DataFrame(
        [{"phase": "A", "temperature": 1000, "pressure": 1, "gibbs_energy": -10, "composition": "X"}]
    ).to_csv(data_dir / "thermochemical_phases.csv", index=False)
    pd.DataFrame(
        [{
            "body_id": "Earth", "initial_composition": "A", "provenance": "NC",
            "accretion_time": "late", "thermal_history": "hot", "redox_history": "variable",
            "losses": "yes", "late_inputs": "yes", "final_partition": "state1",
        }]
    ).to_csv(data_dir / "planetary_histories.csv", index=False)
    registry = DataRegistry(data_dir)
    assert evaluate_engine("condensation", registry).outcome == Outcome.BLOCKED
    assert evaluate_engine("planetary_value", registry).outcome == Outcome.BLOCKED


def test_climate_memory_accepts_iso_dates_without_float_cast_failure():
    from oric_full.domains.climate import _numeric_time_axis

    values = pd.Series(["1880-01-15", "1880-02-15", "1880-03-15"])
    axis = _numeric_time_axis(values)
    assert axis[0] == 0.0
    assert np.all(np.diff(axis) > 0)
    assert 0.07 < axis[-1] < 0.2
