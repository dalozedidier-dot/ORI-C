#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import math
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "plateforme" / "campagne_maximale_reelle" / "data"
OUT = HERE / "resultats" / "DYNAMIQUE_TEMPORELLE.json"
SEED = 20260816
rng = np.random.default_rng(SEED)

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

timecourse_path = DATA / "prebiotic_timecourses.csv"
timecourses = pd.read_csv(timecourse_path)
metrics = []
for (condition, generation, well), group in timecourses.groupby(["condition", "generation", "well"]):
    group = group.sort_values("time_seconds")
    time_h = group.time_seconds.to_numpy(float) / 3600.0
    values = group.turbidity_A400.to_numpy(float)
    early = (time_h >= 0) & (time_h <= 2)
    second = (time_h >= 2) & (time_h <= 6)
    if early.sum() < 2 or second.sum() < 2:
        continue
    early_min = float(np.nanmin(values[early]))
    rebound_max = float(np.nanmax(values[second]))
    metrics.append({
        "condition": condition,
        "generation": generation,
        "well": well,
        "rebound_amp": rebound_max - early_min,
        "auc_2_6_above_early_min": float(np.trapezoid(values[second] - early_min, time_h[second])),
        "slope_2_6_per_hour": float(np.polyfit(time_h[second], values[second], 1)[0]),
    })
metric_table = pd.DataFrame(metrics)

def compare(condition_a, generation_a, condition_b, generation_b, metric, permutations=19999):
    a = metric_table[
        (metric_table.condition == condition_a) & (metric_table.generation == generation_a)
    ][metric].to_numpy()
    b = metric_table[
        (metric_table.condition == condition_b) & (metric_table.generation == generation_b)
    ][metric].to_numpy()
    observed = float(a.mean() - b.mean())
    bootstrap = np.empty(20000)
    for index in range(len(bootstrap)):
        bootstrap[index] = (
            rng.choice(a, len(a), replace=True).mean()
            - rng.choice(b, len(b), replace=True).mean()
        )
    combined = np.r_[a, b]
    n_a = len(a)
    exceed = 0
    for _ in range(permutations):
        permuted = rng.permutation(combined)
        if permuted[:n_a].mean() - permuted[n_a:].mean() >= observed:
            exceed += 1
    return {
        "n_A": len(a),
        "n_B": len(b),
        "mean_difference": observed,
        "bootstrap95": [float(value) for value in np.quantile(bootstrap, [0.025, 0.975])],
        "permutation_p_one_sided": float((exceed + 1) / (permutations + 1)),
    }

summary = []
for (condition, generation), group in metric_table.groupby(["condition", "generation"]):
    summary.append({
        "condition": condition,
        "generation": generation,
        "n_wells": len(group),
        **{
            metric: {
                "mean": float(group[metric].mean()),
                "median": float(group[metric].median()),
                "sd": float(group[metric].std()),
            }
            for metric in ["rebound_amp", "auc_2_6_above_early_min", "slope_2_6_per_hour"]
        },
    })

comparisons = {}
for generation, controls in [("gen1", ["FU", "UR", "UU"]), ("gen2", ["UR", "UU"])]:
    for control in controls:
        for metric in ["rebound_amp", "auc_2_6_above_early_min", "slope_2_6_per_hour"]:
            comparisons[f"FR_{generation}_minus_{control}_{generation}:{metric}"] = compare(
                "FR", generation, control, generation, metric
            )

lineages = pd.read_csv(DATA / "prebiotic_lineages.csv")
endpoint = []
for source_file, group in lineages[lineages.condition == "FR"].groupby("source_file"):
    duration = float(group.generation_duration_h.iloc[0])
    common = int(min(
        group[group.arm == "drift"].generation.max(),
        group[group.arm == "selection"].generation.max(),
    ))
    common_group = group[group.generation == common]
    selection = common_group[common_group.arm == "selection"]["yield"]
    drift = common_group[common_group.arm == "drift"]["yield"]
    if len(selection) and len(drift):
        pooled = math.sqrt(
            (
                (len(selection) - 1) * selection.var()
                + (len(drift) - 1) * drift.var()
            )
            / (len(selection) + len(drift) - 2)
        )
        endpoint.append({
            "source_file": source_file,
            "generation_duration_h": duration,
            "last_shared_generation": common,
            "selection_minus_drift_mean_yield": float(selection.mean() - drift.mean()),
            "standardized_difference": float((selection.mean() - drift.mean()) / pooled) if pooled else None,
            "n_selection": len(selection),
            "n_drift": len(drift),
        })

result = {
    "schema": "oric.vesicle-temporal-reanalysis.v1",
    "source": "plateforme/campagne_maximale_reelle/data/prebiotic_timecourses.csv",
    "source_sha256": sha256(timecourse_path),
    "rows": len(timecourses),
    "analysis_status": "retrospective_exploratory_mechanistic_reanalysis",
    "window_rationale": (
        "2-6 h window quantifies the published second-growth temporal regime; "
        "it is not a new prospective Pacc definition."
    ),
    "metrics_by_condition_generation": summary,
    "FR_vs_controls": comparisons,
    "FR_selection_drift_endpoint_by_generation_duration": sorted(
        endpoint, key=lambda item: item["generation_duration_h"]
    ),
    "original_Pacc_ablation_contrast": -0.0375,
    "original_Pacc_bootstrap95": [-0.1458333333333, 0.0625],
    "original_Pacc_provenance": {
        "status": "historical_result_not_regenerated_by_this_script",
        "source_result_sha256": "562c0bc4e6e5a0c09755d25d540c289c93c68af6ed23253928a992dd2e478f8b",
    },
    "interpretation": (
        "The old discrete-class Pacc result remains negative. Time-resolved A400 shows "
        "a distinct FR rebound and slope regime that is erased by an inventory-only endpoint "
        "proxy. This is a mechanism-level reanalysis, not retrospective requalification of Pacc."
    ),
    "strict_PACC_INT_CHALLENGE_V1_qualified": False,
    "section_XIV_credit": False,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print(f"{len(timecourses)} time-series rows -> {OUT.relative_to(ROOT)}")
