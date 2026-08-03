import unittest

import numpy as np

from oric_memory_tests.exoplanet import (
    generate_controlled_histories,
    simulate_reduced_climate,
)
from oric_memory_tests.mpt import simulate_mpt


class ModelTests(unittest.TestCase):
    def test_m0_converges_under_constant_forcing(self):
        forcing = np.ones(500)
        result = simulate_mpt(
            "M0",
            forcing,
            0.0,
            {
                "forcing_gain": 1.0,
                "forcing_offset": 0.0,
                "tau_ice_kyr": 20.0,
            },
        )
        self.assertAlmostEqual(result["ice"][-1], 1.0, places=6)

    def test_controlled_histories_share_exact_final_boundary(self):
        forcing = generate_controlled_histories(step_myr=0.1)
        final = forcing["time_myr"] >= 50.0
        self.assertTrue(
            np.array_equal(
                forcing.loc[final, "obliquity_A_deg"],
                forcing.loc[final, "obliquity_B_deg"],
            )
        )
        self.assertTrue(
            np.array_equal(
                forcing.loc[final, "eccentricity_A"],
                forcing.loc[final, "eccentricity_B"],
            )
        )

    def test_identical_forcing_produces_identical_classical_climate(self):
        time = np.arange(0.0, 2.01, 0.02)
        obliquity = np.full_like(time, 23.5)
        eccentricity = np.full_like(time, 0.05)
        initial = np.array([0.0, 0.2, 300.0, 0.8, 0.3])
        first = simulate_reduced_climate(
            time, obliquity, eccentricity, "classic", initial
        )
        second = simulate_reduced_climate(
            time, obliquity, eccentricity, "classic", initial
        )
        np.testing.assert_allclose(first, second, atol=0.0, rtol=0.0)


if __name__ == "__main__":
    unittest.main()

