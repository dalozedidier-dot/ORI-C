#!/usr/bin/env python3
from __future__ import annotations
import csv, json
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
POS='IRM_positive_saturee'; NEG='IRM_negative_saturee'

def rows(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))
def num(v):
    x=float(v)
    if not np.isfinite(x): raise ValueError('non-finite pilot value')
    return x

def analyse(af_path, field_path, output=None):
    af=rows(af_path); tf=rows(field_path)
    levels=sorted({num(r['af_mT']) for r in af})
    per=[]; chosen=None
    for level in levels:
        hvals={}
        for h in (POS,NEG):
            vals=[]
            for r in af:
                if r['history']==h and num(r['af_mT'])==level:
                    b=abs(num(r['trace_before'])); a=abs(num(r['trace_after']))
                    if b>0: vals.append(1-a/b)
            hvals[h]=float(np.median(vals)) if vals else None
        ok=all(hvals[h] is not None and hvals[h]>=0.80 for h in (POS,NEG))
        per.append({'af_mT':level,'median_trace_reduction_by_history':hvals,'passes_inherited_80_percent_rule':ok})
        if ok and chosen is None: chosen=level
    field_rows=[]
    for level in sorted({num(r['test_field_mT']) for r in tf}):
        subset=[r for r in tf if num(r['test_field_mT'])==level]
        overwrite=[]; snr=[]
        for r in subset:
            b=abs(num(r['trace_before_test'])); a=abs(num(r['trace_after_test']))
            if b>0: overwrite.append(abs(a-b)/b)
            noise=abs(num(r['instrument_noise_sd']))
            if noise>0: snr.append(abs(num(r['response_projection']))/noise)
        field_rows.append({'test_field_mT':level,'median_trace_overwrite_fraction':float(np.median(overwrite)) if overwrite else None,'median_signal_to_noise':float(np.median(snr)) if snr else None,'n':len(subset)})
    temps=[num(r['temperature_C']) for r in [*af,*tf]]
    report={'schema':'oric.mag-pair-001.pilot-report.v1','confirmatory_credit':False,'recommended_af_plateau_mT_from_inherited_rule':chosen,'af_levels':per,'test_field_candidates_measured':field_rows,'observed_temperature_C':{'min':min(temps),'max':max(temps),'median':float(np.median(temps))} if temps else None,'test_field_selection_status':'requires_lab_threshold_freeze','scope':'pilot only; no PRED-MATIERE-ABLATION-001 or XIV credit'}
    if output: Path(output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    return report
if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('af_sweep'); ap.add_argument('test_field_sweep'); ap.add_argument('--output',default=str(HERE/'MAG-PAIR-001.pilot-report.json')); a=ap.parse_args(); print(json.dumps(analyse(a.af_sweep,a.test_field_sweep,a.output),ensure_ascii=False,indent=2))
