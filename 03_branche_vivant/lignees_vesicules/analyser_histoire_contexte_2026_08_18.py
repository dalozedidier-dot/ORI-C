#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / 'plateforme/campagne_maximale_reelle/data'
OUT = HERE / 'resultats/HISTOIRE_CONTEXTE_2026_08_18.json'
EXISTING = HERE / 'resultats/DYNAMIQUE_TEMPORELLE.json'
SEED = 20260818

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()

def bh(p):
    p = np.asarray(p, float); n = len(p); order = np.argsort(p); q = np.empty(n); prev = 1.0
    for rank in range(n, 0, -1):
        idx = order[rank-1]; val = min(prev, p[idx]*n/rank); q[idx] = val; prev = val
    return q

def endpoint_contrasts(lin):
    rng = np.random.default_rng(SEED); rows = []
    for src, g in lin.groupby('source_file'):
        if not {'selection','drift'} <= set(g.arm.dropna().unique()): continue
        common = int(min(g[g.arm=='selection'].generation.max(), g[g.arm=='drift'].generation.max()))
        gg = g[g.generation==common]
        a = gg[gg.arm=='selection']['yield'].dropna().to_numpy(float)
        b = gg[gg.arm=='drift']['yield'].dropna().to_numpy(float)
        if len(a) < 2 or len(b) < 2: continue
        diff = float(a.mean()-b.mean())
        pooled = math.sqrt(((len(a)-1)*a.var(ddof=1)+(len(b)-1)*b.var(ddof=1))/(len(a)+len(b)-2))
        combined = np.r_[a,b]; exceed = 0; permutations = 20000
        for _ in range(permutations):
            z = rng.permutation(combined); pdiff = z[:len(a)].mean()-z[len(a):].mean()
            exceed += abs(pdiff) >= abs(diff)-1e-15
        boot = np.empty(10000)
        for i in range(len(boot)):
            boot[i] = rng.choice(a,len(a),replace=True).mean()-rng.choice(b,len(b),replace=True).mean()
        r = g.iloc[0]
        rows.append({
            'source_file':src,'condition':str(r.condition),'fed':bool(r.fed),'resuspended':bool(r.resuspended),
            'generation_duration_h':float(r.generation_duration_h),'last_shared_generation':common,
            'n_selection':len(a),'n_drift':len(b),'selection_mean_yield':float(a.mean()),'drift_mean_yield':float(b.mean()),
            'selection_minus_drift_mean_yield':diff,'standardized_difference':float(diff/pooled) if pooled else None,
            'bootstrap95':[float(x) for x in np.quantile(boot,[.025,.975])],
            'permutation_p_two_sided':float((exceed+1)/(permutations+1))
        })
    q = bh([r['permutation_p_two_sided'] for r in rows])
    for r,x in zip(rows,q): r['BH_FDR_q'] = float(x)
    return sorted(rows,key=lambda x:(x['condition'],x['generation_duration_h'],x['source_file']))

def add_ancestors(t,max_depth=4):
    out=t.copy(); lookup=out.set_index('lineage_id')[['parent_id','yield']].to_dict('index')
    for depth in range(1,max_depth+1):
        vals=[]
        for row in out.itertuples():
            pid=row.parent_id; value=np.nan
            for _ in range(depth):
                if pd.isna(pid) or pid not in lookup: value=np.nan; break
                rec=lookup[pid]; value=rec['yield']; pid=rec['parent_id']
            vals.append(value)
        out[f'ancestor_yield_d{depth}']=vals
    return out

def ridge_oof(data,numeric,categorical,target='yield',group='source_file'):
    pred=np.full(len(data),np.nan); splitter=GroupKFold(n_splits=5)
    for train,test in splitter.split(data,groups=data[group]):
        trans=[]
        if numeric: trans.append(('num',Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())]),numeric))
        if categorical: trans.append(('cat',OneHotEncoder(handle_unknown='ignore'),categorical))
        model=Pipeline([('features',ColumnTransformer(trans)),('ridge',Ridge(alpha=1.0))])
        model.fit(data.iloc[train],data.iloc[train][target]); pred[test]=model.predict(data.iloc[test])
    return pred

