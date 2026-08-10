#!/usr/bin/env python3
"""Homologie persistante de l'expansion simpliciale documentaire de l'hypergraphe.

Chaque hyperarête est remplacacée par les simplexes de dimension <=2 portés par
l'union de ses entrées/sorties. La filtration t=1-plancher_documentaire fait
entrer en premier les relations les mieux documentées. Ceci n'est pas une
'homologie de l'hypergraphe' unique/canonique : le choix d'expansion est écrit
explicitement et sert de test de robustesse multi-seuil.
"""
from __future__ import annotations
from itertools import combinations
from pathlib import Path
import json
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]; HERE=Path(__file__).resolve().parent

def build_simplices():
    e=pd.read_csv(HERE/'hyperaretes.csv',sep=';')
    c=pd.read_csv(HERE/'calibrage_v094/resultats/calibrage_hyperaretes.csv',sep=';')
    score=dict(zip(c.edge_id,c.plancher_documentaire.astype(float)))
    nodes=pd.read_csv(HERE/'noeuds.csv',sep=';')['node_id'].astype(str).tolist()
    filt={(v,):0.0 for v in nodes}
    for _,r in e.iterrows():
        vs=sorted(set(str(r.entrees).split('|')+str(r.sorties).split('|')))
        t=1.0-score[str(r.edge_id)]
        for d in (2,3):
            for s in combinations(vs,d): filt[s]=min(filt.get(s,1.0),t)
    return filt

def persistence(filt):
    simplices=sorted(filt,key=lambda s:(filt[s],len(s)-1,s))
    idx={s:i for i,s in enumerate(simplices)}
    low_to_col={}; reduced={}; pairs=[]; births=[]
    for j,s in enumerate(simplices):
        dim=len(s)-1
        col=set()
        if dim>0:
            for face in combinations(s,len(s)-1): col.add(idx[tuple(face)])
        while col:
            low=max(col)
            if low not in low_to_col: break
            col ^= reduced[low_to_col[low]]
        if col:
            low=max(col); low_to_col[low]=j; reduced[j]=col
            b=simplices[low]; pairs.append({'dimension':len(b)-1,'birth':filt[b],'death':filt[s],'birth_simplex':list(b),'death_simplex':list(s)})
        else:
            reduced[j]=set(); births.append(j)
    killed=set(low_to_col.keys())
    intervals=[]
    for p in pairs:
        if p['dimension']<=1: intervals.append(p)
    for j in births:
        if j not in killed and len(simplices[j])-1<=1:
            s=simplices[j]; intervals.append({'dimension':len(s)-1,'birth':filt[s],'death':None,'birth_simplex':list(s),'death_simplex':None})
    return simplices,intervals

def main():
    filt=build_simplices(); simplices,ints=persistence(filt)
    rows=[]
    for x in ints:
        y=x.copy(); y['persistence']=None if x['death'] is None else x['death']-x['birth']; rows.append(y)
    pd.DataFrame(rows).to_json(HERE/'resultats_topologie/intervalles_persistance.json',orient='records',indent=2,force_ascii=False)
    finite1=[x for x in rows if x['dimension']==1 and x['death'] is not None]
    infinite1=[x for x in rows if x['dimension']==1 and x['death'] is None]
    top=sorted(finite1,key=lambda x:x['persistence'],reverse=True)[:10]
    result={'status':'executed','object':'documentary simplicial expansion of ORI-C material hypergraph',
      'filtration':'t = 1 - plancher_documentaire; vertices at t=0; faces up to dimension 2',
      'nodes':sum(1 for s in simplices if len(s)==1),'simplices_total':len(simplices),
      'H0_intervals':sum(x['dimension']==0 for x in rows),'H1_intervals':sum(x['dimension']==1 for x in rows),
      'H1_infinite_at_end':len(infinite1),'top_finite_H1':top,
      'scope':'multi-threshold structural robustness diagnostic; not empirical support for ORI-C and not a canonical hypergraph homology'}
    (HERE/'resultats_topologie/RESULTAT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
