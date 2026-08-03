from __future__ import annotations

from dataclasses import dataclass
import json
import numpy as np
import pandas as pd
import networkx as nx
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GroupKFold, cross_val_predict


@dataclass(frozen=True)
class MatterAnalysis:
    metrics: dict[str, float]
    details: dict


def audit_transitions(frame: pd.DataFrame) -> MatterAnalysis:
    dimensions = ["n", "G", "I", "E", "Pi", "H"]
    missing_fraction = float(frame[dimensions].isna().mean().mean())
    unique_ids = float(frame["transition_id"].nunique() / max(len(frame), 1))
    evidence = pd.to_numeric(frame["evidence_level"], errors="coerce")
    evidence_coverage = float(evidence.notna().mean())
    return MatterAnalysis(
        {"missing_fraction": missing_fraction, "unique_id_fraction": unique_ids, "evidence_coverage": evidence_coverage},
        {"rows": len(frame), "dimensions": dimensions},
    )


def analyze_nucleosynthesis(frame: pd.DataFrame) -> MatterAnalysis:
    frame = frame.copy()
    frame["yield_mass"] = pd.to_numeric(frame["yield_mass"], errors="coerce")
    frame["uncertainty"] = pd.to_numeric(frame["uncertainty"], errors="coerce")
    grouped = frame.groupby("element", dropna=False)["yield_mass"].agg(["mean", "std", "count"])
    diversity = int((grouped["mean"] > 0).sum())
    cv = (grouped["std"] / grouped["mean"].abs().replace(0, np.nan)).replace([np.inf, -np.inf], np.nan)
    return MatterAnalysis(
        {"elements_with_positive_yield": float(diversity), "median_between_source_cv": float(cv.median(skipna=True) or 0.0)},
        {"element_summary": grouped.reset_index().to_dict(orient="records")},
    )


def build_reaction_graph(frame: pd.DataFrame) -> nx.DiGraph:
    graph = nx.DiGraph()
    for row in frame.itertuples(index=False):
        reactants = [x.strip() for x in str(row.reactants).split("+") if x.strip()]
        products = [x.strip() for x in str(row.products).split("+") if x.strip()]
        for r in reactants:
            for p in products:
                graph.add_edge(r, p, reaction_id=str(row.reaction_id), rate=float(row.rate))
    return graph


def accessible_species(frame: pd.DataFrame, initial_species: set[str], temperature: float) -> set[str]:
    valid = frame[(frame["temperature_min"] <= temperature) & (frame["temperature_max"] >= temperature)]
    accessible = set(initial_species)
    changed = True
    while changed:
        changed = False
        for row in valid.itertuples(index=False):
            reactants = {x.strip() for x in str(row.reactants).split("+") if x.strip()}
            products = {x.strip() for x in str(row.products).split("+") if x.strip()}
            if reactants <= accessible and not products <= accessible:
                accessible |= products
                changed = True
    return accessible


def analyze_astrochemistry(network: pd.DataFrame, inventory: pd.DataFrame | None = None) -> MatterAnalysis:
    graph = build_reaction_graph(network)
    species = sorted(graph.nodes)
    initial = set(species[: min(3, len(species))])
    temps = np.linspace(float(network.temperature_min.min()), float(network.temperature_max.max()), 8)
    counts = [len(accessible_species(network, initial, t)) for t in temps]
    metrics = {
        "species": float(graph.number_of_nodes()),
        "reactions_edges": float(graph.number_of_edges()),
        "accessible_species_max": float(max(counts, default=0)),
        "accessible_species_variation": float(np.ptp(counts) if counts else 0.0),
    }
    details = {"temperatures": temps.tolist(), "accessible_counts": counts}
    if inventory is not None and not inventory.empty:
        observed = set(inventory["species"].astype(str))
        predicted = set(graph.nodes)
        metrics["observed_coverage"] = len(observed & predicted) / max(len(observed), 1)
    return MatterAnalysis(metrics, details)


def analyze_condensation(frame: pd.DataFrame) -> MatterAnalysis:
    f = frame.copy()
    for col in ["temperature", "pressure", "gibbs_energy"]:
        f[col] = pd.to_numeric(f[col], errors="coerce")
    grouped = f.groupby(["temperature", "pressure"], dropna=True)
    winners = grouped.apply(lambda g: g.loc[g["gibbs_energy"].idxmin(), "phase"], include_groups=False)
    phase_counts = winners.value_counts()
    return MatterAnalysis(
        {
            "stable_phase_count": float(phase_counts.size),
            "state_points": float(len(winners)),
            "dominant_phase_fraction": float(phase_counts.iloc[0] / len(winners)) if len(winners) else 0.0,
        },
        {"stable_phase_counts": phase_counts.to_dict()},
    )


def transition_prediction(frame: pd.DataFrame, seed: int = 0) -> MatterAnalysis:
    features = ["n", "G", "I", "E", "Pi", "H"]
    x = frame[features].apply(pd.to_numeric, errors="coerce").fillna(0.0).to_numpy()
    y = frame["after_state"].astype(str).to_numpy()
    class_count = len(np.unique(y))
    if class_count < 2 or len(frame) < 10:
        return MatterAnalysis({"masked_accuracy": float("nan")}, {"reason": "Données insuffisantes"})
    # Une cible quasi unique par ligne n'est pas une tâche de classification valide.
    # Le code refuse ce cas au lieu de produire un score artificiel et des avertissements.
    if class_count > max(20, len(frame) // 2):
        return MatterAnalysis(
            {"masked_accuracy": float("nan")},
            {"reason": "Cible trop cardinalisée pour une classification", "n": len(frame), "classes": class_count},
        )
    groups = np.arange(len(frame)) % min(5, len(frame))
    cv = GroupKFold(n_splits=min(5, len(np.unique(groups))))
    model = RandomForestClassifier(n_estimators=200, random_state=seed, class_weight="balanced")
    pred = cross_val_predict(model, x, y, groups=groups, cv=cv)
    return MatterAnalysis({"masked_accuracy": float(accuracy_score(y, pred))}, {"n": len(frame), "classes": int(len(np.unique(y)))})
