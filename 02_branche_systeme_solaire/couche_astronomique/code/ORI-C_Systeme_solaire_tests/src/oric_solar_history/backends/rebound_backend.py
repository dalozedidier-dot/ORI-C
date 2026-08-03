from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ..catalog import apply_modifications, load_catalog


@dataclass(frozen=True)
class CartesianState:
    name: str
    mass_msun: float
    x_au: float
    y_au: float
    z_au: float
    vx_au_per_year: float
    vy_au_per_year: float
    vz_au_per_year: float


@dataclass
class SimulationRuntime:
    sim: Any
    reboundx_extras: Any | None = None
    relativistic_force: Any | None = None
    relativity_model: str = "none"

    def total_energy(self) -> float:
        energy = float(self.sim.energy())
        if self.reboundx_extras is not None and self.relativistic_force is not None:
            if self.relativity_model == "gr_potential":
                energy += float(
                    self.reboundx_extras.gr_potential_potential(self.relativistic_force)
                )
            elif self.relativity_model == "gr":
                energy = float(self.reboundx_extras.gr_hamiltonian(self.relativistic_force))
            elif self.relativity_model == "gr_full":
                energy = float(self.reboundx_extras.gr_full_hamiltonian(self.relativistic_force))
        return energy


def _require_rebound():
    try:
        import rebound  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Le backend REBOUND n'est pas installé. Lancez: pip install -e '.[nbody]'"
        ) from exc
    return rebound


def _require_reboundx():
    try:
        import reboundx  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "La relativité générale demande REBOUNDx. Installez l'extra scientifique compatible."
        ) from exc
    return reboundx


def _energy_and_angmom(runtime: SimulationRuntime) -> tuple[float, float]:
    angular_momentum = runtime.sim.angular_momentum()
    norm = math.sqrt(angular_momentum.x**2 + angular_momentum.y**2 + angular_momentum.z**2)
    return runtime.total_energy(), float(norm)


def _default_horizons_path() -> Path:
    packaged = Path(__file__).resolve().parents[1] / "data" / "horizons_j2000_de441.csv"
    if packaged.exists():
        return packaged
    return Path(__file__).resolve().parents[3] / "data" / "horizons_j2000_de441.csv"


