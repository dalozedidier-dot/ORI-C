"""Estimateur interventionnel apparié de P_acc.

Ce module ne transforme jamais un support observationnel en accessibilité
causale. Il exige un ensemble de défis futurs déclaré avant observation, des
seuils de matérialité déclarés et des unités indépendantes appariées entre
contrôle et intervention sur m.

La quantité locale est la fraction pondérée des cellules défi×dimension dont
la réponse future s'écarte de l'état d'ancrage X d'au moins le seuil déclaré de
la dimension. Les amplitudes brutes ne sont pas comparables entre domaines
sans une construction commune des défis, seuils et poids.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np

DEFINITION_ID = "PACC-INT-CHALLENGE-V1"
REQUIRED_MATCHING_FLAGS = (
    "X_matched",
    "Theta_matched",
    "architecture_matched",
    "m_targeted_only",
    "independent_units",
    "challenge_set_predeclared",
    "thresholds_predeclared",
    "future_response_after_intervention",
)


class PAccInputError(ValueError):
    """Entrée incompatible avec la définition interventionnelle."""


def _as_response_cube(value: np.ndarray | Sequence[float], name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.ndim != 3:
        raise PAccInputError(f"{name} doit avoir la forme unités×défis×dimensions")
    if not np.isfinite(array).all():
        raise PAccInputError(f"{name} contient une valeur non finie")
    return array


def _broadcast_anchor(anchor: np.ndarray | Sequence[float], shape: tuple[int, int, int]) -> np.ndarray:
    array = np.asarray(anchor, dtype=float)
    n_units, n_challenges, n_dims = shape
    if array.shape == (n_units, n_dims):
        array = np.repeat(array[:, None, :], n_challenges, axis=1)
    elif array.shape == (n_dims,):
        array = np.broadcast_to(array[None, None, :], shape)
    elif array.shape != shape:
        raise PAccInputError(
            "X_anchor doit avoir la forme dimensions, unités×dimensions ou unités×défis×dimensions"
        )
    if not np.isfinite(array).all():
        raise PAccInputError("X_anchor contient une valeur non finie")
    return np.asarray(array, dtype=float)


def _weights(value: np.ndarray | Sequence[float] | None, shape: tuple[int, int]) -> np.ndarray:
    n_challenges, n_dims = shape
    if value is None:
        result = np.ones((n_challenges, n_dims), dtype=float)
    else:
        result = np.asarray(value, dtype=float)
        if result.shape == (n_dims,):
            result = np.broadcast_to(result[None, :], (n_challenges, n_dims)).copy()
        elif result.shape != (n_challenges, n_dims):
            raise PAccInputError("weights doit avoir la forme dimensions ou défis×dimensions")
    if not np.isfinite(result).all() or np.any(result < 0) or float(result.sum()) <= 0:
        raise PAccInputError("weights doit être fini, positif ou nul, avec une somme strictement positive")
    return result / result.sum()


def _thresholds(value: np.ndarray | Sequence[float], n_dims: int) -> np.ndarray:
    result = np.asarray(value, dtype=float)
    if result.shape != (n_dims,):
        raise PAccInputError("materiality_thresholds doit contenir un seuil par dimension")
    if not np.isfinite(result).all() or np.any(result <= 0):
        raise PAccInputError("les seuils de matérialité doivent être finis et strictement positifs")
    return result


def _accessibility(response: np.ndarray, anchor: np.ndarray, thresholds: np.ndarray) -> np.ndarray:
    return np.abs(response - anchor) >= thresholds[None, None, :]


def _pacc_per_unit(accessibility: np.ndarray, weights: np.ndarray) -> np.ndarray:
    return np.sum(accessibility * weights[None, :, :], axis=(1, 2))


def _bootstrap_mean(delta: np.ndarray, repeats: int, seed: int) -> tuple[float, float]:
    if repeats < 1:
        raise PAccInputError("bootstrap_repeats doit être >= 1")
    rng = np.random.default_rng(seed)
    n = len(delta)
    indices = rng.integers(0, n, size=(repeats, n))
    means = delta[indices].mean(axis=1)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def _matching_report(matching: Mapping[str, bool]) -> dict[str, object]:
    flags = {name: bool(matching.get(name, False)) for name in REQUIRED_MATCHING_FLAGS}
    missing = [name for name, ok in flags.items() if not ok]
    return {
        "required_flags": flags,
        "all_required_matching_conditions_met": not missing,
        "failed_or_missing_flags": missing,
    }


def estimate_matched_intervention_pacc(
    *,
    X_anchor: np.ndarray | Sequence[float],
    control_response: np.ndarray | Sequence[float],
    intervention_response: np.ndarray | Sequence[float],
    materiality_thresholds: np.ndarray | Sequence[float],
    matching: Mapping[str, bool],
    sham_response: np.ndarray | Sequence[float] | None = None,
    weights: np.ndarray | Sequence[float] | None = None,
    sham_tolerance: float = 0.0,
    bootstrap_repeats: int = 5000,
    seed: int = 20260812,
) -> dict[str, object]:
    """Calcule P_acc et le contraste apparié contrôle → do(m).

    Le statut causal exige toutes les conditions d'appariement déclarées et un
    sham disponible dont le contraste moyen absolu ne dépasse pas la tolérance
    déclarée. L'absence de ces conditions n'empêche pas le calcul descriptif,
    mais interdit sa qualification causale.
    """
    control = _as_response_cube(control_response, "control_response")
    intervention = _as_response_cube(intervention_response, "intervention_response")
    if control.shape != intervention.shape:
        raise PAccInputError("contrôle et intervention doivent avoir exactement la même forme")
    n_units, n_challenges, n_dims = control.shape
    if n_units < 2:
        raise PAccInputError("au moins deux unités indépendantes sont nécessaires")
    anchor = _broadcast_anchor(X_anchor, control.shape)
    thresholds = _thresholds(materiality_thresholds, n_dims)
    normalized_weights = _weights(weights, (n_challenges, n_dims))

    control_access = _accessibility(control, anchor, thresholds)
    intervention_access = _accessibility(intervention, anchor, thresholds)
    pacc_control = _pacc_per_unit(control_access, normalized_weights)
    pacc_intervention = _pacc_per_unit(intervention_access, normalized_weights)
    delta = pacc_intervention - pacc_control
    q025, q975 = _bootstrap_mean(delta, bootstrap_repeats, seed)

    matching_report = _matching_report(matching)
    sham = None
    sham_ok = False
    if sham_response is not None:
        sham_array = _as_response_cube(sham_response, "sham_response")
        if sham_array.shape != control.shape:
            raise PAccInputError("sham_response doit avoir exactement la même forme que le contrôle")
        pacc_sham = _pacc_per_unit(_accessibility(sham_array, anchor, thresholds), normalized_weights)
        sham_delta = pacc_sham - pacc_control
        sham_max_abs = float(np.max(np.abs(sham_delta)))
        sham_mean_abs = float(np.mean(np.abs(sham_delta)))
        sham_ok = sham_max_abs <= float(sham_tolerance)
        sham = {
            "available": True,
            "P_acc_mean": float(pacc_sham.mean()),
            "Delta_vs_control_mean": float(sham_delta.mean()),
            "max_abs_Delta_vs_control": sham_max_abs,
            "mean_abs_Delta_vs_control": sham_mean_abs,
            "tolerance": float(sham_tolerance),
            "passes": sham_ok,
        }
    else:
        sham = {
            "available": False,
            "passes": False,
            "reason": "un sham apparié est requis pour la qualification causale stricte",
        }

    causal_qualified = bool(matching_report["all_required_matching_conditions_met"] and sham_ok)
    nonzero = bool((q025 > 0.0) or (q975 < 0.0))
    control_non_extreme = float(np.mean((pacc_control > 0.0) & (pacc_control < 1.0)))
    intervention_non_extreme = float(np.mean((pacc_intervention > 0.0) & (pacc_intervention < 1.0)))

    return {
        "schema": "oric.pacc.matched-intervention.v1",
        "definition_id": DEFINITION_ID,
        "definition": (
            "fraction pondérée des cellules défi×dimension dont la réponse future s'écarte de X "
            "d'au moins un seuil de matérialité pré-déclaré"
        ),
        "denominator_cells": int(n_challenges * n_dims),
        "independent_units": int(n_units),
        "challenges": int(n_challenges),
        "response_dimensions": int(n_dims),
        "P_acc_control_mean": float(pacc_control.mean()),
        "P_acc_control_median": float(np.median(pacc_control)),
        "P_acc_intervention_mean": float(pacc_intervention.mean()),
        "P_acc_intervention_median": float(np.median(pacc_intervention)),
        "Delta_P_acc_mean": float(delta.mean()),
        "Delta_P_acc_median": float(np.median(delta)),
        "Delta_P_acc_bootstrap_q025": q025,
        "Delta_P_acc_bootstrap_q975": q975,
        "fraction_units_with_nonzero_Delta": float(np.mean(np.abs(delta) > 0.0)),
        "fraction_control_units_non_extreme": control_non_extreme,
        "fraction_intervention_units_non_extreme": intervention_non_extreme,
        "matching": matching_report,
        "sham": sham,
        "causal_qualified": causal_qualified,
        "causal_effect_nonzero_at_95pct": bool(causal_qualified and nonzero),
        "status": "qualified_matched_intervention" if causal_qualified else "descriptive_only_unqualified",
        "cross_domain_magnitude_comparison_allowed": False,
        "comparability_rule": (
            "comparer directement les amplitudes seulement si défis, dimensions, seuils, poids et unité "
            "de réplication ont la même construction pré-déclarée"
        ),
    }
