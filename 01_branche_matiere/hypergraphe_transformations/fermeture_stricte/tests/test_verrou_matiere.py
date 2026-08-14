from pathlib import Path
import importlib.util
import sys

MODULE = Path(__file__).resolve().parents[1] / "analyser_verrou.py"
spec = importlib.util.spec_from_file_location("verrou", MODULE)
verrou = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = verrou
assert spec.loader
spec.loader.exec_module(verrou)


def test_canonique_reproduit_le_verrou_de_sept_noeuds():
    edges = verrou.load_edges()
    nodes = {row["node_id"] for row in verrou.read_semicolon(verrou.BASE / "noeuds.csv")}
    closure = verrou.strict_closure(edges, {"N036"})
    assert nodes - closure == {"N029", "N030", "N031", "N032", "N035", "N053", "N054"}


def test_recodage_h052_ferme_le_graphe_sans_modifier_le_canonique():
    edges = verrou.load_edges()
    nodes = {row["node_id"] for row in verrou.read_semicolon(verrou.BASE / "noeuds.csv")}
    candidate = verrou.replace_edge(edges, "H052", inputs={"N051", "N028"}, outputs={"N053", "N030"})
    assert nodes <= verrou.strict_closure(candidate, {"N036"})
    original = next(edge for edge in edges if edge.edge_id == "H052")
    assert "N030" in original.inputs


def test_les_ablations_ne_peuvent_pas_ameliorer_la_fermeture():
    edges = verrou.load_edges()
    nodes = {row["node_id"] for row in verrou.read_semicolon(verrou.BASE / "noeuds.csv")}
    rows = verrou.ablate_edges(edges, {"N036"}, nodes)
    assert len(rows) == len(edges) == 53
    assert all(row["reachable_after_ablation"] <= 46 for row in rows)

def test_hc02_ferme_le_graphe_sans_toucher_h052():
    edges = verrou.load_edges()
    nodes = {row["node_id"] for row in verrou.read_semicolon(verrou.BASE / "noeuds.csv")}
    hc02 = verrou.Edge(
        edge_id="HC02", process="bootstrap interface",
        inputs=frozenset({"N051", "N028"}), outputs=frozenset({"N030"}),
        evidence="candidate", source_id="HC02_AUDIT"
    )
    assert nodes <= verrou.strict_closure(verrou.add_edge(edges, hc02), {"N036"})
    original = next(edge for edge in edges if edge.edge_id == "H052")
    assert original.inputs == frozenset({"N051", "N028", "N030"})
    assert original.outputs == frozenset({"N053"})



def test_hc02_est_qualifiee_en_extension_sans_recrire_le_baseline():
    import json
    cfg = json.loads((MODULE.parent / "HC02_CROUTE_HYDROSPHERE_INTERFACE.json").read_text(encoding="utf-8"))
    assert cfg["status"] == "evidence_qualified_extension"
    assert set(cfg["semantic_target"]["components"].values())
    assert all(str(v).startswith("supported") for v in cfg["semantic_target"]["components"].values())
    assert cfg["canonical_change"] is False
    assert cfg["mathematical_closure_if_added"] == "53/53"


def test_hc02_matrice_primaire_4_sur_4():
    import csv
    with (MODULE.parent / "HC02_EVIDENCE_MATRIX.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter=";"))
    assert {r["component"] for r in rows} == {"interface", "fluid_chemistry", "gradients", "catalysis"}
    assert all(r["verdict"] == "supported" for r in rows)
    assert {"10.3389/feart.2018.00180", "10.1029/2021GC009827", "10.1038/s41467-026-71130-7"} <= {r["doi"] for r in rows}
