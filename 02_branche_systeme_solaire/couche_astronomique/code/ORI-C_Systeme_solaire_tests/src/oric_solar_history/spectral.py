from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import signal


@dataclass(frozen=True)
class SpectrumResult:
    spectrum: pd.DataFrame
    peaks: pd.DataFrame
    ar1_phi: float


def estimate_ar1(x: np.ndarray) -> float:
    centered = np.asarray(x, dtype=float) - np.nanmean(x)
    if centered.size < 3 or np.allclose(centered, 0):
        return 0.0
    numerator = float(np.dot(centered[:-1], centered[1:]))
    denominator = float(np.dot(centered[:-1], centered[:-1]))
    if denominator == 0:
        return 0.0
    return float(np.clip(numerator / denominator, -0.98, 0.98))


def _ar1_series(phi: float, n: int, std: float, rng: np.random.Generator) -> np.ndarray:
    noise_std = std * np.sqrt(max(1.0 - phi * phi, 1e-12))
    y = np.zeros(n, dtype=float)
    y[0] = rng.normal(0.0, std)
    for i in range(1, n):
        y[i] = phi * y[i - 1] + rng.normal(0.0, noise_std)
    return y


def analyze_regular_series(
    times_years: np.ndarray,
    values: np.ndarray,
    min_period_years: float,
    max_period_years: float,
    peak_count: int = 8,
    red_noise_surrogates: int = 100,
    confidence: float = 0.95,
    seed: int = 0,
) -> SpectrumResult:
    times = np.asarray(times_years, dtype=float)
    x = np.asarray(values, dtype=float)
    if times.size != x.size or times.size < 8:
        raise ValueError("La série doit contenir au moins 8 points alignés")
    dt = np.diff(times)
    if not np.allclose(dt, np.median(dt), rtol=1e-5, atol=1e-9):
        raise ValueError("Cette fonction exige un échantillonnage régulier")
    sample_step = float(np.median(dt))
    fs = 1.0 / sample_step
    frequencies, power = signal.periodogram(
        x,
        fs=fs,
        window="hann",
        detrend="linear",
        scaling="spectrum",
    )
    valid = frequencies > 0
    frequencies = frequencies[valid]
    power = power[valid]
    periods = 1.0 / frequencies
    band = (periods >= min_period_years) & (periods <= max_period_years)
    frequencies = frequencies[band]
    periods = periods[band]
    power = power[band]
    if power.size == 0:
        raise ValueError("Aucune fréquence ne tombe dans la bande demandée")

    phi = estimate_ar1(x)
    rng = np.random.default_rng(seed)
    std = float(np.std(signal.detrend(x)))
    surrogate_powers = []
    for _ in range(int(red_noise_surrogates)):
        surrogate = _ar1_series(phi, x.size, std, rng)
        f_s, p_s = signal.periodogram(
            surrogate,
            fs=fs,
            window="hann",
            detrend="linear",
            scaling="spectrum",
        )
        p_s = p_s[f_s > 0]
        surrogate_powers.append(p_s[band])
    if surrogate_powers:
        threshold = np.quantile(np.vstack(surrogate_powers), confidence, axis=0)
    else:
        threshold = np.full_like(power, np.nan)

    spectrum = pd.DataFrame(
        {
            "frequency_per_year": frequencies,
            "period_years": periods,
            "power": power,
            "red_noise_threshold": threshold,
            "significant": power > threshold,
        }
    ).sort_values("period_years")

    peak_indices, properties = signal.find_peaks(
        power, prominence=max(float(power.max()) * 0.01, 0.0)
    )
    if peak_indices.size == 0:
        peak_indices = np.argsort(power)[-min(peak_count, power.size) :]
    ranked = peak_indices[np.argsort(power[peak_indices])[::-1]][:peak_count]
    peaks = pd.DataFrame(
        {
            "period_years": periods[ranked],
            "frequency_per_year": frequencies[ranked],
            "power": power[ranked],
            "red_noise_threshold": threshold[ranked],
            "significant": power[ranked] > threshold[ranked],
        }
    ).sort_values("power", ascending=False, ignore_index=True)
    return SpectrumResult(spectrum=spectrum, peaks=peaks, ar1_phi=phi)
