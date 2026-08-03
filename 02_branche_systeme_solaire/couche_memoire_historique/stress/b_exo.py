"""Campagne B — durcissement du test exoplanétaire contrôlé.

Étapes :
  B1  Convergence numérique : l'écart A−B de M2 est-il au-dessus de l'erreur
      d'intégration ? Le pas livré est 0,02 Ma.
  B2  Taille d'ensemble et graines : l'écart médian et la valeur p sont-ils
      stables ?
  B3  Test de relaxation (décisif) : le palier final est prolongé de 10 Ma
      jusqu'à 600 Ma. Une mémoire véritable persiste ; un simple retard
      s'efface.
  B4  Sonde de multistabilité : sous le forçage final identique, des états
      initiaux très différents convergent-ils vers un attracteur unique ?
  B5  Carte de matérialité : existe-t-il une région de paramètres où l'écart
      dépasse les seuils préenregistrés et y reste ?
"""

from __future__ import annotations

import argparse
import json
import math
import time

import numpy as np
import pandas as pd

from core import (
    OUTPUT_ROOT,
    controlled_histories,
    exo_initial_states,
    exo_parameter_vector,
    paired_wilcoxon_greater,
    simulate_exo,
)
from oric_memory_tests.exoplanet import (
    MATERIALITY_THRESHOLDS,
    STATE_NAMES,
    TEST_VARIABLES,
)
from oric_memory_tests.metrics import holm_adjust

OUT = OUTPUT_ROOT / "exoplanet"
MODES = ("classic", "ablated", "M2")
VARIABLE_INDEX = {name: index for index, name in enumerate(STATE_NAMES)}


def final_deltas(step_myr, final_hold_myr, states, parameters,
                 window_myr=2.0, modes=MODES):
    """Écart |A − B| moyenné sur la dernière fenêtre du palier, par réplicat."""
    history = controlled_histories(step_myr=step_myr, final_hold_myr=final_hold_myr)
    time_myr = history["time_myr"]
    end = 50.0 + final_hold_myr
    mask = time_myr >= end - window_myr
    output = {}
    for mode in modes:
        deltas = np.empty((len(states), len(STATE_NAMES)))
        for index, state in enumerate(states):
            values = {}
            for trajectory in ("A", "B"):
                simulation = simulate_exo(
                    time_myr,
                    history[f"obliquity_{trajectory}_deg"],
                    history[f"eccentricity_{trajectory}"],
                    mode, state, parameters,
                )
                values[trajectory] = simulation[mask].mean(axis=0)
            deltas[index] = np.abs(values["A"] - values["B"])
        output[mode] = deltas
    return output


def median_table(deltas, ensemble_label="") -> pd.DataFrame:
    rows = []
    raw_p = []
    for variable in TEST_VARIABLES:
        position = VARIABLE_INDEX[variable]
        by_mode = {mode: deltas[mode][:, position] for mode in deltas}
        p_value = paired_wilcoxon_greater(by_mode["M2"], by_mode["ablated"])
        raw_p.append(p_value)
        median_m2 = float(np.median(by_mode["M2"]))
        median_ablated = float(np.median(by_mode["ablated"]))
        rows.append({
            "ensemble": ensemble_label,
            "variable": variable,
            "median_delta_classic": float(np.median(by_mode["classic"])),
            "median_delta_ablated": median_ablated,
            "median_delta_M2": median_m2,
            "effect_ratio_M2_to_ablated": (median_m2 + 1e-12) / (median_ablated + 1e-12),
            "ablation_reduction_fraction": 1.0 - median_ablated / max(median_m2, 1e-12),
            "materiality_threshold": MATERIALITY_THRESHOLDS[variable],
            "materiality_pass": bool(median_m2 >= MATERIALITY_THRESHOLDS[variable]),
            "wilcoxon_p_raw": p_value,
        })
    for row, adjusted in zip(rows, holm_adjust(raw_p)):
        row["holm_adjusted_p"] = adjusted
        row["structural_pass"] = bool(
            adjusted < 0.05 and row["effect_ratio_M2_to_ablated"] >= 10.0
        )
        row["memory_ablation_pass"] = bool(row["ablation_reduction_fraction"] >= 0.9)
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------

