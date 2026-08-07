#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAYLOAD = HERE / "payload"
PATCH_MANIFEST = HERE / "PATCH_MANIFEST.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def run(repo: Path, *args: str) -> None:
    print("+", " ".join(args))
    subprocess.run(args, cwd=repo, check=True)


def load_manifest() -> dict:
    payload = json.loads(PATCH_MANIFEST.read_text(encoding="utf-8"))
    if payload.get("repository") != "dalozedidier-dot/ORI-C":
        raise SystemExit("PATCH_MANIFEST.json inattendu")
    return payload


def verify_payload(manifest: dict) -> None:
    for item in manifest["files"]:
        rel = Path(item["path"])
        source = PAYLOAD / rel
        if not source.is_file():
            raise SystemExit(f"Payload absent: {rel}")
        actual = sha256(source)
        expected = item["sha256_after"]
        if actual != expected:
            raise SystemExit(f"Payload altéré: {rel}\n{actual}\n!=\n{expected}")


def verify_base(repo: Path, manifest: dict) -> None:
    errors: list[str] = []
    for item in manifest["files"]:
        rel = Path(item["path"])
        target = repo / rel
        status = item["status"]
        if status == "replace_existing":
            if not target.is_file():
                errors.append(f"fichier à remplacer absent: {rel}")
                continue
            expected = item.get("expected_current_github_blob_sha_before")
            actual = git_blob_sha(target)
            if expected and actual != expected:
                errors.append(
                    f"base différente pour {rel}: blob local {actual}, attendu {expected}"
                )
        elif status == "new":
            if target.exists():
                source = PAYLOAD / rel
                if target.is_file() and sha256(target) == sha256(source):
                    continue
                errors.append(f"le nouveau fichier existe déjà avec un autre contenu: {rel}")
        else:
            errors.append(f"statut de patch inconnu pour {rel}: {status}")
    if errors:
        print("\nREFUS D'APPLICATION : le dépôt n'est plus exactement la base auditée.\n")
        for error in errors:
            print("-", error)
        print("\nAucun fichier n'a été modifié.")
        raise SystemExit(3)


def make_backup(repo: Path, manifest: dict) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = repo.parent / f"ORI-C_backup_avant_barriere_scientifique_{stamp}"
    backup.mkdir(parents=True, exist_ok=False)
    inventory = []
    for item in manifest["files"]:
        rel = Path(item["path"])
        target = repo / rel
        if target.is_file():
            dst = backup / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, dst)
            inventory.append(rel.as_posix())
    (backup / "BACKUP_FILES.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for name in ("MANIFEST.sha256", "MANIFEST.sha256.json"):
        p = repo / name
        if p.is_file():
            shutil.copy2(p, backup / name)
    return backup


def apply_payload(repo: Path, manifest: dict) -> None:
    for item in manifest["files"]:
        rel = Path(item["path"])
        source = PAYLOAD / rel
        target = repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def restore(repo: Path, backup: Path, manifest: dict) -> None:
    print("\nÉchec: restauration de la base précédente...")
    for item in manifest["files"]:
        rel = Path(item["path"])
        target = repo / rel
        backed = backup / rel
        if backed.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backed, target)
        elif item["status"] == "new" and target.exists():
            target.unlink()
    for name in ("MANIFEST.sha256", "MANIFEST.sha256.json"):
        backed = backup / name
        if backed.is_file():
            shutil.copy2(backed, repo / name)
    print(f"Restauration terminée. Sauvegarde conservée: {backup}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Applique la barrière scientifique ORI-C puis reconstruit immédiatement les deux manifestes SHA-256."
    )
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="racine du dépôt ORI-C")
    parser.add_argument(
        "--full-validation",
        action="store_true",
        help="exécute aussi les tests pytest ciblés après les contrôles d'intégrité",
    )
    args = parser.parse_args()
    repo = args.repo.expanduser().resolve()

    required = [repo / "build_manifest.py", repo / "verifier_dossier.py", repo / ".git"]
    if not all(p.exists() for p in required):
        raise SystemExit(f"Ce chemin ne ressemble pas à la racine du dépôt Git ORI-C: {repo}")

    manifest = load_manifest()
    verify_payload(manifest)
    verify_base(repo, manifest)
    backup = make_backup(repo, manifest)

    try:
        apply_payload(repo, manifest)

        # CRITIQUE : le manifeste est reconstruit AVANT tout validateur qui le lit.
        run(repo, sys.executable, "build_manifest.py", "build")
        run(repo, sys.executable, "build_manifest.py", "verify")
        run(repo, sys.executable, "verifier_dossier.py", "--allow-lfs-pointers")
        run(repo, sys.executable, "scripts/valider_barriere_scientifique_publication.py")

        if args.full_validation:
            run(
                repo,
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "plateforme/source_corrigee/tests/test_scientific_firewall.py",
                "plateforme/source_corrigee/tests/test_runner.py",
                "plateforme/source_corrigee/tests/test_data_and_engines.py",
            )

        m1 = repo / "MANIFEST.sha256"
        m2 = repo / "MANIFEST.sha256.json"
        print("\nCORRECTION APPLIQUÉE ET MANIFESTES RECONSTRUITS.")
        print(f"MANIFEST.sha256      sha256={sha256(m1)}")
        print(f"MANIFEST.sha256.json sha256={sha256(m2)}")
        print(f"Sauvegarde: {backup}")
        print("Tu peux maintenant vérifier git diff puis commit/push.")
        return 0
    except Exception:
        restore(repo, backup, manifest)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
