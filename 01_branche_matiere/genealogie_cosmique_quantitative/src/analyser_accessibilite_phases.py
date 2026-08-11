from __future__ import annotations
import csv, json, re
from pathlib import Path

ELEMENTS=set('H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og'.split())
TOKEN=re.compile(r'[A-Z][a-z]?')

def _read(path: Path, delimiter=','):
    with path.open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f,delimiter=delimiter))

def _formula_elements(formula: str) -> set[str]:
    return {x for x in TOKEN.findall(formula or '') if x in ELEMENTS}

def analyse(root: Path, output_dir: Path):
    phases=_read(root/'plateforme/campagne_maximale_reelle/data/thermochemical_phases.csv')
    yields=_read(root/'plateforme/campagne_maximale_reelle/data/nucleosynthesis_yields.csv')
    baseline=_read(root/'01_branche_matiere/genealogie_cosmique_quantitative/data/BBN_BASELINE_ELEMENTAIRE.csv',';')
    bbn={r['element'] for r in baseline}
    stellar={r['element'] for r in yields}
    enriched=bbn|stellar
    unique={}
    for r in phases:
        unique.setdefault((r['phase'],r['composition']),_formula_elements(r['composition']))
    usable=[(k,e) for k,e in unique.items() if e]
    bbn_adm=[(k,e) for k,e in usable if e<=bbn]
    enriched_adm=[(k,e) for k,e in usable if e<=enriched]
    newly=[(k,e) for k,e in enriched_adm if not e<=bbn]
    examples=[]
    wanted={'corundum','forsterite','enstatite','spinel','fayalite','quartz,beta'}
    for (phase,comp),els in sorted(unique.items()):
        if phase in wanted:
            examples.append({'phase':phase,'composition':comp,'elements':sorted(els),'bbn_stoichiometrically_admissible':els<=bbn,'enriched_stoichiometrically_admissible':els<=enriched})
    out={
      'schema':'oric.gc.phase-accessibility.v1',
      'source_table':'plateforme/campagne_maximale_reelle/data/thermochemical_phases.csv',
      'source_rows':len(phases),
      'unique_phase_compositions':len(unique),
      'parsed_nonempty_phase_compositions':len(usable),
      'bbn_available_elements':sorted(bbn),
      'stellar_yield_elements':len(stellar),
      'enriched_available_elements':len(enriched),
      'bbn_stoichiometrically_admissible_phase_compositions':len(bbn_adm),
      'enriched_stoichiometrically_admissible_phase_compositions':len(enriched_adm),
      'newly_stoichiometrically_admissible_after_stellar_inventory':len(newly),
      'examples':examples,
      'status':'set_theoretic_constituent_filter_only',
      'interpretation':'Ce filtre teste uniquement une condition nécessaire de composition: une phase ne peut être construite si ses éléments ne sont pas disponibles. Il ne calcule ni équilibre de condensation, ni activité, ni cinétique, ni réalisation historique dans le disque protosolaire.',
    }
    (output_dir/'ACCESSIBILITE_PHASES.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return out
