#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,zipfile
from io import StringIO
import numpy as np,pandas as pd
from scipy.stats import spearmanr
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ARCH=ROOT/'donnees_externes/aicc2023/AICC2023.zip'
OUT=HERE/'AICC2023_CHRONOLOGIE_APPROFONDIE.json'
BINS=[(0,100,'0-100'),(100,300,'100-300'),(300,600,'300-600'),(600,850,'600-850')]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(z,n):
 txt=z.read(n).decode('utf-8','replace'); body=txt.split('*/',1)[1] if '*/' in txt else txt; return pd.read_csv(StringIO(body),sep='\t')
def pick(cols,terms):
 for c in cols:
  if all(t.lower() in c.lower() for t in terms): return c
 raise KeyError(terms)
out={}
with zipfile.ZipFile(ARCH) as z:
 for core in ['EDML','VOSTOK','TALDICE','EDC','NGRIP']:
  n=next(x for x in z.namelist() if x.endswith(core+'_chronology.tab')); d=load(z,n)
  a23=pick(d.columns,['Ice age','AICC2023']); a12=pick(d.columns,['Ice age','AICC2012']); sc=pick(d.columns,['Ice age unc','AICC2023'])
  age=pd.to_numeric(d[a23],errors='coerce'); old=pd.to_numeric(d[a12],errors='coerce'); sig=pd.to_numeric(d[sc],errors='coerce')
  good=age.notna()&sig.notna(); ag=age[good]; sg=sig[good]; rho,p=spearmanr(ag,sg)
  bins={}
  for lo,hi,label in BINS:
   m=(ag>=lo)&(ag<hi)
   if m.any(): bins[label]={'n':int(m.sum()),'sigma_median_ka':float(sg[m].median()),'sigma_q95_ka':float(sg[m].quantile(.95))}
  both=age.notna()&old.notna()&sig.notna()&(sig>0); delta=(age[both]-old[both]).abs(); ss=sig[both]; ratio=(delta/ss).replace([np.inf,-np.inf],np.nan).dropna()
  first=next(iter(bins.values()))['sigma_median_ka']; last=list(bins.values())[-1]['sigma_median_ka']
  out[core]={'n':int(good.sum()),'age_max_ka':float(ag.max()),'sigma_by_age_bin':bins,
    'oldest_bin_over_0_100_median_sigma_ratio':float(last/first) if first else None,
    'spearman_age_vs_sigma':{'rho':float(rho),'p':float(p)},
    'AICC2023_vs_2012_revision_diagnostic':{'n':int(both.sum()),'fraction_abs_revision_within_1_current_sigma':float((delta<=ss).mean()),
       'fraction_abs_revision_within_2_current_sigma':float((delta<=2*ss).mean()),'median_abs_revision_over_current_sigma':float(ratio.median()),
       'q95_abs_revision_over_current_sigma':float(ratio.quantile(.95)),
       'guard':'AICC2012 is not ground truth; this is revision compatibility, not coverage calibration.'}}
result={'schema':'oric.aicc2023-chronology-deep-audit.v2','analysis_status':'real_external_archive_retrospective_audit','source_sha256':sha(ARCH),'cores':out,
 'limits':['Age uncertainty increases strongly with age in all five cores, but the rate is core-dependent.',
           'AICC2023-vs-AICC2012 differences cannot be interpreted as errors against truth.',
           'An independent target and a negative chronology control remain required for the full ORI-C test.'],
 'section_XIV_credit':False}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n'); print(OUT)
