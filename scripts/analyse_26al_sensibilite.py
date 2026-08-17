#!/usr/bin/env python3
from pathlib import Path
import json, math
ROOT=Path(__file__).resolve().parents[1]; CFG=ROOT/'data'/'al26_config.json'; OUT=ROOT/'resultats'/'AL26_CHRONOMETRIE_APPROFONDIE.json'
cfg=json.loads(CFG.read_text()); hl=float(cfg['half_life_myr']); z=1.959963984540054
scenarios=[]; events=[]
for e in cfg['events']:
    t=float(e['time_after_CAI_myr']); s=float(e['time_sigma_myr'])
    canonical=2**(-t/hl); q025=2**(-(t+z*s)/hl); q975=2**(-(t-z*s)/hl)
    rec={'event':e['event'],'time_after_CAI_myr':t,'time_sigma_myr':s,'canonical':{'median':canonical,'q025':q025,'q975':q975},'reservoir_scenarios':{}}
    for f in cfg['reservoir_depletion_factors']:
        key='canonical' if f==1 else f'depleted_x{int(f)}'; med=canonical/f; lo=q025/f; hi=q975/f
        rec['reservoir_scenarios'][key]={'factor':f,'median':med,'q025':lo,'q975':hi,
          'thresholds_at_median':[x for x in cfg['thresholds'] if med>=x],
          'thresholds_robust_q025':[x for x in cfg['thresholds'] if lo>=x]}
    stable=set(cfg['thresholds'])
    for r in rec['reservoir_scenarios'].values(): stable &= set(r['thresholds_robust_q025'])
    rec['thresholds_robust_across_all_declared_reservoir_scenarios']=sorted(stable,reverse=True)
    events.append(rec)
adj=[]
for a,b in zip(events,events[1:]):
    A=a['canonical']; B=b['canonical']; overlap=max(0.0,min(A['q975'],B['q975'])-max(A['q025'],B['q025']))
    adj.append({'earlier_event':a['event'],'later_event':b['event'],'median_fraction_ratio_earlier_over_later':A['median']/B['median'],
                '95pct_fraction_intervals_overlap':bool(overlap>0),'overlap_width':overlap})
h=cfg['heterogeneity_crosscheck']; ref=float(h['canonical_decay_only_reference_26Al_27Al']); cai1=float(h['measured_chondrule_bearing_CAI1_26Al_27Al']); cai2=float(h['measured_chondrule_bearing_CAI2_26Al_27Al_upper_bound'])
cross={'canonical_reference':ref,'CAI1_fraction_of_reference':cai1/ref,'CAI1_deficit_percent':(1-cai1/ref)*100,
       'CAI2_upper_bound_fraction_of_reference':cai2/ref,'CAI2_minimum_deficit_percent':(1-cai2/ref)*100,
       'interpretation':'Time sets a decay reference, but local reservoir/mixing history can strongly modify local 26Al inventory.',
       'guard':h['guard']}
result={'schema':'oric.26al-chronometry-deep-sensitivity.v2','analysis_status':'retrospective_analytic_sensitivity','half_life_myr':hl,
        'events':events,'adjacent_event_separation':adj,'heterogeneity_crosscheck':cross,
        'key_limits':['Canonical median inventory decreases monotonically, but every adjacent pair has overlapping propagated 95% intervals.',
                      'Threshold accessibility changes under the declared reservoir depletion scenarios; time alone is not a unique local-inventory predictor.',
                      'The cross-check is deterministic and post hoc; no significance test is invented.',
                      'This is not a thermal simulation, a heating probability, or a do(m) intervention.'],
        'section_XIV_credit':False}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n'); print(OUT)
