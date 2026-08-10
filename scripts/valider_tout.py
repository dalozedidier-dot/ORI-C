#!/usr/bin/env python3
"""Contrôles rapides, portables et sans enchaînement de piles natives.

Les suites scientifiques sont exécutées dans des étapes CI séparées. Cette
séparation évite les blocages de sortie observés lorsque plusieurs bibliothèques
BLAS, Numba et REBOUND sont chargées successivement sous un même parent.
"""
from __future__ import annotations
import argparse,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(*cmd:str)->None:
    env=None
    # Python UTF-8 rend les sous-processus portables, y compris sous Windows.
    if cmd and Path(str(cmd[0])).name.lower().startswith('python'):
        import os
        env=os.environ.copy(); env['PYTHONUTF8']='1'
    r=subprocess.run(cmd,cwd=ROOT,start_new_session=True,env=env)
    if r.returncode: raise SystemExit(r.returncode)
def main(argv=None)->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--strict-lfs',action='store_true')
    a=p.parse_args(argv)
    verifier=[sys.executable,'verifier_dossier.py']
    if not a.strict_lfs: verifier.append('--allow-lfs-pointers')
    run(*verifier)
    run(sys.executable,'-m','compileall','-q','.')
    run(sys.executable,'methodologie_puissance/power_monte_carlo.py','validate-all','.')
    run(sys.executable,'scripts/construire_registre_preuves.py')
    run(sys.executable,'scripts/valider_registre_preuves.py')
    run(sys.executable,'scripts/valider_publication_stable.py')
    run(sys.executable,'scripts/valider_barriere_empirique.py')
    print('Contrôles rapides réussis, barrière empirique comprise. Les suites scientifiques sont séparées dans la CI.')
    return 0
if __name__=='__main__': raise SystemExit(main())
