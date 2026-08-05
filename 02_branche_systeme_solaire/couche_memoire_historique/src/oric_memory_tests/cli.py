from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import matplotlib
import numpy
import pandas
import scipy

from .data import prepare_mpt_dataset
from .exoplanet import run_exoplanet_test
from .mpt import run_mpt_test
from .report import write_report


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_config(root: Path, config_path: str) -> dict:
    path = Path(config_path)
    if not path.is_absolute():
        path = root / path
    return json.loads(path.read_text(encoding="utf-8"))


MANIFEST_EXCLUDED_NAMES = {"MANIFEST.sha256"}
MANIFEST_EXCLUDED_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".pytest-tmp",
    ".mplconfig",
    "dist",
}


def manifest_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.name not in MANIFEST_EXCLUDED_NAMES
        and not any(part in MANIFEST_EXCLUDED_PARTS for part in path.relative_to(root).parts)
    )


def manifest_entries(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in manifest_files(root)
    }


def write_manifest(root: Path) -> Path:
    entries = manifest_entries(root)
    manifest = root / "MANIFEST.sha256"
    manifest.write_text(
        "".join(f"{digest}  {path}\n" for path, digest in entries.items()),
        encoding="utf-8",
        newline="\n",
    )
    return manifest


def read_manifest(root: Path) -> dict[str, str]:
    manifest = root / "MANIFEST.sha256"
    entries: dict[str, str] = {}
    for line_number, line in enumerate(
        manifest.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        digest, separator, relative = line.partition("  ")
        if (
            not separator
            or len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
            or not relative
        ):
            raise ValueError(
                f"Ligne invalide dans MANIFEST.sha256 à la ligne {line_number}"
            )
        if relative in entries:
            raise ValueError(f"Entrée dupliquée dans MANIFEST.sha256 : {relative}")
        entries[relative] = digest
    return entries


def verify_manifest(root: Path) -> int:
    expected = read_manifest(root)
    actual = manifest_entries(root)

    missing = sorted(set(expected) - set(actual))
    unlisted = sorted(set(actual) - set(expected))
    modified = sorted(
        path for path in set(expected) & set(actual) if expected[path] != actual[path]
    )

    if missing or unlisted or modified:
        details = []
        if missing:
            details.append("absents=" + ", ".join(missing))
        if unlisted:
            details.append("non_listés=" + ", ".join(unlisted))
        if modified:
            details.append("modifiés=" + ", ".join(modified))
        raise ValueError("Manifeste invalide : " + " ; ".join(details))

    return len(actual)


def run_all(root: Path, config: dict) -> dict:
    mpt = run_mpt_test(root, **config["mpt"])
    exoplanet = run_exoplanet_test(root, **config["exoplanet"])
    environment = {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": numpy.__version__,
        "pandas": pandas.__version__,
        "scipy": scipy.__version__,
        "matplotlib": matplotlib.__version__,
        "config": config,
    }
    (root / "results" / "environment.json").write_text(
        json.dumps(environment, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    report = write_report(root)
    manifest = write_manifest(root)
    summary = {
        "mpt": mpt,
        "exoplanet": exoplanet,
        "report": str(report.relative_to(root)),
        "manifest": str(manifest.relative_to(root)),
    }
    (root / "results" / "run_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_manifest(root)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Tests ORI-C de mémoire historique"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=project_root(),
        help="Racine du paquet",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare-data")
    prepare.add_argument(
        "--output", default="data/processed/mpt_lr04_la2004.csv"
    )

    for command in ("run-mpt", "run-exoplanet", "run-all"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--config", default="configs/primary.json")

    subparsers.add_parser("report")
    subparsers.add_parser("manifest")
    subparsers.add_parser("verify-manifest")
    return parser


def main() -> None:
    parser = build_parser()
    arguments = parser.parse_args()
    root = arguments.root.resolve()

    if arguments.command == "prepare-data":
        output = root / arguments.output
        _, quality = prepare_mpt_dataset(root / "data" / "raw", output)
        print(json.dumps(quality, indent=2, ensure_ascii=False))
        return
    if arguments.command == "report":
        print(write_report(root))
        return
    if arguments.command == "manifest":
        print(write_manifest(root))
        return
    if arguments.command == "verify-manifest":
        try:
            count = verify_manifest(root)
        except (OSError, ValueError) as exc:
            raise SystemExit(str(exc)) from exc
        print(f"Manifeste valide : {count} fichiers")
        return

    config = load_config(root, arguments.config)
    if arguments.command == "run-mpt":
        print(json.dumps(run_mpt_test(root, **config["mpt"]), indent=2))
    elif arguments.command == "run-exoplanet":
        print(
            json.dumps(
                run_exoplanet_test(root, **config["exoplanet"]), indent=2
            )
        )
    else:
        print(json.dumps(run_all(root, config), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
