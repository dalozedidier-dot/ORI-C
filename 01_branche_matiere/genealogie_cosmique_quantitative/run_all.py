#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE/'src'))
from analyser_nucleosynthese import analyse as analyse_nuc
from analyser_chaine import analyse as analyse_chain
from analyser_observations import analyse as analyse_obs
from analyser_accessibilite_phases import analyse as analyse_phase_acc

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output-dir',type=Path,default=HERE/'resultats'); args=ap.parse_args()
    out=args.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    nuc=analyse_nuc(ROOT,out); chain=analyse_chain(ROOT,out); obs=analyse_obs(ROOT,out); phase_acc=analyse_phase_acc(ROOT,out)
    # Existing downstream anchors: do not mutate verdicts.
    cert=json.loads((ROOT/'plateforme/campagne_maximale_reelle/RESULTATS_SCIENTIFIQUES_CERTIFIES.json').read_text(encoding='utf-8'))
    cast=next(r for r in cert['resultats'] if r['criterion_id']=='C-AST-01')
    h011=json.loads((ROOT/'01_branche_matiere/tests_causaux/resultats/H011_RESULTAT.json').read_text(encoding='utf-8'))
    handoff={
      'schema':'oric.gc.handoff-solar-system.v1','status':'open','reason':'Aucun pipeline de formation planétaire de cette branche ne produit encore avec incertitudes les conditions initiales J2000 utilisées par C-AST.',
      'formation_endpoint':'GC-023','downstream_model':'C-AST-01','downstream_verdict':cast['verdict'],'downstream_evidence_level':cast['niveau_preuve'],
      'downstream_passed_criteria':cast['mesures']['criteres_passes'],'downstream_total_criteria':cast['mesures']['criteres_total'],
      'required_future_closure':['modèle formation-disque→planètes','sortie masses+éléments orbitaux avec incertitudes','comparaison à plusieurs observables indépendantes','handoff explicite vers les variables C-AST'],
      'non_claim':'Le succès aval de C-AST ne constitue pas une reconstruction de la formation du Système solaire.'
    }
    (out/'HANDOFF_SYSTEME_SOLAIRE.json').write_text(json.dumps(handoff,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    summary={
      'schema':'oric.gc.summary.v1','branch':'genealogie_cosmique_quantitative','status':'ok' if chain['status']=='ok' else 'error',
      'stages':chain['stage_count'],'edges':chain['edge_count'],'sources':chain['source_count'],'claims':chain['claim_count'],
      'stellar_yield_families':nuc['model_family_count'],'stellar_yield_elements':nuc['elements_total'],'stellar_yield_isotopes':nuc['isotopes_total'],
      'elements_beyond_bbn_baseline':nuc['elements_beyond_bbn_baseline'],'all_key_rocky_elements_present':nuc['all_key_rocky_elements_present'],
      'curated_observation_records':obs['record_count'],
      'thermochemical_phase_compositions':phase_acc['unique_phase_compositions'],
      'bbn_stoichiometrically_admissible_phases':phase_acc['bbn_stoichiometrically_admissible_phase_compositions'],
      'enriched_stoichiometrically_admissible_phases':phase_acc['enriched_stoichiometrically_admissible_phase_compositions'],
      'newly_stoichiometrically_admissible_phases':phase_acc['newly_stoichiometrically_admissible_after_stellar_inventory'],'h011_threshold_ratio_high_low_turbulence':h011['threshold_ratio_high_low_turbulence'],
      'h011_status':h011['h011_status'],'c_ast_passed':cast['mesures']['criteres_passes'],'c_ast_total':cast['mesures']['criteres_total'],
      'c_ast_verdict':cast['verdict'],'handoff_status':handoff['status'],
      'end_to_end_verdict':'open_not_certified',
      'research_depth':'deep_branch_review_plus_machine_tests',
      'interpretation':'Plusieurs maillons indépendants soutiennent une transmission historique de matière, d’isotopes, de contraintes et d’architecture. La dérivation quantitative unique jusqu’aux conditions initiales du modèle orbital actuel reste ouverte.'
    }
    (out/'SYNTHESE.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    report=f"""# Rapport — Généalogie cosmique quantitative\n\n## Couverture\n\n- Stades : **{summary['stages']}**\n- Relations parent→descendant : **{summary['edges']}**\n- Sources : **{summary['sources']}**\n- Claims locales : **{summary['claims']}**\n- Enregistrements quantitatifs de littérature : **{summary['curated_observation_records']}**\n\n## Nucléosynthèse versionnée\n\n- Familles de modèles : **{summary['stellar_yield_families']}**\n- Éléments couverts : **{summary['stellar_yield_elements']}**\n- Isotopes couverts : **{summary['stellar_yield_isotopes']}**\n- Éléments du tableau au-delà du baseline BBN H/He/Li : **{summary['elements_beyond_bbn_baseline']}**\n- Éléments rocheux clefs tous présents : **{summary['all_key_rocky_elements_present']}**\n\nCe calcul mesure une **expansion de l’inventaire dans les rendements stellaires versionnés**. Il ne remplace pas une simulation d’évolution chimique galactique.\n\n## Maillons causalement informatifs déjà présents\n\n- Grains présolaires : transmission matérielle directe étroite depuis des sources stellaires jusqu’à des matériaux primitifs.\n- Glaces nuage→disque : observation forte dans un analogue externe, non transposée comme mesure directe du disque solaire.\n- Réservoirs isotopiques : archives météoritiques montrant une histoire de mélange/tri non totalement effacée.\n- 26Al + temps d’accrétion : mécanisme où l’histoire modifie le budget thermique et donc les futurs matériels.\n- Concentration/streaming : mécanisme modèle vers les planétésimaux; H011 conserve son statut `{summary['h011_status']}` et son rapport {summary['h011_threshold_ratio_high_low_turbulence']:.12g}.\n\n## Raccordement Système solaire\n\nC-AST reste **{summary['c_ast_passed']}/{summary['c_ast_total']}**, verdict `{summary['c_ast_verdict']}`. Le handoff formation→conditions initiales actuelles reste **OPEN**. Aucun résultat de cette branche ne requalifie C-AST ni ne transforme un scénario de formation en histoire unique certifiée.\n\n## Verdict de branche\n\n**{summary['end_to_end_verdict']}**\n\nLa branche établit une base quantitative et bibliographique profonde pour tester le mécanisme ORI-C de transmission historique. Elle ne revendique pas encore une fermeture causale de bout en bout.\n"""
    (out/'RAPPORT.md').write_text(report,encoding='utf-8',newline='\n')
    files=sorted(p for p in out.rglob('*') if p.is_file() and p.name!='RESULTATS.sha256')
    lines=[f'{sha(p)}  {p.relative_to(out).as_posix()}' for p in files]
    (out/'RESULTATS.sha256').write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
