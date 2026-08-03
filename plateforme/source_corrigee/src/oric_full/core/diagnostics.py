from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import networkx as nx


@dataclass(frozen=True)
class DDiagnostic:
    relaxation_time: float
    residual: float
    persistent: bool


@dataclass(frozen=True)
class HDiagnostic:
    area: float
    threshold_forward: float
    threshold_backward: float
    asymmetric: bool


@dataclass(frozen=True)
class LDiagnostic:
    lost_nodes: int
    lost_edges: int
    lost_components: int
    unreachable_pairs_delta: int
    topological_loss: bool


def duration_diagnostic(time: np.ndarray, signal: np.ndarray, baseline: float = 0.0, tolerance: float = 0.05) -> DDiagnostic:
    t = np.asarray(time, dtype=float)
    y = np.asarray(signal, dtype=float)
    if len(t) != len(y) or len(t) < 3:
        raise ValueError("Série temporelle invalide")
    scale = max(float(np.max(np.abs(y - baseline))), np.finfo(float).eps)
    residuals = np.abs(y - baseline) / scale
    inside = residuals <= tolerance
    relaxation = float(t[-1] - t[0])
    for i in range(len(t)):
        if np.all(inside[i:]):
            relaxation = float(t[i] - t[0])
            break
    residual = float(residuals[-1])
    return DDiagnostic(relaxation, residual, residual > tolerance)


def _crossing(x: np.ndarray, y: np.ndarray, level: float) -> float:
    signs = np.sign(y - level)
    idx = np.flatnonzero(signs[:-1] * signs[1:] <= 0)
    if len(idx) == 0:
        return float("nan")
    i = int(idx[0])
    if y[i + 1] == y[i]:
        return float(x[i])
    frac = (level - y[i]) / (y[i + 1] - y[i])
    return float(x[i] + frac * (x[i + 1] - x[i]))


def hysteresis_diagnostic(
    control_forward: np.ndarray,
    response_forward: np.ndarray,
    control_backward: np.ndarray,
    response_backward: np.ndarray,
    level: float | None = None,
    tolerance: float = 1e-3,
) -> HDiagnostic:
    xf = np.asarray(control_forward, dtype=float)
    yf = np.asarray(response_forward, dtype=float)
    xb = np.asarray(control_backward, dtype=float)
    yb = np.asarray(response_backward, dtype=float)
    if level is None:
        level = float((min(yf.min(), yb.min()) + max(yf.max(), yb.max())) / 2)
    order_f = np.argsort(xf)
    order_b = np.argsort(xb)
    grid = np.linspace(max(xf.min(), xb.min()), min(xf.max(), xb.max()), 512)
    fi = np.interp(grid, xf[order_f], yf[order_f])
    bi = np.interp(grid, xb[order_b], yb[order_b])
    area = float(np.trapezoid(np.abs(fi - bi), grid))
    tf = _crossing(xf[order_f], yf[order_f], level)
    tb = _crossing(xb[order_b], yb[order_b], level)
    asym = bool(np.isfinite(tf) and np.isfinite(tb) and abs(tf - tb) > tolerance)
    return HDiagnostic(area, tf, tb, asym)


def loss_diagnostic(before: nx.Graph, after: nx.Graph) -> LDiagnostic:
    lost_nodes = len(set(before.nodes) - set(after.nodes))
    before_edges = {tuple(sorted(map(str, edge))) for edge in before.edges}
    after_edges = {tuple(sorted(map(str, edge))) for edge in after.edges}
    lost_edges = len(before_edges - after_edges)
    lost_components = max(nx.number_connected_components(after.to_undirected()) - nx.number_connected_components(before.to_undirected()), 0)

    common = sorted(set(before.nodes) & set(after.nodes), key=str)
    unreachable_before = 0
    unreachable_after = 0
    ub = before.to_undirected()
    ua = after.to_undirected()
    for i, source in enumerate(common):
        for target in common[i + 1 :]:
            if not nx.has_path(ub, source, target):
                unreachable_before += 1
            if not nx.has_path(ua, source, target):
                unreachable_after += 1
    delta = unreachable_after - unreachable_before
    return LDiagnostic(lost_nodes, lost_edges, lost_components, delta, any([lost_nodes, lost_edges, lost_components, delta > 0]))
