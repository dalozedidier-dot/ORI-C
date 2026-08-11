from __future__ import annotations
import csv,hashlib,json,math,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]

def rows(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def test_empirical_only_policy_and_banned_artifacts_absent():
    m=rows(HERE/'data/MESURES_EMPIRIQUES.csv')
    allowed={'astronomical_observation','spacecraft_observation','returned_sample_measurement','meteorite_isotope_measurement','meteoritic_chronometry','laboratory_experiment','planetary_isotope_reconstruction','official_observation_product'}
    forbidden=('synthetic','simulat','mock','constructed','numerical_model_output','theoretical_yield','thermochemical_model')
    assert m and all(x['evidence_mode'] in allowed for x in m)
    assert not any(any(t in (x['evidence_mode']+' '+x['record_id']+' '+x['quantity']+' '+x['scope_note']).lower() for t in forbidden) for x in m)
    banned={'BBN_BASELINE_ELEMENTAIRE.csv','MODELES_CONCURRENTS.csv','analyser_nucleosynthese.py','analyser_accessibilite_phases.py','ACCESSIBILITE_PHASES.json','NUCLEOSYNTHESE.json'}
    present={p.name for p in HERE.rglob('*') if p.is_file()}
    assert not (banned & present)

def test_sources_are_primary_or_official_and_mixed_sources_have_firewall():
    s=rows(HERE/'SOURCES_EMPIRIQUES.csv'); m=rows(HERE/'data/MESURES_EMPIRIQUES.csv')
    ids={x['source_id'] for x in s}
    assert len(s)==48
    assert all(x['source_class'] in {'primary_peer_reviewed','official_observation_product','curated_empirical_database','primary_research_dataset'} for x in s)
    assert all(x['url'].startswith('http') for x in s)
    assert all(x['portion_used'].strip() and x['portion_excluded'].strip() for x in s)
    assert all(x['source_id'] in ids for x in m)

def test_every_stage_has_empirical_measurement_and_source():
    stages={x['stage_id'] for x in rows(HERE/'CHAINE_EMPIRIQUE.csv')}
    m=rows(HERE/'data/MESURES_EMPIRIQUES.csv')
    covered={x['stage_id'] for x in m}
    assert len(stages)==20
    assert stages <= covered
    assert all(any(r['stage_id']==sid for r in m) for sid in stages)

def test_results_are_deep_and_empirical_only():
    s=json.loads((HERE/'resultats/SYNTHESE.json').read_text())
    a=json.loads((HERE/'resultats/AUDIT_ADMISSIBILITE.json').read_text())
    assert s['stages']==20 and s['links']==22 and s['primary_or_official_sources']==48
    assert s['empirical_measurement_records']==120
    assert s['simulations_used']==0 and s['synthetic_rows']==0 and s['imputed_rows']==0
    assert s['supported_claims']==15 and s['unresolved_claims']==1
    assert s['global_empirical_verdict']=='supports_empirical_historical_accessibility_mechanism'
    assert a['status']=='pass' and a['simulations_used_as_evidence']==0 and a['model_outputs_used_as_evidence']==0 and a['theoretical_yields_used_as_evidence']==0 and a['thermochemical_outputs_used_as_evidence']==0 and a['orbital_integrations_used_as_genealogy_evidence']==0 and a['synthetic_rows']==0 and a['imputed_rows']==0
    assert a['all_stages_have_measurements'] and a['all_stages_have_sources']

def test_stellar_dust_and_returned_sample_results():
    s=json.loads((HERE/'resultats/SYNTHESE.json').read_text())
    assert s['SN1987A_dust_mass_solar_range']==[0.4,0.7]
    assert s['SN1987A_dust_temperature_K_range']==[17.0,23.0]
    assert s['bennu_presolar_grains_total']==52
    assert s['ryugu_presolar_grains_total']==57
    assert s['returned_sample_presolar_grains_minimum_across_cited_studies']==110
    assert s['returned_sample_bodies_with_presolar_detection']==3
    assert s['wild2_refractory_and_highT_material_detected'] is True

def test_observational_molecular_comparison_is_reproducible():
    r=json.loads((HERE/'resultats/RESULTATS_EMPIRIQUES.json').read_text())['derived_from_observations']
    assert math.isclose(r['comet_67P_D2O_over_H2O_derived'],1.89e-5,rel_tol=0,abs_tol=1e-16)
    assert 0.8 < r['V883_vs_67P_standardized_difference'] < 0.9
    assert r['TW_Hya_methanol_direct_detection'] is True

def test_chronology_and_laboratory_results():
    s=json.loads((HERE/'resultats/SYNTHESE.json').read_text())
    assert math.isclose(s['chondrule_measured_age_span_myr'],2.61,abs_tol=1e-12)
    assert math.isclose(s['angrite_to_CM_carbonate_event_gap_nominal_myr'],2.8,abs_tol=1e-12)
    assert s['laboratory_erosion_threshold_m_s']==0.5
    assert s['laboratory_instability_wavelength_cm']==3.0

def test_claims_have_fifteen_positive_results_and_one_explicit_limit():
    d=json.loads((HERE/'resultats/CLAIMS.json').read_text())
    assert d['schema']=='oric.gc.claims.v3'
    by={x['claim_id']:x for x in d['claims']}
    assert len(d['claims'])==16
    assert sum(x['verdict'].startswith('supports_') for x in d['claims'])==15
    assert by['C-GC-E15']['verdict']=='supports_empirical_historical_accessibility_mechanism'
    assert by['C-GC-E15']['criteria']['all_required_local_claims_positive'] is True
    assert by['C-GC-E13']['criteria']['PDS70_same_system_disk_gap_context'] is True
    assert by['C-GC-E05']['criteria']['independent_streamer_systems']==2
    assert by['C-GC-E07']['criteria']['EC53_same_object_time_domain_change'] is True
    assert by['C-GC-E07']['criteria']['EC53_crystalline_species_appearing_only_during_burst']==2
    assert by['C-GC-E16']['verdict']=='undetermined_empirical_only'
    assert by['C-GC-E16']['criteria']['unique_history_claimed'] is False

def test_policy_and_replication_docs_exist():
    for name in ['README.md','PROTOCOLE.md','METHODOLOGIE_RECHERCHE.md','REVUE_EMPIRIQUE_APPROFONDIE.md','DICTIONNAIRE_DONNEES.md','EMPIRICAL_ONLY_POLICY.json','CRITERES_REPLICATION_FUTURE.json']:
        assert (HERE/name).is_file(), name
    p=json.loads((HERE/'EMPIRICAL_ONLY_POLICY.json').read_text())
    assert 'simulation' in p['forbidden_as_evidence'] and 'synthetic_data' in p['forbidden_as_evidence']

def test_exact_rebuild():
    with tempfile.TemporaryDirectory() as td:
        subprocess.run([sys.executable,str(HERE/'run_all.py'),'--output-dir',td],check=True,capture_output=True,text=True)
        ref=HERE/'resultats'; cand=Path(td)
        for p in sorted(ref.rglob('*')):
            if p.is_file():
                q=cand/p.relative_to(ref)
                assert q.is_file(), p
                assert hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256(q.read_bytes()).digest(),p

def test_result_manifest():
    root=HERE/'resultats'; listed={}
    for line in (root/'RESULTATS.sha256').read_text().splitlines():
        h,rel=line.split('  ',1); listed[rel]=h
    files={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and p.name!='RESULTATS.sha256'}
    assert listed==files


def test_deep_quantitative_layer_is_empirical_only():
    d=json.loads((HERE/'resultats/APPROFONDISSEMENT_EMPIRIQUE.json').read_text())
    assert d['analytical_stages']==23
    assert d['qualified_relations']==40
    assert d['selected_quantitative_observations']==24
    assert d['quantitative_synthesis_claims']==12
    assert d['underlying_empirical_measurement_records']==120
    assert d['primary_or_official_sources']==48
    assert d['simulations_used']==0 and d['synthetic_rows']==0 and d['imputed_rows']==0
    assert d['dag_acyclic'] is True and d['all_analytical_stages_empirically_anchored'] is True
    assert d['authoritative_empirical_claims_preserved']==16
    sel=rows(HERE/'data/OBSERVATIONS_QUANTITATIVES_SELECTION.csv')
    allowed={'astronomical_observation','spacecraft_observation','returned_sample_measurement','meteorite_isotope_measurement','meteoritic_chronometry','laboratory_experiment','planetary_isotope_reconstruction','official_observation_product'}
    assert len(sel)==24 and all(x['evidence_mode'] in allowed for x in sel)
    assert len(rows(HERE/'DAG_EMPIRIQUE_APPROFONDI.csv'))==23
    assert len(rows(HERE/'RELATIONS_EMPIRIQUES_APPROFONDIES.csv'))==40
    assert len(rows(HERE/'CLAIMS_QUANTITATIFS_EMPIRIQUES.csv'))==12


def test_quantitative_v2_has_real_calculations_not_count_only():
    v=json.loads((HERE/'resultats/VERDICT_QUANTITATIF.json').read_text())
    t=json.loads((HERE/'resultats/TESTS_QUANTITATIFS_REELS.json').read_text())
    assert v['schema']=='oric.gc.quantitative-real-verdict.v2'
    assert v['sources']==48 and v['measurement_records']==120
    assert v['tests']==8 and v['tests_passed']==8
    assert v['simulations_used']==0 and v['synthetic_rows']==0 and v['imputed_rows']==0
    assert v['strict_archive_sequence_stellar_to_present_endpoint'] is True
    assert v['strict_end_to_end_from_primordial_baseline'] is False
    assert v['global_quantitative_verdict']=='supports_history_dependent_material_and_temporal_constraints_with_open_end_to_end_closure'
    by={x['test_id']:x for x in t['tests']}
    assert set(by)=={f'GCQ-T{i:02d}' for i in range(1,9)}
    assert all(x['passed'] for x in by.values())
    assert by['GCQ-T01']['result']['pairs'][0]['standardized_descriptive_difference']==0
    assert by['GCQ-T01']['result']['pairs'][1]['standardized_descriptive_difference']<0.2
    assert 0.8<by['GCQ-T02']['result']['standardized_difference']<0.9
    assert all(x['ordering_gt_5sigma'] for x in by['GCQ-T03']['result']['comparisons'])
    assert by['GCQ-T03']['result']['independent_AlMg_crosscheck']['remelting_delay_myr_after_canonical_CAI']==2
    assert by['GCQ-T04']['result']['EC53_crystalline_species_appearing_only_during_burst']==2
    assert by['GCQ-T05']['result']['independent_systems']==2
    assert by['GCQ-T06']['result']['late_fluid_flow_lower_bound_myr_after_formation']>=1000


def test_quantitative_v2_ablation_and_bottlenecks_are_explicit():
    g=json.loads((HERE/'resultats/ROBUSTESSE_GRAPHE.json').read_text())
    assert g['total_edges']==22
    assert g['strict_archive_or_same_history_edges']==12
    assert g['analogue_or_nonunique_edges']==9
    assert g['historical_contrast_edges']==1
    assert g['strict_path_stellar_products_to_present_endpoint'] is True
    assert g['strict_path_primordial_baseline_to_present_endpoint'] is False
    a=rows(HERE/'resultats/ABLATIONS_FAMILLES_PREUVES.csv')
    assert len(a)>=7
    assert all(int(x['remaining_measurement_records'])<120 for x in a)
    r=rows(HERE/'resultats/REDONDANCE_PAR_STAGE.csv')
    singles={x['stage_id'] for x in r if x['single_source_bottleneck']=='True'}
    assert {'GC-E11','GC-E12','GC-E16','GC-E17','GC-E19'} <= singles
    assert 'GC-E13' not in singles and 'GC-E18' not in singles
    assert 'GC-E02' not in singles and 'GC-E10' not in singles


def test_new_empirical_sources_are_firewalled():
    s={x['source_id']:x for x in rows(HERE/'SOURCES_EMPIRIQUES.csv')}
    m={x['record_id']:x for x in rows(HERE/'data/MESURES_EMPIRIQUES.csv')}
    assert {'S034','S035','S036','S037','S038','S039','S040','S041','S042','S043'}<=set(s)
    assert s['S034']['doi']=='10.1038/s41586-025-09939-3'
    assert s['S035']['doi']=='10.1038/s41586-025-09483-0'
    assert s['S036']['doi']=='10.1093/mnras/stae472'
    assert s['S037']['doi']=='10.1088/2041-8205/782/1/L2'
    assert s['S038']['doi']=='10.1038/nature03470'
    assert m['M077']['value_numeric']=='0' and m['M078']['value_numeric']=='1'
    assert float(m['M082']['value_numeric'])>=1000
    assert float(m['M084']['value_numeric'])>=2000
    assert float(m['M086']['value_numeric'])>=0.2
    assert m['M087']['value_text']=='true'
    assert float(m['M088']['value_numeric'])==2
    assert math.isclose(float(m['M089']['value_numeric']),4.7e-6,rel_tol=0,abs_tol=1e-16)
    assert math.isclose(float(m['M090']['value_numeric']),1.2e-6,rel_tol=0,abs_tol=1e-16)


def test_quantitative_v3_complete_physical_results_are_real_and_deterministic():
    d=json.loads((HERE/'resultats/RESULTATS_QUANTITATIFS_COMPLETS.json').read_text())
    t=json.loads((HERE/'resultats/TESTS_QUANTITATIFS_COMPLETS.json').read_text())
    assert d['schema']=='oric.gc.quantitative-complete-results.v3'
    assert d['sources_total']==48 and d['measurement_records_total']==120
    assert d['new_v3_tests']==8 and d['criteria_met']==8
    assert d['simulations_used']==0 and d['synthetic_rows']==0 and d['imputed_rows']==0 and d['random_sampling_used']==0
    assert d['global_result']['history_changes_quantified_accessible_physical_inventory'] is True
    assert d['global_result']['primordial_to_present_strict_chain_closed'] is False
    inv={x['event']:x for x in d['radiogenic_inventory']}
    assert 0.34 < inv['angrite']['remaining_26Al_fraction_of_CAI_inventory'] < 0.35
    assert 0.18 < inv['EC002']['remaining_26Al_fraction_of_CAI_inventory'] < 0.19
    assert 0.08 < inv['youngest_chondrule']['remaining_26Al_fraction_of_CAI_inventory'] < 0.083
    assert 0.022 < inv['CM_carbonate']['remaining_26Al_fraction_of_CAI_inventory'] < 0.024
    by={x['test_id']:x for x in t['tests']}
    assert set(by)=={f'GCQ-T{i:02d}' for i in range(9,17)}
    assert all(x['executed'] and x['criterion_met'] for x in by.values())


def test_quantitative_v3_reservoir_memory_and_reactivation_are_quantified():
    d=json.loads((HERE/'resultats/RESULTATS_QUANTITATIFS_COMPLETS.json').read_text())
    r=d['reservoir_persistence']
    assert r['minimum_persistence_myr']==2 and r['maximum_persistence_myr']==3
    assert r['inventory_decline_factor_start_to_end_range'][0] > 6
    assert r['inventory_decline_factor_start_to_end_range'][1] > 18
    assert d['presolar_memory']['conservative_persistence_lower_bound_gyr'] > 4.5
    assert d['late_reactivation']['elapsed_26Al_half_lives_lower_bound'] > 1300
    assert d['late_reactivation']['log10_upper_bound_on_remaining_primordial_26Al_fraction'] < -400


def test_quantitative_v3_earth_conflict_is_not_artificially_closed():
    d=json.loads((HERE/'resultats/RESULTATS_QUANTITATIFS_COMPLETS.json').read_text())
    e=d['earth_provenance']
    assert e['earlier_result_CC_late_addition_supported'] is True
    assert e['newer_result_final_10_20_wt_percent_NC_dominated'] is True
    assert e['status']=='empirically_contested_not_closed'
    assert e['S043_multivariate_homogeneous_accretion_conclusion_used_as_evidence'] is False
    assert e['minor_CC_still_possible_final_mass_interval_wt_percent']==[0.5,1.0]


def test_quantitative_v3_endpoint_and_strict_bottlenecks():
    d=json.loads((HERE/'resultats/RESULTATS_QUANTITATIFS_COMPLETS.json').read_text())
    ep=d['endpoint_architecture']
    assert ep['body_count']==8 and ep['history_reconstructed'] is False
    assert 77 < ep['semimajor_axis_span_factor'] < 78
    g=d['graph_closure']
    assert g['strict_path_stellar_products_to_present_endpoint'] is True
    assert g['strict_path_primordial_baseline_to_present_endpoint'] is False
    assert g['critical_node_count']==6 and g['critical_edge_count']==6
    assert set(g['critical_nodes_for_stellar_to_endpoint_path'])=={'GC-E02','GC-E03','GC-E08','GC-E10','GC-E13','GC-E17'}


def test_new_v3_sources_and_measurements_are_explicitly_firewalled():
    s={x['source_id']:x for x in rows(HERE/'SOURCES_EMPIRIQUES.csv')}
    m={x['record_id']:x for x in rows(HERE/'data/MESURES_EMPIRIQUES.csv')}
    assert s['S039']['doi']=='10.1016/j.epsl.2008.05.003'
    assert s['S041']['doi']=='10.1016/j.gca.2012.09.015'
    assert s['S042']['doi']=='10.1016/j.gca.2024.11.005'
    assert s['S043']['doi']=='10.1038/s41550-026-02824-7'
    assert math.isclose(float(m['M091']['value_numeric']),5.23e-5,rel_tol=0,abs_tol=1e-16)
    assert math.isclose(float(m['M092']['value_numeric']),0.717,rel_tol=0,abs_tol=1e-15)
    assert float(m['M093']['value_numeric'])==1.0 and float(m['M094']['value_numeric'])==1.5
    assert float(m['M098']['value_numeric'])==10 and float(m['M099']['value_numeric'])==20
    assert float(m['M100']['value_numeric'])==0.5 and float(m['M101']['value_numeric'])==1.0
    assert m['M102']['value_text']=='true'
    assert float(m['M105']['value_numeric'])==0.38709927
    assert float(m['M119']['value_numeric'])==30.06992276
    freeze=json.loads((HERE/'GEL_ANALYSE_QUANTITATIVE_V3.json').read_text())
    assert freeze['preregistered'] is False
    assert 'monte_carlo_generated_samples' in freeze['forbidden_as_evidence']


def test_quantitative_v3_claim_artifacts_are_complete_and_machine_readable():
    d=json.loads((HERE/'resultats/CLAIMS_QUANTITATIFS_COMPLETS.json').read_text())
    assert d['schema']=='oric.gc.quantitative-claims.v3'
    claims=d['claims']
    assert len(claims)==8
    assert {c['claim_id'] for c in claims}=={f'GCQ-T{i:02d}' for i in range(9,17)}
    assert all(c['executed'] and c['criterion_met'] for c in claims)
    assert all(c['preregistered'] is False for c in claims)
    assert all(c['data_policy']=='real_measurements_and_official_empirical_data_only' for c in claims)
    for c in claims:
        p=HERE/'resultats/claims_quantitatifs_v3'/f"{c['claim_id']}.json"
        assert p.is_file()
        one=json.loads(p.read_text())
        assert one==c


def test_quantitative_v3_authority_docs_state_current_corpus_and_verdict():
    readme=(HERE/'README.md').read_text()
    review=(HERE/'REVUE_QUANTITATIVE_EMPIRIQUE.md').read_text()
    protocol=(HERE/'PROTOCOLE.md').read_text()
    assert '48 sources/datasets empiriques admissibles' in readme
    assert '120 enregistrements empiriques' in readme
    assert '34,5 %' in readme and '2,30 %' in readme
    assert 'quantified_history_dependent_accessibility_with_explicit_open_links' in readme
    assert '48 sources/datasets empiriques admissibles' in review
    assert 'GCQ-T09' in review and 'GCQ-T16' in review
    assert 'Campagne quantitative complète v3' in protocol


def test_posthoc_26Al_crosscheck_is_explicit_and_not_counted_as_frozen_test():
    d=json.loads((HERE/'resultats/RESULTATS_QUANTITATIFS_COMPLETS.json').read_text())
    x=d['radiogenic_heterogeneity_crosscheck']
    assert d['new_v3_tests']==8 and d['posthoc_crosschecks']==1
    assert x['crosscheck_id']=='GCQ-X01'
    assert x['status']=='posthoc_empirical_crosscheck_not_frozen_test'
    assert 7.5e-6 < x['canonical_decay_only_reference_26Al_27Al'] < 7.7e-6
    assert 0.61 < x['measured_CAI1_fraction_of_decay_only_reference'] < 0.63
    assert x['CAI2_upper_bound_fraction_of_decay_only_reference'] < 0.16
    assert x['independent_reported_26Al_heterogeneity_factor_range']==[3.0,4.0]
    agg=json.loads((HERE/'resultats/CLAIMS_QUANTITATIFS_COMPLETS.json').read_text())
    assert len(agg['claims'])==8 and len(agg['posthoc_crosschecks'])==1
    assert agg['posthoc_crosschecks'][0]['claim_id']=='GCQ-X01'
    assert (HERE/'resultats/claims_quantitatifs_v3/GCQ-X01.json').is_file()


def test_v4_massive_input_selection_excludes_duplicates_unpublished_and_synthetic():
    sel=json.loads((HERE/'data_massives_reelles/IMPORT_SELECTION_V4.json').read_text())
    assert sel['pgd_sic_total_rows']==20432
    assert sel['pgd_sic_unpublished_excluded']==11567
    assert sel['pgd_sic_admissible_rows']==8865
    assert sel['pgd_graphite_admissible_rows']==2342
    assert sel['admissible_presolar_grains_total']==11207
    decisions={x['filename']:x['decision'] for x in sel['inputs']}
    assert decisions['PGD_SiC_2025-03-10.xlsx']=='excluded_duplicate'
    assert decisions['PGD_Gra_2025-03-24.xlsx']=='excluded_duplicate'
    assert decisions['pnas.2423345122.sd01.xlsx']=='excluded_current_scope'
    assert 'included_sheet' in decisions.values()


def test_v4_presolar_population_result_uses_published_grains_only():
    d=json.loads((HERE/'resultats/RESULTATS_QUANTITATIFS_DATA_RICH_V4.json').read_text())
    p=d['presolar_grains']
    assert d['schema']=='oric.gc.quantitative-data-rich-results.v4'
    assert d['tests_total']==5 and d['criteria_met']==5 and d['all_criteria_met']
    assert d['audit']['synthetic_rows_used']==0 and d['audit']['imputed_rows_used']==0 and d['audit']['simulation_rows_used']==0
    assert p['admissible_grains_total']==11207
    assert p['SiC_unpublished_rows_excluded']==11567
    assert p['X_to_M_median_26Al_27Al_factor']>250
    assert p['selected_SiC_type_isotope_medians']['M']['d(29Si/28Si)']['median']>0
    assert p['selected_SiC_type_isotope_medians']['X']['d(29Si/28Si)']['median']<0


def test_v4_NC_CC_multisystem_separation_has_no_imputation():
    d=json.loads((HERE/'resultats/RESULTATS_QUANTITATIFS_DATA_RICH_V4.json').read_text())['NC_CC']
    assert d['rows']==41 and d['isotope_systems']==11
    assert d['leave_one_out_correct']==41 and d['leave_one_out_total']==41
    assert d['missing_values_imputed']==0
    assert min(abs(v['CC_minus_NC_Cohen_d']) for v in d['effect_sizes'].values())>1.9


def test_v4_allende_heterogeneity_is_distribution_level():
    d=json.loads((HERE/'resultats/RESULTATS_QUANTITATIFS_DATA_RICH_V4.json').read_text())
    c=d['Allende_chondrules']; w=d['Allende_subsamples']
    assert c['Allende_chondrules']==34
    assert all(x['fraction_gt_3sigma']>0.70 for x in c['metrics'].values())
    assert w['Allende_subsamples_n']==12
    assert w['pairs_gt_2sigma']==55 and w['pair_count']==66
    assert w['max_pairwise']['z']>36
    assert w['literature_Table4_used'] is False


def test_v4_bennu_individual_measurements_show_resolved_component_contrast():
    b=json.loads((HERE/'resultats/RESULTATS_QUANTITATIFS_DATA_RICH_V4.json').read_text())['Bennu_returned_samples']
    assert b['Bennu_2025_individual_presolar_grains']==52
    assert b['Bennu_2026_O_isotope_spots']==18
    assert b['number_refractory_spots_all_gt_3sigma_from_diopside']==17
    assert b['diopside_vs_each_refractory_min_z']>9.9


def test_v4_claim_artifacts_and_authority_report_exist():
    d=json.loads((HERE/'resultats/CLAIMS_QUANTITATIFS_DATA_RICH_V4.json').read_text())
    assert d['schema']=='oric.gc.quantitative-claims.v4'
    assert {c['claim_id'] for c in d['claims']}=={f'GCQ-T{i}' for i in range(17,22)}
    assert all(c['criterion_met'] for c in d['claims'])
    for c in d['claims']:
        assert (HERE/'resultats/claims_quantitatifs_v4'/f"{c['claim_id']}.json").is_file()
    report=(HERE/'resultats/RAPPORT_QUANTITATIF_DATA_RICH_V4.md').read_text()
    assert '11207' not in report  # guard against hidden control characters
    assert '11207' in report and '41/41' in report and '55/66' in report