def history_depth(lin):
    t=add_ancestors(lin,4); req=[f'ancestor_yield_d{d}' for d in range(1,5)]
    use=t.dropna(subset=['yield','source_file']+req).copy(); y=use['yield'].to_numpy(float)
    base_num=['generation','generation_duration_h']; cat=['condition','arm','fed','resuspended']
    pred=ridge_oof(use,base_num,cat); prev=float(np.sqrt(np.mean((y-pred)**2)))
    levels=[{'depth':0,'RMSE':prev,'incremental_gain_percent':None}]
    for depth in range(1,5):
        pred=ridge_oof(use,base_num+[f'ancestor_yield_d{d}' for d in range(1,depth+1)],cat)
        rmse=float(np.sqrt(np.mean((y-pred)**2))); gain=(prev-rmse)/prev*100
        levels.append({'depth':depth,'RMSE':rmse,'incremental_gain_percent':gain}); prev=rmse
    return {'rows_common_through_depth4':len(use),'source_files':int(use.source_file.nunique()),'levels':levels,
            'effective_depth_at_2pct_increment':max([x['depth'] for x in levels if x['depth'] and x['incremental_gain_percent']>=2] or [0]),
            'deeper_than_parent_adds_2pct_increment':any(x['depth']>=2 and x['incremental_gain_percent']>=2 for x in levels if x['depth'])}

lin=pd.read_csv(DATA/'prebiotic_lineages.csv')
end=endpoint_contrasts(lin); depth=history_depth(lin)
by={}
for cond in sorted(set(r['condition'] for r in end)):
    rr=[r for r in end if r['condition']==cond]
    by[cond]={'source_files':len(rr),'mean_selection_minus_drift':float(np.mean([x['selection_minus_drift_mean_yield'] for x in rr])),
              'median_selection_minus_drift':float(np.median([x['selection_minus_drift_mean_yield'] for x in rr])),
              'positive_sources':sum(x['selection_minus_drift_mean_yield']>0 for x in rr),
              'nominal_p_lt_0_05':sum(x['permutation_p_two_sided']<.05 for x in rr),
              'FDR_q_lt_0_05':sum(x['BH_FDR_q']<.05 for x in rr)}
existing=json.loads(EXISTING.read_text(encoding='utf-8'))
result={
 'schema':'oric.vesicle-history-context-reanalysis.v2','analysis_status':'real_data_retrospective_reanalysis',
 'inputs':{'prebiotic_lineages.csv':{'rows':len(lin),'sha256':sha(DATA/'prebiotic_lineages.csv')},
           'prebiotic_timecourses.csv':{'rows':existing['rows'],'sha256':existing['source_sha256']}},
 'time_resolved_existing_result':{'FR_vs_controls':existing['FR_vs_controls'],'original_Pacc_ablation_contrast':existing['original_Pacc_ablation_contrast'],
                                  'original_Pacc_bootstrap95':existing['original_Pacc_bootstrap95']},
 'selection_vs_drift_same_final_condition':end,'selection_vs_drift_summary_by_condition':by,
 'frozen_history_depth_reproduction':depth,
 'key_limits':[
   'The discrete P_acc ablation contrast remains negative and is not requalified.',
   'Only the immediate parent reaches the frozen 2% incremental-gain rule; deeper ancestors do not.',
   'Selection-versus-drift endpoint effects are heterogeneous across source files and conditions; several are null after FDR correction.',
   'These are retrospective analyses of the existing experiment, not PACC-INT-CHALLENGE-V1 execution.'
 ],
 'strict_PACC_INT_CHALLENGE_V1_qualified':False,'section_XIV_credit':False
}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(OUT)
