from __future__ import annotations
from typing import Any, Mapping
import numpy as np

def _ordinal_alpha(matrix: np.ndarray) -> float:
    # Krippendorff alpha, ordinal distance on 0..4, complete 3-coder matrix.
    m=matrix.astype(int); k=5
    observed=[]
    for row in m:
        observed.extend((row[i]-row[j])**2 for i in range(3) for j in range(i+1,3))
    do=float(np.mean(observed))
    counts=np.bincount(m.ravel(),minlength=k).astype(float); p=counts/counts.sum()
    de=sum(p[i]*p[j]*(i-j)**2 for i in range(k) for j in range(k))
    return 1.0-do/de if de>0 else 1.0

def simulate_and_evaluate(*, rng: np.random.Generator, plan: Mapping[str,Any], n:int, effect:Mapping[str,Any]):
    regimes=np.arange(n)%4
    all_ok=True; alphas=[]
    reliability=min(0.98,max(0.35,0.50+float(effect['absolute'])))
    for d in range(6):
        latent=np.clip((regimes + rng.integers(0,2,n) + d)%5,0,4)
        ratings=np.empty((n,3),int)
        for c in range(3):
            exact=rng.random(n)<reliability
            perturb=rng.choice([-1,1],size=n)
            ratings[:,c]=np.clip(np.where(exact,latent,latent+perturb),0,4)
        alpha=_ordinal_alpha(ratings); alphas.append(alpha)
        discriminates=any(len(np.unique(np.median(ratings[regimes==r],axis=1)))>=2 for r in np.unique(regimes))
        all_ok &= alpha>=0.80 and discriminates
    return {'all_dimensions_pass': bool(all_ok), 'minimum_alpha': float(min(alphas))}
