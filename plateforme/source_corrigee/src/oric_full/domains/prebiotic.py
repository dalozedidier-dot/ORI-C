from __future__ import annotations

from dataclasses import dataclass
import itertools
import numpy as np
import pandas as pd
import networkx as nx


@dataclass(frozen=True)
class PrebioticAnalysis:
    metrics: dict[str, float]
    details: dict


def generate_factorial_design(factors: dict[str, list], replicates: int = 3) -> pd.DataFrame:
    names = list(factors)
    rows = []
    for values in itertools.product(*(factors[name] for name in names)):
        base = dict(zip(names, values))
        for replicate in range(replicates):
            rows.append({**base, "replicate": replicate, "condition_id": f"C{len(rows)+1:05d}"})
    return pd.DataFrame(rows)


def validate_lineages(frame: pd.DataFrame) -> PrebioticAnalysis:
    required = {"lineage_id", "parent_id", "generation", "condition_id", "yield", "polymer_length", "compartment_stability", "copy_fidelity"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes: {sorted(missing)}")
    ids = set(frame["lineage_id"].astype(str))
    parents = set(frame["parent_id"].dropna().astype(str)) - {"", "nan", "None"}
    orphan_fraction = len(parents - ids) / max(len(parents), 1)
    duplicated = 1.0 - frame["lineage_id"].nunique() / max(len(frame), 1)
    return PrebioticAnalysis(
        {"orphan_parent_fraction": float(orphan_fraction), "duplicate_id_fraction": float(duplicated), "lineages": float(len(frame))},
        {"orphan_parents": sorted(parents - ids)},
    )


def lineage_graph(frame: pd.DataFrame) -> nx.DiGraph:
    graph = nx.DiGraph()
    for row in frame.itertuples(index=False):
        child = str(row.lineage_id)
        graph.add_node(child, generation=int(row.generation), condition_id=str(row.condition_id))
        parent = str(row.parent_id)
        if parent and parent not in {"nan", "None", ""}:
            graph.add_edge(parent, child)
    return graph


def analyze_prebiotic_coupling(frame: pd.DataFrame) -> PrebioticAnalysis:
    f = frame.copy()
    metrics_cols = ["yield", "polymer_length", "compartment_stability", "copy_fidelity"]
    for col in metrics_cols:
        f[col] = pd.to_numeric(f[col], errors="coerce")
    corr = f[metrics_cols].corr(method="spearman")
    # geometric mean pénalise les systèmes bons sur un seul axe et nuls sur un autre
    normalized = f[metrics_cols].rank(pct=True).clip(1e-6, 1.0)
    coupling = np.exp(np.log(normalized).mean(axis=1))
    graph = lineage_graph(f)
    longest = nx.dag_longest_path_length(graph) if nx.is_directed_acyclic_graph(graph) and len(graph) else 0
    return PrebioticAnalysis(
        {
            "median_coupling_score": float(np.median(coupling)),
            "max_coupling_score": float(np.max(coupling)),
            "lineage_depth": float(longest),
            "metric_min_correlation": float(corr.where(~np.eye(len(corr), dtype=bool)).min().min()),
        },
        {"correlation": corr.to_dict(), "coupling_scores": coupling.tolist()},
    )


def transition_to_heredity(frame: pd.DataFrame, fidelity_threshold: float = 0.9, generations: int = 3) -> PrebioticAnalysis:
    f = frame.copy()
    f["copy_fidelity"] = pd.to_numeric(f["copy_fidelity"], errors="coerce")
    f["generation"] = pd.to_numeric(f["generation"], errors="coerce")
    viable = f[(f["copy_fidelity"] >= fidelity_threshold) & (f["compartment_stability"] > 0)]
    sustained = viable.groupby("lineage_id")["generation"].nunique() >= generations
    return PrebioticAnalysis(
        {"candidate_hereditary_lineages": float(sustained.sum()), "candidate_fraction": float(sustained.mean()) if len(sustained) else 0.0},
        {"fidelity_threshold": fidelity_threshold, "generations": generations},
    )


def analyze_rna_evolution(frame: pd.DataFrame) -> PrebioticAnalysis:
    """Démographie de séquences mesurées sur plusieurs cycles, sans reconstruire de généalogie."""
    f = frame.copy()
    for column in ["round", "frequency", "relative_frequency"]:
        f[column] = pd.to_numeric(f[column], errors="coerce")
    f = f.dropna(subset=["branch", "round", "sequence_id", "frequency"])
    if f.empty:
        return PrebioticAnalysis({"rows": 0.0}, {"reason": "Aucune mesure exploitable"})
    unique_grain = float(1.0 - f.duplicated(["branch", "round", "sequence_id"]).mean())
    rounds = f.groupby("branch")["round"].nunique().to_dict()
    seq_counts = f.groupby(["branch", "round"])["sequence_id"].nunique()
    trajectories = f.groupby(["branch", "sequence_id"])["round"].nunique()
    return PrebioticAnalysis(
        {"rows": float(len(f)), "branches": float(f["branch"].nunique()), "max_rounds": float(max(rounds.values())), "unique_grain_fraction": unique_grain, "max_sequence_persistence_rounds": float(trajectories.max())},
        {"rounds_by_branch": {str(k): int(v) for k, v in rounds.items()}, "sequences_per_round": {f"{a}:{int(b)}": int(v) for (a, b), v in seq_counts.items()}, "interpretation_limit": "Fréquences publiées; aucune généalogie, autonomie de réplication ou hérédité protocellulaire inférée."},
    )
