from __future__ import annotations

import numpy as np
import pandas as pd


def run_reduced_climate(insolation: pd.DataFrame, config: dict) -> pd.DataFrame:
    times = insolation["time_years"].to_numpy(dtype=float)
    forcing = insolation["insolation_w_m2"].to_numpy(dtype=float)
    if times.size < 2:
        raise ValueError("Au moins deux points sont nécessaires pour le modèle climatique")
    dt = np.diff(times, prepend=times[0])
    if dt[0] == 0:
        dt[0] = np.median(np.diff(times))

    tau_t = float(config["response_time_years"])
    tau_i = float(config["ice_response_time_years"])
    t_ref = float(config["reference_temperature_c"])
    sensitivity = float(config["forcing_sensitivity_k_per_w_m2"])
    ice_cooling = float(config["ice_cooling_k"])
    freeze_on = float(config["freeze_on_c"])
    melt_off = float(config["melt_off_c"])

    q_ref = float(np.mean(forcing))
    temperature = np.empty_like(forcing)
    ice = np.empty_like(forcing)
    temperature[0] = t_ref
    ice[0] = 0.25
    regime = 0

    for k in range(1, forcing.size):
        target_temp = t_ref + sensitivity * (forcing[k] - q_ref) - ice_cooling * ice[k - 1]
        alpha_t = 1.0 - np.exp(-dt[k] / tau_t)
        temperature[k] = temperature[k - 1] + alpha_t * (target_temp - temperature[k - 1])

        if regime == 0 and temperature[k] <= freeze_on:
            regime = 1
        elif regime == 1 and temperature[k] >= melt_off:
            regime = 0
        ice_target = 0.85 if regime == 1 else 0.05
        alpha_i = 1.0 - np.exp(-dt[k] / tau_i)
        ice[k] = ice[k - 1] + alpha_i * (ice_target - ice[k - 1])

    return pd.DataFrame(
        {
            "time_years": times,
            "temperature_c": temperature,
            "ice_fraction": np.clip(ice, 0.0, 1.0),
            "insolation_w_m2": forcing,
        }
    )


def count_threshold_crossings(values: np.ndarray, threshold: float) -> int:
    v = np.asarray(values, dtype=float)
    if v.size < 2:
        return 0
    sides = v >= threshold
    return int(np.count_nonzero(sides[1:] != sides[:-1]))
