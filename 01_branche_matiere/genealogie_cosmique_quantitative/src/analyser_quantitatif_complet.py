from __future__ import annotations
import csv, json, math
from collections import defaultdict, deque
from pathlib import Path

STRICT_CLASSES={
    'same_event_observed_transformation','direct_material_inheritance_class','measured_material_continuity',
    'solar_sample_link','solar_sample_sequence','chronometric_sequence','same_system_observed_sequence',
    'solar_chronometric_sequence','same_body_history_to_endpoint'
}


def read_csv(path: Path):
    with path.open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

def fnum(row, key='value_numeric'):
    s=(row.get(key) or '').strip()
    return None if not s else float(s)

def sigma_sym(row, conservative=True):
    vals=[]
    for k in ('uncertainty_minus','uncertainty_plus'):
        v=fnum(row,k)
        if v is not None: vals.append(abs(v))
    if not vals:return None
    return max(vals) if conservative else sum(vals)/len(vals)

def combined_sigma(*rows):
    ss=[sigma_sym(r) for r in rows]
    if any(s is None for s in ss):return None
    return math.sqrt(sum(s*s for s in ss))

def decay_fraction(t_myr, half_life_myr):
    return 2.0**(-t_myr/half_life_myr)

def decay_fraction_sigma(t, st, half_life, shalf):
    f=decay_fraction(t,half_life)
    dfdt=-math.log(2.0)/half_life*f
    dfdh=math.log(2.0)*t/(half_life*half_life)*f
    return math.sqrt((dfdt*st)**2+(dfdh*shalf)**2)

def ratio_after_time(r0,sr0,t,st,half_life,shalf):
    f=decay_fraction(t,half_life)
    sf=decay_fraction_sigma(t,st,half_life,shalf)
    r=r0*f
    sr=math.sqrt((f*sr0)**2+(r0*sf)**2)
    return r,sr,f,sf

def reachable(edges,start,target,removed_node=None,removed_edge=None):
    if removed_node in (start,target):return False
    adj=defaultdict(list)
    for a,b in edges:
        if removed_node is not None and removed_node in (a,b):continue
        if removed_edge is not None and (a,b)==removed_edge:continue
        adj[a].append(b)
    q=deque([start]); seen={start}
    while q:
        a=q.popleft()
        if a==target:return True
        for b in adj[a]:
            if b not in seen:
                seen.add(b);q.append(b)
    return False

