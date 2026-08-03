"""Noyau de simulation MPT accéléré.

`simulate_mpt` reste la définition de référence des modèles. Ce module en
fournit une transcription équivalente, compilée par numba lorsque celui-ci est
disponible et exécutée en Python pur sinon. Elle sert uniquement à l'intérieur
de la boucle d'optimisation, qui exige des centaines de milliers d'évaluations.

L'égalité avec la référence est vérifiée par `verify_against_reference`, appelée
par la suite de tests. Le budget d'optimisation du protocole corrigé n'est
atteignable en un temps raisonnable qu'avec numba ; sans lui le calcul reste
exact mais environ cent fois plus lent.
"""

from __future__ import annotations

import math

import numpy as np

# Codes des modèles partagés entre la référence et le noyau rapide.
MODEL_CODE = {"M0": 0, "M1": 1, "M2": 2, "M1P": 3, "M2_ablation": 4}


def _core(code, forcing, initial_ice, p):
    """Simulation d'un modèle MPT. `p` est un vecteur de neuf réels décodés.

    Emplacements de `p` :
      0 forcing_gain, 1 forcing_offset, 2 tau rapide, 3 tau_memory_gain,
      4 regolith_scale, 5 tau_regolith, 6 gain de l'état lent,
      7 tau de l'état lent, 8 décalage de l'état lent.

    Pour M0 seuls 0, 1 et 2 sont lus, 2 valant tau_ice_kyr.
    """
    n = forcing.shape[0]
    ice = np.empty(n)
    ice[0] = initial_ice

    if code == 0:
        gain = p[0]
        offset = p[1]
        tau = p[2]
        for i in range(1, n):
            target = gain * forcing[i - 1] + offset
            ice[i] = ice[i - 1] + (target - ice[i - 1]) / tau
        return ice

    gain = p[0]
    offset = p[1]
    tau_fast = p[2]
    tau_gain = p[3]
    regolith_scale = p[4]
    tau_regolith = p[5]
    auxiliary_gain = p[6]
    tau_auxiliary = p[7]
    auxiliary_offset = p[8]

    regolith = initial_ice if initial_ice > 0.0 else 0.0
    if code == 2 or code == 4:
        auxiliary = initial_ice + auxiliary_offset
    elif code == 3:
        auxiliary = forcing[0] + auxiliary_offset
    else:
        auxiliary = 0.0

    for i in range(1, n):
        previous_regolith = regolith if regolith > 0.0 else 0.0
        tau = tau_fast + tau_gain * (
            1.0 - math.exp(-previous_regolith / regolith_scale)
        )
        target = gain * forcing[i - 1] + offset
        if code == 2 or code == 3:
            target += auxiliary_gain * auxiliary
        # code 4 : l'état lent continue d'évoluer mais son couplage est retiré.

        previous_ice = ice[i - 1]
        ice[i] = previous_ice + (target - previous_ice) / tau
        regolith = previous_regolith + (
            (previous_ice if previous_ice > 0.0 else 0.0) - previous_regolith
        ) / tau_regolith

        if code == 2 or code == 4:
            auxiliary += (previous_ice + auxiliary_offset - auxiliary) / tau_auxiliary
        elif code == 3:
            auxiliary += (
                forcing[i - 1] + auxiliary_offset - auxiliary
            ) / tau_auxiliary

    return ice


try:  # pragma: no cover - dépend de l'environnement
    from numba import njit

    simulate_ice = njit(cache=True, fastmath=False)(_core)
    COMPILED = True
except Exception:  # pragma: no cover - repli sans numba
    simulate_ice = _core
    COMPILED = False


def pack_parameters(model: str, parameters: dict) -> np.ndarray:
    """Range un dictionnaire de paramètres dans le vecteur à neuf cases."""
    from .mpt import MODEL_SPECS

    packed = np.zeros(9)
    for index, spec in enumerate(MODEL_SPECS[model]):
        packed[index] = parameters[spec.name]
    return packed


def verify_against_reference(seed: int = 20260731, trials: int = 20) -> float:
    """Écart absolu maximal entre le noyau rapide et `simulate_mpt`.

    Vaut exactement zéro sur l'environnement de livraison : les deux
    implémentations exécutent la même suite d'opérations flottantes dans le
    même ordre. Cette égalité n'est pas garantie entre versions de numpy,
    scipy et numba, qui peuvent réordonner ou vectoriser les opérations. La
    suite de tests exige donc un écart sous 1e-11, et rapporte sa valeur.
    """
    from .mpt import MODEL_SPECS, simulate_mpt

    random = np.random.default_rng(seed)
    forcing = np.ascontiguousarray(random.normal(size=1200))
    worst = 0.0
    for _ in range(trials):
        initial = float(random.normal())
        for model in MODEL_SPECS:
            parameters = {
                spec.name: float(random.uniform(spec.lower, spec.upper))
                for spec in MODEL_SPECS[model]
            }
            fast = simulate_ice(
                MODEL_CODE[model], forcing, initial, pack_parameters(model, parameters)
            )
            slow = simulate_mpt(model, forcing, initial, parameters)["ice"]
            worst = max(worst, float(np.max(np.abs(fast - slow))))
            if model == "M2":
                fast_ablated = simulate_ice(
                    MODEL_CODE["M2_ablation"], forcing, initial,
                    pack_parameters(model, parameters),
                )
                slow_ablated = simulate_mpt(
                    model, forcing, initial, parameters, carbon_ablation=True
                )["ice"]
                worst = max(
                    worst, float(np.max(np.abs(fast_ablated - slow_ablated)))
                )
    return worst
