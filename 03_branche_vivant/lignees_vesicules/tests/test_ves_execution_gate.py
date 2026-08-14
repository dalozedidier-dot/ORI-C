from __future__ import annotations
import importlib.util,json
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
def test_ves_execution_gate_is_fail_closed():
 p=HERE/'valider_gate_ves_pacc_int_01.py'; spec=importlib.util.spec_from_file_location('vgate',p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); assert m.main()==0
def test_ves_execution_package_does_not_change_scientific_protocol():
 e=json.loads((HERE/'VES-PACC-INT-01.execution.json').read_text(encoding='utf-8')); assert e['scientific_protocol_unchanged'] is True; assert e['remaining_execution_blockers']
