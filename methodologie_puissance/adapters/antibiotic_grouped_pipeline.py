from __future__ import annotations
from typing import Any, Mapping
import numpy as np

ANTIBIOTICS=4
REPLICATES=3
ANCESTORS=6

def _one_hot(values, levels):
    out=np.zeros((len(values), levels-1), float)
    for j in range(1, levels): out[:,j-1]=(values==j)
    return out

def _ridge_predict(xtr,ytr,xte,alpha=1.0):
    xtx=xtr.T@xtr
    beta=np.linalg.solve(xtx+alpha*np.eye(xtx.shape[0]), xtr.T@ytr)
    return xte@beta

def _cv_rmse(y, group, limitation, antibiotic, ancestor, include_history):
    preds=np.empty_like(y)
    unique=np.unique(group)
    folds=np.array_split(unique, min(5,len(unique)))
    for held in folds:
        te=np.isin(group, held); tr=~te
        cols=[np.ones(len(y)), limitation.astype(float), _one_hot(antibiotic,ANTIBIOTICS)]
        if include_history: cols.append(_one_hot(ancestor,ANCESTORS))
        X=np.column_stack(cols)
        preds[te]=_ridge_predict(X[tr],y[tr],X[te])
    return float(np.sqrt(np.mean((y-preds)**2)))

def simulate_and_evaluate(*, rng: np.random.Generator, plan: Mapping[str,Any], n:int, effect:Mapping[str,Any]):
    group=np.repeat(np.arange(n), ANTIBIOTICS*REPLICATES)
    limitation_group=np.arange(n)%2
    ancestor_group=np.arange(n)%ANCESTORS
    limitation=np.repeat(limitation_group,ANTIBIOTICS*REPLICATES)
    ancestor=np.repeat(ancestor_group,ANTIBIOTICS*REPLICATES)
    antibiotic=np.tile(np.repeat(np.arange(ANTIBIOTICS),REPLICATES),n)
    abx_effect=np.array([0.0,4.8,0.2,-0.4])[antibiotic]
    lim_effect=0.18*limitation
    history_code=(ancestor-(ANCESTORS-1)/2)/2.0
    # The SESOI is an absolute RMSE-scale target; coefficient calibration keeps
    # the injected signal on the same order without treating folds as units.
    beta=float(effect['absolute'])*2.8
    group_noise=np.repeat(rng.normal(0,0.30,n),ANTIBIOTICS*REPLICATES)
    eps=rng.normal(0,0.72,len(group))
    y=abx_effect+lim_effect+beta*history_code+group_noise+eps
    rmse_state=_cv_rmse(y,group,limitation,antibiotic,ancestor,False)
    rmse_history=_cv_rmse(y,group,limitation,antibiotic,ancestor,True)
    perm=ancestor_group[rng.permutation(n)]
    shuffled=np.repeat(perm,ANTIBIOTICS*REPLICATES)
    rmse_shuffled=_cv_rmse(y,group,limitation,antibiotic,shuffled,True)
    return {
      'history_beats_state': rmse_history < rmse_state,
      'history_beats_shuffled_history': rmse_history < rmse_shuffled,
      'rmse_state': rmse_state, 'rmse_history': rmse_history, 'rmse_shuffled': rmse_shuffled
    }
