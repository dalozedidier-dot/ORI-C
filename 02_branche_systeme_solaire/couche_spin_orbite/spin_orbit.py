"""Dynamique séculaire réduite du spin terrestre.

Le module intègre un axe de spin unitaire s soumis au couple moyen
solaire/luni-solaire, tandis que la normale orbitale n(t) vient directement
des sorties N-corps ORI-C. La convention est adaptée à une intégration vers le
passé exprimée par ``elapsed_years >= 0``.

Le modèle n'intègre pas explicitement l'orbite lunaire ni les marées. La Lune
est représentée par sa contribution effective à la constante de précession.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ARCSEC_TO_RAD = math.pi / (180.0 * 3600.0)
DEFAULT_OBLIQUITY_DEG = 23.43929111
ALPHA_WITH_MOON_ARCSEC_PER_YEAR = 54.93
ALPHA_SOLAR_ONLY_ARCSEC_PER_YEAR = 20.0


def orbital_normals(frame: pd.DataFrame) -> np.ndarray:
    """Normales unitaires au plan orbital à partir de (i, Omega)."""
    inc = frame["inclination_rad"].to_numpy(dtype=float)
    node = frame["long_node_rad"].to_numpy(dtype=float)
    return np.column_stack(
        (
            np.sin(inc) * np.sin(node),
            -np.sin(inc) * np.cos(node),
            np.cos(inc),
        )
    )


def perihelion_directions(frame: pd.DataFrame) -> np.ndarray:
    """Directions unitaires du périhélie dans le repère inertiel."""
    inc = frame["inclination_rad"].to_numpy(dtype=float)
    node = frame["long_node_rad"].to_numpy(dtype=float)
    arg = frame["arg_peri_rad"].to_numpy(dtype=float)
    ci, si = np.cos(inc), np.sin(inc)
    cO, sO = np.cos(node), np.sin(node)
    cw, sw = np.cos(arg), np.sin(arg)
    return np.column_stack(
        (
            cO * cw - sO * sw * ci,
            sO * cw + cO * sw * ci,
            sw * si,
        )
    )


def initial_spin(normal: np.ndarray, obliquity_deg: float = DEFAULT_OBLIQUITY_DEG) -> np.ndarray:
    """Axe J2000 : obliquité prescrite et équinoxe aligné sur l'axe x.

    Avec n proche de z, cette convention place s dans le plan yz. Alors
    cross(s, n) pointe vers +x et définit l'équinoxe J2000, ce qui permet une
    comparaison directe à la longitude du périhélie depuis l'équinoxe mobile
    de La2004.
    """
    n = np.asarray(normal, dtype=float)
    n = n / np.linalg.norm(n)
    x = np.array([1.0, 0.0, 0.0])
    if abs(float(np.dot(x, n))) > 0.95:
        x = np.array([0.0, 1.0, 0.0])
    e1 = x - np.dot(x, n) * n
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(n, e1)
    eps = math.radians(obliquity_deg)
    spin = math.cos(eps) * n + math.sin(eps) * e2
    return spin / np.linalg.norm(spin)


def integrate_spin_batch(
    frames: list[pd.DataFrame],
    alpha_arcsec_per_year: float | np.ndarray,
    substeps_per_orbital_sample: int = 10,
    obliquity_deg: float = DEFAULT_OBLIQUITY_DEG,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Intègre plusieurs scénarios partageant la même grille temporelle.

    L'équation moyenne est la forme vectorielle du problème de Colombo :

        ds/dt = - alpha / (1-e^2)^(3/2) (s.n) (n x s)

    Les séries ORI-C vont vers le passé avec ``elapsed_years`` croissant ; la
    dérivée est donc renversée lors de l'intégration en temps écoulé positif.
    Un RK4 à sous-pas fixes est employé, avec interpolation linéaire de n(t) et
    e(t) entre deux sorties N-corps.
    """
    if not frames:
        raise ValueError("au moins une série orbitale est requise")
    sample_times = frames[0]["elapsed_years"].to_numpy(dtype=float)
    if len(sample_times) < 2:
        raise ValueError("au moins deux échantillons temporels sont requis")
    dt_samples = np.diff(sample_times)
    if not np.allclose(dt_samples, dt_samples[0], rtol=0.0, atol=1e-9):
        raise ValueError("la grille orbitale doit être régulière")
    for frame in frames[1:]:
        times = frame["elapsed_years"].to_numpy(dtype=float)
        if len(times) != len(sample_times) or not np.allclose(times, sample_times, rtol=0.0, atol=1e-9):
            raise ValueError("tous les scénarios doivent partager la même grille")

    scenario_count = len(frames)
    sample_count = len(sample_times)
    normals = np.stack([orbital_normals(frame) for frame in frames])
    eccentricities = np.stack([frame["eccentricity"].to_numpy(dtype=float) for frame in frames])

    alpha = np.asarray(alpha_arcsec_per_year, dtype=float)
    if alpha.ndim == 0:
        alpha = np.full(scenario_count, float(alpha))
    if alpha.shape != (scenario_count,):
        raise ValueError("alpha doit être scalaire ou avoir une valeur par scénario")
    alpha_rad = alpha * ARCSEC_TO_RAD

    spin = np.stack([initial_spin(normals[k, 0], obliquity_deg) for k in range(scenario_count)])
    spins = np.empty((scenario_count, sample_count, 3), dtype=float)
    spins[:, 0, :] = spin
    substeps = int(substeps_per_orbital_sample)
    if substeps < 1:
        raise ValueError("substeps_per_orbital_sample doit être >= 1")
    dt = float(dt_samples[0]) / substeps

    for index in range(sample_count - 1):
        n0 = normals[:, index, :]
        n1 = normals[:, index + 1, :]
        e0 = eccentricities[:, index]
        e1 = eccentricities[:, index + 1]

        def derivative(vectors: np.ndarray, fraction: float) -> np.ndarray:
            n = (1.0 - fraction) * n0 + fraction * n1
            n /= np.linalg.norm(n, axis=1)[:, None]
            e = (1.0 - fraction) * e0 + fraction * e1
            factor = alpha_rad * np.power(1.0 - e * e, -1.5) * np.sum(vectors * n, axis=1)
            # elapsed_years augmente vers le passé : signe inverse de ds/dt physique.
            return factor[:, None] * np.cross(n, vectors)

        for substep in range(substeps):
            f0 = substep / substeps
            fm = (substep + 0.5) / substeps
            f1 = (substep + 1.0) / substeps
            k1 = derivative(spin, f0)
            k2 = derivative(spin + 0.5 * dt * k1, fm)
            k3 = derivative(spin + 0.5 * dt * k2, fm)
            k4 = derivative(spin + dt * k3, f1)
            spin = spin + dt * (k1 + 2.0 * k2 + 2.0 * k3 + k4) / 6.0
            spin /= np.linalg.norm(spin, axis=1)[:, None]
        spins[:, index + 1, :] = spin

    cos_eps = np.sum(spins * normals, axis=2)
    obliquity_deg_out = np.degrees(np.arccos(np.clip(cos_eps, -1.0, 1.0)))
    return obliquity_deg_out, spins, normals


