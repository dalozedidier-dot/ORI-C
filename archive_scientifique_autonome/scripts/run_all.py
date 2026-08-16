import subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
steps=['verify_inputs.py','analyse_aicc2023.py','analyse_endosymbiose.py','audit_accretion.py','analyse_gajrani_pacc.py','analyse_watkins_labels.py','analyse_vesicules.py']
for s in steps:
    print('+',s,flush=True)
    subprocess.run([sys.executable,str(HERE/s)],check=True,cwd=HERE)
print('Reproductions disponibles terminées. Watkins classifier exact et Yen-Papin sont conservés comme historiques, pas faussement rerun.')
