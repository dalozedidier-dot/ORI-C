#!/usr/bin/env python3
"""Diagnostique le verrou de fermeture hypergraphique de la branche matière.

Le graphe canonique n'est jamais modifié par ce script. Les réparations sont
évaluées dans des copies en mémoire et publiées comme scénarios candidats.
"""
from __future__ import annotations

import csv
import itertools
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
OUT = HERE / "resultats"


@dataclass(frozen=True)
class Edge:
    edge_id: str
    process: str
    inputs: frozenset[str]
    outputs: frozenset[str]
    evidence: str
    source_id: str


def read_semicolon(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def load_edges(path: Path = BASE / "hyperaretes.csv") -> list[Edge]:
    rows = read_semicolon(path)
    return [
        Edge(
            edge_id=row["edge_id"],
            process=row["processus"],
            inputs=frozenset(filter(None, row["entrees"].split("|"))),
            outputs=frozenset(filter(None, row["sorties"].split("|"))),
            evidence=row["statut_preuve"],
            source_id=row["source_id"],
        )
        for row in rows
    ]


def strict_closure(edges: Iterable[Edge], roots: Iterable[str]) -> set[str]:
    available = set(roots)
    changed = True
    while changed:
        changed = False
        for edge in edges:
            if edge.inputs <= available and not edge.outputs <= available:
                available.update(edge.outputs)
                changed = True
    return available


def dependency_scc(unreachable: set[str], edges: list[Edge]) -> list[list[str]]:
    graph: dict[str, set[str]] = {node: set() for node in unreachable}
    for edge in edges:
        for output in edge.outputs & unreachable:
            graph[output].update(edge.inputs & unreachable)

    index = 0
    stack: list[str] = []
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    on_stack: set[str] = set()
    components: list[list[str]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlink[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for nxt in graph[node]:
            if nxt not in indices:
                visit(nxt)
                lowlink[node] = min(lowlink[node], lowlink[nxt])
            elif nxt in on_stack:
                lowlink[node] = min(lowlink[node], indices[nxt])
        if lowlink[node] == indices[node]:
            component = []
            while True:
                nxt = stack.pop()
                on_stack.remove(nxt)
                component.append(nxt)
                if nxt == node:
                    break
            components.append(sorted(component))

    for node in sorted(graph):
        if node not in indices:
            visit(node)
    return sorted(components, key=lambda c: (-len(c), c))


def replace_edge(edges: list[Edge], edge_id: str, *, inputs: set[str], outputs: set[str]) -> list[Edge]:
    result = []
    for edge in edges:
        if edge.edge_id == edge_id:
            result.append(Edge(edge.edge_id, edge.process, frozenset(inputs), frozenset(outputs), edge.evidence, edge.source_id))
        else:
            result.append(edge)
    return result


def add_edge(edges: list[Edge], edge: Edge) -> list[Edge]:
    return [*edges, edge]


def minimal_seed_sets(edges: list[Edge], roots: set[str], nodes: set[str], target: set[str]) -> list[dict]:
    candidates = sorted(target)
    complete: list[dict] = []
    for size in range(1, len(candidates) + 1):
        for seeds in itertools.combinations(candidates, size):
            closure = strict_closure(edges, roots | set(seeds))
            reached = target & closure
            if reached == target:
                complete.append({"seeds": list(seeds), "seed_count": size, "reached": len(reached)})
        if complete:
            break
    return complete


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    node_rows = read_semicolon(BASE / "noeuds.csv")
    labels = {row["node_id"]: row["label"] for row in node_rows}
    all_nodes = set(labels)
    edges = load_edges()
    roots = {"N036"}
    baseline = strict_closure(edges, roots)
    unreachable = all_nodes - baseline

    blockers: dict[str, list[dict]] = defaultdict(list)
    for edge in edges:
        for output in edge.outputs & unreachable:
            missing = sorted(edge.inputs - baseline)
            blockers[output].append({
                "edge_id": edge.edge_id,
                "processus": edge.process,
                "entrees_manquantes": missing,
                "source_id": edge.source_id,
                "statut_preuve": edge.evidence,
            })

    # Scénario R1 : H052 ne présuppose plus N030. Il représente alors la
    # formation conjointe du système hydrothermal et de l'interface eau-roche.
    r1_edges = replace_edge(edges, "H052", inputs={"N051", "N028"}, outputs={"N053", "N030"})
    r1_closure = strict_closure(r1_edges, roots)

    # Scénario R2 : le graphe canonique reste intact et une hyperarête
    # alternative explicite la même hypothèse. Elle est séparée pour audit.
    r2_edge = Edge(
        edge_id="HC01",
        process="Emergence d'une circulation hydrothermale et de ses interfaces",
        inputs=frozenset({"N051", "N028"}),
        outputs=frozenset({"N053", "N030"}),
        evidence="candidat_a_sourcer",
        source_id="S14",
    )
    r2_closure = strict_closure(add_edge(edges, r2_edge), roots)

    seed_sets = minimal_seed_sets(edges, roots, all_nodes, unreachable)
    components = dependency_scc(unreachable, edges)

    scenarios = [
        {
            "scenario_id": "R0",
            "type": "canonique",
            "description": "Hypergraphe inchangé",
            "reachable": len(baseline),
            "unreachable": sorted(unreachable),
            "strictly_closed": not unreachable,
            "scientific_status": "résultat courant",
        },
        {
            "scenario_id": "R1",
            "type": "recodage d'une hyperarête",
            "description": "H052 devient N051|N028 -> N053|N030, sans présupposer l'interface qu'elle entretient.",
            "reachable": len(r1_closure),
            "unreachable": sorted(all_nodes - r1_closure),
            "strictly_closed": all_nodes <= r1_closure,
            "scientific_status": "réparation structurelle candidate, non preuve historique",
        },
        {
            "scenario_id": "R2",
            "type": "hyperarête alternative",
            "description": "Ajout séparé de HC01 : N051|N028 -> N053|N030, source S14 à réévaluer.",
            "reachable": len(r2_closure),
            "unreachable": sorted(all_nodes - r2_closure),
            "strictly_closed": all_nodes <= r2_closure,
            "scientific_status": "hypothèse testable, non canonique",
        },
    ]

    payload = {
        "declared_roots": sorted(roots),
        "node_count": len(all_nodes),
        "edge_count": len(edges),
        "baseline_reachable": len(baseline),
        "baseline_unreachable": sorted(unreachable),
        "blocked_labels": {node: labels[node] for node in sorted(unreachable)},
        "blocking_dependencies": blockers,
        "strongly_connected_components": components,
        "minimal_external_seed_sets": seed_sets,
        "scenarios": scenarios,
        "interpretation": {
            "structural": "Le verrou est concentré dans une boucle N029-N030-N053-N054. N031, N032 et N035 sont bloqués en aval.",
            "candidate_repair": "Un seul recodage de H052 suffit mathématiquement à rendre les 53 nœuds accessibles.",
            "limit": "La fermeture mathématique n'établit ni l'occurrence naturelle de HC01, ni une séquence historique unique.",
        },
    }
    (OUT / "diagnostic_fermeture.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with (OUT / "scenarios_reparation.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["scenario_id", "type", "reachable", "strictly_closed", "scientific_status", "description"], lineterminator="\n")
        writer.writeheader()
        for scenario in scenarios:
            writer.writerow({key: scenario[key] for key in writer.fieldnames})

    report = [
        "# Verrou de fermeture stricte de la branche matière",
        "",
        "## Résultat canonique",
        "",
        f"La fermeture stricte atteint **{len(baseline)} nœuds sur {len(all_nodes)}**. Les sept nœuds inaccessibles sont " + ", ".join(f"`{n}`" for n in sorted(unreachable)) + ".",
        "",
        "Le noyau de dépendance circulaire est `N029`, `N030`, `N053` et `N054`. `N031`, `N032` et `N035` sont bloqués en aval. Le verrou n'est donc pas dispersé dans tout l'hypergraphe.",
        "",
        "## Diagnostic minimal",
        "",
        "Le cycle vient de la combinaison suivante : l'inventaire accessible exige déjà des espèces solubles, la circulation entre réservoirs exige l'inventaire accessible, le système hydrothermal exige déjà l'interface eau-roche, et les espèces solubles exigent le système hydrothermal.",
        "",
        "L'énumération des apports externes montre qu'un seul nœud injecté dans le noyau suffit à fermer mathématiquement tout le graphe. Cette observation localise le verrou, mais ne justifie aucun apport dans la nature.",
        "",
        "## Réparation structurelle candidate",
        "",
        "Le scénario `R1` recode `H052` de `N051|N028|N030 -> N053` vers `N051|N028 -> N053|N030`. La circulation hydrothermale produit alors l'interface eau-roche qu'elle entretient au lieu de la présupposer.",
        "",
        f"Avec ce seul changement, la fermeture atteint **{len(r1_closure)} nœuds sur {len(all_nodes)}**. Le scénario `R2` conserve le graphe canonique et ajoute la même proposition sous la forme d'une hyperarête candidate séparée `HC01`.",
        "",
        "## Statut scientifique",
        "",
        "Le verrou courant est expliqué comme une circularité de représentation localisée. Une réparation minimale existe et ferme le graphe, mais elle reste une hypothèse de codage à valider contre les sources primaires. Le fichier canonique `hyperaretes.csv` n'est pas modifié.",
    ]
    (OUT / "RAPPORT_VERROU_MATIERE.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    candidate_rows = read_semicolon(BASE / "hyperaretes.csv")
    fieldnames = list(candidate_rows[0])
    for row in candidate_rows:
        if row["edge_id"] == "H052":
            row["entrees"] = "N051|N028"
            row["sorties"] = "N053|N030"
            row["incertitude_ou_scenario"] = "recodage candidat : l interface est produite et entretenue par la circulation"
    with (OUT / "hyperaretes_candidat_R1.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=";", lineterminator="\n")
        writer.writeheader(); writer.writerows(candidate_rows)

    print(json.dumps({"baseline": len(baseline), "R1": len(r1_closure), "R2": len(r2_closure), "minimal_seed_sets": seed_sets}, ensure_ascii=False))


if __name__ == "__main__":
    main()
