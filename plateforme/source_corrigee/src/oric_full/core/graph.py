from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
import networkx as nx
from sklearn.metrics import roc_auc_score


# Autorité: vocabulaire relationnel du CODEBOOK livré avec le dossier.
ALLOWED_RELATIONS = {
    "ENBL", "MATR", "ENVR", "STAB", "CATL", "CNST", "CONT",
    "DEPG", "INCO", "DESC", "FEED", "CLOS", "INTG",
    # Compatibilité des jeux de démonstration historiques de la plateforme.
    "TRANS", "ASSOC", "PERT", "COND", "HERIT",
}


@dataclass(frozen=True)
class GraphAudit:
    nodes: int
    edges: int
    invalid_relation_types: tuple[str, ...]
    self_loops: int
    cycles: int
    connected_components: int


def load_relation_graph(path: Path) -> nx.DiGraph:
    frame = pd.read_csv(path)
    required = {"source", "target", "relation_type"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes: {sorted(missing)}")
    graph = nx.DiGraph()
    for row in frame.itertuples(index=False):
        graph.add_edge(str(row.source), str(row.target), relation_type=str(row.relation_type))
    return graph


def audit_graph(graph: nx.DiGraph) -> GraphAudit:
    invalid = sorted({d.get("relation_type", "") for _, _, d in graph.edges(data=True)} - ALLOWED_RELATIONS)
    cycles = sum(1 for _ in nx.simple_cycles(graph))
    return GraphAudit(
        graph.number_of_nodes(),
        graph.number_of_edges(),
        tuple(invalid),
        nx.number_of_selfloops(graph),
        cycles,
        nx.number_weakly_connected_components(graph),
    )


def masked_link_prediction(graph: nx.DiGraph, mask_fraction: float = 0.2, seed: int = 0) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    edges = list(graph.edges())
    if len(edges) < 5:
        return {"auc": float("nan"), "masked_edges": 0.0}
    n_mask = max(1, int(len(edges) * mask_fraction))
    masked_idx = rng.choice(len(edges), size=n_mask, replace=False)
    masked = [edges[i] for i in masked_idx]
    train = graph.copy()
    train.remove_edges_from(masked)

    nodes = list(train.nodes())
    positives = masked
    negatives = []
    existing = set(graph.edges())
    while len(negatives) < n_mask:
        a, b = rng.choice(nodes, size=2, replace=False)
        if (a, b) not in existing and (a, b) not in negatives:
            negatives.append((a, b))

    undirected = train.to_undirected()
    scores = []
    labels = []
    for edge, label in [(e, 1) for e in positives] + [(e, 0) for e in negatives]:
        a, b = edge
        common = len(list(nx.common_neighbors(undirected, a, b))) if a in undirected and b in undirected else 0
        pa = undirected.degree(a) * undirected.degree(b) if a in undirected and b in undirected else 0
        scores.append(common + 1e-6 * pa)
        labels.append(label)
    auc = float(roc_auc_score(labels, scores)) if len(set(labels)) == 2 else float("nan")
    return {"auc": auc, "masked_edges": float(n_mask)}
