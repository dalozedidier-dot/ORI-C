#!/usr/bin/env python3
"""Lance les contrôles rapides du dossier ORI-C."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOCLE = ROOT / "00_socle"
MATTER_HYPER = ROOT / "01_branche_matiere/hypergraphe_transformations"
MATTER_INV = ROOT / "01_branche_matiere/inventaire_hierarchique"
MEMORY = ROOT / "02_branche_systeme_solaire/couche_memoire_historique"
ASTRO = ROOT / "02_branche_systeme_solaire/couche_astronomique/code/ORI-C_Systeme_solaire_tests"
PLATFORM = ROOT / "plateforme/source_corrigee"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict-lfs",
        action="store_true",
        help="refuser tout pointeur Git LFS non hydraté",
    )
    args = parser.parse_args(argv)

    verifier = [sys.executable, "verifier_dossier.py"]
    if not args.strict_lfs:
        verifier.append("--allow-lfs-pointers")

    commands = [
        (ROOT, verifier, None),
        (SOCLE, [sys.executable, "-m", "pytest", "-q"], None),
        (MATTER_HYPER, [sys.executable, "-m", "pytest", "-q"], None),
        (MATTER_INV, [sys.executable, "-m", "pytest", "-q"], None),
        (MEMORY, [sys.executable, "-m", "unittest", "discover", "-s", "tests"], MEMORY / "src"),
        (PLATFORM, [sys.executable, "-m", "pytest", "-q"], None),
        # REBOUND et ses bibliothèques natives sont exécutés en dernier. Sur
        # certaines plateformes, lancer un autre pytest après cette suite peut
        # bloquer le sous-processus suivant malgré une suite REBOUND réussie.
        (ASTRO, [sys.executable, "-m", "pytest", "-q"], ASTRO / "src"),
    ]

    failed: list[tuple[str, int]] = []
    for cwd, cmd, pythonpath in commands:
        env = os.environ.copy()
        if pythonpath is not None:
            previous = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = str(pythonpath) + (os.pathsep + previous if previous else "")
        if "pytest" in cmd:
            env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
        env.setdefault("OPENBLAS_NUM_THREADS", "1")
        env.setdefault("OMP_NUM_THREADS", "1")
        label = "." if cwd == ROOT else cwd.relative_to(ROOT)
        print(f"\n=== {label} ===", flush=True)
        result = subprocess.run(cmd, cwd=cwd, env=env)
        if result.returncode:
            failed.append((str(label), result.returncode))
    if failed:
        print("Échecs :", failed)
        return 1
    print("Tous les contrôles rapides ont réussi.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
