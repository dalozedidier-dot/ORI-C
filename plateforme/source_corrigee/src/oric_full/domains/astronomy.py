from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import re
import subprocess
import sys

import numpy as np
import pandas as pd
from scipy.signal import periodogram


G_AU3_YR2_MSUN = 4.0 * np.pi**2


@dataclass(frozen=True)
class AstronomyAnalysis:
    metrics: dict[str, float]
    details: dict


def spectral_analysis(frame: pd.DataFrame, time_col: str = "time") -> AstronomyAnalysis:
    f = frame.sort_values(time_col)
    t = pd.to_numeric(f[time_col], errors="coerce").to_numpy()
    columns = [column for column in ["eccentricity", "obliquity", "precession"] if column in f.columns]
    if len(t) < 8 or not columns:
        return AstronomyAnalysis({"spectral_columns": 0.0}, {"reason": "Données insuffisantes"})
    dt = float(np.median(np.diff(t)))
    if not np.isfinite(dt) or dt <= 0:
        return AstronomyAnalysis({"spectral_columns": 0.0}, {"reason": "Pas de temps invalide"})
    details: dict[str, dict[str, float]] = {}
    dominant_periods: list[float] = []
    for column in columns:
        y = pd.to_numeric(f[column], errors="coerce").interpolate().bfill().ffill().to_numpy()
        freq, power = periodogram(y - np.mean(y), fs=1.0 / dt)
        valid = freq > 0
        if np.any(valid):
            idx = int(np.argmax(power[valid]))
            period = float(1.0 / freq[valid][idx])
            dominant_periods.append(period)
            # Période secondaire : second maximum local du périodogramme,
            # hors du voisinage du pic dominant. Le WP-A5.4 demande la bande
            # de 2,4 Ma en plus de celle de 405 ka.
            puissances = power[valid].copy()
            frequences = freq[valid]
            voisinage = np.abs(frequences - frequences[idx]) <= 0.25 * frequences[idx]
            puissances[voisinage] = -np.inf
            secondaire = float("nan")
            if np.any(np.isfinite(puissances)):
                idx2 = int(np.argmax(puissances))
                if np.isfinite(puissances[idx2]) and frequences[idx2] > 0:
                    secondaire = float(1.0 / frequences[idx2])
            details[column] = {
                "dominant_period": period,
                "peak_power": float(power[valid][idx]),
                "secondary_period": secondaire,
            }
    return AstronomyAnalysis(
        {
            "spectral_columns": float(len(columns)),
            "median_dominant_period": float(np.median(dominant_periods)) if dominant_periods else float("nan"),
        },
        details,
    )


def compare_reference(simulated: pd.DataFrame, reference: pd.DataFrame) -> AstronomyAnalysis:
    metrics: dict[str, float] = {}
    details: dict[str, dict[str, float]] = {}
    if {"time", "observable", "value"} <= set(reference.columns):
        for observable, ref in reference.groupby("observable"):
            if observable not in simulated.columns:
                continue
            sim = simulated[["time", observable]].dropna().sort_values("time")
            ref = ref.dropna(subset=["time", "value"]).sort_values("time")
            if sim.empty or ref.empty:
                continue
            pred = np.interp(ref["time"].to_numpy(), sim["time"].to_numpy(), sim[observable].to_numpy())
            residual = pred - ref["value"].to_numpy(dtype=float)
            metrics[f"rmse_{observable}"] = float(np.sqrt(np.mean(residual**2)))
            details[str(observable)] = {"n": float(len(ref)), "bias": float(np.mean(residual))}
    metrics["observables_compared"] = float(sum(key.startswith("rmse_") for key in metrics))

    # Horizon de divergence, WP-A2.9. La colonne `uncertainty` de la table de
    # référence porte l'étendue entre solutions également admissibles. Au-delà
    # du seuil, elles sont décorrélées et toute comparaison perd son sens.
    metrics["divergence_horizon_myr"] = float("nan")
    if {"time", "value", "uncertainty"} <= set(reference.columns):
        ref = reference.dropna(subset=["time", "value", "uncertainty"])
        if not ref.empty:
            temps = np.abs(pd.to_numeric(ref["time"], errors="coerce").to_numpy())
            valeur = pd.to_numeric(ref["value"], errors="coerce").to_numpy()
            ecart = pd.to_numeric(ref["uncertainty"], errors="coerce").to_numpy()
            relative = np.divide(ecart, np.maximum(np.abs(valeur), 1e-12))
            ordre = np.argsort(temps)
            depasse = np.flatnonzero(relative[ordre] > 0.01)
            metrics["divergence_horizon_myr"] = (
                float(temps[ordre][depasse[0]] / 1000.0) if len(depasse)
                else float(temps.max() / 1000.0)
            )
    return AstronomyAnalysis(metrics, details)


