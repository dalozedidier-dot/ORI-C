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
