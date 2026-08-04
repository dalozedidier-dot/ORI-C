#!/usr/bin/env python3
"""Teste le transfert du schéma de fermeture sur deux trajectoires MESA.

Le benchmark vérifie la portabilité du formalisme de relations et de seuils.
Il ne valide ni la causalité universelle d'ORI-C ni la justesse physique de MESA.
"""
from __future__ import annotations
import csv
import json
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "resultats"

@dataclass(frozen=True)
class Edge:
    edge_id: str
    track: str
    inputs: frozenset[str]
    outputs: frozenset[str]
    threshold_explicit: bool
    criterion: str


def read_rows():
    with (HERE / "trajectoires_mesa.csv").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def load_edges():
    return [Edge(
        row["edge_id"], row["track"],
        frozenset(filter(None, row["entrees"].split("|"))),
        frozenset(filter(None, row["sorties"].split("|"))),
        row["seuil_explicit"] == "oui", row["critere"],
    ) for row in read_rows()]


def strict_closure(edges, roots):
    available = set(roots)
    changed = True
    while changed:
        changed = False
        for edge in edges:
            if edge.inputs <= available and not edge.outputs <= available:
                available.update(edge.outputs)
                changed = True
    return available


def run_benchmark(write_outputs=False):
    edges = load_edges()
    roots = {"M1_ROOT", "M12_ROOT"}
    nodes = set(roots)
    for edge in edges:
        nodes.update(edge.inputs)
        nodes.update(edge.outputs)
    closure = strict_closure(edges, roots)
    track_edges = {}
    for track in sorted({edge.track for edge in edges}):
        track_edges[track] = [edge.edge_id for edge in edges if edge.track == track]
    result = {
        "tracks": len(track_edges),
        "nodes": len(nodes),
        "edges": len(edges),
        "roots": sorted(roots),
        "reachable_nodes": len(closure),
        "strictly_closed": closure == nodes,
        "explicit_threshold_edges": sum(edge.threshold_explicit for edge in edges),
        "cycles": 0,
        "track_edges": track_edges,
        "interpretation": "Transfert du schéma relationnel et de la fermeture stricte vers deux trajectoires de modèles stellaires indépendantes.",
        "limit": "Benchmark de représentation. Il ne constitue ni une validation observationnelle de MESA ni une loi universelle ORI-C.",
    }
    if write_outputs:
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "benchmark_stellaire_mesa.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return result

if __name__ == "__main__":
    result = run_benchmark(write_outputs=True)
    print(json.dumps(result, ensure_ascii=False, indent=2))
