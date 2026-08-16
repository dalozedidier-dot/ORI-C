#!/usr/bin/env python3
from pathlib import Path
import argparse, subprocess, sys
BAD = 'f5fc7447277abc25eee04662cdb536a626c449e2'
GOOD = '6993cfd6d0e76df9541834ffe7113a125bdac160'

def run(*cmd, check=True):
    print('+', ' '.join(map(str,cmd)), flush=True)
    return subprocess.run([str(x) for x in cmd], check=check)

def capture(*cmd):
    return subprocess.check_output([str(x) for x in cmd], text=True).strip()

def main():
    ap=argparse.ArgumentParser(description='Annule exactement le commit ORI-C qui a importé par erreur le paquet de livraison à la racine.')
    ap.add_argument('--push', action='store_true', help='pousse le commit de restauration sur origin/main après validation')
    args=ap.parse_args()
    root=Path(capture('git','rev-parse','--show-toplevel')).resolve()
    head=capture('git','rev-parse','HEAD')
    if capture('git','status','--porcelain'):
        raise SystemExit('Refus: arbre de travail non propre. Sauvegarder ou annuler les changements locaux avant réparation.')
    if head != BAD:
        if head == GOOD:
            print('Le dépôt est déjà revenu sur la base saine 6993cfd. Aucun revert nécessaire.')
            return 0
        raise SystemExit(f'Refus: HEAD={head}. Ce réparateur est volontairement limité au cas exact {BAD} pour éviter toute suppression imprévue.')
    run('git','revert','--no-edit',BAD)
    # Le revert doit produire exactement l'arbre du parent sain.
    tree_now=capture('git','rev-parse','HEAD^{tree}')
    tree_good=capture('git','rev-parse',GOOD+'^{tree}')
    if tree_now != tree_good:
        raise SystemExit(f'ERREUR: arbre après revert {tree_now} != arbre sain {tree_good}. Ne pas pousser.')
    if subprocess.run(['git','lfs','version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
        run('git','lfs','pull')
    verifier=root/'verifier_dossier.py'
    if not verifier.exists():
        raise SystemExit('verifier_dossier.py introuvable après restauration.')
    run(sys.executable, str(verifier))
    print("REPARATION LOCALE VALIDEE: le dépôt correspond exactement à l'arbre du commit sain 6993cfd et verifier_dossier.py passe.")
    if args.push:
        run('git','push','origin','HEAD:main')
        print('REPARATION POUSSEE SUR origin/main.')
    else:
        print('Pour publier la réparation: git push origin HEAD:main')
    return 0
if __name__=='__main__': raise SystemExit(main())
