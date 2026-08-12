#!/usr/bin/env python3
"""Ajoute les métadonnées d'une registration OSF sans toucher au protocole gelé."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRED_DIR = HERE.parent
INDEX = HERE / "INDEX.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def registration_ids() -> list[str]:
    index = load(INDEX)
    return [row["id"] for row in index["registrations"]]


def apply(identifier: str, public_url: str, registered_at: str, doi: str | None) -> None:
    reg_path = HERE / f"{identifier}.registration.json"
    source_path = PRED_DIR / f"{identifier}.json"
    if not reg_path.is_file() or not source_path.is_file():
        raise SystemExit(f"paquet incomplet pour {identifier}")
    reg = load(reg_path)
    expected = reg.get("source_sha256")
    actual = sha256(source_path)
    if expected != actual:
        raise SystemExit(
            f"empreinte scientifique modifiée pour {identifier}: attendu {expected}, obtenu {actual}"
        )
    reg["public_url"] = public_url
    reg["registered_at"] = registered_at
    if doi:
        reg["doi"] = doi
    reg["status"] = "publicly_registered"
    dump(reg_path, reg)


def update_index(ids: set[str]) -> None:
    index = load(INDEX)
    for row in index["registrations"]:
        if row["id"] in ids:
            row["status"] = "publicly_registered"
    dump(INDEX, index)


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true")
    group.add_argument("--prediction-id", action="append", dest="prediction_ids")
    parser.add_argument("--public-url", required=True)
    parser.add_argument("--registered-at", required=True, help="YYYY-MM-DD")
    parser.add_argument("--doi")
    args = parser.parse_args()

    ids = registration_ids() if args.all else args.prediction_ids
    unknown = sorted(set(ids) - set(registration_ids()))
    if unknown:
        raise SystemExit(f"identifiants inconnus: {unknown}")
    for identifier in ids:
        apply(identifier, args.public_url, args.registered_at, args.doi)
    update_index(set(ids))
    print(f"OSF: métadonnées publiques appliquées à {len(ids)} prédiction(s), protocole scientifique inchangé")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
