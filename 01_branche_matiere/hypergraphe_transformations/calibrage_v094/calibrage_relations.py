#!/usr/bin/env python3
"""Calibre les 53 hyperarêtes de la branche matière sans modifier le graphe canonique.

Le calibrage sépare strictement :
- la solidité documentaire, issue du codage existant ;
- la fonction structurelle, calculée par ablation et redondance ;
- les dimensions encore non mesurées, conservées comme telles.

Les coefficients documentaires servent à des analyses de sensibilité. Ils ne
sont ni des probabilités de vérité ni une mesure universelle de causalité.
"""
from __future__ import annotations

import csv
import json
import math
import random
import sys
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
BASE = HERE.parent
OUT = HERE / "resultats"
ROOT_NODE = "N036"
SEED = 9404
MONTE_CARLO_RUNS = 4000

EVIDENCE_SCORES = {
    "observe": 1.00,
    "observe_experience": 0.95,
    "experience_modele": 0.90,
    "observe_infere": 0.85,
    "observe_modele": 0.80,
    "modele_appuye": 0.75,
    "observe_hypothese": 0.65,
    "modele": 0.60,
    "definition_operationnelle": 0.55,
    "scenario_concurrent": 0.45,
    "hypothese_testable": 0.35,
}
SOURCE_SCORES = {
    "revue_reference": 1.00,
    "article": 0.95,
    "mission_source": 0.90,
    "article_recent": 0.90,
    "revue": 0.85,
    "reference": 0.80,
    "article_modele": 0.80,
    "perspective": 0.65,
    "prepublication": 0.55,
    "source_secondaire": 0.40,
}
PROFILES = {
    "complet": 0.00,
    "permissif": 0.45,
    "equilibre": 0.65,
    "conservateur": 0.80,
    "tres_strict": 0.90,
}


