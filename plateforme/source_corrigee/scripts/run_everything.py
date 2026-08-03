from __future__ import annotations

import argparse
from pathlib import Path

from oric_full.pipeline import bootstrap_workspace


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialiser et exécuter la totalité du programme ORI-C")
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--oric-root", type=Path, default=None)
    parser.add_argument("--synthetic", action="store_true")
    parser.add_argument("--seed", type=int, default=20260801)
    parser.add_argument("--max-priority", type=int, choices=[1, 2, 3], default=None)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = bootstrap_workspace(
        root,
        args.workspace,
        seed=args.seed,
        synthetic=args.synthetic,
        oric_root=args.oric_root,
        max_priority=args.max_priority,
    )
    print(f"Espace créé: {result.workspace}")
    print(f"Entrées: {result.tests}; schémas: {result.datasets}; protocoles: {result.protocols}")
    print(result.counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
