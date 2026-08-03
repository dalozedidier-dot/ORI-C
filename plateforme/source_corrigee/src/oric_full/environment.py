from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def capture_environment() -> dict:
    packages = {}
    for name in ["numpy", "pandas", "scipy", "networkx", "matplotlib", "scikit-learn", "statsmodels"]:
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    git_commit = None
    try:
        git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        pass
    return {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "packages": packages,
        "git_commit": git_commit,
        "cwd": os.getcwd(),
    }


def write_manifest(root: Path, output: Path, exclude: set[Path] | None = None) -> None:
    exclude = {p.resolve() for p in (exclude or set())}
    rows = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.resolve() in exclude:
            continue
        rows.append(f"{sha256_file(path)}  {path.relative_to(root).as_posix()}")
    output.write_text("\n".join(rows) + "\n", encoding="utf-8")


def write_environment(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(capture_environment(), ensure_ascii=False, indent=2), encoding="utf-8")
