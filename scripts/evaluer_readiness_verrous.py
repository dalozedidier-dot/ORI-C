#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'plan_directeur' / 'READINESS_VERROUS.json'


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def main():
    hc = load('01_branche_matiere/hypergraphe_transformations/fermeture_stricte/HC02_CROUTE_HYDROSPHERE_INTERFACE.json')
    mag = load('01_branche_matiere/memoire_materielle_reelle/experiences_appariees/MAG-PAIR-001.execution.json')
    ves = load('03_branche_vivant/lignees_vesicules/VES-PACC-INT-01.execution.json')
    micplan = load('plan_directeur/campagne_centrale_2026_08_11/PREDICTIONS_PROSPECTIVES/REPLICATION_LTEE_NEW_MIC_PLAN.json')
    pmag = load('01_branche_matiere/memoire_materielle_reelle/experiences_appariees/PACC-MAG-INT-01.design.json')
    yen = load('03_branche_vivant/benchmark_yen_papin_2017/resultats/RESULTAT.json')
    gajrani = load('03_branche_vivant/memoire_externalisee_gajrani_2025/resultats/RESULTAT.json')
    matter = load('plan_directeur/campagne_centrale_2026_08_11/PREDICTIONS_PROSPECTIVES/PRED-MATIERE-WAVE-HISTORY-001.json')
    paleo = load('plan_directeur/PALEO_AGE_ENSEMBLE_ROUTE.json')

    missing_mag = [k for k, v in mag['frozen_fields'].items() if v is None]
    payload = {
        'schema': 'oric.active-lock-readiness.v1',
        'generated_from_versioned_state': True,
        'hc02': {
            'status': hc['status'],
            'baseline': '46/53',
            'extension': '53/53',
            'next': 'independent_semantic_review',
        },
        'mag_pair_001': {
            'status': mag['status'],
            'missing_lab_fields': missing_mag,
            'missing_count': len(missing_mag),
            'next': 'non_confirmatory_instrument_pilot',
        },
        'ves_pacc_int_01': {
            'status': ves['status'],
            'remaining_execution_blockers': ves['remaining_execution_blockers'],
            'next': 'confirm_single_lab_then_public_registration',
        },
        'vivant_new_mic': {
            'status': micplan['status'],
            'strict_route': micplan['routes']['A_strict_replication']['status'],
            'fast_route': micplan['routes']['B_fast_prospective_generalisation']['status'],
            'next': 'choose_strict_or_fast_route_before_outcome_access',
        },
        'yen_papin_2017': {
            'status': 'executed_real_data_negative_for_frozen_threshold',
            'history_gain_percent': yen['primary_result']['history_gain_percent'],
            'rich_X_history_gain_percent': yen['strict_state_sensitivity']['history_gain_percent'],
            'rich_X_permutation_p': yen['strict_state_sensitivity']['permutation_p'],
            'section_XIV_credit': False,
            'lesson': 'history signal must survive a sufficiently rich current-state X',
        },
        'gajrani_2025': {
            'status': 'executed_real_data_supports_externalized_trace_intervention_retrospectively',
            'mild_dilution_threshold_shift_percentage_points': gajrani['key_effects']['mild_dilution_1_2x']['history_memory_shift_percentage_points'],
            'supernatant_only_threshold_shift_percentage_points': gajrani['key_effects']['supernatant_rescue_1_2x']['median_threshold_gap_percentage_points'],
            'strict_pacc_qualified': gajrani['classification']['strict_PACC_INT_CHALLENGE_V1_qualified'],
            'section_XIV_credit': gajrani['classification']['counts_for_section_XIV_condition_9'],
            'lesson': 'physical environmental trace m can transmit H into future R',
        },
        'matter_wave_history_001': {
            'status': matter.get('route_status', matter['statut']),
            'dataset_doi': matter['source']['dataset_doi'],
            'raw_data_opened_by_ORI_C': matter['data_firewall']['raw_experimental_archive_opened_by_ORI_C'],
            'strict_new_data_prospective_credit': matter['data_firewall']['strict_new_data_prospective_credit'],
            'next': 'publish_frozen_mapping_before_opening_exp_zip',
        },
        'cross_branch_pacc': {
            'definition_id': pmag['definition_id'],
            'status': pmag['status'],
            'target': 'XIV-11 after both matter and living qualify',
        },
        'invariant_H_m_R': {
            'status': 'sharpened_by_one_negative_X_enrichment_control_and_one_positive_physical_trace_intervention',
            'authority': 'plan_directeur/MISE_A_JOUR_INVARIANT_HMR.json',
            'next': 'replicate the same two-filter logic in matter and then solar-system branch without weakening gates',
        },
        'section_XIV': 'unchanged_7_of_12_until_real_execution_or_replication',
        'paleo_age_ensemble_route': {
            'status': paleo['status'],
            'dataset_doi': paleo['source']['doi'],
            'age_model_ensembles': paleo['source']['age_ensemble_count'],
            'untuned_age_model_available': bool(paleo['source'].get('untuned_file')),
            'old_pred_paleo_history_02_unchanged': paleo['relationship_to_PRED_PALEO_HISTORY_02']['does_not_retroactively_change_frozen_protocol'],
            'next': 'freeze_new_prediction_ID_around_published_age_ensembles_before_value_analysis',
        },
    }
    OUT.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + '\n',
        encoding='utf-8',
        newline='\n',
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