def stage_convergence(parameters, ensemble_size) -> dict:
    """B1 : l'effet survit-il au raffinement du pas ?"""
    states = exo_initial_states(729, ensemble_size)
    rows = []
    for step in (0.08, 0.04, 0.02, 0.01, 0.005, 0.0025):
        started = time.perf_counter()
        deltas = final_deltas(step, 10.0, states, parameters)
        for variable in TEST_VARIABLES:
            position = VARIABLE_INDEX[variable]
            rows.append({
                "step_myr": step,
                "variable": variable,
                "median_delta_classic": float(np.median(deltas["classic"][:, position])),
                "median_delta_ablated": float(np.median(deltas["ablated"][:, position])),
                "median_delta_M2": float(np.median(deltas["M2"][:, position])),
            })
        print(f"  pas {step} Ma : {time.perf_counter() - started:.1f} s", flush=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(OUT / "b_step_convergence.csv", index=False)

    summary = {}
    for variable in TEST_VARIABLES:
        subset = frame.loc[frame["variable"] == variable].set_index("step_myr")
        reference = float(subset.loc[0.0025, "median_delta_M2"])
        delivered = float(subset.loc[0.02, "median_delta_M2"])
        summary[variable] = {
            "delta_M2_at_delivered_step": delivered,
            "delta_M2_at_finest_step": reference,
            "relative_change_delivered_to_finest": abs(delivered - reference)
            / max(abs(reference), 1e-300),
            "delta_classic_at_finest_step": float(
                subset.loc[0.0025, "median_delta_classic"]
            ),
            "ratio_M2_to_classic_at_finest_step": delivered
            / max(float(subset.loc[0.0025, "median_delta_classic"]), 1e-300),
        }
    return summary


def stage_ensemble(parameters, sizes, seeds) -> dict:
    """B2 : stabilité vis-à-vis de la taille d'ensemble et de la graine."""
    frames = []
    for size in sizes:
        for seed in seeds:
            states = exo_initial_states(seed, size)
            deltas = final_deltas(0.02, 10.0, states, parameters)
            table = median_table(deltas, ensemble_label=f"n{size}_seed{seed}")
            table["ensemble_size"] = size
            table["seed"] = seed
            frames.append(table)
        print(f"  ensemble n={size} terminé", flush=True)
    frame = pd.concat(frames, ignore_index=True)
    frame.to_csv(OUT / "b_ensemble_stability.csv", index=False)

    summary = {}
    largest = frame.loc[frame["ensemble_size"] == max(sizes)]
    for variable in TEST_VARIABLES:
        subset = largest.loc[largest["variable"] == variable]
        summary[variable] = {
            "median_delta_M2_min": float(subset["median_delta_M2"].min()),
            "median_delta_M2_max": float(subset["median_delta_M2"].max()),
            "structural_pass_fraction": float(subset["structural_pass"].mean()),
            "materiality_pass_fraction": float(subset["materiality_pass"].mean()),
            "holm_p_max": float(subset["holm_adjusted_p"].max()),
        }
    summary["sizes"] = list(sizes)
    summary["seeds"] = list(seeds)
    return summary


def stage_relaxation(parameters, ensemble_size, holds) -> dict:
    """B3 : test décisif de persistance.

    Le protocole livré maintient le forçage final pendant 10 Ma. Les constantes
    de temps lentes du modèle valent 8 Ma (carbone) et 60 Ma (régolithe). Un
    palier de 10 Ma ne peut donc pas distinguer une mémoire véritable d'un
    simple retard de relaxation. On prolonge le palier.
    """
    states = exo_initial_states(729, ensemble_size)
    rows = []
    for hold in holds:
        started = time.perf_counter()
        deltas = final_deltas(0.02, float(hold), states, parameters)
        for variable in TEST_VARIABLES:
            position = VARIABLE_INDEX[variable]
            rows.append({
                "final_hold_myr": hold,
                "variable": variable,
                "median_delta_classic": float(np.median(deltas["classic"][:, position])),
                "median_delta_ablated": float(np.median(deltas["ablated"][:, position])),
                "median_delta_M2": float(np.median(deltas["M2"][:, position])),
                "materiality_threshold": MATERIALITY_THRESHOLDS[variable],
            })
        print(f"  palier {hold} Ma : {time.perf_counter() - started:.1f} s", flush=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(OUT / "b_relaxation.csv", index=False)

    summary = {}
    for variable in TEST_VARIABLES:
        subset = frame.loc[frame["variable"] == variable].sort_values("final_hold_myr")
        holds_array = subset["final_hold_myr"].to_numpy(dtype=float)
        values = subset["median_delta_M2"].to_numpy(dtype=float)
        decaying = values > 0
        efolding = None
        if decaying.sum() >= 3:
            fit = np.polyfit(holds_array[decaying], np.log(values[decaying]), 1)
            if fit[0] < 0:
                efolding = float(-1.0 / fit[0])
        first = float(values[0])
        last = float(values[-1])
        summary[variable] = {
            "delta_M2_at_10myr_hold": first,
            "delta_M2_at_longest_hold": last,
            "longest_hold_myr": float(holds_array[-1]),
            "retained_fraction": last / max(first, 1e-300),
            "efolding_myr": efolding,
            "ever_material": bool(
                (subset["median_delta_M2"] >= MATERIALITY_THRESHOLDS[variable]).any()
            ),
        }
    return summary


def stage_multistability(parameters, probe_count, duration_myr) -> dict:
    """B4 : y a-t-il plusieurs équilibres sous le forçage final ?

    Une dépendance au chemin permanente exige au moins deux attracteurs. On
    lâche des états initiaux très dispersés sous le seul forçage final
    (obliquité 23,5°, excentricité 0,05) et on mesure leur dispersion résiduelle.
    """
    step = 0.02
    time_myr = np.arange(0.0, duration_myr + step / 2.0, step)
    obliquity = np.full_like(time_myr, 23.5)
    eccentricity = np.full_like(time_myr, 0.05)
    random = np.random.default_rng(20260731)
    states = np.column_stack([
        random.uniform(-6.0, 6.0, probe_count),
        random.uniform(0.0, 1.0, probe_count),
        random.uniform(120.0, 900.0, probe_count),
        random.uniform(0.0, 1.0, probe_count),
        random.uniform(0.0, 2.0, probe_count),
    ])
    finals = np.empty((probe_count, len(STATE_NAMES)))
    for index, state in enumerate(states):
        simulation = simulate_exo(
            time_myr, obliquity, eccentricity, "M2", state, parameters
        )
        finals[index] = simulation[-1]
    summary = {"probe_count": probe_count, "duration_myr": duration_myr}
    for variable in TEST_VARIABLES:
        position = VARIABLE_INDEX[variable]
        column = finals[:, position]
        summary[variable] = {
            "initial_spread": (
                float(np.ptp(states[:, position])) if position < states.shape[1]
                else None
            ),
            "final_spread": float(np.ptp(column)),
            "final_std": float(column.std()),
            "final_mean": float(column.mean()),
            "materiality_threshold": MATERIALITY_THRESHOLDS[variable],
            "spread_above_threshold": bool(
                np.ptp(column) >= MATERIALITY_THRESHOLDS[variable]
            ),
        }
    pd.DataFrame(finals, columns=list(STATE_NAMES)).to_csv(
        OUT / "b_multistability_final_states.csv", index=False
    )
    return summary


def stage_materiality_map(base_parameters, ensemble_size, grid_size) -> dict:
    """B5 : existe-t-il une région de paramètres rendant l'effet matériel ?

    On balaie les deux constantes de temps de mémoire et le taux d'érosion du
    régolithe. Pour chaque combinaison, on mesure l'écart au palier livré
    (10 Ma) et à un palier long (200 Ma).
    """
    from core import EXO_PARAMETER_ORDER

    states = exo_initial_states(729, ensemble_size)
    index_carbon = EXO_PARAMETER_ORDER.index("tau_carbon_memory_myr")
    index_regolith = EXO_PARAMETER_ORDER.index("tau_regolith_recovery_myr")
    index_erosion = EXO_PARAMETER_ORDER.index("regolith_erosion_rate")
    index_bedrock = EXO_PARAMETER_ORDER.index("bedrock_ice_gain")

    carbon_values = np.geomspace(1.0, 400.0, grid_size)
    regolith_values = np.geomspace(5.0, 2000.0, grid_size)
    erosion_values = (0.03, 0.11, 0.5)
    bedrock_values = (0.5, 1.5, 4.0)

    rows = []
    started = time.perf_counter()
    for erosion in erosion_values:
        for bedrock in bedrock_values:
            for carbon in carbon_values:
                for regolith in regolith_values:
                    parameters = base_parameters.copy()
                    parameters[index_carbon] = carbon
                    parameters[index_regolith] = regolith
                    parameters[index_erosion] = erosion
                    parameters[index_bedrock] = bedrock
                    short = final_deltas(0.02, 10.0, states, parameters,
                                         modes=("ablated", "M2"))
                    long = final_deltas(0.02, 200.0, states, parameters,
                                        modes=("ablated", "M2"))
                    row = {
                        "tau_carbon_memory_myr": carbon,
                        "tau_regolith_recovery_myr": regolith,
                        "regolith_erosion_rate": erosion,
                        "bedrock_ice_gain": bedrock,
                    }
                    for variable in TEST_VARIABLES:
                        position = VARIABLE_INDEX[variable]
                        row[f"delta10_{variable}"] = float(
                            np.median(short["M2"][:, position])
                        )
                        row[f"delta200_{variable}"] = float(
                            np.median(long["M2"][:, position])
                        )
                        row[f"ablated10_{variable}"] = float(
                            np.median(short["ablated"][:, position])
                        )
                    rows.append(row)
            print(f"  érosion={erosion} bedrock={bedrock} : "
                  f"{time.perf_counter() - started:.0f} s cumulées", flush=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(OUT / "b_materiality_map.csv", index=False)

    summary = {"grid_points": len(frame)}
    for variable in TEST_VARIABLES:
        threshold = MATERIALITY_THRESHOLDS[variable]
        short_pass = frame[f"delta10_{variable}"] >= threshold
        long_pass = frame[f"delta200_{variable}"] >= threshold
        summary[variable] = {
            "threshold": threshold,
            "max_delta_10myr_hold": float(frame[f"delta10_{variable}"].max()),
            "max_delta_200myr_hold": float(frame[f"delta200_{variable}"].max()),
            "fraction_material_at_10myr": float(short_pass.mean()),
            "fraction_material_at_200myr": float(long_pass.mean()),
            "fraction_material_at_both": float((short_pass & long_pass).mean()),
        }
    best = frame.loc[frame["delta10_temperature_k"].idxmax()].to_dict()
    summary["best_temperature_configuration"] = {
        key: float(value) for key, value in best.items()
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stages",
        default="convergence,ensemble,relaxation,multistability,materiality",
    )
    parser.add_argument("--ensemble", type=int, default=60)
    parser.add_argument("--grid", type=int, default=9)
    arguments = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    parameters = exo_parameter_vector()
    report = {}
    stages = [item.strip() for item in arguments.stages.split(",") if item.strip()]

    for stage in stages:
        started = time.perf_counter()
        print(f"[B] étape {stage} ...", flush=True)
        if stage == "convergence":
            report["convergence"] = stage_convergence(parameters, arguments.ensemble)
        elif stage == "ensemble":
            report["ensemble"] = stage_ensemble(
                parameters, sizes=(20, 60, 200), seeds=(729, 1301, 2027, 4099, 8191)
            )
        elif stage == "relaxation":
            report["relaxation"] = stage_relaxation(
                parameters, arguments.ensemble,
                holds=(10, 15, 20, 30, 40, 60, 80, 120, 150, 200, 300, 450, 600),
            )
        elif stage == "multistability":
            report["multistability"] = stage_multistability(
                parameters, probe_count=1000, duration_myr=800.0
            )
        elif stage == "materiality":
            report["materiality"] = stage_materiality_map(
                parameters, ensemble_size=20, grid_size=arguments.grid
            )
        print(f"[B] {stage} terminé en {time.perf_counter() - started:.1f} s",
              flush=True)
        (OUT / "b_report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False, default=float),
            encoding="utf-8",
        )
    print(json.dumps(report, indent=2, ensure_ascii=False, default=float)[:6000])


if __name__ == "__main__":
    main()
