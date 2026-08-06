"""Adaptateur de démonstration technique, sans statut scientifique.

Il simule des groupes indépendants composés de trajectoires temporelles, puis
réexécute trois modèles de même protocole en validation leave-one-group-out.
Il sert uniquement à tester l'interface du moteur de puissance.
"""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np


def _fit_predict(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray) -> np.ndarray:
    coefficients, *_ = np.linalg.lstsq(train_x, train_y, rcond=None)
    return test_x @ coefficients


def _sign_flip_pvalue(differences: np.ndarray, rng: np.random.Generator, permutations: int = 2000) -> float:
    observed = float(np.mean(differences))
    signs = rng.choice(np.array([-1.0, 1.0]), size=(permutations, len(differences)))
    null_values = np.mean(signs * differences, axis=1)
    return (1.0 + float(np.sum(null_values >= observed))) / (permutations + 1.0)


def simulate_and_evaluate(*, rng: np.random.Generator, plan: Mapping[str, Any], n: int, effect: Mapping[str, Any]) -> dict[str, bool | float]:
    time_points = 6
    group_ids = np.repeat(np.arange(n), time_points)
    state = np.empty(n * time_points)
    history = np.empty_like(state)
    outcome = np.empty_like(state)
    absolute_effect = float(effect["absolute"])

    for group in range(n):
        start = group * time_points
        stop = start + time_points
        innovations = rng.normal(0.0, 1.0, size=time_points)
        trajectory = np.empty(time_points)
        trajectory[0] = innovations[0]
        for index in range(1, time_points):
            trajectory[index] = 0.65 * trajectory[index - 1] + innovations[index]
        lagged_history = np.concatenate(([0.0], np.cumsum(trajectory[:-1]) / np.arange(1, time_points)))
        baseline = rng.normal(0.0, 0.7)
        noise = rng.normal(0.0, 1.0, size=time_points)
        state[start:stop] = trajectory
        history[start:stop] = lagged_history
        outcome[start:stop] = baseline + 0.7 * trajectory + absolute_effect * lagged_history + noise

    group_permutation = rng.permutation(n)
    shuffled_history = np.empty_like(history)
    for target_group, source_group in enumerate(group_permutation):
        target = slice(target_group * time_points, (target_group + 1) * time_points)
        source = slice(source_group * time_points, (source_group + 1) * time_points)
        shuffled_history[target] = history[source]

    mae_state = []
    mae_history = []
    mae_shuffled = []
    for held_out in range(n):
        train = group_ids != held_out
        test = ~train
        intercept_train = np.ones(int(np.sum(train)))
        intercept_test = np.ones(int(np.sum(test)))
        x_state_train = np.column_stack((intercept_train, state[train]))
        x_state_test = np.column_stack((intercept_test, state[test]))
        x_history_train = np.column_stack((intercept_train, state[train], history[train]))
        x_history_test = np.column_stack((intercept_test, state[test], history[test]))
        x_shuffled_train = np.column_stack((intercept_train, state[train], shuffled_history[train]))
        x_shuffled_test = np.column_stack((intercept_test, state[test], shuffled_history[test]))
        y_test = outcome[test]
        mae_state.append(float(np.mean(np.abs(y_test - _fit_predict(x_state_train, outcome[train], x_state_test)))))
        mae_history.append(float(np.mean(np.abs(y_test - _fit_predict(x_history_train, outcome[train], x_history_test)))))
        mae_shuffled.append(float(np.mean(np.abs(y_test - _fit_predict(x_shuffled_train, outcome[train], x_shuffled_test)))))

    gain_state = np.asarray(mae_state) - np.asarray(mae_history)
    gain_shuffled = np.asarray(mae_shuffled) - np.asarray(mae_history)
    alpha = float(plan["alpha"])
    p_state = _sign_flip_pvalue(gain_state, rng)
    p_shuffled = _sign_flip_pvalue(gain_shuffled, rng)
    return {
        "history_beats_state": bool(np.mean(gain_state) > 0.0 and p_state < alpha),
        "history_beats_shuffled_history": bool(np.mean(gain_shuffled) > 0.0 and p_shuffled < alpha),
        "p_state": p_state,
        "p_shuffled": p_shuffled,
    }
