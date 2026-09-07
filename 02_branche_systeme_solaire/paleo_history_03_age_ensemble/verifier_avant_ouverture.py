#!/usr/bin/env python3
"""Refuse l'ouverture paléo tant que le gel exact n'est pas dans HEAD."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FREEZE = HERE / "PRED-PALEO-HISTORY-03-AGE-ENSEMBLE.json"
RECEIPT = HERE / "PRED-PALEO-HISTORY-03-AGE-ENSEMBLE.sha256"
REL_FREEZE = FREEZE.relative_to(ROOT).as_posix()
REL_RECEIPT = RECEIPT.relative_to(ROOT).as_posix()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def committed_bytes(relative_path: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"HEAD:{relative_path}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if completed.returncode:
        raise RuntimeError(f"absent de HEAD: {relative_path}")
    return completed.stdout


def verify_committed_freeze() -> str:
    working_freeze = FREEZE.read_bytes()
    working_receipt = RECEIPT.read_bytes()
    if committed_bytes(REL_FREEZE) != working_freeze:
        raise RuntimeError("le gel de travail n'est pas identique au gel commité dans HEAD")
    if committed_bytes(REL_RECEIPT) != working_receipt:
        raise RuntimeError("le reçu SHA256 n'est pas identique au reçu commité dans HEAD")
    expected = RECEIPT.read_text(encoding="ascii").strip().split()[0]
    actual = sha256(working_freeze)
    if expected != actual:
        raise RuntimeError(f"SHA256 du gel invalide: attendu {expected}, obtenu {actual}")
    freeze = json.loads(working_freeze)
    if freeze["firewall"]["raw_values_opened_by_ORI_C"] is not False:
        raise RuntimeError("le pare-feu n'atteste plus que les valeurs sont fermées")
    return actual


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("data_path", nargs="?", type=Path)
    args = parser.parse_args()
    if not args.verify_only and args.data_path is None:
        parser.error("data_path est requis hors mode --verify-only")
    try:
        digest = verify_committed_freeze()
    except (OSError, RuntimeError, KeyError, ValueError) as error:
        print(f"OUVERTURE REFUSEE: {error}")
        return 2
    print(f"Gel commité vérifié: sha256:{digest}")
    if args.verify_only:
        return 0
    with args.data_path.open("rb") as stream:
        print(f"Accès autorisé après gel commité: {stream.read(0)!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
