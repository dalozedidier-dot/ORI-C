from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load():
    specification = importlib.util.spec_from_file_location("vesicles", ROOT / "analyser_lignees.py")
    module = importlib.util.module_from_spec(specification)
    assert specification.loader is not None
    specification.loader.exec_module(module)
    return module


def test_pair_parser_uses_donor_recipient_codes(tmp_path):
    path = tmp_path / "FR1_log.xlsx"
    values = pd.DataFrame({0: np.arange(12, dtype=float), 1: np.arange(12, dtype=float) + 100})
    # A1 reçoit A2, A2 reçoit A1. Les autres puits se recopient.
    codes = pd.DataFrame({0: ["A2", "A1", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A12"]})
    with pd.ExcelWriter(path) as writer:
        values.to_excel(writer, sheet_name="drdata", header=False, index=False)
        (values + 10).to_excel(writer, sheet_name="seldata", header=False, index=False)
        codes.to_excel(writer, sheet_name="drcode", header=False, index=False)
        codes.to_excel(writer, sheet_name="selcode", header=False, index=False)
    data = load().pairs(path, "FR")
    assert not data.empty
    assert set(data["arm"]) == {"drift", "selection"}
    assert (data["mapping_mode"] == "coded_lineage").all()
    first = data[(data["arm"] == "drift") & (data["recipient"] == "A1")].iloc[0]
    assert first["donor"] == "A2"
    assert first["parent"] == 1.0
    assert first["offspring"] == 100.0


def test_lineage_permutation_detects_strong_pairing():
    module = load()
    data = pd.DataFrame(
        {
            "condition": ["FR"] * 30,
            "arm": ["selection"] * 30,
            "transition": [0] * 30,
            "parent": np.arange(30, dtype=float),
            "offspring": np.arange(30, dtype=float) + 0.01,
        }
    )
    result = module.lineage_permutation_test(data, repeats=200)
    assert result["observed_parent_offspring_r"] > 0.99
    assert result["permutation_p_one_sided"] < 0.05
