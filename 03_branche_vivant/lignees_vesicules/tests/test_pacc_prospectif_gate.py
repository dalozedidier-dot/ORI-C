import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]


def test_ves_pacc_int_01_ne_requalifie_pas_les_donnees_historiques():
    protocol = json.loads((HERE / 'PROTOCOLE_PACC_CAUSAL_PROSPECTIF_V1.json').read_text(encoding='utf-8'))
    assert protocol['id'] == 'VES-PACC-INT-01'
    assert protocol['prior_dataset']['allowed_use'] == 'calibration_and_design_only'
    assert protocol['preregistration_gate']['current_gate_open'] is False
    assert protocol['m']['operator'] is None
    assert protocol['Theta']['challenge_set'] is None
    assert protocol['R']['response_dimensions'] is None
    assert protocol['P_acc']['materiality_thresholds'] is None
