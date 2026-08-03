"""Construit les produits auditables de la généalogie sans modifier la base historique."""
from __future__ import annotations
import csv, json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REL = ROOT / "00_socle" / "carte_relationnelle" / "data" / "relations_oric_47_provisoires.csv"

MAP = {
    "MATR": "filiation_materielle", "ENBL": "condition_ouverture",
    "ENVR": "transformation_environnementale", "FEED": "transformation_environnementale",
    "CATL": "condition_ouverture", "STAB": "condition_ouverture", "CONT": "condition_ouverture",
    "CNST": "contrainte_inventaire", "DEPG": "dependance_non_genealogique",
    "DESC": "dependance_non_genealogique", "INCO": "transmission_trace_historique",
}

def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))

nodes = rows(HERE / "noeuds.csv")
edges = rows(HERE / "hyperaretes.csv")
sources = rows(HERE / "sources.csv")
node_ids = {r["node_id"] for r in nodes}; source_ids = {r["source_id"] for r in sources}
errors = []
for e in edges:
    ins = e["entrees"].split("|"); outs = e["sorties"].split("|")
    for n in ins + outs:
        if n not in node_ids: errors.append(f"{e['edge_id']}: noeud absent {n}")
    if e["source_id"] not in source_ids: errors.append(f"{e['edge_id']}: source absente")
    if not e["statut_preuve"]: errors.append(f"{e['edge_id']}: statut vide")

old = rows(REL)
cross = []
for r in old:
    cross.append({
        "source": r["source"], "target": r["target"], "code_relation": r["relation"],
        "classe_genealogique": MAP.get(r["relation"], "a_revoir"),
        "portee_originale": r["portee_du_lien"], "niveau_preuve": r["niveau_preuve"],
        "reference_cle": r["reference_cle"],
    })
with (HERE / "reclassement_relations.csv").open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cross[0].keys(), delimiter=";"); w.writeheader(); w.writerows(cross)

# Clôture généalogique. Un nœud consommé sans jamais être produit est une racine :
# soit un apport externe déclaré, soit un trou. Les arêtes à point partagé (règle 4
# du README : transport, survie, recyclage) ne comptent pas comme production, sinon
# tout auto-cycle se déclarerait clos. Ce test a révélé que la chaîne poussière
# N008→N009→N010→N008 tournait sur elle-même sans aucune alimentation matérielle.
produits, consommes = set(), set()
adjacence = defaultdict(set)
for e in edges:
    ins, outs = e["entrees"].split("|"), e["sorties"].split("|")
    partage = set(ins) & set(outs)
    consommes.update(ins)
    produits.update(n for n in outs if n not in partage)
    for a in ins:
        adjacence[a].update(n for n in outs if n != a)
racines = sorted(consommes - produits)

def joignables(depart):
    vus, pile = {depart}, [depart]
    while pile:
        for suivant in adjacence[pile.pop()]:
            if suivant not in vus:
                vus.add(suivant); pile.append(suivant)
    return vus

atteints = set().union(*(joignables(r) for r in racines)) if racines else set()
orphelins = sorted(node_ids - atteints)
if len(racines) != 1:
    errors.append(f"cloture: {len(racines)} racines au lieu d'une seule ({racines})")
for n in orphelins:
    errors.append(f"cloture: {n} inatteignable depuis le socle cosmique")

types = Counter(e["type"] for e in edges); proof = Counter(e["statut_preuve"] for e in edges)
multi_in = sum(len(e["entrees"].split("|")) > 1 for e in edges)
multi_out = sum(len(e["sorties"].split("|")) > 1 for e in edges)
self_transmission = sum(bool(set(e["entrees"].split("|")) & set(e["sorties"].split("|"))) for e in edges)
scenario = sum("scenario" in e["statut_preuve"] or "hypothese" in e["statut_preuve"] for e in edges)
report = {
    "status": "valid" if not errors else "invalid", "errors": errors,
    "nodes": len(nodes), "hyperedges": len(edges), "sources": len(sources),
    "multi_input_edges": multi_in, "multi_output_edges": multi_out,
    "recycling_or_transport_edges_with_shared_endpoint": self_transmission,
    "explicit_scenario_or_hypothesis_edges": scenario,
    "edge_types": dict(types), "evidence_statuses": dict(proof),
    "old_relations_reclassified": len(cross),
    "old_relation_classes": dict(Counter(r["classe_genealogique"] for r in cross)),
    "tests": {
        "not_a_linear_tree": multi_in > 0 and multi_out > 0 and self_transmission > 0,
        "all_endpoints_exist": not any("noeud absent" in x for x in errors),
        "all_edges_sourced": not any("source absente" in x for x in errors),
        "competing_scenarios_explicit": scenario >= 3,
        "four_relation_families_represented": len(set(r["classe_genealogique"] for r in cross)) >= 4,
        "genealogically_closed": not racines or (len(racines) == 1 and not orphelins),
        "cosmic_continuity_complete": not orphelins,
    },
    "declared_roots": racines,
    "nodes_reachable_from_root": len(atteints),
    "unreachable_nodes": orphelins,
    "scope": "Hypergraphe mécanistique initial. Il organise des relations sourcées et des scénarios; il ne valide pas ORI-C ni ne remplace une mesure quantitative d'inventaire accessible."
}
(HERE / "validation_hypergraphe.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
if errors: raise SystemExit(1)
