import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]


def load():
    return json.loads((HERE / 'PROTOCOLE_PACC_CAUSAL_PROSPECTIF_V1.json').read_text(encoding='utf-8'))


def test_historical_data_never_reclassified():
    p = load()
    assert p['prior_dataset']['pairs_already_analysed'] == 11760
    assert p['prior_dataset']['allowed_use'] == 'calibration_and_design_only'


def test_scientific_design_is_complete_and_fixed():
    p = load()
    assert p['m']['operator']
    assert len(p['Theta']['challenge_set']) == 12
    assert len(p['R']['response_dimensions']) == 4
    assert p['P_acc']['materiality_thresholds'] == [0.10, 0.10, 0.05, 0.10]
    assert p['P_acc']['denominator_cells'] == 48
    assert p['independent_unit']['planned_n'] == 48
    assert p['SESOI_and_power']['SESOI_abs_Delta_P_acc'] == 0.08
    assert p['preregistration_gate']['scientific_fields_complete'] is True


def test_execution_remains_blocked_until_public_registration():
    p = load()
    assert p['preregistration_gate']['current_gate_open'] is False
    assert 'public OSF registration URL or equivalent immutable registration identifier' in p['preregistration_gate']['required_before_execution']
