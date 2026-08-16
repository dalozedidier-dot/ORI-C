#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(*args: str) -> None:
    print("+", " ".join(args))
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> int:
    py = sys.executable

    # Regenerate the two derived views with the corrected authority-aware generators.
    run(py, "scripts/construire_verrous_actifs.py")
    run(py, "scripts/evaluer_readiness_verrous.py")

    # Validate the exact campaign that failed in the uploaded logs.
    run(
        py, "-m", "pytest", "-q",
        "plan_directeur/campagne_centrale_2026_08_11/tests",
        "03_branche_vivant/lignees_vesicules/tests/test_pacc_prospectif_gate.py",
    )

    # The helper must not become a repository file. Remove it before rebuilding the manifest.
    this_file = Path(__file__).resolve()
    try:
        this_file.unlink()
    except OSError as exc:
        raise SystemExit(f"Impossible de supprimer le helper temporaire: {exc}")

    # The new registration package is a real repository file, so main goes 1860 -> 1861.
    run(py, "build_manifest.py", "build")
    run(py, "build_manifest.py", "verify")

    # Re-run the generators after manifest construction to prove the views are deterministic.
    run(py, "scripts/construire_verrous_actifs.py")
    run(py, "scripts/evaluer_readiness_verrous.py")
    run(py, "build_manifest.py", "verify")

    print("Correctif ORI-C appliqué et vérifié.")
    print("MAIN_MANIFEST_FILES doit maintenant valoir 1861. Le snapshot stable reste inchangé.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
