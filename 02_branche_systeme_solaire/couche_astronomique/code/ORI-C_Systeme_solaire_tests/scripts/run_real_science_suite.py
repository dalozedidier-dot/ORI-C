#!/usr/bin/env python3
"""Run the pre-registered long N-body validation matrix in parallel."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import shutil
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from oric_solar_history.backends.rebound_backend import (
    _build_simulation,
    _energy_and_angmom,
    run_rebound,
)


SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _versions() -> dict[str, str]:
    names = [
        "numpy",
        "pandas",
        "scipy",
        "PyYAML",
        "rebound",
        "reboundx",
    ]
    result: dict[str, str] = {}
    for name in names:
        try:
            result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result[name] = "not-installed"
    return result


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_csv_gz(frame: pd.DataFrame, path: Path) -> None:
    frame.to_csv(
        path,
        index=False,
        float_format="%.17g",
        compression={"method": "gzip", "compresslevel": 9, "mtime": 0},
    )


def _rebound_config(job: dict[str, Any]) -> dict[str, Any]:
    keys = {
        "integrator",
        "timestep_years",
        "exact_finish_time",
        "initial_conditions",
        "initial_conditions_path",
        "time_direction",
        "general_relativity",
        "speed_of_light_au_per_year",
        "safe_mode",
        "corrector",
        "coordinates",
        "kernel",
        "ejection_radius_au",
        "include_bodies",
    }
    return {key: job[key] for key in keys if key in job}


def _save_nbody_outputs(
    frame: pd.DataFrame,
    job: dict[str, Any],
    target_dir: Path,
    computation_seconds: float,
) -> dict[str, Any]:
    earth = frame.loc[frame["body"] == "Earth"].sort_values("elapsed_years").reset_index(drop=True)
    if earth.empty:
        raise RuntimeError("La Terre est absente du résultat")

    diagnostics = (
        frame.groupby(["time_years", "elapsed_years"], sort=False)
        .agg(
            integration_time_years=("integration_time_years", "first"),
            energy_rel_error=("energy_rel_error", "first"),
            angmom_rel_error=("angmom_rel_error", "first"),
            all_bodies_bound=("bound", "all"),
        )
        .reset_index()
        .sort_values("elapsed_years")
    )
    body_summary = (
        frame.groupby("body", sort=False)
        .agg(
            rows=("body", "size"),
            all_bound=("bound", "all"),
            a_min_au=("a_au", "min"),
            a_max_au=("a_au", "max"),
            eccentricity_min=("eccentricity", "min"),
            eccentricity_max=("eccentricity", "max"),
            inclination_min_rad=("inclination_rad", "min"),
            inclination_max_rad=("inclination_rad", "max"),
        )
        .reset_index()
    )
    sample_step = float(job.get("all_body_sample_step_years", 100_000.0))
    elapsed = frame["elapsed_years"].to_numpy(dtype=float)
    keep = np.isclose(np.remainder(elapsed, sample_step), 0.0, atol=1e-7)
    keep |= np.isclose(elapsed, float(job["duration_years"]), atol=1e-7)
    orbital_sample = frame.loc[keep].reset_index(drop=True)

    _write_csv_gz(earth, target_dir / "earth.csv.gz")
    _write_csv_gz(diagnostics, target_dir / "diagnostics.csv.gz")
    _write_csv_gz(orbital_sample, target_dir / "orbital_sample.csv.gz")
    body_summary.to_csv(
        target_dir / "body_summary.csv",
        index=False,
        float_format="%.17g",
    )

    summary = {
        "kind": "nbody",
        "row_count": int(len(frame)),
        "output_count": int(len(diagnostics)),
        "body_count": int(frame["body"].nunique()),
        "all_bodies_bound": bool(frame["bound"].all()),
        "max_abs_energy_rel_error": float(diagnostics["energy_rel_error"].abs().max()),
        "max_abs_angmom_rel_error": float(diagnostics["angmom_rel_error"].abs().max()),
        "max_abs_output_time_error_years": float(
            (diagnostics["integration_time_years"] - diagnostics["time_years"]).abs().max()
        ),
        "earth_initial_eccentricity": float(earth.iloc[0]["eccentricity"]),
        "earth_eccentricity_mean": float(earth["eccentricity"].mean()),
        "earth_eccentricity_std": float(earth["eccentricity"].std(ddof=0)),
        "earth_eccentricity_min": float(earth["eccentricity"].min()),
        "earth_eccentricity_max": float(earth["eccentricity"].max()),
        "completed_years": float(diagnostics["elapsed_years"].max()),
        "computation_seconds": float(computation_seconds),
    }
    return summary


def _particle_state(sim: Any, names: list[str]) -> dict[str, np.ndarray]:
    result: dict[str, np.ndarray] = {}
    for name in ["Sun", *names]:
        particle = sim.particles[name]
        result[name] = np.array(
            [
                particle.x,
                particle.y,
                particle.z,
                particle.vx,
                particle.vy,
                particle.vz,
            ],
            dtype=float,
        )
    return result


def _run_roundtrip(
    job: dict[str, Any],
    target_dir: Path,
) -> dict[str, Any]:
    rng = np.random.default_rng(int(job["seed"]))
    runtime, included = _build_simulation(
        _rebound_config(job),
        {"name": job["name"], "modifications": job.get("modifications", {})},
        rng,
        float(job.get("initial_angle_sigma_rad", 0.0)),
    )
    sim = runtime.sim
    sim.synchronize()
    initial_state = _particle_state(sim, included)
    energy_initial, angmom_initial = _energy_and_angmom(runtime)
    duration = float(job["duration_years"])
    direction = -1.0 if str(job.get("time_direction")) == "backward" else 1.0
    sim.integrate(direction * duration, exact_finish_time=0)
    sim.synchronize()
    energy_turn, angmom_turn = _energy_and_angmom(runtime)

    sim.dt = -float(sim.dt)
    whfast = getattr(sim, "ri_whfast", None)
    if whfast is not None:
        try:
            whfast.recalculate_coordinates_this_timestep = 1
        except (AttributeError, TypeError, ValueError):
            pass
    sim.integrate(0.0, exact_finish_time=0)
    sim.synchronize()
    final_state = _particle_state(sim, included)
    energy_final, angmom_final = _energy_and_angmom(runtime)

    rows: list[dict[str, Any]] = []
    for name in included:
        initial_relative = initial_state[name] - initial_state["Sun"]
        final_relative = final_state[name] - final_state["Sun"]
        delta = final_relative - initial_relative
        position_scale = max(float(np.linalg.norm(initial_relative[:3])), 1e-30)
        velocity_scale = max(float(np.linalg.norm(initial_relative[3:])), 1e-30)
        position_relative_error = float(np.linalg.norm(delta[:3]) / position_scale)
        velocity_relative_error = float(np.linalg.norm(delta[3:]) / velocity_scale)
        rows.append(
            {
                "body": name,
                "position_absolute_error_au": float(np.linalg.norm(delta[:3])),
                "velocity_absolute_error_au_per_year": float(np.linalg.norm(delta[3:])),
                "position_relative_error": position_relative_error,
                "velocity_relative_error": velocity_relative_error,
                "combined_relative_state_error": float(
                    np.hypot(position_relative_error, velocity_relative_error)
                ),
            }
        )
    errors = pd.DataFrame(rows)
    errors.to_csv(
        target_dir / "roundtrip_errors.csv",
        index=False,
        float_format="%.17g",
    )
    energy_scale = abs(energy_initial)
    angmom_scale = abs(angmom_initial)
    return {
        "kind": "roundtrip",
        "all_bodies_bound": True,
        "completed_years": duration,
        "max_combined_relative_state_error": float(errors["combined_relative_state_error"].max()),
        "earth_combined_relative_state_error": float(
            errors.loc[errors["body"] == "Earth", "combined_relative_state_error"].iloc[0]
        ),
        "turn_abs_energy_rel_error": float(abs(energy_turn - energy_initial) / energy_scale),
        "return_abs_energy_rel_error": float(abs(energy_final - energy_initial) / energy_scale),
        "turn_abs_angmom_rel_error": float(abs(angmom_turn - angmom_initial) / angmom_scale),
        "return_abs_angmom_rel_error": float(abs(angmom_final - angmom_initial) / angmom_scale),
    }


def _run_one(job: dict[str, Any], output_root: str) -> dict[str, Any]:
    started = time.perf_counter()
    root = Path(output_root)
    final_dir = root / job["name"]
    temporary_dir = root / f".{job['name']}.tmp-{os.getpid()}"
    if temporary_dir.exists():
        shutil.rmtree(temporary_dir)
    temporary_dir.mkdir(parents=True)
    try:
        if job.get("kind", "nbody") == "roundtrip":
            summary = _run_roundtrip(job, temporary_dir)
        else:
            frame = run_rebound(
                duration_years=float(job["duration_years"]),
                output_step_years=float(job["output_step_years"]),
                scenario={
                    "name": job["name"],
                    "modifications": job.get("modifications", {}),
                },
                seed=int(job["seed"]),
                rebound_cfg=_rebound_config(job),
                realization=int(job.get("realization", 0)),
                initial_angle_sigma_rad=float(job.get("initial_angle_sigma_rad", 0.0)),
            )
            summary = _save_nbody_outputs(
                frame,
                job,
                temporary_dir,
                time.perf_counter() - started,
            )
        summary["computation_seconds"] = float(time.perf_counter() - started)
        metadata = {
            "job": job,
            "summary": summary,
            "versions": _versions(),
            "python": platform.python_version(),
            "platform": platform.platform(),
        }
        _write_json(temporary_dir / "metadata.json", metadata)
        manifest = {
            path.name: {
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
            for path in sorted(temporary_dir.iterdir())
            if path.is_file()
        }
        _write_json(temporary_dir / "job_manifest.json", manifest)
        if final_dir.exists():
            raise FileExistsError(f"Sortie déjà présente: {final_dir}")
        temporary_dir.rename(final_dir)
        return {"name": job["name"], "ok": True, "summary": summary}
    except Exception as exc:
        failure = {
            "name": job["name"],
            "ok": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
        _write_json(temporary_dir / "failure.json", failure)
        return failure


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def _resolve_jobs(config: dict[str, Any]) -> list[dict[str, Any]]:
    defaults = dict(config["defaults"])
    seed = int(config["suite"]["seed"])
    resolved: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw_job in config["jobs"]:
        job = {**defaults, **raw_job}
        name = str(job["name"])
        if not SAFE_NAME.fullmatch(name):
            raise ValueError(f"Nom de job non sûr: {name}")
        if name in seen:
            raise ValueError(f"Nom de job dupliqué: {name}")
        seen.add(name)
        job["name"] = name
        job["seed"] = int(job.get("seed", seed))
        resolved.append(job)
    return resolved


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/real_science_max.yaml"),
    )
    parser.add_argument("--workers", type=int)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--select", action="append", default=[])
    args = parser.parse_args()
    if args.resume and args.overwrite:
        raise SystemExit("--resume et --overwrite sont incompatibles")

    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    jobs = _resolve_jobs(config)
    if args.select:
        selected = set(args.select)
        jobs = [job for job in jobs if job["name"] in selected]
        missing = selected - {job["name"] for job in jobs}
        if missing:
            raise SystemExit(f"Jobs inconnus: {sorted(missing)}")

    output_root = Path(config["suite"]["output_dir"]).resolve()
    if output_root.exists() and args.overwrite:
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    if output_root.exists() and not args.resume and any(output_root.iterdir()):
        raise SystemExit(f"{output_root} n'est pas vide. Utilisez --resume ou --overwrite.")

    pending: list[dict[str, Any]] = []
    skipped: list[str] = []
    existing_results: list[dict[str, Any]] = []
    for job in jobs:
        manifest = output_root / job["name"] / "job_manifest.json"
        if args.resume and manifest.is_file():
            skipped.append(job["name"])
            metadata_path = output_root / job["name"] / "metadata.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            existing_results.append(
                {
                    "name": job["name"],
                    "ok": True,
                    "summary": metadata["summary"],
                    "reused_existing_result": True,
                }
            )
        else:
            pending.append(job)

    suite_metadata = {
        "config": str(args.config.resolve()),
        "git_commit_before_run": _git_commit(),
        "resolved_jobs": jobs,
        "acceptance": config["acceptance"],
        "versions": _versions(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
    }
    _write_json(output_root / "suite_metadata.json", suite_metadata)
    (output_root / "resolved_config.yaml").write_text(
        yaml.safe_dump(config, sort_keys=False),
        encoding="utf-8",
    )
    if skipped:
        print(json.dumps({"skipped": skipped}, ensure_ascii=False), flush=True)

    workers = int(
        args.workers
        if args.workers is not None
        else config["suite"].get("max_workers", os.cpu_count() or 1)
    )
    workers = max(1, min(workers, len(pending) or 1))
    print(
        json.dumps(
            {
                "event": "suite_start",
                "pending": len(pending),
                "workers": workers,
                "output": str(output_root),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    results: list[dict[str, Any]] = existing_results
    if pending:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(_run_one, job, str(output_root)): job["name"] for job in pending
            }
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                print(
                    json.dumps(
                        {"event": "job_complete", **result},
                        ensure_ascii=False,
                    ),
                    flush=True,
                )
    results.sort(key=lambda item: item["name"])
    _write_json(output_root / "execution_results.json", results)
    failures = [result for result in results if not result["ok"]]
    print(
        json.dumps(
            {
                "event": "suite_complete",
                "completed": len(results) - len(failures),
                "failed": len(failures),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
