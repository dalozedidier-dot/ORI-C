"""Mesure l'association inter-étages sur les mêmes grains publiés.

Chaque ligne relie une classe de source stellaire (Type) au corps hôte final
(Source). Le contrôle principal permute les types à l'intérieur de chaque
publication afin de ne pas transformer la stratégie d'échantillonnage d'une
étude en conservation cosmique.
"""
from __future__ import annotations

import csv
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np


def _entropy(values: list[str]) -> float:
    counts = Counter(values)
    n = len(values)
    return -sum((count / n) * math.log2(count / n) for count in counts.values())


def normalized_mutual_information(left: list[str], right: list[str]) -> float:
    n = len(left)
    joint = Counter(zip(left, right))
    lc, rc = Counter(left), Counter(right)
    mi = sum(
        (count / n) * math.log2((count * n) / (lc[lvalue] * rc[rvalue]))
        for (lvalue, rvalue), count in joint.items()
    )
    entropy = _entropy(left)
    return mi / entropy if entropy else 0.0


def analyse_table(path: Path, repeats: int = 2000) -> dict[str, object]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = [row for row in csv.DictReader(stream) if row.get("Type") and row.get("Source")]
    types = [row["Type"] for row in rows]
    hosts = [row["Source"] for row in rows]
    references = [row.get("Reference", "") for row in rows]
    observed = normalized_mutual_information(types, hosts)
    rng = np.random.default_rng(20260812)
    global_null = []
    stratified_null = []
    reference_indices: dict[str, list[int]] = {}
    for index, reference in enumerate(references):
        reference_indices.setdefault(reference, []).append(index)
    type_array = np.asarray(types, dtype=object)
    for _ in range(repeats):
        global_null.append(normalized_mutual_information(rng.permutation(type_array).tolist(), hosts))
        shuffled = type_array.copy()
        for indices in reference_indices.values():
            shuffled[indices] = rng.permutation(type_array[indices])
        stratified_null.append(normalized_mutual_information(shuffled.tolist(), hosts))
    global_p = (1 + sum(value >= observed for value in global_null)) / (repeats + 1)
    stratified_p = (1 + sum(value >= observed for value in stratified_null)) / (repeats + 1)
    return {
        "dataset": path.name,
        "same_carrier_rows": len(rows),
        "stellar_source_classes": len(set(types)),
        "final_host_bodies": len(set(hosts)),
        "publications": len(set(references)),
        "normalized_I_stellar_type_host": observed,
        "global_label_permutation_p": global_p,
        "publication_stratified_permutation_p": stratified_p,
        "publication_stratified_null_mean": float(np.mean(stratified_null)),
        "status": "association_survives_publication_control" if stratified_p < 0.05 else "association_not_separable_from_publication_sampling",
    }


def analyse(root: Path) -> dict[str, object]:
    data = root / "data_massives_reelles"
    results = [
        analyse_table(data / "PGD_SiC_PUBLISHED_SELECTED.csv"),
        analyse_table(data / "PGD_GRAPHITE_PUBLISHED_SELECTED.csv"),
    ]
    return {
        "schema": "oric.gc.interstage-information.v1",
        "analysis": "retrospective_same_grain_population_association",
        "stages": ["stellar_source_class", "presolar_grain", "meteorite_or_returned_sample_host"],
        "results": results,
        "verdict": "first_interstage_measurement_executed_but_no_conservation_claim_without_publication_robustness",
        "limits": [
            "le type stellaire et le corps hôte sont portés par la même ligne/grain, mais les grains ne sont pas suivis expérimentalement avant et après chaque étage",
            "la permutation dans chaque publication contrôle le ciblage d'échantillons et d'analyses propre à chaque étude",
            "cette mesure n'est pas une courbe complète étoile-grain-disque-corps-planète"
        ],
    }


def write_output(root: Path, output: Path) -> dict[str, object]:
    result = analyse(root)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result
