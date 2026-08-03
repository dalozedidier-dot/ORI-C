"""Noyau rapide et outils communs pour la campagne de tests de stress ORI-C.

Ce module ne modifie pas le paquet original. Il fournit :

- une réimplémentation compilée (numba) de `simulate_mpt` et de
  `simulate_reduced_climate`, vérifiée contre les versions de référence ;
- un modèle de contrôle M1P qui ajoute exactement autant de paramètres que M2
  mais sans mémoire d'état ORI-C ;
- des estimateurs robustes (taille d'échantillon efficace, BIC corrigé de
  l'autocorrélation, bootstrap par blocs) ;
- un ajusteur à budget élevé avec contrôle de convergence.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numba import njit
from scipy.optimize import differential_evolution
from scipy.stats import wilcoxon

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

OUTPUT_ROOT = PROJECT_ROOT / "results_stress"


# --------------------------------------------------------------------------
# 1. Modèles MPT compilés
# --------------------------------------------------------------------------
# Encodage des modèles :
#   0 = M0   (3 paramètres)  réponse fixe
#   1 = M1   (6 paramètres)  + mémoire régolithe (état dérivé de la glace)
#   2 = M2   (9 paramètres)  = M1 + mémoire carbone (état dérivé de la glace)
#   3 = M1P  (9 paramètres)  = M1 + filtre lent du FORÇAGE (pas de mémoire d'état)
#   4 = M2A  (9 paramètres)  = M2 avec carbon_feedback_gain forcé à 0 (ablation)
#
# M1P est le contrôle décisif : il possède exactement le même nombre de degrés
# de liberté que M2 et une constante de temps lente supplémentaire, mais son
# état lent est piloté par le forçage externe et non par la réponse passée du
# système. Un gain de M2 sur M1P isole l'inscription ORI-C ; un gain de M2 sur
# M1 seulement mesure de la flexibilité.

PARAMETER_NAMES = {
    "M0": ("forcing_gain", "forcing_offset", "tau_ice_kyr"),
    "M1": (
        "forcing_gain",
        "forcing_offset",
        "tau_fast_kyr",
        "tau_memory_gain_kyr",
        "regolith_scale",
        "tau_regolith_kyr",
    ),
    "M2": (
        "forcing_gain",
        "forcing_offset",
        "tau_fast_kyr",
        "tau_memory_gain_kyr",
        "regolith_scale",
        "tau_regolith_kyr",
        "carbon_feedback_gain",
        "tau_carbon_kyr",
        "carbon_offset",
    ),
    "M1P": (
        "forcing_gain",
        "forcing_offset",
        "tau_fast_kyr",
        "tau_memory_gain_kyr",
        "regolith_scale",
        "tau_regolith_kyr",
        "slow_forcing_gain",
        "tau_slow_forcing_kyr",
        "slow_forcing_offset",
    ),
}
PARAMETER_NAMES["M2A"] = PARAMETER_NAMES["M2"]

MODEL_CODE = {"M0": 0, "M1": 1, "M2": 2, "M1P": 3, "M2A": 4}
PARAMETER_COUNT = {"M0": 3, "M1": 6, "M2": 9, "M1P": 9, "M2A": 8}

# Bornes de référence (identiques au paquet livré) et bornes élargies.
BOUNDS_REFERENCE = {
    "M0": ((-3.0, 3.0, 0), (-2.0, 2.0, 0), (3.0, 120.0, 1)),
    "M1": (
        (-3.0, 3.0, 0),
        (-2.0, 2.0, 0),
        (3.0, 60.0, 1),
        (0.1, 200.0, 1),
        (0.05, 5.0, 1),
        (200.0, 2500.0, 1),
    ),
    "M2": (
        (-3.0, 3.0, 0),
        (-2.0, 2.0, 0),
        (3.0, 60.0, 1),
        (0.1, 200.0, 1),
        (0.05, 5.0, 1),
        (200.0, 2500.0, 1),
        (-2.0, 2.0, 0),
        (200.0, 2500.0, 1),
        (-2.0, 2.0, 0),
    ),
}
BOUNDS_REFERENCE["M2A"] = BOUNDS_REFERENCE["M2"]
BOUNDS_REFERENCE["M1P"] = (
    (-3.0, 3.0, 0),
    (-2.0, 2.0, 0),
    (3.0, 60.0, 1),
    (0.1, 200.0, 1),
    (0.05, 5.0, 1),
    (200.0, 2500.0, 1),
    (-2.0, 2.0, 0),
    (200.0, 2500.0, 1),
    (-2.0, 2.0, 0),
)

# Bornes élargies : chaque borne touchée par l'ajustement livré est repoussée
# d'au moins un ordre de grandeur, afin de vérifier que l'optimum n'était pas
# artificiellement retenu par la boîte.
BOUNDS_WIDE = {
    "M0": ((-6.0, 6.0, 0), (-4.0, 4.0, 0), (1.0, 500.0, 1)),
    "M1": (
        (-6.0, 6.0, 0),
        (-4.0, 4.0, 0),
        (1.0, 200.0, 1),
        (0.01, 2000.0, 1),
        (0.001, 50.0, 1),
        (20.0, 25000.0, 1),
    ),
    "M2": (
        (-6.0, 6.0, 0),
        (-4.0, 4.0, 0),
        (1.0, 200.0, 1),
        (0.01, 2000.0, 1),
        (0.001, 50.0, 1),
        (20.0, 25000.0, 1),
        (-20.0, 20.0, 0),
        (20.0, 25000.0, 1),
        (-10.0, 10.0, 0),
    ),
}
BOUNDS_WIDE["M2A"] = BOUNDS_WIDE["M2"]
BOUNDS_WIDE["M1P"] = (
    (-6.0, 6.0, 0),
    (-4.0, 4.0, 0),
    (1.0, 200.0, 1),
    (0.01, 2000.0, 1),
    (0.001, 50.0, 1),
    (20.0, 25000.0, 1),
    (-20.0, 20.0, 0),
    (20.0, 25000.0, 1),
    (-10.0, 10.0, 0),
)

BOUNDS_SETS = {"reference": BOUNDS_REFERENCE, "wide": BOUNDS_WIDE}


@njit(cache=True, fastmath=False)
def _simulate_core(code, forcing, initial_ice, p):
    """Simulateur MPT compilé. `p` est un vecteur de 9 réels décodés."""
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
    aux_gain = p[6]
    tau_aux = p[7]
    aux_offset = p[8]

    regolith = initial_ice if initial_ice > 0.0 else 0.0
    # Etat lent supplémentaire (carbone pour M2/M2A, filtre de forçage pour M1P)
    if code == 2 or code == 4:
        aux = initial_ice + aux_offset
    elif code == 3:
        aux = forcing[0] + aux_offset
    else:
        aux = 0.0

    for i in range(1, n):
        previous_regolith = regolith if regolith > 0.0 else 0.0
        tau = tau_fast + tau_gain * (
            1.0 - math.exp(-previous_regolith / regolith_scale)
        )
        target = gain * forcing[i - 1] + offset
        if code == 2:
            target += aux_gain * aux
        elif code == 3:
            target += aux_gain * aux
        # code == 4 (M2A) : le couplage carbone est retiré, l'état continue
        # d'évoluer mais n'agit plus sur la glace.

        previous_ice = ice[i - 1]
        ice[i] = previous_ice + (target - previous_ice) / tau
        regolith = previous_regolith + (
            (previous_ice if previous_ice > 0.0 else 0.0) - previous_regolith
        ) / tau_regolith

        if code == 2 or code == 4:
            aux = aux + (previous_ice + aux_offset - aux) / tau_aux
        elif code == 3:
            aux = aux + (forcing[i - 1] + aux_offset - aux) / tau_aux

    return ice


def simulate(model: str, forcing: np.ndarray, initial_ice: float,
             values: np.ndarray) -> np.ndarray:
    """Interface haut niveau : `values` sont les paramètres déjà décodés."""
    padded = np.zeros(9)
    padded[: len(values)] = values
    return _simulate_core(
        MODEL_CODE[model], np.ascontiguousarray(forcing, dtype=float),
        float(initial_ice), padded,
    )


def decode(model: str, vector: np.ndarray, bounds_name: str = "reference") -> np.ndarray:
    spec = BOUNDS_SETS[bounds_name][model]
    out = np.empty(len(spec))
    for index, (_, _, logarithmic) in enumerate(spec):
        out[index] = math.exp(vector[index]) if logarithmic else vector[index]
    return out


def optimization_bounds(model: str, bounds_name: str = "reference") -> list:
    spec = BOUNDS_SETS[bounds_name][model]
    return [
        (math.log(lo), math.log(hi)) if logarithmic else (lo, hi)
        for lo, hi, logarithmic in spec
    ]


# --------------------------------------------------------------------------
# 2. Ajustement à budget élevé
# --------------------------------------------------------------------------

@dataclass
class FitResult:
    model: str
    parameters: dict
    vector: np.ndarray
    training_rmse: float
    converged: bool
    message: str
    iterations: int
    evaluations: int
    seed: int
    boundary_hits: list


def _objective(vector, code, forcing, observed, training_index, n_params):
    padded = np.zeros(9)
    padded[:n_params] = vector
    predicted = _simulate_core(code, forcing, observed[0], padded)
    if not np.all(np.isfinite(predicted)) or np.max(np.abs(predicted)) > 20.0:
        return 1e6
    residual = observed[training_index] - predicted[training_index]
    return float(np.sqrt(np.mean(residual * residual)))


def fit_model(
    model: str,
    forcing: np.ndarray,
    observed: np.ndarray,
    training_mask: np.ndarray,
    seed: int,
    max_iterations: int = 1500,
    population_size: int = 24,
    bounds_name: str = "reference",
    tol: float = 1e-8,
) -> FitResult:
    spec = BOUNDS_SETS[bounds_name][model]
    bounds = optimization_bounds(model, bounds_name)
    forcing = np.ascontiguousarray(forcing, dtype=float)
    observed = np.ascontiguousarray(observed, dtype=float)
    training_index = np.flatnonzero(training_mask)
    code = MODEL_CODE[model]

    def wrapped(vector):
        decoded = np.empty(len(spec))
        for index, (_, _, logarithmic) in enumerate(spec):
            decoded[index] = math.exp(vector[index]) if logarithmic else vector[index]
        return _objective(decoded, code, forcing, observed, training_index, len(spec))

    result = differential_evolution(
        wrapped,
        bounds,
        seed=seed,
        maxiter=max_iterations,
        popsize=population_size,
        tol=tol,
        polish=True,
        workers=1,
        updating="immediate",
        init="sobol",
    )
    values = decode(model, result.x, bounds_name)
    names = PARAMETER_NAMES[model]

    hits = []
    for index, (lo, hi, _) in enumerate(spec):
        tolerance = max(1e-9, 0.001 * (hi - lo))
        if abs(values[index] - lo) <= tolerance:
            hits.append(f"{names[index]}=borne_basse")
        elif abs(values[index] - hi) <= tolerance:
            hits.append(f"{names[index]}=borne_haute")

    return FitResult(
        model=model,
        parameters={name: float(value) for name, value in zip(names, values)},
        vector=values,
        training_rmse=float(result.fun),
        converged=bool(result.success),
        message=str(result.message),
        iterations=int(result.nit),
        evaluations=int(result.nfev),
        seed=int(seed),
        boundary_hits=hits,
    )


def fit_best_of_seeds(
    model: str,
    forcing: np.ndarray,
    observed: np.ndarray,
    training_mask: np.ndarray,
    seeds,
    **kwargs,
) -> tuple[FitResult, list[FitResult]]:
    runs = [
        fit_model(model, forcing, observed, training_mask, seed=seed, **kwargs)
        for seed in seeds
    ]
    best = min(runs, key=lambda item: item.training_rmse)
    return best, runs


# --------------------------------------------------------------------------
# 3. Statistiques robustes
# --------------------------------------------------------------------------

def rmse(a, b) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return float(np.sqrt(np.mean((a - b) ** 2)))


def lag1_autocorrelation(series: np.ndarray) -> float:
    series = np.asarray(series, dtype=float)
    series = series - series.mean()
    denominator = float(np.sum(series * series))
    if denominator == 0.0:
        return 0.0
    return float(np.sum(series[:-1] * series[1:]) / denominator)


def effective_sample_size(residuals: np.ndarray) -> float:
    """n_eff pour un résidu AR(1) : n * (1 - rho) / (1 + rho)."""
    rho = lag1_autocorrelation(residuals)
    rho = min(max(rho, -0.999), 0.999)
    n = len(residuals)
    return float(n * (1.0 - rho) / (1.0 + rho))


def information_criteria(residuals: np.ndarray, parameter_count: int,
                         sample_size: float | None = None) -> dict:
    residuals = np.asarray(residuals, dtype=float)
    n_actual = len(residuals)
    n = float(n_actual if sample_size is None else sample_size)
    rss = float(np.sum(residuals ** 2))
    variance = max(rss / n_actual, np.finfo(float).tiny)
    aic = n * math.log(variance) + 2 * parameter_count
    bic = n * math.log(variance) + parameter_count * math.log(max(n, 2.0))
    return {"aic": float(aic), "bic": float(bic), "sample_size_used": n}


def moving_block_bootstrap_gain(
    observed: np.ndarray,
    reference: np.ndarray,
    candidate: np.ndarray,
    block_length: int,
    draws: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Distribution bootstrap du gain relatif de RMSE (référence -> candidat).

    Les résidus sont fortement autocorrélés : le rééchantillonnage se fait par
    blocs mobiles pour préserver cette structure.
    """
    error_reference = (observed - reference) ** 2
    error_candidate = (observed - candidate) ** 2
    n = len(observed)
    block_count = int(np.ceil(n / block_length))
    starts_max = n - block_length
    gains = np.empty(draws)
    for draw in range(draws):
        starts = rng.integers(0, starts_max + 1, size=block_count)
        index = np.concatenate([
            np.arange(start, start + block_length) for start in starts
        ])[:n]
        mse_reference = error_reference[index].mean()
        mse_candidate = error_candidate[index].mean()
        gains[draw] = 1.0 - math.sqrt(mse_candidate) / math.sqrt(mse_reference)
    return gains


