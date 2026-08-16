#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess, sys
HERE=Path(__file__).resolve().parent
EXPECTED=json.loads((HERE/'EXPECTED_INPUTS.json').read_text(encoding='utf-8'))

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(description='Applique le correctif 7 axes sur une copie extraite de la base ORI-C exacte.')
    ap.add_argument('repo',type=Path)
    args=ap.parse_args(); repo=args.repo.resolve()
    if not (repo/'MANIFEST.sha256').exists():
        raise SystemExit('Refus: MANIFEST.sha256 absent de la racine cible.')
    data=repo/'plateforme'/'campagne_maximale_reelle'/'data'
    errors=[]
    for f,h in EXPECTED['campaign'].items():
        p=data/f
        if not p.exists(): errors.append(f'absent: {p}')
        elif sha(p)!=h: errors.append(f'hash différent: {p}')
    if errors:
        raise SystemExit('Refus: la base cible ne correspond pas aux entrées scientifiques attendues:\n'+'\n'.join(errors))
    overlay=HERE/'integration_patch'
    for src in overlay.rglob('*'):
        if src.is_dir(): continue
        rel=src.relative_to(overlay); dst=repo/rel
        dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
    extdst=repo/'plan_directeur'/'exploitation_donnees_existantes_2026_08_16'/'donnees_externes'
    extdst.mkdir(parents=True,exist_ok=True)
    for f,h in EXPECTED['external'].items():
        src=HERE/'data'/'external'/f; dst=extdst/f
        if sha(src)!=h: raise SystemExit(f'Hash externe invalide avant copie: {f}')
        shutil.copy2(src,dst)
    verify=repo/'plan_directeur'/'exploitation_donnees_existantes_2026_08_16'/'scripts'/'verify_inputs.py'
    subprocess.run([sys.executable,str(verify)],cwd=verify.parent,check=True)
    print('Overlay appliqué et entrées vérifiées.')
    print('IMPORTANT: reconstruire ensuite MANIFEST.sha256 et MANIFEST.sha256.json avec les outils du dépôt, puis relancer les tests du dépôt. Ce script ne fabrique pas un manifeste racine sans la base complète.')
if __name__=='__main__': main()
