#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'plan_directeur/VERROUS_ACTIFS.json'


def load(rel): return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def sha(rel): return hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()


def main() -> int:
    xiv=load('plan_directeur/campagne_centrale_2026_08_11/resultats/SEUIL_XIV.json')
    h=load('01_branche_matiere/hypergraphe_transformations/fermeture_stricte/AUDIT_H052_2026-08-14.json')
    ves=load('03_branche_vivant/lignees_vesicules/PROTOCOLE_PACC_CAUSAL_PROSPECTIF_V1.json')
    vesreg=load('03_branche_vivant/lignees_vesicules/VES-PACC-INT-01.registration.json')
    mag=load('01_branche_matiere/memoire_materielle_reelle/experiences_appariees/MAG-PAIR-001.json')
    predv=load('plan_directeur/campagne_centrale_2026_08_11/PREDICTIONS_PROSPECTIVES/PRED-VIVANT-HISTOIRE-001.json')
    data={
      'schema':'oric.active-bottlenecks.v1','generated_from_authority':True,
      'section_XIV':{'passed_count':xiv['passed_count'],'conditions_total':xiv['conditions_total'],'missing_ids':xiv['missing_ids']},
      'fronts':[
        {'rank':1,'id':'VES-PACC-INT-01','branch':'vivant','scientific_design_complete':True,
         'public_registration_status':vesreg.get('status'),'public_url_present':bool(vesreg.get('public_url')),
         'execution_open':bool(vesreg.get('status')=='publicly_registered' and vesreg.get('public_url') and vesreg.get('registered_at')),
         'protocol_sha256':sha('03_branche_vivant/lignees_vesicules/PROTOCOLE_PACC_CAUSAL_PROSPECTIF_V1.json'),
         'targets':['XIV-9','XIV-3','XIV-4']},
        {'rank':2,'id':'H052-HC01','branch':'matiere','canonical_closure':f"{h['canonical_closure']['reachable_nodes']}/{h['canonical_closure']['total_nodes']}",
         'candidate_status':h['candidate_hc01_r1']['status'],'verdict':h['verdict'],'targets':['fermeture_hypergraphe_53_53']},
        {'rank':3,'id':'PRED-VIVANT-HISTOIRE-001','branch':'vivant','status':predv['statut'],'data_opened':predv.get('date_ouverture') is not None,
         'result_present':predv.get('resultat') is not None,'targets':['XIV-3','XIV-4','XIV-10']},
        {'rank':4,'id':'MAG-PAIR-001','branch':'matiere','status':mag['status'],'minimum_independent_units':mag['minimum_independent_units'],
         'targets':['XIV-9','PRED-MATIERE-ABLATION-001']},
      ]
    }
    OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f"verrous actifs: XIV {xiv['passed_count']}/{xiv['conditions_total']}, {len(data['fronts'])} fronts")
    return 0
if __name__=='__main__': raise SystemExit(main())
