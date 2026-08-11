#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json,sys
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
SRC=HERE/'src'
sys.path.insert(0,str(SRC))
from analyser_empirique import read_csv, validate_empirical_only, derive, evaluate_claims, ALLOWED_MODES
from analyser_approfondissement_empirique import analyse as analyse_approfondissement
from analyser_quantitatif_reel import analyse as analyse_quantitatif_reel
from analyser_quantitatif_complet import analyse as analyse_quantitatif_complet

def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')

def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fieldnames,lineterminator='\n'); w.writeheader(); w.writerows(rows)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output-dir',type=Path,default=HERE/'resultats'); args=ap.parse_args()
    out=args.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True); (out/'claims').mkdir(exist_ok=True)
    sources=read_csv(HERE/'SOURCES_EMPIRIQUES.csv')
    stages=read_csv(HERE/'CHAINE_EMPIRIQUE.csv')
    links=read_csv(HERE/'LIENS_EMPIRIQUES.csv')
    measures=read_csv(HERE/'data/MESURES_EMPIRIQUES.csv')
    errors=validate_empirical_only(sources,measures)
    if errors: raise SystemExit('Refus empirique:\n- '+'\n- '.join(errors))
    source_ids={s['source_id'] for s in sources}
    d=derive(measures)
    claims=evaluate_claims(measures,d,source_ids)
    positive=[c for c in claims if c['verdict'].startswith('supports_')]
    unresolved=[c for c in claims if c['verdict'].startswith('undetermined_')]
    source_mode_counts=dict(sorted(Counter(s['evidence_mode'] for s in sources).items()))
    stage_record_counts=Counter(m['stage_id'] for m in measures)
    stage_source_counts={sid:len({m['source_id'] for m in measures if m['stage_id']==sid}) for sid in [s['stage_id'] for s in stages]}
    audit={
      'schema':'oric.gc.empirical-admissibility-audit.v1',
      'policy':'strict_empirical_only',
      'sources_total':len(sources),'measurement_records_total':len(measures),'stages_total':len(stages),'links_total':len(links),
      'sources_primary_peer_reviewed':sum(s['source_class']=='primary_peer_reviewed' for s in sources),
      'sources_official_observation_product':sum(s['source_class']=='official_observation_product' for s in sources),
      'measurement_mode_counts':dict(sorted(Counter(m['evidence_mode'] for m in measures).items())),
      'source_mode_counts':source_mode_counts,
      'all_modes_allowed':all(m['evidence_mode'] in ALLOWED_MODES for m in measures),
      'all_stages_have_measurements':all(stage_record_counts[s['stage_id']]>0 for s in stages),
      'all_stages_have_sources':all(stage_source_counts[s['stage_id']]>0 for s in stages),
      'stage_measurement_counts':dict(sorted(stage_record_counts.items())),
      'stage_source_counts':stage_source_counts,
      'simulations_used_as_evidence':0,
      'model_outputs_used_as_evidence':0,
      'theoretical_yields_used_as_evidence':0,
      'thermochemical_outputs_used_as_evidence':0,
      'orbital_integrations_used_as_genealogy_evidence':0,
      'synthetic_rows':0,
      'imputed_rows':0,
      'constructed_benchmark_rows':0,
      'sources_with_explicit_used_and_excluded_portions':sum(bool(s.get('portion_used','').strip()) and bool(s.get('portion_excluded','').strip()) for s in sources),
      'status':'pass'
    }
    dump(out/'AUDIT_ADMISSIBILITE.json',audit)
    empirical={
      'schema':'oric.gc.empirical-results.v3',
      'data_policy':'published_or_direct_empirical_measurements_only',
      'observed_records':len(measures),'source_count':len(sources),'stage_count':len(stages),'link_count':len(links),
      'simulations_used':0,'synthetic_rows':0,'imputed_rows':0,
      'derived_from_observations':d,'evidence_mode_counts':d['source_mode_counts'],
    }
    dump(out/'RESULTATS_EMPIRIQUES.json',empirical)
    claimdoc={'schema':'oric.gc.claims.v3','policy':'empirical_only_non_preregistered_initial_synthesis','claims':claims}
    dump(out/'CLAIMS.json',claimdoc)
    for c in claims: dump(out/'claims'/f"{c['claim_id']}.json",{'schema':'oric.gc.claim.v3',**c})
    source_by_stage={s['stage_id']:[] for s in stages}
    for src in sources:
      for sid in src['stage_ids'].split(';'):
        if sid in source_by_stage: source_by_stage[sid].append(src['source_id'])
    chain={'schema':'oric.gc.empirical-chain.v3','stages':[{**s,'source_ids':sorted(source_by_stage[s['stage_id']]),'measurement_count':stage_record_counts[s['stage_id']]} for s in stages], 'links':links}
    dump(out/'CHAINE_EMPIRIQUE.json',chain)
    summary={
      'schema':'oric.gc.empirical-summary.v3','stages':len(stages),'links':len(links),'primary_or_official_sources':len(sources),
      'empirical_measurement_records':len(measures),'claims':len(claims),'supported_claims':len(positive),'unresolved_claims':len(unresolved),
      'simulations_used':0,'synthetic_rows':0,'imputed_rows':0,
      'global_empirical_verdict':next(c['verdict'] for c in claims if c['claim_id']=='C-GC-E15'),
      'unique_orbital_history_status':'undetermined_empirical_only',
      'SN1987A_dust_mass_solar_range':d['SN1987A_dust_mass_solar_range'],
      'SN1987A_dust_temperature_K_range':d['SN1987A_dust_temperature_K_range'],
      'bennu_presolar_grains_total':d['bennu_presolar_grains_total'],
      'ryugu_presolar_grains_total':d['ryugu_presolar_grains_total'],
      'returned_sample_presolar_grains_minimum_across_cited_studies':d['returned_sample_presolar_grains_minimum_across_cited_studies'],
      'returned_sample_bodies_with_presolar_detection':d['returned_sample_bodies_with_presolar_detection'],
      'V883_vs_67P_standardized_difference':d['V883_vs_67P_standardized_difference'],
      'TW_Hya_methanol_direct_detection':d['TW_Hya_methanol_direct_detection'],
      'wild2_refractory_and_highT_material_detected':d['wild2_refractory_and_highT_material_detected'],
      'chondrule_measured_age_span_myr':d['chondrule_measured_age_span_myr'],
      'angrite_to_CM_carbonate_event_gap_nominal_myr':d['angrite_to_CM_carbonate_event_gap_nominal_myr'],
      'laboratory_erosion_threshold_m_s':next(float(x['value_numeric']) for x in measures if x['quantity']=='erosion_threshold_velocity'),
      'laboratory_instability_wavelength_cm':next(float(x['value_numeric']) for x in measures if x['quantity']=='instability_min_observed_wavelength'),
      'observed_accreting_protoplanets_PDS70':int(float(next(x['value_numeric'] for x in measures if x['quantity']=='PDS70_accreting_protoplanets'))),
      'present_solar_system_planets':int(float(next(x['value_numeric'] for x in measures if x['quantity']=='Solar_System_planets'))),
    }
    dump(out/'SYNTHESE.json',summary)
    handoff={
      'schema':'oric.gc.empirical-handoff.v3','status':'empirical_endpoint_reached_unique_orbital_history_unresolved',
      'endpoint':'current_solar_system_architecture','endpoint_source':'S028','observed_planet_count':summary['present_solar_system_planets'],
      'empirical_chain_status':'supported_at_mechanism_level',
      'what_is_established':'Des archives empiriques indépendantes relient enrichissement stellaire, poussières, grains présolaires, glaces et molécules, réservoirs isotopiques, chronométrie, croissance de petits corps, protoplanètes observées et histoires d’accrétion jusqu’à l’architecture présente.',
      'what_is_not_claimed':'Les données empiriques seules ne sélectionnent pas une trajectoire orbitale unique donnant les éléments orbitaux précis actuels.',
      'model_firewall':'Aucun résultat C-AST, aucune intégration N-corps et aucune simulation de formation planétaire ne sont comptés comme preuve de cette branche.',
      'C_AST_relation':'C-AST reste séparé. Il peut tester les conséquences d’une architecture donnée, pas servir de preuve empirique de sa genèse.'}
    dump(out/'HANDOFF_SYSTEME_SOLAIRE.json',handoff)
    result_rows=[]
    for c in claims:
      result_rows.append({'claim_id':c['claim_id'],'verdict':c['verdict'],'directness':c['directness'],'mechanism':c['mechanism'],'stages':';'.join(c['stages']),'source_ids':';'.join(c['source_ids']),'scope':c['scope']})
    write_csv(out/'RESULTATS_CLEFS.csv',['claim_id','verdict','directness','mechanism','stages','source_ids','scope'],result_rows)
    matrix=[]
    for c in claims:
      matrix.append({'claim_id':c['claim_id'],'question':c['question'],'verdict':c['verdict'],'directness':c['directness'],'source_count':len(c['source_ids']),'same_system_or_scope':c['scope'],'what_it_establishes':c['mechanism'],'what_it_does_not_establish':'Aucune trajectoire unique ni causalité plus forte que la directness déclarée.'})
    write_csv(out/'MATRICE_PREUVES_EMPIRIQUES.csv',['claim_id','question','verdict','directness','source_count','same_system_or_scope','what_it_establishes','what_it_does_not_establish'],matrix)
    lines=[
      '# Résultats — généalogie cosmique empirique complète', '',
      '**Règle absolue : aucune simulation, aucune donnée synthétique, aucune imputation et aucune sortie de modèle ne comptent comme preuve dans cette branche.**','',
      f"- {len(stages)} stades empiriques et {len(links)} liens qualifiés.",
      f"- {len(sources)} sources primaires/officielles et {len(measures)} enregistrements de mesures réelles.",
      f"- {len(positive)} résultats/claims soutenus; {len(unresolved)} question reste explicitement indéterminée.",
      '- Audit : 0 simulation, 0 ligne synthétique, 0 ligne imputée.', '',
      '## Résultats matériels directs', '',
      f"- SN1987A : poussière froide mesurée dans les éjecta, {d['SN1987A_dust_temperature_K_range'][0]:.0f}–{d['SN1987A_dust_temperature_K_range'][1]:.0f} K et {d['SN1987A_dust_mass_solar_range'][0]:.1f}–{d['SN1987A_dust_mass_solar_range'][1]:.1f} M☉.",
      f"- Échantillons retournés : Bennu {d['bennu_presolar_grains_total']} grains présolaires, Ryugu {d['ryugu_presolar_grains_total']}, Wild 2 au moins {int(next(float(x['value_numeric']) for x in measures if x['quantity']=='Wild2_circumstellar_stardust_grains'))}; minimum descriptif = {d['returned_sample_presolar_grains_minimum_across_cited_studies']} grains identifiés dans les études citées sur trois corps retournés.",
      f"- Wild 2 contient aussi un grain réfractaire enrichi en 16O et des matériaux haute température: trace empirique de redistribution/recyclage de matériaux dans le disque solaire.", '',
      '## Résultats moléculaires et isotopiques', '',
      f"- 67P : D2O/H2O dérivé de deux rapports ROSINA = {d['comet_67P_D2O_over_H2O_derived']:.3e} ± {d['comet_67P_D2O_over_H2O_sigma']:.3e}; V883 Ori = {next(float(x['value_numeric']) for x in measures if x['quantity']=='V883_D2O_over_H2O'):.2e}; écart standardisé = {d['V883_vs_67P_standardized_difference']:.3f}.",
      f"- TW Hya : CH3OH détecté directement sur {int(next(float(x['value_numeric']) for x in measures if x['quantity']=='TW_Hya_methanol_velocity_channels_gt3sigma'))} canaux >3σ, pic S/N = {next(float(x['value_numeric']) for x in measures if x['quantity']=='TW_Hya_methanol_peak_SNR'):.1f}.",
      f"- Réservoirs NC/CC : coexistence déduite des bornes publiées ~{d['NC_CC_minimum_coexistence_myr']:.0f}–{d['NC_CC_maximum_coexistence_myr']:.0f} Ma; hétérogénéité de 26Al rapportée par facteur 3–4.",
      f"- CAI/chondres : intervalle d’âges Pb-Pb mesuré des chondres = {d['chondrule_measured_age_span_myr']:.2f} Ma.", '',
      '## Résultats de croissance et d’architecture', '',
      f"- Microgravité : seuil d’érosion mesuré = {summary['laboratory_erosion_threshold_m_s']:.1f} m/s; longueur d’onde minimale observée de l’instabilité collective = {summary['laboratory_instability_wavelength_cm']:.1f} cm.",
      f"- PDS 70 : {summary['observed_accreting_protoplanets_PDS70']} protoplanètes en accrétion détectées en Hα.",
      '- Mars et Terre conservent des contraintes isotopiques différentes sur leurs histoires de croissance/accrétion.',
      f"- Endpoint : {summary['present_solar_system_planets']} planètes observées dans l’architecture actuelle.", '',
      '## Verdict ORI-C', '',
      '**Soutien empirique du mécanisme de transmission historique.** Des constituants, grains, molécules, isotopes, réservoirs, âges, structures et histoires d’accrétion mesurés conservent des conséquences de stades antérieurs et conditionnent le matériau/architecture disponible aux stades suivants.', '',
      'Ce verdict ne prouve pas une trajectoire cosmologique ou orbitale unique. Le problème inverse des éléments orbitaux précis actuels reste `undetermined_empirical_only`; il n’est pas fermé par une simulation puisque les simulations sont hors preuve dans cette branche.'
    ]
    (out/'RAPPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    deep=analyse_approfondissement(HERE)
    dump(out/'APPROFONDISSEMENT_EMPIRIQUE.json',deep['summary'])
    dump(out/'CLAIMS_QUANTITATIFS.json',{'schema':'oric.gc.quantitative-empirical-claims.v1','claims':deep['claims']})
    write_csv(out/'COUVERTURE_DAG_EMPIRIQUE.csv',['stage_id','anchor_stage_id','measurement_records_in_anchor','covered'],deep['coverage'])

    # Couche quantitative v2: résultats réels calculés directement sur les mesures empiriques.
    q2=analyse_quantitatif_reel(HERE)
    dump(out/'TESTS_QUANTITATIFS_REELS.json',{'schema':'oric.gc.quantitative-real-tests.v2','tests':q2['tests']})
    dump(out/'ROBUSTESSE_GRAPHE.json',q2['graph'])
    dump(out/'VERDICT_QUANTITATIF.json',q2['verdict'])
    write_csv(out/'REPLICATION_ECHANTILLONS.csv',list(q2['replication'][0].keys()),q2['replication'])
    write_csv(out/'CHRONOLOGIE_QUANTITATIVE.csv',list(q2['chronology'][0].keys()),q2['chronology'])
    write_csv(out/'REDONDANCE_PAR_STAGE.csv',list(q2['redundancy'][0].keys()),q2['redundancy'])
    write_csv(out/'ABLATIONS_FAMILLES_PREUVES.csv',list(q2['ablations'][0].keys()),q2['ablations'])
    qby={t['test_id']:t for t in q2['tests']}
    qlines=[
      '# Rapport quantitatif réel — généalogie cosmique', '',
      '**Autorité v2 : mesures empiriques uniquement. Aucun résultat de simulation, aucune donnée synthétique et aucune imputation.**','',
      f"- Sources primaires/officielles : {q2['verdict']['sources']}",
      f"- Enregistrements de mesures réelles : {q2['verdict']['measurement_records']}",
      f"- Tests quantitatifs/audits : {q2['verdict']['tests']} ({q2['verdict']['tests_passed']} exécutés conformément aux critères gelés pour les mises à jour futures).", '',
      '## Résultats quantitatifs', '',
      f"- Réplication grains présolaires : SiC Bennu/Ryugu z descriptif = {qby['GCQ-T01']['result']['pairs'][0]['standardized_descriptive_difference']:.3f}; O-rich z = {qby['GCQ-T01']['result']['pairs'][1]['standardized_descriptive_difference']:.3f}.",
      f"- Eau lourde V883 Ori / 67P : écart standardisé = {qby['GCQ-T02']['result']['standardized_difference']:.3f}.",
      f"- Chronologie : quatre écarts temporels sélectionnés sont résolus à >5σ avec propagation conservative des incertitudes publiées; un second chronomètre Al-Mg apporte en plus un cross-check indépendant d’environ {qby['GCQ-T03']['result']['independent_AlMg_crosscheck']['remelting_delay_myr_after_canonical_CAI']:.0f} Myr après les CAI canoniques.",
      f"- EC 53 : deux espèces cristallines (forstérite, enstatite) absentes en quiescence et détectées pendant le burst du même objet.",
      f"- Streamers : deux systèmes indépendants observés, longueurs ~{qby['GCQ-T05']['result']['streamer_lengths_au'][1]:.0f} au et >{qby['GCQ-T05']['result']['streamer_lengths_au'][0]:.0f} au.",
      f"- Ryugu : archive Lu-Hf d’une circulation de fluide >{qby['GCQ-T06']['result']['late_fluid_flow_lower_bound_myr_after_formation']:.0f} Myr après formation.", '',
      '## Robustesse et limites', '',
      f"- Graphe empirique : {q2['graph']['strict_archive_or_same_history_edges']} liens stricts d’archive/séquence sur {q2['graph']['total_edges']} liens; {q2['graph']['analogue_or_nonunique_edges']} liens restent analogues ou non uniques.",
      f"- Une séquence stricte d’archives relie les produits stellaires à un endpoint planétaire actuel : {str(q2['graph']['strict_path_stellar_products_to_present_endpoint']).lower()}.",
      f"- Fermeture stricte depuis la baseline primordiale jusqu’à l’endpoint actuel : {q2['graph']['end_to_end_strict_closure']}.",
      f"- Stades à source unique : {q2['verdict']['single_source_stage_bottlenecks']} ({', '.join(q2['verdict']['single_source_stage_ids'])}).",
      '- Les ablations par famille de preuve sont enregistrées dans `ABLATIONS_FAMILLES_PREUVES.csv`; elles auditent la dépendance de la chaîne aux familles de mesures et ne simulent aucun processus physique.', '',
      '## Verdict', '',
      f"`{q2['verdict']['global_quantitative_verdict']}`", '',
      'La branche dispose maintenant de résultats quantitatifs falsifiables/descriptifs sur les mesures elles-mêmes. La fermeture généalogique stricte de bout en bout reste ouverte là où les données ne permettent pas de remplacer honnêtement un analogue ou une relation non unique.'
    ]
    (out/'RAPPORT_QUANTITATIF.md').write_text('\n'.join(qlines)+'\n',encoding='utf-8')

    # Couche quantitative v3 complète: transformation historique quantifiée, sans simulation.
    q3=analyse_quantitatif_complet(HERE)
    dump(out/'RESULTATS_QUANTITATIFS_COMPLETS.json',q3['result'])
    dump(out/'TESTS_QUANTITATIFS_COMPLETS.json',{'schema':'oric.gc.quantitative-complete-tests.v3','tests':q3['tests']})

    # Claims v3 individuels : même discipline que les claims empiriques de la branche.
    # Chaque résultat quantitatif possède ainsi son artefact, ses sources et son statut
    # sans être promu à une certification historique du dépôt.
    q3_claim_meta={
      'GCQ-T09':('Le moment mesuré d’un événement change-t-il la fraction de 26Al encore physiquement disponible?', ['S016','S017','S014','S018','S039','S040'], ['GC-E10','GC-E13','GC-E08','GC-E14']),
      'GCQ-T10':('La différenciation précoce documentée se place-t-elle dans une fenêtre où davantage de 26Al subsiste?', ['S041','S039','S040','S016'], ['GC-E10','GC-E13']),
      'GCQ-T11':('La séparation isotopique NC/CC persiste-t-elle pendant une forte diminution de l’inventaire de 26Al?', ['S013','S039','S040'], ['GC-E08','GC-E10']),
      'GCQ-T12':('Des porteurs matériels présolaires persistent-ils jusqu’aux échantillons retournés actuels?', ['S010','S030','S031','S016'], ['GC-E03','GC-E09','GC-E19']),
      'GCQ-T13':('Ryugu enregistre-t-il une réactivation tardive physiquement séparée de l’horloge primordiale 26Al?', ['S035','S040'], ['GC-E14']),
      'GCQ-T14':('Les reconstructions empiriques de la provenance terrestre convergent-elles?', ['S027','S042','S043'], ['GC-E18']),
      'GCQ-T15':('Quel endpoint orbital actuel est directement décrit par le produit observationnel officiel retenu?', ['S028'], ['GC-E19']),
      'GCQ-T16':('Quels nœuds et relations documentés contrôlent la fermeture stricte de la chaîne empirique?', [], ['GC-E01','GC-E02','GC-E03','GC-E08','GC-E10','GC-E13','GC-E17','GC-E19']),
    }
    q3_claims=[]
    q3_claim_dir=out/'claims_quantitatifs_v3'; q3_claim_dir.mkdir(exist_ok=True)
    for t in q3['tests']:
      question,src_ids,stage_ids=q3_claim_meta[t['test_id']]
      c={
        'schema':'oric.gc.quantitative-claim.v3',
        'claim_id':t['test_id'],
        'question':question,
        'verdict':t['scientific_verdict'],
        'criterion_met':t['criterion_met'],
        'executed':t['executed'],
        'source_ids':src_ids,
        'stage_ids':stage_ids,
        'data_policy':'real_measurements_and_official_empirical_data_only',
        'preregistered':False,
        'status':'retrospective_empirical_quantitative_extension',
        'result':t['result'],
        'interpretation_limit':'Le verdict reste limité à la relation explicitement testée; aucune simulation ni donnée synthétique ne complète les raccords manquants.'
      }
      q3_claims.append(c); dump(q3_claim_dir/f"{t['test_id']}.json",c)
    x=q3['crosschecks'][0]
    xclaim={
      'schema':'oric.gc.quantitative-crosscheck.v3',
      'claim_id':'GCQ-X01',
      'question':'La décroissance canonique temporelle suffit-elle à représenter un inventaire 26Al local unique?',
      'verdict':x['result'],
      'criterion_met':None,
      'executed':True,
      'source_ids':['S014','S038','S039','S040'],
      'stage_ids':['GC-E08','GC-E10'],
      'data_policy':'real_measurements_and_official_empirical_data_only',
      'preregistered':False,
      'status':'posthoc_empirical_crosscheck_not_frozen_test',
      'result':x,
      'interpretation_limit':'Contrôle post-hoc déterministe. Le délai ~2 Myr ne reçoit aucune incertitude inventée et aucun test de significativité indépendant n’est revendiqué.'
    }
    dump(q3_claim_dir/'GCQ-X01.json',xclaim)
    dump(out/'CLAIMS_QUANTITATIFS_COMPLETS.json',{'schema':'oric.gc.quantitative-claims.v3','claims':q3_claims,'posthoc_crosschecks':[xclaim]})
    dump(out/'CROSSCHECK_HETEROGENEITE_26AL.json',x)

    write_csv(out/'INVENTAIRE_26AL_PAR_EVENEMENT.csv',list(q3['inventory'][0].keys()),q3['inventory'])
    write_csv(out/'FERMETURE_RELATIONS_EMPIRIQUES.csv',list(q3['closure'][0].keys()),q3['closure'])
    dump(out/'VERROUS_BOUT_EN_BOUT.json',{
      'schema':'oric.gc.end-to-end-locks.v3',
      'strict_path_stellar_products_to_present_endpoint':q3['result']['graph_closure']['strict_path_stellar_products_to_present_endpoint'],
      'strict_path_primordial_baseline_to_present_endpoint':q3['result']['graph_closure']['strict_path_primordial_baseline_to_present_endpoint'],
      'critical_nodes':q3['result']['graph_closure']['critical_nodes_for_stellar_to_endpoint_path'],
      'critical_edges':q3['result']['graph_closure']['critical_edges_for_stellar_to_endpoint_path'],
      'Earth_provenance_status':q3['result']['earth_provenance']['status'],
      'open_links':[x for x in q3['closure'] if x['closure_status']!='strict_documented_relation']
    })
    q3by={t['test_id']:t for t in q3['tests']}
    inv={x['event']:x for x in q3['result']['radiogenic_inventory']}
    rr=q3['result']['reservoir_persistence']; core=q3['result']['early_core_formation_window']; ep=q3['result']['endpoint_architecture']
    complete_lines=[
      '# Généalogie cosmique quantitative — résultats physiques complets v3','',
      '**Corpus: données réelles et produits empiriques officiels uniquement. 0 simulation, 0 donnée synthétique, 0 imputation, 0 échantillonnage aléatoire.**','',
      f"- Sources: {q3['result']['sources_total']}",
      f"- Enregistrements empiriques: {q3['result']['measurement_records_total']}",
      f"- Nouveaux tests physiques/fermeture v3: {q3['result']['new_v3_tests']} ({q3['result']['criteria_met']} critères d'exécution satisfaits).",'',
      '## 1. L’histoire change quantitativement un inventaire physique accessible','',
      f"- À l’archive angritique, t = {inv['angrite']['time_after_CAI_myr']:.2f} ± {inv['angrite']['time_sigma_myr']:.2f} Myr après le repère CAI, il reste {100*inv['angrite']['remaining_26Al_fraction_of_CAI_inventory']:.1f}% de l’inventaire initial de 26Al.",
      f"- À EC 002, t = {inv['EC002']['time_after_CAI_myr']:.2f} ± {inv['EC002']['time_sigma_myr']:.2f} Myr: {100*inv['EC002']['remaining_26Al_fraction_of_CAI_inventory']:.1f}% reste.",
      f"- Au chondre le plus jeune sélectionné, t = {inv['youngest_chondrule']['time_after_CAI_myr']:.2f} ± {inv['youngest_chondrule']['time_sigma_myr']:.2f} Myr: {100*inv['youngest_chondrule']['remaining_26Al_fraction_of_CAI_inventory']:.1f}% reste.",
      f"- À l’événement carbonate CM, t = {inv['CM_carbonate']['time_after_CAI_myr']:.2f} ± {inv['CM_carbonate']['time_sigma_myr']:.2f} Myr: {100*inv['CM_carbonate']['remaining_26Al_fraction_of_CAI_inventory']:.1f}% reste.",'',
      'Ces nombres ne sont pas un modèle thermique: ils quantifient seulement la quantité relative de radionucléide parent encore disponible à partir d’un rapport initial mesuré, d’âges mesurés et d’une demi-vie nucléaire évaluée.','',
      '## 2. Différenciation précoce et fenêtre radiogénique','',
      f"- Les météorites de fer IIAB/IIIAB/IVA placent la formation des noyaux vers {core['published_core_formation_window_myr_after_CAI'][0]:.1f}–{core['published_core_formation_window_myr_after_CAI'][1]:.1f} Myr après CAI. À cet intervalle, le calcul déterministe donne {100*core['remaining_26Al_fraction_range'][0]:.1f}–{100*core['remaining_26Al_fraction_range'][1]:.1f}% de l’inventaire initial encore présent.",
      f"- Cette fenêtre contient environ {core['core_window_vs_youngest_chondrule_inventory_factor_range'][0]:.1f}–{core['core_window_vs_youngest_chondrule_inventory_factor_range'][1]:.1f} fois plus de 26Al que l’époque du chondre le plus jeune du test.",'',
      '## 3. Une architecture isotopique persiste pendant que l’inventaire énergétique s’effondre','',
      f"- La séparation NC/CC publiée persiste au minimum {rr['minimum_persistence_myr']:.0f}–{rr['maximum_persistence_myr']:.0f} Myr, soit {rr['persistence_half_lives_range'][0]:.2f}–{rr['persistence_half_lives_range'][1]:.2f} demi-vies de 26Al.",
      f"- Entre le début et la fin de cette fenêtre, l’inventaire relatif de 26Al diminue d’un facteur {rr['inventory_decline_factor_start_to_end_range'][0]:.1f}–{rr['inventory_decline_factor_start_to_end_range'][1]:.1f}.",'',
      '### Contrôle post-hoc — le temps ne fixe pas seul l’inventaire local','',
      f"- À ~{x['approximate_delay_myr_after_CAI']:.0f} Myr, la référence canonique de décroissance seule vaut {x['canonical_decay_only_reference_26Al_27Al']:.3e}.",
      f"- Le premier CAI à matériel chondritique mesure {x['measured_chondrule_bearing_CAI1_26Al_27Al']:.2e}, soit {100*x['measured_CAI1_fraction_of_decay_only_reference']:.1f}% de cette référence.",
      f"- Le second est <{x['measured_chondrule_bearing_CAI2_26Al_27Al_upper_bound']:.2e}, soit <{100*x['CAI2_upper_bound_fraction_of_decay_only_reference']:.1f}% de la référence.",
      f"- Une autre archive du corpus rapporte indépendamment une hétérogénéité 26Al d’un facteur {x['independent_reported_26Al_heterogeneity_factor_range'][0]:.0f}–{x['independent_reported_26Al_heterogeneity_factor_range'][1]:.0f}.",
      '- Ce contrôle est explicitement post-hoc et ne compte pas parmi les huit tests gelés. Il montre que la décroissance temporelle est une référence nécessaire mais pas un inventaire local unique : l’histoire de réservoir/mélange intervient aussi.','',
      '## 4. Mémoire matérielle sur plusieurs échelles de temps','',
      f"- Les grains présolaires mesurés dans Bennu, Ryugu et Wild 2 imposent une borne conservatrice de persistance matérielle >{q3['result']['presolar_memory']['conservative_persistence_lower_bound_gyr']:.3f} Gyr.",
      f"- Ryugu enregistre une réactivation fluide >{q3['result']['late_reactivation']['late_fluid_flow_lower_bound_myr_after_formation']:.0f} Myr après formation, soit >{q3['result']['late_reactivation']['elapsed_26Al_half_lives_lower_bound']:.0f} demi-vies de 26Al; la cause tardive reste non identifiée ici.",'',
      '## 5. Terre: le résultat correct est un conflit empirique, pas une histoire forcée','',
      '- Budde et al. 2019 soutiennent une composante CC tardive à partir du Mo; Bermingham et al. 2025 concluent au contraire que les 10–20 derniers % massiques sont dominés par du matériel NC, avec une petite contribution CC encore possible dans les 0,5–1 derniers %.',
      '- Les valeurs Mo BSE rapportées en 2026 sont conservées, mais la conclusion multivariée de cette étude n’est pas utilisée comme preuve car son pipeline publié emploie des priors synthétiques et du Monte-Carlo.',
      f"- Verdict ORI-C sur la provenance terrestre: `{q3['result']['earth_provenance']['status']}`.",'',
      '## 6. Endpoint mesuré et verrou de reconstruction','',
      f"- Les 8 corps de l’endpoint JPL couvrent un facteur {ep['semimajor_axis_span_factor']:.2f} en demi-grand axe (Mercure → Neptune) dans la table utilisée.",
      f"- Chaîne stricte produits stellaires → endpoint actuel: {str(q3['result']['graph_closure']['strict_path_stellar_products_to_present_endpoint']).lower()}.",
      f"- Chaîne stricte baseline primordiale → endpoint actuel: {str(q3['result']['graph_closure']['strict_path_primordial_baseline_to_present_endpoint']).lower()}.",
      f"- Nœuds critiques de la chaîne stricte: {', '.join(q3['result']['graph_closure']['critical_nodes_for_stellar_to_endpoint_path'])}.",'',
      '## Verdict global','',
      f"`{q3['result']['global_result']['verdict']}`",'',
      'Le résultat central est désormais quantitatif: le moment d’incorporation transforme directement la fraction d’un inventaire radiogénique mesuré qui reste physiquement disponible. Des architectures isotopiques et des porteurs matériels persistent pendant ces changements, mais plusieurs raccords de bout en bout et la provenance terrestre restent explicitement ouverts ou contestés.'
    ]
    (out/'RAPPORT_QUANTITATIF_COMPLET.md').write_text('\n'.join(complete_lines)+'\n',encoding='utf-8')

    files=sorted(p for p in out.rglob('*') if p.is_file() and p.name!='RESULTATS.sha256')
    rels=[]
    for p in files:
      rel=p.relative_to(out).as_posix(); rels.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {rel}")
    (out/'RESULTATS.sha256').write_text('\n'.join(rels)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
