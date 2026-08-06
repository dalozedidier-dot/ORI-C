from __future__ import annotations
from typing import Any, Mapping
import numpy as np

def simulate_and_evaluate(*, rng: np.random.Generator, plan: Mapping[str,Any], n:int, effect:Mapping[str,Any]):
    metrics=3; refs=3
    noise=float(plan['noise_estimation']['value'])
    baseline=rng.normal(0,noise,(n,metrics))
    reference=rng.normal(0,noise,(refs,metrics))
    envelope=np.maximum(np.max(np.abs(reference),axis=0),1e-15)
    signal=float(effect['absolute'])*envelope
    interventions=baseline+signal+rng.normal(0,noise*0.35,(n,metrics))
    accessible=np.abs(interventions)/envelope >= 1.0
    per_intervention=accessible.sum(axis=1)>=2
    pacc_i=float(per_intervention.mean())
    pacc_d=float(accessible.mean())
    return {
      'pacc_interventions_material': pacc_i >= float(plan.get('pacc_interventions_threshold',0.80)),
      'pacc_dimensions_non_saturated': 0.0 < pacc_d < 1.0,
      'pacc_interventions': pacc_i, 'pacc_dimensions': pacc_d
    }
