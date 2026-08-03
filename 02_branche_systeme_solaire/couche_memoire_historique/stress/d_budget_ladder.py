"""Campagne D — le gain de M2 dépend-il du budget d'optimisation ?

Le paquet livré ajuste les modèles avec `maxiter=30` et `popsize=6`, et son
propre `summary.json` signale que M1 et M2 atteignent la limite d'itérations.
Un avantage mesuré dans ces conditions peut refléter un ajustement incomplet du
témoin plutôt qu'une propriété du modèle testé.

On fait donc varier le seul budget d'optimisation, à bornes, graines, données
et fenêtre identiques, et on suit le gain hors échantillon de M2 sur M1 et sur
le contrôle à nombre de paramètres égal M1P.
"""

from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd

from core import OUTPUT_ROOT, fit_best_of_seeds, rmse, simulate
from a_mpt import load_dataset, standardise

OUT = OUTPUT_ROOT / "mpt"
MODELS = ("M0", "M1", "M2", "M1P")

LADDER = (
    ("livre", {"max_iterations": 30, "population_size": 6, "tol": 1e-5}),
    ("faible", {"max_iterations": 80, "population_size": 8, "tol": 1e-6}),
    ("moyen", {"max_iterations": 250, "population_size": 12, "tol": 1e-7}),
    ("eleve", {"max_iterations": 700, "population_size": 18, "tol": 1e-8}),
    ("maximal", {"max_iterations": 1500, "population_size": 26, "tol": 1e-9}),
)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    dataset, _ = load_dataset()
    observed, forcing, training_mask = standardise(dataset, 1200)
    prediction_mask = ~training_mask
    seeds = [729, 766, 803, 840]

    rows = []
    for bounds_name in ("reference", "wide"):
        for label, budget in LADDER:
            started = time.perf_counter()
            row = {"bounds": bounds_name, "budget": label,
                   "max_iterations": budget["max_iterations"],
                   "population_size": budget["population_size"]}
            for model in MODELS:
                best, runs = fit_best_of_seeds(
                    model, forcing, observed, training_mask, seeds,
                    bounds_name=bounds_name, **budget,
                )
                predicted = simulate(model, forcing, observed[0], best.vector)
                row[f"train_rmse_{model}"] = best.training_rmse
                row[f"pred_rmse_{model}"] = rmse(
                    observed[prediction_mask], predicted[prediction_mask]
                )
                row[f"converged_{model}"] = int(sum(r.converged for r in runs))
            row["gain_M2_vs_M1"] = 1.0 - row["pred_rmse_M2"] / row["pred_rmse_M1"]
            row["gain_M2_vs_M1P"] = 1.0 - row["pred_rmse_M2"] / row["pred_rmse_M1P"]
            row["gain_M2_vs_M0"] = 1.0 - row["pred_rmse_M2"] / row["pred_rmse_M0"]
            row["seconds"] = time.perf_counter() - started
            rows.append(row)
            print(f"  {bounds_name}/{label}: gain vs M1 = "
                  f"{row['gain_M2_vs_M1']:+.4f}, vs M1P = "
                  f"{row['gain_M2_vs_M1P']:+.4f} "
                  f"({row['seconds']:.0f} s)", flush=True)

    frame = pd.DataFrame(rows)
    frame.to_csv(OUT / "d_budget_ladder.csv", index=False)
    summary = {
        "seeds": seeds,
        "levels": [name for name, _ in LADDER],
        "gain_vs_M1_at_delivered_budget": float(
            frame.loc[(frame["bounds"] == "reference") & (frame["budget"] == "livre"),
                      "gain_M2_vs_M1"].iloc[0]
        ),
        "gain_vs_M1_at_maximal_budget": float(
            frame.loc[(frame["bounds"] == "wide") & (frame["budget"] == "maximal"),
                      "gain_M2_vs_M1"].iloc[0]
        ),
        "gain_vs_M1P_at_maximal_budget": float(
            frame.loc[(frame["bounds"] == "wide") & (frame["budget"] == "maximal"),
                      "gain_M2_vs_M1P"].iloc[0]
        ),
        "levels_where_gain_vs_M1_above_5pct": int(
            (frame["gain_M2_vs_M1"] >= 0.05).sum()
        ),
        "levels_where_gain_vs_M1P_above_5pct": int(
            (frame["gain_M2_vs_M1P"] >= 0.05).sum()
        ),
        "total_levels": int(len(frame)),
    }
    (OUT / "d_budget_ladder.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=float),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
