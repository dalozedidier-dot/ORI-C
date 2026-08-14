#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
COMMON_FLAGS={"X_matched","Theta_matched","architecture_matched","m_targeted_only","independent_units","challenge_set_predeclared","thresholds_predeclared","future_response_after_intervention"}
def main():
 d=json.loads((HERE/'PACC-MAG-INT-01.design.json').read_text(encoding='utf-8'))
 assert d['definition_id']=='PACC-INT-CHALLENGE-V1'
 assert d['scientific_protocol_change_to_MAG_PAIR_001'] is False
 assert set(d['matching_required'])==COMMON_FLAGS
 assert d['current_credit']=='none'
 assert d['challenge_design']['status']=='pilot_values_not_yet_frozen'
 assert d['materiality_thresholds']['status']=='pilot_values_not_yet_frozen'
 print('PACC-MAG-INT-01 mapping ready; pilot freeze still required; no scientific credit')
 return 0
if __name__=='__main__': raise SystemExit(main())
