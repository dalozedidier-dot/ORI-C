from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    specification = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(specification)
    assert specification.loader is not None
    specification.loader.exec_module(module)
    return module


def test_pacc_has_intervention_and_dimension_levels():
    result = load("mesurer_pacc_astronomique").main()
    assert result["interventions"] == 6
    assert 0 <= result["Pacc_interventions"] <= 1
    assert 0 <= result["Pacc_dimensions"] <= 1
    assert result["total_dimension_cells"] == 18
    assert result["Pacc_dimensions"] < 1


def test_c2b_is_frozen_with_holdout_seeds():
    result = load("preenregistrer_c2b").main()
    assert len(result["protocol_sha256"]) == 64
    assert result["id"] == "WP-C2b"
    assert len(result["holdout_seeds"]) == 8
    assert len(set(result["holdout_seeds"])) == 8


def test_speleothem_audit_with_fixture(tmp_path, monkeypatch):
    module = load("auditer_speleothemes")
    source = tmp_path / "speleothem-d18o-0-22k.csv"
    pd.DataFrame(
        {
            "site": ["A", "A", "B"],
            "age_ka": [0.1, 5.0, 21.0],
            "d18O": [-4.0, -3.5, -2.0],
            "latitude": [45.0, 45.0, -20.0],
        }
    ).to_csv(source, index=False)
    result = module.audit(source)
    assert result["status"] == "audited"
    assert result["rows_age_isotope"] == 3
    assert result["independent_site_count"] == 2