def moving_perihelion_longitude(
    frame: pd.DataFrame,
    spins: np.ndarray,
    normals: np.ndarray | None = None,
) -> np.ndarray:
    """Longitude du périhélie depuis l'équinoxe mobile, en radians."""
    if normals is None:
        normals = orbital_normals(frame)
    peri = perihelion_directions(frame)
    equinox = np.cross(spins, normals)
    equinox /= np.linalg.norm(equinox, axis=1)[:, None]
    y = np.cross(normals, equinox)
    angle = np.arctan2(np.sum(peri * y, axis=1), np.sum(peri * equinox, axis=1))
    return np.mod(angle, 2.0 * np.pi)


def daily_mean_insolation(
    eccentricity: np.ndarray,
    long_peri_rad: np.ndarray,
    obliquity_deg: np.ndarray,
    latitude_deg: float = 65.0,
    solar_longitude_deg: float = 90.0,
    solar_constant_w_m2: float = 1361.0,
) -> np.ndarray:
    """Insolation journalière moyenne à latitude et longitude solaire fixes."""
    e = np.asarray(eccentricity, dtype=float)
    varpi = np.asarray(long_peri_rad, dtype=float)
    eps = np.radians(np.asarray(obliquity_deg, dtype=float))
    phi = math.radians(latitude_deg)
    lam = math.radians(solar_longitude_deg)
    declination = np.arcsin(np.sin(eps) * math.sin(lam))
    cos_h0 = -math.tan(phi) * np.tan(declination)
    h0 = np.arccos(np.clip(cos_h0, -1.0, 1.0))
    h0 = np.where(cos_h0 <= -1.0, np.pi, h0)
    h0 = np.where(cos_h0 >= 1.0, 0.0, h0)
    true_longitude_from_peri = lam - varpi
    r_over_a = (1.0 - e * e) / (1.0 + e * np.cos(true_longitude_from_peri))
    flux = solar_constant_w_m2 / np.square(r_over_a)
    geometry = (
        h0 * math.sin(phi) * np.sin(declination)
        + math.cos(phi) * np.cos(declination) * np.sin(h0)
    )
    return np.maximum(flux * geometry / np.pi, 0.0)


def dominant_period_years(values: np.ndarray, sample_step_years: float, low: float, high: float) -> float:
    signal = np.asarray(values, dtype=float) - float(np.mean(values))
    spectrum = np.abs(np.fft.rfft(signal)) ** 2
    frequencies = np.fft.rfftfreq(len(signal), d=sample_step_years)
    valid = frequencies > 0.0
    periods = np.full_like(frequencies, np.inf, dtype=float)
    periods[valid] = 1.0 / frequencies[valid]
    band = valid & (periods >= low) & (periods <= high)
    if not np.any(band):
        return float("nan")
    indices = np.flatnonzero(band)
    return float(periods[indices[np.argmax(spectrum[band])]])


def circular_difference(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.angle(np.exp(1j * (np.asarray(a) - np.asarray(b))))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_results_manifest(result_dir: Path) -> None:
    entries = []
    for path in sorted(result_dir.rglob("*")):
        if not path.is_file() or path.name == "RESULTATS.sha256":
            continue
        entries.append((sha256(path), path.relative_to(result_dir).as_posix()))
    (result_dir / "RESULTATS.sha256").write_text(
        "".join(f"{digest}  {relative}\n" for digest, relative in entries),
        encoding="utf-8",
        newline="\n",
    )


def verify_results_manifest(result_dir: Path) -> None:
    manifest = result_dir / "RESULTATS.sha256"
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, relative = line.split("  ", 1)
        path = result_dir / relative
        if not path.is_file() or sha256(path) != digest:
            raise RuntimeError(f"résultat non reproductible ou modifié : {relative}")
