#!/usr/bin/env python3
from pathlib import Path
import argparse, shutil, subprocess, sys
BAD='f5fc7447277abc25eee04662cdb536a626c449e2'
PREFIX=Path('plan_directeur/exploitation_donnees_existantes_2026_08_16')
HERE=Path(__file__).resolve().parent
PAYLOAD=HERE/'payload'
BLOCKED={'MANIFEST.sha256','MANIFEST.sha256.json','README.md','build_manifest.py','verifier_dossier.py','.gitattributes','.gitignore'}

def cap(*cmd): return subprocess.check_output([str(x) for x in cmd],text=True).strip()
def run(*cmd):
    print('+',' '.join(map(str,cmd)),flush=True)
    subprocess.run([str(x) for x in cmd],check=True)

def main():
    ap=argparse.ArgumentParser(description='Intègre uniquement le sous-arbre 7 axes dans ORI-C puis reconstruit le manifeste canonique avec les outils du dépôt.')
    ap.add_argument('repo',type=Path)
    args=ap.parse_args(); repo=args.repo.resolve()
    required=[repo/'build_manifest.py',repo/'verifier_dossier.py',repo/'MANIFEST.sha256']
    miss=[str(p) for p in required if not p.exists()]
    if miss: raise SystemExit('Refus: racine ORI-C invalide: '+', '.join(miss))
    # Refuser toute intégration tant que le commit accidentel est HEAD ou ancêtre.
    try:
        is_bad = subprocess.run(['git','-C',str(repo),'merge-base','--is-ancestor',BAD,'HEAD']).returncode == 0
    except Exception:
        is_bad=False
    if is_bad:
        raise SystemExit('Refus: le commit accidentel f5fc744 est encore dans la branche courante. Exécuter d’abord REPARER_DEPOT_APRES_IMPORT_ACCIDENTEL.py.')
    files=[p for p in PAYLOAD.rglob('*') if p.is_file()]
    if not files: raise SystemExit('Payload vide.')
    for srcp in files:
        rel=srcp.relative_to(PAYLOAD)
        if rel.parts[0:2] != ('plan_directeur','exploitation_donnees_existantes_2026_08_16'):
            raise SystemExit(f'Refus chemin hors liste blanche: {rel}')
        if rel.name in BLOCKED or rel.as_posix().startswith('../'):
            raise SystemExit(f'Refus fichier sensible: {rel}')
    for srcp in files:
        rel=srcp.relative_to(PAYLOAD); dst=repo/rel
        dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(srcp,dst)
    run(sys.executable,str(repo/'build_manifest.py'))
    run(sys.executable,str(repo/'verifier_dossier.py'))
    print(f'INTEGRATION VALIDEE: {len(files)} fichiers confinés sous {PREFIX.as_posix()}; manifeste canonique reconstruit par le dépôt.')
if __name__=='__main__': main()
