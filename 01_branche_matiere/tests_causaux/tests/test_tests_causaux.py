from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    specification = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(specification)
    assert specification.loader is not None
    specification.loader.exec_module(module)
    return module


def test_h011_threshold_moves_with_turbulence():
    result = load("analyser_h011").main()
    assert result["zcrit_monotonic_with_turbulence"]
    assert result["threshold_ratio_high_low_turbulence"] >= 2
    assert result["natural_intervention_status"] == "not_measured"


def test_cycle_is_not_declared_closed_without_one_full_trajectory():
    result = load("analyser_cycle_interfaces").main()
    assert set(result["documented_required_edges"]) == {"H030", "H031", "H052", "H053"}
    assert result["single_system_closed_trajectories"] == 0
    assert result["cycle_status"] == "anchored_but_not_closed"
