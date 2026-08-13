from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE / 'data' / 'elife-70676-fig1-data2-v2.csv'
OUT = HERE / 'resultats'
SEED = 20260813
ALPHA = 1.0
N_PERM = 5000
N_BOOT = 5000


def ridge_fit_predict(Xtr, ytr, Xte, alpha=1.0):
    penalty = np.eye(Xtr.shape[1]) * alpha
    penalty[0, 0] = 0.0
    beta = np.linalg.solve(Xtr.T @ Xtr + penalty, Xtr.T @ ytr)
    return Xte @ beta


def main():
    raw = pd.read_csv(DATA).dropna(subset=['MIC'])[
        ['Drug_evolved', 'Drug_tested', 'Day', 'Ancestor', 'Population', 'Measurement', 'MIC']
    ].copy()
    raw = raw[raw.Drug_tested == raw.Drug_evolved].copy()
    agg = (raw.groupby(['Drug_evolved', 'Day', 'Ancestor', 'Population'], as_index=False)
              .agg(MIC_median=('MIC', 'median'), n_technical=('MIC', 'size')))
    if (agg.MIC_median <= 0).any():
        raise RuntimeError('median MIC must be positive')
    agg['log2_MIC'] = np.log2(agg.MIC_median)

    d3 = agg[agg.Day == 3].rename(columns={'log2_MIC': 'X', 'n_technical': 'ntech3'}).drop(columns=['Day', 'MIC_median'])
    d12 = agg[agg.Day == 12].rename(columns={'log2_MIC': 'Y', 'n_technical': 'ntech12'}).drop(columns=['Day', 'MIC_median'])
    d = d3.merge(d12, on=['Drug_evolved', 'Ancestor', 'Population'], validate='one_to_one')
    d = d.sort_values(['Drug_evolved', 'Ancestor', 'Population']).reset_index(drop=True)
    d.Population = d.Population.astype(int)
    if len(d) != 36 or set(d.Population) != {1, 2, 3}:
        raise RuntimeError('unexpected independent-unit structure')

    levels = ['B1', 'B2', 'B3', 'P1', 'P2', 'P3']

    def design(hist_labels=None, train_idx=None):
        x = d.X.to_numpy(float)
        if train_idx is None:
            train_idx = np.arange(len(d))
        mu = x[train_idx].mean()
        sd = x[train_idx].std(ddof=0) or 1.0
        cols = [np.ones(len(d)), (x - mu) / sd, (d.Drug_evolved.to_numpy() == 'Imipenem').astype(float)]
        if hist_labels is not None:
            h = np.asarray(hist_labels)
            cols.extend((h == lev).astype(float) for lev in levels)
        return np.column_stack(cols)

    def cv_pred(hist_labels=None):
        pred = np.empty(len(d), float)
        for held in (1, 2, 3):
            te = np.flatnonzero(d.Population.to_numpy() == held)
            tr = np.flatnonzero(d.Population.to_numpy() != held)
            M = design(hist_labels, tr)
            pred[te] = ridge_fit_predict(M[tr], d.Y.to_numpy()[tr], M[te], ALPHA)
        return pred

    y = d.Y.to_numpy(float)
    p_state = cv_pred(None)
    p_hist = cv_pred(d.Ancestor.to_numpy())
    rmse_state = float(np.sqrt(np.mean((y - p_state) ** 2)))
    rmse_hist = float(np.sqrt(np.mean((y - p_hist) ** 2)))
    gain = float(1 - rmse_hist / rmse_state)

    rng = np.random.default_rng(SEED)
    groups = [np.flatnonzero(d.Drug_evolved.to_numpy() == drug) for drug in sorted(d.Drug_evolved.unique())]
    boot = np.empty(N_BOOT)
    for b in range(N_BOOT):
        ix = np.concatenate([rng.choice(g, size=len(g), replace=True) for g in groups])
        rs = np.sqrt(np.mean((y[ix] - p_state[ix]) ** 2))
        rh = np.sqrt(np.mean((y[ix] - p_hist[ix]) ** 2))
        boot[b] = 1 - rh / rs
    ci = [float(np.quantile(boot, .025)), float(np.quantile(boot, .975))]

    perm = np.empty(N_PERM)
    base = d.Ancestor.to_numpy().copy()
    strata = [np.asarray(list(idx), dtype=int) for idx in d.groupby(['Drug_evolved', 'Population']).groups.values()]
    for b in range(N_PERM):
        labs = base.copy()
        for ix in strata:
            vals = labs[ix].copy()
            rng.shuffle(vals)
            labs[ix] = vals
        pp = cv_pred(labs)
        rh = np.sqrt(np.mean((y - pp) ** 2))
        perm[b] = 1 - rh / rmse_state
    pperm = float((1 + np.sum(perm >= gain)) / (N_PERM + 1))

    by_drug = {}
    for drug, g in d.assign(pred_state=p_state, pred_history=p_hist).groupby('Drug_evolved'):
        yy = g.Y.to_numpy(float)
        rs = float(np.sqrt(np.mean((yy - g.pred_state.to_numpy(float)) ** 2)))
        rh = float(np.sqrt(np.mean((yy - g.pred_history.to_numpy(float)) ** 2)))
        by_drug[drug] = {'n': int(len(g)), 'RMSE_state_only': rs, 'RMSE_state_plus_history': rh,
                         'relative_gain': float(1 - rh / rs), 'relative_gain_percent': float(100 * (1 - rh / rs))}

    success = bool(gain >= .05 and ci[0] > 0 and pperm <= .05)
    result = {
        'schema': 'oric.prediction-replication-result.v1',
        'prediction_id': 'PRED-VIVANT-HISTOIRE-001',
        'dataset': 'Santos-Lopez et al. 2021, eLife 10:e70676, Figure 1 source data 2',
        'opened_on': '2026-08-13',
        'analysis_spec': {
            'X': 'median log2 MIC at day 3 under the same antibiotic used for experimental evolution',
            'R_future': 'median log2 MIC at day 12 under that antibiotic',
            'H': 'six ancestral-history identities B1,B2,B3,P1,P2,P3',
            'independent_unit': 'evolved population (ancestor × antibiotic × population replicate)',
            'n_independent_units': 36,
            'technical_replicates': '3 MIC readings collapsed by median before log2 transform',
            'out_of_sample': '3 folds, each holding out population replicate index 1, 2 or 3 across all histories and both antibiotics',
            'models': 'ridge alpha=1 fixed; state=X+antibiotic; history=X+antibiotic+six-level ancestral history',
            'permutation': '5000 permutations of H within antibiotic × population-replicate strata',
            'bootstrap': '5000 stratified resamples of independent lines within antibiotic'
        },
        'metrics': {
            'RMSE_state_only': rmse_state, 'RMSE_state_plus_history': rmse_hist,
            'relative_RMSE_gain': gain, 'relative_RMSE_gain_percent': 100 * gain,
            'bootstrap_95pct_gain': ci, 'permutation_p_one_sided': pperm,
            'n_permutations': N_PERM, 'n_bootstrap': N_BOOT
        },
        'secondary_prespecified_guard_diagnostics': {'by_antibiotic': by_drug},
        'frozen_success_rule': {'gain_min': .05, 'bootstrap_gain_lower_gt': 0.0, 'permutation_p_max': .05},
        'success': success,
        'verdict': 'success' if success else 'failure_under_frozen_rule',
        'scope': 'external blind validation on public pre-existing data; not newly collected prospective data'
    }
    OUT.mkdir(exist_ok=True)
    (OUT / 'PRED-VIVANT-HISTOIRE-001_SANTOS_LOPEZ_2021_recomputed.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    d.assign(pred_state=p_state, pred_history=p_hist,
             sqerr_state=(y-p_state)**2, sqerr_history=(y-p_hist)**2).to_csv(OUT / 'predictions_hors_echantillon_recomputed.csv', index=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
