from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import hashlib
import json


DEFAULT_EXCLUDES = {
    ".git",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "__pycache__",
    ".venv",
    "venv",
}


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def iter_files(root: Path, excludes: set[str] | None = None) -> Iterable[Path]:
    root = Path(root)
    blocked = DEFAULT_EXCLUDES | set(excludes or set())
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in blocked for part in path.relative_to(root).parts):
            continue
        yield path


def build_manifest(root: Path, output: Path | None = None, excludes: set[str] | None = None) -> dict:
    root = Path(root).resolve()
    output = Path(output).resolve() if output else root / "MANIFEST.sha256.json"
    entries = []
    for path in iter_files(root, excludes=excludes):
        if path.resolve() == output:
            continue
        entries.append(
            {
                "path": path.relative_to(root).as_posix(),
                "size": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    payload = {
        "algorithm": "sha256",
        "root": root.name,
        "file_count": len(entries),
        "entries": entries,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def verify_manifest(root: Path, manifest: Path) -> dict:
    root = Path(root).resolve()
    manifest = Path(manifest)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    expected = {entry["path"]: entry for entry in payload.get("entries", [])}
    current = {
        path.relative_to(root).as_posix(): {
            "size": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in iter_files(root)
        if path.resolve() != manifest.resolve()
    }
    missing = sorted(set(expected) - set(current))
    extra = sorted(set(current) - set(expected))
    modified = sorted(
        key
        for key in set(expected) & set(current)
        if expected[key]["sha256"] != current[key]["sha256"]
        or int(expected[key]["size"]) != int(current[key]["size"])
    )
    return {
        "ok": not missing and not extra and not modified,
        "expected": len(expected),
        "current": len(current),
        "missing": missing,
        "extra": extra,
        "modified": modified,
    }
