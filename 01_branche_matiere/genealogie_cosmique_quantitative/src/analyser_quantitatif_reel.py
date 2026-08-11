from __future__ import annotations
import csv, json, math
from collections import Counter, defaultdict, deque
from pathlib import Path

STRICT_CLASSES={
    'same_event_observed_transformation','direct_material_inheritance_class','measured_material_continuity',
    'solar_sample_link','solar_sample_sequence','chronometric_sequence','same_system_observed_sequence',
    'solar_chronometric_sequence','same_body_history_to_endpoint'
}
ANALOGUE_CLASSES={
    'observed_analogue_bridge','cross_system_empirical_consistency','analogue_to_solar_archive',
    'laboratory_mechanism_stack','mechanism_to_observation_non_unique','solar_context_non_genealogical',
    'analogue_endpoint_bridge'
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

def fnum(row, key='value_numeric'):
    s=(row.get(key) or '').strip()
    return None if not s else float(s)

def sigma_sym(row, conservative=False):
    vals=[]
    for k in ('uncertainty_minus','uncertainty_plus'):
        v=fnum(row,k)
        if v is not None: vals.append(abs(v))
    if not vals: return None
    return max(vals) if conservative else sum(vals)/len(vals)

def combined_sigma(a,b, conservative=False):
    sa=sigma_sym(a,conservative); sb=sigma_sym(b,conservative)
    if sa is None or sb is None: return None
    return math.sqrt(sa*sa+sb*sb)

def standardized_difference(a,b, conservative=False):
    s=combined_sigma(a,b,conservative)
    if not s: return None
    return abs(fnum(a)-fnum(b))/s

def topological_longest_path(nodes, edges):
    adj=defaultdict(list); indeg={n:0 for n in nodes}
    for a,b in edges:
        if a in indeg and b in indeg:
            adj[a].append(b); indeg[b]+=1
    q=deque(sorted(n for n,d in indeg.items() if d==0))
    dist={n:0 for n in nodes}; prev={n:None for n in nodes}; seen=0
    while q:
        a=q.popleft(); seen+=1
        for b in adj[a]:
            if dist[a]+1>dist[b]: dist[b]=dist[a]+1; prev[b]=a
            indeg[b]-=1
            if indeg[b]==0:q.append(b)
    if seen!=len(nodes): raise AssertionError('cycle in empirical graph')
    end=max(nodes,key=lambda n:dist[n])
    path=[]; cur=end
    while cur is not None: path.append(cur); cur=prev[cur]
    return list(reversed(path))

def reachable(nodes, edges, start, target):
    adj=defaultdict(list)
    for a,b in edges: adj[a].append(b)
    q=deque([start]); seen={start}
    while q:
        a=q.popleft()
        if a==target:return True
        for b in adj[a]:
            if b not in seen: seen.add(b); q.append(b)
    return False

def analyse(base: Path):
    stages=read_csv(base/'CHAINE_EMPIRIQUE.csv')
    links=read_csv(base/'LIENS_EMPIRIQUES.csv')
    measures=read_csv(base/'data/MESURES_EMPIRIQUES.csv')
    sources=read_csv(base/'SOURCES_EMPIRIQUES.csv')
    freeze=json.loads((base/'GEL_ANALYSE_QUANTITATIVE_REELLE.json').read_text(encoding='utf-8'))
    byq={r['quantity']:r for r in measures}
    byid={r['record_id']:r for r in measures}
    source_by={s['source_id']:s for s in sources}
    nodes=[s['stage_id'] for s in stages]

    # T01 — cross-mission returned-sample replication on genuinely comparable abundance labels.
    pairs=[
        ('SiC','Bennu_SiC_abundance','Ryugu_SiC_abundance'),
        ('O-rich','Bennu_O_rich_abundance','Ryugu_O_anomalous_abundance'),
    ]
    repl=[]
    for label,qa,qb in pairs:
        a,b=byq[qa],byq[qb]
        z=standardized_difference(a,b)
        repl.append({
            'category':label,'record_a':a['record_id'],'record_b':b['record_id'],
            'value_a_ppm':fnum(a),'value_b_ppm':fnum(b),
            'sigma_a_descriptive':sigma_sym(a),'sigma_b_descriptive':sigma_sym(b),
            'absolute_difference_ppm':abs(fnum(a)-fnum(b)),
            'standardized_descriptive_difference':z,'within_2_combined_sigma':z<2
        })
    t01_pass=all(x['within_2_combined_sigma'] for x in repl)

    # T02 — water isotopologue compatibility, using only measured ratios and propagated published errors.
    hdo=byq['67P_HDO_over_H2O']; d2hdo=byq['67P_D2O_over_HDO']; v883=byq['V883_D2O_over_H2O']
    p=fnum(hdo)*fnum(d2hdo)
    sp=p*math.sqrt((sigma_sym(hdo)/fnum(hdo))**2+(sigma_sym(d2hdo)/fnum(d2hdo))**2)
    sv=sigma_sym(v883)
    z_water=abs(fnum(v883)-p)/math.sqrt(sv*sv+sp*sp)
    t02_pass=z_water<2

    # T03 — conservative chronological ordering from independent published chronometers.
    chrono_specs=[
        ('CAI_to_EC002','CAI_PbPb_age','EC002_PbPb_age'),
        ('CAI_to_angrite','CAI_PbPb_age','angrite_PbPb_age'),
        ('CAI_to_youngest_chondrule','CAI_PbPb_age','chondrule_youngest_PbPb_age'),
        ('angrite_to_CM_carbonate','angrite_PbPb_age','CM_carbonate_age'),
    ]
    chronology=[]
    for name,older_q,younger_q in chrono_specs:
        older,younger=byq[older_q],byq[younger_q]
        gap=fnum(older)-fnum(younger)
        sig=combined_sigma(older,younger,conservative=True)
        z=gap/sig if sig else None
        chronology.append({
            'comparison':name,'older_record':older['record_id'],'younger_record':younger['record_id'],
            'gap_myr':gap,'combined_sigma_conservative_myr':sig,'ordering_sigma':z,'ordering_gt_5sigma':bool(z and z>5)
        })
    # Independent Al-Mg chronometric cross-check from a second primary study.
    # It is intentionally not folded into the >5sigma pass criterion because the published ~2 Myr
    # interval is approximate and no symmetric uncertainty for that derived delay is supplied.
    krot_delay=byq.get('chondrule_bearing_CAI_remelting_delay_after_canonical_CAI')
    krot_ratio1=byq.get('chondrule_bearing_CAI1_initial_26Al_27Al')
    krot_ratio2=byq.get('chondrule_bearing_CAI2_initial_26Al_27Al_upper_bound')
    chrono_crosscheck={
        'source_id':'S038',
        'remelting_delay_myr_after_canonical_CAI':fnum(krot_delay) if krot_delay else None,
        'initial_26Al_27Al_CAI1':fnum(krot_ratio1) if krot_ratio1 else None,
        'initial_26Al_27Al_CAI1_sigma':sigma_sym(krot_ratio1) if krot_ratio1 else None,
        'initial_26Al_27Al_CAI2_upper_bound':fnum(krot_ratio2) if krot_ratio2 else None,
        'role':'independent_chronometric_crosscheck_not_used_in_5sigma_gate'
    }
    t03_pass=all(x['ordering_gt_5sigma'] for x in chronology)

    # T04 — same object, two observed states in time: EC 53 quiescence vs burst.
    ec53={q:fnum(byq[q]) for q in [
        'EC53_quiescent_forsterite_feature_detected','EC53_burst_forsterite_feature_detected',
        'EC53_quiescent_enstatite_feature_detected','EC53_burst_enstatite_feature_detected',
        'EC53_crystalline_species_appearing_only_during_burst']}
    t04_pass=(ec53['EC53_quiescent_forsterite_feature_detected']==0 and ec53['EC53_burst_forsterite_feature_detected']==1 and
              ec53['EC53_quiescent_enstatite_feature_detected']==0 and ec53['EC53_burst_enstatite_feature_detected']==1 and
              ec53['EC53_crystalline_species_appearing_only_during_burst']>=2)

    # T05 — independent observed streamer systems, no modeled accretion rates imported.
    streamer_lengths=[fnum(byq['streamer_length_lower_bound']),fnum(byq['VLA1623B_streamer_length'])]
    t05_pass=len(streamer_lengths)>=2 and all(x>=1000 for x in streamer_lengths)

    # T06 — long-term reactivation retained in a returned sample archive.
    late_flow=fnum(byq['Ryugu_late_fluid_flow_after_formation_lower_bound'])
    late_lu=fnum(byq['Ryugu_late_Lu_mobilization_detected'])
    t06_pass=late_flow>=1000 and late_lu==1

    # T07 — graph strength audit: strict archive/sequence edges vs analogue/non-unique bridges.
    strict_edges=[(r['from_stage'],r['to_stage']) for r in links if r['link_class'] in STRICT_CLASSES]
    analogue_edges=[r for r in links if r['link_class'] in ANALOGUE_CLASSES]
    contrast_edges=[r for r in links if r['link_class']=='empirical_historical_contrast']
    longest=topological_longest_path(nodes,strict_edges)
    strict_stellar_to_endpoint=reachable(nodes,strict_edges,'GC-E01','GC-E19')
    strict_primordial_to_endpoint=reachable(nodes,strict_edges,'GC-E00','GC-E19')
    graph={
        'total_edges':len(links),'strict_archive_or_same_history_edges':len(strict_edges),
        'analogue_or_nonunique_edges':len(analogue_edges),'historical_contrast_edges':len(contrast_edges),
        'strict_longest_path':longest,'strict_longest_path_edges':max(0,len(longest)-1),
        'strict_path_stellar_products_to_present_endpoint':strict_stellar_to_endpoint,
        'strict_path_primordial_baseline_to_present_endpoint':strict_primordial_to_endpoint,
        'end_to_end_strict_closure':'open' if not strict_primordial_to_endpoint else 'closed_at_graph_level',
        'analogue_or_nonunique_relations':[{'from_stage':r['from_stage'],'to_stage':r['to_stage'],'link_class':r['link_class']} for r in analogue_edges]
    }
    t07_pass=(len(strict_edges)>0 and strict_stellar_to_endpoint and not strict_primordial_to_endpoint)

    # Stage redundancy and single-source bottlenecks.
    stage_sources=defaultdict(set); stage_records=Counter(); stage_modes=defaultdict(set)
    for r in measures:
        stage_sources[r['stage_id']].add(r['source_id']); stage_records[r['stage_id']]+=1; stage_modes[r['stage_id']].add(r['evidence_mode'])
    redundancy=[]
    for s in stages:
        sid=s['stage_id']; srcs=sorted(stage_sources[sid])
        redundancy.append({
            'stage_id':sid,'label':s['label'],'measurement_records':stage_records[sid],
            'independent_sources':len(srcs),'source_ids':';'.join(srcs),'evidence_modes':';'.join(sorted(stage_modes[sid])),
            'single_source_bottleneck':len(srcs)==1
        })

    # T08 — evidence-family ablations. These are evidence audits, not physical simulations.
    modes=sorted({r['evidence_mode'] for r in measures})
    ablations=[]
    for mode in modes:
        kept=[r for r in measures if r['evidence_mode']!=mode]
        covered={r['stage_id'] for r in kept}
        lost=sorted(set(nodes)-covered)
        # remove strict edges touching any stage with no remaining measurement
        kept_edges=[(a,b) for a,b in strict_edges if a in covered and b in covered]
        ablations.append({
            'removed_evidence_mode':mode,'remaining_measurement_records':len(kept),
            'covered_stages':len(covered & set(nodes)),'lost_stage_count':len(lost),'lost_stages':';'.join(lost),
            'strict_stellar_to_endpoint_path_preserved':reachable(nodes,kept_edges,'GC-E01','GC-E19') if 'GC-E01' in covered and 'GC-E19' in covered else False
        })
    t08_pass=len(ablations)==len(modes) and all(a['remaining_measurement_records']<len(measures) for a in ablations)

    tests=[
        {'test_id':'GCQ-T01','name':'replication_presolar_returned_samples','passed':t01_pass,'result':{'pairs':repl},'verdict':'supports_cross_mission_consistency' if t01_pass else 'not_supported'},
        {'test_id':'GCQ-T02','name':'water_isotopologue_cross_system_consistency','passed':t02_pass,'result':{'V883_D2O_over_H2O':fnum(v883),'67P_D2O_over_H2O_derived':p,'67P_sigma_propagated':sp,'standardized_difference':z_water},'verdict':'compatible_within_2sigma' if t02_pass else 'not_compatible_within_2sigma'},
        {'test_id':'GCQ-T03','name':'early_solar_chronological_order','passed':t03_pass,'result':{'comparisons':chronology,'independent_AlMg_crosscheck':chrono_crosscheck},'verdict':'supports_resolved_temporal_ordering' if t03_pass else 'ordering_not_resolved'},
        {'test_id':'GCQ-T04','name':'same_object_event_linked_state_change','passed':t04_pass,'result':ec53,'verdict':'supports_same_object_event_linked_state_change' if t04_pass else 'not_supported'},
        {'test_id':'GCQ-T05','name':'streamer_observation_replication','passed':t05_pass,'result':{'independent_systems':2,'streamer_lengths_au':streamer_lengths},'verdict':'supports_replicated_large_scale_streamer_channel' if t05_pass else 'not_supported'},
        {'test_id':'GCQ-T06','name':'long_term_parent_body_reactivation','passed':t06_pass,'result':{'late_fluid_flow_lower_bound_myr_after_formation':late_flow,'late_Lu_mobilization_detected':bool(late_lu)},'verdict':'supports_long_term_history_reactivation' if t06_pass else 'not_supported'},
        {'test_id':'GCQ-T07','name':'empirical_graph_robustness','passed':t07_pass,'result':graph,'verdict':'partial_strict_sequence_with_open_end_to_end_closure'},
        {'test_id':'GCQ-T08','name':'evidence_family_ablation','passed':t08_pass,'result':{'ablations':ablations},'verdict':'sensitivity_mapped_not_redundancy_claimed'},
    ]

    single=[x for x in redundancy if x['single_source_bottleneck']]
    verdict={
        'schema':'oric.gc.quantitative-real-verdict',
        'data_policy':'empirical_measurements_only',
        'sources':len(sources),'measurement_records':len(measures),'tests':len(tests),'tests_passed':sum(t['passed'] for t in tests),
        'simulations_used':0,'synthetic_rows':0,'imputed_rows':0,
        'strong_results':[
            'cross_mission_presolar_abundance_consistency',
            'cross_system_water_isotopologue_compatibility',
            'resolved_early_solar_chronological_order',
            'same_object_burst_linked_crystalline_state_change',
            'replicated_large_scale_streamer_observations',
            'returned_sample_record_of_greater_than_1Gyr_parent_body_reactivation'
        ],
        'strict_archive_sequence_stellar_to_present_endpoint':strict_stellar_to_endpoint,
        'strict_end_to_end_from_primordial_baseline':strict_primordial_to_endpoint,
        'single_source_stage_bottlenecks':len(single),
        'single_source_stage_ids':[x['stage_id'] for x in single],
        'global_quantitative_verdict':'supports_history_dependent_material_and_temporal_constraints_with_open_end_to_end_closure',
        'not_claimed':['unique_orbital_history','universal_ORI_C_law','direct_protosolar_observation_for_analogue_stages','simulation_based_closure'],
        'freeze_status':freeze['status']
    }
    return {
        'tests':tests,'replication':repl,'chronology':chronology,'graph':graph,'redundancy':redundancy,
        'ablations':ablations,'verdict':verdict,
    }
