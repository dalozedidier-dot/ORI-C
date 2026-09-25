"""Exploratory sensitivity audit of the published ORI-C D'Onofrio benchmark.

Run: python approfondissement_donofrio.py --repo PATH_TO_ORIC --output DIR
Dependencies: numpy, pandas. Optional verification: scikit-learn.
Does not modify the repository, frozen protocols, or canonical verdicts.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import itertools
import json
import platform

import numpy as np
import pandas as pd

def grouped_splits(groups, n_splits=5):
    """Match sklearn 1.9 GroupKFold without importing its native dependencies."""
    unique, inverse = np.unique(np.asarray(groups), return_inverse=True)
    counts = np.bincount(inverse)
    order = np.argsort(counts, kind='stable')[::-1]
    weights = np.zeros(n_splits)
    assignment = np.zeros(len(unique), dtype=int)
    for index in order:
        fold = int(np.argmin(weights))
        weights[fold] += counts[index]
        assignment[index] = fold
    labels = assignment[inverse]
    return [(np.flatnonzero(labels != f), np.flatnonzero(labels == f)) for f in range(n_splits)]


def design(data, history=None, include_environment=True):
    features = ['Antibiotic'] + (['Limitation'] if include_environment else [])
    frame = data[features].copy()
    if history is not None:
        frame['History'] = history
    return pd.get_dummies(frame.astype(str), dtype=float).to_numpy()


def predict_ridge(x, y, splits):
    """Independent dense ridge implementation: alpha=1, unpenalized intercept."""
    pred = np.full(len(y), np.nan)
    for train, test in splits:
        a = x[train]
        mean = a.mean(axis=0)
        centered = a - mean
        ymean = y[train].mean()
        beta = np.linalg.solve(centered.T @ centered + np.eye(a.shape[1]),
                               centered.T @ (y[train] - ymean))
        pred[test] = (x[test] - mean) @ beta + ymean
    return pred


def rmse(y, prediction):
    return float(np.sqrt(np.mean((y - prediction) ** 2)))


def coverage(data, splits):
    return [sorted(set(data.Ancestor.iloc[test]) - set(data.Ancestor.iloc[train]))
            for train,test in splits]


def leave_strain_out(data):
    labels=data.Strain.to_numpy()
    return [(np.flatnonzero(labels!=g),np.flatnonzero(labels==g)) for g in np.unique(labels)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--permutations', type=int, default=9999)
    parser.add_argument('--verify-sklearn', action='store_true')
    args = parser.parse_args()
    root = args.repo.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    source = root / 'donnees_externes/histoire_antibiotique_donofrio_2026/extracted/Figure_3_N-lim_Expt_MIC_Raw_Data.csv'
    d = pd.read_csv(source)
    n_input = len(d)
    d = d.loc[d['MIC (ug/mL)'].gt(0) & d.notna().all(axis=1)].reset_index(drop=True)
    y = np.log2(d['MIC (ug/mL)'].to_numpy())
    groups = d.Strain.astype(str)
    splits = grouped_splits(groups)
    assert all(set(groups.iloc[a]).isdisjoint(groups.iloc[b]) for a,b in splits)
    units = d[['Strain','Limitation','Ancestor']].drop_duplicates().reset_index(drop=True)
    assert units.Strain.is_unique, 'History and environment must be constant within strain'
    h = d.Ancestor.to_numpy()
    state = predict_ridge(design(d), y, splits)
    history = predict_ridge(design(d,h), y, splits)
    observed = rmse(y,history)
    state_rmse = rmse(y,state)
    full_loso=leave_strain_out(d)
    full_loso_a=rmse(y,predict_ridge(design(d),y,full_loso))
    full_loso_b=rmse(y,predict_ridge(design(d,h),y,full_loso))
    published = json.loads((root/'03_branche_vivant/benchmark_histoire_antibiotique_2026/resultats/RESULTAT.json').read_text(encoding='utf-8'))
    # Canonical sparse Ridge uses an iterative solver. The direct dense solution
    # differs by about 1.1e-6 RMSE, below the tolerance declared for this audit.
    assert abs(observed-published['rmse_state_plus_history']) < 2e-6
    assert abs(state_rmse-published['rmse_state_only']) < 1e-8
    maxdiff = None
    direct_maxdiff = None
    if args.verify_sklearn:
        modulepath = root/'03_branche_vivant/benchmark_histoire_antibiotique_2026/analyser.py'
        spec = importlib.util.spec_from_file_location('canonical', modulepath)
        canonical = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(canonical)
        reference = canonical.predictions(d, pd.Series(y), groups, ['Limitation','Antibiotic','Ancestor'])
        maxdiff = float(np.max(np.abs(history-reference)))
        assert abs(rmse(y,reference)-observed)<2e-6
        from sklearn.linear_model import Ridge
        from sklearn.model_selection import GroupKFold
        canonical_splits=list(GroupKFold(n_splits=5).split(d,y,groups))
        assert all(np.array_equal(a,c) and np.array_equal(b,e) for (a,b),(c,e) in zip(splits,canonical_splits))
        direct=np.full(len(y),np.nan)
        full_design=design(d,h)
        for train,test in splits:
            direct[test]=Ridge(alpha=1.0,solver='svd').fit(full_design[train],y[train]).predict(full_design[test])
        direct_maxdiff=float(np.max(np.abs(direct-history)))
        assert direct_maxdiff<1e-10
    # Shuffle whole strains within final environment: retain all repeated outcomes
    # and the exact history counts in each environment. Same CV splits and model.
    rng = np.random.default_rng(20260925)
    indices = [part.index.to_numpy() for _,part in units.groupby('Limitation')]
    row_unit = units.set_index('Strain').index.get_indexer(d.Strain)
    original_labels = units.Ancestor.to_numpy()
    base_x = design(d)
    categories = np.sort(units.Ancestor.unique())
    null = []
    for i in range(args.permutations):
        shuffled = original_labels.copy()
        for ix in indices:
            shuffled[ix] = rng.permutation(original_labels[ix])
        row_labels = shuffled[row_unit]
        x = np.column_stack([base_x, row_labels[:,None] == categories])
        score = rmse(y,predict_ridge(x,y,splits))
        null.append(score)
        if i == 0:
            if args.verify_sklearn:
                control=d.assign(Ancestor=row_labels)
                testref=canonical.predictions(control,pd.Series(y),groups,['Limitation','Antibiotic','Ancestor'])
                assert abs(score-rmse(y,testref)) < 1e-4
            assert pd.DataFrame({'s':groups,'h':row_labels}).groupby('s').h.nunique().max()==1
        if (i+1)%2000==0:
            print(f'{i+1} group permutations completed',flush=True)
    null=np.array(null)
    pd.DataFrame({'null_rmse':null}).to_csv(args.output/'permutations_souches.csv',index=False,lineterminator='\n')
    # Descriptive sensitivity to excluding each observed history. These analyses
    # do not test generalization to unseen histories.
    exclusions=[]
    for ancestor in categories:
        sub=d.loc[d.Ancestor.ne(ancestor)].reset_index(drop=True)
        sy=np.log2(sub['MIC (ug/mL)'].to_numpy())
        sp=grouped_splits(sub.Strain.astype(str))
        a=rmse(sy,predict_ridge(design(sub),sy,sp))
        b=rmse(sy,predict_ridge(design(sub,sub.Ancestor),sy,sp))
        unseen=coverage(sub,sp)
        loso=leave_strain_out(sub)
        assert all(not v for v in coverage(sub,loso))
        la=rmse(sy,predict_ridge(design(sub),sy,loso))
        lb=rmse(sy,predict_ridge(design(sub,sub.Ancestor),sy,loso))
        exclusions.append({'excluded_history':ancestor,
                           'original_5fold':{'state_rmse':a,'history_rmse':b,'gain_percent':100*(a-b)/a,
                                            'unseen_histories_by_fold':unseen,
                                            'interpretation':'changes_estimand_to_unseen_histories' if any(unseen) else 'known_histories'},
                           'leave_one_strain_out':{'state_rmse':la,'history_rmse':lb,'gain_percent':100*(la-lb)/la}})
    # Does arbitrary strain-ID ordering drive the original five-fold result?
    # Keep the same model and vary only balanced, group-disjoint partitions.
    split_rng=np.random.default_rng(20260926)
    partition_gains=[]
    for _ in range(500):
        buckets=np.array_split(split_rng.permutation(units.Strain.to_numpy()),5)
        sp=[(np.flatnonzero(~d.Strain.isin(bucket)),np.flatnonzero(d.Strain.isin(bucket))) for bucket in buckets]
        a=rmse(y,predict_ridge(design(d),y,sp))
        b=rmse(y,predict_ridge(design(d,h),y,sp))
        partition_gains.append(100*(a-b)/a)
    pd.DataFrame({'gain_percent':partition_gains}).to_csv(args.output/'sensibilite_partitions.csv',index=False,lineterminator='\n')
    # Transfer between the two measured environments, preserving known histories.
    # Exact label permutations assess alignment of six history profiles across
    # environments, not independent prospective replication.
    transfers=[]
    for train_env in sorted(d.Limitation.unique()):
        train=np.flatnonzero(d.Limitation.eq(train_env))
        test=np.flatnonzero(d.Limitation.ne(train_env))
        sp=[(train,test)]
        a=rmse(y[test],predict_ridge(design(d,include_environment=False),y,sp)[test])
        b=rmse(y[test],predict_ridge(design(d,h,False),y,sp)[test])
        scores=[]
        for order in itertools.permutations(categories):
            mapping=dict(zip(categories,order))
            labels=h.copy()
            labels[test]=[mapping[v] for v in labels[test]]
            scores.append(rmse(y[test],predict_ridge(design(d,labels,False),y,sp)[test]))
        transfers.append({'train_environment':train_env,'test_environment':d.Limitation.iloc[test[0]],
                          'state_rmse':a,'history_rmse':b,'gain_percent':100*(a-b)/a,
                          'exact_permutations':len(scores),'p_history_alignment':float(np.mean(np.array(scores)<=b+1e-12))})
    pd.DataFrame({'strain':d.Strain,'environment':d.Limitation,'ancestor':h,'antibiotic':d.Antibiotic,
                  'observed_log2_mic':y,'state_prediction':state,'history_prediction':history}).to_csv(args.output/'predictions.csv',index=False,lineterminator='\n')
    result={
        'status':'exploratory_retrospective_sensitivity_no_XIV_credit',
        'source':source.relative_to(root).as_posix(),
        'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'seed':20260925,'rows':len(d),'excluded_rows':n_input-len(d),'strains':len(units),'histories':len(categories),
        'canonical_implementation_max_abs_prediction_difference':maxdiff,
        'sklearn_direct_svd_max_abs_prediction_difference':direct_maxdiff,
        'state_rmse':state_rmse,'history_rmse':observed,'gain_percent':100*(state_rmse-observed)/state_rmse,
        'full_leave_one_strain_out':{'state_rmse':full_loso_a,'history_rmse':full_loso_b,
                                    'gain_percent':100*(full_loso_a-full_loso_b)/full_loso_a},
        'canonical_fold_unseen_histories':coverage(d,splits),
        'strain_block_permutation':{'scheme':'within_final_environment_keep_all_12_measurements_per_strain',
            'permutations':len(null),'extreme_count':int(np.sum(null<=observed)),
            'p_plus_one':float((1+np.sum(null<=observed))/(1+len(null))),
            'null_rmse_mean':float(null.mean()),'null_rmse_quantiles':np.quantile(null,[.025,.5,.975]).tolist()},
        'exclude_one_history_sensitivity':exclusions,'cross_environment_transfer':transfers,
        'random_group_partition_sensitivity':{'partitions':len(partition_gains),'seed':20260926,
            'positive_gain_count':int(np.sum(np.array(partition_gains)>0)),
            'gain_percent_quantiles':np.quantile(partition_gains,[0,.025,.5,.975,1]).tolist(),
            'interpretation':'split_sensitivity_distribution_not_a_confidence_interval'},
        'limitations':['Post hoc sensitivity using already public data, not a new confirmatory protocol.',
            'Strain-block permutation assumes exchangeability of strains within environment under the null.',
            'Only six observed ancestral histories. Related descendants need not be independent experimental replicates.',
            'Limitation is the environment in which the strain evolved, not a measured complete current state. The baseline controls antibiotic and evolution environment only.',
            'Transfer only concerns the same known histories in two measured environments.',
            'No causal intervention on memory and no general ORI-C validation.'],
        'environment':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__},
        'verification':{'published_rmse_agreement_tolerance':2e-6,
                        'history_rmse_difference_from_published':observed-published['rmse_state_plus_history'],
                        'sklearn_predictions_verified':args.verify_sklearn}}
    (args.output/'resultat.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,indent=2,ensure_ascii=False))


if __name__=='__main__':
    main()
