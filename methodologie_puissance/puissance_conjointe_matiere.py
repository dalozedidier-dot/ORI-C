#!/usr/bin/env python3
"""Puissance conjointe prospective pour un plan histoire→trace→réponse→ablation.

Ce simulateur ne recycle aucun effet observé comme vérité. Les effets sont des
hypothèses dimensionnelles explicites et la puissance porte sur la conjonction
des maillons, ce qui évite de dimensionner l'expérience sur un seul test facile.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
ROOT=Path(__file__).resolve().parents[1]

def one(rng,n,strata,b_ht,b_tr,retention,ablation_fraction,alpha=.05):
    # doses équilibrées 0..1, strates >=5
    dose=np.tile(np.linspace(0,1,strata),int(np.ceil(n/strata)))[:n]; rng.shuffle(dose)
    trace=b_ht*dose+rng.normal(0,1,n)
    delayed=retention*trace+rng.normal(0,.7,n)
    response=b_tr*trace+.35*dose+rng.normal(0,1,n)
    # ablation appariée synthétique sur une fraction : la trace est remise près du fond
    k=max(strata,int(round(n*ablation_fraction)))
    ids=rng.choice(n,k,replace=False)
    response_ab=.15*dose[ids]+rng.normal(0,1,k)
    # quatre conditions minimales : H→T, T→R, persistance T→Tdelay, ablation réduit |réponse|
    p1=spearmanr(dose,trace).pvalue
    p2=spearmanr(trace,response).pvalue
    p3=spearmanr(trace,delayed).pvalue
    # test permutation simple sur contraste moyen |R| - |R_ab|, conservateur 199 perm
    obs=np.mean(np.abs(response[ids]))-np.mean(np.abs(response_ab))
    pool=np.c_[np.abs(response[ids]),np.abs(response_ab)]
    ge=0
    for _ in range(199):
        swap=rng.random(k)<.5
        a=np.where(swap,pool[:,1],pool[:,0]); b=np.where(swap,pool[:,0],pool[:,1])
        ge += (np.mean(a)-np.mean(b) >= obs)
    p4=(ge+1)/200
    # Robustesse retrait d'une strate pour les trois corrélations : signe conservé.
    robust=True
    groups=np.floor(dose*(strata-1)+1e-9).astype(int)
    for g in np.unique(groups):
        keep=groups!=g
        if spearmanr(dose[keep],trace[keep]).statistic<=0 or spearmanr(trace[keep],response[keep]).statistic<=0:
            robust=False; break
    return bool(p1<alpha and p2<alpha and p3<alpha and p4<alpha and robust)

def simulate(n,reps=400,seed=20260810,**kw):
    rng=np.random.default_rng(seed+n)
    return sum(one(rng,n,**kw) for _ in range(reps))/reps

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--reps',type=int,default=400); a=ap.parse_args()
    assumptions={'strata':6,'b_ht':1.5,'b_tr':1.2,'retention':0.85,'ablation_fraction':0.5}
    ns=[36,48,60,72,84,96,120]
    rows=[{'n':n,'joint_power':simulate(n,reps=a.reps,**assumptions)} for n in ns]
    first=next((r['n'] for r in rows if r['joint_power']>=.9),None)
    result={'schema':'oric.joint-power-material.v1','status':'prospective_simulation','repetitions_per_n':a.reps,'seed':20260810,
      'assumptions_standardized_not_empirical_estimates':assumptions,'success_rule':'all four chain tests + leave-one-stratum sign robustness','grid':rows,
      'first_n_reaching_90pct_under_these_assumptions':first,
      'decision':'Use this as a dimensioning engine. The returned n is conditional on explicit assumed effects and must not be described as an empirically guaranteed sample size.'}
    p=ROOT/'methodologie_puissance/PUISSANCE_CONJOINTE_MATIERE.json';p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
