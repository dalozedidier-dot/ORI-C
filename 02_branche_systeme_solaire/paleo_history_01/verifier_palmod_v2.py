#!/usr/bin/env python3
"""Vérifie les distributions PALMOD sans désérialiser un pickle distant."""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def inspect_lipd_zip(path: Path) -> dict:
    with zipfile.ZipFile(path) as archive:
        lipd = [name for name in archive.namelist() if name.endswith(".lpd")]
    return {"lipd_count": len(lipd), "sha256": sha256(path), "has_475_sites": len(lipd) == 475}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("lipd_zip", type=Path)
    args = parser.parse_args()
    result = inspect_lipd_zip(args.lipd_zip)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["has_475_sites"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