def initial_condition_audit(frame: pd.DataFrame) -> AstronomyAnalysis:
    required = {"body", "x", "y", "z", "vx", "vy", "vz", "mass"}
    missing = sorted(required - set(frame.columns))
    if missing:
        return AstronomyAnalysis({"valid": 0.0}, {"missing_columns": missing})
    numeric = frame[["x", "y", "z", "vx", "vy", "vz", "mass"]].apply(pd.to_numeric, errors="coerce")
    duplicate_bodies = int(frame["body"].astype(str).duplicated().sum())
    finite_fraction = float(np.isfinite(numeric.to_numpy()).mean())
    positive_mass_fraction = float((numeric["mass"] > 0).mean())
    total_mass = float(numeric["mass"].sum())
    if total_mass > 0:
        barycenter = np.average(numeric[["x", "y", "z"]].to_numpy(), axis=0, weights=numeric["mass"])
        momentum = (numeric[["vx", "vy", "vz"]].to_numpy() * numeric["mass"].to_numpy()[:, None]).sum(axis=0)
    else:
        barycenter = np.full(3, np.nan)
        momentum = np.full(3, np.nan)
    valid = float(not missing and duplicate_bodies == 0 and finite_fraction == 1.0 and positive_mass_fraction == 1.0)
    return AstronomyAnalysis(
        {
            "valid": valid,
            "finite_fraction": finite_fraction,
            "positive_mass_fraction": positive_mass_fraction,
            "duplicate_bodies": float(duplicate_bodies),
            "barycenter_norm": float(np.linalg.norm(barycenter)),
            "momentum_norm": float(np.linalg.norm(momentum)),
        },
        {"barycenter": barycenter.tolist(), "momentum": momentum.tolist(), "body_count": len(frame)},
    )


def _prepare_system(frame: pd.DataFrame) -> tuple[list[str], np.ndarray, np.ndarray, np.ndarray]:
    columns = ["x", "y", "z", "vx", "vy", "vz", "mass"]
    f = frame[["body", *columns]].copy()
    for column in columns:
        f[column] = pd.to_numeric(f[column], errors="raise")
    names = f["body"].astype(str).tolist()
    positions = f[["x", "y", "z"]].to_numpy(dtype=float)
    velocities = f[["vx", "vy", "vz"]].to_numpy(dtype=float)
    masses = f["mass"].to_numpy(dtype=float)
    # Les tables planétaires omettent souvent l'étoile centrale. On l'ajoute explicitement.
    if not np.any(masses >= 0.1):
        names = ["Sun", *names]
        positions = np.vstack([np.zeros(3), positions])
        velocities = np.vstack([np.zeros(3), velocities])
        masses = np.concatenate([[1.0], masses])
        velocities[0] = -np.sum(velocities[1:] * masses[1:, None], axis=0) / masses[0]
    return names, positions, velocities, masses


def _accelerations(positions: np.ndarray, masses: np.ndarray, softening: float = 1e-12) -> np.ndarray:
    n = len(masses)
    acc = np.zeros_like(positions)
    for i in range(n):
        delta = positions - positions[i]
        dist2 = np.sum(delta * delta, axis=1) + softening**2
        dist2[i] = np.inf
        inv_r3 = dist2 ** (-1.5)
        acc[i] = G_AU3_YR2_MSUN * np.sum(delta * (masses * inv_r3)[:, None], axis=0)
    return acc


def _energy(positions: np.ndarray, velocities: np.ndarray, masses: np.ndarray) -> float:
    kinetic = 0.5 * float(np.sum(masses[:, None] * velocities**2))
    potential = 0.0
    for i in range(len(masses)):
        for j in range(i + 1, len(masses)):
            distance = max(float(np.linalg.norm(positions[j] - positions[i])), 1e-15)
            potential -= G_AU3_YR2_MSUN * masses[i] * masses[j] / distance
    return kinetic + potential


