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


def write_manifest(root: Path) -> Path:
    excluded_names = {"MANIFEST.sha256"}
    lines = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if path.name in excluded_names or "__pycache__" in path.parts:
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.relative_to(root).as_posix()}")
    manifest = root / "MANIFEST.sha256"
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


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
