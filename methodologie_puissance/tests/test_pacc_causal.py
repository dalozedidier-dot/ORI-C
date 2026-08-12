from __future__ import annotations

import numpy as np

from methodologie_puissance.pacc_causal import (
    DEFINITION_ID,
    PAccInputError,
    estimate_matched_intervention_pacc,
)


MATCHED = {
    "X_matched": True,
    "Theta_matched": True,
    "architecture_matched": True,
    "m_targeted_only": True,
    "independent_units": True,
    "challenge_set_predeclared": True,
    "thresholds_predeclared": True,
    "future_response_after_intervention": True,
}


def fixture_arrays():
    # 4 unités, 2 défis, 2 dimensions = 4 cellules par unité.
    # Contrôle: 3/4 accessibles. Intervention: 2/4 accessibles. Sham = contrôle.
    x = np.zeros((4, 2))
    control_unit = np.array([[2.0, 2.0], [2.0, 0.0]])
    intervention_unit = np.array([[2.0, 0.0], [2.0, 0.0]])
    control = np.repeat(control_unit[None, :, :], 4, axis=0)
    intervention = np.repeat(intervention_unit[None, :, :], 4, axis=0)
    return x, control, intervention


def test_estimateur_non_sature_et_apparie() -> None:
    x, control, intervention = fixture_arrays()
    result = estimate_matched_intervention_pacc(
        X_anchor=x,
        control_response=control,
        intervention_response=intervention,
        sham_response=control.copy(),
        materiality_thresholds=[1.0, 1.0],
        matching=MATCHED,
        bootstrap_repeats=200,
    )
    assert result["definition_id"] == DEFINITION_ID
    assert result["P_acc_control_mean"] == 0.75
    assert result["P_acc_intervention_mean"] == 0.5
    assert result["Delta_P_acc_mean"] == -0.25
    assert result["causal_qualified"] is True
    assert result["causal_effect_nonzero_at_95pct"] is True
    assert result["sham"]["max_abs_Delta_vs_control"] == 0.0


def test_un_appariement_manquant_interdit_le_label_causal() -> None:
    x, control, intervention = fixture_arrays()
    matching = dict(MATCHED)
    matching["Theta_matched"] = False
    result = estimate_matched_intervention_pacc(
        X_anchor=x,
        control_response=control,
        intervention_response=intervention,
        sham_response=control.copy(),
        materiality_thresholds=[1.0, 1.0],
        matching=matching,
        bootstrap_repeats=50,
    )
    assert result["causal_qualified"] is False
    assert result["status"] == "descriptive_only_unqualified"
    assert "Theta_matched" in result["matching"]["failed_or_missing_flags"]


def test_absence_de_sham_interdit_le_label_causal() -> None:
    x, control, intervention = fixture_arrays()
    result = estimate_matched_intervention_pacc(
        X_anchor=x,
        control_response=control,
        intervention_response=intervention,
        materiality_thresholds=[1.0, 1.0],
        matching=MATCHED,
        bootstrap_repeats=50,
    )
    assert result["causal_qualified"] is False
    assert result["sham"]["available"] is False


def test_formes_incompatibles_refusees() -> None:
    x, control, intervention = fixture_arrays()
    bad = intervention[:, :, :1]
    try:
        estimate_matched_intervention_pacc(
            X_anchor=x,
            control_response=control,
            intervention_response=bad,
            materiality_thresholds=[1.0, 1.0],
            matching=MATCHED,
        )
    except PAccInputError:
        pass
    else:
        raise AssertionError("une forme incompatible doit être refusée")
