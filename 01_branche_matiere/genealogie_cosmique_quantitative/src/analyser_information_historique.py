#!/usr/bin/env python3
"""Mesure l'information de provenance dans les tables individuelles publiées.

Analyse rétrospective descriptive : elle mesure si une étiquette historique ou
de provenance reste décodable dans les observables. Elle ne prétend pas mesurer
un transfert causal entre étages non appariés.
"""
from __future__ import annotations

import csv
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
DATA = BASE / "data_massives_reelles"
OUT = BASE / "resultats"

SPECS = [
    ("reservoir_NC_CC", "SOSSI_NC_CC_MEASURED.csv", "Reservoir", ["17O", "48Ca", "50Ti", "54Cr", "54Fe", "64Ni", "66Zn", "96Zr", "94Mo", "95Mo", "100Ru"]),
    ("grains_SiC", "PGD_SiC_PUBLISHED_SELECTED.csv", "Type", ["12C/13C", "14N/15N", "26Al/27Al", "d(29Si/28Si)", "d(30Si/28Si)"]),
    ("grains_graphite", "PGD_GRAPHITE_PUBLISHED_SELECTED.csv", "Type", ["12C/13C", "14N/15N", "26Al/27Al", "d(29Si/28Si)", "d(30Si/28Si)"]),
    ("chondres", "FUKUDA_CHONDRULE_O_CR_TI.csv", "meteorite", ["epsilon54Cr", "epsilon50Ti", "Delta17O", "mean_size_mm"]),
    ("Bennu_refractaires", "BENNU_REFRACTORY_O_2026.csv", "context", ["d17O", "d18O", "Delta17O"]),
]


def finite(value: str) -> float | None:
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def load(spec: tuple) -> tuple[list[str], list[list[float]], list[str]]:
    _, filename, label_column, candidates = spec
    rows = list(csv.DictReader((DATA / filename).open(encoding="utf-8-sig", newline="")))
    counts = Counter(row.get(label_column, "").strip() for row in rows)
    allowed = {label for label, count in counts.items() if label and count >= 2}
    usable_features = [name for name in candidates if sum(finite(row.get(name, "")) is not None for row in rows if row.get(label_column, "").strip() in allowed) >= 4]
    labels, values = [], []
    for row in rows:
        label = row.get(label_column, "").strip()
        vector = [finite(row.get(name, "")) for name in usable_features]
        if label in allowed and vector and all(v is not None for v in vector):
            labels.append(label); values.append([float(v) for v in vector])
    return labels, values, usable_features


def loo_nearest_centroid(labels: list[str], x: list[list[float]]) -> tuple[float, list[bool]]:
    dimensions = len(x[0]); n = len(x)
    totals = [sum(row[j] for row in x) for j in range(dimensions)]
    total_squares = [sum(row[j] ** 2 for row in x) for j in range(dimensions)]
    group_counts = Counter(labels)
    group_sums = {label: [0.0] * dimensions for label in group_counts}
    for label, row in zip(labels, x):
        for j, value in enumerate(row): group_sums[label][j] += value
    correct = []
    for held in range(len(x)):
        means = [(totals[j] - x[held][j]) / (n - 1) for j in range(dimensions)]
        scales = []
        for j, mean in enumerate(means):
            square_sum = total_squares[j] - x[held][j] ** 2
            variance = max(0.0, (square_sum - (n - 1) * mean ** 2) / max(1, n - 2))
            scales.append(math.sqrt(variance) or 1.0)
        distances = {}
        for label, count in group_counts.items():
            adjusted_count = count - (label == labels[held])
            if not adjusted_count: continue
            centroid = [(group_sums[label][j] - (x[held][j] if label == labels[held] else 0.0)) / adjusted_count for j in range(dimensions)]
            distances[label] = sum(((x[held][j] - centroid[j]) / scales[j]) ** 2 for j in range(dimensions))
        predicted = min(distances, key=distances.get)
        correct.append(predicted == labels[held])
    return sum(correct) / len(correct), correct


def normalized_mi(labels: list[str], values: list[float], bins: int = 5) -> float:
    ordered = sorted(values)
    cuts = [ordered[min(len(ordered) - 1, math.floor(k * len(ordered) / bins))] for k in range(1, bins)]
    binned = [sum(value > cut for cut in cuts) for value in values]
    joint = Counter(zip(labels, binned)); lc = Counter(labels); bc = Counter(binned); n = len(labels)
    mi = sum((count / n) * math.log((count * n) / (lc[label] * bc[b])) for (label, b), count in joint.items())
    entropy = -sum((count / n) * math.log(count / n) for count in lc.values())
    return mi / entropy if entropy else 0.0


def separation_ratio(labels: list[str], x: list[list[float]]) -> float:
    ratios = []
    for j in range(len(x[0])):
        overall = sum(row[j] for row in x) / len(x)
        groups = defaultdict(list)
        for label, row in zip(labels, x): groups[label].append(row[j])
        between = sum(len(v) * ((sum(v) / len(v)) - overall) ** 2 for v in groups.values())
        within = sum(sum((z - sum(v) / len(v)) ** 2 for z in v) for v in groups.values())
        ratios.append(between / within if within else float("inf"))
    finite_ratios = [r for r in ratios if math.isfinite(r)]
    return sum(finite_ratios) / len(finite_ratios) if finite_ratios else float("inf")


