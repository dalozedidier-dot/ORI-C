#!/usr/bin/env python3
"""Convergent Cross Mapping minimal, déterministe, pour analyses exploratoires.

Direction reportée `source -> target` : le collecteur reconstruit SOURCE depuis
le manifold de TARGET, conformément à l'idée CCM que l'effet porte une trace de
sa cause. Ce module ne transforme pas CCM en preuve interventionnelle.
"""
from __future__ import annotations
import numpy as np
from scipy.spatial.distance import cdist

def embed(x,E=3,tau=5):
    x=np.asarray(x,float); start=(E-1)*tau
    M=np.column_stack([x[start-k*tau:len(x)-k*tau] for k in range(E)])
    return M,start

def skill(source,target,library_size,E=3,tau=5,repeats=20,seed=0):
    source=np.asarray(source,float); target=np.asarray(target,float)
    M,start=embed(target,E,tau); src=source[start:]
    n=len(src); L=min(library_size,n)
    rng=np.random.default_rng(seed+L)
    vals=[]
    for _ in range(repeats):
        ids=np.sort(rng.choice(n,L,replace=False))
        X=M[ids]; y=src[ids]
        D=cdist(X,X); np.fill_diagonal(D,np.inf)
        k=E+1
        nn=np.argpartition(D,kth=k-1,axis=1)[:,:k]
        ds=np.take_along_axis(D,nn,axis=1)
        d1=np.maximum(ds.min(axis=1,keepdims=True),1e-15)
        w=np.exp(-ds/d1); w/=w.sum(axis=1,keepdims=True)
        pred=np.sum(w*y[nn],axis=1)
        if np.std(pred)>0 and np.std(y)>0: vals.append(float(np.corrcoef(pred,y)[0,1]))
    return {'mean_rho':float(np.mean(vals)),'sd_rho':float(np.std(vals)),'repeats':len(vals)}
