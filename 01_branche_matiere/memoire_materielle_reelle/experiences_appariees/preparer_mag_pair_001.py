#!/usr/bin/env python3
from __future__ import annotations
import csv, json, math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

HERE=Path(__file__).resolve().parent
PROTOCOL=HERE/'MAG-PAIR-001.json'
EXEC=HERE/'MAG-PAIR-001.execution.json'
UNITS=HERE/'mag_pair_001_units.csv'
MEAS=HERE/'mag_pair_001_measurements.csv'
OUT=HERE/'mag_pair_001_analysis_ready.csv'


def f(x): return float(x)
def mag(r): return math.sqrt(f(r['remanence_x'])**2+f(r['remanence_y'])**2+f(r['remanence_z'])**2)

def gate_config():
    e=json.loads(EXEC.read_text(encoding='utf-8'))
    fields=e['frozen_fields']
    missing=[k for k,v in fields.items() if v is None]
    if e.get('status')!='frozen_ready_for_registration' or missing:
        raise SystemExit('Preparation gate closed: laboratory freeze incomplete: '+', '.join(missing))
    reg=e.get('registration',{})
    if not (reg.get('public_url') and reg.get('registered_at')):
        raise SystemExit('Preparation gate closed: public preregistration URL/timestamp absent.')
    return e

def prepare(units_path=UNITS, measurements_path=MEAS, out_path=OUT):
    e=gate_config(); protocol=json.loads(PROTOCOL.read_text(encoding='utf-8'))
    if not units_path.exists() or not measurements_path.exists(): raise SystemExit('Raw MAG-PAIR-001 tables are absent.')
    units=list(csv.DictReader(units_path.open(encoding='utf-8-sig',newline='')))
    if len(units)<int(protocol['minimum_independent_units']): raise ValueError('insufficient independent units')
    ids=[r['unit_id'] for r in units]
    if len(ids)!=len(set(ids)): raise ValueError('duplicate unit_id')
    allowed_h=set(protocol['histories']); allowed_a={'ablation','sham'}
    if any(r['history'] not in allowed_h or r['arm'] not in allowed_a for r in units): raise ValueError('invalid history/arm')
    u={r['unit_id']:r for r in units}
    rows=list(csv.DictReader(measurements_path.open(encoding='utf-8-sig',newline='')))
    if any(r['unit_id'] not in u for r in rows): raise ValueError('measurement for unknown unit')
    by=defaultdict(lambda:defaultdict(list))
    for r in rows: by[r['unit_id']][r['stage']].append(r)
    req={'trace_initial':1,'trace_day7':10,'trace_post_ablation':1,'response_pre':1,'response_post':1}
    out=[]; ff=e['frozen_fields']
    for uid in ids:
        stages=by[uid]
        for stage,n in req.items():
            if len(stages.get(stage,[]))!=n: raise ValueError(f'{uid}: {stage} requires {n} rows')
        day7=sorted(stages['trace_day7'],key=lambda r:int(r['reading_index']))
        if [int(r['reading_index']) for r in day7] != list(range(1,11)): raise ValueError(f'{uid}: trace_day7 reading_index must be 1..10')
        allr=[r for rs in stages.values() for r in rs]
        if any(abs(f(r['test_field_mT'])-float(ff['test_field_mT']))>1e-12 for r in stages['response_pre']+stages['response_post']): raise ValueError(f'{uid}: test field mismatch')
        if any(abs(f(r['temperature_c'])-float(ff['temperature_target_c']))>float(ff['temperature_tolerance_c']) for r in allr): raise ValueError(f'{uid}: temperature out of tolerance')
        post=stages['trace_post_ablation'][0]
        if u[uid]['arm']=='ablation' and abs(f(post['af_field_mT'])-float(ff['af_plateau_mT']))>1e-12: raise ValueError(f'{uid}: AF plateau mismatch')
        if u[uid]['arm']=='sham' and abs(f(post['af_field_mT']))>1e-12: raise ValueError(f'{uid}: sham AF must be zero')
        initial=mag(stages['trace_initial'][0]); postm=mag(post); persist=sum(mag(r) for r in day7)/10
        out.append({
          'unit_id':uid,'block_id':u[uid]['block_id'],'history':u[uid]['history'],'arm':u[uid]['arm'],
          'trace_initial_magnitude':initial,'trace_day7_mean_magnitude':persist,'trace_post_ablation_magnitude':postm,
          'trace_reduction_fraction':(1-postm/initial) if initial else '',
          'response_pre':f(stages['response_pre'][0]['response_projection']),
          'response_post':f(stages['response_post'][0]['response_projection'])
        })
    fields=list(out[0]);
    with out_path.open('w',encoding='utf-8',newline='') as h:
        w=csv.DictWriter(h,fieldnames=fields); w.writeheader(); w.writerows(out)
    print(f'MAG-PAIR-001 prepared: {len(out)} units -> {out_path}')
    return out

if __name__=='__main__': prepare()
