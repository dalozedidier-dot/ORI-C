from __future__ import annotations

import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]


def load_module():
    specification = importlib.util.spec_from_file_location(
        "wong_seguin_real", HERE / "analyser_wong_seguin_2015.py"
    )
    module = importlib.util.module_from_spec(specification)
    assert specification.loader is not None
    specification.loader.exec_module(module)
    return module


def test_official_archive_members_and_hashes_are_preserved():
    source_path = ROOT / "donnees_externes/wong_seguin_2015/SOURCE.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    assert source["verification"]["all_official_members_present"] is True
    assert source["verification"]["all_official_md5_match"] is True
    for item in source["file_provenance"]:
        path = source_path.parent / item["local_path"]
        assert path.is_file()
        assert path.stat().st_size == item["size_bytes"]
        assert load_module().sha256(path) == item["sha256"]


def test_real_join_has_one_row_per_evolved_population():
    frame = load_module().prepare()
    assert len(frame) == 46
    assert frame["Population"].nunique() == 46
    assert frame["Progenitor_id"].nunique() == 6
    assert frame["Evolved_MIC_ng_mL"].gt(0).all()


def test_result_remains_negative_and_non_confirmatory():
    result = json.loads(
        (HERE / "resultats/RESULTAT_WONG_SEGUIN_2015.json").read_text(encoding="utf-8")
    )
    assert result["mapping"]["n_independent_units"] == 46
    assert result["results"]["history_gain_percent"] < 0
    assert result["results"]["permutation_p_one_sided"] > 0.05
    assert result["verdict"] == "does_not_support_incremental_founder_mutation_information"
    assert result["qualification"]["synthetic_or_simulated_scientific_data"] is False
    assert result["qualification"]["strict_donofrio_replication"] is False
    assert result["qualification"]["section_XIV_credit"] is False
