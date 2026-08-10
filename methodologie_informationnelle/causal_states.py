#!/usr/bin/env python3
"""Approximation finie des états causaux prédictifs.

Ce n'est pas CSSR complet ni une epsilon-machine asymptotique. Les passés de
longueur L sont regroupés lorsque leurs distributions empiriques du prochain
symbole sont proches en Jensen-Shannon. Les quantités C_mu, E_finie et une
crypticité finie sont donc des proxys à horizon fini, nommés comme tels.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from math import log2
import numpy as np


def quantile_symbols(values, n_symbols=4):
    a=np.asarray(values,float)
    if a.ndim!=1 or len(a)<10: raise ValueError("série trop courte")
    qs=np.quantile(a,np.linspace(0,1,n_symbols+1))
    # gérer les quantiles identiques sans masquer le problème
    qs=np.maximum.accumulate(qs)
    inner=qs[1:-1]
    sym=np.digitize(a,inner,right=False)
    return sym.astype(int), qs.tolist()


def _js(p,q):
    p=np.asarray(p,float); q=np.asarray(q,float); m=(p+q)/2
    def kl(a,b):
        mask=a>0
        return float(np.sum(a[mask]*np.log2(a[mask]/b[mask])))
    return 0.5*kl(p,m)+0.5*kl(q,m)


def _entropy(counts):
    vals=np.asarray(list(counts),float); vals=vals[vals>0]
    p=vals/vals.sum(); return float(-np.sum(p*np.log2(p)))


def reconstruct(values, n_symbols=4, history_length=4, js_threshold=0.08, min_history_count=3):
    sym,edges=quantile_symbols(values,n_symbols)
    K=n_symbols
    hist_counts=defaultdict(Counter)
    samples=[]
    for t in range(history_length,len(sym)):
        h=tuple(sym[t-history_length:t]); f=int(sym[t])
        hist_counts[h][f]+=1; samples.append((h,f))
    valid={h:c for h,c in hist_counts.items() if sum(c.values())>=min_history_count}
    items=[]
    for h,c in sorted(valid.items()):
        v=np.array([c.get(k,0) for k in range(K)],float); v=(v+0.5)/(v.sum()+0.5*K)
        items.append((h,v,sum(c.values())))
    clusters=[]
    assignment={}
    for h,v,n in items:
        best=None
        for i,c in enumerate(clusters):
            d=_js(v,c['dist'])
            if d<=js_threshold and (best is None or d<best[0]): best=(d,i)
        if best is None:
            clusters.append({'dist':v.copy(),'weight':n,'members':[h]}); idx=len(clusters)-1
        else:
            idx=best[1]; c=clusters[idx]
            total=c['weight']+n; c['dist']=(c['dist']*c['weight']+v*n)/total; c['weight']=total; c['members'].append(h)
        assignment[h]=idx
    joint=Counter(); state_count=Counter(); future_count=Counter(); covered=0
    for h,f in samples:
        if h not in assignment: continue
        s=assignment[h]; joint[(s,f)]+=1; state_count[s]+=1; future_count[f]+=1; covered+=1
    if covered==0: raise ValueError("aucun historique admissible")
    Cmu=_entropy(state_count.values())
    Hy=_entropy(future_count.values())
    # MI état-futur
    I=0.0
    for (s,f),n in joint.items():
        p=n/covered; ps=state_count[s]/covered; pf=future_count[f]/covered
        I += p*log2(p/(ps*pf))
    return {
        'method':'finite_history_predictive_state_clustering',
        'not_exact_epsilon_machine':True,
        'n_symbols':n_symbols,'history_length':history_length,'js_threshold':js_threshold,
        'min_history_count':min_history_count,'quantile_edges':edges,
        'n_states':len(clusters),'covered_samples':covered,'coverage_fraction':covered/max(1,len(samples)),
        'C_mu_finite_bits':Cmu,'E_finite_bits':I,'crypticity_finite_proxy_bits':max(0.0,Cmu-I),
        'future_entropy_bits':Hy,
        'state_sizes':sorted([c['weight'] for c in clusters],reverse=True),
    }
