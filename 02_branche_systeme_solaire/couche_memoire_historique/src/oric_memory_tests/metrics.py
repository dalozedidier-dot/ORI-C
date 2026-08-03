from __future__ import annotations

import math

import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks, periodogram
from scipy.stats import wilcoxon


def rmse(observed: np.ndarray, predicted: np.ndarray) -> float:
    return float(np.sqrt(np.mean((np.asarray(observed) - np.asarray(predicted)) ** 2)))


def correlation(observed: np.ndarray, predicted: np.ndarray) -> float:
    observed = np.asarray(observed)
    predicted = np.asarray(predicted)
    if np.std(observed) == 0.0 or np.std(predicted) == 0.0:
        return float("nan")
    return float(np.corrcoef(observed, predicted)[0, 1])


def best_lag_correlation(
    observed: np.ndarray, predicted: np.ndarray, max_lag: int = 30
) -> tuple[int, float]:
    best_lag = 0
    best_value = -np.inf
    observed = np.asarray(observed)
    predicted = np.asarray(predicted)
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            left, right = observed[-lag:], predicted[:lag]
        elif lag > 0:
            left, right = observed[:-lag], predicted[lag:]
        else:
            left, right = observed, predicted
        value = correlation(left, right)
        if np.isfinite(value) and value > best_value:
            best_lag, best_value = lag, value
    return int(best_lag), float(best_value)


def spectral_band_energy(
    series: np.ndarray,
    period_min: float,
    period_max: float,
    step: float = 1.0,
) -> float:
    values = np.asarray(series, dtype=float)
    frequency, power = periodogram(
        values - np.mean(values), fs=1.0 / step, detrend="linear"
    )
    period = np.divide(
        1.0,
        frequency,
        out=np.full_like(frequency, np.inf),
        where=frequency > 0,
    )
    selected = (period >= period_min) & (period <= period_max)
    if selected.sum() == 0:
        return 0.0
    if selected.sum() == 1:
        return float(power[selected][0])
    return float(np.trapezoid(power[selected], frequency[selected]))


def mpt_power_ratio(series: np.ndarray, step: float = 1.0) -> float:
    power_100 = spectral_band_energy(series, 80.0, 120.0, step)
    power_41 = spectral_band_energy(series, 39.0, 43.0, step)
    return float(power_100 / max(power_41, np.finfo(float).tiny))


def log_ratio_error(value: float, reference: float) -> float:
    return float(abs(math.log(max(value, 1e-300) / max(reference, 1e-300))))


def termination_events(
    series: np.ndarray,
    elapsed_kyr: np.ndarray,
    smooth_sigma: float = 2.0,
    minimum_separation_kyr: int = 35,
) -> np.ndarray:
    smooth = gaussian_filter1d(np.asarray(series, dtype=float), smooth_sigma)
    deglaciation_rate = -np.gradient(smooth)
    prominence = max(float(np.std(deglaciation_rate) * 0.6), 1e-8)
    peaks, _ = find_peaks(
        deglaciation_rate,
        distance=max(1, int(minimum_separation_kyr)),
        prominence=prominence,
    )
    return np.asarray(elapsed_kyr)[peaks]


def event_timing_mae(
    observed_events: np.ndarray,
    predicted_events: np.ndarray,
    maximum_match_distance_kyr: float = 60.0,
) -> float:
    if len(observed_events) == 0 or len(predicted_events) == 0:
        return float("inf")
    distances = []
    for event in observed_events:
        distance = float(np.min(np.abs(predicted_events - event)))
        if distance <= maximum_match_distance_kyr:
            distances.append(distance)
        else:
            distances.append(maximum_match_distance_kyr)
    return float(np.mean(distances))


def lag1_autocorrelation(series: np.ndarray) -> float:
    series = np.asarray(series, dtype=float)
    series = series - series.mean()
    denominator = float(np.sum(series * series))
    if denominator == 0.0:
        return 0.0
    return float(np.sum(series[:-1] * series[1:]) / denominator)


