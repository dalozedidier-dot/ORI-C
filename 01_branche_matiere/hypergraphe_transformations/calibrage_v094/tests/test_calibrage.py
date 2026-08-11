from pathlib import Path
import importlib.util
import json
import sys

MODULE = Path(__file__).resolve().parents[1] / "calibrage_relations.py"
spec = importlib.util.spec_from_file_location("calibrage_v094", MODULE)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
assert spec.loader
spec.loader.exec_module(module)


def test_baseline_reste_53_projection_et_46_strict():
    edges = module.load_edges()
    nodes = set(module.load_nodes())
    assert len(module.reachable_pairwise(edges) & nodes) == 53
    assert len(module.strict_closure(edges, {module.ROOT_NODE}) & nodes) == 46


def test_calibrage_ne_modifie_pas_les_fichiers_canoniques():
    before_edges = (module.BASE / "hyperaretes.csv").read_bytes()
    before_nodes = (module.BASE / "noeuds.csv").read_bytes()
    module.main()
    assert (module.BASE / "hyperaretes.csv").read_bytes() == before_edges
    assert (module.BASE / "noeuds.csv").read_bytes() == before_nodes


def test_cycle_verrou_est_identifie():
    rows = module.analyze_edges(module.load_edges(), module.load_nodes(), module.load_sources())
    ids = {row["edge_id"] for row in rows if row["cycle_verrou_interfaces"] == "true"}
    assert {"H030", "H031", "H052", "H053"} <= ids


def test_benchmark_stellaire_est_strictement_ferme():
    from benchmark_externe_stellaire.tester_transfert import run_benchmark
    result = run_benchmark(write_outputs=False)
    assert result["tracks"] == 2
    assert result["strictly_closed"] is True
    assert result["reachable_nodes"] == result["nodes"]


def test_resultat_synthese_conserve_les_dimensions_non_mesurees():
    module.main()
    payload = json.loads((module.OUT / "SYNTHESE_CALIBRAGE.json").read_text(encoding="utf-8"))
    assert payload["canonical_graph_modified"] is False
    assert "necessite_empirique" in payload["unmeasured_dimensions"]
    assert payload["external_stellar_benchmark"]["strictly_closed"] is True
