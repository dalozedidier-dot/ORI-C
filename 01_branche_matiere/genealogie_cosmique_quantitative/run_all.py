#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json,sys
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
SRC=HERE/'src'
sys.path.insert(0,str(SRC))
from analyser_empirique import read_csv, validate_empirical_only, derive, evaluate_claims, ALLOWED_MODES

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
    files=sorted(p for p in out.rglob('*') if p.is_file() and p.name!='RESULTATS.sha256')
    rels=[]
    for p in files:
      rel=p.relative_to(out).as_posix(); rels.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {rel}")
    (out/'RESULTATS.sha256').write_text('\n'.join(rels)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
