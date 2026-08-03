"""Verdict durci : les cinq critères MPT préenregistrés, recalculés.

Rien n'est ajouté aux critères et aucun seuil n'est modifié. Trois choses
seulement changent par rapport au paquet livré :

  1. l'optimiseur reçoit un budget suffisant pour converger, avec douze graines
     indépendantes et des bornes assez larges pour ne pas retenir l'optimum ;
  2. le BIC est calculé sur la taille d'échantillon efficace, car les résidus
     sur une grille de 1 ka ont une autocorrélation de rang 1 supérieure à
     0,97 ; le compte naïf est conservé à côté ;
  3. le témoin est doublé : le critère est évalué contre M1 comme dans le
     protocole, et contre M1P, qui possède exactement le même nombre de
     paramètres que M2 mais aucune mémoire d'état.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from a_mpt import fit_all, load_dataset, standardise, BUDGET_HIGH
from core import (
    OUTPUT_ROOT,
    PARAMETER_COUNT,
    effective_sample_size,
    information_criteria,
    lag1_autocorrelation,
    paired_wilcoxon_greater,
    rmse,
    simulate,
)
from oric_memory_tests.metrics import (
    contiguous_block_scores,
    correlation,
    event_timing_mae,
    log_ratio_error,
    mpt_power_ratio,
    termination_events,
)

OUT = OUTPUT_ROOT / "mpt"
MODELS = ("M0", "M1", "M2", "M1P")


def criteria_for(reference, observed, predictions, prediction_mask, elapsed):
    o = observed[prediction_mask]
    target_ratio = mpt_power_ratio(o)
    m2 = predictions["M2"][prediction_mask]
    ref = predictions[reference][prediction_mask]

    ratio_m2 = mpt_power_ratio(m2)
    ratio_ref = mpt_power_ratio(ref)
    residual_m2 = o - m2
    residual_ref = o - ref
    n_eff_m2 = effective_sample_size(residual_m2)
    n_eff_ref = effective_sample_size(residual_ref)

    bic_naive = (
        information_criteria(residual_m2, PARAMETER_COUNT["M2"])["bic"]
        - information_criteria(residual_ref, PARAMETER_COUNT[reference])["bic"]
    )
    bic_effective = (
        information_criteria(residual_m2, PARAMETER_COUNT["M2"], n_eff_m2)["bic"]
        - information_criteria(residual_ref, PARAMETER_COUNT[reference], n_eff_ref)["bic"]
    )

    gain = 1.0 - rmse(o, m2) / rmse(o, ref)
    correlation_m2 = correlation(o, m2)
    timing = event_timing_mae(
        termination_events(o, elapsed[prediction_mask]),
        termination_events(m2, elapsed[prediction_mask]),
    )
    blocks = pd.DataFrame(contiguous_block_scores(
        o, {reference: ref, "M2": m2}, block_size=50
    ))
    p_block = paired_wilcoxon_greater(
        blocks[f"rmse_{reference}"].to_numpy(), blocks["rmse_M2"].to_numpy()
    )

    return [
        {
            "criterion": "forecast_rmse_gain_at_least_5pct",
            "value": gain, "threshold": 0.05, "passed": bool(gain >= 0.05),
        },
        {
            "criterion": "forecast_delta_bic_at_most_minus_10 (naif)",
            "value": bic_naive, "threshold": -10.0,
            "passed": bool(bic_naive <= -10.0),
        },
        {
            "criterion": "forecast_delta_bic_at_most_minus_10 (n_eff)",
            "value": bic_effective, "threshold": -10.0,
            "passed": bool(bic_effective <= -10.0),
        },
        {
            "criterion": "100k_regime_within_factor_2_and_closer_than_reference",
            "value": ratio_m2, "threshold": target_ratio / 2.0,
            "passed": bool(
                target_ratio / 2.0 <= ratio_m2 <= target_ratio * 2.0
                and log_ratio_error(ratio_m2, target_ratio)
                < log_ratio_error(ratio_ref, target_ratio)
            ),
        },
        {
            "criterion": "chronology_correlation_and_termination_timing",
            "value": correlation_m2, "threshold": 0.4,
            "passed": bool(correlation_m2 >= 0.4 and timing <= 25.0),
        },
        {
            "criterion": "blockwise_wilcoxon_M2_better",
            "value": p_block, "threshold": 0.05, "passed": bool(p_block < 0.05),
        },
    ], {
        "observed_power_ratio": float(target_ratio),
        "termination_timing_mae_kyr": float(timing),
        "residual_lag1_autocorrelation_M2": float(lag1_autocorrelation(residual_m2)),
        "effective_sample_size_M2": float(n_eff_m2),
        "actual_sample_size": int(prediction_mask.sum()),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    dataset, _ = load_dataset()
    observed, forcing, training_mask = standardise(dataset, 1200)
    prediction_mask = ~training_mask
    elapsed = dataset["elapsed_kyr"].to_numpy()
    seeds = [729 + 37 * k for k in range(12)]

    report = {}
    frames = []
    for bounds_name, label in (("reference", "bornes livrées"),
                               ("wide", "bornes élargies")):
        fits, _ = fit_all(observed, forcing, training_mask, MODELS, seeds,
                          BUDGET_HIGH, bounds_name=bounds_name)
        predictions = {
            model: simulate(model, forcing, observed[0], fit.vector)
            for model, fit in fits.items()
        }
        for reference in ("M1", "M1P"):
            rows, extra = criteria_for(
                reference, observed, predictions, prediction_mask, elapsed
            )
            frame = pd.DataFrame(rows)
            frame["bounds"] = label
            frame["reference_model"] = reference
            frames.append(frame)
            core = [row for row in rows
                    if "naif" not in row["criterion"]]
            report[f"{bounds_name}_vs_{reference}"] = {
                "passed": int(sum(row["passed"] for row in core)),
                "total": len(core),
                "detail": rows,
                **extra,
            }
            print(f"{label} / témoin {reference} : "
                  f"{report[f'{bounds_name}_vs_{reference}']['passed']}"
                  f"/{len(core)} critères réussis", flush=True)

    table = pd.concat(frames, ignore_index=True)
    table.to_csv(OUT / "e_hardened_verdict.csv", index=False)
    (OUT / "e_hardened_verdict.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=float),
        encoding="utf-8",
    )
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()
