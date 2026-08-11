import importlib.util
from pathlib import Path


PATH = Path(__file__).parents[1] / "src" / "analyser_information_interetages.py"
SPEC = importlib.util.spec_from_file_location("interstage", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_normalized_mutual_information_bounds():
    assert MODULE.normalized_mutual_information(["a", "a", "b", "b"], ["x", "x", "y", "y"]) == 1.0
    assert MODULE.normalized_mutual_information(["a", "a", "b", "b"], ["x", "y", "x", "y"]) == 0.0


def test_real_tables_preserve_same_grain_rows():
    root = Path(__file__).parents[1]
    result = MODULE.analyse(root)
    assert len(result["results"]) == 2
    assert sum(row["same_carrier_rows"] for row in result["results"]) > 10_000
    assert all(0 <= row["normalized_I_stellar_type_host"] <= 1 for row in result["results"])