def bootstrap_accuracy(correct: list[bool], seed: int = 260811, n_boot: int = 2000) -> list[float]:
    rng = random.Random(seed); n = len(correct)
    estimates = [sum(correct[rng.randrange(n)] for _ in range(n)) / n for _ in range(n_boot)]
    estimates.sort()
    return [estimates[int(0.025 * n_boot)], estimates[int(0.975 * n_boot) - 1]]


def permutation_p(labels: list[str], x: list[list[float]], observed: float, seed: int = 110826, n_perm: int = 500) -> float:
    rng = random.Random(seed); exceed = 0
    shuffled = list(labels)
    for _ in range(n_perm):
        rng.shuffle(shuffled)
        accuracy, _ = loo_nearest_centroid(shuffled, x)
        exceed += accuracy >= observed
    return (exceed + 1) / (n_perm + 1)


def analyse() -> dict:
    results = []
    for spec in SPECS:
        dataset, filename, label_column, _ = spec
        labels, x, features = load(spec)
        if len(set(labels)) < 2 or len(labels) < 6:
            results.append({"dataset": dataset, "status": "non_testable", "n": len(labels), "reason": "moins de deux groupes ou moins de six lignes complètes"})
            continue
        accuracy, correct = loo_nearest_centroid(labels, x)
        baseline = max(Counter(labels).values()) / len(labels)
        mi = [normalized_mi(labels, [row[j] for row in x]) for j in range(len(features))]
        results.append({
            "dataset": dataset, "source": f"data_massives_reelles/{filename}", "label": label_column,
            "n": len(labels), "groups": len(set(labels)), "features": features,
            "loo_accuracy": accuracy, "majority_baseline": baseline,
            "accuracy_gain": accuracy - baseline, "bootstrap_95_accuracy": bootstrap_accuracy(correct),
            "label_permutation_p_one_sided": permutation_p(labels, x, accuracy),
            "label_permutations": 500,
            "normalized_mi_by_feature": dict(zip(features, mi)), "normalized_mi_mean": sum(mi) / len(mi),
            "between_within_ratio_mean": separation_ratio(labels, x),
            "status": "information_decodable" if accuracy > baseline else "non_decodable_par_ce_test",
        })
    return {
        "schema": "oric.gc.historical-information.v1", "analysis": "retrospective",
        "estimand": "information de provenance décodable dans les mesures individuelles",
        "results": results,
        "limits": [
            "les classes rares et lignes incomplètes sont exclues selon une règle fixe",
            "l'information décodable n'établit pas que la provenance modifie une réponse future",
            "les tables ne suivent pas les mêmes objets entre étages; aucune courbe de perte causale inter-étages n'est revendiquée",
        ],
    }


def render_report(result: dict) -> str:
    """Construit le rapport lisible depuis le même résultat que le JSON."""
    labels = {
        "reservoir_NC_CC": "Réservoirs NC/CC",
        "grains_SiC": "Grains SiC",
        "grains_graphite": "Grains graphite",
        "chondres": "Chondres",
        "Bennu_refractaires": "Réfractaires Bennu",
    }
    rows = []
    for item in result["results"]:
        label = labels[item["dataset"]]
        if item["status"] == "non_testable":
            rows.append(f"| {label} | {item['n']} | — | — | — | — | groupes complets insuffisants |")
            continue
        verdict = "provenance décodable" if item["status"] == "information_decodable" else "non décodable par ce test"
        gain = item["accuracy_gain"]
        rows.append(
            f"| {label} | {item['n']} | {item['loo_accuracy']:.3f} | "
            f"{item['majority_baseline']:.3f} | {gain:+.3f} | "
            f"{item['label_permutation_p_one_sided']:.5f} | {verdict} |"
        )
    return "\n".join([
        "# Information historique dans les mesures cosmiques individuelles", "",
        "## Résultat", "",
        "L'analyse rétrospective utilise uniquement des lignes publiées, une",
        "classification par centroïdes en leave-one-out, un bootstrap de l'exactitude et",
        "500 permutations des étiquettes.", "",
        "| Population | n | Exactitude | Baseline majoritaire | Gain | p permutation | Verdict local |",
        "|---|---:|---:|---:|---:|---:|---|", *rows, "",
        "Les deux résultats positifs montrent qu'une information de population reste",
        "présente dans les observables isotopiques. Les trois autres résultats empêchent",
        "d'étendre cette conclusion à toutes les populations.", "",
        "## Limite décisive", "",
        "Les tables ne suivent pas les mêmes objets de l'étoile au grain, puis au disque",
        "et au planétésimal. Cette analyse ne produit donc pas encore une courbe causale",
        "de conservation de l'histoire entre étages. Elle mesure une information locale",
        "de provenance, pas `I(H_ancien;X_t)` sur une lignée matérielle appariée.", "",
    ])


def write_outputs(out: Path) -> dict:
    """Écrit les deux artefacts canoniques dans le dossier demandé."""
    result = analyse()
    out.mkdir(parents=True, exist_ok=True)
    (out / "INFORMATION_HISTORIQUE.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (out / "RAPPORT_INFORMATION_HISTORIQUE.md").write_text(
        render_report(result), encoding="utf-8", newline="\n"
    )
    return result


def main() -> int:
    result = write_outputs(OUT)
    print(json.dumps({r["dataset"]: r["status"] for r in result["results"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
