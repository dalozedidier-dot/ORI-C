#!/usr/bin/env python3
"""Recalcule les formalismes externes versionnés puis compare leurs sorties.

Le script travaille dans l'arbre courant parce que plusieurs adaptateurs historiques
écrivent encore vers un chemin de sortie fixe. Chaque sortie de référence est copiée
avant le recalcul et restaurée dans un bloc ``finally``. La comparaison est numérique
et tolérancée : elle ne dépend donc pas d'une identité binaire des derniers bits entre
versions compatibles de Python/NumPy.

PCMCI+ n'est pas inclus ici : son résultat n'est pas versionné tant que Tigramite
n'est pas disponible dans l'environnement scientifique principal. Il possède un job CI
séparé qui publie son artefact exploratoire.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CASES = [
    (
        "pid_antibiotique",
        [sys.executable, "03_branche_vivant/benchmark_histoire_antibiotique_2026/analyser_pid.py"],
        ["03_branche_vivant/benchmark_histoire_antibiotique_2026/resultats/PID_X_M_A.json"],
    ),
    (
        "etats_causaux_finis",
        [sys.executable, "methodologie_informationnelle/run_causal_states.py"],
        ["methodologie_informationnelle/RESULTATS_ETATS_CAUSAUX.json"],
    ),
    (
        "topologie_persistante",
        [sys.executable, "01_branche_matiere/hypergraphe_transformations/topologie_persistante.py"],
        [
            "01_branche_matiere/hypergraphe_transformations/resultats_topologie/RESULTAT.json",
            "01_branche_matiere/hypergraphe_transformations/resultats_topologie/intervalles_persistance.json",
        ],
    ),
    (
        "organisations_chimiques",
        [sys.executable, "01_branche_matiere/organisations_chimiques/run_diagnostic.py"],
        ["01_branche_matiere/organisations_chimiques/resultats/DIAGNOSTIC.json"],
    ),
    (
        "puissance_conjointe_matiere",
        [sys.executable, "methodologie_puissance/puissance_conjointe_matiere.py", "--reps", "250"],
        ["methodologie_puissance/PUISSANCE_CONJOINTE_MATIERE.json"],
    ),
    (
        "ccm_paleoclimat",
        [sys.executable, "02_branche_systeme_solaire/couche_memoire_historique/exploratoire_causalite/run_ccm.py"],
        ["02_branche_systeme_solaire/couche_memoire_historique/exploratoire_causalite/resultats/CCM_RESULTAT.json"],
    ),
    (
        "ltee_replay",
        [sys.executable, "03_branche_vivant/ltee_replay_history/analyser.py"],
        ["03_branche_vivant/ltee_replay_history/resultats/RESULTAT.json"],
    ),
    (
        "assembly_bridge",
        [sys.executable, "comparaisons_externes/assembly_theory/run_diagnostic.py"],
        ["comparaisons_externes/assembly_theory/DIAGNOSTIC.json"],
    ),
    (
        "viabilite_spin",
        [sys.executable, "02_branche_systeme_solaire/couche_spin_orbite/run_viability.py"],
        [
            "02_branche_systeme_solaire/couche_spin_orbite/resultats/viabilite/RESULTAT.json",
            "02_branche_systeme_solaire/couche_spin_orbite/resultats/viabilite/trajectoires_frontiere.csv",
        ],
    ),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--relative-tolerance", type=float, default=1e-10)
    parser.add_argument("--absolute-tolerance", type=float, default=1e-10)
    args = parser.parse_args()

    originals: dict[Path, bytes] = {}
    with tempfile.TemporaryDirectory(prefix="oric_formalismes_") as td:
        temp = Path(td)
        reference = temp / "reference"
        candidate = temp / "candidate"
        try:
            for name, command, outputs in CASES:
                print(f"[recalcul] {name}")
                for rel in outputs:
                    path = ROOT / rel
                    if not path.is_file():
                        raise FileNotFoundError(f"sortie de référence absente: {rel}")
                    originals.setdefault(path, path.read_bytes())
                    dest = reference / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(originals[path])

                subprocess.run(command, cwd=ROOT, check=True, stdout=subprocess.DEVNULL)

                for rel in outputs:
                    path = ROOT / rel
                    dest = candidate / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, dest)

            verify = [
                sys.executable,
                str(ROOT / "scripts/verifier_reproductibilite_resultats.py"),
                "--reference", str(reference),
                "--candidate", str(candidate),
                "--relative-tolerance", str(args.relative_tolerance),
                "--absolute-tolerance", str(args.absolute_tolerance),
            ]
            completed = subprocess.run(verify, cwd=ROOT)
            return completed.returncode
        finally:
            for path, content in originals.items():
                path.write_bytes(content)


if __name__ == "__main__":
    raise SystemExit(main())
