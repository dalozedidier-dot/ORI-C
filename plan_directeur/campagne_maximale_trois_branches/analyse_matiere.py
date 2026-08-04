"""Analyses de robustesse exploitables avec les données actuelles de la branche matière.

Les sorties sont structurelles ou descriptives. Elles ne convertissent jamais une
clôture de graphe ou un recouvrement d'intervalles en validation générale d'ORI-C.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

import networkx as nx

from common import ROOT, RESULTS, read_csv, read_json, write_json

HYPER = ROOT / "01_branche_matiere" / "hypergraphe_transformations"
BASE = ROOT / "01_branche_matiere" / "base_transitions"
OUTPUT = RESULTS / "matiere_robustesse.json"


def endpoints(edge: dict[str, str]) -> tuple[list[str], list[str]]:
    return edge["entrees"].split("|"), edge["sorties"].split("|")


def baseline_root(edges: list[dict[str, str]]) -> str:
    produced: set[str] = set()
    consumed: set[str] = set()
    for edge in edges:
        inputs, outputs = endpoints(edge)
        shared = set(inputs) & set(outputs)
        consumed.update(inputs)
        produced.update(node for node in outputs if node not in shared)
    roots = sorted(consumed - produced)
    if len(roots) != 1:
        raise ValueError(f"Une racine unique était attendue, trouvé: {roots}")
    return roots[0]


def reachable_from_seeds(
    seeds: set[str],
    edges: Iterable[dict[str, str]],
    removed_nodes: set[str] | None = None,
) -> set[str]:
    """Fermeture stricte à partir de plusieurs apports explicitement disponibles."""
    removed_nodes = removed_nodes or set()
    seen = set(seeds) - removed_nodes
    active = []
    for edge in edges:
        inputs, outputs = endpoints(edge)
        if any(node in removed_nodes for node in inputs + outputs):
            continue
        active.append((set(inputs), set(outputs)))
    changed = True
    while changed:
        changed = False
        for inputs, outputs in active:
            if inputs <= seen:
                additions = outputs - seen
                if additions:
                    seen.update(additions)
                    changed = True
    return seen


def reachable(
    root: str,
    edges: Iterable[dict[str, str]],
    removed_nodes: set[str] | None = None,
) -> set[str]:
    """Clôture dirigée exigeant toutes les entrées de chaque hyperarête.

    Une projection paire à paire transformerait une réaction multi-entrée en
    plusieurs réactions fictives à une seule entrée. La propagation est donc
    effectuée par point fixe sur les hyperarêtes complètes.
    """
    return reachable_from_seeds({root}, edges, removed_nodes)


def strict_gap_diagnostics(
    nodes: set[str], edges: list[dict[str, str]], root: str, base_reachable: set[str]
) -> dict:
    """Localise le noyau cyclique et teste les apports minimaux qui le déverrouillent."""
    unreachable = sorted(nodes - base_reachable)
    graph = nx.DiGraph()
    graph.add_nodes_from(unreachable)
    unreachable_set = set(unreachable)
    for edge in edges:
        inputs, outputs = endpoints(edge)
        for source in inputs:
            for target in outputs:
                if source != target and source in unreachable_set and target in unreachable_set:
                    graph.add_edge(source, target, edge_id=edge["edge_id"])
    components = [
        sorted(component)
        for component in nx.strongly_connected_components(graph)
        if len(component) > 1
    ]
    components.sort(key=lambda component: (-len(component), component))
    cycle_nodes = sorted({node for component in components for node in component})
    downstream_only = sorted(unreachable_set - set(cycle_nodes))

    seed_tests = []
    for seed in unreachable:
        reached = reachable_from_seeds({root, seed}, edges)
        seed_tests.append({
            "seed_node": seed,
            "nodes_reachable": len(reached),
            "restores_full_closure": reached == nodes,
            "remaining_unreachable": sorted(nodes - reached),
        })
    restoring = [row["seed_node"] for row in seed_tests if row["restores_full_closure"]]
    return {
        "nontrivial_strongly_connected_components": components,
        "cycle_kernel_nodes": cycle_nodes,
        "downstream_nodes_blocked_by_cycle": downstream_only,
        "single_seed_tests": seed_tests,
        "single_nodes_that_restore_full_closure": restoring,
        "minimum_additional_seed_count": 1 if restoring else None,
        "interpretation": (
            "Le noyau cyclique est une propriété de l'encodage actuel. Le fait qu'un seul nœud "
            "déclaré disponible suffise à fermer le graphe ne constitue pas une preuve qu'un tel "
            "apport externe existe dans la nature."
        ),
    }


def edge_robustness(nodes: set[str], edges: list[dict[str, str]], root: str) -> dict:
    base_reachable = reachable(root, edges)
    deletion_rows = []
    for removed in edges:
        kept = [edge for edge in edges if edge["edge_id"] != removed["edge_id"]]
        current = reachable(root, kept)
        lost = sorted(base_reachable - current)
        deletion_rows.append({
            "edge_id": removed["edge_id"],
            "processus": removed["processus"],
            "type": removed["type"],
            "statut_preuve": removed["statut_preuve"],
            "nodes_lost": len(lost),
            "lost_node_ids": lost,
        })
    deletion_rows.sort(key=lambda row: (-row["nodes_lost"], row["edge_id"]))

    node_rows = []
    for removed in sorted(nodes - {root}):
        current = reachable(root, edges, {removed})
        downstream_lost = sorted((base_reachable - {removed}) - current)
        node_rows.append({
            "node_id": removed,
            "downstream_nodes_lost": len(downstream_lost),
            "lost_node_ids": downstream_lost,
        })
    node_rows.sort(key=lambda row: (-row["downstream_nodes_lost"], row["node_id"]))

    by_type = []
    for edge_type in sorted({edge["type"] for edge in edges}):
        kept = [edge for edge in edges if edge["type"] != edge_type]
        current = reachable(root, kept)
        lost = sorted(base_reachable - current)
        by_type.append({
            "removed_type": edge_type,
            "removed_edges": sum(edge["type"] == edge_type for edge in edges),
            "nodes_lost": len(lost),
            "lost_node_ids": lost,
        })
    by_type.sort(key=lambda row: (-row["nodes_lost"], row["removed_type"]))

    critical = [row for row in deletion_rows if row["nodes_lost"] > 0]
    gap = strict_gap_diagnostics(nodes, edges, root, base_reachable)
    return {
        "declared_root": root,
        "baseline_nodes": len(nodes),
        "baseline_reachable": len(base_reachable),
        "baseline_unreachable": sorted(nodes - base_reachable),
        "strict_gap_diagnostics": gap,
        "reachability_rule": "toutes les entrées d'une hyperarête doivent être disponibles",
        "single_edge_deletions": len(deletion_rows),
        "critical_edges": len(critical),
        "critical_edge_fraction": round(len(critical) / len(edges), 6),
        "critical_edges_by_evidence_status": dict(Counter(row["statut_preuve"] for row in critical)),
        "top_edge_impacts": deletion_rows[:15],
        "top_node_impacts": node_rows[:15],
        "type_ablations": by_type,
        "interpretation": (
            "Une arête critique au sens de ce test est nécessaire à la joignabilité depuis la racine "
            "dans la représentation publiée. Cela mesure la fragilité structurelle du graphe, pas la "
            "nécessité physique universelle du processus correspondant."
        ),
    }


def interval_overlap(expected_low: float, expected_high: float | None, observed: list[float]) -> bool:
    observed_low, observed_high = min(observed), max(observed)
    if expected_high is None:
        return observed_high >= expected_low
    return max(expected_low, observed_low) <= min(expected_high, observed_high)


def expected_interval(records: list[dict[str, str]], mass_ratio: float) -> tuple[float, float | None]:
    values = [float(record["D_metal_sur_silicate"]) for record in records]
    low = min(values) * mass_ratio
    has_open_lower_bound = any(record["type_de_valeur"] == "borne_inferieure" for record in records)
    high = None if has_open_lower_bound else max(values) * mass_ratio
    return low, high


def partition_leave_one_out() -> dict:
    coefficients = read_csv(HYPER / "coefficients_partage.csv", delimiter=";")
    masses = read_csv(HYPER / "masses_reservoirs.csv", delimiter=";")
    inventory_results = read_json(HYPER / "inventaire_accessible_resultats.json")
    mass_by_reservoir = {row["reservoir"]: float(row["masse_kg"]) for row in masses}
    mass_ratio = mass_by_reservoir["noyau"] / mass_by_reservoir["terre silicatee totale"]

    by_element: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in coefficients:
        by_element[row["element"]].append(row)

    outcomes = {}
    fragile = []
    for element, records in sorted(by_element.items()):
        observed = inventory_results["prediction_par_les_coefficients_de_partage"][element][
            "rapport_de_masses_observe"
        ]
        low, high = expected_interval(records, mass_ratio)
        baseline = interval_overlap(low, high, observed)
        leave_one_out = []
        for removed in records:
            kept = [record for record in records if record["record_id"] != removed["record_id"]]
            if not kept:
                leave_one_out.append({
                    "removed_record": removed["record_id"],
                    "evaluable": False,
                    "reason": "un seul coefficient disponible",
                })
                continue
            loo_low, loo_high = expected_interval(kept, mass_ratio)
            leave_one_out.append({
                "removed_record": removed["record_id"],
                "evaluable": True,
                "expected_interval": [round(loo_low, 6), None if loo_high is None else round(loo_high, 6)],
                "overlap": interval_overlap(loo_low, loo_high, observed),
            })
        evaluable = [row for row in leave_one_out if row["evaluable"]]
        robust_fraction = (
            sum(bool(row["overlap"]) for row in evaluable) / len(evaluable) if evaluable else None
        )
        is_fragile = baseline and evaluable and any(not row["overlap"] for row in evaluable)
        if is_fragile:
            fragile.append(element)
        outcomes[element] = {
            "coefficients": [float(record["D_metal_sur_silicate"]) for record in records],
            "coefficient_record_ids": [record["record_id"] for record in records],
            "observed_interval": observed,
            "baseline_expected_interval": [round(low, 6), None if high is None else round(high, 6)],
            "baseline_overlap": baseline,
            "leave_one_out": leave_one_out,
            "leave_one_out_overlap_fraction": None if robust_fraction is None else round(robust_fraction, 6),
            "baseline_overlap_fragile": bool(is_fragile),
        }
    return {
        "core_to_silicate_mass_ratio": mass_ratio,
        "per_element": outcomes,
        "fragile_overlap_elements": fragile,
        "interpretation": (
            "Le retrait d'un coefficient publié teste si le recouvrement dépend d'une seule valeur. "
            "Ce contrôle ne résout pas les désaccords entre scénarios géochimiques."
        ),
    }


def completeness() -> dict:
    report = read_json(BASE / "completude.json")
    fields = report["par_champ"]
    zero = sorted(name for name, item in fields.items() if item["remplis"] == 0)
    partial = sorted(
        name for name, item in fields.items() if 0 < item["remplis"] < item["sur"]
    )
    full = sorted(name for name, item in fields.items() if item["remplis"] == item["sur"])
    return {
        "transitions": report["transitions"],
        "global_fill_rate": report["taux_global"],
        "fully_filled_fields": full,
        "partially_filled_fields": partial,
        "empty_fields": zero,
        "fields_requiring_external_sources_or_evaluators": sorted(
            name for name, item in fields.items() if not item["renseignable_depuis_le_dossier"]
        ),
    }


def run() -> dict:
    nodes = read_csv(HYPER / "noeuds.csv", delimiter=";")
    edges = read_csv(HYPER / "hyperaretes.csv", delimiter=";")
    node_ids = {row["node_id"] for row in nodes}
    root = baseline_root(edges)
    payload = {
        "status": "completed",
        "branch": "matiere",
        "hypergraph_robustness": edge_robustness(node_ids, edges, root),
        "partition_coefficient_robustness": partition_leave_one_out(),
        "transition_database_completeness": completeness(),
        "limitations": [
            "Les ablations portent sur une représentation de 53 nœuds et 53 hyperarêtes.",
            "La majorité des fractions mobilisables et des probabilités de transfert restent absentes.",
            "Aucun stock opératoire n'est disponible pour étendre la chaîne jusqu'à l'opérativité.",
            "Les tests de recouvrement comparent des intervalles publiés et ne constituent pas une inférence causale complète.",
        ],
    }
    write_json(OUTPUT, payload)
    return payload


if __name__ == "__main__":
    result = run()
    print(f"Matière: {result['hypergraph_robustness']['critical_edges']} arêtes critiques sur "
          f"{result['hypergraph_robustness']['single_edge_deletions']}.")
