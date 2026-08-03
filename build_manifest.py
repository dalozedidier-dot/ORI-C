"""Construit et vérifie un manifeste SHA-256 portable du dossier ORI-C."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# .mplconfig et .claude sont des caches regeneres a l execution. Ils
# etaient exclus par verifier_dossier.py et construire_dossier.py mais pas
# ici : le manifeste inscrivait un fichier que le verificateur ne balayait
# pas, et le signalait ensuite comme absent. Les trois listes sont alignees.
EXCLUDED_PARTS = {".git", "__pycache__", ".pytest_cache", ".pytest-tmp",
                  ".mplconfig", ".claude", "node_modules"}
EXCLUDED_FILES = {"MANIFEST.sha256", "MANIFEST.sha256.json"}


def files() -> list[Path]:
    return sorted(
        (path for path in ROOT.rglob("*")
         if path.is_file()
         and path.name not in EXCLUDED_FILES
         and not any(part in EXCLUDED_PARTS for part in path.relative_to(ROOT).parts)),
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def build() -> list[dict[str, object]]:
    entries = [
        {"path": path.relative_to(ROOT).as_posix(), "size": path.stat().st_size, "sha256": digest(path)}
        for path in files()
    ]
    (ROOT / "MANIFEST.sha256").write_text(
        "".join(f"{entry['sha256']}  {entry['path']}\n" for entry in entries), encoding="utf-8"
    )
    (ROOT / "MANIFEST.sha256.json").write_text(
        json.dumps({"algorithm": "sha256", "path_base": ".", "files": entries}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return entries


def verify() -> None:
    document = json.loads((ROOT / "MANIFEST.sha256.json").read_text(encoding="utf-8"))
    expected = {entry["path"]: entry for entry in document["files"]}
    actual = {path.relative_to(ROOT).as_posix(): path for path in files()}
    if set(expected) != set(actual):
        raise SystemExit("La liste de fichiers diffère du manifeste")
    for name, path in actual.items():
        if path.stat().st_size != expected[name]["size"] or digest(path) != expected[name]["sha256"]:
            raise SystemExit(f"Empreinte invalide: {name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "verify"))
    args = parser.parse_args()
    if args.command == "build":
        print(f"{len(build())} fichiers inscrits")
    else:
        verify()
        print("Manifeste valide")
