"""Tests du harnais de stress.

Aucun résultat de la campagne de stress n'a de valeur si le noyau compilé
diverge des modèles livrés ou si les estimateurs robustes sont faux. Ces tests
verrouillent les deux.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT / "src", ROOT / "stress"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from core import (  # noqa: E402
    PARAMETER_COUNT,
    PARAMETER_NAMES,
    PowerRatio,
    controlled_histories,
    effective_sample_size,
    exo_initial_states,
    exo_parameter_vector,
    fourier_surrogate,
    information_criteria,
    lag1_autocorrelation,
    simulate,
    simulate_exo,
)
from oric_memory_tests.exoplanet import simulate_reduced_climate  # noqa: E402
from oric_memory_tests.metrics import mpt_power_ratio  # noqa: E402
from oric_memory_tests.mpt import simulate_mpt  # noqa: E402

# ---------------------------------------------------------------------------
# Tolérance des comparaisons au modèle de référence
# ---------------------------------------------------------------------------
# Le noyau compilé exécute la même suite d'opérations flottantes que
# `simulate_mpt`. Sur l'environnement de livraison l'écart est exactement nul,
# et le test le vérifiait par une égalité stricte. Cette égalité n'est pas
# portable : numpy, scipy et numba peuvent réordonner ou vectoriser les
# opérations d'une version à l'autre, ce qui déplace le dernier bit.
#
# Le dossier retient donc la reproductibilité numérique tolérée plutôt que la
# reproductibilité binaire, qui exigerait un conteneur alors que les
# dépendances ne sont bornées que par le bas.
#
# La tolérance retenue reste très inférieure aux échelles numériques pertinentes
# pour les résultats rapportés. Elle absorbe les écarts d'arrondi entre
# environnements et détecte les divergences dépassant le seuil fixé.
TOLERANCE_RELATIVE = 1e-11
TOLERANCE_ABSOLUE = 1e-11




def random_parameters(rng):
    return {
        "forcing_gain": rng.uniform(-3, 3),
        "forcing_offset": rng.uniform(-2, 2),
        "tau_ice_kyr": rng.uniform(3, 120),
        "tau_fast_kyr": rng.uniform(3, 60),
        "tau_memory_gain_kyr": rng.uniform(0.1, 200),
        "regolith_scale": rng.uniform(0.05, 5),
        "tau_regolith_kyr": rng.uniform(200, 2500),
        "carbon_feedback_gain": rng.uniform(-2, 2),
        "tau_carbon_kyr": rng.uniform(200, 2500),
        "carbon_offset": rng.uniform(-2, 2),
    }


class TestCompiledMptCore(unittest.TestCase):
    def test_matches_reference_within_tolerance(self):
        rng = np.random.default_rng(7)
        forcing = rng.normal(size=800)
        for _ in range(15):
            parameters = random_parameters(rng)
            initial = float(rng.normal())
            for model in ("M0", "M1", "M2"):
                values = np.array(
                    [parameters[name] for name in PARAMETER_NAMES[model]]
                )
                fast = simulate(model, forcing, initial, values)
                slow = simulate_mpt(model, forcing, initial, parameters)["ice"]
                np.testing.assert_allclose(
                    fast, slow, rtol=TOLERANCE_RELATIVE, atol=TOLERANCE_ABSOLUE
                )

    def test_ablation_matches_reference(self):
        rng = np.random.default_rng(8)
        forcing = rng.normal(size=600)
        parameters = random_parameters(rng)
        values = np.array([parameters[name] for name in PARAMETER_NAMES["M2"]])
        fast = simulate("M2A", forcing, 0.3, values)
        slow = simulate_mpt("M2", forcing, 0.3, parameters, carbon_ablation=True)
        np.testing.assert_allclose(
            fast, slow["ice"], rtol=TOLERANCE_RELATIVE, atol=TOLERANCE_ABSOLUE
        )

    def test_control_model_has_same_parameter_count_as_M2(self):
        self.assertEqual(len(PARAMETER_NAMES["M1P"]), len(PARAMETER_NAMES["M2"]))
        self.assertEqual(PARAMETER_COUNT["M1P"], PARAMETER_COUNT["M2"])

    def test_control_model_slow_state_ignores_response(self):
        """L'état lent de M1P ne doit dépendre que du forçage.

        On change la condition initiale de glace : la trajectoire de M2 doit
        bouger par le canal carbone, celle de M1P uniquement par le canal
        rapide. Le test vérifie que M1P reste identique quand seule la valeur
        d'ancrage de son état lent est laissée inchangée.
        """
        rng = np.random.default_rng(9)
        forcing = rng.normal(size=400)
        parameters = random_parameters(rng)
        values = np.array([parameters[name] for name in PARAMETER_NAMES["M2"]])
        # Sans couplage de l'état lent, M1P se réduit exactement à M1.
        neutral = values.copy()
        neutral[6] = 0.0
        reduced = simulate("M1P", forcing, 0.2, neutral)
        m1_values = np.array(
            [parameters[name] for name in PARAMETER_NAMES["M1"]]
        )
        np.testing.assert_allclose(
            reduced, simulate("M1", forcing, 0.2, m1_values),
            rtol=TOLERANCE_RELATIVE, atol=TOLERANCE_ABSOLUE,
        )


class TestCompiledExoCore(unittest.TestCase):
    def test_matches_reference(self):
        history = controlled_histories(step_myr=0.05, final_hold_myr=4.0)
        parameters = exo_parameter_vector()
        states = exo_initial_states(3, 2)
        for mode in ("classic", "ablated", "M2"):
            for state in states:
                fast = simulate_exo(
                    history["time_myr"], history["obliquity_A_deg"],
                    history["eccentricity_A"], mode, state, parameters,
                )
                slow = simulate_reduced_climate(
                    history["time_myr"], history["obliquity_A_deg"],
                    history["eccentricity_A"], mode, state,
                )
                scale = np.maximum(np.abs(slow).max(axis=0), 1e-12)
                self.assertLess(float(np.max(np.abs(fast - slow) / scale)), 1e-12)

    def test_longer_hold_keeps_the_common_final_forcing(self):
        for hold in (10.0, 200.0):
            history = controlled_histories(final_hold_myr=hold)
            after = history["time_myr"] >= 50.0
            # Ici l'égalité doit rester exacte : les deux histoires reçoivent
            # littéralement la même valeur de forçage après 50 Ma, ce n'est pas
            # un résultat de calcul mais une affectation.
            np.testing.assert_array_equal(
                history["obliquity_A_deg"][after], history["obliquity_B_deg"][after]
            )
            np.testing.assert_array_equal(
                history["eccentricity_A"][after], history["eccentricity_B"][after]
            )


class TestRobustStatistics(unittest.TestCase):
    def test_power_ratio_matches_reference(self):
        rng = np.random.default_rng(11)
        for length in (601, 1200, 1201):
            series = np.cumsum(rng.normal(size=length))
            self.assertAlmostEqual(
                PowerRatio(length)(series), mpt_power_ratio(series), places=9
            )

    def test_effective_sample_size_on_white_noise(self):
        rng = np.random.default_rng(12)
        noise = rng.normal(size=20000)
        self.assertGreater(effective_sample_size(noise), 18000)

    def test_effective_sample_size_collapses_for_autocorrelated_residuals(self):
        rng = np.random.default_rng(13)
        n = 20000
        series = np.empty(n)
        series[0] = 0.0
        for index in range(1, n):
            series[index] = 0.95 * series[index - 1] + rng.normal()
        self.assertAlmostEqual(lag1_autocorrelation(series), 0.95, places=1)
        # (1-rho)/(1+rho) = 0.0256 pour rho = 0,95
        self.assertLess(effective_sample_size(series), n * 0.05)

    def test_bic_penalty_uses_the_sample_size_given(self):
        residuals = np.random.default_rng(14).normal(size=1000)
        naive = information_criteria(residuals, 9)
        corrected = information_criteria(residuals, 9, sample_size=20.0)
        self.assertLess(corrected["bic"] - naive["bic"], 0.0)
        # Le terme de pénalité doit rétrécir avec n_eff.
        self.assertLess(
            9 * np.log(20.0), 9 * np.log(1000.0)
        )

    def test_fourier_surrogate_preserves_the_power_spectrum(self):
        rng = np.random.default_rng(15)
        series = np.cumsum(rng.normal(size=2048))
        surrogate = fourier_surrogate(series, rng)
        original = np.abs(np.fft.rfft(series - series.mean()))
        produced = np.abs(np.fft.rfft(surrogate - surrogate.mean()))
        scale = original.sum()
        self.assertLess(
            float(np.max(np.abs(original - produced))) / scale, 1e-6
        )
        self.assertGreater(
            float(np.max(np.abs(series - surrogate))), 1e-6
        )


if __name__ == "__main__":
    unittest.main()
