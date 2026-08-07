#!/usr/bin/env python3
from __future__ import annotations
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
errors=[]
version=(ROOT/'VERSION').read_text(encoding='utf-8').strip()
if not re.fullmatch(r'\d+\.\d+\.\d+(?:-[A-Za-z0-9.]+)?', version):
    errors.append(f'VERSION invalide: {version}')
release_notes=f'RELEASE_NOTES_v{version}.md'
for p in ['CITATION.cff','.zenodo.json','LICENSE','LICENSING.md',release_notes,'PUBLICATION_STABLE.md','.github/workflows/release.yml']:
    if not (ROOT/p).exists(): errors.append(f'manquant: {p}')
if version not in (ROOT/'CITATION.cff').read_text(encoding='utf-8'): errors.append('CITATION.cff non synchronisé')
z=json.loads((ROOT/'.zenodo.json').read_text(encoding='utf-8'))
if z.get('version')!=version: errors.append('.zenodo.json non synchronisé')
workflow=(ROOT/'.github/workflows/release.yml').read_text(encoding='utf-8')
if 'RELEASE_NOTES_${GITHUB_REF_NAME}.md' not in workflow:
    errors.append('workflow release encore lié à une version fixe')
for bad in ['MISE_A_JOUR_SITE.diff','LICENSE_PENDING.md','plateforme/requirements-lock.txt']:
    if (ROOT/bad).exists(): errors.append(f'fichier obsolète présent: {bad}')
# Runtime caches are excluded from manifests and archives.
# Claims required on public pages
proof=(ROOT/'site/preuves.html').read_text(encoding='utf-8')
repro=(ROOT/'site/reproductibilite.html').read_text(encoding='utf-8')
for needle in ['7,02 Ma','1 critère sur 10','tolérance','3 fenêtres sur 3','Trajectoires réelles','31 nœuds','H011','MESA','11 760','0,00050','1,1309','0,8042','0,00498','626 blocages']:
    if needle not in proof+repro: errors.append(f'page publique incomplète: {needle}')
current_text = '\n'.join([
    (ROOT/'README.md').read_text(encoding='utf-8'),
    (ROOT/'ETAT_DES_PREUVES.md').read_text(encoding='utf-8'),
    proof,
])
for stale in [
    'Le vivant montre un petit signal exploratoire',
    'Lignées de vésicules | **En attente',
    'Histoire antibiotique 2026 | **En attente',
    "La grille reste une preuve de concept. Sur l'amikacine",
    '298 réussites techniques, 337 blocages',
    '<strong>298</strong><span>analyses exécutées</span>',
]:
    if stale in current_text: errors.append(f'formulation périmée présente: {stale}')
print(json.dumps({'version':version,'errors':errors,'status':'ok' if not errors else 'error'},ensure_ascii=False,indent=2))
raise SystemExit(1 if errors else 0)
