from __future__ import annotations
import csv, importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]

def load():
 p=HERE/'analyser_pilote_mag_pair_001.py'; spec=importlib.util.spec_from_file_location('magpilot',p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def test_pilot_selects_first_measured_af_level_passing_both_histories(tmp_path):
 m=load(); af=tmp_path/'af.csv'; tf=tmp_path/'tf.csv'
 with af.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=['specimen_id','history','af_mT','trace_before','trace_after','temperature_C']); w.writeheader()
  for level,after in [(10,0.4),(20,0.15)]:
   for h in [m.POS,m.NEG]: w.writerow({'specimen_id':h+str(level),'history':h,'af_mT':level,'trace_before':1,'trace_after':after,'temperature_C':22})
 with tf.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=['specimen_id','history','test_field_mT','trace_before_test','trace_after_test','response_projection','instrument_noise_sd','temperature_C']); w.writeheader(); w.writerow({'specimen_id':'x','history':m.POS,'test_field_mT':1,'trace_before_test':1,'trace_after_test':0.99,'response_projection':0.2,'instrument_noise_sd':0.01,'temperature_C':22})
 r=m.analyse(af,tf); assert r['recommended_af_plateau_mT_from_inherited_rule']==20; assert r['confirmatory_credit'] is False

def test_execution_freezes_non_lab_fields_only():
 import json
 d=json.loads((HERE/'MAG-PAIR-001.execution.json').read_text(encoding='utf-8')); f=d['frozen_fields']
 assert f['randomization_seed'] is not None and f['permutation_seed'] is not None and f['exclusion_rule']
 assert f['af_plateau_mT'] is None and f['test_field_mT'] is None and f['laboratory_id'] is None
