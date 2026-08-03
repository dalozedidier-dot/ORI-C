from oric_solar_history.backends.surrogate import run_surrogate


def test_counterfactual_changes_earth_series():
    baseline = run_surrogate(500_000, 1000, {"name": "baseline", "modifications": {}}, 1)
    altered = run_surrogate(
        500_000,
        1000,
        {"name": "altered", "modifications": {"Jupiter": {"mass_scale": 1.1}}},
        1,
    )
    e0 = baseline[baseline.body == "Earth"].eccentricity.to_numpy()
    e1 = altered[altered.body == "Earth"].eccentricity.to_numpy()
    assert not (e0 == e1).all()
