import json
import pandas as pd
from scipy import stats
from common import DATA, sha256, dump
p_e=DATA/'endosymbiosis_events.csv'; p_h=DATA/'endosymbiont_hmm_presence_absence.csv'
e=pd.read_csv(p_e); h=pd.read_csv(p_h)
rows=[]
for _,r in e.iterrows():
    for sec,val in json.loads(r.section_retention_json).items():
        rows.append({'event_id':r.event_id,'genome_retention':float(r.genome_retention_proxy),'section':sec,'retention':float(val)})
s=pd.DataFrame(rows); wide=s.pivot(index='event_id',columns='section',values='retention')
q1=e.genome_retention_proxy.quantile(.25); q3=e.genome_retention_proxy.quantile(.75)
secstats={}
for sec,g in s.groupby('section'):
    rho,p=stats.spearmanr(g.genome_retention,g.retention)
    secstats[sec]={
        'n':len(g),'mean':float(g.retention.mean()),'median':float(g.retention.median()),
        'spearman_vs_genome_retention':float(rho),'spearman_p':float(p),
        'low_genome_retention_quartile_mean':float(g[g.genome_retention<=q1].retention.mean()),
        'high_genome_retention_quartile_mean':float(g[g.genome_retention>=q3].retention.mean())}
paired={}
for sec in ['PMF','envelope','replication','transcription']:
    d=wide.translation-wide[sec]; W,p=stats.wilcoxon(d,alternative='greater')
    paired[sec]={'translation_minus_section_mean':float(d.mean()),'median':float(d.median()),
                 'translation_greater_n':int((d>0).sum()),'equal_n':int((d==0).sum()),'wilcoxon_p_one_sided':float(p)}
fr,pfr=stats.friedmanchisquare(*(wide[c] for c in ['PMF','envelope','replication','transcription','translation']))
out={
 'schema':'oric.endosymbiosis-modular-retention.v1','events':len(e),'hmm_rows':len(h),
 'source_events_sha256':sha256(p_e),'source_hmm_sha256':sha256(p_h),
 'analysis_status':'retrospective_cross_sectional_structural_analysis','section_retention':secstats,
 'paired_translation_retention':paired,'friedman_across_five_modules':{'statistic':float(fr),'p':float(pfr)},
 'interpretation':'Genome reduction is strongly non-uniform across functional modules. Translation is retained disproportionately while envelope/PMF/replication are lost earlier. This is a structural constraint pattern, not evidence of temporal memory H or an isolated trace m.',
 'counts_for_strict_invariant':False}
dump('ENDOSYMBIOSE_RETENTION_MODULAIRE.json',out)
print('ENDO OK',len(e),len(h))
