#!/usr/bin/env python3
"""Inventorie PALMOD 2 et vérifie les fichiers LiPD contenant les ensembles.

Le ZIP de compilation ne contient que les résumés. Chaque fiche LiPDverse
expose séparément un fichier ``*-ensemble.lpd``. Ce module construit leurs URL
directes sans télécharger les données et contrôle localement qu'un fichier
d'ensemble contient bien 1 000 tirages chronologiques plus la profondeur.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _metadata_from_lpd_bytes(payload: bytes) -> dict:
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        return json.loads(archive.read("bag/data/metadata.jsonld"))


def build_ensemble_catalog(path: Path) -> list[dict]:
    """Retourne les 475 URL individuelles à partir du ZIP PALMOD public."""
    records: list[dict] = []
    with zipfile.ZipFile(path) as compilation:
        for name in sorted(n for n in compilation.namelist() if n.endswith(".lpd")):
            metadata = _metadata_from_lpd_bytes(compilation.read(name))
            base = metadata["lipdverseLink"].rstrip("/")
            dataset_name = metadata["dataSetName"]
            records.append({
                "dataset_id": metadata["datasetId"],
                "dataset_name": dataset_name,
                "dataset_version": metadata["datasetVersion"],
                "ensemble_url": f"{base}/{dataset_name}-ensemble.lpd",
            })
    return records


def inspect_lipd_zip(path: Path) -> dict:
    records = build_ensemble_catalog(path)
    return {
        "lipd_count": len(records),
        "sha256": sha256(path),
        "has_475_sites": len(records) == 475,
        "ensemble_urls_constructed": len(records),
    }


def inspect_ensemble_lpd(path: Path) -> dict:
    """Contrôle structurel d'un fichier ``-ensemble.lpd`` téléchargé."""
    with zipfile.ZipFile(path) as archive:
        metadata = json.loads(archive.read("bag/data/metadata.jsonld"))
        chron_tables = [
            name for name in archive.namelist()
            if ".chron" in name and "ensemble" in name and name.endswith(".csv")
        ]
        column_counts = []
        for name in chron_tables:
            first_line = archive.read(name).splitlines()[0].decode("utf-8")
            column_counts.append(len(next(csv.reader([first_line]))))
        metadata_text = json.dumps(metadata, ensure_ascii=False)
    return {
        "sha256": sha256(path),
        "chronology_ensemble_tables": len(chron_tables),
        "column_counts": column_counts,
        "age_ensemble_declared": '"ageEnsemble"' in metadata_text,
        "has_1000_age_draws": bool(column_counts) and all(n == 1001 for n in column_counts),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("lipd_zip", type=Path, help="ZIP PALMOD 2 de compilation")
    parser.add_argument("--ensemble", type=Path, help="fichier individuel *-ensemble.lpd")
    parser.add_argument("--write-catalog", type=Path, help="écrit le catalogue léger des URL")
    args = parser.parse_args()

    result = inspect_lipd_zip(args.lipd_zip)
    if args.write_catalog:
        catalog = build_ensemble_catalog(args.lipd_zip)
        args.write_catalog.write_text(
            json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        result["catalog_written"] = str(args.write_catalog)
    if args.ensemble:
        result["ensemble_check"] = inspect_ensemble_lpd(args.ensemble)
    print(json.dumps(result, ensure_ascii=False))
    ensemble_ok = not args.ensemble or result["ensemble_check"]["has_1000_age_draws"]
    return 0 if result["has_475_sites"] and ensemble_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
