from __future__ import annotations
import csv, hashlib, json, subprocess, sys, tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parents[1]

def csvrows(p):
    with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter=';'))

def test_chain_depth_and_sources():
    nodes=csvrows(HERE/'CHAINE_GENEALOGIQUE.csv'); src=csvrows(HERE/'SOURCES_PRIMAIRES.csv'); claims=csvrows(HERE/'MATRICE_PREUVES.csv')
    assert len(nodes)==23
    assert len(src)>=34
    assert len(claims)>=12
    assert all(r['doi'] for r in src)
    assert len({r['doi'] for r in src})==len(src)
    assert nodes[0]['id']=='GC-001' and nodes[-1]['id']=='GC-023'

def test_existing_genealogy_is_unchanged():
    expected=(HERE/'BASELINE_GENEALOGIE_EXISTANTE.sha256').read_text().split()[0]
    got=hashlib.sha256((ROOT/'01_branche_matiere/genealogie/genealogie_matiere.csv').read_bytes()).hexdigest()
    assert got==expected

def test_nucleosynthesis_machine_result():
    d=json.loads((HERE/'resultats/NUCLEOSYNTHESE.json').read_text())
    assert d['model_family_count']==6
    assert d['elements_total']>=80
    assert d['elements_beyond_bbn_baseline']>=75
    assert d['all_key_rocky_elements_present'] is True

def test_handoff_stays_open_and_cast_unchanged():
    h=json.loads((HERE/'resultats/HANDOFF_SYSTEME_SOLAIRE.json').read_text())
    assert h['status']=='open'
    assert h['downstream_model']=='C-AST-01'
    assert h['downstream_passed_criteria']==13
    assert h['downstream_total_criteria']==15
    assert h['downstream_evidence_level']=='E4_modele'

def test_end_to_end_not_overclaimed():
    s=json.loads((HERE/'resultats/SYNTHESE.json').read_text())
    assert s['end_to_end_verdict']=='open_not_certified'
    assert s['handoff_status']=='open'


def test_research_depth_outputs():
    obs=csvrows(HERE/'data/OBSERVATIONS_CLEFS.csv')
    assert len(obs)>=23
    assert {'mesure échantillon','observation analogue externe','reconstruction isotopique','inférence de modèle','sortie de modèle'} <= {r['status'] for r in obs}
    claims=json.loads((HERE/'resultats/CLAIMS.json').read_text())
    assert claims['claim_count']>=12
    assert claims['verdict_counts']['open_not_certified']==1
    epi=json.loads((HERE/'resultats/COUVERTURE_EPISTEMIQUE.json').read_text())
    assert epi['stages_with_at_least_one_source']==23
    assert epi['stages_total']==23

def test_result_hashes():
    for line in (HERE/'resultats/RESULTATS.sha256').read_text().splitlines():
        digest,name=line.split('  ',1)
        path=HERE/'resultats'/name
        assert path.is_file(), name
        assert hashlib.sha256(path.read_bytes()).hexdigest()==digest

def test_byte_reproducible_outputs():
    with tempfile.TemporaryDirectory() as td:
        subprocess.run([sys.executable,str(HERE/'run_all.py'),'--output-dir',td],check=True,capture_output=True,text=True)
        for p in sorted(x for x in (HERE/'resultats').rglob('*') if x.is_file()):
            if p.name=='RESULTATS.sha256': continue
            rel=p.relative_to(HERE/'resultats')
            q=Path(td)/rel
            assert q.is_file(), rel.as_posix()
            assert p.read_bytes()==q.read_bytes(), rel.as_posix()


def test_constituent_accessibility_filter_is_narrowly_interpreted():
    d=json.loads((HERE/'resultats/ACCESSIBILITE_PHASES.json').read_text())
    assert d['status']=='set_theoretic_constituent_filter_only'
    assert d['enriched_stoichiometrically_admissible_phase_compositions'] > d['bbn_stoichiometrically_admissible_phase_compositions']
    assert d['newly_stoichiometrically_admissible_after_stellar_inventory'] > 0
    assert 'ne calcule ni équilibre de condensation' in d['interpretation']
