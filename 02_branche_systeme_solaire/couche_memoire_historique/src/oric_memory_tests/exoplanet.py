from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .metrics import holm_adjust, paired_wilcoxon_greater


STATE_NAMES = (
    "temperature_k",
    "ice_fraction",
    "co2_ppm",
    "regolith_fraction",
    "carbon_memory",
    "productivity",
)
TEST_VARIABLES = (
    "temperature_k",
    "ice_fraction",
    "co2_ppm",
    "productivity",
)
MATERIALITY_THRESHOLDS = {
    "temperature_k": 0.1,
    "ice_fraction": 0.01,
    "co2_ppm": 1.0,
    "productivity": 0.01,
}


DEFAULT_PARAMETERS = {
    "tau_temperature_myr": 0.05,
    "tau_ice_myr": 0.18,
    "tau_co2_myr": 0.8,
    "global_forcing_gain": 2.2,
    "co2_temperature_gain": 1.6,
    "ice_albedo_gain": 3.8,
    "polar_forcing_gain": 1.3,
    "ice_threshold": 0.2,
    "ice_transition_width": 0.55,
    "bedrock_ice_gain": 1.5,
    "bedrock_tau_gain": 1.5,
    "regolith_erosion_rate": 0.11,
    "tau_regolith_recovery_myr": 60.0,
    "carbon_sequestration_gain": 0.6,
    "tau_carbon_memory_myr": 8.0,
    "weathering_temperature_gain": 0.09,
}


def _smoothstep(value: np.ndarray) -> np.ndarray:
    clipped = np.clip(value, 0.0, 1.0)
    return clipped**2 * (3.0 - 2.0 * clipped)


def generate_controlled_histories(
    step_myr: float = 0.02,
    spinup_myr: float = 10.0,
    history_myr: float = 50.0,
    final_hold_myr: float = 10.0,
) -> pd.DataFrame:
    time = np.arange(
        -spinup_myr,
        history_myr + final_hold_myr + step_myr / 2.0,
        step_myr,
    )
    progress = np.clip(time / history_myr, 0.0, 1.0)
    remaining = 1.0 - _smoothstep(progress)
    excursion = 4.0 * progress * (1.0 - progress)

    obliquity_a = 23.5 + (70.0 - 23.5) * remaining
    eccentricity_a = 0.05 + (0.30 - 0.05) * remaining

    obliquity_b_base = 23.5 + (10.0 - 23.5) * remaining
    obliquity_b = obliquity_b_base + (30.0 - 16.75) * excursion
    eccentricity_b_base = 0.05 + (0.01 - 0.05) * remaining
    eccentricity_b = eccentricity_b_base + (0.10 - 0.03) * excursion

    before = time < 0.0
    after = time >= history_myr
    obliquity_a[before], eccentricity_a[before] = 70.0, 0.30
    obliquity_b[before], eccentricity_b[before] = 10.0, 0.01
    obliquity_a[after], eccentricity_a[after] = 23.5, 0.05
    obliquity_b[after], eccentricity_b[after] = 23.5, 0.05

    return pd.DataFrame(
        {
            "time_myr": time,
            "obliquity_A_deg": obliquity_a,
            "eccentricity_A": eccentricity_a,
            "obliquity_B_deg": obliquity_b,
            "eccentricity_B": eccentricity_b,
        }
    )


def polar_summer_insolation(
    obliquity_deg: np.ndarray | float,
    eccentricity: np.ndarray | float,
    latitude_deg: float = 65.0,
    varpi_deg: float = 102.9,
    solar_constant: float = 1365.0,
) -> np.ndarray:
    obliquity = np.deg2rad(obliquity_deg)
    eccentricity = np.asarray(eccentricity, dtype=float)
    latitude = np.deg2rad(latitude_deg)
    varpi = np.deg2rad(varpi_deg)
    solar_longitude = np.pi / 2.0
    sunset = np.arccos(
        np.clip(-np.tan(latitude) * np.tan(obliquity), -1.0, 1.0)
    )
    distance = (
        (1.0 + eccentricity * np.cos(solar_longitude - varpi)) ** 2
        / (1.0 - eccentricity**2) ** 2
    )
    geometry = (
        sunset * np.sin(latitude) * np.sin(obliquity)
        + np.cos(latitude) * np.cos(obliquity) * np.sin(sunset)
    )
    return solar_constant / np.pi * distance * geometry


