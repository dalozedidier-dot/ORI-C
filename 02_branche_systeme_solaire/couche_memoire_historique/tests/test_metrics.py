import unittest

import numpy as np

from oric_memory_tests.metrics import holm_adjust, mpt_power_ratio


class MetricTests(unittest.TestCase):
    def test_power_ratio_detects_100k_dominance(self):
        time = np.arange(0.0, 1200.0, 1.0)
        series = np.sin(2 * np.pi * time / 100.0) + 0.2 * np.sin(
            2 * np.pi * time / 41.0
        )
        self.assertGreater(mpt_power_ratio(series), 10.0)

    def test_holm_adjustment_is_monotone_in_rank(self):
        raw = [0.01, 0.04, 0.02, 0.5]
        adjusted = holm_adjust(raw)
        ordered = sorted(zip(raw, adjusted))
        values = [item[1] for item in ordered]
        self.assertEqual(values, sorted(values))
        self.assertTrue(all(0.0 <= value <= 1.0 for value in adjusted))


if __name__ == "__main__":
    unittest.main()

