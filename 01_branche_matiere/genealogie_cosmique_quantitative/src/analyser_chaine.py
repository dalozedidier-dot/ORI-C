from __future__ import annotations
import csv, json, hashlib
from collections import Counter
from pathlib import Path

def read_csv(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f,delimiter=';'))

def analyse(root: Path, output_dir: Path):
    br=root/'01_branche_matiere/genealogie_cosmique_quantitative'
    nodes=read_csv(br/'CHAINE_GENEALOGIQUE.csv'); sources=read_csv(br/'SOURCES_PRIMAIRES.csv'); claims=read_csv(br/'MATRICE_PREUVES.csv')
    ids={r['id'] for r in nodes}; sids={r['source_id'] for r in sources}
    errors=[]
    if len(ids)!=len(nodes): errors.append('duplicate_stage_id')
    order={r['id']:int(r['ordre']) for r in nodes}
    edges=[]
    for r in nodes:
        for p in filter(None,r['parents'].split('|')):
            if p not in ids: errors.append(f'unresolved_parent:{r["id"]}:{p}')
            else:
                edges.append((p,r['id']))
                if order[p]>=order[r['id']]: errors.append(f'non_forward_edge:{p}->{r["id"]}')
        refs=[x for x in r['source_ids'].split('|') if x]
        if r['id']!='GC-023' and not refs: errors.append(f'no_source:{r["id"]}')
        for s in refs:
            if s not in sids: errors.append(f'unresolved_source:{r["id"]}:{s}')
    for c in claims:
        for s in filter(None,c['source_ids'].split('|')):
            if s not in sids: errors.append(f'unresolved_claim_source:{c["claim_id"]}:{s}')
    # Kahn-style cycle check
    indeg={i:0 for i in ids}; adj={i:[] for i in ids}
    for a,b in edges: adj[a].append(b); indeg[b]+=1
    q=sorted([i for i,v in indeg.items() if v==0]); seen=[]
    while q:
        n=q.pop(0); seen.append(n)
        for m in sorted(adj[n]):
            indeg[m]-=1
            if indeg[m]==0: q.append(m); q.sort()
    if len(seen)!=len(ids): errors.append('cycle_detected')
    primary=sum(1 for s in sources if 'revue' not in s['source_type'].lower() and 'synthèse' not in s['source_type'].lower())
    old=root/'01_branche_matiere/genealogie/genealogie_matiere.csv'
    old_hash=hashlib.sha256(old.read_bytes()).hexdigest()
    frozen=(br/'BASELINE_GENEALOGIE_EXISTANTE.sha256').read_text().split()[0]
    if old_hash!=frozen: errors.append('existing_genealogy_changed')
    out={
      'schema':'oric.gc.chain.v1','stage_count':len(nodes),'edge_count':len(edges),'source_count':len(sources),'primary_or_primary_like_source_count':primary,
      'claim_count':len(claims),'dag_valid':len(seen)==len(ids),'all_references_resolved':not any('unresolved' in e for e in errors),
      'existing_genealogy_sha256':old_hash,'existing_genealogy_unchanged':old_hash==frozen,'first_stage':'GC-001','last_stage':'GC-023',
      'handoff_status':'open','errors':errors,'status':'ok' if not errors else 'error'
    }
    output_dir.mkdir(parents=True,exist_ok=True)
    (output_dir/'CHAINE.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')

    source_by_id={s['source_id']:s for s in sources}
    coverage=[]
    for r in nodes:
        refs=[x for x in r['source_ids'].split('|') if x]
        claim_refs=[c['claim_id'] for c in claims if r['id'] in [x for x in c['stages'].split('|') if x]]
        source_types=sorted({source_by_id[x]['source_type'] for x in refs if x in source_by_id})
        evidence_modes=sorted({source_by_id[x]['evidence_mode'] for x in refs if x in source_by_id})
        primary_refs=[x for x in refs if x in source_by_id and 'revue' not in source_by_id[x]['source_type'].lower() and 'synthèse' not in source_by_id[x]['source_type'].lower()]
        coverage.append({
            'stage_id':r['id'],'ordre':int(r['ordre']),'nom':r['nom'],
            'source_count':len(refs),'primary_source_count':len(primary_refs),
            'claim_count':len(claim_refs),'source_types':' | '.join(source_types),
            'evidence_modes':' | '.join(evidence_modes),'status':r['statut'],
            'non_demontre':r['non_demontre'],
        })
    with (output_dir/'COUVERTURE_PREUVES.csv').open('w',encoding='utf-8',newline='') as f:
        fields=list(coverage[0]); wr=csv.DictWriter(f,fieldnames=fields,delimiter=';',lineterminator='\n'); wr.writeheader(); wr.writerows(coverage)

    claim_rows=[]
    claim_dir=output_dir/'claims'; claim_dir.mkdir(parents=True,exist_ok=True)
    for c in claims:
        payload={
            'schema':'oric.gc.claim.v1',
            'claim_id':c['claim_id'],'question':c['question'],'mechanism':c['mechanism'],
            'stages':[x for x in c['stages'].split('|') if x],
            'source_ids':[x for x in c['source_ids'].split('|') if x],
            'evidence_mode':c['evidence_mode'],'directness':c['directness'],
            'verdict':c['verdict'],'scope':c['scope'],'counterfactual':c['counterfactual'],
            'limitation':c['limitation'],
        }
        (claim_dir/f"{c['claim_id']}.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
        claim_rows.append(payload)
    claim_summary={
        'schema':'oric.gc.claims.v1','claim_count':len(claim_rows),
        'verdict_counts':dict(sorted(Counter(c['verdict'] for c in claims).items())),
        'claims':claim_rows,
    }
    (output_dir/'CLAIMS.json').write_text(json.dumps(claim_summary,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')

    epist={
        'schema':'oric.gc.evidence-coverage.v1',
        'source_type_counts':dict(sorted(Counter(s['source_type'] for s in sources).items())),
        'evidence_mode_counts':dict(sorted(Counter(s['evidence_mode'] for s in sources).items())),
        'stages_with_at_least_one_source':sum(1 for r in coverage if r['source_count']>0),
        'stages_with_at_least_two_sources':sum(1 for r in coverage if r['source_count']>=2),
        'stages_total':len(coverage),
        'open_handoff_stage':'GC-023',
        'review_sources':[s['source_id'] for s in sources if 'revue' in s['source_type'].lower() or 'synthèse' in s['source_type'].lower()],
    }
    (output_dir/'COUVERTURE_EPISTEMIQUE.json').write_text(json.dumps(epist,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return out
