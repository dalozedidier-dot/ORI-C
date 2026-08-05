from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load():
    specification = importlib.util.spec_from_file_location("antibiotic", ROOT / "analyser.py")
    module = importlib.util.module_from_spec(specification)
    assert specification.loader is not None
    specification.loader.exec_module(module)
    return module


def test_protocol_exists():
    assert (ROOT / "PROTOCOLE.md").exists()


def test_grouped_model_can_use_history_signal():
    module = load()
    rows = []
    for strain_index in range(20):
        history = "A" if strain_index % 2 == 0 else "B"
        for antibiotic in ("drug1", "drug2"):
            rows.append(
                {
                    "strain": f"s{strain_index}",
                    "limitation": "N",
                    "ancestor": history,
                    "antibiotic": antibiotic,
                }
            )
    data = pd.DataFrame(rows)
    y = pd.Series(
        [1.0 if row == "A" else 4.0 for row in data["ancestor"]],
        dtype=float,
    )
    groups = data["strain"]
    state = module.predictions(data, y, groups, ["limitation", "antibiotic"])
    history = module.predictions(data, y, groups, ["limitation", "antibiotic", "ancestor"])
    assert module.rmse(y, history) < module.rmse(y, state)
    assert np.isfinite(history).all()
