#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; errors=[]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def pointer(obj,p):
 for part in p.strip('/').split('/') if p.strip('/') else []:
  part=part.replace('~1','/').replace('~0','~'); obj=obj[int(part)] if isinstance(obj,list) else obj[part]
 return obj
reg=json.loads((ROOT/'preuves/PREUVES.json').read_text())
ids=set()
for e in reg['entries']:
 if e['id'] in ids: errors.append(f"preuve dupliquée {e['id']}")
 ids.add(e['id']); p=ROOT/e['artefact']
 if not p.is_file(): errors.append(f"artefact absent {e['id']}: {e['artefact']}")
 elif e.get('empreinte_sortie') and sha(p)!=e['empreinte_sortie']: errors.append(f"empreinte preuve divergente {e['id']}")
# Les 5 certifications doivent être identiques en statut au registre certifié.
cert=json.loads((ROOT/'plateforme/campagne_maximale_reelle/RESULTATS_SCIENTIFIQUES_CERTIFIES.json').read_text())
for c in cert['resultats']:
 e=next((x for x in reg['entries'] if x['id']==c['criterion_id']),None)
 if not e or e['statut']!='certifie' or e['verdict']!=c['verdict'] or e['niveau_preuve']!=c['niveau_preuve']: errors.append(f"certification désynchronisée {c['criterion_id']}")
nums=json.loads((ROOT/'preuves/CHIFFRES.json').read_text())
for n in nums['valeurs']:
 p=ROOT/n['source']
 try:
  src=pointer(json.loads(p.read_text()),n['pointer'])
  if n.get('transform')=='len': src=len(src)
  elif n.get('transform')=='count_intervariable_unique':
   pairs=set()
   for row in src:
    if row.get('source')!=row.get('target'):
     pairs.add(tuple(sorted((row.get('source'),row.get('target')))) + (row.get('lag_kyr'),))
   src=len(pairs)
 except Exception as exc: errors.append(f"source chiffre illisible {n['id']}: {exc}"); continue
 if isinstance(src,(int,float)) and isinstance(n['value'],(int,float)):
  if not math.isclose(float(src),float(n['value']),rel_tol=0,abs_tol=float(n.get('tolerance',0))): errors.append(f"chiffre divergent {n['id']}: source={src} registre={n['value']}")
 elif src!=n['value']: errors.append(f"chiffre divergent {n['id']}")
 for t in n.get('targets',[]):
  if n['display'] not in (ROOT/t).read_text(encoding='utf-8'): errors.append(f"rendu public manquant {n['id']} -> {t}: {n['display']}")
text=(ROOT/'ETAT_DES_PREUVES.md').read_text(encoding='utf-8')
if 'Fichier généré. Ne pas modifier à la main.' not in text: errors.append('ETAT_DES_PREUVES.md non marqué généré')
print(json.dumps({'preuves':len(reg['entries']),'chiffres':len(nums['valeurs']),'errors':errors,'status':'ok' if not errors else 'error'},ensure_ascii=False,indent=2))
raise SystemExit(1 if errors else 0)
