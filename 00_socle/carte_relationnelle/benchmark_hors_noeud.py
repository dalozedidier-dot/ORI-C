"""Benchmark hors nœud : chronologie seule contre attributs ORI-C disponibles.

Chaque transition cible est laissée entièrement hors apprentissage. Le modèle
ne voit aucune paire incidente à cette transition. Il prédit ensuite les liens
entrants possibles depuis les transitions antérieures.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUTPUT = ROOT / "resultats_analyse" / "benchmark_hors_noeud.json"


def load() -> tuple[dict[str, dict], set[tuple[str, str]]]:
    with (DATA / "noeuds_poc.csv").open(encoding="utf-8-sig", newline="") as stream:
        nodes = {row["id"]: row for row in csv.DictReader(stream, delimiter=";")}
    with (DATA / "relations_oric_47_provisoires.csv").open(encoding="utf-8-sig", newline="") as stream:
        edges = {
            (row["source"], row["target"])
            for row in csv.DictReader(stream, delimiter=";")
            if row["relation"] != "FEED" and rank(row["source"]) < rank(row["target"])
        }
    return nodes, edges


def rank(node: str) -> int:
    return int(node.split("-")[1])


def features(pair: tuple[str, str], nodes: dict[str, dict], regimes: dict[str, int]) -> np.ndarray:
    source, target = pair
    gap = rank(target) - rank(source)
    rs, rt = regimes[source], regimes[target]
    return np.array([
        -np.log1p(gap),
        float(rs == rt),
        -float(abs(rt - rs)),
    ])


def fit_logistic(x: np.ndarray, y: np.ndarray, ridge: float = 1.0) -> np.ndarray:
    x = np.column_stack([np.ones(len(x)), x])
    weights = np.where(y == 1, len(y) / (2 * y.sum()), len(y) / (2 * (len(y) - y.sum())))
    beta = np.zeros(x.shape[1])
    penalty = np.diag([0.0] + [ridge] * (x.shape[1] - 1))
    for _ in range(50):
        probability = 1.0 / (1.0 + np.exp(-np.clip(x @ beta, -30, 30)))
        variance = np.maximum(probability * (1.0 - probability), 1e-8)
        gradient = x.T @ (weights * (probability - y)) + penalty @ beta
        hessian = x.T @ ((weights * variance)[:, None] * x) + penalty
        updated = beta - np.linalg.solve(hessian, gradient)
        if np.max(np.abs(updated - beta)) < 1e-10:
            beta = updated
            break
        beta = updated
    return beta


def predict(beta: np.ndarray, x: np.ndarray) -> np.ndarray:
    return np.column_stack([np.ones(len(x)), x]) @ beta


def auc(y: np.ndarray, scores: np.ndarray) -> float:
    positives = scores[y == 1]
    negatives = scores[y == 0]
    return float(np.mean((positives[:, None] > negatives).astype(float)
                         + 0.5 * (positives[:, None] == negatives)))


def evaluate(nodes: dict[str, dict], edges: set[tuple[str, str]], regimes: dict[str, int]) -> dict:
    ordered = sorted(nodes, key=rank)
    candidates = [(u, v) for u in ordered for v in ordered if rank(u) < rank(v)]
    truth, chronology, expanded = [], [], []
    folds = []
    for held_target in ordered[1:]:
        train = [pair for pair in candidates if held_target not in pair]
        test = [pair for pair in candidates if pair[1] == held_target]
        train_y = np.array([int(pair in edges) for pair in train])
        test_y = np.array([int(pair in edges) for pair in test])
        if train_y.sum() == 0 or test_y.sum() == 0:
            continue
        train_x = np.vstack([features(pair, nodes, regimes) for pair in train])
        test_x = np.vstack([features(pair, nodes, regimes) for pair in test])
        beta = fit_logistic(train_x, train_y)
        truth.extend(test_y.tolist())
        chronology.extend(test_x[:, 0].tolist())
        expanded.extend(predict(beta, test_x).tolist())
        folds.append({"target": held_target, "positives": int(test_y.sum()), "candidates": len(test)})
    y = np.asarray(truth)
    return {
        "auc_chronologie": auc(y, np.asarray(chronology)),
        "auc_chronologie_plus_regime": auc(y, np.asarray(expanded)),
        "difference": auc(y, np.asarray(expanded)) - auc(y, np.asarray(chronology)),
        "positifs": int(y.sum()),
        "negatifs": int(len(y) - y.sum()),
        "folds": len(folds),
        "details_folds": folds,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--permutations", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20260802)
    args = parser.parse_args()
    nodes, edges = load()
    regimes = {node: int(row["regime_num"]) for node, row in nodes.items()}
    observed = evaluate(nodes, edges, regimes)
    rng = np.random.default_rng(args.seed)
    node_ids = sorted(nodes, key=rank)
    values = np.array([regimes[node] for node in node_ids])
    null_differences = []
    for _ in range(args.permutations):
        shuffled = dict(zip(node_ids, rng.permutation(values).tolist()))
        null_differences.append(evaluate(nodes, edges, shuffled)["difference"])
    null = np.asarray(null_differences)
    report = {
        "protocol": "leave-one-target-node-out",
        "seed": args.seed,
        "permutations": args.permutations,
        "observed": observed,
        "permutation_regime": {
            "mean_difference": float(null.mean()),
            "ci_2.5": float(np.percentile(null, 2.5)),
            "ci_97.5": float(np.percentile(null, 97.5)),
            "p_one_sided": float((np.sum(null >= observed["difference"]) + 1) / (len(null) + 1)),
        },
        "interpretation_rule": (
            "Les attributs ORI-C disponibles apportent une information hors chronologie seulement si "
            "la difference d'AUC est positive et depasse la distribution obtenue en permutant les regimes."
        ),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
