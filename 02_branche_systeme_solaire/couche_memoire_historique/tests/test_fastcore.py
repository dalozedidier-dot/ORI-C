"""Le noyau d'optimisation doit rester le modèle de référence, à la
tolérance numérique près définie ci-dessous."""

from __future__ import annotations

import unittest

import numpy as np

from oric_memory_tests.fastcore import (
    MODEL_CODE,
    pack_parameters,
    simulate_ice,
    verify_against_reference,
)
from oric_memory_tests.metrics import (
    effective_sample_size,
    lag1_autocorrelation,
    information_criteria,
    moving_block_bootstrap_gain,
)
from oric_memory_tests.mpt import MODEL_SPECS, simulate_mpt

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




class FastCoreTests(unittest.TestCase):
    def test_identical_to_reference(self):
        """Le noyau compilé doit rester le modèle de référence.

        L'écart est rapporté, pas seulement testé : sur l'environnement de
        livraison il vaut exactement 0,0. Une valeur non nulle mais sous la
        tolérance signale un simple réordonnancement flottant ; au-dessus,
        c'est une divergence algorithmique.
        """
        ecart = verify_against_reference()
        self.assertLess(
            ecart, TOLERANCE_ABSOLUE,
            f"écart au modèle de référence : {ecart:.3e}",
        )

    def test_control_model_reduces_to_M1_without_slow_coupling(self):
        """M1P privé de son couplage lent doit redevenir exactement M1.

        C'est ce qui garantit que M1P est bien M1 plus trois paramètres, et non
        un modèle différent.
        """
        random = np.random.default_rng(4)
        forcing = np.ascontiguousarray(random.normal(size=500))
        parameters = {
            spec.name: float(random.uniform(spec.lower, spec.upper))
            for spec in MODEL_SPECS["M1P"]
        }
        parameters["slow_forcing_gain"] = 0.0
        control = simulate_mpt("M1P", forcing, 0.25, parameters)["ice"]
        base = simulate_mpt(
            "M1", forcing, 0.25,
            {spec.name: parameters[spec.name] for spec in MODEL_SPECS["M1"]},
        )["ice"]
        np.testing.assert_allclose(
            control, base, rtol=TOLERANCE_RELATIVE, atol=TOLERANCE_ABSOLUE
        )

    def test_la_tolerance_detecte_une_divergence_algorithmique(self):
        """La tolérance doit discriminer, pas tout laisser passer.

        Une perturbation relative de 1e-9 sur une constante de temps représente
        une divergence algorithmique et non du bruit d'arrondi. Elle doit être
        détectée. Ce test documente le chiffre cité dans `VALIDATION.md`.
        """
        random = np.random.default_rng(3)
        forcing = np.ascontiguousarray(random.normal(size=1200))
        parameters = {
            spec.name: float(random.uniform(spec.lower, spec.upper))
            for spec in MODEL_SPECS["M2"]
        }
        reference = simulate_mpt("M2", forcing, 0.2, parameters)["ice"]

        perturbes = dict(parameters)
        perturbes["tau_fast_kyr"] = parameters["tau_fast_kyr"] * (1 + 1e-9)
        perturbe = simulate_mpt("M2", forcing, 0.2, perturbes)["ice"]

        ecart = float(np.max(np.abs(reference - perturbe)))
        self.assertGreater(
            ecart, TOLERANCE_ABSOLUE,
            f"une divergence de 1e-9 produit {ecart:.3e}, non détectée",
        )
        with self.assertRaises(AssertionError):
            np.testing.assert_allclose(
                reference, perturbe,
                rtol=TOLERANCE_RELATIVE, atol=TOLERANCE_ABSOLUE,
            )

    def test_control_model_has_same_parameter_count_as_M2(self):
        self.assertEqual(len(MODEL_SPECS["M1P"]), len(MODEL_SPECS["M2"]))

    def test_control_slow_state_ignores_the_response(self):
        """L'état lent de M1P ne doit dépendre que du forçage.

        Changer la condition initiale de glace déplace la trajectoire de M2 par
        son canal carbone. Pour M1P, l'état lent lui-même doit rester le même.
        """
        random = np.random.default_rng(5)
        forcing = np.ascontiguousarray(random.normal(size=400))
        parameters = {
            spec.name: float(random.uniform(spec.lower, spec.upper))
            for spec in MODEL_SPECS["M1P"]
        }
        first = simulate_mpt("M1P", forcing, 0.1, parameters)["slow_forcing"]
        second = simulate_mpt("M1P", forcing, 0.9, parameters)["slow_forcing"]
        np.testing.assert_allclose(
            first, second, rtol=TOLERANCE_RELATIVE, atol=TOLERANCE_ABSOLUE
        )

        carbon_parameters = {
            spec.name: float(random.uniform(spec.lower, spec.upper))
            for spec in MODEL_SPECS["M2"]
        }
        carbon_first = simulate_mpt("M2", forcing, 0.1, carbon_parameters)["carbon"]
        carbon_second = simulate_mpt("M2", forcing, 0.9, carbon_parameters)["carbon"]
        self.assertGreater(float(np.max(np.abs(carbon_first - carbon_second))), 1e-6)

    def test_slow_state_offset_symmetry_is_removed(self):
        """Le décalage de l'état lent ne doit plus être un paramètre libre.

        Laisser `carbon_offset` libre crée une symétrie exacte avec
        `forcing_offset` : la trajectoire de glace est invariante, mais
        l'ablation carbone ne l'est pas. Le test vérifie d'abord que la symétrie
        existe bien dans le simulateur, puis qu'elle n'est plus atteignable par
        l'ajustement.
        """
        random = np.random.default_rng(11)
        forcing = np.ascontiguousarray(random.normal(size=600))
        parameters = {
            spec.name: float(random.uniform(spec.lower, spec.upper))
            for spec in MODEL_SPECS["M2"]
        }
        parameters["carbon_feedback_gain"] = -7.5
        parameters["carbon_offset"] = 0.0

        shift = 0.37
        shifted = dict(parameters)
        shifted["carbon_offset"] = shift
        shifted["forcing_offset"] = (
            parameters["forcing_offset"]
            - parameters["carbon_feedback_gain"] * shift
        )

        base = simulate_mpt("M2", forcing, 0.15, parameters)["ice"]
        moved = simulate_mpt("M2", forcing, 0.15, shifted)["ice"]
        self.assertLess(float(np.max(np.abs(base - moved))), 1e-12)

        ablated_base = simulate_mpt(
            "M2", forcing, 0.15, parameters, carbon_ablation=True
        )["ice"]
        ablated_moved = simulate_mpt(
            "M2", forcing, 0.15, shifted, carbon_ablation=True
        )["ice"]
        self.assertGreater(
            float(np.max(np.abs(ablated_base - ablated_moved))), 1.0
        )

        names = [spec.name for spec in MODEL_SPECS["M2"]]
        self.assertNotIn("carbon_offset", names)
        self.assertNotIn(
            "slow_forcing_offset", [spec.name for spec in MODEL_SPECS["M1P"]]
        )

    def test_packed_vector_follows_the_specification_order(self):
        parameters = {spec.name: float(index)
                      for index, spec in enumerate(MODEL_SPECS["M2"])}
        packed = pack_parameters("M2", parameters)
        count = len(MODEL_SPECS["M2"])
        np.testing.assert_array_equal(packed[:count], np.arange(float(count)))
        np.testing.assert_array_equal(packed[count:], np.zeros(9 - count))
        self.assertEqual(MODEL_CODE["M2"], 2)
        self.assertEqual(
            simulate_ice(0, np.zeros(3), 0.0, np.array([0.0, 0.0, 1.0])).shape, (3,)
        )


