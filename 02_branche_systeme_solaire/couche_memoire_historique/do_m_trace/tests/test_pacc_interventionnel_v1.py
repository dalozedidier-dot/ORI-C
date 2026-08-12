import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]


def test_validation_pacc_interventionnel_reproduit_exo_dom():
    result = json.loads((HERE / 'resultats/VALIDATION_PACC_INTERVENTIONNEL_V1.json').read_text(encoding='utf-8'))
    assert result['passed'] is True
    assert result['counts_for_section_xiv_condition_9'] is False
    assert result['estimate']['causal_qualified'] is True
    assert abs(result['estimate']['P_acc_control_median'] - 0.91) < 1e-12
    assert abs(result['estimate']['P_acc_intervention_median'] - 0.87) < 1e-12
    assert abs(result['estimate']['Delta_P_acc_median'] + 0.04) < 1e-12
    assert result['estimate']['sham']['passes'] is True
