"""Independent-reference and numerical-convergence metrics for real N-body runs."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from scipy import signal


def load_la2010_eccentricity(path: str | Path) -> pd.DataFrame:
    """Load an official IMCCE La2010 t[kyr], eccentricity file."""
    values = np.loadtxt(path, dtype=float)
    if values.ndim != 2 or values.shape[1] != 2:
        raise ValueError(f"Format La2010 inattendu: {path}")
    frame = pd.DataFrame(
        {
            "time_years": values[:, 0] * 1000.0,
            "eccentricity": values[:, 1],
        }
    )
    if frame["time_years"].duplicated().any():
        raise ValueError(f"Temps dupliqués dans {path}")
    return frame.sort_values("time_years").reset_index(drop=True)


def load_earth_output(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    required = {"time_years", "elapsed_years", "eccentricity"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Colonnes terrestres manquantes: {sorted(missing)}")
    return frame.sort_values("time_years").reset_index(drop=True)


def align_eccentricity(
    candidate: pd.DataFrame,
    reference: pd.DataFrame,
    candidate_name: str = "candidate",
    reference_name: str = "reference",
) -> pd.DataFrame:
    left = candidate[["time_years", "eccentricity"]].rename(
        columns={"eccentricity": candidate_name}
    )
    right = reference[["time_years", "eccentricity"]].rename(
        columns={"eccentricity": reference_name}
    )
    aligned = left.merge(right, on="time_years", how="inner", validate="one_to_one")
    return aligned.sort_values("time_years").reset_index(drop=True)


def series_metrics(
    candidate: np.ndarray | pd.Series,
    reference: np.ndarray | pd.Series,
) -> dict[str, float | int]:
    x = np.asarray(candidate, dtype=float)
    y = np.asarray(reference, dtype=float)
    if x.shape != y.shape or x.ndim != 1 or len(x) < 2:
        raise ValueError("Deux séries unidimensionnelles alignées sont requises")
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("Les séries contiennent des valeurs non finies")
    delta = x - y
    correlation = float(np.corrcoef(x, y)[0, 1])
    return {
        "samples": int(len(x)),
        "correlation": correlation,
        "rmse": float(np.sqrt(np.mean(delta**2))),
        "mae": float(np.mean(np.abs(delta))),
        "bias": float(np.mean(delta)),
        "max_abs_error": float(np.max(np.abs(delta))),
        "candidate_std": float(np.std(x, ddof=0)),
        "reference_std": float(np.std(y, ddof=0)),
    }


def metrics_by_horizon(
    candidate: pd.DataFrame,
    reference: pd.DataFrame,
    horizons_years: Iterable[float],
) -> pd.DataFrame:
    aligned = align_eccentricity(candidate, reference)
    aligned["elapsed_years"] = aligned["time_years"].abs()
    rows: list[dict[str, float | int]] = []
    for horizon in horizons_years:
        window = aligned.loc[aligned["elapsed_years"] <= float(horizon)]
        if len(window) < 2:
            continue
        metrics = series_metrics(window["candidate"], window["reference"])
        rows.append({"horizon_years": float(horizon), **metrics})
    return pd.DataFrame(rows)


def multitaper_spectrum(
    time_years: np.ndarray | pd.Series,
    values: np.ndarray | pd.Series,
    min_period_years: float,
    max_period_years: float,
    time_halfbandwidth: float = 4.0,
    taper_count: int = 7,
) -> pd.DataFrame:
    """Estimate a deterministic DPSS multitaper spectrum on a regular grid."""
    time_values = np.asarray(time_years, dtype=float)
    series_values = np.asarray(values, dtype=float)
    if (
        time_values.ndim != 1
        or series_values.ndim != 1
        or len(time_values) != len(series_values)
        or len(time_values) < 16
    ):
        raise ValueError("Série régulière trop courte ou dimensions incompatibles")
    order = np.argsort(time_values)
    time_values = time_values[order]
    series_values = series_values[order]
    steps = np.diff(time_values)
    step = float(np.median(steps))
    if step <= 0 or not np.allclose(steps, step, rtol=1e-9, atol=1e-8):
        raise ValueError("Le multitaper exige un échantillonnage régulier")
    centered = signal.detrend(series_values, type="linear")
    tapers = signal.windows.dpss(
        len(centered),
        NW=float(time_halfbandwidth),
        Kmax=int(taper_count),
        sym=False,
    )
    frequency = np.fft.rfftfreq(len(centered), d=step)
    spectra = []
    sample_frequency = 1.0 / step
    for taper in tapers:
        transform = np.fft.rfft(centered * taper)
        spectra.append(np.abs(transform) ** 2 / (sample_frequency * float(np.sum(taper**2))))
    power = np.mean(np.asarray(spectra), axis=0)
    keep = frequency > 0
    frequency = frequency[keep]
    power = power[keep]
    period = 1.0 / frequency
    keep = (period >= float(min_period_years)) & (period <= float(max_period_years))
    return pd.DataFrame(
        {
            "frequency_per_year": frequency[keep],
            "period_years": period[keep],
            "power": power[keep],
        }
    ).sort_values("frequency_per_year", ignore_index=True)


def target_band_metrics(
    spectrum: pd.DataFrame,
    bands: dict[str, tuple[float, float, float]],
) -> pd.DataFrame:
    """Return peak period and normalized integrated power for named bands."""
    required = {"frequency_per_year", "period_years", "power"}
    missing = required - set(spectrum.columns)
    if missing:
        raise ValueError(f"Colonnes spectrales manquantes: {sorted(missing)}")
    frequency = spectrum["frequency_per_year"].to_numpy(dtype=float)
    power = spectrum["power"].to_numpy(dtype=float)
    total = float(np.trapezoid(power, frequency))
    rows: list[dict[str, float | str]] = []
    for name, (low_period, high_period, nominal_period) in bands.items():
        band = spectrum.loc[spectrum["period_years"].between(low_period, high_period)]
        if band.empty:
            rows.append(
                {
                    "band": name,
                    "low_period_years": low_period,
                    "high_period_years": high_period,
                    "nominal_period_years": nominal_period,
                    "peak_period_years": np.nan,
                    "relative_period_error": np.nan,
                    "normalized_band_power": np.nan,
                }
            )
            continue
        peak = band.loc[band["power"].idxmax()]
        band_frequency = band["frequency_per_year"].to_numpy(dtype=float)
        band_power = band["power"].to_numpy(dtype=float)
        integrated = float(np.trapezoid(band_power, band_frequency)) if len(band) > 1 else 0.0
        peak_period = float(peak["period_years"])
        rows.append(
            {
                "band": name,
                "low_period_years": low_period,
                "high_period_years": high_period,
                "nominal_period_years": nominal_period,
                "peak_period_years": peak_period,
                "relative_period_error": abs(peak_period - nominal_period) / nominal_period,
                "normalized_band_power": integrated / total if total > 0 else np.nan,
            }
        )
    return pd.DataFrame(rows)


def top_local_peaks(spectrum: pd.DataFrame, count: int = 12) -> pd.DataFrame:
    power = spectrum["power"].to_numpy(dtype=float)
    if len(power) < 3:
        return spectrum.nlargest(count, "power").copy()
    indices, properties = signal.find_peaks(
        np.log10(np.maximum(power, np.finfo(float).tiny)),
        prominence=0.05,
    )
    peaks = spectrum.iloc[indices].copy()
    peaks["log10_prominence"] = properties["prominences"]
    return peaks.nlargest(count, "power").reset_index(drop=True)
