#!/usr/bin/env python3
"""Pont de comparaison avec Assembly Theory, sans équivalence postulée."""
from __future__ import annotations
import math
import numpy as np
from scipy.stats import spearmanr

def assembly_ensemble_score(assembly_indices,copy_numbers):
    a=np.asarray(assembly_indices,float); n=np.asarray(copy_numbers,float)
    if len(a)!=len(n) or len(a)==0 or np.any(n<1): raise ValueError('données invalides')
    NT=float(n.sum())
    return float(np.sum(np.exp(a)*(n-1.0)/NT))

def compare_depths(oric_depth,assembly_index):
    if len(oric_depth)!=len(assembly_index) or len(oric_depth)<3: raise ValueError('au moins 3 objets appariés')
    r,p=spearmanr(oric_depth,assembly_index)
    return {'spearman_rho':float(r),'p':float(p),'n':len(oric_depth)}
