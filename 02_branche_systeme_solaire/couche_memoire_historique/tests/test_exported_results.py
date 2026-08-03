import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from oric_memory_tests.metrics import mpt_power_ratio


ROOT = Path(__file__).resolve().parents[1]


class ExportedResultTests(unittest.TestCase):
    def test_mpt_metrics_recompute_from_predictions(self):
        predictions = pd.read_csv(ROOT / "results" / "mpt" / "predictions.csv")
        metrics = pd.read_csv(ROOT / "results" / "mpt" / "metrics.csv")
        selected = predictions["age_kyr_bp"] < 1200
        observed = predictions.loc[selected, "observed_standardized"].to_numpy()
        for model in ("M0", "M1", "M2", "M2_ablation"):
            predicted = predictions.loc[selected, model].to_numpy()
            exported = metrics.loc[
                (metrics["interval"] == "prediction")
                & (metrics["model"] == model)
            ].iloc[0]
            calculated_rmse = np.sqrt(np.mean((observed - predicted) ** 2))
            self.assertAlmostEqual(
                calculated_rmse, exported["rmse_standardized"], places=12
            )
            self.assertAlmostEqual(
                mpt_power_ratio(predicted),
                exported["power_ratio_100k_to_41k"],
                places=12,
            )

    def test_exoplanet_deltas_recompute_from_final_states(self):
        states = pd.read_csv(
            ROOT / "results" / "exoplanet" / "ensemble_final_states.csv"
        )
        exported = pd.read_csv(
            ROOT / "results" / "exoplanet" / "path_deltas.csv"
        )
        wide = states.pivot_table(
            index=["model", "replicate", "variable"],
            columns="trajectory",
            values="final_mean",
        )
        calculated = (
            (wide["A"] - wide["B"])
            .abs()
            .rename("calculated_delta")
            .reset_index()
        )
        merged = exported.merge(
            calculated, on=["model", "replicate", "variable"]
        )
        np.testing.assert_allclose(
            merged["absolute_delta_A_B"],
            merged["calculated_delta"],
            atol=1e-12,
            rtol=0.0,
        )


if __name__ == "__main__":
    unittest.main()

