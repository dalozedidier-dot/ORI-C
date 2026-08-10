#!/usr/bin/env python3
from pathlib import Path
import json
import pandas as pd
from scipy.stats import fisher_exact, spearmanr
HERE=Path(__file__).resolve().parent; D=pd.read_csv(HERE/'data/replay_counts_blount2008.csv')
reps=[c for c in D if c.endswith('_replicates')]; pos=[c for c in D if c.endswith('_citplus')]
D['replicates_total']=D[reps].sum(axis=1); D['citplus_total']=D[pos].sum(axis=1)
pre=D[D.generation<20000]; post=D[D.generation>=20000]
a=int(pre.citplus_total.sum()); b=int(pre.replicates_total.sum()-a); c=int(post.citplus_total.sum()); d=int(post.replicates_total.sum()-c)
odds,p=fisher_exact([[c,d],[a,b]],alternative='greater')
# Corrélation descriptive entre génération et proportion, pondération non appliquée.
rate=D.citplus_total/D.replicates_total.replace(0,float('nan'))
rho,rhop=spearmanr(D.generation,rate,nan_policy='omit')
result={'status':'secondary_reanalysis_of_published_replay_counts','source_doi':'10.1073/pnas.0803151105',
 'totals':{'replicates':int(D.replicates_total.sum()),'citplus':int(D.citplus_total.sum())},
 'pre_20000_generations':{'replicates':int(pre.replicates_total.sum()),'citplus':a},
 'from_20000_generations':{'replicates':int(post.replicates_total.sum()),'citplus':c},
 'fisher_one_sided_post_vs_pre':{'odds_ratio':None if odds==float('inf') else float(odds),'p':float(p)},
 'generation_vs_replay_success_rate_spearman':{'rho':float(rho),'p':float(rhop)},
 'interpretation':'Published replay counts are compatible with historical potentiation: Cit+ replay events occur only from later sampled ancestors in this table.',
 'scope':'External historical-contingency benchmark; secondary table transcription, exploratory for ORI-C, no certification level assigned.'}
(HERE/'resultats/RESULTAT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
