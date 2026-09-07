#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'plan_directeur/VERROUS_ACTIFS.json'


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def sha(rel):
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def main() -> int:
    xiv = load('plan_directeur/campagne_centrale_2026_08_11/resultats/SEUIL_XIV.json')
    h = load('01_branche_matiere/hypergraphe_transformations/fermeture_stricte/AUDIT_H052_2026-08-14.json')
    vesreg = load('03_branche_vivant/lignees_vesicules/VES-PACC-INT-01.registration.json')
    mag = load('01_branche_matiere/memoire_materielle_reelle/experiences_appariees/MAG-PAIR-001.json')
    magexec = load('01_branche_matiere/memoire_materielle_reelle/experiences_appariees/MAG-PAIR-001.execution.json')
    vesexec = load('03_branche_vivant/lignees_vesicules/VES-PACC-INT-01.execution.json')
    veslabs = load('03_branche_vivant/lignees_vesicules/LAB_CANDIDATES_VES_PACC_INT_01.json')
    repplan = load('plan_directeur/campagne_centrale_2026_08_11/PREDICTIONS_PROSPECTIVES/REPLICATION_LTEE_NEW_MIC_PLAN.json')
    yen = load('03_branche_vivant/benchmark_yen_papin_2017/resultats/RESULTAT.json')
    matter = load('plan_directeur/campagne_centrale_2026_08_11/PREDICTIONS_PROSPECTIVES/PRED-MATIERE-WAVE-HISTORY-001.json')
    matter_result = load('01_branche_matiere/memoire_materielle_reelle/derive/RESULTAT_WATKINS_2026.json')
    paleo = load('02_branche_systeme_solaire/paleo_history_03_age_ensemble/PRED-PALEO-HISTORY-03-AGE-ENSEMBLE.json')

    yen_gain = yen['primary_result']['history_gain_percent']
    rich_gain = yen['strict_state_sensitivity']['history_gain_percent']

    data = {
        'schema': 'oric.active-bottlenecks.v1',
        'generated_from_authority': True,
        'section_XIV': {
            'passed_count': xiv['passed_count'],
            'conditions_total': xiv['conditions_total'],
            'missing_ids': xiv['missing_ids'],
        },
        'scientific_core': {
            'claim': 'same or sufficiently matched X with different H matters only when H survives rich-X control or is carried by manipulable m changing R/P_acc',
            'status': 'sharpened_not_yet_transversally_validated',
            'new_evidence_ids': ['YEN-PAPIN-HIST-01', 'GAJRANI-EXTMEM-01', 'HMR-SOLAR-OPEN-ARTIFACTS-01'],
        },
        'executed_routes': [
            {
                'id': matter['id'],
                'branch': 'matiere',
                'status': 'executed_negative_no_XIV_credit',
                'raw_data_opened_by_ORI_C': matter_result['opening']['opened_after_local_freeze'],
                'n_trials': matter_result['label_reconstruction']['n_trials'],
                'classifier_gain_percentage_points': matter_result['classifier']['gain_percentage_points'],
                'frozen_gain_threshold_percentage_points': matter_result['classifier']['success_threshold_gain_pp'],
                'bootstrap_95pct_gain': matter_result['classifier']['bootstrap95_gain_pp'],
                'section_XIV_credit': matter_result['section_XIV_credit'],
            },
        ],
        'fronts': [
            {
                'rank': 1,
                'id': paleo['id'],
                'branch': 'systeme_solaire',
                'status': paleo['status'],
                'source_doi': paleo['source']['doi'],
                'age_model_ensembles': paleo['source']['age_ensemble_count'],
                'purpose': 'replace fabricated LR04 age uncertainty with published chronology ensembles in a new frozen prediction ID',
                'targets': ['solar-system H-versus-X test', 'chronology uncertainty propagation'],
                'raw_values_opened_by_ORI_C': paleo['firewall']['raw_values_opened_by_ORI_C'],
                'section_XIV_credit': paleo['section_XIV_credit'],
            },
            {
                'rank': 2,
                'id': 'VES-PACC-INT-01',
                'branch': 'vivant',
                'scientific_design_complete': True,
                'public_registration_status': vesreg.get('status'),
                'public_url_present': bool(vesreg.get('public_url')),
                'execution_package_status': vesexec.get('status'),
                'candidate_lab_count': len(veslabs.get('candidates', [])),
                'execution_open': bool(
                    vesreg.get('status') == 'publicly_registered'
                    and vesreg.get('public_url')
                    and vesreg.get('registered_at')
                ),
                'protocol_sha256': sha('03_branche_vivant/lignees_vesicules/PROTOCOLE_PACC_CAUSAL_PROSPECTIF_V1.json'),
                'targets': ['XIV-9', 'XIV-3', 'XIV-4'],
            },
            {
                'rank': 3,
                'id': 'MAG-PAIR-001',
                'branch': 'matiere',
                'status': mag['status'],
                'minimum_independent_units': mag['minimum_independent_units'],
                'execution_freeze_status': magexec.get('status'),
                'remaining_lab_fields': sum(v is None for v in magexec.get('frozen_fields', {}).values()),
                'pilot_installed': True,
                'parallel_pacc_design': 'PACC-MAG-INT-01',
                'targets': ['XIV-9', 'XIV-11', 'PRED-MATIERE-ABLATION-001'],
            },
            {
                'rank': 4,
                'id': 'PRED-VIVANT-HISTOIRE-001',
                'branch': 'vivant',
                'status': 'frozen_prediction_not_supported_by_two_external_history_datasets_so_far',
                'latest_controls': {
                    'windels': 'negative',
                    'yen_papin': (
                        f'{yen_gain:.3f}_percent_gain_below_5_percent; '
                        f'rich_X_residual_{rich_gain:.3f}_percent_not_significant'
                    ),
                },
                'new_MIC_route_status': repplan.get('status'),
                'targets': ['XIV-3', 'XIV-4', 'XIV-10'],
            },
            {
                'rank': 5,
                'id': 'H052-HC01-HC02',
                'branch': 'matiere',
                'canonical_closure': f"{h['canonical_closure']['reachable_nodes']}/{h['canonical_closure']['total_nodes']}",
                'candidate_status': h['candidate_hc01_r1']['status'],
                'hc02_status': h.get('candidate_hc02_direct_interface', {}).get('status'),
                'hc02_preferred_next_audit': h.get('candidate_hc02_direct_interface', {}).get('preferred_over_hc01_for_next_audit', False),
                'verdict': h['verdict'],
                'extension_closure': '53/53' if h.get('hc02_extension', {}).get('status') == 'evidence_qualified_extension' else None,
                'targets': ['fermeture_hypergraphe_53_53'],
            },
        ],
    }
    OUT.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
        newline='\n',
    )
    print(f"verrous actifs: XIV {xiv['passed_count']}/{xiv['conditions_total']}, {len(data['fronts'])} fronts")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
