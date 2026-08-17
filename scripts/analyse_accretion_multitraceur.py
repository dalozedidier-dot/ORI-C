#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'data'/'late_accretion_tracers.csv'; OUT=ROOT/'resultats'/'ACCRETION_MULTITRACEUR_APPROFONDIE.json'
def sha(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def eta2(y,groups):
 y=np.asarray(y,float); grand=y.mean(); sst=((y-grand)**2).sum(); ssb=0.0
 temp=pd.DataFrame({'y':y,'g':np.asarray(groups)})
 for _,g in temp.groupby('g'): ssb+=len(g)*(g.y.mean()-grand)**2
 return float(ssb/sst) if sst else None
t=pd.read_csv(P); rich=t.groupby(['sample_id','candidate_source']).tracer.nunique().reset_index(name='n_tracers')
tr=[]
for tracer,g in t.groupby('tracer'):
 x=g.copy(); x['log10_value']=np.log10(x.final_value.astype(float))
 raw=eta2(x.log10_value,x.candidate_source)
 x['compilation_residual']=x.log10_value-x.groupby('compilation').log10_value.transform('mean')
 conditional=eta2(x.compilation_residual,x.candidate_source)
 tr.append({'tracer':tracer,'rows':len(x),'candidate_source_labels':int(x.candidate_source.nunique()),'compilations':int(x.compilation.nunique()),
            'eta2_candidate_source_log10_value':raw,'eta2_candidate_source_after_compilation_mean_removal':conditional})
tr=sorted(tr,key=lambda x:x['eta2_candidate_source_after_compilation_mean_removal'],reverse=True)
by_source=[]
for src,g in t.groupby('candidate_source'):
 r=rich[rich.candidate_source==src]
 by_source.append({'candidate_source':src,'rows':len(g),'unique_samples':int(g.sample_id.nunique()),'tracer_types':int(g.tracer.nunique()),
                   'samples_with_2plus_tracers':int((r.n_tracers>=2).sum()),'samples_with_4plus_tracers':int((r.n_tracers>=4).sum())})
result={'schema':'oric.late-accretion-multitracer-deep-audit.v2','analysis_status':'real_data_retrospective_descriptive_audit',
 'source_sha256':sha(P),'rows':len(t),'unique_samples':int(t.sample_id.nunique()),'candidate_source_labels':int(t.candidate_source.nunique()),
 'uncertainty_nonmissing_fraction':float(t.uncertainty.notna().mean()),'samples_with_2plus_tracers':int((rich.n_tracers>=2).sum()),
 'samples_with_4plus_tracers':int((rich.n_tracers>=4).sum()),'max_tracers_per_sample':int(rich.n_tracers.max()),
 'tracer_specific_candidate_source_structure':tr,'candidate_source_coverage':sorted(by_source,key=lambda x:(-x['rows'],x['candidate_source'])),
 'key_limits':['Per-measurement uncertainties are absent (0% non-missing).',
               'candidate_source is a geological-family label, not a calibrated late-accretion mixing endmember.',
               'Candidate-source structure remains tracer-dependent after a simple compilation-mean removal; this is descriptive, not a causal or calibrated mixing result.',
               'The weakest conditional source structure occurs for some tracers and must be preserved as a limit rather than averaged away.'],
 'calibrated_late_accretion_mixing_claim':False,'section_XIV_credit':False}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n'); print(OUT)
