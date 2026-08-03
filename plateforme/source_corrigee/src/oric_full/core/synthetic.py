from __future__ import annotations

import numpy as np
import networkx as nx

from .xma import classify_change
from .diagnostics import duration_diagnostic, hysteresis_diagnostic, loss_diagnostic
from .memory import convolve_memory, fit_memory_model
from .viability import estimate_viability, box_sampler


def run_core_synthetic(seed: int = 0) -> dict:
    rng = np.random.default_rng(seed)
    checks: dict[str, bool] = {}
    metrics: dict[str, float] = {}

    g0 = nx.path_graph(4)
    g1 = g0.copy()
    g1.add_edge(0, 3)
    checks["xma_state"] = classify_change([0, 0], [1, 0], [1], [1], g0, g0).classification == "state"
    checks["xma_parameter"] = classify_change([0, 0], [0, 0], [1], [2], g0, g0).classification == "memory_or_parameter"
    checks["xma_architecture"] = classify_change([0, 0], [0, 0], [1], [1], g0, g1).classification == "architecture"

    t = np.linspace(0, 100, 1001)
    y = np.exp(-t / 10)
    d = duration_diagnostic(t, y, baseline=0.0, tolerance=0.05)
    checks["d_relaxation"] = 25 <= d.relaxation_time <= 35
    metrics["relaxation_time"] = d.relaxation_time

    x_up = np.linspace(-2, 2, 500)
    x_down = np.linspace(2, -2, 500)
    y_up = np.tanh(4 * (x_up - 0.3))
    y_down = np.tanh(4 * (x_down + 0.3))
    h = hysteresis_diagnostic(x_up, y_up, x_down, y_down)
    checks["h_asymmetry"] = h.asymmetric and h.area > 0.1
    metrics["hysteresis_area"] = h.area

    before = nx.cycle_graph(6)
    after = before.copy()
    after.remove_edges_from([(0, 1), (3, 4)])
    l = loss_diagnostic(before, after)
    checks["l_topology"] = l.topological_loss
    metrics["lost_edges"] = float(l.lost_edges)

    forcing = rng.normal(size=len(t))
    target = 0.4 * forcing + 1.7 * convolve_memory(forcing, t[1] - t[0], "exponential", np.array([8.0]))
    target += rng.normal(0, 0.03, len(t))
    fit = fit_memory_model(t, forcing, target, "exponential")
    checks["memory_recovery"] = fit.success and abs(fit.params[0] - 8.0) / 8.0 < 0.35
    metrics["recovered_tau"] = fit.params[0]

    sampler = box_sampler(np.array([[-2, 2], [-2, 2]]))
    estimate = estimate_viability(
        sampler,
        lambda states: np.sum(states**2, axis=1) <= 4.0,
        lambda states, horizon, constraints: np.sum(states**2, axis=1) <= constraints["radius"] ** 2,
        horizon=10,
        constraints={"radius": 1.0},
        n_samples=10000,
        seed=seed,
    )
    checks["pacc_subset"] = 0 < estimate.pacc_fraction < estimate.pth_fraction < 1
    metrics["pth"] = estimate.pth_fraction
    metrics["pacc"] = estimate.pacc_fraction

    return {"passed": all(checks.values()), "checks": checks, "metrics": metrics}