def simulate_reduced_climate(
    time_myr: np.ndarray,
    obliquity_deg: np.ndarray,
    eccentricity: np.ndarray,
    mode: str,
    initial_state: np.ndarray,
    parameters: dict[str, float] | None = None,
) -> np.ndarray:
    """EMIC réduit.

    `classic` retire les deux états lents. `ablated` conserve leurs couplages
    mais les fixe à une référence identique pour les deux histoires. `M2`
    laisse évoluer le régolithe et la mémoire du carbone.
    """

    parameters = {**DEFAULT_PARAMETERS, **(parameters or {})}
    time = np.asarray(time_myr, dtype=float)
    step = float(np.median(np.diff(time)))
    substep_count = max(1, int(np.ceil(step / 0.02)))
    internal_step = step / substep_count
    polar = polar_summer_insolation(obliquity_deg, eccentricity)
    polar_reference = float(polar_summer_insolation(23.5, 0.05))
    polar_anomaly = (polar - polar_reference) / 100.0
    annual_flux_anomaly = (
        1.0 / np.sqrt(1.0 - np.asarray(eccentricity) ** 2)
        - 1.0 / np.sqrt(1.0 - 0.05**2)
    ) / 0.05

    temperature, ice, co2, regolith, carbon_memory = map(float, initial_state)
    output = np.empty((len(time), len(STATE_NAMES)), dtype=float)

    for index in range(len(time)):
        for _ in range(substep_count):
            productivity = (
                np.exp(-((temperature - 0.5) / 4.0) ** 2)
                * (max(co2, 50.0) / 280.0) ** 0.2
                * (1.0 - 0.45 * ice)
            )

            if mode == "M2":
                bedrock = 1.0 - regolith
                carbon_effect = carbon_memory - 0.5
            elif mode == "ablated":
                bedrock = 0.5
                carbon_effect = 0.0
                regolith = 0.5
                carbon_memory = 0.5
            elif mode == "classic":
                bedrock = 0.0
                carbon_effect = 0.0
            else:
                raise ValueError(f"Mode climatique inconnu: {mode}")

            temperature_target = (
                parameters["global_forcing_gain"] * annual_flux_anomaly[index]
                + parameters["co2_temperature_gain"]
                * np.log(max(co2, 50.0) / 280.0)
                - parameters["ice_albedo_gain"] * ice
            )
            ice_argument = -(
                temperature
                + parameters["polar_forcing_gain"] * polar_anomaly[index]
                - parameters["ice_threshold"]
                - parameters["bedrock_ice_gain"] * bedrock
            ) / parameters["ice_transition_width"]
            ice_target = 1.0 / (
                1.0 + np.exp(-np.clip(ice_argument, -30.0, 30.0))
            )
            co2_target = 280.0 * np.exp(
                -parameters["weathering_temperature_gain"] * temperature
                - parameters["carbon_sequestration_gain"] * carbon_effect
            )
            effective_tau_ice = parameters["tau_ice_myr"] * (
                1.0 + parameters["bedrock_tau_gain"] * bedrock
            )

            temperature += internal_step * (
                temperature_target - temperature
            ) / parameters["tau_temperature_myr"]
            ice = float(
                np.clip(
                    ice
                    + internal_step * (ice_target - ice) / effective_tau_ice,
                    0.0,
                    1.0,
                )
            )
            co2 = float(
                np.clip(
                    co2
                    + internal_step
                    * (co2_target - co2)
                    / parameters["tau_co2_myr"],
                    80.0,
                    1200.0,
                )
            )

            if mode == "M2":
                regolith += internal_step * (
                    -parameters["regolith_erosion_rate"] * ice * regolith
                    + (1.0 - regolith)
                    / parameters["tau_regolith_recovery_myr"]
                )
                carbon_memory += internal_step * (
                    productivity - carbon_memory
                ) / parameters["tau_carbon_memory_myr"]
                regolith = float(np.clip(regolith, 0.0, 1.0))
                carbon_memory = float(np.clip(carbon_memory, 0.0, 2.0))

        output[index] = (
            temperature,
            ice,
            co2,
            regolith,
            carbon_memory,
            productivity,
        )
    return output


