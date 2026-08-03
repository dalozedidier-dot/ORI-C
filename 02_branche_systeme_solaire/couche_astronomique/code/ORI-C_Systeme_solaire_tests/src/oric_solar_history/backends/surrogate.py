from __future__ import annotations

import numpy as np
import pandas as pd


def _scenario_factors(modifications: dict) -> tuple[float, float, float]:
    j = modifications.get("Jupiter", {})
    s = modifications.get("Saturn", {})
    j_mass = float(j.get("mass_scale", 1.0))
    j_a = float(j.get("a_scale", 1.0))
    s_mass = float(s.get("mass_scale", 1.0))
    s_a = float(s.get("a_scale", 1.0))

    frequency_factor = 1.0 + 0.18 * (j_mass - 1.0) - 0.12 * (j_a - 1.0)
    frequency_factor += 0.10 * (s_mass - 1.0) - 0.08 * (s_a - 1.0)
    amplitude_factor = 1.0 + 0.45 * (j_mass - 1.0) + 0.25 * (s_mass - 1.0)
    phase_shift = 2.0 * np.pi * (0.7 * (j_a - 1.0) - 0.4 * (s_a - 1.0))
    return frequency_factor, amplitude_factor, phase_shift


def run_surrogate(
    duration_years: float,
    output_step_years: float,
    scenario: dict,
    seed: int,
    realization: int = 0,
) -> pd.DataFrame:
    """Generate deterministic synthetic orbital series.

    This backend validates the analysis pipeline only. It is deliberately not an
    N-body approximation and must never be used as scientific evidence.
    """
    times = np.arange(0.0, duration_years + 0.5 * output_step_years, output_step_years)
    mods = scenario.get("modifications", {})
    f_factor, a_factor, phase = _scenario_factors(mods)
    rng = np.random.default_rng(seed + 1009 * realization)
    tiny_phase = rng.normal(0.0, 1e-4)

    p405 = 405_000.0 / f_factor
    p100 = 100_000.0 / (1.0 + 0.08 * (f_factor - 1.0))
    p95 = 95_000.0 / (1.0 - 0.05 * (f_factor - 1.0))
    p24m = 2_400_000.0 / (1.0 + 0.25 * (f_factor - 1.0))

    e = (
        0.028
        + a_factor * 0.0100 * np.sin(2 * np.pi * times / p405 + 0.3 + phase + tiny_phase)
        + a_factor * 0.0060 * np.sin(2 * np.pi * times / p100 + 1.1)
        + a_factor * 0.0035 * np.sin(2 * np.pi * times / p95 - 0.7)
        + 0.0020 * np.sin(2 * np.pi * times / p24m + 0.4)
    )
    e = np.clip(e, 0.001, 0.12)
    inc = np.deg2rad(
        1.6
        + 0.6 * np.sin(2 * np.pi * times / 70_000.0 + 0.2)
        + 0.25 * np.sin(2 * np.pi * times / 1_200_000.0)
    )
    varpi = np.mod(2 * np.pi * times / 23_000.0 + 0.4 * np.sin(2 * np.pi * times / p405), 2 * np.pi)
    node = np.mod(-2 * np.pi * times / 70_000.0, 2 * np.pi)
    omega = np.mod(varpi - node, 2 * np.pi)
    mean_longitude = np.mod(2 * np.pi * times + varpi, 2 * np.pi)

    earth = pd.DataFrame(
        {
            "time_years": times,
            "body": "Earth",
            "a_au": 1.0 + 2e-5 * np.sin(2 * np.pi * times / 100_000.0),
            "eccentricity": e,
            "inclination_rad": inc,
            "long_node_rad": node,
            "arg_peri_rad": omega,
            "long_peri_rad": varpi,
            "mean_longitude_rad": mean_longitude,
            "energy_rel_error": 0.0,
            "angmom_rel_error": 0.0,
            "bound": True,
            "backend": "surrogate",
        }
    )

    # Add giant planets so output schemas match the N-body backend.
    rows = [earth]
    for body, a, period, e0 in [
        ("Jupiter", 5.203, 11.862, 0.048),
        ("Saturn", 9.537, 29.447, 0.054),
    ]:
        rows.append(
            pd.DataFrame(
                {
                    "time_years": times,
                    "body": body,
                    "a_au": a,
                    "eccentricity": e0 + 0.002 * np.sin(2 * np.pi * times / 50_000.0),
                    "inclination_rad": np.deg2rad(1.5),
                    "long_node_rad": np.mod(-2 * np.pi * times / 100_000.0, 2 * np.pi),
                    "arg_peri_rad": np.mod(2 * np.pi * times / 80_000.0, 2 * np.pi),
                    "long_peri_rad": np.mod(2 * np.pi * times / 80_000.0, 2 * np.pi),
                    "mean_longitude_rad": np.mod(2 * np.pi * times / period, 2 * np.pi),
                    "energy_rel_error": 0.0,
                    "angmom_rel_error": 0.0,
                    "bound": True,
                    "backend": "surrogate",
                }
            )
        )
    return pd.concat(rows, ignore_index=True)
