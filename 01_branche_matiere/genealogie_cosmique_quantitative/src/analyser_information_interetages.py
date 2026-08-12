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
from functools import lru_cache
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


def _nmi_from_joint_counts(joint: np.ndarray) -> float:
    n = float(joint.sum())
    if n <= 0:
        return 0.0
    left = joint.sum(axis=1)
    right = joint.sum(axis=0)
    positive_left = left[left > 0] / n
    entropy = -float(np.sum(positive_left * np.log2(positive_left)))
    if entropy <= 0:
        return 0.0
    rows, cols = np.nonzero(joint)
    values = joint[rows, cols].astype(float)
    mi = float(np.sum((values / n) * np.log2((values * n) / (left[rows] * right[cols]))))
    return mi / entropy


def publication_robustness(
    types: list[str], hosts: list[str], references: list[str], observed: float, bootstrap_repeats: int = 1000
) -> dict[str, object]:
    type_levels = sorted(set(types))
    host_levels = sorted(set(hosts))
    type_index = {value: i for i, value in enumerate(type_levels)}
    host_index = {value: i for i, value in enumerate(host_levels)}
    refs = sorted(set(references))
    ref_index = {value: i for i, value in enumerate(refs)}

    cubes = np.zeros((len(refs), len(type_levels), len(host_levels)), dtype=np.int64)
    for left, right, reference in zip(types, hosts, references):
        cubes[ref_index[reference], type_index[left], host_index[right]] += 1
    total = cubes.sum(axis=0)
    sizes = cubes.sum(axis=(1, 2))

    loo = []
    for i, reference in enumerate(refs):
        joint = total - cubes[i]
        if joint.sum() < 2 or np.count_nonzero(joint.sum(axis=1)) < 2 or np.count_nonzero(joint.sum(axis=0)) < 2:
            continue
        value = _nmi_from_joint_counts(joint)
        loo.append({
            "reference": reference,
            "rows_removed": int(sizes[i]),
            "remaining_rows": int(joint.sum()),
            "normalized_I": value,
            "delta_vs_full": value - observed,
        })
    loo.sort(key=lambda row: (row["normalized_I"], row["reference"]))

    rng = np.random.default_rng(20260812)
    boot = np.empty(bootstrap_repeats, dtype=float)
    for repeat in range(bootstrap_repeats):
        multiplicities = np.bincount(rng.integers(0, len(refs), size=len(refs)), minlength=len(refs))
        joint = np.tensordot(multiplicities, cubes, axes=(0, 0))
        boot[repeat] = _nmi_from_joint_counts(joint)

    order = np.argsort(-sizes, kind="stable")
    largest_i = int(order[0])
    return {
        "leave_one_publication_out": {
            "runs": len(loo),
            "min_normalized_I": float(min(row["normalized_I"] for row in loo)) if loo else None,
            "median_normalized_I": float(np.median([row["normalized_I"] for row in loo])) if loo else None,
            "max_normalized_I": float(max(row["normalized_I"] for row in loo)) if loo else None,
            "most_reducing_publications": loo[:5],
            "most_increasing_publications": list(reversed(loo[-5:])),
        },
        "publication_cluster_bootstrap": {
            "repeats": bootstrap_repeats,
            "seed": 20260812,
            "q025": float(np.quantile(boot, 0.025)),
            "median": float(np.median(boot)),
            "q975": float(np.quantile(boot, 0.975)),
        },
        "sampling_concentration": {
            "largest_publication": refs[largest_i],
            "largest_publication_rows": int(sizes[largest_i]),
            "largest_publication_fraction": float(sizes[largest_i] / len(types)),
            "top5_publication_fraction": float(sizes[order[:5]].sum() / len(types)),
        },
    }

def analyse_table(path: Path, repeats: int = 2000) -> dict[str, object]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = [row for row in csv.DictReader(stream) if row.get("Type") and row.get("Source")]
    types = [row["Type"] for row in rows]
    hosts = [row["Source"] for row in rows]
    references = [row.get("Reference", "") for row in rows]
    observed = normalized_mutual_information(types, hosts)
    rng = np.random.default_rng(20260812)

    # Même test de permutation et même seed que la version initiale, mais les
    # NMI sont calculées depuis des tables de contingence NumPy. Cela évite de
    # reconstruire des Counter Python sur >10 000 grains à chaque permutation.
    type_levels = sorted(set(types))
    host_levels = sorted(set(hosts))
    type_lookup = {value: index for index, value in enumerate(type_levels)}
    host_lookup = {value: index for index, value in enumerate(host_levels)}
    type_codes = np.asarray([type_lookup[value] for value in types], dtype=np.int64)
    host_codes = np.asarray([host_lookup[value] for value in hosts], dtype=np.int64)
    joint_size = len(type_levels) * len(host_levels)

    def nmi_codes(left_codes: np.ndarray) -> float:
        joint = np.bincount(
            left_codes * len(host_levels) + host_codes,
            minlength=joint_size,
        ).reshape(len(type_levels), len(host_levels))
        return _nmi_from_joint_counts(joint)

    reference_indices: dict[str, np.ndarray] = {}
    grouped: dict[str, list[int]] = {}
    for index, reference in enumerate(references):
        grouped.setdefault(reference, []).append(index)
    for reference, indices in grouped.items():
        reference_indices[reference] = np.asarray(indices, dtype=np.int64)

    global_null = np.empty(repeats, dtype=float)
    stratified_null = np.empty(repeats, dtype=float)
    for repeat in range(repeats):
        global_null[repeat] = nmi_codes(rng.permutation(type_codes))
        shuffled = type_codes.copy()
        for indices in reference_indices.values():
            shuffled[indices] = rng.permutation(type_codes[indices])
        stratified_null[repeat] = nmi_codes(shuffled)

    global_p = float((1 + np.sum(global_null >= observed)) / (repeats + 1))
    stratified_p = float((1 + np.sum(stratified_null >= observed)) / (repeats + 1))
    robustness = publication_robustness(types, hosts, references, observed)
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
        "publication_robustness": robustness,
        "status": "association_survives_publication_control" if stratified_p < 0.05 else "association_not_separable_from_publication_sampling",
    }


@lru_cache(maxsize=4)
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
            "les analyses leave-one-publication-out et bootstrap par publication quantifient la dépendance à la composition du corpus sans créer de nouvelles observations",
            "cette mesure n'est pas une courbe complète étoile-grain-disque-corps-planète"
        ],
    }


def write_output(root: Path, output: Path) -> dict[str, object]:
    result = analyse(root)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return result