def _plot_forcings(forcing: pd.DataFrame, output_path: Path) -> None:
    figure, axes = plt.subplots(2, 1, figsize=(11.5, 7.0), sharex=True)
    axes[0].plot(
        forcing["time_myr"],
        forcing["obliquity_A_deg"],
        color="#D97706",
        label="Trajectoire A",
    )
    axes[0].plot(
        forcing["time_myr"],
        forcing["obliquity_B_deg"],
        color="#2B6CB0",
        label="Trajectoire B",
    )
    axes[0].set_ylabel("Obliquité (°)")
    axes[0].legend(frameon=False, ncol=2)
    axes[1].plot(
        forcing["time_myr"],
        forcing["eccentricity_A"],
        color="#D97706",
    )
    axes[1].plot(
        forcing["time_myr"],
        forcing["eccentricity_B"],
        color="#2B6CB0",
    )
    axes[1].set_ylabel("Excentricité")
    axes[1].set_xlabel("Temps (Ma)")
    for axis in axes:
        axis.axvspan(-10.0, 0.0, color="#E9EEF5", alpha=0.6)
        axis.axvspan(50.0, 60.0, color="#E7F4EA", alpha=0.7)
        axis.grid(axis="y", color="#D9DDE3", linewidth=0.7)
    figure.suptitle("Deux histoires distinctes avec un forçage final identique")
    figure.tight_layout()
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def _plot_final_deltas(statistics: pd.DataFrame, output_path: Path) -> None:
    variables = statistics["variable"].tolist()
    positions = np.arange(len(variables))
    width = 0.25
    figure, axis = plt.subplots(figsize=(9.2, 5.4))
    for offset, (column, label, color) in enumerate(
        (
            ("median_delta_classic", "Classique", "#A7A9AC"),
            ("median_delta_ablated", "M2 sans mémoire", "#8A5CF6"),
            ("median_delta_M2", "M2 ORI-C", "#D97706"),
        )
    ):
        axis.bar(
            positions + (offset - 1) * width,
            statistics[column].clip(lower=1e-10),
            width,
            label=label,
            color=color,
            edgecolor="#333333",
            linewidth=0.4,
        )
    axis.set_yscale("log")
    axis.set_xticks(positions, variables)
    axis.set_ylabel("|A − B|, médiane de l’ensemble")
    axis.set_title("Écart final entre les deux histoires")
    axis.legend(frameon=False, ncol=3)
    axis.grid(axis="y", which="both", color="#D9DDE3", linewidth=0.7)
    figure.tight_layout()
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)


def _median_absolute_deltas(
    time: np.ndarray,
    forcing: pd.DataFrame,
    initial_states,
    mode: str,
    final_mask: np.ndarray,
    parameters: dict[str, float] | None,
) -> np.ndarray:
    """Écarts |A − B| par réplicat sur la fenêtre finale, pour un mode donné."""
    deltas = np.empty((len(initial_states), len(STATE_NAMES)))
    for index, initial_state in enumerate(initial_states):
        finals = {}
        for trajectory in ("A", "B"):
            simulation = simulate_reduced_climate(
                time,
                forcing[f"obliquity_{trajectory}_deg"].to_numpy(),
                forcing[f"eccentricity_{trajectory}"].to_numpy(),
                mode,
                initial_state,
                parameters,
            )
            finals[trajectory] = simulation[final_mask].mean(axis=0)
        deltas[index] = np.abs(finals["A"] - finals["B"])
    return deltas


