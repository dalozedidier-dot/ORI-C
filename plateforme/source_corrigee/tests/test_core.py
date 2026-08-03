import warnings

import numpy as np

from oric_full.core.memory import convolve_memory, gamma_kernel
from oric_full.core.synthetic import run_core_synthetic
from oric_full.core.intervention import ChemostatConfig, intervention_effect


def test_gamma_kernel_is_finite_without_runtime_warning():
    lags = np.arange(100, dtype=float)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("error", RuntimeWarning)
        weights = gamma_kernel(lags, np.array([0.5, 10.0]))
    assert not caught
    assert np.all(np.isfinite(weights))
    assert np.isclose(np.trapezoid(weights, lags), 1.0)


def test_core_synthetic_and_intervention():
    result = run_core_synthetic(seed=4)
    assert result["passed"]
    effect = intervention_effect(ChemostatConfig(), intervention_loss=0.05)
    assert all(np.isfinite(value) for value in effect.values())