def _load_cartesian_states(path: str | Path | None = None) -> dict[str, CartesianState]:
    state_path = Path(path) if path is not None else _default_horizons_path()
    if not state_path.is_file():
        raise FileNotFoundError(f"Vecteurs Horizons introuvables: {state_path}")
    frame = pd.read_csv(state_path)
    required = {
        "name",
        "mass_msun",
        "x_au",
        "y_au",
        "z_au",
        "vx_au_per_year",
        "vy_au_per_year",
        "vz_au_per_year",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Colonnes Horizons manquantes: {sorted(missing)}")
    result: dict[str, CartesianState] = {}
    for row in frame.to_dict(orient="records"):
        state = CartesianState(
            name=str(row["name"]),
            mass_msun=float(row["mass_msun"]),
            x_au=float(row["x_au"]),
            y_au=float(row["y_au"]),
            z_au=float(row["z_au"]),
            vx_au_per_year=float(row["vx_au_per_year"]),
            vy_au_per_year=float(row["vy_au_per_year"]),
            vz_au_per_year=float(row["vz_au_per_year"]),
        )
        result[state.name] = state
    if "Sun" not in result:
        raise ValueError("Le catalogue Horizons doit contenir le Soleil")
    return result


def _add_named_particle(sim: Any, name: str, **kwargs: Any) -> None:
    try:
        sim.add(name=name, **kwargs)
    except TypeError:
        # REBOUND 4 uses ``hash`` while REBOUND 5 introduced ``name``.
        sim.add(hash=name, **kwargs)


def _configure_whfast(sim: Any, rebound_cfg: dict[str, Any]) -> None:
    options = {
        "safe_mode": int(rebound_cfg.get("safe_mode", 0)),
        "corrector": int(rebound_cfg.get("corrector", 11)),
        "kernel": str(rebound_cfg.get("kernel", "default")),
        "coordinates": str(rebound_cfg.get("coordinates", "jacobi")),
    }
    configured = False
    legacy = getattr(sim, "ri_whfast", None)
    if legacy is not None:
        for key, value in options.items():
            try:
                setattr(legacy, key, value)
            except (AttributeError, TypeError, ValueError):
                pass
        configured = True
    if not configured:
        active = sim.integrator
        for key, value in options.items():
            try:
                setattr(active, key, value)
            except (AttributeError, TypeError, ValueError):
                pass


def _orbit_from_state(
    rebound: Any,
    sun_state: CartesianState,
    body_state: CartesianState,
):
    temporary = rebound.Simulation()
    temporary.units = ("yr", "AU", "Msun")
    temporary.add(m=sun_state.mass_msun)
    temporary.add(
        m=body_state.mass_msun,
        x=body_state.x_au - sun_state.x_au,
        y=body_state.y_au - sun_state.y_au,
        z=body_state.z_au - sun_state.z_au,
        vx=body_state.vx_au_per_year - sun_state.vx_au_per_year,
        vy=body_state.vy_au_per_year - sun_state.vy_au_per_year,
        vz=body_state.vz_au_per_year - sun_state.vz_au_per_year,
    )
    return temporary.particles[1].orbit(primary=temporary.particles[0])


def _build_from_horizons(
    sim: Any,
    rebound: Any,
    rebound_cfg: dict[str, Any],
    scenario: dict[str, Any],
    rng: np.random.Generator,
    initial_angle_sigma_rad: float,
) -> list[str]:
    states = _load_cartesian_states(rebound_cfg.get("initial_conditions_path"))
    sun_state = states["Sun"]
    _add_named_particle(
        sim,
        "Sun",
        m=sun_state.mass_msun,
        x=sun_state.x_au,
        y=sun_state.y_au,
        z=sun_state.z_au,
        vx=sun_state.vx_au_per_year,
        vy=sun_state.vy_au_per_year,
        vz=sun_state.vz_au_per_year,
    )
    sun = sim.particles[0]
    included = list(
        rebound_cfg.get(
            "include_bodies",
            rebound_cfg.get("include_planets", [name for name in states if name != "Sun"]),
        )
    )
    modifications = scenario.get("modifications", {})
    unknown = set(modifications) - set(states)
    if unknown:
        raise KeyError(f"Corps Horizons inconnu: {sorted(unknown)}")

    for name in included:
        if name not in states:
            raise KeyError(f"Corps absent des vecteurs Horizons: {name}")
        state = states[name]
        changes = modifications.get(name, {})
        mass = float(changes.get("mass_msun", state.mass_msun))
        mass *= float(changes.get("mass_scale", 1.0))
        a_scale = float(changes.get("a_scale", 1.0))
        e_scale = float(changes.get("e_scale", 1.0))
        explicit_e = changes.get("e")
        explicit_a = changes.get("a_au")
        angle_delta = (
            float(rng.normal(0.0, initial_angle_sigma_rad)) if initial_angle_sigma_rad > 0 else 0.0
        )
        requires_elements = (
            a_scale != 1.0
            or e_scale != 1.0
            or explicit_e is not None
            or explicit_a is not None
            or angle_delta != 0.0
        )
        if requires_elements:
            orbit = _orbit_from_state(rebound, sun_state, state)
            a = float(explicit_a) if explicit_a is not None else orbit.a * a_scale
            eccentricity = float(explicit_e) if explicit_e is not None else orbit.e * e_scale
            if mass <= 0 or a <= 0 or not (0 <= eccentricity < 1):
                raise ValueError(f"Paramètres non physiques pour {name}")
            _add_named_particle(
                sim,
                name,
                m=mass,
                a=a,
                e=eccentricity,
                inc=orbit.inc,
                Omega=orbit.Omega,
                omega=orbit.omega,
                M=orbit.M + angle_delta,
                primary=sun,
            )
        else:
            if mass <= 0:
                raise ValueError(f"Masse non physique pour {name}")
            _add_named_particle(
                sim,
                name,
                m=mass,
                x=state.x_au,
                y=state.y_au,
                z=state.z_au,
                vx=state.vx_au_per_year,
                vy=state.vy_au_per_year,
                vz=state.vz_au_per_year,
            )
    return included


def _build_from_elements(
    sim: Any,
    rebound_cfg: dict[str, Any],
    scenario: dict[str, Any],
    rng: np.random.Generator,
    initial_angle_sigma_rad: float,
) -> list[str]:
    catalog = apply_modifications(load_catalog(), scenario.get("modifications", {}))
    _add_named_particle(sim, "Sun", m=1.0)
    sun = sim.particles[0]
    included = list(
        rebound_cfg.get("include_bodies", rebound_cfg.get("include_planets", list(catalog)))
    )
    for name in included:
        p = catalog[name]
        inc = math.radians(p.inc_deg)
        Omega = math.radians(p.long_node_deg)
        omega = math.radians(p.long_peri_deg - p.long_node_deg)
        mean_anomaly = math.radians(p.mean_longitude_deg - p.long_peri_deg)
        if initial_angle_sigma_rad > 0:
            Omega += rng.normal(0.0, initial_angle_sigma_rad)
            omega += rng.normal(0.0, initial_angle_sigma_rad)
            mean_anomaly += rng.normal(0.0, initial_angle_sigma_rad)
        _add_named_particle(
            sim,
            name,
            m=p.mass_msun,
            a=p.a_au,
            e=p.e,
            inc=inc,
            Omega=Omega,
            omega=omega,
            M=mean_anomaly,
            primary=sun,
        )
    return included


def _build_simulation(
    rebound_cfg: dict[str, Any],
    scenario: dict[str, Any],
    rng: np.random.Generator,
    initial_angle_sigma_rad: float,
) -> tuple[SimulationRuntime, list[str]]:
    rebound = _require_rebound()
    sim = rebound.Simulation()
    sim.units = ("yr", "AU", "Msun")
    integrator_name = str(rebound_cfg.get("integrator", "whfast")).lower()
    sim.integrator = integrator_name
    direction_name = str(rebound_cfg.get("time_direction", "forward")).lower()
    direction = -1.0 if direction_name in {"backward", "past", "-1"} else 1.0
    sim.dt = direction * abs(float(rebound_cfg.get("timestep_years", 0.01)))
    if integrator_name == "whfast":
        _configure_whfast(sim, rebound_cfg)

    initial_conditions = str(rebound_cfg.get("initial_conditions", "elements_j2000")).lower()
    if initial_conditions in {"horizons", "horizons_j2000", "de441"}:
        included = _build_from_horizons(
            sim,
            rebound,
            rebound_cfg,
            scenario,
            rng,
            initial_angle_sigma_rad,
        )
    elif initial_conditions in {"elements", "elements_j2000", "approximate"}:
        included = _build_from_elements(
            sim,
            rebound_cfg,
            scenario,
            rng,
            initial_angle_sigma_rad,
        )
    else:
        raise ValueError(f"Conditions initiales inconnues: {initial_conditions}")

    sim.move_to_com()
    runtime = SimulationRuntime(sim=sim)
    relativity = str(rebound_cfg.get("general_relativity", "none")).lower()
    if relativity in {"gr_potential", "gr", "gr_full"}:
        reboundx = _require_reboundx()
        extras = reboundx.Extras(sim)
        force = extras.load_force(relativity)
        extras.add_force(force)
        force.params["c"] = float(rebound_cfg.get("speed_of_light_au_per_year", 63241.07708426628))
        runtime.reboundx_extras = extras
        runtime.relativistic_force = force
        runtime.relativity_model = relativity
    elif relativity not in {"none", "off", "false"}:
        raise ValueError("Relativité prise en charge: none, gr_potential, gr ou gr_full")
    return runtime, included


def run_rebound(
    duration_years: float,
    output_step_years: float,
    scenario: dict,
    seed: int,
    rebound_cfg: dict[str, Any],
    realization: int = 0,
    initial_angle_sigma_rad: float = 0.0,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 1009 * realization)
    runtime, included = _build_simulation(
        rebound_cfg,
        scenario,
        rng,
        initial_angle_sigma_rad,
    )
    sim = runtime.sim
    sim.synchronize()
    initial_energy, initial_angmom = _energy_and_angmom(runtime)
    ejection_radius = float(rebound_cfg.get("ejection_radius_au", 500.0))
    exact_finish = bool(rebound_cfg.get("exact_finish_time", False))
    direction_name = str(rebound_cfg.get("time_direction", "forward")).lower()
    direction = -1.0 if direction_name in {"backward", "past", "-1"} else 1.0
    elapsed_times = np.arange(
        0.0,
        duration_years + 0.5 * output_step_years,
        output_step_years,
    )
    times = direction * elapsed_times
    rows: list[dict[str, Any]] = []
    sun = sim.particles[0]

    for elapsed_t, requested_t in zip(elapsed_times, times, strict=True):
        sim.integrate(float(requested_t), exact_finish_time=int(exact_finish))
        sim.synchronize()
        actual_t = float(sim.t)
        energy, angmom = _energy_and_angmom(runtime)
        energy_err = (energy - initial_energy) / abs(initial_energy)
        angmom_err = (angmom - initial_angmom) / abs(initial_angmom)
        for name in included:
            particle = sim.particles[name]
            orbit = particle.orbit(primary=sun)
            radius = math.sqrt(particle.x**2 + particle.y**2 + particle.z**2)
            bound = bool(orbit.e < 1.0 and orbit.a > 0.0 and radius < ejection_radius)
            rows.append(
                {
                    "time_years": float(requested_t),
                    "elapsed_years": float(elapsed_t),
                    "integration_time_years": actual_t,
                    "body": name,
                    "a_au": float(orbit.a),
                    "eccentricity": float(orbit.e),
                    "inclination_rad": float(orbit.inc),
                    "long_node_rad": float(orbit.Omega % (2 * math.pi)),
                    "arg_peri_rad": float(orbit.omega % (2 * math.pi)),
                    "long_peri_rad": float((orbit.Omega + orbit.omega) % (2 * math.pi)),
                    "mean_longitude_rad": float(
                        (orbit.Omega + orbit.omega + orbit.M) % (2 * math.pi)
                    ),
                    "energy_rel_error": float(energy_err),
                    "angmom_rel_error": float(angmom_err),
                    "bound": bound,
                    "backend": "rebound",
                }
            )
        if not all(row["bound"] for row in rows[-len(included) :]):
            break

    return pd.DataFrame(rows)
