import pandas as pd
from common import DATA, sha256, dump
p=DATA/'late_accretion_tracers.csv'; la=pd.read_csv(p)
rich=la.groupby(['sample_id','candidate_source']).tracer.nunique().reset_index(name='n_tracers')
out={'schema':'oric.late-accretion-existing-data-audit.v1','rows':len(la),'source_sha256':sha256(p),
'unique_samples':int(la.sample_id.nunique()),'candidate_source_labels':int(la.candidate_source.nunique()),
'tracers':{str(k):int(v) for k,v in la.tracer.value_counts().items()},
'uncertainty_nonmissing_fraction':float(la.uncertainty.notna().mean()),
'samples_with_2plus_tracers':int((rich.n_tracers>=2).sum()),'samples_with_4plus_tracers':int((rich.n_tracers>=4).sum()),
'max_tracers_per_sample':int(rich.n_tracers.max()),
'interpretation':'Large multitracer coverage exists and was underexploited, but candidate_source is a geological-family label rather than a late-accretion mixing endmember and per-measurement uncertainties are absent. The table can support fingerprint/sensitivity work, not a calibrated late-accretion mixing claim.'}
dump('ACCRETION_TARDIVE_AUDIT_MULTITRACEUR.json',out)
print('ACCRETION OK',len(la))
