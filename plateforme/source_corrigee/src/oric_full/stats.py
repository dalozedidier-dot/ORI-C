from __future__ import annotations

import math
from dataclasses import dataclass
import numpy as np


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    a = np.asarray(y_true, dtype=float)
    b = np.asarray(y_pred, dtype=float)
    return float(np.sqrt(np.mean((a - b) ** 2)))


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    a = np.asarray(y_true, dtype=float)
    b = np.asarray(y_pred, dtype=float)
    return float(np.mean(np.abs(a - b)))


def r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    a = np.asarray(y_true, dtype=float)
    b = np.asarray(y_pred, dtype=float)
    denom = float(np.sum((a - np.mean(a)) ** 2))
    if denom == 0:
        return 0.0
    return 1.0 - float(np.sum((a - b) ** 2)) / denom


def aic(n: int, rss: float, k: int) -> float:
    rss = max(float(rss), np.finfo(float).tiny)
    return n * math.log(rss / n) + 2 * k


def bic(n: int, rss: float, k: int) -> float:
    rss = max(float(rss), np.finfo(float).tiny)
    return n * math.log(rss / n) + k * math.log(n)


def block_splits(n: int, n_splits: int = 5) -> list[tuple[np.ndarray, np.ndarray]]:
    if n_splits < 2 or n < n_splits:
        raise ValueError("n_splits incompatible")
    indices = np.arange(n)
    blocks = np.array_split(indices, n_splits)
    result = []
    for test in blocks:
        train = np.setdiff1d(indices, test, assume_unique=True)
        result.append((train, test))
    return result


def bootstrap_ci(values: np.ndarray, statistic=np.mean, n_boot: int = 2000, alpha: float = 0.05, seed: int = 0) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    samples = np.empty(n_boot)
    for i in range(n_boot):
        samples[i] = statistic(rng.choice(values, size=len(values), replace=True))
    return float(np.quantile(samples, alpha / 2)), float(np.quantile(samples, 1 - alpha / 2))


@dataclass(frozen=True)
class Comparison:
    baseline_rmse: float
    candidate_rmse: float
    relative_gain: float
    wins: bool


def compare_predictions(y_true: np.ndarray, baseline: np.ndarray, candidate: np.ndarray, min_gain: float = 0.02) -> Comparison:
    b = rmse(y_true, baseline)
    c = rmse(y_true, candidate)
    gain = (b - c) / b if b > 0 else 0.0
    return Comparison(b, c, gain, gain >= min_gain)
