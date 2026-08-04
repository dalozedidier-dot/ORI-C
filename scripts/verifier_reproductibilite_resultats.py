#!/usr/bin/env python3
"""Compare deux dossiers de résultats avec une tolérance numérique explicite.

Les fichiers non JSON restent comparés octet par octet. Les structures JSON,
les clés, les listes et les valeurs non numériques doivent être strictement
identiques. Seuls les flottants bénéficient d'une tolérance destinée à absorber
les écarts d'arrondi entre BLAS, bibliothèques et versions mineures de Python.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ComparisonState:
    numbers_compared: int = 0
    maximum_absolute_difference: float = 0.0
    maximum_relative_difference: float = 0.0
    maximum_difference_path: str = ""


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _compare_values(
    reference: Any,
    candidate: Any,
    *,
    location: str,
    relative_tolerance: float,
    absolute_tolerance: float,
    state: ComparisonState,
    errors: list[str],
) -> None:
    if _is_number(reference) and _is_number(candidate):
        if isinstance(reference, int) and isinstance(candidate, int):
            if reference != candidate:
                errors.append(f"{location}: entier attendu {reference}, obtenu {candidate}")
            return

        reference_float = float(reference)
        candidate_float = float(candidate)
        state.numbers_compared += 1

        if not (math.isfinite(reference_float) and math.isfinite(candidate_float)):
            if reference_float != candidate_float:
                errors.append(
                    f"{location}: valeur non finie différente "
                    f"({reference_float!r} contre {candidate_float!r})"
                )
            return

        absolute_difference = abs(reference_float - candidate_float)
        denominator = max(abs(reference_float), abs(candidate_float), absolute_tolerance)
        relative_difference = absolute_difference / denominator
        if absolute_difference > state.maximum_absolute_difference:
            state.maximum_absolute_difference = absolute_difference
            state.maximum_relative_difference = relative_difference
            state.maximum_difference_path = location

        if not math.isclose(
            reference_float,
            candidate_float,
            rel_tol=relative_tolerance,
            abs_tol=absolute_tolerance,
        ):
            errors.append(
                f"{location}: {reference_float!r} contre {candidate_float!r} "
                f"(écart absolu {absolute_difference:.3e}, "
                f"écart relatif {relative_difference:.3e})"
            )
        return

    if type(reference) is not type(candidate):
        errors.append(
            f"{location}: type attendu {type(reference).__name__}, "
            f"obtenu {type(candidate).__name__}"
        )
        return

    if isinstance(reference, dict):
        reference_keys = set(reference)
        candidate_keys = set(candidate)
        missing = sorted(reference_keys - candidate_keys)
        unexpected = sorted(candidate_keys - reference_keys)
        if missing:
            errors.append(f"{location}: clés absentes {missing}")
        if unexpected:
            errors.append(f"{location}: clés inattendues {unexpected}")
        for key in sorted(reference_keys & candidate_keys, key=str):
            _compare_values(
                reference[key],
                candidate[key],
                location=f"{location}.{key}",
                relative_tolerance=relative_tolerance,
                absolute_tolerance=absolute_tolerance,
                state=state,
                errors=errors,
            )
        return

    if isinstance(reference, list):
        if len(reference) != len(candidate):
            errors.append(
                f"{location}: longueur attendue {len(reference)}, "
                f"obtenue {len(candidate)}"
            )
        for index, (reference_item, candidate_item) in enumerate(
            zip(reference, candidate, strict=False)
        ):
            _compare_values(
                reference_item,
                candidate_item,
                location=f"{location}[{index}]",
                relative_tolerance=relative_tolerance,
                absolute_tolerance=absolute_tolerance,
                state=state,
                errors=errors,
            )
        return

    if reference != candidate:
        errors.append(f"{location}: attendu {reference!r}, obtenu {candidate!r}")


def _relative_files(root: Path) -> set[Path]:
    return {
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def compare_directories(
    reference_dir: Path,
    candidate_dir: Path,
    *,
    relative_tolerance: float,
    absolute_tolerance: float,
) -> tuple[ComparisonState, list[str], int]:
    state = ComparisonState()
    errors: list[str] = []
    reference_files = _relative_files(reference_dir)
    candidate_files = _relative_files(candidate_dir)

    missing = sorted(reference_files - candidate_files)
    unexpected = sorted(candidate_files - reference_files)
    if missing:
        errors.append("Fichiers absents : " + ", ".join(map(str, missing)))
    if unexpected:
        errors.append("Fichiers inattendus : " + ", ".join(map(str, unexpected)))

    compared_files = 0
    for relative_path in sorted(reference_files & candidate_files):
        compared_files += 1
        reference_path = reference_dir / relative_path
        candidate_path = candidate_dir / relative_path
        if relative_path.suffix.lower() == ".json":
            try:
                reference_payload = json.loads(reference_path.read_text(encoding="utf-8"))
                candidate_payload = json.loads(candidate_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                errors.append(f"{relative_path}: JSON illisible : {exc}")
                continue
            _compare_values(
                reference_payload,
                candidate_payload,
                location=str(relative_path),
                relative_tolerance=relative_tolerance,
                absolute_tolerance=absolute_tolerance,
                state=state,
                errors=errors,
            )
        elif reference_path.read_bytes() != candidate_path.read_bytes():
            errors.append(f"{relative_path}: contenu non JSON différent")

    return state, errors, compared_files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--relative-tolerance", type=float, default=1e-8)
    parser.add_argument("--absolute-tolerance", type=float, default=1e-10)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.reference.is_dir():
        print(f"Dossier de référence introuvable : {args.reference}", file=sys.stderr)
        return 2
    if not args.candidate.is_dir():
        print(f"Dossier candidat introuvable : {args.candidate}", file=sys.stderr)
        return 2
    if args.relative_tolerance < 0 or args.absolute_tolerance < 0:
        print("Les tolérances doivent être positives ou nulles.", file=sys.stderr)
        return 2

    state, errors, compared_files = compare_directories(
        args.reference,
        args.candidate,
        relative_tolerance=args.relative_tolerance,
        absolute_tolerance=args.absolute_tolerance,
    )

    if errors:
        print("Reproductibilité refusée :")
        for error in errors[:50]:
            print(f"- {error}")
        if len(errors) > 50:
            print(f"- ... {len(errors) - 50} autres différences")
        return 1

    print(
        "Reproductibilité validée : "
        f"{compared_files} fichiers, {state.numbers_compared} nombres comparés, "
        f"tolérances rel={args.relative_tolerance:.0e} et abs={args.absolute_tolerance:.0e}."
    )
    if state.maximum_difference_path:
        print(
            "Écart maximal accepté : "
            f"{state.maximum_absolute_difference:.3e} en absolu "
            f"({state.maximum_relative_difference:.3e} en relatif) "
            f"dans {state.maximum_difference_path}."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
