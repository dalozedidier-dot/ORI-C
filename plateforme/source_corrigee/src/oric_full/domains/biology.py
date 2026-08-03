from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd
import networkx as nx


@dataclass(frozen=True)
class BiologyAnalysis:
    metrics: dict[str, float]
    details: dict


def analyze_cell_architecture(frame: pd.DataFrame) -> BiologyAnalysis:
    graph = nx.DiGraph()
    for row in frame.itertuples(index=False):
        taxon = str(row.taxon)
        component = str(row.component)
        function = str(row.function)
        graph.add_edge(f"taxon:{taxon}", f"component:{component}", relation="HAS")
        graph.add_edge(f"component:{component}", f"function:{function}", relation="ENABLES")
        dependency = str(row.dependency)
        if dependency and dependency not in {"nan", "None", ""}:
            graph.add_edge(f"component:{component}", f"component:{dependency}", relation="DEPENDS")
    centrality = nx.pagerank(graph) if len(graph) else {}
    component_centrality = {k: v for k, v in centrality.items() if k.startswith("component:")}
    evidence = pd.to_numeric(frame["evidence_level"], errors="coerce")
    return BiologyAnalysis(
        {
            "components": float(frame["component"].nunique()),
            "functions": float(frame["function"].nunique()),
            "dependency_edges": float(sum(1 for _, _, d in graph.edges(data=True) if d.get("relation") == "DEPENDS")),
            "mean_evidence_level": float(evidence.mean(skipna=True) or 0.0),
        },
        {"component_centrality": component_centrality},
    )


def analyze_endosymbiosis(frame: pd.DataFrame) -> BiologyAnalysis:
    f = frame.copy()
    for col in ["gene_transfer", "metabolic_integration", "dependency", "evidence_level"]:
        f[col] = pd.to_numeric(f[col], errors="coerce")
    integration = f[["gene_transfer", "metabolic_integration", "dependency"]].mean(axis=1)
    return BiologyAnalysis(
        {
            "events": float(len(f)),
            "median_integration": float(integration.median(skipna=True) or 0.0),
            "integration_evidence_correlation": float(integration.corr(f["evidence_level"]) or 0.0),
        },
        {"integration_scores": dict(zip(f["event_id"].astype(str), integration.fillna(0).tolist()))},
    )


def biological_history_value(frame: pd.DataFrame) -> BiologyAnalysis:
    f = frame.copy()
    # Taux de collisions : mêmes états actuels avec futurs différents, signal minimal de dépendance à l'histoire.
    state_future = f.groupby("state")["future_outcome"].nunique()
    ambiguous_states = state_future[state_future > 1]
    history_resolves = []
    for state in ambiguous_states.index:
        sub = f[f["state"] == state]
        deterministic = sub.groupby("history")["future_outcome"].nunique()
        history_resolves.append(float((deterministic == 1).mean()))
    return BiologyAnalysis(
        {
            "ambiguous_state_fraction": float(len(ambiguous_states) / max(len(state_future), 1)),
            "history_resolution_fraction": float(np.mean(history_resolves)) if history_resolves else 0.0,
        },
        {"ambiguous_states": ambiguous_states.to_dict()},
    )
