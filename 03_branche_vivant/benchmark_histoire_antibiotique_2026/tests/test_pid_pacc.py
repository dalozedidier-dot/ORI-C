from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load():
    path = ROOT / "analyser_pid.py"
    spec = importlib.util.spec_from_file_location("antibiotic_pid", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_pacc_support_is_bounded_and_history_conditioned():
    module = load()
    df = pd.DataFrame(
        [
            {"Limitation": "N", "Antibiotic": "A", "Ancestor": "H1", "Strain": 1, "MIC (ug/mL)": 1},
            {"Limitation": "N", "Antibiotic": "A", "Ancestor": "H1", "Strain": 2, "MIC (ug/mL)": 1},
            {"Limitation": "N", "Antibiotic": "A", "Ancestor": "H2", "Strain": 3, "MIC (ug/mL)": 2},
            {"Limitation": "N", "Antibiotic": "A", "Ancestor": "H2", "Strain": 4, "MIC (ug/mL)": 4},
        ]
    )
    result = module.pacc_from_frame(df)
    assert result["strata_count"] == 2
    assert 0.0 <= result["mean_P_acc"] <= 1.0
    assert sorted(row["P_acc"] for row in result["rows"]) == [1 / 3, 2 / 3]


def test_real_pid_result_exposes_retrospective_pacc_after_execution():
    result = json.loads((ROOT / "resultats/PID_X_M_A.json").read_text(encoding="utf-8"))
    pacc = result["P_acc_retrospective"]
    assert pacc["strata_count"] == 48
    assert 0.0 < pacc["mean_P_acc"] < 1.0
    assert pacc["same_complexity_history_permutation"]["p_one_sided_observed_support_narrower_than_shuffled"] < 0.01
