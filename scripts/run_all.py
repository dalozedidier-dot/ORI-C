#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
HERE=Path(__file__).resolve().parent
for name in ['analyse_vesicules_histoire.py','analyse_aicc_chronologie.py','analyse_26al_sensibilite.py','analyse_accretion_multitraceur.py']:
    subprocess.run([sys.executable,str(HERE/name)],check=True)
