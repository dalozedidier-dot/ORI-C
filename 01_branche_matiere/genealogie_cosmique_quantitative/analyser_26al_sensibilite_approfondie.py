#!/usr/bin/env python3
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
DISTRIBUTION=HERE/'resultats/DISTRIBUTION_ACCESSIBILITE_26AL.json'
CROSSCHECK=HERE/'resultats/CROSSCHECK_HETEROGENEITE_26AL.json'
OUT=HERE/'resultats/AL26_CHRONOMETRIE_APPROFONDIE.json'
Z95=1.959963984540054
dist=json.loads(DISTRIBUTION.read_text(encoding='utf-8'))
cross_source=json.loads(CROSSCHECK.read_text(encoding='utf-8'))
HALF_LIFE_MYR=float(dist['half_life_myr'])
THRESHOLDS=[float(x) for x in dist['threshold_partition']]
RESERVOIR_DEPLETION_FACTORS=[1.0,3.0,4.0]
events=[]
for e in dist['events']:
    t=float(e['time_after_CAI_myr']); s=float(e['time_sigma_myr'])
    canonical=2**(-t/HALF_LIFE_MYR); q025=2**(-(t+Z95*s)/HALF_LIFE_MYR); q975=2**(-(t-Z95*s)/HALF_LIFE_MYR)
    rec={'event':e['event'],'time_after_CAI_myr':t,'time_sigma_myr':s,'canonical':{'median':canonical,'q025':q025,'q975':q975},'reservoir_scenarios':{}}
    for f in RESERVOIR_DEPLETION_FACTORS:
        key='canonical' if f==1 else f'depleted_x{int(f)}'; med=canonical/f; lo=q025/f; hi=q975/f
        rec['reservoir_scenarios'][key]={'factor':f,'median':med,'q025':lo,'q975':hi,
          'thresholds_at_median':[x for x in THRESHOLDS if med>=x],
          'thresholds_robust_q025':[x for x in THRESHOLDS if lo>=x]}
    stable=set(THRESHOLDS)
    for r in rec['reservoir_scenarios'].values(): stable &= set(r['thresholds_robust_q025'])
    rec['thresholds_robust_across_all_declared_reservoir_scenarios']=sorted(stable,reverse=True)
    events.append(rec)
adj=[]
for a,b in zip(events,events[1:]):
    A=a['canonical']; B=b['canonical']; overlap=max(0.0,min(A['q975'],B['q975'])-max(A['q025'],B['q025']))
    adj.append({'earlier_event':a['event'],'later_event':b['event'],'median_fraction_ratio_earlier_over_later':A['median']/B['median'],
                '95pct_fraction_intervals_overlap':bool(overlap>0),'overlap_width':overlap})
ref=float(cross_source['canonical_decay_only_reference_26Al_27Al'])
cai1=float(cross_source['measured_chondrule_bearing_CAI1_26Al_27Al'])
cai2=float(cross_source['measured_chondrule_bearing_CAI2_26Al_27Al_upper_bound'])
cross={'canonical_reference':ref,'CAI1_fraction_of_reference':cai1/ref,'CAI1_deficit_percent':(1-cai1/ref)*100,
       'CAI2_upper_bound_fraction_of_reference':cai2/ref,'CAI2_minimum_deficit_percent':(1-cai2/ref)*100,
       'interpretation':'Time sets a decay reference, but local reservoir/mixing history can strongly modify local 26Al inventory.',
       'guard':'posthoc deterministic cross-check; no invented uncertainty or significance test'}
result={'schema':'oric.26al-chronometry-deep-sensitivity.v2','analysis_status':'retrospective_analytic_sensitivity','half_life_myr':HALF_LIFE_MYR,
        'events':events,'adjacent_event_separation':adj,'heterogeneity_crosscheck':cross,
        'key_limits':['Canonical median inventory decreases monotonically, but every adjacent pair has overlapping propagated 95% intervals.',
                      'Threshold accessibility changes under the declared reservoir depletion scenarios; time alone is not a unique local-inventory predictor.',
                      'The cross-check is deterministic and post hoc; no significance test is invented.',
                      'This is not a thermal simulation, a heating probability, or a do(m) intervention.'],
        'section_XIV_credit':False}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n'); print(OUT)
