#!/usr/bin/env python3
from __future__ import annotations
import csv, json
from collections import defaultdict
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
PROTOCOL=HERE/'MAG-PAIR-001.json'; EXEC=HERE/'MAG-PAIR-001.execution.json'; INPUT=HERE/'mag_pair_001_analysis_ready.csv'; OUT=HERE/'MAG-PAIR-001.result.json'
POS='IRM_positive_saturee'; NEG='IRM_negative_saturee'

def gap(rows, arm, field):
    a=[float(r[field]) for r in rows if r['arm']==arm and r['history']==POS]
    b=[float(r[field]) for r in rows if r['arm']==arm and r['history']==NEG]
    if not a or not b: raise ValueError(f'missing cells for {arm}/{field}')
    return float(np.mean(a)-np.mean(b))

def interaction_stat(rows):
    # Difference of history-specific pre→post changes between true ablation and sham.
    def ch(arm,h):
        vals=[float(r['response_post'])-float(r['response_pre']) for r in rows if r['arm']==arm and r['history']==h]
        if not vals: raise ValueError('empty interaction cell')
        return float(np.mean(vals))
    return (ch('ablation',POS)-ch('ablation',NEG))-(ch('sham',POS)-ch('sham',NEG))

def permutation_p(rows, draws, seed):
    obs=abs(interaction_stat(rows)); rng=np.random.default_rng(seed); ge=0
    blocks=defaultdict(list)
    for i,r in enumerate(rows): blocks[r['block_id']].append(i)
    for _ in range(draws):
        perm=[dict(r) for r in rows]
        for idxs in blocks.values():
            labels=[perm[i]['history'] for i in idxs]; rng.shuffle(labels)
            for i,l in zip(idxs,labels): perm[i]['history']=l
        try: stat=abs(interaction_stat(perm))
        except ValueError: continue
        ge += stat >= obs-1e-15
    return (ge+1)/(draws+1)

def gate():
    e=json.loads(EXEC.read_text(encoding='utf-8')); missing=[k for k,v in e['frozen_fields'].items() if v is None]
    if e.get('status')!='frozen_ready_for_registration' or missing: raise SystemExit('Analysis gate closed: laboratory freeze incomplete.')
    reg=e.get('registration',{})
    if not (reg.get('public_url') and reg.get('registered_at')): raise SystemExit('Analysis gate closed: public preregistration absent.')
    return e

def analyze(path=INPUT):
    e=gate(); protocol=json.loads(PROTOCOL.read_text(encoding='utf-8'))
    if not path.exists(): raise SystemExit('Analysis-ready MAG-PAIR-001 table absent.')
    rows=list(csv.DictReader(path.open(encoding='utf-8-sig',newline='')))
    if len(rows)<int(protocol['minimum_independent_units']): raise ValueError('insufficient independent units')
    d0=gap(rows,'ablation','response_pre'); d1=gap(rows,'ablation','response_post')
    A=1-abs(d1)/abs(d0) if d0 else float('-inf')
    s0=gap(rows,'sham','response_pre'); s1=gap(rows,'sham','response_post')
    Asham=1-abs(s1)/abs(s0) if s0 else None
    ff=e['frozen_fields']; p=permutation_p(rows,int(ff['permutation_draws']),int(ff['permutation_seed']))
    trace_reduction=[float(r['trace_reduction_fraction']) for r in rows if r['arm']=='ablation' and r['trace_reduction_fraction']!='']
    trace_target=bool(trace_reduction and float(np.mean(trace_reduction))>=0.80)
    success=bool(d0!=0 and A>=0.50 and p<=0.05 and trace_target)
    result={'schema':'oric.mag-pair-001.result.v1','protocol_id':'MAG-PAIR-001','n':len(rows),'delta_R_before':d0,'delta_R_after':d1,'A_normalized':A,'sham_delta_R_before':s0,'sham_delta_R_after':s1,'sham_A_normalized':Asham,'interaction_statistic':interaction_stat(rows),'interaction_permutation_p_two_sided':p,'mean_trace_reduction_fraction_true_ablation':float(np.mean(trace_reduction)) if trace_reduction else None,'trace_reduction_target_ge_0p80':trace_target,'prediction_success':success,'scope':'prospective only if public registration preceded acquisition; script does not retro-qualify historical data'}
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n'); print(json.dumps(result,ensure_ascii=False,indent=2)); return result
if __name__=='__main__': analyze()
