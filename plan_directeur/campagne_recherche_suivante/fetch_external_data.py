#!/usr/bin/env python3
"""Télécharge, contrôle et inventorie les données externes des nouveaux tests."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = Path(__file__).with_name("sources_externes.json")
DEST = ROOT / "donnees_externes"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def combined_sha256(files: list[dict[str, object]]) -> str:
    """Empreinte déterministe d'un jeu téléchargé fichier par fichier."""
    digest = hashlib.sha256()
    for item in sorted(files, key=lambda value: str(value["name"])):
        digest.update(str(item["name"]).encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(item["sha256"]).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def download(url: str, target: Path, retries: int = 4) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".part")
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "ORI-C scientific-research acquisition/1.1",
                    "Accept": "*/*",
                    "Referer": "https://datadryad.org/",
                },
            )
            with urllib.request.urlopen(request, timeout=300) as source, temporary.open("wb") as destination:
                shutil.copyfileobj(source, destination)
            if temporary.stat().st_size == 0:
                raise OSError("réponse vide")
            temporary.replace(target)
            return
        except (OSError, urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            temporary.unlink(missing_ok=True)
            if attempt < retries:
                time.sleep(2**attempt)
    raise RuntimeError(f"échec après {retries} tentatives: {last_error}")


def extract(raw: Path, folder: Path) -> list[str]:
    extracted_root = folder / "extracted"
    if extracted_root.exists():
        shutil.rmtree(extracted_root)
    extracted_root.mkdir(parents=True, exist_ok=True)
    if zipfile.is_zipfile(raw):
        with zipfile.ZipFile(raw) as archive:
            archive.extractall(extracted_root)
        return sorted(str(path.relative_to(extracted_root)) for path in extracted_root.rglob("*") if path.is_file())
    copied = extracted_root / raw.name
    shutil.copy2(raw, copied)
    return [copied.name]


def acquire_individual_files(
    dataset: dict[str, object],
    folder: Path,
    force: bool,
) -> tuple[list[str], list[dict[str, object]], str]:
    """Télécharge les fichiers publics un par un lorsque l'archive globale exige une authentification."""
    extracted_root = folder / "extracted"
    extracted_root.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    downloaded_count = 0

    for item in dataset.get("file_downloads", []):
        name = str(item["name"])
        url = str(item["url"])
        target = (extracted_root / name).resolve()
        if extracted_root.resolve() not in target.parents:
            raise ValueError(f"chemin de fichier interdit: {name}")
        if force or not target.exists():
            download(url, target)
            downloaded_count += 1
        records.append(
            {
                "name": name,
                "url": url,
                "sha256": sha256(target),
                "size_bytes": target.stat().st_size,
            }
        )

    if not records:
        raise ValueError("aucun fichier individuel déclaré")
    status = "downloaded" if downloaded_count == len(records) else ("cached" if downloaded_count == 0 else "mixed")
    extracted = sorted(str(path.relative_to(extracted_root)) for path in extracted_root.rglob("*") if path.is_file())
    return extracted, records, status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", action="append", help="Identifiant d'un jeu à télécharger")
    parser.add_argument("--force", action="store_true", help="Retélécharger même si le fichier est présent")
    parser.add_argument("--strict-optional", action="store_true", help="Échouer aussi pour un jeu optionnel")
    args = parser.parse_args(argv)

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    DEST.mkdir(exist_ok=True)
    report: list[dict[str, object]] = []

    for dataset in registry["datasets"]:
        if args.only and dataset["id"] not in args.only:
            continue
        folder = DEST / dataset["id"]
        folder.mkdir(parents=True, exist_ok=True)
        try:
            if dataset.get("file_downloads"):
                extracted, file_records, status = acquire_individual_files(dataset, folder, args.force)
                dataset_hash = combined_sha256(file_records)
                dataset_size = sum(int(item["size_bytes"]) for item in file_records)
                provenance = {
                    **dataset,
                    "download_status": status,
                    "sha256": dataset_hash,
                    "size_bytes": dataset_size,
                    "file_provenance": file_records,
                    "extracted_files": extracted,
                }
            else:
                raw = folder / dataset["archive_name"]
                status = "cached"
                if args.force or not raw.exists():
                    download(dataset["download_url"], raw)
                    status = "downloaded"
                extracted = extract(raw, folder)
                provenance = {
                    **dataset,
                    "download_status": status,
                    "sha256": sha256(raw),
                    "size_bytes": raw.stat().st_size,
                    "extracted_files": extracted,
                }

            missing = [
                name
                for name in dataset.get("expected_files", [])
                if not any(Path(item).name == name for item in extracted)
            ]
            provenance["missing_expected"] = missing
            (folder / "SOURCE.json").write_text(
                json.dumps(provenance, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            result_status = "ok" if not missing else "incomplete"
            report.append(
                {
                    "id": dataset["id"],
                    "required": bool(dataset.get("required_for_current_tests", False)),
                    "status": result_status,
                    "missing": missing,
                    "sha256": provenance["sha256"],
                    "size_bytes": provenance["size_bytes"],
                }
            )
        except Exception as exc:
            report.append(
                {
                    "id": dataset["id"],
                    "required": bool(dataset.get("required_for_current_tests", False)),
                    "status": "download_failed",
                    "error": str(exc),
                    "url": dataset.get("download_url"),
                }
            )

    (DEST / "ACQUISITION_REPORT.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))

    blocking = [
        item
        for item in report
        if item["status"] in {"download_failed", "incomplete"}
        and (item["required"] or args.strict_optional)
    ]
    return 1 if blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
