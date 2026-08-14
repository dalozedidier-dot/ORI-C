#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'plan_directeur'/'READINESS_VERROUS.json'

def load(rel): return json.loads((ROOT/rel).read_text(encoding='utf-8'))

def main():
    hc=load('01_branche_matiere/hypergraphe_transformations/fermeture_stricte/HC02_CROUTE_HYDROSPHERE_INTERFACE.json')
    mag=load('01_branche_matiere/memoire_materielle_reelle/experiences_appariees/MAG-PAIR-001.execution.json')
    ves=load('03_branche_vivant/lignees_vesicules/VES-PACC-INT-01.execution.json')
    ltee=load('plan_directeur/campagne_centrale_2026_08_11/PREDICTIONS_PROSPECTIVES/LTEE_MATERIAL_AND_CONTACT_ROUTE_2026-08-14.json')
    micplan=load('plan_directeur/campagne_centrale_2026_08_11/PREDICTIONS_PROSPECTIVES/REPLICATION_LTEE_NEW_MIC_PLAN.json')
    pmag=load('01_branche_matiere/memoire_materielle_reelle/experiences_appariees/PACC-MAG-INT-01.design.json')
    missing_mag=[k for k,v in mag['frozen_fields'].items() if v is None]
    payload={
      'schema':'oric.active-lock-readiness.v1',
      'generated_from_versioned_state':True,
      'hc02':{'status':hc['status'],'baseline':'46/53','extension':'53/53','next':'independent_semantic_review'},
      'mag_pair_001':{'status':mag['status'],'missing_lab_fields':missing_mag,'missing_count':len(missing_mag),'next':'non_confirmatory_instrument_pilot'},
      'ves_pacc_int_01':{'status':ves['status'],'remaining_execution_blockers':ves['remaining_execution_blockers'],'next':'confirm_single_lab_then_public_registration'},
      'vivant_new_mic':{'status':micplan['status'],'strict_route':micplan['routes']['A_strict_replication']['status'],'fast_route':micplan['routes']['B_fast_prospective_generalisation']['status'],'next':'choose_strict_or_fast_route_before_outcome_access'},
      'cross_branch_pacc':{'definition_id':pmag['definition_id'],'status':pmag['status'],'target':'XIV-11 after both matter and living qualify'},
      'section_XIV':'unchanged_7_of_12_until_real_execution_or_replication'
    }
    OUT.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(payload,indent=2,ensure_ascii=False))
    return 0
if __name__=='__main__': raise SystemExit(main())
