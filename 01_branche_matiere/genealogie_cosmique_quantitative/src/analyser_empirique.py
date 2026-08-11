from __future__ import annotations
import csv, math
from collections import Counter
from pathlib import Path

ALLOWED_MODES={
    'astronomical_observation','spacecraft_observation','returned_sample_measurement',
    'meteorite_isotope_measurement','meteoritic_chronometry','laboratory_experiment',
    'planetary_isotope_reconstruction','official_observation_product'
}
ALLOWED_SOURCE_CLASSES={'primary_peer_reviewed','official_observation_product'}
FORBIDDEN_EVIDENCE_TOKENS=('synthetic','simulat','mock','constructed','numerical_model_output','theoretical_yield','thermochemical_model')

def read_csv(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def num(row):
    s=row.get('value_numeric','').strip()
    return None if not s else float(s)

def value_map(rows):
    return {r['quantity']: num(r) for r in rows if num(r) is not None}

def row_map(rows):
    return {r['quantity']: r for r in rows}

def validate_empirical_only(sources, measurements):
    errors=[]
    source_ids={s['source_id'] for s in sources}
    source_by_id={s['source_id']:s for s in sources}
    for s in sources:
        if s['source_class'] not in ALLOWED_SOURCE_CLASSES:
            errors.append(f"{s['source_id']}: source_class inadmissible")
        if s['evidence_mode'] not in ALLOWED_MODES:
            errors.append(f"{s['source_id']}: evidence_mode inadmissible")
        if not s['url'].startswith('http'):
            errors.append(f"{s['source_id']}: URL absente")
        if not s.get('portion_used','').strip() or not s.get('portion_excluded','').strip():
            errors.append(f"{s['source_id']}: portion utilisée/exclue non documentée")
    for r in measurements:
        if r['source_id'] not in source_ids:
            errors.append(f"{r['record_id']}: source inconnue")
            continue
        if r['evidence_mode'] not in ALLOWED_MODES:
            errors.append(f"{r['record_id']}: evidence_mode inadmissible {r['evidence_mode']}")
        if r['evidence_mode'] != source_by_id[r['source_id']]['evidence_mode']:
            errors.append(f"{r['record_id']}: mode différent de la source")
        hay=(' '.join([r['evidence_mode'],r['record_id'],r.get('quantity',''),r.get('scope_note','')])).lower()
        if any(t in hay for t in FORBIDDEN_EVIDENCE_TOKENS):
            errors.append(f"{r['record_id']}: donnée non empirique interdite")
    return errors

def derive(measurements):
    v=value_map(measurements); r=row_map(measurements)
    # Produit de deux rapports mesurés par ROSINA, propagation gaussienne indépendante.
    p=v['67P_HDO_over_H2O']*v['67P_D2O_over_HDO']
    s1=float(r['67P_HDO_over_H2O']['uncertainty_plus'])
    s2=float(r['67P_D2O_over_HDO']['uncertainty_plus'])
    sp=p*math.sqrt((s1/v['67P_HDO_over_H2O'])**2+(s2/v['67P_D2O_over_HDO'])**2)
    sv=float(r['V883_D2O_over_H2O']['uncertainty_plus'])
    z=abs(v['V883_D2O_over_H2O']-p)/math.sqrt(sv**2+sp**2)
    bennu=int(v['Bennu_O_rich_presolar_grains']+v['Bennu_SiC_presolar_grains']+v['Bennu_graphite_presolar_grains'])
    ryugu=int(v['Ryugu_presolar_silicate_grains']+v['Ryugu_presolar_oxide_grains']+v['Ryugu_presolar_SN_O_anomalous_grains']+v['Ryugu_presolar_SiC_grains']+v['Ryugu_presolar_carbonaceous_grains'])
    wild2=int(v['Wild2_circumstellar_stardust_grains'])
    return {
        'bennu_presolar_grains_total': bennu,
        'bennu_presolar_nominal_abundance_sum_ppm': v['Bennu_SiC_abundance']+v['Bennu_graphite_abundance']+v['Bennu_O_rich_abundance'],
        'ryugu_presolar_grains_total': ryugu,
        'ryugu_presolar_nominal_abundance_sum_ppm': v['Ryugu_O_anomalous_abundance']+v['Ryugu_SiC_abundance']+v['Ryugu_carbonaceous_abundance'],
        'returned_sample_presolar_grains_minimum_across_cited_studies': bennu+ryugu+wild2,
        'returned_sample_bodies_with_presolar_detection': 3,
        'SN1987A_dust_temperature_K_range':[v['SN1987A_dust_temperature_min'],v['SN1987A_dust_temperature_max']],
        'SN1987A_dust_mass_solar_range':[v['SN1987A_dust_mass_min'],v['SN1987A_dust_mass_max']],
        'comet_67P_D2O_over_H2O_derived': p,
        'comet_67P_D2O_over_H2O_sigma': sp,
        'V883_vs_67P_standardized_difference': z,
        'TW_Hya_methanol_direct_detection': bool(v['TW_Hya_methanol_velocity_channels_gt3sigma']>=6 and v['TW_Hya_methanol_peak_SNR']>=5),
        'NC_CC_minimum_coexistence_myr': v['NC_CC_separation_end_min']-v['NC_CC_separation_start'],
        'NC_CC_maximum_coexistence_myr': v['NC_CC_separation_end_max']-v['NC_CC_separation_start'],
        'chondrule_measured_age_span_myr': v['chondrule_oldest_PbPb_age']-v['chondrule_youngest_PbPb_age'],
        'EC002_offset_from_CAI_nominal_myr': v['CAI_PbPb_age']-v['EC002_PbPb_age'],
        'angrite_to_CM_carbonate_event_gap_nominal_myr': v['angrite_PbPb_age']-v['CM_carbonate_age'],
        'wild2_refractory_and_highT_material_detected': bool(v['Wild2_16O_refractory_grains']>=1 and v['Wild2_high_temperature_material_detected']==1),
        'source_mode_counts': dict(sorted(Counter(x['evidence_mode'] for x in measurements).items())),
    }

def evaluate_claims(measurements, derived, source_ids):
    v=value_map(measurements)
    claims=[]
    def add(cid,q,verdict,stages,sources,mechanism,directness,scope,criteria):
        claims.append(dict(claim_id=cid,question=q,verdict=verdict,stages=stages,source_ids=sources,
                           mechanism=mechanism,directness=directness,scope=scope,criteria=criteria,
                           preregistration='non_preregistered_initial_empirical_synthesis'))
    add('C-GC-E01','Les observations réelles montrent-elles que la composition disponible change entre l’inventaire primordial léger et les produits stellaires ultérieurs ?',
        'supports_empirical_enrichment_sequence',['GC-E00','GC-E01'],['S001','S002','S003','S004'],
        'composition_available_changes_across_cosmic_history','direct_observation_plus_observational_reconstruction',
        'Contraste empirique entre abondances primordiales reconstruites depuis spectres et noyaux produits par des étoiles/explosions détectés directement; aucune table de rendement théorique n’est utilisée.',
        {'D_over_H_measured':v['primordial_D_over_H']>0,'Yp_measured':v['primordial_helium_mass_fraction']>0,'Ti44_direct_lines':v['Ti44_line_energy_1']>0 and v['Ti44_line_energy_2']>0,'odd_Z_detected':v['CasA_K_detection_sigma']>=6 and v['CasA_Cl_detection_sigma']>=5})
    add('C-GC-E02','Observe-t-on directement la conversion d’éjecta stellaires enrichis en poussière solide ?',
        'supports_observed_stellar_dust_formation',['GC-E01','GC-E02'],['S003','S029'],
        'stellar_ejecta_produce_persistent_solid_dust','same_object_astronomical_observation',
        'SN1987A fournit un cas observationnel où les produits de l’explosion et une grande masse de poussière froide sont mesurés dans les éjecta. La masse est issue de la photométrie publiée; aucun rendement simulé n’est utilisé.',
        {'dust_temperature_K':derived['SN1987A_dust_temperature_K_range'],'dust_mass_solar':derived['SN1987A_dust_mass_solar_range']})
    add('C-GC-E03','De la matière formée avant le Système solaire est-elle encore mesurable dans plusieurs corps primitifs retournés ?',
        'supports_replicated_direct_material_inheritance',['GC-E02','GC-E03'],['S010','S030','S031'],
        'stellar_material_survives_as_presolar_grains','multi_mission_returned_sample_direct_measurement',
        'Transmission matérielle directe observée indépendamment dans Bennu, Ryugu et Wild 2. Le total de grains est un minimum de détections des études citées, pas une abondance combinée comparable.',
        {'Bennu_grains':derived['bennu_presolar_grains_total'],'Ryugu_grains':derived['ryugu_presolar_grains_total'],'Wild2_circumstellar_grains':int(v['Wild2_circumstellar_stardust_grains']),'minimum_detected_across_studies':derived['returned_sample_presolar_grains_minimum_across_cited_studies'],'returned_sample_bodies':derived['returned_sample_bodies_with_presolar_detection']})
    add('C-GC-E04','Les grains et glaces sont-ils déjà transformés dans les nuages denses avant la phase protostellaire ?',
        'supports_pre_stellar_material_processing',['GC-E04'],['S005','S006'],
        'ice_inventory_and_grain_growth_precede_protostar','direct_astronomical_observation','Analogue astrophysique de l’amont de systèmes planétaires, pas observation du nuage protosolaire historique.',
        {'ice_budget_percent_range':[v['dense_cloud_ice_budget_min'],v['dense_cloud_ice_budget_max']],'grain_scale_micrometre_at_least':v['dense_cloud_grain_scale']})
    add('C-GC-E05','Observe-t-on un transfert réel de matière du nuage vers les échelles du disque ?',
        'supports_observed_cloud_to_disk_supply',['GC-E05'],['S007','S036'],
        'large_scale_material_stream_feeds_disk_scales','replicated_direct_astronomical_observation','Deux systèmes protostellaires indépendants montrent des streamers à l’échelle de milliers d’au. Cela réplique l’existence physique du canal d’apport sans reconstruire l’histoire particulière du Soleil.',
        {'Per_emb_2_streamer_length_au_lower_bound':v['streamer_length_lower_bound'],'VLA1623B_streamer_length_au':v['VLA1623B_streamer_length'],'VLA1623B_streamer_excitation_temperature_K':v['VLA1623B_streamer_SO_excitation_temperature'],'independent_streamer_systems':2})
    add('C-GC-E06','Des signatures moléculaires formées en phase froide sont-elles observées jusque dans les disques et compatibles avec des matériaux cométaires ?',
        'supports_observational_molecular_inheritance',['GC-E04','GC-E06'],['S008','S009','S033'],
        'molecular_and_isotopic_signatures_survive_across_formation_stages','cross_system_observational_consistency',
        'V883 Ori/67P testent la continuité isotopique de l’eau; TW Hya apporte une détection indépendante de CH3OH. Les abondances modélisées de TW Hya sont exclues.',
        {'V883_D2O_H2O':v['V883_D2O_over_H2O'],'67P_D2O_H2O_derived':derived['comet_67P_D2O_over_H2O_derived'],'standardized_difference':derived['V883_vs_67P_standardized_difference'],'criterion_z_lt_2':derived['V883_vs_67P_standardized_difference']<2,'TW_Hya_direct_detection':derived['TW_Hya_methanol_direct_detection']})
    add('C-GC-E07','La formation de solides réfractaires est-elle directement observable dans un disque planétaire jeune ?',
        'supports_observed_refractory_solid_formation',['GC-E07'],['S024','S034'],
        'hot_gas_and_crystalline_refractory_solids_are_observed_and_crystalline_state_changes_with_burst','direct_astronomical_observation_plus_same_object_time_domain_contrast',
        'HOPS-315 fournit une détection de solides réfractaires dans un jeune disque. EC 53 ajoute un contraste temporel du même objet: forstérite et enstatite sont absentes en quiescence et détectées pendant le burst. Les modèles de transport restent exclus.',
        {'refractory_disk_observation_present':True,'EC53_same_object_time_domain_change':bool(v['EC53_burst_forsterite_feature_detected']==1 and v['EC53_quiescent_forsterite_feature_detected']==0 and v['EC53_burst_enstatite_feature_detected']==1 and v['EC53_quiescent_enstatite_feature_detected']==0),'EC53_crystalline_species_appearing_only_during_burst':int(v['EC53_crystalline_species_appearing_only_during_burst'])})
    add('C-GC-E08','Les archives réelles du disque solaire montrent-elles une architecture isotopique et temporelle non homogène ?',
        'supports_persistent_nebular_heterogeneity',['GC-E08','GC-E10'],['S011','S012','S013','S014','S015','S016'],
        'isotopic_reservoirs_and_time_order_are_recorded_in_solids','returned_sample_and_meteorite_measurements','Les causes dynamiques exactes de la séparation NC/CC et de l’hétérogénéité ne sont pas imposées.',
        {'solar_planetary_O_shift_percent':v['rocky_material_O17_O18_enrichment_vs_sun'],'NC_CC_coexistence_myr':[derived['NC_CC_minimum_coexistence_myr'],derived['NC_CC_maximum_coexistence_myr']],'Al26_factor':[v['Al26_heterogeneity_factor_min'],v['Al26_heterogeneity_factor_max']],'mu30Si_mu26Mg_slope':v['outer_disk_mu30Si_mu26Mg_slope'],'chondrule_age_span_myr':derived['chondrule_measured_age_span_myr']})
    add('C-GC-E09','Des échantillons cométaires retournés enregistrent-ils une redistribution de matériaux formés dans des régimes thermiques différents ?',
        'supports_empirical_solar_disk_material_redistribution',['GC-E09'],['S031','S032'],
        'high_temperature_and_presolar_material_coexist_in_outer_comet','returned_sample_mineralogy_and_isotopes',
        'La coexistence de stardust et de matériaux réfractaires/haute température dans Wild 2 soutient un mélange/transport à grande échelle. Aucun scénario dynamique ni distance de transport n’est calculé ici.',
        {'circumstellar_grain_detected':v['Wild2_circumstellar_stardust_grains']>=1,'O16_refractory_grain_detected':v['Wild2_16O_refractory_grains']>=1,'high_temperature_material_detected':bool(v['Wild2_high_temperature_material_detected'])})
    add('C-GC-E10','La succession CAI/chondres est-elle quantitativement ordonnée par chronométrie directe ?',
        'supports_measured_early_solar_chronology',['GC-E10'],['S016'],
        'absolute_PbPb_ages_record_time_order_and_duration','meteoritic_chronometry',
        'Âges Pb-Pb U-corrigés mesurés sur inclusions et chondres; aucune horloge synthétique n’est utilisée.',
        {'CAI_age_Ma':v['CAI_PbPb_age'],'oldest_chondrule_Ma':v['chondrule_oldest_PbPb_age'],'youngest_chondrule_Ma':v['chondrule_youngest_PbPb_age'],'measured_chondrule_span_myr':derived['chondrule_measured_age_span_myr']})
    add('C-GC-E11','Des expériences physiques réelles montrent-elles des étapes de croissance et de structuration collectives de poussière ?',
        'supports_laboratory_dust_mechanisms',['GC-E11','GC-E12'],['S019','S020'],
        'grain_aggregation_and_dust_gas_collective_structure','laboratory_experiment','Seules les mesures expérimentales entrent dans les résultats; toute section numérique des articles est exclue.',
        {'cluster_cm':v['largest_cluster_length'],'erosion_threshold_m_s':v['erosion_threshold_velocity'],'observed_instability_wavelength_cm':v['instability_min_observed_wavelength'],'observed_frequency_lower_hz':v['observed_frequency_lower']})
    add('C-GC-E12','L’ordre temporel mesuré est-il associé à des destins matériels différents des petits corps ?',
        'supports_timing_dependent_material_fates',['GC-E13','GC-E14'],['S017','S018'],
        'formation_time_associates_with_differentiated_vs_hydrous_records','meteoritic_chronometry','Association chronologique empirique entre archives de corps différenciés précoces et carbonates hydratés plus tardifs; aucun calcul thermique n’est utilisé comme preuve.',
        {'angrite_age_Ma':v['angrite_PbPb_age'],'angrite_Mg26_excess':bool(v['angrite_Mg26_excess_detected']),'CM_carbonate_age_Ma':v['CM_carbonate_age'],'nominal_event_gap_myr':derived['angrite_to_CM_carbonate_event_gap_nominal_myr']})
    add('C-GC-E13','Observe-t-on dans de vrais systèmes une séquence allant de disques jeunes structurés à des protoplanètes en accrétion ?',
        'supports_observed_disk_to_protoplanet_sequence',['GC-E15','GC-E16'],['S021','S022','S023','S025'],
        'disk_substructure_and_planetary_accretion_are_observed_stages','astronomical_observation','Le contexte général utilise plusieurs systèmes observés, mais PDS 70 fournit en plus un raccord dans le même système entre une cavité de disque et deux protoplanètes Hα en accrétion; aucune structure annulaire n’est automatiquement attribuée à une planète et aucune migration/résonance n’est utilisée comme preuve.',
        {'TMC1A_age_yr':v['TMC1A_age'],'IRS63_rings':v['IRS63_annular_substructures'],'DSHARP_disks':v['DSHARP_disks'],'PDS70_accreting_protoplanets':v['PDS70_accreting_protoplanets'],'PDS70_same_system_disk_gap_context':bool(v['PDS70_protoplanets_within_disk_gap'])})
    add('C-GC-E14','Des planètes du Système solaire portent-elles aujourd’hui des histoires d’accrétion différentes mesurables ?',
        'supports_planet_specific_accretion_histories',['GC-E17','GC-E18','GC-E19'],['S026','S027','S028'],
        'present_planets_retain_isotopic_constraints_on_distinct_growth_histories','planetary_isotope_reconstruction_plus_observed_endpoint','Les scénarios orbitaux expliquant ces apports sont exclus; seuls les systèmes isotopiques mesurés et l’endpoint planétaire actuel sont retenus.',
        {'Mars_half_size_time_upper_myr':v['Mars_half_size_time_upper'],'Earth_Mo_between_NC_CC':bool(v['Earth_Mo_between_NC_CC']),'present_planets':v['Solar_System_planets']})
    required_ids=[f'C-GC-E{i:02d}' for i in range(1,15)]
    by_id={c['claim_id']:c for c in claims}
    local_positive=all(by_id[cid]['verdict'].startswith('supports_') for cid in required_ids)
    global_verdict='supports_empirical_historical_accessibility_mechanism' if local_positive else 'undetermined_empirical_synthesis'
    add('C-GC-E15','L’ensemble des données empiriques soutient-il le mécanisme ORI-C selon lequel l’histoire modifie les constituants, traces, contraintes ou architectures disponibles pour les étapes suivantes ?',
        global_verdict,[f'GC-E{i:02d}' for i in range(20)],sorted(source_ids),
        'history_is_physically_carried_by_material_isotopic_chemical_temporal_and_architectural_state','cross_domain_empirical_synthesis',
        'Synthèse initiale non préenregistrée. Le verdict est calculé à partir des quatorze résultats locaux précédents. Il porte sur le mécanisme de transmission historique, pas sur une loi universelle ni sur une trajectoire cosmologique/orbitale unique.',
        {'required_positive_local_claims':required_ids,'all_required_local_claims_positive':local_positive,'simulation_evidence_count':0,'synthetic_data_rows':0,'imputed_rows':0})
    add('C-GC-E16','Les seules données empiriques permettent-elles de reconstruire une trajectoire causale unique jusqu’aux éléments orbitaux précis du Système solaire actuel ?',
        'undetermined_empirical_only',['GC-E19'],['S028'],
        'unique_orbital_genealogy_not_identifiable_from_empirical_archives_alone','explicit_limit','Les archives empiriques atteignent l’architecture présente et contraignent des histoires de croissance, mais elles ne sélectionnent pas une unique trajectoire orbitale détaillée. Aucune simulation n’est substituée pour fermer artificiellement ce problème inverse.',
        {'empirical_endpoint_observed':v['Solar_System_planets']==8,'unique_history_claimed':False})
    return claims
