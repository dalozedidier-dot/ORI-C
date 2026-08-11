from __future__ import annotations
import csv, json, math
from pathlib import Path

def _rows(path):
    path=Path(path)
    with path.open(encoding='utf-8-sig',newline='') as f:
        sample=f.read(4096); f.seek(0)
        delimiter=';' if sample.splitlines()[0].count(';') > sample.splitlines()[0].count(',') else ','
        return list(csv.DictReader(f, delimiter=delimiter))

def analyse(root: Path, output_dir: Path):
    y=_rows(root/'plateforme/campagne_maximale_reelle/data/nucleosynthesis_yields.csv')
    iso=_rows(root/'plateforme/campagne_maximale_reelle/data/nucleosynthesis_isotope_yields.csv')
    baseline={r['element'] for r in _rows(root/'01_branche_matiere/genealogie_cosmique_quantitative/data/BBN_BASELINE_ELEMENTAIRE.csv')}
    elements=sorted({r['element'] for r in y})
    families=sorted({r['model_family'] for r in y})
    models=sorted({r['source_id'] for r in y})
    key=['C','O','Mg','Al','Si','Ca','Ti','Fe','Ni']
    coverage=[]
    for el in elements:
        rs=[r for r in y if r['element']==el]
        pos=[r for r in rs if float(r['yield_mass'])>0]
        fam_pos=sorted({r['model_family'] for r in pos})
        vals=[float(r['yield_mass']) for r in pos]
        coverage.append({
            'element':el,
            'in_bbn_baseline':el in baseline,
            'families_with_positive_yield':len(fam_pos),
            'families_total':len(families),
            'source_models_with_positive_yield':len({r['source_id'] for r in pos}),
            'positive_yield_min':min(vals) if vals else None,
            'positive_yield_max':max(vals) if vals else None,
            'log10_dynamic_range':(math.log10(max(vals)/min(vals)) if vals and min(vals)>0 and max(vals)>0 else None),
        })
    out={
        'schema':'oric.gc.nucleosynthesis.v1',
        'yield_rows':len(y),
        'isotope_yield_rows':len(iso),
        'model_families':families,
        'model_family_count':len(families),
        'source_model_count':len(models),
        'elements_total':len(elements),
        'isotopes_total':len({r['isotope'] for r in iso}),
        'bbn_baseline_elements':sorted(baseline),
        'bbn_baseline_element_count':len(baseline),
        'elements_beyond_bbn_baseline':len(set(elements)-baseline),
        'key_rocky_elements':key,
        'key_rocky_elements_present':sorted(set(key)&set(elements)),
        'all_key_rocky_elements_present':set(key)<=set(elements),
        'interpretation':'Les tables de rendements stellaires versionnées couvrent un inventaire élémentaire nettement plus large que le baseline élémentaire BBN. Ceci est un résultat de couverture de modèles, pas une reconstruction fermée de l’évolution chimique galactique.',
    }
    output_dir.mkdir(parents=True,exist_ok=True)
    (output_dir/'NUCLEOSYNTHESE.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    with (output_dir/'COUVERTURE_ELEMENTS.csv').open('w',encoding='utf-8',newline='') as f:
        fields=list(coverage[0]); wr=csv.DictWriter(f,fieldnames=fields,delimiter=';',lineterminator='\n'); wr.writeheader(); wr.writerows(coverage)
    return out
