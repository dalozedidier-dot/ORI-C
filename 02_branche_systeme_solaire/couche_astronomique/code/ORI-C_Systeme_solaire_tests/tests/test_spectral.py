import numpy as np

from oric_solar_history.spectral import analyze_regular_series


def test_detects_405k_signal():
    t = np.arange(0.0, 1_620_001.0, 1000.0)
    x = np.sin(2 * np.pi * t / 405_000.0) + 0.2 * np.sin(2 * np.pi * t / 100_000.0)
    result = analyze_regular_series(
        t,
        x,
        min_period_years=50_000,
        max_period_years=800_000,
        peak_count=5,
        red_noise_surrogates=16,
        seed=1,
    )
    dominant = float(result.peaks.iloc[0]["period_years"])
    assert abs(dominant - 405_000.0) / 405_000.0 < 0.08
