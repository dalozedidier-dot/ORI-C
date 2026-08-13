from __future__ import annotations
import json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTOCOL = HERE / 'PROTOCOLE_PACC_CAUSAL_PROSPECTIF_V1.json'
INPUT = HERE / 'ves_pacc_int_01_analysis_ready.npz'
META = HERE / 'ves_pacc_int_01_analysis_ready.metadata.json'
OUT = HERE / 'resultats' / 'RESULTAT_VES_PACC_INT_01.json'

# On the ORI-C repository this module already exists. The fallback below makes
# the failure explicit if the script is run outside the repository tree.
try:
    from methodologie_puissance.pacc_causal import estimate_matched_intervention_pacc
except ImportError as exc:
    raise SystemExit('Run this script from the ORI-C repository root with methodologie_puissance available') from exc


def main():
    p = json.loads(PROTOCOL.read_text(encoding='utf-8'))
    if p['preregistration_gate']['current_gate_open'] is not True:
        raise SystemExit('Execution gate closed: attach the public preregistration identifier before collecting/analyzing test data.')
    z = np.load(INPUT)
    meta = json.loads(META.read_text(encoding='utf-8'))
    for key in ('control_response', 'intervention_response', 'sham_response'):
        if z[key].ndim != 3 or z[key].shape[1:] != (12, 4):
            raise ValueError(f'{key} must be n×12×4')
    n = int(z['control_response'].shape[0])
    if not (z['intervention_response'].shape[0] == n == z['sham_response'].shape[0]):
        raise ValueError('arm sizes must match')

    matching = {name: bool(meta['matching'][name]) for name in p['matching_required']}
    estimate = estimate_matched_intervention_pacc(
        X_anchor=np.ones((n, 4), dtype=float),
        control_response=z['control_response'],
        intervention_response=z['intervention_response'],
        sham_response=z['sham_response'],
        materiality_thresholds=np.asarray(p['P_acc']['materiality_thresholds'], dtype=float),
        matching=matching,
        weights=None,
        sham_tolerance=float(p['P_acc']['sham_tolerance_max_abs_Delta_P_acc']),
        bootstrap_repeats=int(p['P_acc']['bootstrap_draws']),
        seed=int(p['P_acc']['bootstrap_seed']),
    )

    fidelity = meta['fidelity']
    n_ok = n >= int(p['independent_unit']['minimum_analyzable_n_for_primary_decision'])
    strict = bool(
        estimate['causal_qualified']
        and n_ok
        and fidelity['do_m_population_target_passes']
        and fidelity['sham_structural_fidelity_passes']
    )
    delta = float(estimate['Delta_P_acc_mean'])
    upper = float(estimate['Delta_P_acc_bootstrap_q975'])
    sesoi = float(p['SESOI_and_power']['SESOI_abs_Delta_P_acc'])
    inv_a = bool(strict and delta <= -sesoi and upper < 0.0)

    result = {
        'schema': 'oric.ves-pacc-int-result.v1',
        'protocol_id': p['id'],
        'definition_id': p['strict_definition_id'],
        'n_analyzable_independent_units': n,
        'strict_causal_qualified': strict,
        'section_XIV_condition_9_local_branch_measurement': strict,
        'direct_INV_A_support': inv_a,
        'fidelity': fidelity,
        'estimate': estimate,
        'decision_rule_applied_without_redefinition': True,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
