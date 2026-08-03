from __future__ import annotations

import hashlib
import json
import platform
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _package_version(distribution: str) -> str | None:
    try:
        return version(distribution)
    except PackageNotFoundError:
        return None


def write_manifest(run_dir: Path, config: dict) -> Path:
    files = []
    for path in sorted(run_dir.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            files.append(
                {
                    "path": str(path.relative_to(run_dir)),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    manifest = {
        "schema_version": 1,
        "experiment": config["experiment"]["name"],
        "backend": config["experiment"]["backend"],
        "python": sys.version,
        "platform": platform.platform(),
        "packages": {
            "oric-solar-history": _package_version("oric-solar-history"),
            "numpy": _package_version("numpy"),
            "scipy": _package_version("scipy"),
            "pandas": _package_version("pandas"),
            "matplotlib": _package_version("matplotlib"),
            "pyyaml": _package_version("PyYAML"),
            "tabulate": _package_version("tabulate"),
            "rebound": _package_version("rebound"),
            "reboundx": _package_version("reboundx"),
        },
        "files": files,
    }
    output = run_dir / "manifest.json"
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return output