def fourier_surrogate(series: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Surrogate à phases aléatoires : même spectre de puissance, structure
    temporelle détruite."""
    series = np.asarray(series, dtype=float)
    n = len(series)
    spectrum = np.fft.rfft(series - series.mean())
    phases = rng.uniform(0.0, 2.0 * math.pi, size=len(spectrum))
    phases[0] = 0.0
    if n % 2 == 0:
        phases[-1] = 0.0
    surrogate = np.fft.irfft(np.abs(spectrum) * np.exp(1j * phases), n=n)
    surrogate = surrogate / surrogate.std() * series.std() + series.mean()
    return surrogate


def paired_wilcoxon_greater(first: np.ndarray, second: np.ndarray) -> float:
    difference = np.asarray(first) - np.asarray(second)
    if np.allclose(difference, 0.0):
        return 1.0
    return float(wilcoxon(difference, alternative="greater").pvalue)


# --------------------------------------------------------------------------
# 4. EMIC exoplanétaire compilé
# --------------------------------------------------------------------------
# Ordre des paramètres du vecteur compilé (identique à DEFAULT_PARAMETERS)
EXO_PARAMETER_ORDER = (
    "tau_temperature_myr",
    "tau_ice_myr",
    "tau_co2_myr",
    "global_forcing_gain",
    "co2_temperature_gain",
    "ice_albedo_gain",
    "polar_forcing_gain",
    "ice_threshold",
    "ice_transition_width",
    "bedrock_ice_gain",
    "bedrock_tau_gain",
    "regolith_erosion_rate",
    "tau_regolith_recovery_myr",
    "carbon_sequestration_gain",
    "tau_carbon_memory_myr",
    "weathering_temperature_gain",
)

EXO_MODE_CODE = {"classic": 0, "ablated": 1, "M2": 2}


@njit(cache=True, fastmath=False)
def _exo_core(polar_anomaly, annual_flux_anomaly, mode, initial_state,
              p, step, substep_count):
    n = polar_anomaly.shape[0]
    internal_step = step / substep_count
    temperature = initial_state[0]
    ice = initial_state[1]
    co2 = initial_state[2]
    regolith = initial_state[3]
    carbon_memory = initial_state[4]

    output = np.empty((n, 6))
    productivity = 0.0

    for index in range(n):
        for _ in range(substep_count):
            co2_clamped = co2 if co2 > 50.0 else 50.0
            productivity = (
                math.exp(-((temperature - 0.5) / 4.0) ** 2)
                * (co2_clamped / 280.0) ** 0.2
                * (1.0 - 0.45 * ice)
            )

            if mode == 2:
                bedrock = 1.0 - regolith
                carbon_effect = carbon_memory - 0.5
            elif mode == 1:
                bedrock = 0.5
                carbon_effect = 0.0
                regolith = 0.5
                carbon_memory = 0.5
            else:
                bedrock = 0.0
                carbon_effect = 0.0

            temperature_target = (
                p[3] * annual_flux_anomaly[index]
                + p[4] * math.log(co2_clamped / 280.0)
                - p[5] * ice
            )
            ice_argument = -(
                temperature + p[6] * polar_anomaly[index] - p[7] - p[9] * bedrock
            ) / p[8]
            if ice_argument > 30.0:
                ice_argument = 30.0
            elif ice_argument < -30.0:
                ice_argument = -30.0
            ice_target = 1.0 / (1.0 + math.exp(-ice_argument))
            co2_target = 280.0 * math.exp(
                -p[15] * temperature - p[13] * carbon_effect
            )
            effective_tau_ice = p[1] * (1.0 + p[10] * bedrock)

            temperature += internal_step * (temperature_target - temperature) / p[0]
            ice = ice + internal_step * (ice_target - ice) / effective_tau_ice
            if ice < 0.0:
                ice = 0.0
            elif ice > 1.0:
                ice = 1.0
            co2 = co2 + internal_step * (co2_target - co2) / p[2]
            if co2 < 80.0:
                co2 = 80.0
            elif co2 > 1200.0:
                co2 = 1200.0

            if mode == 2:
                regolith += internal_step * (
                    -p[11] * ice * regolith + (1.0 - regolith) / p[12]
                )
                carbon_memory += internal_step * (productivity - carbon_memory) / p[14]
                if regolith < 0.0:
                    regolith = 0.0
                elif regolith > 1.0:
                    regolith = 1.0
                if carbon_memory < 0.0:
                    carbon_memory = 0.0
                elif carbon_memory > 2.0:
                    carbon_memory = 2.0

        output[index, 0] = temperature
        output[index, 1] = ice
        output[index, 2] = co2
        output[index, 3] = regolith
        output[index, 4] = carbon_memory
        output[index, 5] = productivity
    return output


def exo_parameter_vector(overrides: dict | None = None) -> np.ndarray:
    from oric_memory_tests.exoplanet import DEFAULT_PARAMETERS

    merged = {**DEFAULT_PARAMETERS, **(overrides or {})}
    return np.array([merged[name] for name in EXO_PARAMETER_ORDER], dtype=float)


def polar_summer_insolation(obliquity_deg, eccentricity, latitude_deg=65.0,
                            varpi_deg=102.9, solar_constant=1365.0):
    obliquity = np.deg2rad(obliquity_deg)
    eccentricity = np.asarray(eccentricity, dtype=float)
    latitude = np.deg2rad(latitude_deg)
    varpi = np.deg2rad(varpi_deg)
    solar_longitude = np.pi / 2.0
    sunset = np.arccos(np.clip(-np.tan(latitude) * np.tan(obliquity), -1.0, 1.0))
    distance = (
        (1.0 + eccentricity * np.cos(solar_longitude - varpi)) ** 2
        / (1.0 - eccentricity ** 2) ** 2
    )
    geometry = (
        sunset * np.sin(latitude) * np.sin(obliquity)
        + np.cos(latitude) * np.cos(obliquity) * np.sin(sunset)
    )
    return solar_constant / np.pi * distance * geometry


def simulate_exo(time_myr, obliquity_deg, eccentricity, mode, initial_state,
                 parameters: np.ndarray) -> np.ndarray:
    time = np.asarray(time_myr, dtype=float)
    step = float(np.median(np.diff(time)))
    substep_count = max(1, int(np.ceil(step / 0.02)))
    polar = polar_summer_insolation(obliquity_deg, eccentricity)
    polar_reference = float(polar_summer_insolation(23.5, 0.05))
    polar_anomaly = np.ascontiguousarray((polar - polar_reference) / 100.0)
    annual_flux_anomaly = np.ascontiguousarray(
        (1.0 / np.sqrt(1.0 - np.asarray(eccentricity, dtype=float) ** 2)
         - 1.0 / np.sqrt(1.0 - 0.05 ** 2)) / 0.05
    )
    return _exo_core(
        polar_anomaly, annual_flux_anomaly, EXO_MODE_CODE[mode],
        np.ascontiguousarray(initial_state, dtype=float),
        np.ascontiguousarray(parameters, dtype=float), step, substep_count,
    )


def controlled_histories(step_myr=0.02, spinup_myr=10.0, history_myr=50.0,
                         final_hold_myr=10.0):
    """Version paramétrable de `generate_controlled_histories`.

    Seule la durée du palier final est ouverte, afin de tester la relaxation.
    """
    from oric_memory_tests.exoplanet import _smoothstep

    time = np.arange(
        -spinup_myr, history_myr + final_hold_myr + step_myr / 2.0, step_myr
    )
    progress = np.clip(time / history_myr, 0.0, 1.0)
    remaining = 1.0 - _smoothstep(progress)
    excursion = 4.0 * progress * (1.0 - progress)

    obliquity_a = 23.5 + (70.0 - 23.5) * remaining
    eccentricity_a = 0.05 + (0.30 - 0.05) * remaining
    obliquity_b = 23.5 + (10.0 - 23.5) * remaining + (30.0 - 16.75) * excursion
    eccentricity_b = 0.05 + (0.01 - 0.05) * remaining + (0.10 - 0.03) * excursion

    before = time < 0.0
    after = time >= history_myr
    obliquity_a[before], eccentricity_a[before] = 70.0, 0.30
    obliquity_b[before], eccentricity_b[before] = 10.0, 0.01
    obliquity_a[after], eccentricity_a[after] = 23.5, 0.05
    obliquity_b[after], eccentricity_b[after] = 23.5, 0.05

    return {
        "time_myr": time,
        "obliquity_A_deg": obliquity_a,
        "eccentricity_A": eccentricity_a,
        "obliquity_B_deg": obliquity_b,
        "eccentricity_B": eccentricity_b,
    }


def exo_initial_states(seed: int, count: int) -> np.ndarray:
    random = np.random.default_rng(seed)
    states = np.empty((count, 5))
    for index in range(count):
        states[index] = (
            random.normal(0.0, 0.2),
            np.clip(random.normal(0.2, 0.05), 0.0, 1.0),
            random.normal(300.0, 15.0),
            random.uniform(0.6, 1.0),
            random.uniform(0.1, 0.6),
        )
    return states


# --------------------------------------------------------------------------
# 5. Rapport spectral rapide (identique à `mpt_power_ratio` à 1e-15 près)
# --------------------------------------------------------------------------

class PowerRatio:
    """Rapport de puissance 80–120 ka / 39–43 ka avec masques précalculés."""

    def __init__(self, length: int, step: float = 1.0):
        self.length = length
        self.frequency = np.fft.rfftfreq(length, d=step)
        positive = self.frequency > 0
        period = np.divide(
            1.0, self.frequency,
            out=np.full_like(self.frequency, np.inf), where=positive,
        )
        self.mask_100 = (period >= 80.0) & (period <= 120.0)
        self.mask_41 = (period >= 39.0) & (period <= 43.0)
        self.double_slice = slice(1, -1 if length % 2 == 0 else None)

    def __call__(self, series: np.ndarray) -> float:
        from scipy.signal import detrend

        centred = detrend(series - series.mean(), type="linear")
        spectrum = np.abs(np.fft.rfft(centred)) ** 2 / self.length
        spectrum[self.double_slice] *= 2.0
        numerator = np.trapezoid(
            spectrum[self.mask_100], self.frequency[self.mask_100]
        )
        denominator = np.trapezoid(
            spectrum[self.mask_41], self.frequency[self.mask_41]
        )
        return float(numerator / max(denominator, np.finfo(float).tiny))
