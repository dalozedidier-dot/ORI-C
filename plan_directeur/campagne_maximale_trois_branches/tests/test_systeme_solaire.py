from __future__ import annotations


def test_astronomical_acceptance_is_not_overstated(solar_result):
    result = solar_result["astronomical_acceptance"]
    assert result["criteria"] == 15
    assert result["passed"] == 13
    assert result["failed"] == 2
    assert {row["test"] for row in result["failed_tests"]} == {
        "angular_momentum_conservation",
        "roundtrip_reversibility_100kyr",
    }


def test_interventions_are_separated_from_selected_numerical_floor(solar_result):
    result = solar_result["numerical_effect_separation"]
    assert result["minimum_ratio"] > 1000
    assert len(result["intervention_to_numerical_ratios"]) == 6


def test_paired_interventions_show_different_symmetries(solar_result):
    pairs = solar_result["paired_intervention_symmetry"]
    assert pairs["jupiter_semimajor_axis"]["mean_delta_changes_sign"] is False
    assert pairs["jupiter_mass"]["mean_delta_changes_sign"] is True
    assert pairs["saturn_mass"]["mean_delta_changes_sign"] is True


def test_long_bands_are_not_misread_from_short_interventions(solar_result):
    unresolved = solar_result["band_selectivity"]["unresolved_bands_in_2myr_interventions"]
    assert unresolved == ["2.4 Myr", "405 kyr"]
    resolved = solar_result["band_selectivity"]["resolved_bands_in_2myr_interventions"]
    assert set(resolved) == {"95 kyr", "125 kyr"}


def test_100ka_signal_is_window_dependent(solar_result):
    windows = solar_result["paleoclimate_and_path_dependence"]["100ka_null_test_by_window"]
    assert windows[0]["significant_at_0.05"] is True
    assert windows[1]["significant_at_0.05"] is False
    assert windows[2]["significant_at_0.05"] is False


def test_exoplanet_paths_relax_on_long_hold(solar_result):
    rows = solar_result["paleoclimate_and_path_dependence"]["exoplanet_long_hold"]
    assert all(item["ever_material"] is False for item in rows.values())
    assert max(item["retained_fraction"] for item in rows.values()) < 1e-10
