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


def test_realistic_plate_parser_uses_first_well_block_and_ignores_auxiliary_columns(tmp_path):
    module = load()
    path = tmp_path / "UR3_log.xlsx"
    wells = [f"{row}{column}" for row in "ABCDEFGH" for column in range(1, 13)]
    data = pd.DataFrame(
        {
            0: [None] + wells + [None] + wells,
            1: ["29G0D"] + list(np.linspace(0.1, 0.2, 96)) + [None] + [99.0] * 96,
            2: ["29G1D-F"] + [0.05] * 96 + [None] + [99.0] * 96,
            3: ["29G1D"] + list(np.linspace(0.2, 0.3, 96)) + [None] + [99.0] * 96,
            4: [None] + [None] * 96 + [None] + [99.0] * 96,
            5: [None] + list(np.linspace(0.3, 0.4, 96)) + [None] + [99.0] * 96,
            6: ["29G3D"] + list(np.linspace(0.4, 0.5, 96)) + [None] + [99.0] * 96,
        }
    )
    codes = pd.DataFrame({0: ["29G0D"] + ["A1"] * 48, 1: ["29G1D"] + ["('A1', 'A1')"] * 48})
    with pd.ExcelWriter(path) as writer:
        data.to_excel(writer, sheet_name="drdata", header=False, index=False)
        data.to_excel(writer, sheet_name="seldata", header=False, index=False)
        codes.to_excel(writer, sheet_name="drcode", header=False, index=False)
        codes.to_excel(writer, sheet_name="selcode", header=False, index=False)
    matrix = module.numeric_matrix(path, "drdata")
    assert matrix.shape == (96, 4)
    assert list(matrix.columns) == ["g0", "g1", "g2", "g3"]
    assert matrix.loc["A1", "g0"] == 0.1
    assert matrix.loc["A1", "g2"] == 0.3
    assert 99.0 not in matrix.to_numpy()


def test_transfer_parser_prefers_explicit_pairs_over_single_well_column(tmp_path):
    module = load()
    path = tmp_path / "FR1_log.xlsx"
    values = pd.DataFrame({0: np.arange(12, dtype=float), 1: np.arange(12, dtype=float) + 100})
    codes = pd.DataFrame(
        {
            0: ["G0D"] + ["A1"] * 12,
            1: ["G1D"] + ["('A2', 'A1')"] + ["('A1', 'A2')"] + ["('A3', 'A3')"] * 10,
            2: ["G1D"] + ["A2"] * 12,
        }
    )
    with pd.ExcelWriter(path) as writer:
        values.to_excel(writer, sheet_name="drdata", header=False, index=False)
        values.to_excel(writer, sheet_name="seldata", header=False, index=False)
        codes.to_excel(writer, sheet_name="drcode", header=False, index=False)
        codes.to_excel(writer, sheet_name="selcode", header=False, index=False)
    data = module.pairs(path, "FR")
    first = data[(data["arm"] == "drift") & (data["recipient"] == "A1")].iloc[0]
    assert first["donor"] == "A2"
    assert first["parent"] == 1.0
    assert first["offspring"] == 100.0

def test_canonical_numbers_absorb_python_312_313_micro_rounding():
    module = load()
    python_312 = [
        0.06690393379475486,
        0.0739995249584005,
        0.07820001718266686,
        0.06103300460982823,
        -0.06941470029147188,
        0.025529538435400463,
        0.7230421932936663,
        0.663904733093481,
        0.7642621398380935,
        0.7466668339764724,
    ]
    python_313 = [
        0.06690393379475482,
        0.07399952495840054,
        0.07820001718266696,
        0.06103300460982825,
        -0.06941470029147194,
        0.025529538435400456,
        0.7230421932936661,
        0.6639047330934812,
        0.7642621398380934,
        0.7466668339764723,
    ]
    assert module.canonicalize_numbers(python_312) == module.canonicalize_numbers(python_313)

