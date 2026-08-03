from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
import numpy as np
from scipy.integrate import solve_ivp


KineticName = Literal["monod", "hill", "contois", "haldane", "droop"]


@dataclass(frozen=True)
class ChemostatConfig:
    kinetic: KineticName = "monod"
    mu_max: float = 1.0
    ks: float = 0.5
    yield_coeff: float = 0.6
    dilution: float = 0.2
    resource_in: float = 5.0
    loss: float = 0.05
    hill_n: float = 2.0
    inhibition: float = 10.0
    quota_min: float = 0.1
    noise_sigma: float = 0.0
    pulse_times: tuple[float, ...] = ()
    pulse_fraction: float = 0.0


def growth_rate(resource: float, biomass: float, quota: float, cfg: ChemostatConfig) -> float:
    s = max(resource, 0.0)
    x = max(biomass, 1e-12)
    if cfg.kinetic == "monod":
        return cfg.mu_max * s / (cfg.ks + s)
    if cfg.kinetic == "hill":
        return cfg.mu_max * s**cfg.hill_n / (cfg.ks**cfg.hill_n + s**cfg.hill_n)
    if cfg.kinetic == "contois":
        return cfg.mu_max * s / (cfg.ks * x + s)
    if cfg.kinetic == "haldane":
        return cfg.mu_max * s / (cfg.ks + s + s * s / max(cfg.inhibition, 1e-12))
    if cfg.kinetic == "droop":
        return cfg.mu_max * max(1.0 - cfg.quota_min / max(quota, cfg.quota_min), 0.0)
    raise KeyError(cfg.kinetic)


def simulate_chemostat(
    cfg: ChemostatConfig,
    *,
    t_end: float = 100.0,
    dt: float = 0.05,
    initial: tuple[float, float, float] = (0.2, 5.0, 0.5),
    seed: int = 0,
) -> dict[str, np.ndarray]:
    times = np.arange(0.0, t_end + dt / 2, dt)

    def rhs(_t: float, y: np.ndarray) -> np.ndarray:
        x, s, q = y
        mu = growth_rate(s, x, q, cfg)
        dx = (mu - cfg.dilution - cfg.loss) * x
        ds = cfg.dilution * (cfg.resource_in - s) - mu * x / max(cfg.yield_coeff, 1e-12)
        dq = 0.0
        if cfg.kinetic == "droop":
            uptake = cfg.mu_max * s / (cfg.ks + s)
            dq = uptake - mu * q
        return np.array([dx, ds, dq], dtype=float)

    sol = solve_ivp(rhs, (0.0, t_end), np.asarray(initial, dtype=float), t_eval=times, rtol=1e-8, atol=1e-10)
    if not sol.success:
        raise RuntimeError(sol.message)
    x, s, q = sol.y

    if cfg.pulse_times and cfg.pulse_fraction > 0:
        # Approximation reproductible : appliquer les pertes sur les points de sortie puis poursuivre localement.
        for pulse in cfg.pulse_times:
            idx = int(np.argmin(np.abs(times - pulse)))
            x[idx:] *= max(1.0 - cfg.pulse_fraction, 0.0)

    if cfg.noise_sigma > 0:
        rng = np.random.default_rng(seed)
        x = np.maximum(x * np.exp(rng.normal(0.0, cfg.noise_sigma * np.sqrt(dt), len(x))), 0.0)

    return {"time": times, "biomass": x, "resource": s, "quota": q}


def intervention_effect(
    cfg: ChemostatConfig,
    intervention_loss: float,
    *,
    t_end: float = 100.0,
) -> dict[str, float]:
    baseline = simulate_chemostat(cfg, t_end=t_end)
    changed = simulate_chemostat(ChemostatConfig(**{**cfg.__dict__, "loss": intervention_loss}), t_end=t_end)
    b_final = float(baseline["biomass"][-1])
    c_final = float(changed["biomass"][-1])
    return {
        "baseline_final_biomass": b_final,
        "intervention_final_biomass": c_final,
        "absolute_effect": c_final - b_final,
        "relative_effect": (c_final - b_final) / max(abs(b_final), 1e-12),
        "baseline_persistent": float(b_final > 1e-6),
        "intervention_persistent": float(c_final > 1e-6),
    }
