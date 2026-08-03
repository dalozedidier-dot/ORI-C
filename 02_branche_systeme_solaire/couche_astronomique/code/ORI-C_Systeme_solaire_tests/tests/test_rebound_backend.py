import numpy as np
import pytest

from oric_solar_history.backends.rebound_backend import run_rebound


def test_rebound_backend_accepts_named_particles():
    pytest.importorskip("rebound")
    frame = run_rebound(
        duration_years=0.1,
        output_step_years=0.05,
        scenario={"modifications": {}},
        seed=20260729,
        rebound_cfg={
            "integrator": "whfast",
            "timestep_years": 0.01,
            "exact_finish_time": False,
            "include_planets": ["Earth", "Jupiter"],
            "ejection_radius_au": 200.0,
        },
    )
    assert not frame.empty
    assert set(frame["body"]) == {"Earth", "Jupiter"}
    assert frame["bound"].all()
    earth = frame[frame["body"] == "Earth"]
    assert np.allclose(np.diff(earth["time_years"]), 0.05)
    assert (earth["integration_time_years"] - earth["time_years"]).abs().max() <= 0.01 + 1e-12


def test_horizons_gr_run_starts_at_la2010_eccentricity_and_goes_backward():
    pytest.importorskip("rebound")
    pytest.importorskip("reboundx")
    frame = run_rebound(
        duration_years=1.0,
        output_step_years=0.5,
        scenario={"name": "baseline", "modifications": {}},
        seed=20260729,
        rebound_cfg={
            "integrator": "whfast",
            "timestep_years": 0.01,
            "exact_finish_time": False,
            "initial_conditions": "horizons_j2000",
            "time_direction": "backward",
            "general_relativity": "gr_potential",
            "include_bodies": [
                "Mercury",
                "Venus",
                "Earth",
                "Mars",
                "Jupiter",
                "Saturn",
                "Uranus",
                "Neptune",
            ],
        },
    )
    earth = frame.loc[frame["body"] == "Earth"].reset_index(drop=True)
    assert abs(float(earth.iloc[0]["eccentricity"]) - 0.016702362) < 1e-8
    assert earth["time_years"].tolist() == [0.0, -0.5, -1.0]
    assert frame["bound"].all()
