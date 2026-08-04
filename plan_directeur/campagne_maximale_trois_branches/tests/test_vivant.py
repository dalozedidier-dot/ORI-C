from __future__ import annotations

import numpy as np


def test_antibiotic_rows_and_final_holdout_are_real(living_result):
    result = living_result["antibiotic_history_robustness"]
    assert result["longitudinal_lineages"] == 203
    assert result["prediction_rows"] == 358
    assert result["final_transition_holdout"]["test_rows"] == 148


def test_group_folds_do_not_mix_test_lineages():
    from analyse_vivant import build_prediction_rows, lineage_folds, load_antibiotic_series
    series, doses = load_antibiotic_series()
    rows = build_prediction_rows(series, doses)
    folds = lineage_folds(rows, folds=10, seed=20260804)
    assert len(folds) == 10
    assert set.union(*folds) == {str(row["lineage"]) for row in rows}
    for index, fold in enumerate(folds):
        assert all(fold.isdisjoint(other) for other in folds[index + 1 :])


def test_history_gain_is_small_and_slope_ablation_does_not_support_order(living_result):
    result = living_result["antibiotic_history_robustness"]
    models = result["group_cross_validation"]["models"]
    assert models["history"]["mae"] < models["equal_complexity"]["mae"]
    assert models["history_no_slope"]["mae"] < models["history"]["mae"]
    assert result["slope_ablation"]["mean"] < 0
    assert result["primary_paired_comparison"]["exact_two_sided_sign_flip_p"] > 0.05
    assert result["slope_ablation"]["exact_two_sided_sign_flip_p"] < 0.05


def test_final_transition_does_not_confirm_history(living_result):
    models = living_result["antibiotic_history_robustness"]["final_transition_holdout"]["models"]
    assert models["state_only"]["mae"] < models["history"]["mae"]
    assert models["equal_complexity"]["mae"] < models["history"]["mae"]


def test_leave_one_dose_out_is_not_uniform(living_result):
    rows = living_result["antibiotic_history_robustness"]["leave_one_dose_out"]
    differences = np.asarray([row["equal_complexity_minus_history"] for row in rows.values()])
    assert np.any(differences > 0)
    assert np.any(differences < 0)


def test_ordered_history_null_is_not_below_five_percent(living_result):
    result = living_result["antibiotic_history_robustness"]["ordered_history_null"]
    assert result["draws"] == 1000
    assert result["one_sided_fraction_null_at_least_observed"] >= 0.05


def test_rna_analysis_keeps_population_scope_explicit(living_result):
    result = living_result["catalytic_rna_frequency_dynamics"]
    assert result["observations"] == 80
    assert result["branches"] == ["52-2", "71-89"]
    assert "tracked" in result["scope"].lower() or "suivi" in result["scope"].lower()
    assert result["branch_dynamics"]["52-2"]["entropy_trend_exact_permutation"]["exact_two_sided_p"] > 0.05
    assert result["branch_dynamics"]["71-89"]["entropy_trend_exact_permutation"]["exact_two_sided_p"] < 0.05
    assert all(
        branch["largest_share_trend_exact_permutation"]["exact_two_sided_p"] > 0.05
        for branch in result["branch_dynamics"].values()
    )


def test_prebiotic_fixture_is_identified_as_synthetic(living_result):
    result = living_result["prebiotic_lineage_schema"]
    assert result["schema_valid"] is True
    assert result["synthetic_marker_detected"] is True
