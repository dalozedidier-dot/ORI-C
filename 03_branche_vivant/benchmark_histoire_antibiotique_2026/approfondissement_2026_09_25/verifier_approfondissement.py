"""Independent numerical checks on the extension, using the real source table."""
from pathlib import Path
import sys
import json
import numpy as np
import pandas as pd
import approfondissement_donofrio as audit

root=Path(sys.argv[1])
out=Path(sys.argv[2])
d=pd.read_csv(root/'donnees_externes/histoire_antibiotique_donofrio_2026/extracted/Figure_3_N-lim_Expt_MIC_Raw_Data.csv')
y=np.log2(d['MIC (ug/mL)'].to_numpy())
splits=audit.grouped_splits(d.Strain.astype(str))
x=audit.design(d,d.Ancestor)
pred=audit.predict_ridge(x,y,splits)
independent=np.full(len(y),np.nan)
for train,test in splits:
    # Solve an augmented least-squares problem with an explicit, unpenalized
    # intercept, independently of centering and normal equations.
    train_x=np.column_stack([np.ones(len(train)),x[train]])
    penalty=np.diag([0.0]+[1.0]*x.shape[1])
    beta=np.linalg.lstsq(np.vstack([train_x,penalty]),np.r_[y[train],np.zeros(x.shape[1]+1)],rcond=None)[0]
    independent[test]=np.column_stack([np.ones(len(test)),x[test]])@beta
    assert set(d.Strain.iloc[train]).isdisjoint(d.Strain.iloc[test])
assert np.isfinite(pred).all()
maxdiff=float(np.max(np.abs(pred-independent)))
assert maxdiff<1e-10,maxdiff
state=audit.predict_ridge(audit.design(d),y,splits)
constant=audit.predict_ridge(audit.design(d,np.repeat('same',len(d))),y,splits)
assert np.max(np.abs(state-constant))<1e-10
result=json.loads((out/'resultat.json').read_text(encoding='utf-8'))
assert len(pd.read_csv(out/'permutations_souches.csv'))==9999
assert all(v['exact_permutations']==720 for v in result['cross_environment_transfer'])
assert result['rows']==288 and result['strains']==24 and result['histories']==6
assert all(len(v)==0 for v in result['canonical_fold_unseen_histories'])
record={'status':'passed','independent_augmented_lstsq_max_abs_difference':maxdiff,
        'checks':['group_disjoint_splits','finite_predictions','ridge_against_augmented_lstsq',
                  'constant_history_has_no_effect','complete_permutation_counts','source_dimensions','known_histories_in_baseline_folds']}
(out/'verification.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(record,indent=2))