@dataclass(frozen=True)
class Edge:
    edge_id: str
    process: str
    inputs: frozenset[str]
    outputs: frozenset[str]
    edge_type: str
    branch: str
    capacity: str
    evidence: str
    source_id: str
    uncertainty: str
    genealogical_role: str


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def write_csv(path: Path, rows: Sequence[dict], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=";", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_edges(path: Path = BASE / "hyperaretes.csv") -> list[Edge]:
    return [
        Edge(
            edge_id=row["edge_id"],
            process=row["processus"],
            inputs=frozenset(filter(None, row["entrees"].split("|"))),
            outputs=frozenset(filter(None, row["sorties"].split("|"))),
            edge_type=row["type"],
            branch=row["branche"],
            capacity=row["capacite_acquise"],
            evidence=row["statut_preuve"],
            source_id=row["source_id"],
            uncertainty=row["incertitude_ou_scenario"],
            genealogical_role=row["role_genealogique"],
        )
        for row in read_csv(path)
    ]


def load_sources(path: Path = BASE / "sources.csv") -> dict[str, dict[str, str]]:
    return {row["source_id"]: row for row in read_csv(path)}


def load_nodes(path: Path = BASE / "noeuds.csv") -> dict[str, dict[str, str]]:
    return {row["node_id"]: row for row in read_csv(path)}


def strict_closure(edges: Iterable[Edge], roots: Iterable[str]) -> set[str]:
    available = set(roots)
    changed = True
    edges = list(edges)
    while changed:
        changed = False
        for edge in edges:
            if edge.inputs <= available and not edge.outputs <= available:
                available.update(edge.outputs)
                changed = True
    return available


def adjacency(edges: Iterable[Edge]) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        for source in edge.inputs:
            graph[source].update(edge.outputs)
        for output in edge.outputs:
            graph.setdefault(output, set())
    return graph


def reachable_pairwise(edges: Iterable[Edge], root: str = ROOT_NODE) -> set[str]:
    graph = adjacency(edges)
    seen = {root}
    queue = deque([root])
    while queue:
        node = queue.popleft()
        for nxt in graph.get(node, ()):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def descendants(graph: dict[str, set[str]], starts: Iterable[str]) -> set[str]:
    seen = set(starts)
    queue = deque(starts)
    while queue:
        node = queue.popleft()
        for nxt in graph.get(node, ()):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def strongly_connected_components(graph: dict[str, set[str]]) -> list[list[str]]:
    index = 0
    stack: list[str] = []
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    on_stack: set[str] = set()
    components: list[list[str]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for nxt in graph.get(node, ()):
            if nxt not in indices:
                visit(nxt)
                lowlinks[node] = min(lowlinks[node], lowlinks[nxt])
            elif nxt in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[nxt])
        if lowlinks[node] == indices[node]:
            component: list[str] = []
            while True:
                nxt = stack.pop()
                on_stack.remove(nxt)
                component.append(nxt)
                if nxt == node:
                    break
            components.append(sorted(component))

    all_nodes = set(graph)
    for targets in graph.values():
        all_nodes.update(targets)
    for node in sorted(all_nodes):
        if node not in indices:
            visit(node)
    return sorted(components, key=lambda values: (-len(values), values))


def documentary(edge: Edge, sources: dict[str, dict[str, str]]) -> dict[str, float | str]:
    source = sources[edge.source_id]
    evidence = EVIDENCE_SCORES.get(edge.evidence, 0.25)
    source_score = SOURCE_SCORES.get(source["type"], 0.50)
    floor = min(evidence, source_score)
    mean = (evidence + source_score) / 2.0
    if floor >= 0.65:
        stress_weight = 1.00
    elif floor >= 0.45:
        stress_weight = 0.70
    else:
        stress_weight = 0.35
    return {
        "evidence_score": evidence,
        "source_score": source_score,
        "documentary_floor": floor,
        "documentary_mean": mean,
        "stress_activation_weight": stress_weight,
        "source_type": source["type"],
    }


def calibration_priority(
    *, documentary_floor: float, pairwise_loss: int, strict_loss: int,
    in_cycle: bool, blocking_cycle: bool, alternatives: int, downstream: int,
    downstream_median: float,
) -> str:
    if blocking_cycle:
        return "P1_cycle_verrou"
    if documentary_floor < 0.65 and downstream >= downstream_median:
        return "P1_documentation_effet_aval"
    if pairwise_loss > 0 or strict_loss > 0:
        return "P1_ablation_structurelle"
    if in_cycle:
        return "P2_cycle_entretien"
    if alternatives == 0 and downstream >= downstream_median:
        return "P2_voie_unique"
    if documentary_floor < 0.65:
        return "P2_documentation_locale"
    if alternatives > 0:
        return "P3_redondante"
    return "P3_stable"


def analyze_edges(edges: list[Edge], nodes: dict[str, dict[str, str]], sources: dict[str, dict[str, str]]) -> list[dict]:
    all_nodes = set(nodes)
    baseline_pairwise = reachable_pairwise(edges)
    baseline_strict = strict_closure(edges, {ROOT_NODE})
    graph = adjacency(edges)
    components = strongly_connected_components(graph)
    component_by_node: dict[str, int] = {}
    cyclic_components: set[int] = set()
    for index, component in enumerate(components, start=1):
        for node in component:
            component_by_node[node] = index
        if len(component) > 1 or any(node in graph.get(node, set()) for node in component):
            cyclic_components.add(index)

    producers: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        for output in edge.outputs:
            producers[output].add(edge.edge_id)

    downstream_counts = {
        edge.edge_id: len(descendants(graph, edge.outputs) - set(edge.outputs))
        for edge in edges
    }
    values = sorted(downstream_counts.values())
    downstream_median = values[len(values) // 2]
    blocking_nodes = {"N029", "N030", "N053", "N054"}
    rows: list[dict] = []
    for edge in edges:
        reduced = [candidate for candidate in edges if candidate.edge_id != edge.edge_id]
        pairwise_after = reachable_pairwise(reduced)
        strict_after = strict_closure(reduced, {ROOT_NODE})
        alternative_counts = [len(producers[output] - {edge.edge_id}) for output in edge.outputs]
        alternatives = min(alternative_counts) if alternative_counts else 0
        cycle_ids = {
            component_by_node[node]
            for node in edge.inputs | edge.outputs
            if component_by_node.get(node) in cyclic_components
        }
        in_cycle = bool(cycle_ids)
        blocking_cycle = bool(edge.inputs & blocking_nodes) and bool(edge.outputs & blocking_nodes)
        inputs_without_edge = strict_closure(reduced, {ROOT_NODE})
        missing_inputs_without_edge = sorted(edge.inputs - inputs_without_edge)
        doc = documentary(edge, sources)
        pairwise_loss = len(baseline_pairwise - pairwise_after)
        strict_loss = len(baseline_strict - strict_after)
        priority = calibration_priority(
            documentary_floor=float(doc["documentary_floor"]),
            pairwise_loss=pairwise_loss,
            strict_loss=strict_loss,
            in_cycle=in_cycle,
            blocking_cycle=blocking_cycle,
            alternatives=alternatives,
            downstream=downstream_counts[edge.edge_id],
            downstream_median=downstream_median,
        )
        rows.append({
            "edge_id": edge.edge_id,
            "processus": edge.process,
            "type": edge.edge_type,
            "branche": edge.branch,
            "source_id": edge.source_id,
            "source_type": doc["source_type"],
            "statut_preuve": edge.evidence,
            "score_preuve": f"{doc['evidence_score']:.3f}",
            "score_source": f"{doc['source_score']:.3f}",
            "plancher_documentaire": f"{doc['documentary_floor']:.3f}",
            "moyenne_documentaire": f"{doc['documentary_mean']:.3f}",
            "poids_activation_stress": f"{doc['stress_activation_weight']:.3f}",
            "perte_projection_ablation": pairwise_loss,
            "perte_fermeture_stricte_ablation": strict_loss,
            "noeuds_aval": downstream_counts[edge.edge_id],
            "voies_alternatives_min": alternatives,
            "appartient_cycle": str(in_cycle).lower(),
            "cycle_ids": "|".join(map(str, sorted(cycle_ids))),
            "cycle_verrou_interfaces": str(blocking_cycle).lower(),
            "entrees_manquantes_sans_arete": "|".join(missing_inputs_without_edge),
            "role_genealogique": edge.genealogical_role,
            "priorite_calibrage": priority,
            "necessite_empirique": "non_mesuree",
            "suffisance_empirique": "non_mesuree",
            "temporalite_quantitative": "non_mesuree",
            "reversibilite_physique": "non_mesuree",
            "intervention_directe": "non_mesuree",
        })
    return rows


def threshold_profiles(edges: list[Edge], sources: dict[str, dict[str, str]], all_nodes: set[str]) -> list[dict]:
    rows = []
    for profile, threshold in PROFILES.items():
        retained = [edge for edge in edges if documentary(edge, sources)["documentary_floor"] >= threshold]
        pairwise = reachable_pairwise(retained)
        strict = strict_closure(retained, {ROOT_NODE})
        components = strongly_connected_components(adjacency(retained))
        largest = max((len(component) for component in components), default=0)
        rows.append({
            "profil": profile,
            "seuil_plancher_documentaire": f"{threshold:.2f}",
            "hyperaretes_conservees": len(retained),
            "projection_atteignable": len(pairwise & all_nodes),
            "fermeture_stricte_atteignable": len(strict & all_nodes),
            "plus_grande_composante_fortement_connexe": largest,
            "noeuds_projection_manquants": "|".join(sorted(all_nodes - pairwise)),
            "noeuds_stricts_manquants": "|".join(sorted(all_nodes - strict)),
        })
    return rows


def source_ablations(edges: list[Edge], sources: dict[str, dict[str, str]], all_nodes: set[str]) -> list[dict]:
    baseline_pairwise = reachable_pairwise(edges)
    baseline_strict = strict_closure(edges, {ROOT_NODE})
    rows = []
    for source_id in sorted(sources):
        reduced = [edge for edge in edges if edge.source_id != source_id]
        pairwise = reachable_pairwise(reduced)
        strict = strict_closure(reduced, {ROOT_NODE})
        rows.append({
            "source_id": source_id,
            "type_source": sources[source_id]["type"],
            "hyperaretes_retires": sum(edge.source_id == source_id for edge in edges),
            "perte_projection": len((baseline_pairwise & all_nodes) - pairwise),
            "perte_fermeture_stricte": len((baseline_strict & all_nodes) - strict),
            "noeuds_projection_perdus": "|".join(sorted((baseline_pairwise & all_nodes) - pairwise)),
            "noeuds_stricts_perdus": "|".join(sorted((baseline_strict & all_nodes) - strict)),
        })
    return rows


def monte_carlo(edges: list[Edge], nodes: dict[str, dict[str, str]], sources: dict[str, dict[str, str]]) -> tuple[list[dict], dict]:
    rng = random.Random(SEED)
    all_nodes = set(nodes)
    pairwise_hits = Counter()
    strict_hits = Counter()
    pairwise_sizes = Counter()
    strict_sizes = Counter()
    for _ in range(MONTE_CARLO_RUNS):
        retained = []
        for edge in edges:
            weight = float(documentary(edge, sources)["stress_activation_weight"])
            if rng.random() <= weight:
                retained.append(edge)
        pairwise = reachable_pairwise(retained) & all_nodes
        strict = strict_closure(retained, {ROOT_NODE}) & all_nodes
        pairwise_sizes[len(pairwise)] += 1
        strict_sizes[len(strict)] += 1
        pairwise_hits.update(pairwise)
        strict_hits.update(strict)
    rows = []
    for node_id in sorted(all_nodes):
        pair_freq = pairwise_hits[node_id] / MONTE_CARLO_RUNS
        strict_freq = strict_hits[node_id] / MONTE_CARLO_RUNS
        baseline_strict = strict_closure(edges, {ROOT_NODE}) & all_nodes
        if node_id not in baseline_strict:
            tier = "verrou_canonique"
        elif strict_freq >= 0.95:
            tier = "noyau_stable"
        elif strict_freq >= 0.50:
            tier = "dependance_sensible"
        else:
            tier = "fragile_sous_stress"
        rows.append({
            "node_id": node_id,
            "label": nodes[node_id]["label"],
            "frequence_projection": f"{pair_freq:.6f}",
            "frequence_fermeture_stricte": f"{strict_freq:.6f}",
            "classe_stabilite": tier,
        })
    summary = {
        "runs": MONTE_CARLO_RUNS,
        "seed": SEED,
        "interpretation": "Fréquences de survie sous stress paramétrique. Elles ne sont pas des probabilités de vérité.",
        "pairwise_size_distribution": dict(sorted(pairwise_sizes.items())),
        "strict_size_distribution": dict(sorted(strict_sizes.items())),
        "stable_core_nodes": [row["node_id"] for row in rows if row["classe_stabilite"] == "noyau_stable"],
        "sensitive_nodes": [row["node_id"] for row in rows if row["classe_stabilite"] == "dependance_sensible"],
        "fragile_nodes": [row["node_id"] for row in rows if row["classe_stabilite"] == "fragile_sous_stress"],
        "canonical_lock_nodes": [row["node_id"] for row in rows if row["classe_stabilite"] == "verrou_canonique"],
    }
    return rows, summary


def cycle_rows(edges: list[Edge], nodes: dict[str, dict[str, str]]) -> list[dict]:
    graph = adjacency(edges)
    components = strongly_connected_components(graph)
    rows = []
    for index, component in enumerate(components, start=1):
        self_loop = any(node in graph.get(node, set()) for node in component)
        if len(component) <= 1 and not self_loop:
            continue
        edge_ids = sorted(
            edge.edge_id for edge in edges
            if (edge.inputs | edge.outputs) & set(component)
        )
        rows.append({
            "cycle_id": index,
            "taille": len(component),
            "noeuds": "|".join(component),
            "labels": "|".join(nodes[node]["label"] for node in component),
            "hyperaretes_associees": "|".join(edge_ids),
            "inclut_verrou_interfaces": str(bool(set(component) & {"N029", "N030", "N053", "N054"})).lower(),
        })
    return rows


def build_report(edge_rows: list[dict], profile_rows: list[dict], source_rows: list[dict], mc_rows: list[dict], mc_summary: dict, cycles: list[dict], benchmark: dict) -> str:
    priorities = Counter(row["priorite_calibrage"] for row in edge_rows)
    low_doc = [row for row in edge_rows if float(row["plancher_documentaire"]) < 0.65]
    critical = [row for row in edge_rows if int(row["perte_projection_ablation"]) or int(row["perte_fermeture_stricte_ablation"])]
    source_top = sorted(source_rows, key=lambda row: (int(row["perte_projection"]), int(row["perte_fermeture_stricte"])), reverse=True)[:5]
    stable = [row for row in mc_rows if row["classe_stabilite"] == "noyau_stable"]
    sensitive = [row for row in mc_rows if row["classe_stabilite"] == "dependance_sensible"]
    fragile = [row for row in mc_rows if row["classe_stabilite"] == "fragile_sous_stress"]
    locked = [row for row in mc_rows if row["classe_stabilite"] == "verrou_canonique"]
    lines = [
        "# Calibrage structurel de l'architecture matérielle ORI-C",
        "",
        "## Portée",
        "",
        "Le graphe canonique v0.9.3 est gelé. Aucun nœud ni aucune hyperarête n'est modifié par cette campagne. Le calibrage sépare la documentation, la fonction structurelle et les dimensions encore non mesurées.",
        "",
        "Les coefficients documentaires sont des conventions explicites utilisées pour les tests de sensibilité. Les relations dont le plancher documentaire atteint 0,65 sont conservées dans tous les tirages. Seules les six relations moins documentées sont activées ou retirées. Ces coefficients ne représentent pas une probabilité de vérité et ne démontrent pas une causalité empirique.",
        "",
        "## Résultat principal",
        "",
        f"Les **{len(edge_rows)} hyperarêtes** ont été évaluées. **{len(critical)}** produisent une perte mesurable lors d'une ablation dans la projection ou la fermeture stricte. **{len(low_doc)}** ont un plancher documentaire inférieur à 0,65.",
        "",
        f"Le stress paramétrique identifie **{len(stable)} nœuds dans le noyau stable**, **{len(sensitive)} nœuds sensibles**, **{len(fragile)} nœuds fragiles** et **{len(locked)} nœuds déjà bloqués par le verrou canonique**. Cette classification décrit la dépendance au codage documentaire actuel, pas la fréquence naturelle des phénomènes.",
        "",
        "## Tri des relations",
        "",
    ]
    for name, count in sorted(priorities.items()):
        lines.append(f"- `{name}` : {count} hyperarêtes")
    lines += [
        "",
        "Le cycle des interfaces `N029-N030-N053-N054` reste une priorité propre. Il n'est pas absorbé dans un score unique, car son problème est d'abord une dépendance collective et une direction causale à documenter.",
        "",
        "## Sensibilité aux seuils documentaires",
        "",
        "| Profil | Arêtes | Projection | Fermeture stricte |",
        "|---|---:|---:|---:|",
    ]
    for row in profile_rows:
        lines.append(f"| {row['profil']} | {row['hyperaretes_conservees']} | {row['projection_atteignable']} | {row['fermeture_stricte_atteignable']} |")
    lines += [
        "",
        "La diminution du nombre de nœuds avec le seuil ne signifie pas que les processus retirés sont faux. Elle montre quelles portions de l'architecture dépendent actuellement de relations moins fortement documentées selon la convention choisie.",
        "",
        "## Dépendance aux sources",
        "",
    ]
    for row in source_top:
        lines.append(f"- `{row['source_id']}` ({row['type_source']}) : perte de projection {row['perte_projection']}, perte stricte {row['perte_fermeture_stricte']}.")
    lines += [
        "",
        "## Test de transfert externe",
        "",
        f"Le schéma a été appliqué à deux trajectoires stellaires indépendantes documentées par MESA. Le benchmark contient **{benchmark['tracks']} trajectoires**, **{benchmark['edges']} transitions** et atteint **{benchmark['reachable_nodes']} nœuds sur {benchmark['nodes']}** en fermeture stricte.",
        "",
        "Ce test montre que le format de relation, le contrôle des seuils et la fermeture stricte se transfèrent à une autre architecture historique. Il ne valide pas une loi universelle de transformation et ne prouve pas que le calibrage documentaire ORI-C est optimal.",
        "",
        "## Ce que le calibrage permet maintenant",
        "",
        "1. Séparer les relations structurellement critiques des relations seulement faiblement documentées.",
        "2. Repérer les sources dont dépend une grande partie de l'architecture.",
        "3. Identifier un noyau stable et des zones sensibles sous variations explicites de seuils.",
        "4. Conserver comme non mesurées la nécessité empirique, la suffisance, la temporalité quantitative, la réversibilité physique et l'effet d'une intervention directe.",
        "",
        "## Limite décisive",
        "",
        "Le calibrage affine le tri. Il ne remplace ni une expérience, ni une ablation naturelle, ni une prédiction hors échantillon. Une relation peut être structurellement indispensable dans le graphe et rester causalement insuffisamment démontrée dans la nature.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    edges = load_edges()
    sources = load_sources()
    nodes = load_nodes()
    all_nodes = set(nodes)

    edge_rows = analyze_edges(edges, nodes, sources)
    profile_rows = threshold_profiles(edges, sources, all_nodes)
    source_rows = source_ablations(edges, sources, all_nodes)
    mc_rows, mc_summary = monte_carlo(edges, nodes, sources)
    cycles = cycle_rows(edges, nodes)

    from benchmark_externe_stellaire.tester_transfert import run_benchmark
    benchmark = run_benchmark(write_outputs=True)

    edge_fields = list(edge_rows[0])
    write_csv(OUT / "calibrage_hyperaretes.csv", edge_rows, edge_fields)
    write_csv(OUT / "profils_seuils.csv", profile_rows, list(profile_rows[0]))
    write_csv(OUT / "ablation_sources.csv", source_rows, list(source_rows[0]))
    write_csv(OUT / "stabilite_noeuds.csv", mc_rows, list(mc_rows[0]))
    write_csv(OUT / "modules_cycliques.csv", cycles, list(cycles[0]) if cycles else ["cycle_id"])
    (OUT / "monte_carlo_resume.json").write_text(json.dumps(mc_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    synthesis = {
        "version": "v0.9.4-candidate",
        "canonical_graph_modified": False,
        "nodes": len(nodes),
        "edges": len(edges),
        "baseline_pairwise_reachable": len(reachable_pairwise(edges) & all_nodes),
        "baseline_strict_reachable": len(strict_closure(edges, {ROOT_NODE}) & all_nodes),
        "edge_priority_counts": dict(Counter(row["priorite_calibrage"] for row in edge_rows)),
        "documentary_floor_below_065": sum(float(row["plancher_documentaire"]) < 0.65 for row in edge_rows),
        "ablation_critical_edges": [row["edge_id"] for row in edge_rows if int(row["perte_projection_ablation"]) or int(row["perte_fermeture_stricte_ablation"])],
        "blocking_cycle_edges": [row["edge_id"] for row in edge_rows if row["cycle_verrou_interfaces"] == "true"],
        "monte_carlo": mc_summary,
        "external_stellar_benchmark": benchmark,
        "unmeasured_dimensions": [
            "necessite_empirique", "suffisance_empirique", "temporalite_quantitative",
            "reversibilite_physique", "intervention_directe",
        ],
        "scientific_status": "calibrage structurel et documentaire; pas une validation causale générale",
    }
    (OUT / "SYNTHESE_CALIBRAGE.json").write_text(json.dumps(synthesis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (OUT / "RAPPORT_CALIBRAGE.md").write_text(
        build_report(edge_rows, profile_rows, source_rows, mc_rows, mc_summary, cycles, benchmark),
        encoding="utf-8", newline="\n",
    )
    print(f"Calibrage terminé : {len(edges)} hyperarêtes, {len(nodes)} nœuds, {MONTE_CARLO_RUNS} tirages de stress.")
    print(f"Résultats : {OUT}")


if __name__ == "__main__":
    main()
