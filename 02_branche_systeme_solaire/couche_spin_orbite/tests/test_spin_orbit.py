from pathlib import Path
import sys

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from spin_orbit import (
    ALPHA_SOLAR_ONLY_ARCSEC_PER_YEAR,
    ALPHA_WITH_MOON_ARCSEC_PER_YEAR,
    daily_mean_insolation,
    initial_spin,
    integrate_spin_batch,
    orbital_normals,
)


def toy_orbit(samples=21):
    t = np.arange(samples, dtype=float) * 1000.0
    inc = np.deg2rad(1.5 + 0.3 * np.sin(2 * np.pi * t / 70000.0))
    node = np.mod(-2 * np.pi * t / 70000.0, 2 * np.pi)
    return pd.DataFrame({
        "time_years": -t,
        "elapsed_years": t,
        "eccentricity": 0.0167 + 0.002 * np.sin(2 * np.pi * t / 100000.0),
        "inclination_rad": inc,
        "long_node_rad": node,
        "arg_peri_rad": np.mod(2 * np.pi * t / 120000.0, 2 * np.pi),
    })


def test_initial_spin_has_requested_obliquity():
    frame = toy_orbit(2)
    n = orbital_normals(frame)[0]
    s = initial_spin(n, 23.43929111)
    angle = np.degrees(np.arccos(np.clip(np.dot(n, s), -1.0, 1.0)))
    assert abs(angle - 23.43929111) < 1e-10


def test_moon_and_ablation_produce_distinct_spin_paths():
    frame = toy_orbit(101)
    obl, _, _ = integrate_spin_batch(
        [frame, frame],
        np.array([ALPHA_WITH_MOON_ARCSEC_PER_YEAR, ALPHA_SOLAR_ONLY_ARCSEC_PER_YEAR]),
        substeps_per_orbital_sample=5,
    )
    assert np.max(np.abs(obl[0] - obl[1])) > 0.1


def test_rk4_converges_when_substep_is_halved():
    frame = toy_orbit(101)
    coarse, _, _ = integrate_spin_batch([frame], ALPHA_WITH_MOON_ARCSEC_PER_YEAR, 10)
    fine, _, _ = integrate_spin_batch([frame], ALPHA_WITH_MOON_ARCSEC_PER_YEAR, 20)
    assert np.sqrt(np.mean((coarse[0] - fine[0]) ** 2)) < 1e-4


def test_insolation_responds_to_dynamic_obliquity():
    e = np.array([0.0167, 0.0167])
    p = np.array([1.8, 1.8])
    q = daily_mean_insolation(e, p, np.array([10.0, 40.0]))
    assert q[1] > q[0]
