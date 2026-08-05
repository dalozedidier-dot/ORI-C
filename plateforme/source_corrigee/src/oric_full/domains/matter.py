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
    for column in ["yield_mass", "uncertainty", "mass_solar", "metallicity"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    grouped = frame.groupby("element", dropna=False)["yield_mass"].agg(["mean", "std", "count"])
    diversity = int((grouped["mean"] > 0).sum())
    cv = (grouped["std"] / grouped["mean"].abs().replace(0, np.nan)).replace([np.inf, -np.inf], np.nan)
    mass_summary = (
        frame.dropna(subset=["mass_solar", "yield_mass"])
        .groupby(["mass_solar", "element"], dropna=False)["yield_mass"]
        .mean()
        .reset_index()
    )
    mass_pivot = mass_summary.pivot_table(index="element", columns="mass_solar", values="yield_mass")
    mass_effect = (mass_pivot.max(axis=1) - mass_pivot.min(axis=1)) / mass_pivot.mean(axis=1).abs().replace(0, np.nan)
    families = sorted(frame.get("model_family", pd.Series(dtype=str)).dropna().astype(str).unique().tolist())
    return MatterAnalysis(
        {
            "elements_with_positive_yield": float(diversity),
            "median_between_source_cv": float(cv.median(skipna=True) or 0.0),
            "mass_levels": float(frame["mass_solar"].nunique()),
            "model_families": float(len(families)),
            "median_relative_mass_effect": float(mass_effect.median(skipna=True) or 0.0),
        },
        {
            "element_summary": grouped.reset_index().to_dict(orient="records"),
            "mass_summary": mass_summary.to_dict(orient="records"),
            "families": families,
        },
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
    species = set(graph.nodes)
    temperatures = np.array([10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0])
    tmin = pd.to_numeric(network["temperature_min"], errors="coerce")
    tmax = pd.to_numeric(network["temperature_max"], errors="coerce")
    active_counts = [int(((tmin <= temperature) & (tmax >= temperature)).sum()) for temperature in temperatures]
    uncertainty = (
        pd.to_numeric(network["uncertainty_factor"], errors="coerce")
        if "uncertainty_factor" in network.columns
        else pd.Series(np.nan, index=network.index, dtype=float)
    )
    source_counts = (
        network.get("source_network", pd.Series(["unspecified"] * len(network)))
        .fillna("unspecified").astype(str).value_counts().sort_index().astype(int).to_dict()
    )
    metrics = {
        "species": float(graph.number_of_nodes()),
        "reaction_rows": float(len(network)),
        "reactions_edges": float(graph.number_of_edges()),
        "independent_networks": float(len(source_counts)),
        "rate_uncertainty_coverage": float(uncertainty.notna().mean()),
        "active_reactions_max": float(max(active_counts, default=0)),
        "accessible_species_max": float(graph.number_of_nodes()),
    }
    details = {
        "temperatures_k": temperatures.tolist(),
        "active_reaction_counts": active_counts,
        "network_rows": source_counts,
        "interpretation_limit": "Audit structurel du réseau. Aucune fermeture chimique dynamique ni accessibilité moléculaire n'est déduite de ce seul calcul.",
    }
    if inventory is not None and not inventory.empty:
        inventory_species = set(inventory["species"].astype(str))
        metrics["inventory_network_overlap"] = len(inventory_species & species) / max(len(inventory_species), 1)
        details["inventory_species"] = sorted(inventory_species)
        details["inventory_kind"] = sorted(inventory.get("inventory_kind", pd.Series(dtype=str)).dropna().astype(str).unique().tolist())
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
