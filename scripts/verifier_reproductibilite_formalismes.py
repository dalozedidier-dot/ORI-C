#!/usr/bin/env python3
"""Recalcule les formalismes externes versionnés puis compare leurs sorties.

Toutes les sorties déterministes sont comparées à la tolérance numérique globale
(très serrée par défaut). CCM est traité séparément : son estimateur dépend d'un
classement de voisins dans un espace reconstruit et de répétitions d'échantillons.
De minuscules différences de distances entre bibliothèques numériques peuvent
changer l'identité de voisins quasi ex aequo et déplacer les moyennes de rho de
~1e-4 sans changer le diagnostic. Sa tolérance dédiée est donc explicite et
locale ; elle ne relâche aucun autre formalisme.

PCMCI+ n'est pas versionné : son job CI séparé publie l'artefact exploratoire.
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


def _verify(reference: Path, candidate: Path, *, rel: float, abs_: float, label: str) -> int:
    print(f"[comparaison] {label}: rel={rel:g}, abs={abs_:g}")
    command = [
        sys.executable,
        str(ROOT / "scripts/verifier_reproductibilite_resultats.py"),
        "--reference", str(reference),
        "--candidate", str(candidate),
        "--relative-tolerance", str(rel),
        "--absolute-tolerance", str(abs_),
    ]
    return subprocess.run(command, cwd=ROOT).returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--relative-tolerance", type=float, default=1e-10)
    parser.add_argument("--absolute-tolerance", type=float, default=1e-10)
    parser.add_argument("--ccm-relative-tolerance", type=float, default=5e-3)
    parser.add_argument("--ccm-absolute-tolerance", type=float, default=2e-4)
    args = parser.parse_args()

    originals: dict[Path, bytes] = {}
    with tempfile.TemporaryDirectory(prefix="oric_formalismes_") as td:
        temp = Path(td)
        ref_strict = temp / "reference_strict"
        cand_strict = temp / "candidate_strict"
        ref_ccm = temp / "reference_ccm"
        cand_ccm = temp / "candidate_ccm"
        try:
            for name, command, outputs in CASES:
                print(f"[recalcul] {name}")
                is_ccm = name == "ccm_paleoclimat"
                reference = ref_ccm if is_ccm else ref_strict
                candidate = cand_ccm if is_ccm else cand_strict

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

            strict_rc = _verify(
                ref_strict,
                cand_strict,
                rel=args.relative_tolerance,
                abs_=args.absolute_tolerance,
                label="formalismes déterministes",
            )
            ccm_rc = _verify(
                ref_ccm,
                cand_ccm,
                rel=args.ccm_relative_tolerance,
                abs_=args.ccm_absolute_tolerance,
                label="CCM exploratoire",
            )
            if strict_rc or ccm_rc:
                return 1
            print("Reproductibilité des formalismes externes validée")
            return 0
        finally:
            for path, content in originals.items():
                path.write_bytes(content)


if __name__ == "__main__":
    raise SystemExit(main())
