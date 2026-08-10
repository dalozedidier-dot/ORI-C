#!/usr/bin/env python3
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
r={'status':'not_evaluable_on_current_ORI-C_objects','source':'Sharma et al., Nature 622, 321-328 (2023), DOI 10.1038/s41586-023-06600-9',
 'implemented':['published ensemble assembly equation from assembly index and copy number','paired-rank comparator ORI-C depth vs assembly index'],
 'missing_for_direct_test':['assembly index measured/computed for the same ORI-C objects','copy number for those same objects','common elementary-building-block convention'],
 'non_equivalence_rule':'ORI-C documentary/organizational depth is not relabelled as assembly index. A formal empirical comparison requires paired observables on the same objects.',
 'scope':'external-framework bridge only; no evidence verdict changes.'}
(HERE/'DIAGNOSTIC.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,ensure_ascii=False,indent=2))
