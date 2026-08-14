#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/'plan_directeur/campagne_centrale_2026_08_11/PREDICTIONS_PROSPECTIVES/REGISTRE_ELIGIBILITE_DATASETS_VIVANT.json'
TEMPLATE=ROOT/'plan_directeur/campagne_centrale_2026_08_11/PREDICTIONS_PROSPECTIVES/CANDIDAT_LTEE_MIC_BLIND_TEMPLATE.json'

def main():
 d=json.loads(REG.read_text(encoding='utf-8'))
 if d.get('schema')!='oric.blind-dataset-eligibility.v1': raise SystemExit('schema dataset registry invalid')
 seen=d['known_seen_datasets']; ids=[x['id'] for x in seen]; identifiers=[x['identifier'] for x in seen]
 if len(ids)!=len(set(ids)) or len(identifiers)!=len(set(identifiers)): raise SystemExit('duplicate seen dataset')
 bad=[x['id'] for x in seen if x.get('eligible_for_strict_future_test')]
 if bad: raise SystemExit('seen dataset incorrectly marked eligible: '+', '.join(bad))
 req=d['future_candidate_requirements']
 if not all(req.values()): raise SystemExit('future eligibility rule weakened')
 for c in d.get('eligible_candidates',[]):
  required=['independent_longitudinal_dataset','not_previously_opened_by_ORI_C','lineage_or_history_variable_available','present_state_predictors_available','future_MIC_or_equivalent_registered_target_available','grouping_for_within_group_history_permutation_available','analysis_protocol_frozen_before_opening','public_registration_before_opening']
  if not all(c.get(k) is True for k in required): raise SystemExit('eligible candidate does not satisfy all frozen requirements')
 routes=d.get('candidate_routes',[])
 if not any(r.get('id')=='LTEE-NEW-MIC-ROUTE-001' and r.get('status')=='metadata_route_ready_not_yet_eligible' for r in routes): raise SystemExit('LTEE new-MIC route missing or over-promoted')
 t=json.loads(TEMPLATE.read_text(encoding='utf-8'))
 if t.get('eligible_for_execution') is not False or t.get('exact_target_MIC_opened_by_ORI_C') is not False: raise SystemExit('blind LTEE template is not fail-closed')
 if not t.get('forbidden_fields_before_measurement'): raise SystemExit('blind LTEE template missing forbidden result fields')
 print(f"Vivant blind-dataset registry: {len(seen)} seen datasets excluded, {len(d.get('eligible_candidates',[]))} strict candidate(s), {len(routes)} candidate route(s)")
 return 0
if __name__=='__main__': raise SystemExit(main())
