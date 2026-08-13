import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]


def test_santos_lopez_benchmark_reproduit_sans_requalification_stricte():
    result = json.loads((HERE / "resultats/RESULTAT.json").read_text(encoding="utf-8"))
    assert result["reference_numeric_rule_support"] is True
    assert abs(result["metrics"]["RMSE_state_only"] - 0.9374820345860344) < 1e-12
    assert abs(result["metrics"]["RMSE_state_plus_history"] - 0.732491587271193) < 1e-12
    assert abs(result["metrics"]["relative_RMSE_gain"] - 0.2186606673538649) < 1e-12
    assert result["strict_prediction_success"] is False
    assert result["counts_for_section_XIV_condition_3"] is False
    assert result["counts_for_section_XIV_condition_10"] is False
