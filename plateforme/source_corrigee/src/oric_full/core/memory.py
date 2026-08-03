from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
import numpy as np
from scipy.optimize import least_squares
from scipy.signal import fftconvolve

from ..stats import rmse, aic, bic


Kernel = Callable[[np.ndarray, np.ndarray], np.ndarray]


def exponential_kernel(lags: np.ndarray, params: np.ndarray) -> np.ndarray:
    tau = max(float(params[0]), 1e-12)
    return np.exp(-lags / tau) / tau


def gamma_kernel(lags: np.ndarray, params: np.ndarray) -> np.ndarray:
    shape = max(float(params[0]), 1e-3)
    scale = max(float(params[1]), 1e-12)
    lags = np.asarray(lags, dtype=float)
    # Évite 0**(shape-1) lorsque shape < 1 sans masquer un avertissement numérique.
    safe_lags = np.maximum(lags, np.finfo(float).tiny)
    raw = np.zeros_like(safe_lags)
    valid = lags >= 0
    raw[valid] = safe_lags[valid] ** (shape - 1) * np.exp(-safe_lags[valid] / scale)
    norm = np.trapezoid(raw, lags)
    return raw / norm if np.isfinite(norm) and norm > 0 else np.zeros_like(raw)


def powerlaw_kernel(lags: np.ndarray, params: np.ndarray) -> np.ndarray:
    alpha = max(float(params[0]), 1e-3)
    offset = max(float(params[1]), 1e-12)
    raw = (lags + offset) ** (-alpha)
    norm = np.trapezoid(raw, lags)
    return raw / norm if norm > 0 else raw


def stretched_exponential_kernel(lags: np.ndarray, params: np.ndarray) -> np.ndarray:
    tau = max(float(params[0]), 1e-12)
    beta = float(np.clip(params[1], 0.05, 2.0))
    raw = np.exp(-((lags / tau) ** beta))
    norm = np.trapezoid(raw, lags)
    return raw / norm if norm > 0 else raw


KERNELS: dict[str, tuple[Kernel, np.ndarray, tuple[np.ndarray, np.ndarray]]] = {
    "exponential": (exponential_kernel, np.array([10.0]), (np.array([1e-3]), np.array([1e6]))),
    "gamma": (gamma_kernel, np.array([2.0, 10.0]), (np.array([0.1, 1e-3]), np.array([20.0, 1e6]))),
    "powerlaw": (powerlaw_kernel, np.array([1.0, 1.0]), (np.array([0.01, 1e-6]), np.array([5.0, 1e6]))),
    "stretched": (stretched_exponential_kernel, np.array([10.0, 0.7]), (np.array([1e-3, 0.05]), np.array([1e6, 2.0]))),
}


def convolve_memory(forcing: np.ndarray, dt: float, kernel_name: str, params: np.ndarray, max_lag: int | None = None) -> np.ndarray:
    forcing = np.asarray(forcing, dtype=float)
    if kernel_name not in KERNELS:
        raise KeyError(kernel_name)
    kernel_fn = KERNELS[kernel_name][0]
    n = len(forcing) if max_lag is None else min(len(forcing), max_lag)
    lags = np.arange(n, dtype=float) * dt
    weights = kernel_fn(lags, np.asarray(params, dtype=float)) * dt
    output = fftconvolve(forcing, weights, mode="full")[: len(forcing)]
    return np.asarray(output, dtype=float)


@dataclass(frozen=True)
class MemoryFit:
    kernel: str
    params: tuple[float, ...]
    coefficients: tuple[float, ...]
    prediction: np.ndarray
    rmse: float
    aic: float
    bic: float
    success: bool


def fit_memory_model(time: np.ndarray, forcing: np.ndarray, target: np.ndarray, kernel_name: str) -> MemoryFit:
    time = np.asarray(time, dtype=float)
    forcing = np.asarray(forcing, dtype=float)
    target = np.asarray(target, dtype=float)
    if len(time) < 5 or len(time) != len(forcing) or len(time) != len(target):
        raise ValueError("Séries incompatibles")
    dt = float(np.median(np.diff(time)))
    kernel_fn, initial, bounds = KERNELS[kernel_name]

    def residual(theta: np.ndarray) -> np.ndarray:
        n_params = len(initial)
        memory = convolve_memory(forcing, dt, kernel_name, theta[:n_params])
        intercept, direct, memory_weight = theta[n_params:]
        pred = intercept + direct * forcing + memory_weight * memory
        return pred - target

    x0 = np.concatenate([initial, [float(np.mean(target)), 0.0, 1.0]])
    lower = np.concatenate([bounds[0], [-np.inf, -np.inf, -np.inf]])
    upper = np.concatenate([bounds[1], [np.inf, np.inf, np.inf]])
    result = least_squares(residual, x0, bounds=(lower, upper), max_nfev=3000)
    n_params = len(initial)
    memory = convolve_memory(forcing, dt, kernel_name, result.x[:n_params])
    pred = result.x[n_params] + result.x[n_params + 1] * forcing + result.x[n_params + 2] * memory
    rss = float(np.sum((pred - target) ** 2))
    k = len(result.x)
    return MemoryFit(
        kernel_name,
        tuple(map(float, result.x[:n_params])),
        tuple(map(float, result.x[n_params:])),
        pred,
        rmse(target, pred),
        aic(len(target), rss, k),
        bic(len(target), rss, k),
        bool(result.success),
    )
