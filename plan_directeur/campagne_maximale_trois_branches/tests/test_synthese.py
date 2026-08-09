from __future__ import annotations

import json
from pathlib import Path


def test_generated_outputs_have_three_separate_branches():
    root = Path(__file__).resolve().parents[1] / "resultats"
    summary = json.loads((root / "synthese_trois_branches.json").read_text(encoding="utf-8"))
    assert set(summary["branches"]) == {"matiere", "systeme_solaire_et_terre", "vivant"}
    assert summary["campaign"] == "integrated_repository_evidence_synthesis"
    vivant = summary["branches"]["vivant"]["main_results"]
    assert vivant["legacy_prebiotic_real_lineage_data"] is False
    assert vivant["current_real_biological_results_included"] is True
    assert vivant["donofrio_rows"] == 288
    assert vivant["vesicle_parent_offspring_pairs"] == 11760
    assert summary["branches"]["matiere"]["main_results"][
        "material_memory_transversality_verdict"
    ] == "ne_soutient_pas"
    assert "ne valide pas ORI-C" in summary["global_verdict"]


def test_report_exists_and_keeps_global_verdict_limited():
    path = Path(__file__).resolve().parents[1] / "resultats" / "RAPPORT_CAMPAGNE_MAXIMALE.md"
    text = path.read_text(encoding="utf-8")
    assert "## 1. Matière" in text
    assert "## 2. Système solaire et Terre" in text
    assert "## 3. Vivant" in text
    assert "D'Onofrio" in text
    assert "11760 relations parent-descendant" in text
    assert "C-MAT-MEM-05" in text
    assert "ORI-C n'est donc pas validé" in text
