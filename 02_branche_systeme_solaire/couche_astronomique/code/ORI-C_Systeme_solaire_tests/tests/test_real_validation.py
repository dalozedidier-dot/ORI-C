from pathlib import Path

import numpy as np

from oric_solar_history.real_validation import (
    load_la2010_eccentricity,
    metrics_by_horizon,
    multitaper_spectrum,
    target_band_metrics,
)


def test_loads_la2010_time_in_years(tmp_path: Path):
    path = tmp_path / "ecc.dat"
    path.write_text("0 0.0167\n-1 0.0171\n-2 0.0175\n", encoding="utf-8")
    frame = load_la2010_eccentricity(path)
    assert frame["time_years"].tolist() == [-2000.0, -1000.0, 0.0]


def test_multitaper_recovers_long_period_and_reference_metrics():
    time = np.arange(-20_000_000.0, 1.0, 1000.0)
    values = np.sin(2 * np.pi * time / 405_000.0)
    spectrum = multitaper_spectrum(
        time,
        values,
        min_period_years=100_000,
        max_period_years=1_000_000,
    )
    bands = target_band_metrics(
        spectrum,
        {"405 kyr": (350_000.0, 460_000.0, 405_000.0)},
    )
    assert float(bands.iloc[0]["relative_period_error"]) < 0.02

    candidate = {
        "time_years": time,
        "eccentricity": values,
    }
    reference = {
        "time_years": time,
        "eccentricity": values + 1e-6,
    }
    import pandas as pd

    metrics = metrics_by_horizon(
        pd.DataFrame(candidate),
        pd.DataFrame(reference),
        [1_000_000],
    )
    assert float(metrics.iloc[0]["correlation"]) > 0.999999
    assert np.isclose(float(metrics.iloc[0]["rmse"]), 1e-6)
