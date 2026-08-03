"""Benchmark exploratoire réel : l'histoire prédit-elle la survie suivante ?"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "antibiotic_measurements.csv"
EXPOSURES = ROOT / "data" / "antibiotic_cycles.csv"
OUTPUT = ROOT / "resultats_consolides" / "benchmark_antibiotic_history.json"
SEED = 20260802
REPEATS = 200
RIDGES = (0.0, 0.01, 0.1, 1.0, 10.0, 100.0)


def load() -> list[dict[str, float | str]]:
    dose = {}
    with EXPOSURES.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            dose[row["lineage_id"]] = float(row["dose"])
    series: dict[str, list[tuple[int, float]]] = defaultdict(list)
    with INPUT.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            if row["cycle"].strip() and row["survival"].strip() and row["lineage_id"] in dose:
                value = float(row["survival"])
                if value > 0:
                    series[row["lineage_id"]].append((int(float(row["cycle"])), np.log10(value)))
    observations = []
    for lineage, values in series.items():
        values = sorted(values)
        for index in range(2, len(values) - 1):
            history = values[: index + 1]
            cycles = np.array([item[0] for item in history], dtype=float)
            survival = np.array([item[1] for item in history], dtype=float)
            slope = float(np.polyfit(cycles, survival, 1)[0])
            observations.append({
                "lineage": lineage,
                "cycle": float(history[-1][0]),
                "dose": float(np.log10(dose[lineage])),
                "current": float(survival[-1]),
                "mean": float(survival.mean()),
                "std": float(survival.std(ddof=1)),
                "slope": slope,
                "target": float(values[index + 1][1]),
            })
    return observations


def matrices(rows: list[dict], model: str) -> tuple[np.ndarray, np.ndarray]:
    x = []
    for row in rows:
        base = [row["current"], row["dose"], row["cycle"]]
        if model == "equal_complexity":
            base += [row["cycle"] ** 2, row["current"] * row["cycle"], row["dose"] * row["cycle"]]
        elif model == "history":
            base += [row["mean"], row["std"], row["slope"]]
        x.append(base)
    return np.asarray(x, dtype=float), np.asarray([row["target"] for row in rows])


def fit_predict(train: list[dict], test: list[dict], model: str, ridge: float) -> np.ndarray:
    x_train, y_train = matrices(train, model)
    x_test, _ = matrices(test, model)
    mean, std = x_train.mean(axis=0), x_train.std(axis=0)
    std[std == 0] = 1.0
    x_train = np.column_stack([np.ones(len(x_train)), (x_train - mean) / std])
    x_test = np.column_stack([np.ones(len(x_test)), (x_test - mean) / std])
    penalty = np.eye(x_train.shape[1]) * ridge
    penalty[0, 0] = 0.0
    beta = np.linalg.solve(x_train.T @ x_train + penalty, x_train.T @ y_train)
    return x_test @ beta


def choose_ridge(train: list[dict], model: str, rng: np.random.Generator) -> float:
    lineages = np.array(sorted({row["lineage"] for row in train}))
    rng.shuffle(lineages)
    validation_ids = set(lineages[: max(1, len(lineages) // 5)])
    fit_rows = [row for row in train if row["lineage"] not in validation_ids]
    validation = [row for row in train if row["lineage"] in validation_ids]
    truth = np.asarray([row["target"] for row in validation])
    errors = [(float(np.mean(np.abs(truth - fit_predict(fit_rows, validation, model, ridge)))), ridge)
              for ridge in RIDGES]
    return min(errors)[1]


def main() -> int:
    rows = load()
    lineages = np.array(sorted({row["lineage"] for row in rows}))
    rng = np.random.default_rng(SEED)
    models = ("state_only", "equal_complexity", "history")
    errors = {model: [] for model in models}
    differences = []
    for _ in range(REPEATS):
        shuffled = rng.permutation(lineages)
        test_ids = set(shuffled[: max(1, len(shuffled) // 5)])
        train = [row for row in rows if row["lineage"] not in test_ids]
        test = [row for row in rows if row["lineage"] in test_ids]
        truth = np.asarray([row["target"] for row in test])
        fold = {}
        for model in models:
            ridge = choose_ridge(train, model, rng)
            fold[model] = float(np.mean(np.abs(truth - fit_predict(train, test, model, ridge))))
            errors[model].append(fold[model])
        differences.append(fold["equal_complexity"] - fold["history"])
    result = {
        "status": "exploratory_not_confirmatory",
        "outcome": "next_observed_log10_survival",
        "lineages": int(len(lineages)),
        "prediction_rows": int(len(rows)),
        "repeated_group_splits": REPEATS,
        "models": {
            model: {"mae_mean": float(np.mean(values)),
                    "mae_ci_2.5": float(np.percentile(values, 2.5)),
                    "mae_ci_97.5": float(np.percentile(values, 97.5))}
            for model, values in errors.items()
        },
        "equal_complexity_minus_history": {
            "mean": float(np.mean(differences)),
            "ci_2.5": float(np.percentile(differences, 2.5)),
            "ci_97.5": float(np.percentile(differences, 97.5)),
            "fraction_history_better": float(np.mean(np.asarray(differences) > 0)),
        },
        "limitations": [
            "single antibiotic (amikacin)",
            "exploratory repeated splits; no untouched final test set",
            "endpoint MIC/persister rows cannot be joined to longitudinal lineages",
            "history features summarize prior survival, not independently varied exposure sequences",
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

