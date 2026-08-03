from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
import numpy as np


@dataclass(frozen=True)
class ViabilityEstimate:
    pth_fraction: float
    pacc_fraction: float
    accessible_count: int
    theoretical_count: int
    ci_low: float
    ci_high: float


def estimate_viability(
    sampler: Callable[[np.random.Generator, int], np.ndarray],
    theoretical_predicate: Callable[[np.ndarray], np.ndarray],
    accessible_predicate: Callable[[np.ndarray, float, dict], np.ndarray],
    *,
    horizon: float,
    constraints: dict,
    epsilon: float = 0.05,
    n_samples: int = 10000,
    seed: int = 0,
) -> ViabilityEstimate:
    rng = np.random.default_rng(seed)
    states = sampler(rng, n_samples)
    theoretical = np.asarray(theoretical_predicate(states), dtype=bool)
    accessible = np.asarray(accessible_predicate(states, horizon, constraints), dtype=bool) & theoretical
    nt = int(theoretical.sum())
    na = int(accessible.sum())
    pth = nt / n_samples
    pacc = na / n_samples
    # Wilson interval for accessible fraction
    z = 1.959963984540054
    n = n_samples
    denom = 1 + z**2 / n
    center = (pacc + z**2 / (2 * n)) / denom
    half = z * np.sqrt((pacc * (1 - pacc) + z**2 / (4 * n)) / n) / denom
    return ViabilityEstimate(pth, pacc, na, nt, float(center - half), float(center + half))


def box_sampler(bounds: np.ndarray) -> Callable[[np.random.Generator, int], np.ndarray]:
    bounds = np.asarray(bounds, dtype=float)
    if bounds.ndim != 2 or bounds.shape[1] != 2:
        raise ValueError("bounds doit être de forme (dimension, 2)")

    def sample(rng: np.random.Generator, n: int) -> np.ndarray:
        return rng.uniform(bounds[:, 0], bounds[:, 1], size=(n, len(bounds)))

    return sample
