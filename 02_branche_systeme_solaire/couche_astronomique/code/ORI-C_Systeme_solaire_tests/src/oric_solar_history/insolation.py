from __future__ import annotations

import numpy as np
import pandas as pd


def daily_mean_insolation(
    eccentricity: np.ndarray,
    long_peri_rad: np.ndarray,
    latitude_deg: float,
    solar_longitude_deg: float,
    obliquity_deg: float = 23.44,
    solar_constant_w_m2: float = 1361.0,
) -> np.ndarray:
    e = np.asarray(eccentricity, dtype=float)
    varpi = np.asarray(long_peri_rad, dtype=float)
    phi = np.deg2rad(latitude_deg)
    lam = np.deg2rad(solar_longitude_deg)
    eps = np.deg2rad(obliquity_deg)

    declination = np.arcsin(np.sin(eps) * np.sin(lam))
    cos_h0 = -np.tan(phi) * np.tan(declination)
    h0 = np.arccos(np.clip(cos_h0, -1.0, 1.0))
    h0 = np.where(cos_h0 <= -1.0, np.pi, h0)
    h0 = np.where(cos_h0 >= 1.0, 0.0, h0)

    true_longitude_from_peri = lam - varpi
    r_over_a = (1.0 - e * e) / (1.0 + e * np.cos(true_longitude_from_peri))
    flux = solar_constant_w_m2 / np.square(r_over_a)
    geometry = h0 * np.sin(phi) * np.sin(declination) + np.cos(phi) * np.cos(declination) * np.sin(
        h0
    )
    q = flux * geometry / np.pi
    return np.maximum(q, 0.0)


def build_insolation_frame(earth_orbits: pd.DataFrame, config: dict) -> pd.DataFrame:
    q = daily_mean_insolation(
        earth_orbits["eccentricity"].to_numpy(),
        earth_orbits["long_peri_rad"].to_numpy(),
        latitude_deg=float(config["latitude_deg"]),
        solar_longitude_deg=float(config["solar_longitude_deg"]),
        obliquity_deg=float(config.get("obliquity_deg", 23.44)),
        solar_constant_w_m2=float(config.get("solar_constant_w_m2", 1361.0)),
    )
    return pd.DataFrame(
        {
            "time_years": earth_orbits["time_years"].to_numpy(),
            "insolation_w_m2": q,
            "latitude_deg": float(config["latitude_deg"]),
            "solar_longitude_deg": float(config["solar_longitude_deg"]),
            "obliquity_deg": float(config.get("obliquity_deg", 23.44)),
        }
    )
