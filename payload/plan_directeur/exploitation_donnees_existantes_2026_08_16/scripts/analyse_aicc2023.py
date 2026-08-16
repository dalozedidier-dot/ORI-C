import zipfile, tempfile
from pathlib import Path
import pandas as pd
import numpy as np
from common import EXT, dump

BINS=[(0,100,'0-100'),(100,300,'100-300'),(300,600,'300-600'),(600,850,'600-850')]
CORES=['EDML','VOSTOK','TALDICE','EDC','NGRIP']

def load_tab(path):
    text=path.read_text(encoding='utf-8',errors='replace')
    body=text.split('*/',1)[1] if '*/' in text else text
    from io import StringIO
    return pd.read_csv(StringIO(body),sep='\t')

def pick(cols, contains):
    for c in cols:
        if all(x.lower() in c.lower() for x in contains): return c
    raise KeyError((contains,cols))

out={}
with tempfile.TemporaryDirectory() as td:
    with zipfile.ZipFile(EXT/'AICC2023.zip') as z: z.extractall(td)
    root=Path(td)
    for core in CORES:
        p=next(root.rglob(core+'_chronology.tab'))
        d=load_tab(p)
        age23=pick(d.columns,['Ice age','AICC2023'])
        age12=pick(d.columns,['Ice age','AICC2012'])
        sig=pick(d.columns,['Ice age unc','AICC2023'])
        age=pd.to_numeric(d[age23],errors='coerce')
        old=pd.to_numeric(d[age12],errors='coerce')
        sigma=pd.to_numeric(d[sig],errors='coerce')
        good=age.notna() & sigma.notna()
        ageg=age[good]; sigg=sigma[good]
        by={}
        for lo,hi,name in BINS:
            m=(ageg>=lo)&(ageg<hi)
            if m.any():
                by[name]={'n':int(m.sum()),'sigma_median_ka':float(sigg[m].median()),'sigma_q95_ka':float(sigg[m].quantile(.95))}
        dd=(age-old).dropna()
        out[core]={
            'n':int(good.sum()),'age_max_ka':float(ageg.max()),'sigma_median_ka':float(sigg.median()),'sigma_max_ka':float(sigg.max()),
            'sigma_by_age_bin':by,
            'AICC2023_minus_2012_median_ka':float(dd.median()),
            'AICC2023_minus_2012_abs_q95_ka':float(dd.abs().quantile(.95)),
            'AICC2023_minus_2012_abs_max_ka':float(dd.abs().max())}
dump('RESULTAT_AICC2023_UNCERTAINTY.json',out)
print('AICC OK', out['EDC']['n'])
