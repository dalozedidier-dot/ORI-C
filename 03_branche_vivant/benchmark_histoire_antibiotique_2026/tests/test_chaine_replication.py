from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]


def test_replication_chain_is_fail_closed_and_thresholds_are_frozen():
    chain = json.loads((HERE / "CHAINE_REPLICATION_INDEPENDANTE.json").read_text(encoding="utf-8"))
    assert chain["frozen_rule"]["gain_percent_min"] == 5.0
    assert chain["frozen_rule"]["thresholds_moved"] is False
    assert chain["current_verdict"] == "no_strict_independent_positive_replication_completed"
    assert all(candidate["section_XIV_10_credit"] is False for candidate in chain["candidates_in_order"])
    assert (HERE / "AUDIT_WONG_SEGUIN_2015.json").is_file()
