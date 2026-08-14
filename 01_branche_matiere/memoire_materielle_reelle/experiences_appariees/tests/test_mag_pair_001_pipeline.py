from __future__ import annotations
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]

def load(name):
 p=HERE/name; spec=importlib.util.spec_from_file_location(name.replace('.py',''),p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def test_gate_is_fail_closed_before_lab_freeze():
 m=load('valider_gate_mag_pair_001.py')
 assert m.main()==0

def test_interaction_statistic_has_expected_sign_and_magnitude():
 m=load('analyser_mag_pair_001.py')
 rows=[
  {'block_id':'b1','arm':'ablation','history':m.POS,'response_pre':'1','response_post':'0.1'},
  {'block_id':'b1','arm':'ablation','history':m.NEG,'response_pre':'-1','response_post':'-0.1'},
  {'block_id':'b1','arm':'sham','history':m.POS,'response_pre':'1','response_post':'0.95'},
  {'block_id':'b1','arm':'sham','history':m.NEG,'response_pre':'-1','response_post':'-0.95'},
 ]
 assert abs(m.interaction_stat(rows)+1.7)<1e-12
