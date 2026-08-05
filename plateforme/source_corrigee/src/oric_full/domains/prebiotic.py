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
    declared_metrics = ["yield", "polymer_length", "compartment_stability", "copy_fidelity"]
    measured_metrics: list[str] = []
    for col in declared_metrics:
        f[col] = pd.to_numeric(f[col], errors="coerce")
        if f[col].notna().any():
            measured_metrics.append(col)
    if not measured_metrics:
        return PrebioticAnalysis(
            {"lineage_depth": 0.0, "measured_metric_count": 0.0},
            {"reason": "Aucune métrique numérique mesurée"},
        )
    normalized = f[measured_metrics].rank(pct=True).clip(1e-6, 1.0)
    coupling = np.exp(np.log(normalized).mean(axis=1, skipna=True))
    graph = lineage_graph(f)
    longest = nx.dag_longest_path_length(graph) if nx.is_directed_acyclic_graph(graph) and len(graph) else 0
    if len(measured_metrics) >= 2:
        corr = f[measured_metrics].corr(method="spearman")
        off_diagonal = corr.where(~np.eye(len(corr), dtype=bool)).stack()
        min_corr = float(off_diagonal.min()) if len(off_diagonal) else float("nan")
        corr_details = corr.to_dict()
    else:
        min_corr = float("nan")
        corr_details = {}
    finite_coupling = coupling.replace([np.inf, -np.inf], np.nan).dropna()
    return PrebioticAnalysis(
        {
            "median_coupling_score": float(finite_coupling.median()) if len(finite_coupling) else float("nan"),
            "max_coupling_score": float(finite_coupling.max()) if len(finite_coupling) else float("nan"),
            "lineage_depth": float(longest),
            "metric_min_correlation": min_corr,
            "measured_metric_count": float(len(measured_metrics)),
        },
        {
            "correlation": corr_details,
            "measured_metrics": measured_metrics,
            "unmeasured_metrics": [name for name in declared_metrics if name not in measured_metrics],
            "interpretation_limit": (
                "Le score utilise uniquement les colonnes réellement mesurées. Les colonnes absentes "
                "restent absentes et ne sont jamais remplacées par zéro ou par une valeur supposée."
            ),
        },
    )


def transition_to_heredity(frame: pd.DataFrame, fidelity_threshold: float = 0.9, generations: int = 3) -> PrebioticAnalysis:
    f = frame.copy()
    f["copy_fidelity"] = pd.to_numeric(f["copy_fidelity"], errors="coerce")
    f["compartment_stability"] = pd.to_numeric(f["compartment_stability"], errors="coerce")
    f["generation"] = pd.to_numeric(f["generation"], errors="coerce")
    graph = lineage_graph(f)
    depth = nx.dag_longest_path_length(graph) if nx.is_directed_acyclic_graph(graph) and len(graph) else 0
    parent_nodes = set(graph.nodes)
    transmitted = {node for node in parent_nodes if graph.out_degree(node) > 0}
    leaves = {node for node in parent_nodes if graph.out_degree(node) == 0}
    measurable_fidelity = int(f["copy_fidelity"].notna().sum())
    measurable_stability = int(f["compartment_stability"].notna().sum())
    if measurable_fidelity and measurable_stability:
        viable = f[(f["copy_fidelity"] >= fidelity_threshold) & (f["compartment_stability"] > 0)]
        sustained = viable.groupby("condition_id")["generation"].nunique() >= generations
        candidate_count = float(sustained.sum())
        candidate_fraction = float(sustained.mean()) if len(sustained) else 0.0
    else:
        candidate_count = float("nan")
        candidate_fraction = float("nan")
    return PrebioticAnalysis(
        {
            "candidate_hereditary_lineages": candidate_count,
            "candidate_fraction": candidate_fraction,
            "lineage_depth": float(depth),
            "transmitted_node_fraction": float(len(transmitted) / max(len(parent_nodes), 1)),
            "terminal_node_fraction": float(len(leaves) / max(len(parent_nodes), 1)),
            "measured_copy_fidelity_rows": float(measurable_fidelity),
            "measured_compartment_stability_rows": float(measurable_stability),
        },
        {
            "fidelity_threshold": fidelity_threshold,
            "generations": generations,
            "interpretation_limit": (
                "La profondeur et la transmission sont mesurées par les cartes de transfert. "
                "Le statut héréditaire fondé sur fidélité de copie et stabilité compartimentale "
                "reste indéterminé lorsque ces variables ne sont pas publiées."
            ),
        },
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
