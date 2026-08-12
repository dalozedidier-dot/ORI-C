#!/usr/bin/env python3
from __future__ import annotations
import json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
errors=[]
version=(ROOT/'VERSION').read_text(encoding='utf-8').strip()
short_version=version.split('-',1)[0]
if not re.fullmatch(r'\d+\.\d+\.\d+(?:-[A-Za-z0-9.]+)?', version): errors.append(f'VERSION invalide: {version}')
release_notes=f'RELEASE_NOTES_v{version}.md'
for p in ['CITATION.cff','.zenodo.json','LICENSE','LICENSING.md',release_notes,'PUBLICATION_STABLE.md','.github/workflows/release.yml','preuves/PREUVES.json','preuves/CHIFFRES.json']:
    if not (ROOT/p).exists(): errors.append(f'manquant: {p}')
if version not in (ROOT/'CITATION.cff').read_text(encoding='utf-8'): errors.append('CITATION.cff non synchronisé')
z=json.loads((ROOT/'.zenodo.json').read_text(encoding='utf-8'))
if z.get('version')!=version: errors.append('.zenodo.json non synchronisé')
workflow=(ROOT/'.github/workflows/release.yml').read_text(encoding='utf-8')
if 'RELEASE_NOTES_${GITHUB_REF_NAME}.md' not in workflow: errors.append('workflow release encore lié à une version fixe')
for bad in ['MISE_A_JOUR_SITE.diff','LICENSE_PENDING.md','plateforme/requirements-lock.txt']:
    if (ROOT/bad).exists(): errors.append(f'fichier obsolète présent: {bad}')
# Les affirmations numériques sont désormais validées source -> registre -> rendu,
# jamais par une liste de nombres codés en dur dans ce script.
r=subprocess.run([sys.executable,str(ROOT/'scripts/valider_registre_preuves.py')],cwd=ROOT,capture_output=True,text=True)
if r.returncode:
    errors.append('registre preuves/chiffres invalide: '+(r.stdout+r.stderr).strip())
proof=(ROOT/'site/preuves.html').read_text(encoding='utf-8')
repro=(ROOT/'site/reproductibilite.html').read_text(encoding='utf-8')
# Présence de concepts/sections seulement ; les nombres associés sont contrôlés par CHIFFRES.json.
for needle in ['tolérance','Trajectoires réelles','H011','MESA','Généalogie cosmique quantitative','11 467','41 / 41',f'Publication stable {short_version}',f'Version stable : <code>{short_version}</code>']:
    if needle not in proof+repro: errors.append(f'page publique incomplète: {needle}')
current_text='\n'.join([(ROOT/'README.md').read_text(encoding='utf-8'),(ROOT/'ETAT_DES_PREUVES.md').read_text(encoding='utf-8'),proof])
for required in ['13 / 15','1 / 10',short_version]:
    if required not in current_text + repro:
        errors.append(f'frontière stable absente du rendu public: {required}')
if 'MPT-M2-01' not in (ROOT/'preuves/PREUVES.json').read_text(encoding='utf-8'):
    errors.append('M2 absent du registre PREUVES.json')
if 'PCMCI-CLIM-01' not in (ROOT/'preuves/PREUVES.json').read_text(encoding='utf-8'):
    errors.append('PCMCI+ exploratoire absent du registre PREUVES.json')
for stale in ['main prépare <code>0.9.6</code>','préparation de 0.9.6','Le vivant montre un petit signal exploratoire','Lignées de vésicules | **En attente','Histoire antibiotique 2026 | **En attente',"La grille reste une preuve de concept. Sur l'amikacine",'298 réussites techniques, 337 blocages','<strong>298</strong><span>analyses exécutées</span>']:
    if stale in current_text: errors.append(f'formulation périmée présente: {stale}')
print(json.dumps({'version':version,'errors':errors,'status':'ok' if not errors else 'error'},ensure_ascii=False,indent=2))
raise SystemExit(1 if errors else 0)