def run_exoplanet_test(
    project_root: Path,
    seed: int = 729,
    ensemble_size: int = 20,
    step_myr: float = 0.02,
    final_hold_myr: float = 10.0,
    persistence_hold_myr: float = 300.0,
    parameters: dict[str, float] | None = None,
) -> dict:
    output_dir = project_root / "results" / "exoplanet"
    figure_dir = output_dir / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)

    forcing = generate_controlled_histories(
        step_myr=step_myr, final_hold_myr=final_hold_myr
    )
    time = forcing["time_myr"].to_numpy()
    final_mask = time >= 50.0 + final_hold_myr - 2.0
    final_forcing_equal = bool(
        np.array_equal(
            forcing.loc[time >= 50.0, "obliquity_A_deg"].to_numpy(),
            forcing.loc[time >= 50.0, "obliquity_B_deg"].to_numpy(),
        )
        and np.array_equal(
            forcing.loc[time >= 50.0, "eccentricity_A"].to_numpy(),
            forcing.loc[time >= 50.0, "eccentricity_B"].to_numpy(),
        )
    )

    random = np.random.default_rng(seed)
    initial_states = []
    for _ in range(ensemble_size):
        initial_states.append(
            np.array(
                [
                    random.normal(0.0, 0.2),
                    np.clip(random.normal(0.2, 0.05), 0.0, 1.0),
                    random.normal(300.0, 15.0),
                    random.uniform(0.6, 1.0),
                    random.uniform(0.1, 0.6),
                ]
            )
        )

    state_rows = []
    trajectory_rows = []
    for mode in ("classic", "ablated", "M2"):
        for replicate, initial_state in enumerate(initial_states):
            simulations = {}
            for trajectory in ("A", "B"):
                simulations[trajectory] = simulate_reduced_climate(
                    time,
                    forcing[f"obliquity_{trajectory}_deg"].to_numpy(),
                    forcing[f"eccentricity_{trajectory}"].to_numpy(),
                    mode,
                    initial_state,
                    parameters,
                )
                final_mean = simulations[trajectory][final_mask].mean(axis=0)
                final_std = simulations[trajectory][final_mask].std(axis=0)
                for index, variable in enumerate(STATE_NAMES):
                    state_rows.append(
                        {
                            "model": mode,
                            "replicate": replicate,
                            "trajectory": trajectory,
                            "variable": variable,
                            "final_mean": float(final_mean[index]),
                            "final_window_std": float(final_std[index]),
                        }
                    )
            if replicate == 0:
                for trajectory, values in simulations.items():
                    for index, current_time in enumerate(time):
                        trajectory_rows.append(
                            {
                                "model": mode,
                                "trajectory": trajectory,
                                "time_myr": current_time,
                                **{
                                    name: float(values[index, position])
                                    for position, name in enumerate(STATE_NAMES)
                                },
                            }
                        )

    states = pd.DataFrame(state_rows)
    sample_trajectories = pd.DataFrame(trajectory_rows)
    delta_rows = []
    for (model, replicate, variable), group in states.groupby(
        ["model", "replicate", "variable"]
    ):
        values = group.set_index("trajectory")["final_mean"]
        delta_rows.append(
            {
                "model": model,
                "replicate": replicate,
                "variable": variable,
                "absolute_delta_A_B": float(abs(values["A"] - values["B"])),
            }
        )
    deltas = pd.DataFrame(delta_rows)

    statistics_rows = []
    raw_p_values = []
    for variable in TEST_VARIABLES:
        by_model = {
            model: deltas.loc[
                (deltas["model"] == model) & (deltas["variable"] == variable),
                "absolute_delta_A_B",
            ].to_numpy()
            for model in ("classic", "ablated", "M2")
        }
        p_value = paired_wilcoxon_greater(by_model["M2"], by_model["ablated"])
        raw_p_values.append(p_value)
        statistics_rows.append(
            {
                "variable": variable,
                "median_delta_classic": float(np.median(by_model["classic"])),
                "median_delta_ablated": float(np.median(by_model["ablated"])),
                "median_delta_M2": float(np.median(by_model["M2"])),
                "wilcoxon_p_M2_greater_than_ablated": p_value,
                "effect_ratio_M2_to_ablated": float(
                    (np.median(by_model["M2"]) + 1e-12)
                    / (np.median(by_model["ablated"]) + 1e-12)
                ),
                "ablation_reduction_fraction": float(
                    1.0
                    - np.median(by_model["ablated"])
                    / max(np.median(by_model["M2"]), 1e-12)
                ),
                "materiality_threshold": MATERIALITY_THRESHOLDS[variable],
                "materiality_pass": bool(
                    np.median(by_model["M2"]) >= MATERIALITY_THRESHOLDS[variable]
                ),
            }
        )
    adjusted = holm_adjust(raw_p_values)
    for row, adjusted_p in zip(statistics_rows, adjusted):
        row["holm_adjusted_p"] = adjusted_p
        row["structural_path_dependence_pass"] = bool(
            adjusted_p < 0.05 and row["effect_ratio_M2_to_ablated"] >= 10.0
        )
        row["memory_ablation_pass"] = bool(
            row["ablation_reduction_fraction"] >= 0.9
        )

    # Test de persistance. Les constantes de temps lentes du modèle valent 8 Ma
    # pour le carbone et 60 Ma pour le régolithe. Un palier final de 10 Ma ne
    # peut donc pas distinguer une mémoire véritable d'un simple retard de
    # relaxation : les deux histoires sont encore en train de converger. On
    # prolonge le palier et on exige que l'écart survive.
    persistence_forcing = generate_controlled_histories(
        step_myr=step_myr, final_hold_myr=persistence_hold_myr
    )
    persistence_time = persistence_forcing["time_myr"].to_numpy()
    persistence_mask = persistence_time >= 50.0 + persistence_hold_myr - 2.0
    persistence_deltas = _median_absolute_deltas(
        persistence_time, persistence_forcing, initial_states, "M2",
        persistence_mask, parameters,
    )
    for row in statistics_rows:
        position = STATE_NAMES.index(row["variable"])
        long_hold = float(np.median(persistence_deltas[:, position]))
        row["median_delta_M2_long_hold"] = long_hold
        row["persistence_hold_myr"] = float(persistence_hold_myr)
        row["retained_fraction_after_long_hold"] = float(
            long_hold / max(row["median_delta_M2"], 1e-300)
        )
        # Une inscription persistante doit conserver au moins un dixième de son
        # écart après un palier trente fois plus long, et rester matérielle.
        row["persistence_pass"] = bool(
            row["retained_fraction_after_long_hold"] >= 0.1
            and long_hold >= MATERIALITY_THRESHOLDS[row["variable"]]
        )

    statistics = pd.DataFrame(statistics_rows)

    structural_count = int(statistics["structural_path_dependence_pass"].sum())
    ablation_count = int(statistics["memory_ablation_pass"].sum())
    material_count = int(statistics["materiality_pass"].sum())
    persistence_count = int(statistics["persistence_pass"].sum())
    structural_pass = bool(
        final_forcing_equal and structural_count >= 2 and ablation_count >= 2
    )
    physical_relevance_pass = bool(material_count >= 2)
    persistence_relevance_pass = bool(persistence_count >= 2)

    forcing.to_csv(output_dir / "controlled_forcings.csv", index=False)
    states.to_csv(output_dir / "ensemble_final_states.csv", index=False)
    deltas.to_csv(output_dir / "path_deltas.csv", index=False)
    statistics.to_csv(output_dir / "statistical_tests.csv", index=False)
    sample_trajectories.to_csv(
        output_dir / "sample_trajectories_replicate_0.csv", index=False
    )
    (output_dir / "parameters.json").write_text(
        json.dumps(
            {**DEFAULT_PARAMETERS, **(parameters or {})},
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    _plot_forcings(forcing, figure_dir / "controlled_forcings.png")
    _plot_final_deltas(statistics, figure_dir / "final_path_deltas.png")

    summary = {
        "test": "exoplanet_controlled_history",
        "status": (
            "structural_pass"
            if structural_pass
            else "structural_test_not_passed"
        ),
        "structural_pass": structural_pass,
        "physical_relevance_pass": physical_relevance_pass,
        "persistence_pass": persistence_relevance_pass,
        "same_final_forcing_pass": final_forcing_equal,
        "structural_variables_passed": structural_count,
        "ablation_variables_passed": ablation_count,
        "material_variables_passed": material_count,
        "persistent_variables_passed": persistence_count,
        "variables_tested": len(TEST_VARIABLES),
        "ensemble_size": ensemble_size,
        "final_hold_myr": float(final_hold_myr),
        "persistence_hold_myr": float(persistence_hold_myr),
        "seed": seed,
        "interpretation": (
            "Ce calcul teste la logique de dépendance au chemin, son ablation et "
            "sa persistance. Il ne mesure pas une supériorité prédictive face à "
            "un GCM."
        ),
        "persistence_note": (
            "Le test structurel seul ne distingue pas une inscription durable "
            "d'un retard de relaxation. Avec un palier final de l'ordre des "
            "constantes de temps lentes du modèle, deux histoires différentes "
            "sont encore en train de converger. Le critère de persistance exige "
            "qu'un écart matériel subsiste après un palier beaucoup plus long."
        ),
        "scope_limit": (
            "Les deux trajectoires orbitales sont prescrites et non produites par "
            "un calcul N-corps-spin validé. L'EMIC est un modèle réduit non calibré "
            "sur ROCKE-3D, WACCM6 ou GEOCLIM."
        ),
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return summary
