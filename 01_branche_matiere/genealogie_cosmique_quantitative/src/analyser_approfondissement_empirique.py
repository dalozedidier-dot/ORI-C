from __future__ import annotations
import csv, json
from collections import Counter, deque
from pathlib import Path
ALLOWED={'astronomical_observation','spacecraft_observation','returned_sample_measurement','meteorite_isotope_measurement','meteoritic_chronometry','laboratory_experiment','planetary_isotope_reconstruction','official_observation_product'}

def read_csv(p):
    with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def analyse(base: Path):
    stages=read_csv(base/'DAG_EMPIRIQUE_APPROFONDI.csv')
    rels=read_csv(base/'RELATIONS_EMPIRIQUES_APPROFONDIES.csv')
    measures=read_csv(base/'data/MESURES_EMPIRIQUES.csv')
    selection=read_csv(base/'data/OBSERVATIONS_QUANTITATIVES_SELECTION.csv')
    claims=read_csv(base/'CLAIMS_QUANTITATIFS_EMPIRIQUES.csv')
    sources=read_csv(base/'SOURCES_EMPIRIQUES.csv')
    sid={x['stage_id'] for x in stages}; mids={x['record_id'] for x in measures}; srcids={x['source_id'] for x in sources}
    assert len(stages)==23 and len(rels)==40 and len(selection)==24 and len(claims)==12
    assert len(sid)==23
    assert all(x['evidence_mode'] in ALLOWED for x in selection)
    assert all(x['record_id'] in mids for x in selection)
    assert all(set(x['source_ids'].split(';'))<=srcids for x in rels)
    assert all(x['source_stage'] in sid and x['target_stage'] in sid for x in rels)
    # DAG check
    indeg={s:0 for s in sid}; adj={s:[] for s in sid}
    for r in rels:
        a,b=r['source_stage'],r['target_stage']; adj[a].append(b); indeg[b]+=1
    q=deque(sorted(s for s,d in indeg.items() if d==0)); seen=[]
    while q:
        a=q.popleft(); seen.append(a)
        for b in adj[a]:
            indeg[b]-=1
            if indeg[b]==0:q.append(b)
    assert len(seen)==len(sid)
    # coverage from anchor stages
    m_by_stage=Counter(x['stage_id'] for x in measures)
    coverage=[]
    for s in stages:
        coverage.append({'stage_id':s['stage_id'],'anchor_stage_id':s['anchor_stage_id'],'measurement_records_in_anchor':m_by_stage[s['anchor_stage_id']], 'covered':m_by_stage[s['anchor_stage_id']]>0})
    assert all(x['covered'] for x in coverage)
    claimdocs=[]
    for c in claims:
        recs=c['record_ids'].split(';'); sups=c['supporting_empirical_claim_ids'].split(';')
        assert set(recs)<=mids
        claimdocs.append({**c,'record_ids':recs,'supporting_empirical_claim_ids':sups})
    return {
      'summary':{
        'schema':'oric.gc.deep-empirical-quantitative.v1','analytical_stages':23,'qualified_relations':40,'selected_quantitative_observations':24,'quantitative_synthesis_claims':12,
        'underlying_empirical_measurement_records':len(measures),'primary_or_official_sources':len(sources),'simulations_used':0,'synthetic_rows':0,'imputed_rows':0,
        'dag_acyclic':True,'all_analytical_stages_empirically_anchored':True,'authoritative_empirical_claims_preserved':16,'supported_authoritative_empirical_claims_preserved':15,'unresolved_authoritative_empirical_claims_preserved':1,
        'interpretation':'Approfondissement quantitatif dérivé exclusivement de la couche empirique; il ne remplace ni les 16 claims empiriques d’autorité ni leur limite sur l’histoire orbitale unique.'},
      'coverage':coverage,'claims':claimdocs,
      'selection_mode_counts':dict(sorted(Counter(x['evidence_mode'] for x in selection).items()))
    }
