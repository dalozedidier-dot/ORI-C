#!/usr/bin/env python3
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "donnees_externes/donnees_reelles_2026_08_07/SOURCE_BUNDLE.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle", type=Path)
    ap.add_argument("--verify-all", action="store_true", help="Vérifier toutes les entrées de MANIFESTE.csv")
    ap.add_argument("--check-only", action="store_true", help="Ne rien écrire dans le dépôt")
    args = ap.parse_args()

    cfg = json.loads(SOURCE.read_text(encoding="utf-8"))
    if sha256_file(args.bundle) != cfg["bundle_sha256"]:
        raise SystemExit("SHA-256 du bundle inattendu")

    with zipfile.ZipFile(args.bundle) as zf:
        manifest_name = "DONNEES_REELLES_ORI-C/MANIFESTE.csv"
        rows = list(csv.DictReader(zf.read(manifest_name).decode("utf-8-sig").splitlines()))
        by_path = {row["chemin"].replace("\\", "/"): row for row in rows}

        if args.verify_all:
            for rel, row in by_path.items():
                member = f"DONNEES_REELLES_ORI-C/{rel}"
                data = zf.read(member)
                if len(data) != int(row["octets"]) or sha256_bytes(data) != row["sha256"]:
                    raise SystemExit(f"Entrée du bundle invalide: {rel}")

        imported = []
        for item in cfg["selected_assets"]:
            member = item["source_path"]
            rel_manifest = member.removeprefix("DONNEES_REELLES_ORI-C/")
            row = by_path.get(rel_manifest)
            if row is None:
                raise SystemExit(f"Fichier absent du manifeste du bundle: {member}")
            data = zf.read(member)
            digest = sha256_bytes(data)
            if len(data) != item["size"] or digest != item["sha256"]:
                raise SystemExit(f"Empreinte inattendue: {member}")
            if int(row["octets"]) != item["size"] or row["sha256"] != item["sha256"]:
                raise SystemExit(f"SOURCE_BUNDLE et MANIFESTE.csv divergent: {member}")
            target = ROOT / item["target_path"]
            if not args.check_only:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            imported.append({"target": item["target_path"], "sha256": digest, "size": len(data)})

    for absent in cfg.get("deliberately_absent", []):
        path = ROOT / absent["path"]
        if path.exists():
            raise SystemExit(f"Fichier qui doit rester absent: {absent['path']}")

    print(json.dumps({"status": "ok", "check_only": args.check_only, "assets": imported}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
