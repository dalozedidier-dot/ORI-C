import unittest
from pathlib import Path

import numpy as np

from oric_memory_tests.data import (
    daily_mean_insolation,
    load_la2004,
    load_lr04,
    prepare_mpt_dataset,
)


ROOT = Path(__file__).resolve().parents[1]


class DataTests(unittest.TestCase):
    def test_lr04_source(self):
        frame = load_lr04(
            ROOT / "data" / "raw" / "lisiecki2005-d18o-stack-noaa.txt"
        )
        self.assertEqual(len(frame), 2115)
        self.assertEqual(frame.iloc[0]["age_calkaBP"], 0.0)
        self.assertGreaterEqual(frame.iloc[-1]["age_calkaBP"], 5300.0)

    def test_la2004_source(self):
        frame = load_la2004(
            ROOT / "data" / "raw" / "INSOLN.LA2004.BTL.ASC"
        )
        self.assertEqual(len(frame), 51001)
        self.assertAlmostEqual(frame.iloc[0]["time_kyr_j2000"], 0.0)
        self.assertAlmostEqual(frame.iloc[-1]["time_kyr_j2000"], -51000.0)

    def test_insolation_range(self):
        value = daily_mean_insolation(
            65.0,
            np.pi / 2.0,
            np.array([0.0167]),
            np.array([0.4091]),
            np.array([1.7963]),
        )
        self.assertGreater(value[0], 450.0)
        self.assertLess(value[0], 600.0)

    def test_common_grid(self):
        frame, quality = prepare_mpt_dataset(ROOT / "data" / "raw")
        self.assertEqual(len(frame), 2601)
        self.assertEqual(quality["null_count"], 0)
        self.assertEqual(quality["duplicate_age_count"], 0)


if __name__ == "__main__":
    unittest.main()

