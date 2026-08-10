#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from methodologie_informationnelle.causal_states import reconstruct
OUT=ROOT/'methodologie_informationnelle/RESULTATS_ETATS_CAUSAUX.json'
series={}
mpt=pd.read_csv(ROOT/'02_branche_systeme_solaire/couche_memoire_historique/data/processed/mpt_lr04_la2004.csv')
series['paleoclimat_d18o_2600ka']=mpt['d18o_permil'].to_numpy()
for name,file in [('spin_with_moon_20myr','baseline_with_moon_20myr.csv'),('spin_no_moon_20myr','baseline_no_moon_20myr.csv')]:
 df=pd.read_csv(ROOT/'02_branche_systeme_solaire/couche_spin_orbite/resultats'/file)
 # première fenêtre de 2 Ma pour rester comparable à la plupart des interventions
 series[name]=df[df.elapsed_years<=2_000_000]['obliquity_deg'].to_numpy()
rng=np.random.default_rng(20260810)
results={}
for name,v in series.items():
 r=reconstruct(v,n_symbols=4,history_length=4,js_threshold=.08,min_history_count=3)
 perm=[]
 for _ in range(200):
  vp=np.array(v,copy=True); rng.shuffle(vp)
  try: perm.append(reconstruct(vp,n_symbols=4,history_length=4,js_threshold=.08,min_history_count=3)['E_finite_bits'])
  except ValueError: pass
 a=np.asarray(perm,float)
 r['shuffle_control_E_finite_bits']={'replicates':len(a),'mean':float(a.mean()),'q975':float(np.quantile(a,.975)),'p_ge_observed':float((1+np.sum(a>=r['E_finite_bits']))/(len(a)+1))}
 results[name]=r
payload={'status':'exploratory_finite_causal_state_analysis','scope':'finite-history predictive-state approximation; not an exact CSSR reconstruction or asymptotic epsilon-machine','results':results}
OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(payload,ensure_ascii=False,indent=2))
