#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fail(message: str) -> None:
    print(f"[ECHEC] {message}")
    raise SystemExit(1)


def safe_target(relative: str) -> Path:
    target = (ROOT / relative).resolve()
    if target != ROOT and ROOT not in target.parents:
        fail(f"chemin non sûr: {relative}")
    return target


def verify_checksums() -> int:
    lines = (ROOT / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
    count = 0
    for line in lines:
        if not line.strip():
            continue
        digest, relative = line.split("  ", 1)
        target = safe_target(relative)
        if not target.is_file():
            fail(f"fichier absent: {relative}")
        if sha256_file(target) != digest:
            fail(f"empreinte incorrecte: {relative}")
        count += 1
    print(f"[OK] {count} empreintes principales")
    return count


def verify_main_manifest(checksum_count: int) -> dict:
    manifest = json.loads((ROOT / "MANIFESTE.json").read_text(encoding="utf-8"))
    entries = manifest["files"]
    if len(entries) + 1 != checksum_count:
        fail("nombre de fichiers incohérent dans le manifeste principal")
    for entry in entries:
        target = safe_target(entry["path"])
        if target.stat().st_size != entry["bytes"]:
            fail(f"taille incorrecte: {entry['path']}")
        if sha256_file(target) != entry["sha256"]:
            fail(f"manifeste incorrect: {entry['path']}")
    print("[OK] manifeste principal")
    return manifest


def verify_job_manifests() -> int:
    root = ROOT / "resultats" / "real_science_max"
    count = 0
    for manifest_path in sorted(root.glob("*/job_manifest.json")):
        job_dir = manifest_path.parent
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for filename, expected in manifest.items():
            target = job_dir / filename
            if not target.is_file():
                fail(f"sortie de job absente: {target.relative_to(ROOT)}")
            if target.stat().st_size != expected["bytes"]:
                fail(f"taille de job incorrecte: {target.relative_to(ROOT)}")
            if sha256_file(target) != expected["sha256"]:
                fail(f"empreinte de job incorrecte: {target.relative_to(ROOT)}")
        count += 1
    if count != 25:
        fail(f"25 manifestes de job attendus, {count} trouvés")
    print(f"[OK] {count} manifestes de calcul")
    return count


def verify_analysis_manifest() -> None:
    root = ROOT / "resultats" / "real_science_max" / "analysis"
    manifest = json.loads((root / "analysis_manifest.json").read_text(encoding="utf-8"))
    for relative, expected in manifest.items():
        target = root / relative
        if not target.is_file():
            fail(f"sortie d'analyse absente: {relative}")
        if target.stat().st_size != expected["bytes"]:
            fail(f"taille d'analyse incorrecte: {relative}")
        if sha256_file(target) != expected["sha256"]:
            fail(f"empreinte d'analyse incorrecte: {relative}")
    print(f"[OK] {len(manifest)} sorties d'analyse")


def verify_archives(manifest: dict) -> None:
    for relative in [
        "documents/Architecture_historique_du_Systeme_solaire_ORI-C_revue.docx",
        "distribution/oric_solar_history-0.2.0-py3-none-any.whl",
    ]:
        with zipfile.ZipFile(ROOT / relative) as archive:
            damaged = archive.testzip()
        if damaged is not None:
            fail(f"archive corrompue: {relative}, entrée {damaged}")
    git = shutil.which("git")
    if git:
        bundle = ROOT / "git" / "ORI-C_Systeme_solaire_tests.bundle"
        heads = subprocess.check_output(
            [git, "bundle", "list-heads", str(bundle)],
            text=True,
        )
        if manifest["source_git_commit"] not in heads:
            fail("le bundle Git ne contient pas le commit source")
    print("[OK] roue, document et bundle Git")


def main() -> None:
    count = verify_checksums()
    manifest = verify_main_manifest(count)
    verify_job_manifests()
    verify_analysis_manifest()
    verify_archives(manifest)
    print("PAQUET SCIENTIFIQUE VALIDE")


if __name__ == "__main__":
    main()
