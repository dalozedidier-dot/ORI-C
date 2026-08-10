#!/usr/bin/env python3
"""PCMCI+ exploratoire sur LR04/La2004 via Tigramite.

Dépendance volontairement séparée du socle. Le script échoue explicitement si
Tigramite n'est pas installé ; la CI dédiée installe une version figée.
"""
from __future__ import annotations
from pathlib import Path
import json
import numpy as np,pandas as pd
HERE=Path(__file__).resolve().parent; MEM=HERE.parent
try:
    from tigramite import data_processing as pp
    from tigramite.pcmci import PCMCI
    from tigramite.independence_tests.parcorr import ParCorr
except ImportError as exc:
    raise SystemExit('Tigramite requis pour PCMCI+ exploratoire; installer requirements-pcmci.lock.txt') from exc
cols=['d18o_permil','eccentricity','obliquity_deg','insolation_65n_june_wm2']
df=pd.read_csv(MEM/'data/processed/mpt_lr04_la2004.csv')[cols].dropna()
x=(df-df.mean())/df.std(ddof=0)
dataframe=pp.DataFrame(x.to_numpy(),var_names=cols)
pcmci=PCMCI(dataframe=dataframe,cond_ind_test=ParCorr(significance='analytic'),verbosity=0)
res=pcmci.run_pcmciplus(tau_min=0,tau_max=20,pc_alpha=0.01)
# Sérialisation compacte des liens significatifs, sans interprétation causale forte.
p=res['p_matrix']; val=res['val_matrix']; graph=res['graph']
links=[]
for i,a in enumerate(cols):
 for j,b in enumerate(cols):
  for tau in range(p.shape[2]):
   if p[i,j,tau] <= .01 and graph[i,j,tau] != '':
    links.append({'source':a,'target':b,'lag_kyr':tau,'p':float(p[i,j,tau]),'value':float(val[i,j,tau]),'graph_mark':str(graph[i,j,tau])})
out={'status':'exploratory_pcmciplus','tigramite_version':__import__('tigramite').__version__ if hasattr(__import__('tigramite'),'__version__') else 'unknown',
 'variables':cols,'tau_max_kyr':20,'pc_alpha':.01,'significant_links_raw_p_le_0p01':links,
 'scope':'Exploratory observational causal-discovery diagnostic. LR04 chronology is orbitally tuned; no change to M2 verdict or certified climate evidence.'}
(HERE/'resultats/PCMCI_PLUS_RESULTAT.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))
