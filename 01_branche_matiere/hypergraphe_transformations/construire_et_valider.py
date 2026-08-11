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
    w = csv.DictWriter(
        f,
        fieldnames=cross[0].keys(),
        delimiter=";",
        lineterminator="\n",
    )
    w.writeheader()
    w.writerows(cross)

# Deux lectures de la continuité sont publiées séparément. La projection paire
# à paire répond à la question « existe-t-il une succession de liens ? ». La
# fermeture hypergraphique stricte exige que toutes les entrées d'un processus
# multi-entrée soient déjà disponibles. Confondre les deux transforme une
# hyperarête A|B -> C en deux réactions fictives A -> C et B -> C.
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

def joignables_projection(depart):
    vus, pile = {depart}, [depart]
    while pile:
        for suivant in adjacence[pile.pop()]:
            if suivant not in vus:
                vus.add(suivant)
                pile.append(suivant)
    return vus

def fermeture_hypergraphique(departs):
    vus = set(departs)
    change = True
    while change:
        change = False
        for e in edges:
            ins = set(e["entrees"].split("|"))
            outs = set(e["sorties"].split("|"))
            if ins <= vus:
                ajouts = outs - vus
                if ajouts:
                    vus.update(ajouts)
                    change = True
    return vus

atteints_projection = (
    set().union(*(joignables_projection(r) for r in racines)) if racines else set()
)
atteints_stricts = fermeture_hypergraphique(racines)
orphelins_projection = sorted(node_ids - atteints_projection)
orphelins_stricts = sorted(node_ids - atteints_stricts)

if len(racines) != 1:
    errors.append(f"cloture: {len(racines)} racines au lieu d'une seule ({racines})")
for n in orphelins_projection:
    errors.append(f"projection: {n} inatteignable depuis le socle cosmique")

blocages_stricts = {}
for n in orphelins_stricts:
    producteurs = []
    for e in edges:
        if n not in e["sorties"].split("|"):
            continue
        ins = e["entrees"].split("|")
        producteurs.append({
            "edge_id": e["edge_id"],
            "processus": e["processus"],
            "entrees": ins,
            "entrees_manquantes": sorted(x for x in ins if x not in atteints_stricts),
        })
    blocages_stricts[n] = producteurs
warnings = []
if orphelins_stricts:
    warnings.append(
        "La projection paire à paire est connectée, mais la fermeture "
        f"hypergraphique stricte laisse {len(orphelins_stricts)} nœuds inatteignables."
    )

types = Counter(e["type"] for e in edges); proof = Counter(e["statut_preuve"] for e in edges)
multi_in = sum(len(e["entrees"].split("|")) > 1 for e in edges)
multi_out = sum(len(e["sorties"].split("|")) > 1 for e in edges)
self_transmission = sum(bool(set(e["entrees"].split("|")) & set(e["sorties"].split("|"))) for e in edges)
scenario = sum("scenario" in e["statut_preuve"] or "hypothese" in e["statut_preuve"] for e in edges)
report = {
    "status": (
        "invalid" if errors else
        "valid_with_strict_closure_gap" if orphelins_stricts else
        "valid"
    ),
    "errors": errors,
    "warnings": warnings,
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
        "single_declared_root": len(racines) == 1,
        "pairwise_projection_connected": not orphelins_projection,
        "strict_hypergraph_closed": not orphelins_stricts,
    },
    "declared_roots": racines,
    "pairwise_projection": {
        "nodes_reachable_from_root": len(atteints_projection),
        "unreachable_nodes": orphelins_projection,
        "scope": "Projection de chaque hyperarête en liens paire à paire. Elle ne vérifie pas la disponibilité simultanée de toutes les entrées.",
    },
    "strict_hypergraph_closure": {
        "nodes_reachable_from_root": len(atteints_stricts),
        "unreachable_nodes": orphelins_stricts,
        "blocking_dependencies": blocages_stricts,
        "scope": "Fermeture par point fixe exigeant toutes les entrées de chaque hyperarête.",
    },
    "nodes_reachable_from_root": len(atteints_stricts),
    "unreachable_nodes": orphelins_stricts,
    "scope": "Hypergraphe mécanistique initial. La connectivité de sa projection et sa fermeture hypergraphique stricte sont distinctes. Il ne valide pas ORI-C ni ne remplace une mesure quantitative d'inventaire accessible."
}
(HERE / "validation_hypergraphe.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
if errors: raise SystemExit(1)
