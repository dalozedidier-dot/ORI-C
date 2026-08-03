from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import signal


def make_synthetic_archive(
    insolation: pd.DataFrame,
    sampling_step_years: float,
    age_jitter_years: float,
    noise_std: float,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    max_age = float(insolation["time_years"].max())
    ages = np.arange(0.0, max_age + sampling_step_years, sampling_step_years)
    ages += rng.normal(0.0, age_jitter_years, size=ages.size)
    ages = np.clip(ages, 0.0, max_age)
    ages = np.unique(np.sort(ages))
    proxy = np.interp(
        ages,
        insolation["time_years"].to_numpy(),
        insolation["insolation_w_m2"].to_numpy(),
    )
    proxy = (proxy - proxy.mean()) / max(proxy.std(), 1e-12)
    proxy = 0.7 * proxy + rng.normal(0.0, noise_std, size=proxy.size)
    return pd.DataFrame(
        {
            "age_years": ages,
            "proxy": proxy,
            "age_sigma_years": np.full(ages.size, age_jitter_years),
            "source": "synthetic_pipeline_test",
        }
    )


def lomb_scargle_archive(
    archive: pd.DataFrame,
    min_period_years: float,
    max_period_years: float,
    n_frequencies: int = 5000,
) -> pd.DataFrame:
    t = archive["age_years"].to_numpy(dtype=float)
    y = archive["proxy"].to_numpy(dtype=float)
    y = signal.detrend(y)
    frequencies = np.linspace(1.0 / max_period_years, 1.0 / min_period_years, n_frequencies)
    angular = 2.0 * np.pi * frequencies
    power = signal.lombscargle(t, y, angular, normalize=True)
    return pd.DataFrame(
        {
            "frequency_per_year": frequencies,
            "period_years": 1.0 / frequencies,
            "power": power,
        }
    ).sort_values("period_years")


def compare_archive_to_forcing(forcing: pd.DataFrame, archive: pd.DataFrame) -> dict:
    t = archive["age_years"].to_numpy(dtype=float)
    y = archive["proxy"].to_numpy(dtype=float)
    x = np.interp(
        t,
        forcing["time_years"].to_numpy(dtype=float),
        forcing["insolation_w_m2"].to_numpy(dtype=float),
    )
    x = (x - x.mean()) / max(x.std(), 1e-12)
    y = (y - y.mean()) / max(y.std(), 1e-12)
    return {
        "n_archive_points": int(t.size),
        "pearson_correlation": float(np.corrcoef(x, y)[0, 1]),
        "age_min_years": float(t.min()),
        "age_max_years": float(t.max()),
    }


def load_archive(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    required = {"age_years", "proxy"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Colonnes d'archive manquantes: {sorted(missing)}")
    return frame.sort_values("age_years", ignore_index=True)
