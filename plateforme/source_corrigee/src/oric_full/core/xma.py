from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import numpy as np
import networkx as nx


@dataclass(frozen=True)
class XMAChange:
    state_change: float
    parameter_change: float
    topology_change: float
    classification: str


def _norm_distance(a: Any, b: Any) -> float:
    aa = np.asarray(a, dtype=float).ravel()
    bb = np.asarray(b, dtype=float).ravel()
    if aa.shape != bb.shape:
        return 1.0
    scale = max(float(np.linalg.norm(aa)), float(np.linalg.norm(bb)), 1.0)
    return float(np.linalg.norm(aa - bb) / scale)


def _graph_distance(a: nx.Graph | None, b: nx.Graph | None) -> float:
    if a is None and b is None:
        return 0.0
    if a is None or b is None:
        return 1.0
    edges_a = {tuple(sorted(map(str, edge))) for edge in a.edges()}
    edges_b = {tuple(sorted(map(str, edge))) for edge in b.edges()}
    union = edges_a | edges_b
    if not union:
        return 0.0
    return 1.0 - len(edges_a & edges_b) / len(union)


def classify_change(
    state_before: Any,
    state_after: Any,
    parameters_before: Any,
    parameters_after: Any,
    topology_before: nx.Graph | None = None,
    topology_after: nx.Graph | None = None,
    threshold: float = 1e-6,
) -> XMAChange:
    x = _norm_distance(state_before, state_after)
    m = _norm_distance(parameters_before, parameters_after)
    a = _graph_distance(topology_before, topology_after)
    if a > threshold:
        label = "architecture"
    elif m > threshold:
        label = "memory_or_parameter"
    elif x > threshold:
        label = "state"
    else:
        label = "none"
    return XMAChange(x, m, a, label)
