import math
import numpy as np
import pandas as pd
from common import DATA, SEED, sha256, dump

rng=np.random.default_rng(SEED)
p_tc=DATA/'prebiotic_timecourses.csv'
tc=pd.read_csv(p_tc)
metrics=[]
for (cond,gen,well),d in tc.groupby(['condition','generation','well']):
    d=d.sort_values('time_seconds')
    t=d.time_seconds.to_numpy(float)/3600.0
    y=d.turbidity_A400.to_numpy(float)
    a=(t>=0)&(t<=2); b=(t>=2)&(t<=6)
    if a.sum()<2 or b.sum()<2:
        continue
    early_min=float(np.nanmin(y[a])); rebound_max=float(np.nanmax(y[b]))
    metrics.append({
        'condition':cond,'generation':gen,'well':well,
        'rebound_amp':rebound_max-early_min,
        'auc_2_6_above_early_min':float(np.trapezoid(y[b]-early_min,t[b])),
        'slope_2_6_per_hour':float(np.polyfit(t[b],y[b],1)[0])
    })
met=pd.DataFrame(metrics)

def compare(condA,genA,condB,genB,metric,N=19999):
    a=met[(met.condition==condA)&(met.generation==genA)][metric].to_numpy()
    b=met[(met.condition==condB)&(met.generation==genB)][metric].to_numpy()
    obs=float(a.mean()-b.mean())
    boots=np.empty(20000)
    for i in range(len(boots)):
        boots[i]=rng.choice(a,len(a),replace=True).mean()-rng.choice(b,len(b),replace=True).mean()
    z=np.r_[a,b]; n1=len(a); k=0
    for _ in range(N):
        q=rng.permutation(z)
        if q[:n1].mean()-q[n1:].mean()>=obs:
            k+=1
    return {
        'n_A':len(a),'n_B':len(b),'mean_difference':obs,
        'bootstrap95':[float(x) for x in np.quantile(boots,[.025,.975])],
        'permutation_p_one_sided':float((k+1)/(N+1))
    }

summary=[]
for (c,g),x in met.groupby(['condition','generation']):
    summary.append({'condition':c,'generation':g,'n_wells':len(x),**{
        m:{'mean':float(x[m].mean()),'median':float(x[m].median()),'sd':float(x[m].std())}
        for m in ['rebound_amp','auc_2_6_above_early_min','slope_2_6_per_hour']
    }})
comps={}
for gen,controls in [('gen1',['FU','UR','UU']),('gen2',['UR','UU'])]:
    for c in controls:
        for m in ['rebound_amp','auc_2_6_above_early_min','slope_2_6_per_hour']:
            comps[f'FR_{gen}_minus_{c}_{gen}:{m}']=compare('FR',gen,c,gen,m)

lin=pd.read_csv(DATA/'prebiotic_lineages.csv')
short=[]
for src,g in lin[lin.condition=='FR'].groupby('source_file'):
    dur=float(g.generation_duration_h.iloc[0])
    common=int(min(g[g.arm=='drift'].generation.max(),g[g.arm=='selection'].generation.max()))
    gg=g[g.generation==common]
    s=gg[gg.arm=='selection']['yield']; d=gg[gg.arm=='drift']['yield']
    if len(s) and len(d):
        pooled=math.sqrt(((len(s)-1)*s.var()+(len(d)-1)*d.var())/(len(s)+len(d)-2))
        short.append({
            'source_file':src,'generation_duration_h':dur,'last_shared_generation':common,
            'selection_minus_drift_mean_yield':float(s.mean()-d.mean()),
            'standardized_difference':float((s.mean()-d.mean())/pooled) if pooled else None,
            'n_selection':len(s),'n_drift':len(d)
        })

out={
 'schema':'oric.vesicle-temporal-reanalysis.v1',
 'source':'plateforme/campagne_maximale_reelle/data/prebiotic_timecourses.csv',
 'source_sha256':sha256(p_tc),'rows':len(tc),
 'analysis_status':'retrospective_exploratory_mechanistic_reanalysis',
 'window_rationale':'2-6 h window is used to quantify the published second-growth temporal regime; it is not a new prospective Pacc definition',
 'metrics_by_condition_generation':summary,
 'FR_vs_controls':comps,
 'FR_selection_drift_endpoint_by_generation_duration':sorted(short,key=lambda x:x['generation_duration_h']),
 'original_Pacc_ablation_contrast':-0.0375,
 'original_Pacc_bootstrap95':[-0.1458333333333,0.0625],
 'original_Pacc_provenance':{
    'status':'historical_result_not_regenerated_in_this_package',
    'source_result_sha256':'562c0bc4e6e5a0c09755d25d540c289c93c68af6ed23253928a992dd2e478f8b'
 },
 'interpretation':'The old discrete-class Pacc result remains negative. Time-resolved A400 shows a distinct FR rebound/slope regime that is erased by an inventory-only endpoint proxy. This is a mechanism-level reanalysis, not retrospective requalification of Pacc.',
 'strict_PACC_INT_CHALLENGE_V1_qualified':False
}
dump('VESICULES_DYNAMIQUE_TEMPORELLE.json',out)
print('VES OK', len(tc))
