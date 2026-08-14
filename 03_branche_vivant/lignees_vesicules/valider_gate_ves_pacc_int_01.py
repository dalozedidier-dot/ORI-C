#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
P=HERE/'PROTOCOLE_PACC_CAUSAL_PROSPECTIF_V1.json'; A=HERE/'analyser_ves_pacc_int_01.py'; R=HERE/'VES-PACC-INT-01.registration.json'; E=HERE/'VES-PACC-INT-01.execution.json'
PROSPECTIVE=['ves_pacc_int_01_raw','ves_pacc_int_01_analysis_ready.npz','ves_pacc_int_01_analysis_ready.metadata.json','VES-PACC-INT-01.result.json']
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 r=json.loads(R.read_text(encoding='utf-8')); e=json.loads(E.read_text(encoding='utf-8'))
 if r['source_sha256']!=sha(P) or r['analysis_script_sha256']!=sha(A): raise SystemExit('VES frozen SHA mismatch')
 present=[x for x in PROSPECTIVE if (HERE/x).exists()]
 open_=bool(r.get('status')=='publicly_registered' and r.get('public_url') and r.get('registered_at'))
 if not open_:
  if present: raise SystemExit('prospective VES data/results present while public registration gate is closed: '+', '.join(present))
  if e.get('status')!='blocked_until_public_registration_and_confirmed_lab': raise SystemExit('VES execution state inconsistent with closed registration gate')
  print('VES-PACC-INT-01 gate correctly closed: frozen science intact, no prospective data present')
  return 0
 print('VES public registration metadata present; verify confirmed lab/blind-key execution freeze before acquisition')
 return 0
if __name__=='__main__': raise SystemExit(main())
