#!/usr/bin/env python3
from pathlib import Path
import json,sys
import pandas as pd
HERE=Path(__file__).resolve().parent; MEM=HERE.parent
sys.path.insert(0,str(HERE)); from ccm import skill
D=pd.read_csv(MEM/'data/processed/mpt_lr04_la2004.csv')
pairs=[('insolation_65n_june_wm2','d18o_permil'),('eccentricity','d18o_permil'),('obliquity_deg','d18o_permil')]
libs=[300,600,1200,2000,2500]; out=[]
for x,y in pairs:
 for source,target in [(x,y),(y,x)]:
  curve=[]
  for L in libs: curve.append({'library_size':L,**skill(D[source],D[target],L,E=3,tau=5,repeats=20,seed=20260810)})
  out.append({'reported_direction':f'{source} -> {target}','reconstruction_rule':f'reconstruct {source} from manifold of {target}','E':3,'tau_kyr':5,'curve':curve,'delta_rho_last_minus_first':curve[-1]['mean_rho']-curve[0]['mean_rho']})
result={'status':'exploratory_ccm_executed','data':'LR04 + La2004 merged series, 2600-0 ka BP','results':out,
 'scope':'Exploratory nonlinear state-space diagnostic only. LR04 chronology is orbitally tuned; this analysis cannot independently validate orbital climate causality and does not modify the negative M2 verdict.'}
(HERE/'resultats/CCM_RESULTAT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