def integrate_nbody(
    frame: pd.DataFrame,
    *,
    years: float = 2.0,
    steps: int = 2000,
) -> dict[str, object]:
    if steps < 2 or years <= 0:
        raise ValueError("Durée et nombre de pas invalides")
    names, pos, vel, masses = _prepare_system(frame)
    dt = years / steps
    initial_energy = _energy(pos, vel, masses)
    trajectory = np.empty((steps + 1, len(names), 3), dtype=float)
    trajectory[0] = pos
    acc = _accelerations(pos, masses)
    for index in range(1, steps + 1):
        vel_half = vel + 0.5 * dt * acc
        pos = pos + dt * vel_half
        acc_new = _accelerations(pos, masses)
        vel = vel_half + 0.5 * dt * acc_new
        acc = acc_new
        trajectory[index] = pos
    final_energy = _energy(pos, vel, masses)
    drift = abs(final_energy - initial_energy) / max(abs(initial_energy), 1e-30)
    return {
        "names": names,
        "times": np.linspace(0.0, years, steps + 1),
        "trajectory": trajectory,
        "final_velocity": vel,
        "energy_drift": float(drift),
    }


def reproducibility_diagnostic(frame: pd.DataFrame) -> AstronomyAnalysis:
    first = integrate_nbody(frame)
    second = integrate_nbody(frame)
    difference = float(np.max(np.abs(first["trajectory"] - second["trajectory"])))
    return AstronomyAnalysis(
        {
            "deterministic_max_difference": difference,
            "energy_drift": float(first["energy_drift"]),
            "body_count": float(len(first["names"])),
        },
        {"duration_years": float(first["times"][-1]), "steps": len(first["times"]) - 1},
    )


def physics_sensitivity(frame: pd.DataFrame, seed: int = 0) -> AstronomyAnalysis:
    baseline = integrate_nbody(frame, years=1.0, steps=1000)
    perturbed = frame.copy()
    rng = np.random.default_rng(seed)
    perturbed["mass"] = pd.to_numeric(perturbed["mass"], errors="raise") * (1.0 + rng.normal(0, 1e-4, len(perturbed)))
    altered = integrate_nbody(perturbed, years=1.0, steps=1000)
    displacement = np.linalg.norm(baseline["trajectory"][-1] - altered["trajectory"][-1], axis=1)
    return AstronomyAnalysis(
        {
            "median_final_displacement": float(np.median(displacement)),
            "max_final_displacement": float(np.max(displacement)),
            "baseline_energy_drift": float(baseline["energy_drift"]),
        },
        {"body_displacements": dict(zip(baseline["names"], displacement.tolist()))},
    )


def causal_ablation(frame: pd.DataFrame) -> AstronomyAnalysis:
    baseline = integrate_nbody(frame, years=1.0, steps=1000)
    f = frame.copy()
    masses = pd.to_numeric(f["mass"], errors="raise")
    remove_index = int(masses.idxmax()) if len(f) > 1 else int(f.index[0])
    removed_body = str(f.loc[remove_index, "body"])
    ablated_frame = f.drop(index=remove_index)
    if ablated_frame.empty:
        return AstronomyAnalysis({"ablation_effect": float("nan")}, {"reason": "Un seul corps"})
    ablated = integrate_nbody(ablated_frame, years=1.0, steps=1000)
    common = [name for name in baseline["names"] if name in set(ablated["names"])]
    b_index = {name: i for i, name in enumerate(baseline["names"])}
    a_index = {name: i for i, name in enumerate(ablated["names"])}
    effects = {
        name: float(np.linalg.norm(baseline["trajectory"][-1, b_index[name]] - ablated["trajectory"][-1, a_index[name]]))
        for name in common
    }
    return AstronomyAnalysis(
        {
            "ablation_effect": float(np.median(list(effects.values()))) if effects else float("nan"),
            "max_ablation_effect": float(max(effects.values())) if effects else float("nan"),
        },
        {"removed_body": removed_body, "effects": effects},
    )


def run_existing_astronomy_suite(oric_root: Path, timeout: int = 900) -> AstronomyAnalysis:
    package = oric_root / "02_branche_systeme_solaire" / "couche_astronomique" / "code" / "ORI-C_Systeme_solaire_tests"
    if not package.exists():
        return AstronomyAnalysis({"returncode": -1.0}, {"reason": f"Paquet absent: {package}"})
    env = os.environ.copy()
    env["PYTHONPATH"] = str(package / "src") + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=package,
        env=env,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    def count(label: str) -> int:
        match = re.search(rf"(\d+) {label}", proc.stdout)
        return int(match.group(1)) if match else 0
    return AstronomyAnalysis(
        {
            "returncode": float(proc.returncode),
            "passed": float(count("passed")),
            "failed": float(count("failed")),
            "skipped": float(count("skipped")),
        },
        {"stdout": proc.stdout[-10000:], "stderr": proc.stderr[-10000:]},
    )
