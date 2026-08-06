from __future__ import annotations

import copy
from pathlib import Path

import numpy as np
import pytest

from methodologie_puissance.power_monte_carlo import (
    Adapter,
    PlanError,
    effect_context,
    estimate_power,
    read_plan,
    validate_plan,
    wilson_interval,
)

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "methodologie_puissance" / "exemple_power_plan.json"


def test_example_plan_is_valid() -> None:
    plan = read_plan(EXAMPLE)
    assert plan["independent_unit"] == "groupe_experimental"


def test_folds_are_rejected_as_independent_units() -> None:
    plan = read_plan(EXAMPLE)
    invalid = copy.deepcopy(plan)
    invalid["independent_unit"] = "CV folds"
    with pytest.raises(PlanError, match="fold"):
        validate_plan(invalid)


def test_relative_effect_is_converted_to_absolute_difference() -> None:
    plan = read_plan(EXAMPLE)
    effect = effect_context(plan)
    assert effect["absolute"] == pytest.approx(0.04)


def test_wilson_interval_contains_observed_rate() -> None:
    lower, upper = wilson_interval(80, 100)
    assert lower < 0.8 < upper
    assert lower == pytest.approx(0.7112, abs=1e-3)
    assert upper == pytest.approx(0.8666, abs=1e-3)


class _DeterministicModule:
    @staticmethod
    def simulate_and_evaluate(*, rng: np.random.Generator, plan, n: int, effect):
        draw = float(rng.random())
        return {
            "history_beats_state": draw < 0.75,
            "history_beats_shuffled_history": draw < 0.55,
        }


def test_joint_power_requires_all_success_criteria() -> None:
    plan = read_plan(EXAMPLE)
    adapter = Adapter(path=Path("fake.py"), module=_DeterministicModule(), sha256="0" * 64)
    first = estimate_power(plan, adapter, n=20, simulations=400, seed=123)
    second = estimate_power(plan, adapter, n=20, simulations=400, seed=123)
    assert first == second
    assert first["power"] == first["criterion_rates"]["history_beats_shuffled_history"]
    assert first["criterion_rates"]["history_beats_state"] > first["power"]
