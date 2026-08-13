"""Adaptateur de puissance pour VES-PACC-INT-01.

La simulation est réservée à la planification de puissance. Elle représente la
quantité primaire appariée Delta_P_acc au niveau des populations parentales
indépendantes avec l'écart-type de planification gelé. Elle ne génère aucune
donnée biologique de preuve et ne remplace pas l'inférence finale par bootstrap
préenregistrée dans le protocole.
"""
from __future__ import annotations

from typing import Any, Mapping

import numpy as np
from scipy import stats


def simulate_and_evaluate(
    *,
    rng: np.random.Generator,
    plan: Mapping[str, Any],
    n: int,
    effect: Mapping[str, Any],
) -> dict[str, bool | float]:
    """Simule n contrastes appariés et applique le test bilatéral de planification."""
    sd = float(plan["noise_estimation"]["value"])
    # Le SESOI est une amplitude. Le protocole attend une contraction, donc le
    # contraste simulé est négatif par convention do(m)-contrôle.
    mean_delta = -float(effect["absolute"])
    deltas = rng.normal(loc=mean_delta, scale=sd, size=int(n))
    test = stats.ttest_1samp(deltas, popmean=0.0, alternative="two-sided")
    p_value = float(test.pvalue)
    observed = float(np.mean(deltas))
    return {
        "paired_effect_detected": bool(observed < 0.0 and p_value < float(plan["alpha"])),
        "mean_delta": observed,
        "p_value": p_value,
    }
