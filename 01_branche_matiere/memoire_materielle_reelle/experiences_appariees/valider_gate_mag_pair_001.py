#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
DATA=['mag_pair_001_units.csv','mag_pair_001_measurements.csv','mag_pair_001_analysis_ready.csv','MAG-PAIR-001.result.json']

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 e=json.loads((HERE/'MAG-PAIR-001.execution.json').read_text(encoding='utf-8')); f=e['frozen_fields']; missing=[k for k,v in f.items() if v is None]
 present=[x for x in DATA if (HERE/x).exists()]
 if e['status']=='blocked_missing_lab_freeze':
  if not missing: raise SystemExit('gate says blocked but no frozen field is missing')
  if present: raise SystemExit('prospective MAG data/results present while gate is blocked: '+', '.join(present))
  print(f'MAG-PAIR-001 gate correctly closed: {len(missing)} lab fields missing, no prospective data present')
  return 0
 if e['status']=='frozen_ready_for_registration':
  if missing: raise SystemExit('freeze status open with missing fields')
  reg=e.get('registration',{})
  if not (reg.get('public_url') and reg.get('registered_at')):
   print('MAG-PAIR-001 scientific freeze complete; acquisition still blocked until public registration')
   return 0
  print('MAG-PAIR-001 administrative gate open; acquisition may proceed under frozen protocol')
  return 0
 raise SystemExit('unknown MAG gate status')
if __name__=='__main__': raise SystemExit(main())
