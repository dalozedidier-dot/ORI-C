from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

from .archives import (
    compare_archive_to_forcing,
    load_archive,
    lomb_scargle_archive,
    make_synthetic_archive,
)
from .config import ConfigError, load_config
from .experiment import run_experiment


def _doctor() -> int:
    checks = {
        "numpy": importlib.util.find_spec("numpy") is not None,
        "scipy": importlib.util.find_spec("scipy") is not None,
        "pandas": importlib.util.find_spec("pandas") is not None,
        "matplotlib": importlib.util.find_spec("matplotlib") is not None,
        "yaml": importlib.util.find_spec("yaml") is not None,
        "rebound (optionnel)": importlib.util.find_spec("rebound") is not None,
        "reboundx (science, optionnel)": importlib.util.find_spec("reboundx") is not None,
    }
    for name, ok in checks.items():
        print(f"{'OK' if ok else 'ABSENT':>6}  {name}")
    return 0 if all(v for k, v in checks.items() if "optionnel" not in k) else 1


def _make_demo_archive(args: argparse.Namespace) -> int:
    forcing_path = Path(args.forcing) if args.forcing else None
    if forcing_path and forcing_path.exists():
        forcing = pd.read_csv(forcing_path)
    else:
        times = pd.Series(range(0, 1_200_001, 1000), dtype=float)
        import numpy as np

        forcing = pd.DataFrame(
            {
                "time_years": times,
                "insolation_w_m2": 500
                + 20 * np.sin(2 * np.pi * times / 405_000)
                + 8 * np.sin(2 * np.pi * times / 100_000),
            }
        )
    archive = make_synthetic_archive(
        forcing,
        sampling_step_years=float(args.sampling_step),
        age_jitter_years=float(args.age_jitter),
        noise_std=float(args.noise),
        seed=int(args.seed),
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    archive.to_csv(output, index=False)
    print(output)
    return 0


def _compare_archive(args: argparse.Namespace) -> int:
    forcing = pd.read_csv(args.forcing)
    archive = load_archive(args.archive)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    spectrum = lomb_scargle_archive(
        archive,
        min_period_years=float(args.min_period),
        max_period_years=float(args.max_period),
    )
    spectrum.to_csv(output / "archive_lomb_scargle.csv", index=False)
    metrics = compare_archive_to_forcing(forcing, archive)
    (output / "archive_comparison.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="oric-solar-history")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="Vérifier l'environnement")

    check = sub.add_parser("check-config", help="Valider un YAML")
    check.add_argument("--config", required=True)

    run = sub.add_parser("run", help="Exécuter une expérience")
    run.add_argument("--config", required=True)
    run.add_argument("--overwrite", action="store_true")

    demo = sub.add_parser("make-demo-archive", help="Créer une archive synthétique")
    demo.add_argument("--forcing")
    demo.add_argument("--output", required=True)
    demo.add_argument("--sampling-step", type=float, default=5000)
    demo.add_argument("--age-jitter", type=float, default=1200)
    demo.add_argument("--noise", type=float, default=0.25)
    demo.add_argument("--seed", type=int, default=20260729)

    compare = sub.add_parser("compare-archive", help="Comparer une archive à une insolation")
    compare.add_argument("--forcing", required=True)
    compare.add_argument("--archive", required=True)
    compare.add_argument("--output", required=True)
    compare.add_argument("--min-period", type=float, default=18000)
    compare.add_argument("--max-period", type=float, default=1000000)
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            code = _doctor()
        elif args.command == "check-config":
            config = load_config(args.config)
            print(f"Configuration valide: {config['experiment']['name']}")
            code = 0
        elif args.command == "run":
            config = load_config(args.config)
            output = run_experiment(config, overwrite=args.overwrite)
            print(output)
            code = 0
        elif args.command == "make-demo-archive":
            code = _make_demo_archive(args)
        elif args.command == "compare-archive":
            code = _compare_archive(args)
        else:
            parser.error("Commande inconnue")
            return
    except (ConfigError, ValueError, RuntimeError, FileExistsError, KeyError) as exc:
        print(f"ERREUR: {exc}", file=sys.stderr)
        code = 2
    raise SystemExit(code)
