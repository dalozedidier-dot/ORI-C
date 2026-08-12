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


def test_publication_robustness_is_reported_without_upgrading_claim() -> None:
    result = MODULE.analyse(Path(__file__).parents[1])
    for row in result["results"]:
        robustness = row["publication_robustness"]
        assert robustness["leave_one_publication_out"]["runs"] > 0
        assert robustness["publication_cluster_bootstrap"]["repeats"] == 1000
        assert 0.0 < robustness["sampling_concentration"]["largest_publication_fraction"] <= 1.0
    assert "no_conservation_claim" in result["verdict"]


def test_stable_json_numbers_absorb_last_bit_platform_drift() -> None:
    a = MODULE._stable_json_numbers({"value": 0.47226386806596704})
    b = MODULE._stable_json_numbers({"value": 0.47226386806599704})
    assert a == b == {"value": 0.472263868066}
