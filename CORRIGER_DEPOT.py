#!/usr/bin/env python3
"""Corrige l'intégration du tri 366/317 dans un checkout ORI-C existant.

Ce script est un outil de livraison externe. Il ne doit pas être copié dans le
repo. Il applique les fichiers de politique, retire les artefacts de paquet qui
n'ont rien à faire dans le dépôt, restaure les garde-fous CI, enregistre
l'autorité documentaire, reconstruit les manifestes officiels, puis exécute les
contrôles disponibles.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAYLOAD = HERE / "payload"

BAD_ROOT_FILES = [
    "APPLIQUER.md",
    "TRI_COMPLET_683_ORIC.csv",
    "TRI_COMPLET_683_ORIC.md",
]


def fail(message: str) -> None:
    raise SystemExit(message)


def run(cmd: list[str], cwd: Path, *, required: bool = True) -> int:
    print("+", " ".join(cmd))
    result = subprocess.run(cmd, cwd=cwd)
    if required and result.returncode:
        fail(f"Commande en échec ({result.returncode}) : {' '.join(cmd)}")
    return result.returncode


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        fail(f"Ancre {label!r} attendue exactement une fois, trouvée {count} fois")
    return text.replace(old, new, 1)


def patch_workflow(repo: Path) -> None:
    path = repo / ".github/workflows/audit-empirique-strict.yml"
    text = path.read_text(encoding="utf-8")

    trigger = "      - 'plateforme/valider_noyau_probant.py'\n"
    trigger_test = "      - 'plateforme/campagne_maximale_reelle/tests/test_noyau_probant.py'\n"
    if trigger_test not in text:
        if trigger not in text:
            fail("Le workflow ne contient pas l'ancre valider_noyau_probant.py")
        text = text.replace(trigger, trigger + trigger_test, 1)

    validation_step = """      - name: Valider et matérialiser le noyau probant actif\n        run: |\n          python plateforme/valider_noyau_probant.py \\\n            --sortie-csv plateforme/campagne_maximale_reelle/resultats_empiriques/strict_683/NOYAU_PROBANT_ACTIF.csv \\\n            --sortie-json plateforme/campagne_maximale_reelle/resultats_empiriques/strict_683/NOYAU_PROBANT_RESUME.json\n"""
    test_noyau = """      - name: Tester le tri fail-closed du noyau probant\n        run: python -m pytest -q plateforme/campagne_maximale_reelle/tests/test_noyau_probant.py\n\n"""
    if "Tester le tri fail-closed du noyau probant" not in text:
        if validation_step not in text:
            fail("Étape de matérialisation du noyau absente ou modifiée de façon inattendue")
        text = text.replace(validation_step, test_noyau + validation_step, 1)

    certification_step = """      - name: Tester la couche de certification fail-closed\n        run: python -m pytest -q plateforme/campagne_maximale_reelle/tests/test_certifications_specialisees.py\n\n"""
    certifier_anchor = "      - name: Certifier les verdicts scientifiques des campagnes spécialisées\n"
    if "Tester la couche de certification fail-closed" not in text:
        if certifier_anchor not in text:
            fail("Étape de certification spécialisée introuvable")
        text = text.replace(certifier_anchor, certification_step + certifier_anchor, 1)

    path.write_text(text, encoding="utf-8", newline="\n")


def patch_authority(repo: Path) -> None:
    path = repo / "AUTORITE_DES_DOCUMENTS.md"
    text = path.read_text(encoding="utf-8")
    row = (
        "| Politique du noyau probant | `plateforme/POLITIQUE_NOYAU_PROBANT.csv` et "
        "`plateforme/NOYAU_PROBANT.md` | organisation des cibles de preuve ; **ne fixe aucun verdict** "
        "et ne remplace ni les 683 entrées canoniques ni les critères gelés |\n"
    )
    if "| Politique du noyau probant |" not in text:
        anchor = "| Campagne plateforme | `plan_directeur/campagne_plateforme/README.md` | généré ; **ne fixe aucun statut** |\n"
        if anchor not in text:
            fail("Ancre 'Campagne plateforme' absente de AUTORITE_DES_DOCUMENTS.md")
        text = text.replace(anchor, anchor + row, 1)
    path.write_text(text, encoding="utf-8", newline="\n")


def copy_payload(repo: Path) -> None:
    for src in PAYLOAD.rglob("*"):
        if not src.is_file():
            continue
        rel = src.relative_to(PAYLOAD)
        dst = repo / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", nargs="?", default=".", type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve()

    if (repo / ".git").exists():
        initial = subprocess.run(
            ["git", "status", "--porcelain"], cwd=repo, capture_output=True, text=True, encoding="utf-8"
        ).stdout.strip()
        if initial:
            fail("Le checkout doit être propre avant correction. Changements présents :\n" + initial)

    required = [
        repo / "build_manifest.py",
        repo / "verifier_dossier.py",
        repo / "scripts/valider_tout.py",
        repo / "plateforme/catalogue_tests.csv",
        repo / ".github/workflows/audit-empirique-strict.yml",
    ]
    missing = [str(p.relative_to(repo)) for p in required if not p.exists()]
    if missing:
        fail(f"Ce dossier ne ressemble pas au checkout ORI-C attendu : {missing}")

    print("== Retrait des artefacts de livraison qui ne doivent pas être versionnés ==")
    for rel in BAD_ROOT_FILES:
        path = repo / rel
        if path.exists():
            path.unlink()
            print("supprimé:", rel)

    print("== Installation de la politique et de ses tests ==")
    copy_payload(repo)

    print("== Restauration des garde-fous CI ==")
    patch_workflow(repo)
    patch_authority(repo)

    print("== Validation spécifique du tri ==")
    run([sys.executable, "plateforme/valider_noyau_probant.py"], repo)
    run([sys.executable, "-m", "pytest", "-q", "plateforme/campagne_maximale_reelle/tests/test_noyau_probant.py"], repo)
    run([sys.executable, "-m", "pytest", "-q", "plateforme/campagne_maximale_reelle/tests/test_certifications_specialisees.py"], repo)
    run([sys.executable, "-m", "pytest", "-q", "plateforme/source_corrigee/tests/test_catalogue.py"], repo)
    run([sys.executable, "-m", "compileall", "-q", "plateforme/valider_noyau_probant.py", "plateforme/campagne_maximale_reelle/tests/test_noyau_probant.py"], repo)

    print("== Reconstruction officielle des manifestes APRÈS la dernière modification ==")
    run([sys.executable, "build_manifest.py", "build"], repo)

    print("== Contrôles d'intégrité ==")
    run([sys.executable, "verifier_dossier.py"], repo)
    run([sys.executable, "scripts/verifier_fins_de_ligne.py"], repo)

    # Ces deux contrôles peuvent dépendre de Git LFS ou du contexte Git réel.
    # Ils restent obligatoires dans le checkout de publication ; le script les
    # lance et propage leur échec.
    run([sys.executable, "scripts/controle_avant_push.py"], repo)
    run([sys.executable, "scripts/valider_tout.py", "--strict-lfs"], repo)
    run(["git", "diff", "--check"], repo)

    if (repo / ".git").exists():
        status = subprocess.run(
            ["git", "status", "--porcelain"], cwd=repo, capture_output=True, text=True, encoding="utf-8"
        ).stdout.splitlines()
        allowed = {
            ".github/workflows/audit-empirique-strict.yml",
            "APPLIQUER.md",
            "AUTORITE_DES_DOCUMENTS.md",
            "MANIFEST.sha256",
            "MANIFEST.sha256.json",
            "TRI_COMPLET_683_ORIC.csv",
            "TRI_COMPLET_683_ORIC.md",
            "plateforme/NOYAU_PROBANT.md",
            "plateforme/POLITIQUE_NOYAU_PROBANT.csv",
            "plateforme/valider_noyau_probant.py",
            "plateforme/campagne_maximale_reelle/tests/test_noyau_probant.py",
        }
        unexpected = []
        for line in status:
            path = line[3:]
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            if path not in allowed:
                unexpected.append(line)
        if unexpected:
            fail("Changements inattendus après correction :\n" + "\n".join(unexpected))
        print("\nGit status attendu :")
        for line in status:
            print(line)

    print("\nCorrection terminée : manifestes reconstruits et contrôles passés.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
