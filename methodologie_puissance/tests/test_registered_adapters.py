from __future__ import annotations
import importlib.util, json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]

def load(path):
    spec=importlib.util.spec_from_file_location('adapter', ROOT/path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

def test_adapters_return_registered_boolean_criteria():
    cases=[
      ('03_branche_vivant/benchmark_histoire_antibiotique_2026/POWER_PLAN.json',24),
      ('01_branche_matiere/base_transitions/POWER_PLAN.json',40),
      ('02_branche_systeme_solaire/tests_suivants/PACC_POWER_PLAN.json',6),
    ]
    for plan_path,n in cases:
        plan=json.loads((ROOT/plan_path).read_text(encoding='utf-8'))
        mod=load(plan['adapter']['path'])
        effect={'absolute': float(plan['effect'].get('baseline',1.0))*float(plan['effect']['sesoi']) if plan['effect']['type']=='relative_improvement' else float(plan['effect']['sesoi'])}
        result=mod.simulate_and_evaluate(rng=np.random.default_rng(42), plan=plan, n=n, effect=effect)
        for criterion in plan['success_rule']:
            assert isinstance(result[criterion], (bool,np.bool_))
