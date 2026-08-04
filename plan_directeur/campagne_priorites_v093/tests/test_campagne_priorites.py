from pathlib import Path
import json
HERE=Path(__file__).resolve().parents[1]
def test_synthese_priorites_complete():
    p=HERE/'resultats/synthese_priorites_v093.json'
    assert p.exists()
    s=json.loads(p.read_text())
    assert set(s['verdicts'])=={'matiere','transfert_climatique','hysteresis','antibiotique_externe','prebiotique'}
    assert all(x['returncode']==0 for x in s['executions'].values())
def test_statuts_ne_sont_pas_elargis():
    s=json.loads((HERE/'resultats/synthese_priorites_v093.json').read_text())
    assert s['verdicts']['antibiotique_externe']['status']=='retrospectif_externe_non_confirmatoire'
    assert s['verdicts']['prebiotique']['criterion_testable'] is False
