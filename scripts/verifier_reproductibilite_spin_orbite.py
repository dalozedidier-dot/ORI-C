#!/usr/bin/env python3
"""Vérifie la reproductibilité de la couche spin-orbite selon son régime dynamique.

Le témoin avec couple lunaire effectif reste régulier sur 20 Ma et est comparé
point par point à tolérance serrée. L'ablation lunaire devient fortement sensible
aux derniers bits sur les longues fenêtres : elle est comparée point par point
jusqu'à 2 Ma, puis par les statistiques canoniques de ``summary.json`` sur 20 Ma.
Les rapports Markdown, figures, empreintes et le sous-dossier ``viabilite`` ne
font pas partie des sorties de ``run_spin_orbit.py`` ; la viabilité possède son
propre recalcul dans ``verifier_reproductibilite_formalismes.py``.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

TIGHT_REL = 1e-10
TIGHT_ABS = 1e-10
SUMMARY_REL = 2e-6
SUMMARY_ABS = 2e-5
NO_MOON_POINTWISE_HORIZON_YEARS = 2_000_000.0


def _compare_number(a: float, b: float, *, rel: float, abs_: float, where: str, errors: list[str]) -> None:
    if not math.isclose(a, b, rel_tol=rel, abs_tol=abs_):
        d = abs(a - b)
        den = max(abs(a), abs(b), abs_)
        errors.append(f"{where}: {a!r} contre {b!r} (écart absolu {d:.3e}, écart relatif {d/den:.3e})")


def _compare_json(a, b, *, rel: float, abs_: float, where: str, errors: list[str], counter: list[int]) -> None:
    if isinstance(a, bool) or isinstance(b, bool):
        if a != b:
            errors.append(f"{where}: {a!r} contre {b!r}")
        return
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if isinstance(a, int) and isinstance(b, int):
            if a != b:
                errors.append(f"{where}: entier attendu {a}, obtenu {b}")
            return
        counter[0] += 1
        _compare_number(float(a), float(b), rel=rel, abs_=abs_, where=where, errors=errors)
        return
    if type(a) is not type(b):
        errors.append(f"{where}: type {type(a).__name__} contre {type(b).__name__}")
        return
    if isinstance(a, dict):
        if set(a) != set(b):
            errors.append(f"{where}: clés différentes")
        for key in sorted(set(a) & set(b), key=str):
            _compare_json(a[key], b[key], rel=rel, abs_=abs_, where=f"{where}.{key}", errors=errors, counter=counter)
        return
    if isinstance(a, list):
        if len(a) != len(b):
            errors.append(f"{where}: longueur {len(a)} contre {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            _compare_json(x, y, rel=rel, abs_=abs_, where=f"{where}[{i}]", errors=errors, counter=counter)
        return
    if a != b:
        errors.append(f"{where}: {a!r} contre {b!r}")


def compare_json_file(ref: Path, cand: Path, *, rel: float, abs_: float, errors: list[str], counter: list[int]) -> None:
    _compare_json(
        json.loads(ref.read_text(encoding="utf-8")),
        json.loads(cand.read_text(encoding="utf-8")),
        rel=rel,
        abs_=abs_,
        where=ref.name,
        errors=errors,
        counter=counter,
    )


def compare_csv_file(ref: Path, cand: Path, *, rel: float, abs_: float, errors: list[str], counter: list[int]) -> None:
    with ref.open(encoding="utf-8", newline="") as h:
        rr = list(csv.reader(h))
    with cand.open(encoding="utf-8", newline="") as h:
        cc = list(csv.reader(h))
    if len(rr) != len(cc):
        errors.append(f"{ref.name}: nombre de lignes {len(rr)} contre {len(cc)}")
        return
    for i, (r, c) in enumerate(zip(rr, cc), start=1):
        if len(r) != len(c):
            errors.append(f"{ref.name}[{i}]: nombre de colonnes différent")
            return
        for j, (a, b) in enumerate(zip(r, c), start=1):
            if a == b:
                try:
                    float(a)
                    counter[0] += 1
                except ValueError:
                    pass
                continue
            try:
                af, bf = float(a), float(b)
            except ValueError:
                errors.append(f"{ref.name}[{i}][{j}]: {a!r} contre {b!r}")
                continue
            counter[0] += 1
            _compare_number(af, bf, rel=rel, abs_=abs_, where=f"{ref.name}[{i}][{j}]", errors=errors)


def compare_no_moon_first_2myr(ref: Path, cand: Path, *, errors: list[str], counter: list[int]) -> None:
    with ref.open(encoding="utf-8", newline="") as h:
        rr = list(csv.reader(h))
    with cand.open(encoding="utf-8", newline="") as h:
        cc = list(csv.reader(h))
    if not rr or not cc or rr[0] != cc[0]:
        errors.append("baseline_no_moon_20myr.csv: en-tête différent")
        return
    try:
        elapsed_col = rr[0].index("elapsed_years")
    except ValueError:
        errors.append("baseline_no_moon_20myr.csv: colonne elapsed_years absente")
        return
    ref_rows = [rr[0]] + [row for row in rr[1:] if float(row[elapsed_col]) <= NO_MOON_POINTWISE_HORIZON_YEARS]
    cand_rows = [cc[0]] + [row for row in cc[1:] if float(row[elapsed_col]) <= NO_MOON_POINTWISE_HORIZON_YEARS]
    if len(ref_rows) != len(cand_rows):
        errors.append("baseline_no_moon_20myr.csv: nombre de lignes <=2 Ma différent")
        return
    for i, (r, c) in enumerate(zip(ref_rows[1:], cand_rows[1:]), start=2):
        for j, (a, b) in enumerate(zip(r, c), start=1):
            if a == b:
                try:
                    float(a)
                    counter[0] += 1
                except ValueError:
                    pass
                continue
            try:
                af, bf = float(a), float(b)
            except ValueError:
                errors.append(f"baseline_no_moon_20myr.csv[{i}][{j}]: {a!r} contre {b!r}")
                continue
            counter[0] += 1
            _compare_number(af, bf, rel=TIGHT_REL, abs_=TIGHT_ABS, where=f"baseline_no_moon_20myr.csv[{i}][{j}]", errors=errors)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference", required=True, type=Path)
    ap.add_argument("--candidate", required=True, type=Path)
    args = ap.parse_args()
    if not args.reference.is_dir() or not args.candidate.is_dir():
        print("Dossier de référence ou candidat absent", file=sys.stderr)
        return 2

    required = [
        "baseline_with_moon_20myr.csv",
        "baseline_no_moon_20myr.csv",
        "interventions_spin_insolation.csv",
        "validation_la2004.csv",
        "convergence.json",
        "summary.json",
    ]
    missing = [name for name in required if not (args.reference / name).is_file() or not (args.candidate / name).is_file()]
    if missing:
        print("Sorties requises absentes : " + ", ".join(missing), file=sys.stderr)
        return 1

    errors: list[str] = []
    tight_count = [0]
    summary_count = [0]

    compare_csv_file(args.reference / "baseline_with_moon_20myr.csv", args.candidate / "baseline_with_moon_20myr.csv", rel=TIGHT_REL, abs_=TIGHT_ABS, errors=errors, counter=tight_count)
    compare_csv_file(args.reference / "validation_la2004.csv", args.candidate / "validation_la2004.csv", rel=TIGHT_REL, abs_=TIGHT_ABS, errors=errors, counter=tight_count)
    compare_json_file(args.reference / "convergence.json", args.candidate / "convergence.json", rel=TIGHT_REL, abs_=TIGHT_ABS, errors=errors, counter=tight_count)
    compare_no_moon_first_2myr(args.reference / "baseline_no_moon_20myr.csv", args.candidate / "baseline_no_moon_20myr.csv", errors=errors, counter=tight_count)

    # Les rapports d'effet utilisent comme dénominateur une dispersion d'ensemble
    # ~1e-9 : une différence de quelques derniers bits sur ce plancher déplace le
    # rapport d'environ 1 ppm sans modifier l'effet physique. On compare donc ces
    # agrégats et les statistiques 20 Ma avec une tolérance relative dédiée.
    compare_csv_file(args.reference / "interventions_spin_insolation.csv", args.candidate / "interventions_spin_insolation.csv", rel=SUMMARY_REL, abs_=SUMMARY_ABS, errors=errors, counter=summary_count)
    compare_json_file(args.reference / "summary.json", args.candidate / "summary.json", rel=SUMMARY_REL, abs_=SUMMARY_ABS, errors=errors, counter=summary_count)

    if errors:
        print("Reproductibilité spin-orbite refusée :")
        for err in errors[:60]:
            print("-", err)
        if len(errors) > 60:
            print(f"- ... {len(errors)-60} autres différences")
        return 1

    print("Reproductibilité spin-orbite validée")
    print(f"- comparaison point par point stricte : {tight_count[0]} nombres, rel={TIGHT_REL:g}, abs={TIGHT_ABS:g}")
    print(f"- ablation lunaire point par point : 0-{NO_MOON_POINTWISE_HORIZON_YEARS/1e6:g} Ma")
    print(f"- agrégats 20 Ma et rapports effet/plancher : {summary_count[0]} nombres, rel={SUMMARY_REL:g}, abs={SUMMARY_ABS:g}")
    print("- viabilité exclue ici : recalculée séparément par le workflow des formalismes externes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