def analyse(base: Path):
    measures=read_csv(base/'data/MESURES_EMPIRIQUES.csv')
    sources=read_csv(base/'SOURCES_EMPIRIQUES.csv')
    links=read_csv(base/'LIENS_EMPIRIQUES.csv')
    stages=read_csv(base/'CHAINE_EMPIRIQUE.csv')
    freeze=json.loads((base/'GEL_ANALYSE_QUANTITATIVE_V3.json').read_text(encoding='utf-8'))
    q={r['quantity']:r for r in measures}
    v={k:fnum(r) for k,r in q.items() if fnum(r) is not None}

    # Q1 — Radiogenic accessibility. This is deterministic radioactive decay from measured/evaluated inputs.
    r0=v['canonical_CAI_initial_26Al_27Al']; sr0=sigma_sym(q['canonical_CAI_initial_26Al_27Al'])
    half=v['Al26_half_life']
    # Evaluated NuDat page gives 7.17E+5 y without a numeric uncertainty in the selected record.
    # We therefore do not invent one. When no half-life sigma is stored, only event-age + r0 uncertainties are propagated.
    shalf=0.0
    cai=q['CAI_PbPb_age']
    event_specs=[
        ('angrite','angrite_PbPb_age','differentiated_parent_body_archive'),
        ('EC002','EC002_PbPb_age','early_igneous_body_archive'),
        ('youngest_chondrule','chondrule_youngest_PbPb_age','late_chondrule_archive'),
        ('CM_carbonate','CM_carbonate_age','aqueous_parent_body_archive'),
    ]
    inventory=[]
    for name,quantity,role in event_specs:
        event=q[quantity]
        t=fnum(cai)-fnum(event)
        st=combined_sigma(cai,event)
        rr,srr,f,sf=ratio_after_time(r0,sr0,t,st,half,shalf)
        inventory.append({
            'event':name,'role':role,'time_after_CAI_myr':t,'time_sigma_myr':st,
            'remaining_26Al_fraction_of_CAI_inventory':f,'remaining_fraction_sigma':sf,
            'decayed_fraction':1.0-f,'expected_26Al_27Al_from_decay_only':rr,
            'expected_ratio_sigma_from_measured_age_and_initial_ratio':srr,
            'calculation_class':'deterministic_decay_from_empirical_inputs'
        })
    by_event={x['event']:x for x in inventory}
    t09_pass=(by_event['angrite']['remaining_26Al_fraction_of_CAI_inventory']>
              by_event['EC002']['remaining_26Al_fraction_of_CAI_inventory']>
              by_event['youngest_chondrule']['remaining_26Al_fraction_of_CAI_inventory']>
              by_event['CM_carbonate']['remaining_26Al_fraction_of_CAI_inventory'])

    # Q2 — Independent Hf-W core-formation window mapped onto the same measured nuclear clock.
    core_min=v['iron_meteorite_core_formation_after_CAI_min']
    core_max=v['iron_meteorite_core_formation_after_CAI_max']
    core_fraction_high=decay_fraction(core_min,half)
    core_fraction_low=decay_fraction(core_max,half)
    young=by_event['youngest_chondrule']['remaining_26Al_fraction_of_CAI_inventory']
    cm=by_event['CM_carbonate']['remaining_26Al_fraction_of_CAI_inventory']
    core_window={
        'published_core_formation_window_myr_after_CAI':[core_min,core_max],
        'paper_reports_age_uncertainty_approximately_myr':1.0,
        'remaining_26Al_fraction_range':[core_fraction_low,core_fraction_high],
        'remaining_fraction_at_youngest_chondrule':young,
        'core_window_vs_youngest_chondrule_inventory_factor_range':[core_fraction_low/young,core_fraction_high/young],
        'core_window_vs_CM_carbonate_inventory_factor_range':[core_fraction_low/cm,core_fraction_high/cm],
        'interpretation_limit':'The mapping quantifies available parent radionuclide inventory only; it does not model temperature, melting, size, porosity or accretion.'
    }
    t10_pass=core_fraction_low>young and core_fraction_low>cm

    # Q3 — Reservoir persistence while the radiogenic inventory changes strongly.
    sep_start=v['NC_CC_separation_start']; sep_end_min=v['NC_CC_separation_end_min']; sep_end_max=v['NC_CC_separation_end_max']
    f_start=decay_fraction(sep_start,half); f_end_min=decay_fraction(sep_end_min,half); f_end_max=decay_fraction(sep_end_max,half)
    reservoir={
        'separation_start_myr_after_solar_start':sep_start,
        'separation_end_range_myr_after_solar_start':[sep_end_min,sep_end_max],
        'minimum_persistence_myr':sep_end_min-sep_start,
        'maximum_persistence_myr':sep_end_max-sep_start,
        'persistence_half_lives_range':[(sep_end_min-sep_start)/half,(sep_end_max-sep_start)/half],
        '26Al_fraction_at_start':f_start,
        '26Al_fraction_at_end_range':[f_end_max,f_end_min],
        'inventory_decline_factor_start_to_end_range':[f_start/f_end_min,f_start/f_end_max],
        'inventory_loss_percent_start_to_end_range':[(1-f_end_min/f_start)*100.0,(1-f_end_max/f_start)*100.0],
        'result':'isotopic_partition_persists_while_radiogenic_inventory_changes_by_large_factor'
    }
    t11_pass=(reservoir['minimum_persistence_myr']>=2 and reservoir['inventory_decline_factor_start_to_end_range'][0]>5)

    # Post-hoc X01 — the canonical decay curve is a time reference, not a unique local inventory.
    # This cross-check was added after the frozen T09-T16 set and is therefore never counted
    # among the eight frozen v3 criteria. It uses already-versioned measured ratios only.
    krot_delay=v['chondrule_bearing_CAI_remelting_delay_after_canonical_CAI']
    decay_ref_at_krot=decay_fraction(krot_delay,half)
    ratio_ref_at_krot=r0*decay_ref_at_krot
    krot1=v['chondrule_bearing_CAI1_initial_26Al_27Al']
    krot2_upper=v['chondrule_bearing_CAI2_initial_26Al_27Al_upper_bound']
    heterogeneity={
        'crosscheck_id':'GCQ-X01',
        'status':'posthoc_empirical_crosscheck_not_frozen_test',
        'approximate_delay_myr_after_CAI':krot_delay,
        'canonical_decay_only_reference_fraction':decay_ref_at_krot,
        'canonical_decay_only_reference_26Al_27Al':ratio_ref_at_krot,
        'measured_chondrule_bearing_CAI1_26Al_27Al':krot1,
        'measured_CAI1_fraction_of_decay_only_reference':krot1/ratio_ref_at_krot,
        'measured_CAI1_deficit_vs_decay_only_reference_percent':(1.0-krot1/ratio_ref_at_krot)*100.0,
        'measured_chondrule_bearing_CAI2_26Al_27Al_upper_bound':krot2_upper,
        'CAI2_upper_bound_fraction_of_decay_only_reference':krot2_upper/ratio_ref_at_krot,
        'CAI2_minimum_deficit_vs_decay_only_reference_percent':(1.0-krot2_upper/ratio_ref_at_krot)*100.0,
        'independent_reported_26Al_heterogeneity_factor_range':[v['Al26_heterogeneity_factor_min'],v['Al26_heterogeneity_factor_max']],
        'result':'canonical_decay_curve_is_time_reference_not_unique_local_inventory',
        'interpretation':'Measured local 26Al/27Al values can depart substantially from the homogeneous canonical decay-only reference. Time dependence is real, but reservoir/mixing history also constrains local inventory.',
        'no_significance_test_reason':'The ~2 Myr delay is approximate and is not assigned an invented uncertainty; this is a deterministic ratio cross-check, not an independent significance test.'
    }

    # Q4 — Material memory carried by presolar grains into returned Solar System samples.
    caima=fnum(cai)
    presolar={
        'conservative_persistence_lower_bound_myr':caima,
        'conservative_persistence_lower_bound_gyr':caima/1000.0,
        'basis':'Presolar grains predate the Solar System and are measured in returned material; CAI age is used only as a conservative lower time anchor.',
        'returned_sample_bodies_with_presolar_evidence':3,
        'source_ids':['S010','S030','S031']
    }
    t12_pass=presolar['conservative_persistence_lower_bound_gyr']>4.5

    # Q5 — Ryugu late reactivation lies vastly beyond the primordial 26Al interval.
    late=v['Ryugu_late_fluid_flow_after_formation_lower_bound']
    half_lives_late=late/half
    log10_fraction=-half_lives_late*math.log10(2.0)
    ryugu={
        'late_fluid_flow_lower_bound_myr_after_formation':late,
        'elapsed_26Al_half_lives_lower_bound':half_lives_late,
        'log10_upper_bound_on_remaining_primordial_26Al_fraction':log10_fraction,
        'late_Lu_mobilization_detected':bool(v['Ryugu_late_Lu_mobilization_detected']),
        'result':'late_reactivation_is_physically_separated_from_primordial_26Al_clock',
        'cause_not_inferred':True
    }
    t13_pass=half_lives_late>1000 and log10_fraction < -300

    # Q6 — Earth provenance: record the empirical conflict instead of selecting a preferred narrative.
    earth={
        'earlier_Mo_reconstruction_source':'S027',
        'earlier_result_CC_late_addition_supported':bool(v['Earth_Mo_between_NC_CC']),
        'newer_Mo_reconstruction_source':'S042',
        'newer_result_final_10_20_wt_percent_NC_dominated':bool(v['Earth_late_stage_NC_dominated']),
        'newer_late_stage_interval_wt_percent':[v['Earth_late_stage_accretion_mass_fraction_min'],v['Earth_late_stage_accretion_mass_fraction_max']],
        'minor_CC_still_possible_final_mass_interval_wt_percent':[v['Earth_final_minor_CC_possible_mass_fraction_min'],v['Earth_final_minor_CC_possible_mass_fraction_max']],
        'latest_BSE_Mo_values_source':'S043',
        'BSE_epsilon94Mo':[v['BSE_epsilon94Mo_latest'],sigma_sym(q['BSE_epsilon94Mo_latest'])],
        'BSE_epsilon95Mo':[v['BSE_epsilon95Mo_latest'],sigma_sym(q['BSE_epsilon95Mo_latest'])],
        'S043_multivariate_homogeneous_accretion_conclusion_used_as_evidence':False,
        'reason_S043_conclusion_excluded':'Its published multivariate workflow inserts synthetic priors for missing ratios and uses Monte-Carlo regression; only the reported empirical BSE Mo values are retained under the branch policy.',
        'status':'empirically_contested_not_closed'
    }
    t14_pass=(earth['earlier_result_CC_late_addition_supported'] and earth['newer_result_final_10_20_wt_percent_NC_dominated'] and not earth['S043_multivariate_homogeneous_accretion_conclusion_used_as_evidence'])

    # Q7 — Present endpoint vector from JPL Table 1. This is not a backward reconstruction.
    planet_order=['Mercury','Venus','Earth_Moon_Barycenter','Mars','Jupiter','Saturn','Uranus','Neptune']
    endpoint=[]
    for p in planet_order:
        endpoint.append({'body':p,'a_au':v[f'{p}_JPL_fit_semimajor_axis'],'e':v[f'{p}_JPL_fit_eccentricity']})
    a=[x['a_au'] for x in endpoint]; e=[x['e'] for x in endpoint]
    endpoint_summary={
        'bodies':endpoint,'body_count':len(endpoint),
        'semimajor_axis_min_au':min(a),'semimajor_axis_max_au':max(a),'semimajor_axis_span_factor':max(a)/min(a),
        'eccentricity_min':min(e),'eccentricity_max':max(e),'eccentricity_range':max(e)-min(e),
        'source':'JPL Table 1 fitted Keplerian elements valid 1800-2050',
        'history_reconstructed':False
    }
    t15_pass=len(endpoint)==8 and endpoint_summary['semimajor_axis_span_factor']>70

    # Q8 — Strict-chain fragility and closure. No simulated graph: exact ablation of documented empirical links.
    nodes=[s['stage_id'] for s in stages]
    strict_edges=[(r['from_stage'],r['to_stage']) for r in links if r['link_class'] in STRICT_CLASSES]
    start,target='GC-E01','GC-E19'
    critical_nodes=[]
    for n in nodes:
        if n in (start,target):continue
        if not reachable(strict_edges,start,target,removed_node=n):critical_nodes.append(n)
    critical_edges=[]
    for ed in strict_edges:
        if not reachable(strict_edges,start,target,removed_edge=ed):critical_edges.append(ed)
    closure=[]
    source_counts=defaultdict(set); record_counts=defaultdict(int)
    for r in measures:
        source_counts[r['stage_id']].add(r['source_id']);record_counts[r['stage_id']]+=1
    for r in links:
        strict=r['link_class'] in STRICT_CLASSES
        closure.append({
            'from_stage':r['from_stage'],'to_stage':r['to_stage'],'link_class':r['link_class'],'strict_empirical_archive_or_sequence':strict,
            'from_independent_sources':len(source_counts[r['from_stage']]),'to_independent_sources':len(source_counts[r['to_stage']]),
            'from_measurement_records':record_counts[r['from_stage']],'to_measurement_records':record_counts[r['to_stage']],
            'closure_status':'strict_documented_relation' if strict else 'open_or_nonunique_bridge'
        })
    graph={
        'strict_path_stellar_products_to_present_endpoint':reachable(strict_edges,start,target),
        'strict_path_primordial_baseline_to_present_endpoint':reachable(strict_edges,'GC-E00','GC-E19'),
        'critical_nodes_for_stellar_to_endpoint_path':critical_nodes,
        'critical_edges_for_stellar_to_endpoint_path':[{'from_stage':a,'to_stage':b} for a,b in critical_edges],
        'critical_node_count':len(critical_nodes),'critical_edge_count':len(critical_edges),
        'strict_edge_count':len(strict_edges),'all_documented_edge_count':len(links),
        'end_to_end_status':'open_from_primordial_baseline'
    }
    t16_pass=graph['strict_path_stellar_products_to_present_endpoint'] and not graph['strict_path_primordial_baseline_to_present_endpoint'] and len(critical_nodes)>0

    tests=[
        {'test_id':'GCQ-T09','name':'radiogenic_inventory_by_dated_event','executed':True,'criterion_met':t09_pass,'scientific_verdict':'supports_strong_time_dependence_of_radiogenic_accessibility','result':{'events':inventory}},
        {'test_id':'GCQ-T10','name':'early_core_formation_radiogenic_window','executed':True,'criterion_met':t10_pass,'scientific_verdict':'supports_earlier_differentiation_archive_during_higher_26Al_inventory','result':core_window},
        {'test_id':'GCQ-T11','name':'NC_CC_reservoir_persistence_across_26Al_decay','executed':True,'criterion_met':t11_pass,'scientific_verdict':'supports_persistent_isotopic_architecture_across_large_inventory_change','result':reservoir},
        {'test_id':'GCQ-T12','name':'presolar_carrier_persistence_lower_bound','executed':True,'criterion_met':t12_pass,'scientific_verdict':'supports_gigayear_material_memory_carrier','result':presolar},
        {'test_id':'GCQ-T13','name':'Ryugu_late_reactivation_after_26Al_extinction','executed':True,'criterion_met':t13_pass,'scientific_verdict':'supports_late_reactivation_of_old_material_memory_by_unresolved_later_process','result':ryugu},
        {'test_id':'GCQ-T14','name':'Earth_provenance_competing_empirical_reconstructions','executed':True,'criterion_met':t14_pass,'scientific_verdict':'contested_not_closed','result':earth},
        {'test_id':'GCQ-T15','name':'present_endpoint_architecture_vector','executed':True,'criterion_met':t15_pass,'scientific_verdict':'endpoint_quantified_history_not_reconstructed','result':endpoint_summary},
        {'test_id':'GCQ-T16','name':'strict_chain_bottleneck_and_closure_audit','executed':True,'criterion_met':t16_pass,'scientific_verdict':'strict_stellar_to_endpoint_chain_exists_but_primordial_end_to_end_closure_open','result':graph},
    ]
    result={
        'schema':'oric.gc.quantitative-complete-results.v3',
        'data_policy':'real_measurements_and_official_empirical_data_only',
        'sources_total':len(sources),'measurement_records_total':len(measures),
        'new_v3_tests':len(tests),'criteria_met':sum(t['criterion_met'] for t in tests),
        'simulations_used':0,'synthetic_rows':0,'imputed_rows':0,'random_sampling_used':0,
        'radiogenic_inventory':inventory,'early_core_formation_window':core_window,'reservoir_persistence':reservoir,
        'radiogenic_heterogeneity_crosscheck':heterogeneity,
        'posthoc_crosschecks':1,
        'presolar_memory':presolar,'late_reactivation':ryugu,'earth_provenance':earth,'endpoint_architecture':endpoint_summary,
        'graph_closure':graph,
        'global_result':{
            'history_changes_quantified_accessible_physical_inventory':True,
            'time_only_decay_reference_is_not_unique_local_inventory':True,
            'history_carriers_persist_across_multiple_timescales':True,
            'same_single_unique_orbital_history_reconstructed':False,
            'primordial_to_present_strict_chain_closed':False,
            'Earth_provenance_closed':False,
            'verdict':'quantified_history_dependent_accessibility_with_explicit_open_links'
        },
        'freeze_status':freeze['status']
    }
    return {'tests':tests,'result':result,'inventory':inventory,'closure':closure,'crosschecks':[heterogeneity]}