class AutocorrelationTests(unittest.TestCase):
    def test_effective_sample_size_collapses_for_correlated_residuals(self):
        random = np.random.default_rng(6)
        n = 20000
        series = np.empty(n)
        series[0] = 0.0
        for index in range(1, n):
            series[index] = 0.95 * series[index - 1] + random.normal()
        self.assertAlmostEqual(lag1_autocorrelation(series), 0.95, places=1)
        self.assertLess(effective_sample_size(series), 0.05 * n)
        self.assertGreater(
            effective_sample_size(random.normal(size=n)), 0.9 * n
        )

    def test_bic_penalty_shrinks_with_effective_sample_size(self):
        residuals = np.random.default_rng(7).normal(size=1200)
        naive = information_criteria(residuals, 9)
        corrected = information_criteria(residuals, 9, sample_size=18.0)
        self.assertEqual(naive["sample_size_used"], 1200.0)
        self.assertEqual(corrected["sample_size_used"], 18.0)
        # Trois paramètres de plus coûtent bien davantage à n_eff qu'à n brut.
        naive_cost = (
            information_criteria(residuals, 9)["bic"]
            - information_criteria(residuals, 6)["bic"]
        )
        corrected_cost = (
            information_criteria(residuals, 9, 18.0)["bic"]
            - information_criteria(residuals, 6, 18.0)["bic"]
        )
        self.assertLess(corrected_cost, naive_cost)

    def test_block_bootstrap_is_reproducible_and_bounded(self):
        random = np.random.default_rng(8)
        observed = np.cumsum(random.normal(size=600))
        reference = observed + random.normal(scale=1.0, size=600)
        candidate = observed + random.normal(scale=0.5, size=600)
        first = moving_block_bootstrap_gain(
            observed, reference, candidate, block_length=40, draws=200, seed=3
        )
        second = moving_block_bootstrap_gain(
            observed, reference, candidate, block_length=40, draws=200, seed=3
        )
        np.testing.assert_array_equal(first, second)
        self.assertTrue(np.all(first < 1.0))
        self.assertGreater(float(np.median(first)), 0.0)


if __name__ == "__main__":
    unittest.main()
