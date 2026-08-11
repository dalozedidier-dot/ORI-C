from __future__ import annotations
import csv, json
from collections import Counter
from pathlib import Path

def analyse(root: Path, output_dir: Path):
    path=root/'01_branche_matiere/genealogie_cosmique_quantitative/data/OBSERVATIONS_CLEFS.csv'
    with path.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f,delimiter=';'))
    counts=Counter(r['status'] for r in rows)
    out={'schema':'oric.gc.observations.v1','record_count':len(rows),'status_counts':dict(sorted(counts.items())),
         'rule':'Les valeurs gardent le statut epistemique de leur source; une inférence de modèle ne devient pas une mesure directe.'}
    (output_dir/'OBSERVATIONS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return out
