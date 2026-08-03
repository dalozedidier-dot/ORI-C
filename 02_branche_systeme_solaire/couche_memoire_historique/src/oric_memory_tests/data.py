from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd


LR04_COLUMNS = ("age_calkaBP", "d18O_benthic", "d18O_error")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_lr04(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, sep="\t", comment="#")
    missing = set(LR04_COLUMNS).difference(frame.columns)
    if missing:
        raise ValueError(f"Colonnes LR04 manquantes: {sorted(missing)}")
    frame = frame.loc[:, LR04_COLUMNS].apply(pd.to_numeric, errors="coerce")
    if frame.isna().any().any():
        raise ValueError("LR04 contient des valeurs non numériques ou manquantes.")
    if not frame["age_calkaBP"].is_monotonic_increasing:
        raise ValueError("Les âges LR04 doivent être croissants.")
    if frame["age_calkaBP"].duplicated().any():
        raise ValueError("Les âges LR04 doivent être uniques.")
    return frame


def _fortran_float(value: str | bytes) -> float:
    if isinstance(value, bytes):
        value = value.decode("ascii")
    return float(value.replace("D", "E"))


def load_la2004(path: Path) -> pd.DataFrame:
    values = np.loadtxt(
        path,
        converters={1: _fortran_float, 2: _fortran_float, 3: _fortran_float},
    )
    frame = pd.DataFrame(
        values,
        columns=("time_kyr_j2000", "eccentricity", "obliquity_rad", "varpi_rad"),
    )
    if len(frame) < 50_000:
        raise ValueError("Le fichier La2004 paraît incomplet.")
    if not frame["time_kyr_j2000"].is_monotonic_decreasing:
        raise ValueError("Le temps La2004 doit décroître du présent vers le passé.")
    return frame


def daily_mean_insolation(
    latitude_deg: float,
    solar_longitude_rad: float | np.ndarray,
    eccentricity: np.ndarray | float,
    obliquity_rad: np.ndarray | float,
    varpi_rad: np.ndarray | float,
    solar_constant: float = 1365.0,
) -> np.ndarray:
    """Insolation journalière moyenne selon la géométrie de Berger/Laskar."""

    latitude = np.deg2rad(latitude_deg)
    solar_longitude = np.asarray(solar_longitude_rad, dtype=float)
    eccentricity = np.asarray(eccentricity, dtype=float)
    obliquity = np.asarray(obliquity_rad, dtype=float)
    varpi = np.asarray(varpi_rad, dtype=float)

    declination = np.arcsin(np.sin(obliquity) * np.sin(solar_longitude))
    sunset_angle = np.arccos(
        np.clip(-np.tan(latitude) * np.tan(declination), -1.0, 1.0)
    )
    inverse_distance_squared = (
        (1.0 + eccentricity * np.cos(solar_longitude - varpi)) ** 2
        / (1.0 - eccentricity**2) ** 2
    )
    geometry = (
        sunset_angle * np.sin(latitude) * np.sin(declination)
        + np.cos(latitude) * np.cos(declination) * np.sin(sunset_angle)
    )
    return solar_constant / np.pi * inverse_distance_squared * geometry


def prepare_mpt_dataset(
    raw_dir: Path,
    output_path: Path | None = None,
    start_age_kyr: int = 2600,
    end_age_kyr: int = 0,
) -> tuple[pd.DataFrame, dict]:
    lr04_path = raw_dir / "lisiecki2005-d18o-stack-noaa.txt"
    la2004_path = raw_dir / "INSOLN.LA2004.BTL.ASC"
    lr04 = load_lr04(lr04_path)
    orbital = load_la2004(la2004_path)

    age_kyr = np.arange(start_age_kyr, end_age_kyr - 1, -1, dtype=float)
    elapsed_kyr = start_age_kyr - age_kyr

    orbital_sorted = orbital.sort_values("time_kyr_j2000")
    insolation = daily_mean_insolation(
        latitude_deg=65.0,
        solar_longitude_rad=np.pi / 2.0,
        eccentricity=orbital_sorted["eccentricity"].to_numpy(),
        obliquity_rad=orbital_sorted["obliquity_rad"].to_numpy(),
        varpi_rad=orbital_sorted["varpi_rad"].to_numpy(),
    )
    orbital_time = orbital_sorted["time_kyr_j2000"].to_numpy()
    requested_time = -age_kyr

    frame = pd.DataFrame(
        {
            "elapsed_kyr": elapsed_kyr,
            "age_kyr_bp": age_kyr,
            "d18o_permil": np.interp(
                age_kyr, lr04["age_calkaBP"], lr04["d18O_benthic"]
            ),
            "d18o_error_permil": np.interp(
                age_kyr, lr04["age_calkaBP"], lr04["d18O_error"]
            ),
            "eccentricity": np.interp(
                requested_time, orbital_time, orbital_sorted["eccentricity"]
            ),
            "obliquity_deg": np.rad2deg(
                np.interp(
                    requested_time, orbital_time, orbital_sorted["obliquity_rad"]
                )
            ),
            "varpi_rad": np.interp(
                requested_time, orbital_time, orbital_sorted["varpi_rad"]
            ),
            "insolation_65n_june_wm2": np.interp(
                requested_time, orbital_time, insolation
            ),
        }
    )
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(output_path, index=False)

    quality = {
        "row_count": int(len(frame)),
        "age_min_kyr_bp": float(frame["age_kyr_bp"].min()),
        "age_max_kyr_bp": float(frame["age_kyr_bp"].max()),
        "grid_step_kyr": float(np.median(np.diff(frame["elapsed_kyr"]))),
        "null_count": int(frame.isna().sum().sum()),
        "duplicate_age_count": int(frame["age_kyr_bp"].duplicated().sum()),
        "lr04_source_rows": int(len(lr04)),
        "la2004_source_rows": int(len(orbital)),
        "lr04_sha256": sha256_file(lr04_path),
        "la2004_sha256": sha256_file(la2004_path),
        "insolation_min_wm2": float(frame["insolation_65n_june_wm2"].min()),
        "insolation_max_wm2": float(frame["insolation_65n_june_wm2"].max()),
    }
    return frame, quality

