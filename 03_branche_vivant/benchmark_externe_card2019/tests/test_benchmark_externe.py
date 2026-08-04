from pathlib import Path
import json, subprocess, sys
HERE=Path(__file__).resolve().parents[1]
def test_benchmark_externe_s_execute():
    r=subprocess.run([sys.executable,str(HERE/'analyser_benchmark.py')],capture_output=True,text=True)
    assert r.returncode==0,r.stdout+r.stderr
    v=json.loads((HERE/'resultats/verdict_externe.json').read_text())
    assert v['rows']==130
    assert v['train_rows']==90
    assert v['test_rows']==40
    assert v['status']=='retrospectif_externe_non_confirmatoire'
def test_separation_temporelle_stricte():
    v=json.loads((HERE/'resultats/verdict_externe.json').read_text())
    assert max(v['train_generations_k']) < min(v['test_generations_k'])
