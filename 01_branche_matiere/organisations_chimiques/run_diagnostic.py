#!/usr/bin/env python3
from pathlib import Path
import json,pandas as pd
HERE=Path(__file__).resolve().parent; H=HERE.parent/'hypergraphe_transformations/hyperaretes.csv'
df=pd.read_csv(H,sep=';')
result={'schema':'oric.cot-bridge.v1','status':'not_evaluable_on_current_hypergraph','formalism':'Chemical Organization Theory: closed and mass-maintaining sets',
 'hyperedges_inspected':len(df),'closure_mapping_possible':True,'mass_maintenance_evaluable':False,
 'missing_required_data':['stoichiometric coefficients per reaction','reaction orientation with chemically conserved species','flux feasibility constraints'],
 'decision':'No current ORI-C node set is labelled a chemical organization from documentary reachability alone.',
 'scope':'fail-closed formal bridge; reusable COT module is tested on explicit stoichiometric toy networks, but no evidence verdict changes.'}
(HERE/'resultats/DIAGNOSTIC.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
