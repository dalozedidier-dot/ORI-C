#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from methodologie_informationnelle.pid import pid_imin
DATA=ROOT/'donnees_externes/histoire_antibiotique_donofrio_2026/extracted/Figure_3_N-lim_Expt_MIC_Raw_Data.csv'
OUT=Path(__file__).resolve().parent/'resultats/PID_X_M_A.json'

def main():
    df=pd.read_csv(DATA)
    X=(df['Limitation'].astype(str)+'|'+df['Antibiotic'].astype(str)).tolist()
    M=df['Ancestor'].astype(str).tolist(); Y=df['MIC (ug/mL)'].astype(str).tolist()
    obs=pid_imin(X,M,Y)
    # Index compact des groupes Strain dans chaque limitation. Une permutation
    # agit sur les ancêtres au niveau de l'unité Strain, jamais ligne par ligne.
    groups=df[['Strain','Limitation','Ancestor']].drop_duplicates().sort_values(['Limitation','Strain']).reset_index(drop=True)
    group_key={(int(r.Strain),str(r.Limitation)):i for i,r in groups.iterrows()}
    row_group=np.array([group_key[(int(s),str(l))] for s,l in zip(df.Strain,df.Limitation)],dtype=int)
    ancestor_by_group=groups['Ancestor'].astype(str).to_numpy()
    strata=[]
    for lim in sorted(groups['Limitation'].astype(str).unique()): strata.append(np.flatnonzero(groups['Limitation'].astype(str).to_numpy()==lim))
    rng=np.random.default_rng(20260810); nperm=2000
    keys=['unique_M_history_bits','synergy_XM_bits','I_XM_Y_bits']; null={k:np.empty(nperm) for k in keys}
    for i in range(nperm):
        perm=ancestor_by_group.copy()
        for ids in strata: perm[ids]=rng.permutation(perm[ids])
        Mp=perm[row_group].tolist(); r=pid_imin(X,Mp,Y)
        for k in keys: null[k][i]=r[k]
    result={'status':'exploratory_additional_analysis','method':'Williams-Beer I_min PID on discretely observed variables',
      'scope':'Does not alter C-ANT-01 certification; X=Limitation|Antibiotic, M=Ancestor, Y=observed MIC level.',
      'rows':len(df),'strain_groups':int(df['Strain'].nunique()),'permutations':nperm,'seed':20260810,'observed':obs,'null':{},
      'warning':'PID I_min is one redundancy definition among several; results are exploratory and discretization-specific.'}
    for k,a in null.items(): result['null'][k]={'mean':float(a.mean()),'q025':float(np.quantile(a,.025)),'q975':float(np.quantile(a,.975)),'p_one_sided_ge_observed':float((1+np.sum(a>=obs[k]))/(nperm+1))}
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