def effective_sample_size(residuals: np.ndarray) -> float:
    """Nombre de points indépendants d'un résidu autocorrélé.

    Sur une grille de 1 ka, les résidus d18O ont une autocorrélation de rang 1
    proche de 0,97. Traiter les 1 200 points comme indépendants gonfle la
    vraisemblance et rend le terme de pénalité du BIC négligeable. On applique
    la correction AR(1) usuelle n_eff = n (1 - rho) / (1 + rho).
    """
    rho = min(max(lag1_autocorrelation(residuals), -0.999), 0.999)
    return float(len(residuals) * (1.0 - rho) / (1.0 + rho))


def information_criteria(
    residuals: np.ndarray,
    parameter_count: int,
    sample_size: float | None = None,
) -> dict:
    """Critères d'information.

    `sample_size` permet de substituer la taille d'échantillon efficace à la
    longueur brute de la série. La variance résiduelle reste estimée sur tous
    les points ; seule la contribution en nombre d'observations change.
    """
    residuals = np.asarray(residuals, dtype=float)
    observed_count = len(residuals)
    n = float(observed_count if sample_size is None else sample_size)
    rss = float(np.sum(residuals**2))
    variance = max(rss / observed_count, np.finfo(float).tiny)
    aic = n * math.log(variance) + 2 * parameter_count
    bic = n * math.log(variance) + parameter_count * math.log(max(n, 2.0))
    if n > parameter_count + 1:
        aicc = aic + (
            2 * parameter_count * (parameter_count + 1)
            / (n - parameter_count - 1)
        )
    else:
        aicc = float("inf")
    return {
        "aic": float(aic),
        "aicc": float(aicc),
        "bic": float(bic),
        "sample_size_used": float(n),
    }


def moving_block_bootstrap_gain(
    observed: np.ndarray,
    reference: np.ndarray,
    candidate: np.ndarray,
    block_length: int,
    draws: int,
    seed: int,
) -> np.ndarray:
    """Distribution du gain relatif de RMSE, rééchantillonnée par blocs mobiles.

    Un bootstrap point par point supposerait des résidus indépendants, ce qui
    est faux ici. Les blocs préservent l'autocorrélation.
    """
    observed = np.asarray(observed, dtype=float)
    error_reference = (observed - np.asarray(reference, dtype=float)) ** 2
    error_candidate = (observed - np.asarray(candidate, dtype=float)) ** 2
    n = len(observed)
    block_length = int(max(1, min(block_length, n)))
    block_count = int(np.ceil(n / block_length))
    random = np.random.default_rng(seed)
    gains = np.empty(draws)
    for draw in range(draws):
        starts = random.integers(0, n - block_length + 1, size=block_count)
        index = np.concatenate(
            [np.arange(start, start + block_length) for start in starts]
        )[:n]
        gains[draw] = 1.0 - math.sqrt(
            error_candidate[index].mean()
        ) / math.sqrt(max(error_reference[index].mean(), np.finfo(float).tiny))
    return gains


def contiguous_block_scores(
    observed: np.ndarray,
    predictions: dict[str, np.ndarray],
    block_size: int = 50,
) -> list[dict]:
    observed = np.asarray(observed)
    rows: list[dict] = []
    for start in range(0, len(observed) - block_size + 1, block_size):
        stop = start + block_size
        row = {"block_start_index": start, "block_stop_index": stop}
        for name, values in predictions.items():
            row[f"rmse_{name}"] = rmse(observed[start:stop], values[start:stop])
        rows.append(row)
    return rows


def paired_wilcoxon_greater(first: np.ndarray, second: np.ndarray) -> float:
    difference = np.asarray(first) - np.asarray(second)
    if np.allclose(difference, 0.0):
        return 1.0
    return float(wilcoxon(difference, alternative="greater").pvalue)


def holm_adjust(p_values: list[float]) -> list[float]:
    values = np.asarray(p_values, dtype=float)
    order = np.argsort(values)
    adjusted = np.empty_like(values)
    running = 0.0
    count = len(values)
    for rank, index in enumerate(order):
        candidate = min(1.0, (count - rank) * values[index])
        running = max(running, candidate)
        adjusted[index] = running
    return adjusted.tolist()

