from __future__ import annotations

import json
from pathlib import Path


def test_generated_outputs_have_three_separate_branches():
    root = Path(__file__).resolve().parents[1] / "resultats"
    summary = json.loads((root / "synthese_trois_branches.json").read_text(encoding="utf-8"))
    assert set(summary["branches"]) == {"matiere", "systeme_solaire_et_terre", "vivant"}
    assert summary["branches"]["vivant"]["main_results"]["prebiotic_real_lineage_data"] is False
    assert "ne valide pas ORI-C" in summary["global_verdict"]


def test_report_exists_and_keeps_global_verdict_limited():
    path = Path(__file__).resolve().parents[1] / "resultats" / "RAPPORT_CAMPAGNE_MAXIMALE.md"
    text = path.read_text(encoding="utf-8")
    assert "## 1. Matière" in text
    assert "## 2. Système solaire et Terre" in text
    assert "## 3. Vivant" in text
    assert "sans fournir la prédiction positive transversale" in text
