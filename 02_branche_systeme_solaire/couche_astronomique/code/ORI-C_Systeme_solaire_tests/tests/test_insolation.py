import numpy as np

from oric_solar_history.insolation import daily_mean_insolation


def test_insolation_is_positive_and_sensitive_to_perihelion():
    e = np.array([0.03, 0.03])
    varpi = np.array([np.deg2rad(90.0), np.deg2rad(270.0)])
    q = daily_mean_insolation(e, varpi, 65.0, 90.0)
    assert np.all(q > 0)
    assert q[0] > q[1]
