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
    assert len(s)==38
    assert all(x['source_class'] in {'primary_peer_reviewed','official_observation_product'} for x in s)
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
    assert s['stages']==20 and s['links']==22 and s['primary_or_official_sources']==38
    assert s['empirical_measurement_records']==90
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
    assert d['underlying_empirical_measurement_records']==90
    assert d['primary_or_official_sources']==38
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
    assert v['sources']==38 and v['measurement_records']==90
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
    assert all(int(x['remaining_measurement_records'])<90 for x in a)
    r=rows(HERE/'resultats/REDONDANCE_PAR_STAGE.csv')
    singles={x['stage_id'] for x in r if x['single_source_bottleneck']=='True'}
    assert {'GC-E11','GC-E12','GC-E13','GC-E16','GC-E17','GC-E18','GC-E19'} <= singles
    assert 'GC-E02' not in singles and 'GC-E10' not in singles


def test_new_empirical_sources_are_firewalled():
    s={x['source_id']:x for x in rows(HERE/'SOURCES_EMPIRIQUES.csv')}
    m={x['record_id']:x for x in rows(HERE/'data/MESURES_EMPIRIQUES.csv')}
    assert {'S034','S035','S036','S037','S038'}<=set(s)
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
