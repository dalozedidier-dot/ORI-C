#!/usr/bin/env python3
"""Construit une archive ORI-C autonome après hydratation de Git LFS.

Le script refuse de produire une archive dite canonique tant qu'un seul
pointeur Git LFS est présent. Il régénère ensuite les manifestes, exécute le
contrôle strict, crée un ZIP déterministe et publie son SHA-256.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
EXCLUDED_PARTS = {
    ".git", "__pycache__", ".pytest_cache", ".pytest-tmp",
    ".mplconfig", ".claude", "node_modules", "dist",
}
FIXED_DATE = (2026, 8, 10, 0, 0, 0)
EXCLUDED_PATH_PREFIXES = ("donnees_externes/lot_scientifique_maximal_2026_08_05/raw/",)


def is_lfs_pointer(path: Path) -> bool:
    if path.stat().st_size > 1024:
        return False
    data = path.read_bytes()
    return data.replace(b"\r\n", b"\n").startswith(
        b"version https://git-lfs.github.com/spec/v1\n"
    )


def files() -> list[Path]:
    return sorted(
        (
            path for path in ROOT.rglob("*")
            if path.is_file()
            and not any(part in EXCLUDED_PARTS for part in path.relative_to(ROOT).parts)
            and not any(
                path.relative_to(ROOT).as_posix().startswith(prefix)
                for prefix in EXCLUDED_PATH_PREFIXES
            )
        ),
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )


def run(*parts: str) -> None:
    completed = subprocess.run(parts, cwd=ROOT)
    if completed.returncode:
        raise SystemExit(completed.returncode)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def build_zip(destination: Path) -> None:
    prefix = f"ORI-C-{VERSION}"
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files():
            relative = path.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(f"{prefix}/{relative}", FIXED_DATE)
            mode = path.stat().st_mode & 0o777
            info.external_attr = (mode & 0xFFFF) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT.parent,
        help="répertoire de sortie du ZIP et de son fichier SHA-256",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="ne pas exécuter les suites rapides avant l'archivage",
    )
    args = parser.parse_args()

    pointers = [path.relative_to(ROOT).as_posix() for path in files() if is_lfs_pointer(path)]
    if pointers:
        print(f"Impossible de construire l'archive canonique : {len(pointers)} objets Git LFS ne sont pas hydratés.")
        for path in pointers[:20]:
            print(f"  {path}")
        if len(pointers) > 20:
            print(f"  ... et {len(pointers) - 20} autres")
        print("Exécuter `git lfs pull`, puis relancer ce script.")
        return 2

    run(sys.executable, "build_manifest.py", "build")
    run(sys.executable, "build_manifest.py", "verify")
    run(sys.executable, "verifier_dossier.py")
    if not args.skip_tests:
        run(sys.executable, "scripts/valider_tout.py", "--strict-lfs")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    destination = args.output_dir / f"ORI-C-{VERSION}-canonique.zip"
    build_zip(destination)
    sha256 = digest(destination)
    checksum = destination.with_suffix(destination.suffix + ".sha256")
    checksum.write_text(f"{sha256}  {destination.name}\n", encoding="utf-8", newline="\n")
    print(f"Archive créée : {destination}")
    print(f"SHA-256 : {sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
