#!/usr/bin/env python3
"""Build a deterministic, self-verifying package for the maximal science run."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import stat
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any

import pandas as pd


FIXED_TIME = (2026, 7, 29, 20, 0, 0)
PACKAGE_NAME = "ORI-C_Systeme_solaire_validation_scientifique_maximale"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _git(repo: Path, *arguments: str) -> str:
    return subprocess.check_output(
        ["git", *arguments],
        cwd=repo,
        text=True,
    ).strip()


def _copy_tracked_repository(repo: Path, destination: Path) -> None:
    destination.mkdir(parents=True)
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=repo)
    for encoded in raw.split(b"\0"):
        if not encoded:
            continue
        relative = Path(encoded.decode("utf-8"))
        source = repo / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def _copy_results(source: Path, destination: Path) -> None:
    def ignore(directory: str, names: list[str]) -> set[str]:
        del directory
        return {
            name
            for name in names
            if name.startswith(".") or name in {"__pycache__", ".pytest_cache"}
        }

    shutil.copytree(source, destination, ignore=ignore)


def _verifier_source() -> str:
    return """#!/usr/bin/env python3
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
"""


def _top_documents(
    package: Path,
    commit: str,
    summary: dict[str, Any],
    acceptance: pd.DataFrame,
) -> None:
    passed = int(summary["acceptance_passed"])
    failed = int(summary["acceptance_failed"])
    status = "entièrement réussi" if failed == 0 else "partiellement réussi"
    acceptance_view = acceptance.copy()
    acceptance_view["statut"] = acceptance_view["passed"].map({True: "RÉUSSI", False: "ÉCHEC"})
    for column in ["observed", "threshold"]:
        acceptance_view[column] = acceptance_view[column].map(_format_acceptance_value)
    acceptance_table = acceptance_view[
        ["test", "observed", "operator", "threshold", "statut"]
    ].to_markdown(index=False, disable_numparse=True)

    (package / "LISEZ_MOI.md").write_text(
        "\n".join(
            [
                "# ORI-C — validation scientifique maximale du Système solaire",
                "",
                f"Ce paquet contient 25 calculs N-corps et contrôles numériques issus du commit `{commit}`.",
                "",
                f"Le protocole préenregistré est **{status}** : {passed} critères réussis et {failed} échoués.",
                "",
                "Commencez par :",
                "",
                "```bash",
                "python scripts/verifier_paquet.py",
                "```",
                "",
                "Le rapport scientifique complet se trouve dans :",
                "",
                "`resultats/real_science_max/analysis/SCIENTIFIC_VALIDATION_REPORT.md`",
                "",
                "La procédure de recalcul se trouve dans `REPRODUCTION.md`.",
                "",
                "Les sorties incluent la trajectoire terrestre, les invariants, les échantillons de tous "
                "les corps, les comparaisons JPL Horizons et La2010, les spectres multitaper, les "
                "contrefactuels et l’ensemble de sensibilité.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (package / "STATUT_SCIENTIFIQUE.md").write_text(
        "\n".join(
            [
                "# Statut scientifique",
                "",
                "## Critères préenregistrés",
                "",
                acceptance_table,
                "",
                "## Portée",
                "",
                "Les résultats constituent des preuves numériques et astronomiques réelles à "
                "l’intérieur d’un modèle N-corps explicite. Le départ est fondé sur JPL Horizons "
                "DE441 et les sorties sont confrontées aux références indépendantes Horizons et "
                "La2010.",
                "",
                "Ils ne constituent pas encore une validation empirique générale d’ORI-C. Le modèle "
                "réduit ne résout pas la Lune, la rotation terrestre, le J2 solaire, les marées, "
                "l’obliquité dynamique ni une archive géologique hors échantillon.",
                "",
                "La conclusion autorisée est une validation astronomique et numérique du mécanisme "
                "réduit, avec les échecs éventuels conservés dans le tableau ci-dessus.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (package / "REPRODUCTION.md").write_text(
        "\n".join(
            [
                "# Reproduction",
                "",
                "## Vérification immédiate",
                "",
                "```bash",
                "python scripts/verifier_paquet.py",
                "```",
                "",
                "## Refaire seulement l’analyse",
                "",
                "```bash",
                "python -m venv .venv-science",
                "source .venv-science/bin/activate",
                "python -m pip install -r code/ORI-C_Systeme_solaire_tests/requirements.science.lock.txt",
                "python -m pip install --no-build-isolation --no-deps -e code/ORI-C_Systeme_solaire_tests",
                "cd code/ORI-C_Systeme_solaire_tests",
                "python scripts/analyze_real_science_suite.py \\",
                "  --config configs/real_science_max.yaml \\",
                "  --runs ../../../resultats/real_science_max \\",
                "  --output ../../../analyse_recalculee",
                "```",
                "",
                "## Refaire les 25 calculs",
                "",
                "Depuis le dossier de code et dans le même environnement :",
                "",
                "```bash",
                "python scripts/run_real_science_suite.py \\",
                "  --config configs/real_science_max.yaml \\",
                "  --overwrite",
                "python scripts/analyze_real_science_suite.py \\",
                "  --config configs/real_science_max.yaml",
                "```",
                "",
                "L’exécution utilise jusqu’à neuf cœurs. Sa durée dépend fortement du processeur. "
                "Les jobs intacts peuvent être conservés avec `--resume` après une interruption.",
                "",
                "Les données JPL et IMCCE sont figées dans `data/`. Les scripts d’acquisition "
                "permettent aussi de refaire les requêtes réseau.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (package / "VALIDATION_FINALE.md").write_text(
        "\n".join(
            [
                "# Validation finale",
                "",
                f"- commit source : `{commit}`",
                f"- critères réussis : {passed}",
                f"- critères échoués : {failed}",
                f"- durée de la trajectoire principale : {summary['long_baseline_completed_years'] / 1e6:.1f} Myr",
                f"- temps de calcul cumulé : {summary['total_computation_seconds'] / 3600:.3f} heures-cœur",
                f"- erreur initiale d’excentricité contre La2010 : {summary['initial_eccentricity_abs_error']:.3g}",
                "- manifestes de jobs : 25",
                f"- intégrité des jobs avant assemblage : {summary['all_job_hashes_valid']}",
                "",
                "Les tests unitaires, Ruff, les deux versions REBOUND prises en charge, les "
                "manifestes internes et l’archive finale sont contrôlés séparément avant livraison.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    scripts = package / "scripts"
    scripts.mkdir(exist_ok=True)
    verifier = scripts / "verifier_paquet.py"
    verifier.write_text(_verifier_source(), encoding="utf-8")
    verifier.chmod(0o755)


def _format_acceptance_value(value: Any) -> str:
    """Render mixed boolean/numeric acceptance fields without lossy coercion."""
    text = str(value)
    if text in {"True", "False"}:
        return text
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return text


def _archive_info(name: str, mode: int, directory: bool = False) -> zipfile.ZipInfo:
    if directory and not name.endswith("/"):
        name += "/"
    info = zipfile.ZipInfo(name, FIXED_TIME)
    info.create_system = 3
    info.compress_type = zipfile.ZIP_DEFLATED
    file_type = stat.S_IFDIR if directory else stat.S_IFREG
    info.external_attr = ((file_type | mode) & 0xFFFF) << 16
    if directory:
        info.external_attr |= 0x10
    return info


def _deterministic_zip(source: Path, output: Path) -> str:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        output,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        archive.writestr(
            _archive_info(source.name, 0o755, directory=True),
            b"",
        )
        for path in sorted(source.rglob("*")):
            relative = path.relative_to(source).as_posix()
            archive_name = f"{source.name}/{relative}"
            if path.is_dir():
                archive.writestr(
                    _archive_info(archive_name, 0o755, directory=True),
                    b"",
                )
            elif path.is_file():
                executable = (
                    path.suffix in {".sh", ".py"} or "scripts" in path.relative_to(source).parts
                )
                mode = 0o755 if executable else 0o644
                archive.writestr(
                    _archive_info(archive_name, mode),
                    path.read_bytes(),
                )
    digest = _sha256(output)
    output.with_name(output.name + ".sha256").write_text(
        f"{digest}  {output.name}\n",
        encoding="utf-8",
    )
    return digest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--output-zip", type=Path, required=True)
    args = parser.parse_args()

    repo = args.repo.resolve()
    runs = args.runs.resolve()
    wheel = args.wheel.resolve()
    pdf = args.pdf.resolve()
    package = args.output_dir.resolve()
    output_zip = args.output_zip.resolve()
    if package.name != PACKAGE_NAME:
        raise SystemExit(f"Le dossier final doit s’appeler {PACKAGE_NAME}")
    analysis = runs / "analysis"
    required = [
        analysis / "analysis_summary.json",
        analysis / "acceptance_tests.csv",
        analysis / "analysis_manifest.json",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise SystemExit(f"Analyse incomplète: {missing}")
    if not wheel.is_file() or not pdf.is_file():
        raise SystemExit("Roue Python ou PDF absent")
    if _git(repo, "status", "--porcelain"):
        raise SystemExit("Le dépôt doit être propre avant l’assemblage")

    commit = _git(repo, "rev-parse", "HEAD")
    summary = json.loads((analysis / "analysis_summary.json").read_text(encoding="utf-8"))
    acceptance = pd.read_csv(analysis / "acceptance_tests.csv")
    if package.exists():
        shutil.rmtree(package)
    package.mkdir(parents=True)

    _copy_tracked_repository(
        repo,
        package / "code" / "ORI-C_Systeme_solaire_tests",
    )
    _copy_results(runs, package / "resultats" / "real_science_max")
    documents = package / "documents"
    documents.mkdir()
    docx = repo / "docs" / "source" / "Architecture_historique_du_Systeme_solaire_ORI-C_revue.docx"
    shutil.copy2(docx, documents / docx.name)
    shutil.copy2(pdf, documents / pdf.name)
    distribution = package / "distribution"
    distribution.mkdir()
    shutil.copy2(wheel, distribution / wheel.name)
    git_dir = package / "git"
    git_dir.mkdir()
    subprocess.run(
        [
            "git",
            "bundle",
            "create",
            str(git_dir / "ORI-C_Systeme_solaire_tests.bundle"),
            "HEAD",
        ],
        cwd=repo,
        check=True,
    )
    _top_documents(package, commit, summary, acceptance)

    entries = []
    for path in sorted(package.rglob("*")):
        if not path.is_file() or path.name in {"MANIFESTE.json", "SHA256SUMS.txt"}:
            continue
        entries.append(
            {
                "path": path.relative_to(package).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    manifest = {
        "package": PACKAGE_NAME,
        "source_git_commit": commit,
        "science_suite": "real_science_max",
        "job_count": 25,
        "acceptance_passed": int(summary["acceptance_passed"]),
        "acceptance_failed": int(summary["acceptance_failed"]),
        "files": entries,
    }
    _write_json(package / "MANIFESTE.json", manifest)
    checksum_paths = [
        path
        for path in sorted(package.rglob("*"))
        if path.is_file() and path.name != "SHA256SUMS.txt"
    ]
    (package / "SHA256SUMS.txt").write_text(
        "".join(
            f"{_sha256(path)}  {path.relative_to(package).as_posix()}\n" for path in checksum_paths
        ),
        encoding="utf-8",
    )

    subprocess.run(
        [sys.executable, str(package / "scripts" / "verifier_paquet.py")],
        check=True,
    )
    digest = _deterministic_zip(package, output_zip)
    with zipfile.ZipFile(output_zip) as archive:
        damaged = archive.testzip()
    if damaged is not None:
        raise RuntimeError(f"Archive ZIP corrompue à l’entrée {damaged}")
    print(f"{digest}  {output_zip.name}")


if __name__ == "__main__":
    main()
