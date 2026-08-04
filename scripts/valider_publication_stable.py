#!/usr/bin/env python3
from __future__ import annotations
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
errors=[]
version=(ROOT/'VERSION').read_text().strip()
if version!='0.9.3-research': errors.append(f'VERSION inattendue: {version}')
for p in ['CITATION.cff','.zenodo.json','LICENSE','LICENSING.md','RELEASE_NOTES_v0.9.3-research.md','PUBLICATION_STABLE.md','.github/workflows/release.yml']:
    if not (ROOT/p).exists(): errors.append(f'manquant: {p}')
if '0.9.3-research' not in (ROOT/'CITATION.cff').read_text(): errors.append('CITATION.cff non synchronisé')
z=json.loads((ROOT/'.zenodo.json').read_text())
if z.get('version')!=version: errors.append('.zenodo.json non synchronisé')
for bad in ['MISE_A_JOUR_SITE.diff','LICENSE_PENDING.md','plateforme/requirements-lock.txt']:
    if (ROOT/bad).exists(): errors.append(f'fichier obsolète présent: {bad}')
# Runtime caches are excluded from manifests and archives.
# Claims required on public pages
proof=(ROOT/'site/preuves.html').read_text()
repro=(ROOT/'site/reproductibilite.html').read_text()
for needle in ['7,02 Ma','1 critère sur 10','tolérance','3 fenêtres sur 3','Trajectoires réelles']:
    if needle not in proof+repro: errors.append(f'page publique incomplète: {needle}')
print(json.dumps({'version':version,'errors':errors,'status':'ok' if not errors else 'error'},ensure_ascii=False,indent=2))
raise SystemExit(1 if errors else 0)
