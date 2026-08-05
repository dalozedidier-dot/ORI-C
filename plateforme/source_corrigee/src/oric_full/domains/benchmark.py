from __future__ import annotations

from dataclasses import dataclass
import json
import numpy as np
import pandas as pd
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, brier_score_loss, log_loss


@dataclass(frozen=True)
class BenchmarkAnalysis:
    metrics: dict[str, float]
    details: dict


def _flatten_json(value: str) -> str:
    try:
        obj = json.loads(value)
        if isinstance(obj, dict):
            return " ".join(f"{k}={v}" for k, v in sorted(obj.items()))
        return str(obj)
    except Exception:
        return str(value)


def _evaluate_binary(model: LogisticRegression, x_test, target: pd.Series) -> dict[str, float]:
    prediction = model.predict(x_test)
    classes = list(model.classes_)
    positive = "outcome=increase"
    if positive not in classes:
        positive = classes[-1]
    positive_index = classes.index(positive)
    probability = model.predict_proba(x_test)[:, positive_index]
    truth_binary = (target.astype(str).to_numpy() == positive).astype(int)
    return {
        "accuracy": float(accuracy_score(target, prediction)),
        "balanced_accuracy": float(balanced_accuracy_score(target, prediction)),
        "brier": float(brier_score_loss(truth_binary, probability)),
        "log_loss": float(log_loss(target, model.predict_proba(x_test), labels=classes)),
    }


def run_cross_domain_benchmark(frame: pd.DataFrame) -> BenchmarkAnalysis:
    f = frame.copy()
    f = f[f["split"].isin(["train", "validation", "test"])].copy()
    f["state_text"] = f["state_json"].map(_flatten_json)
    f["history_text"] = f["history_json"].map(_flatten_json)
    f["target"] = f["future_json"].map(_flatten_json)
    if len(f) < 20 or f["target"].nunique() < 2:
        return BenchmarkAnalysis({"gain_history": float("nan")}, {"reason": "Données insuffisantes"})
    train = f[f["split"].isin(["train", "validation"])].copy()
    test = f[f["split"] == "test"].copy()
    if train.empty or test.empty or train["target"].nunique() < 2 or test["target"].nunique() < 2:
        return BenchmarkAnalysis({"gain_history": float("nan")}, {"reason": "Split ou classes insuffisants"})

    state_vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=5000, token_pattern=r"(?u)\b[\w.=+-]+\b")
    history_vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=5000, token_pattern=r"(?u)\b[\w.=+-]+\b")
    x_state = state_vec.fit_transform(train["state_text"])
    x_state_test = state_vec.transform(test["state_text"])
    x_hist = history_vec.fit_transform(train["history_text"])
    x_hist_test = history_vec.transform(test["history_text"])

    baseline = LogisticRegression(max_iter=3000, random_state=0, class_weight="balanced").fit(x_state, train["target"])
    candidate = LogisticRegression(max_iter=3000, random_state=0, class_weight="balanced").fit(
        hstack([x_state, x_hist]), train["target"]
    )
    baseline_metrics = _evaluate_binary(baseline, x_state_test, test["target"])
    history_metrics = _evaluate_binary(candidate, hstack([x_state_test, x_hist_test]), test["target"])

    per_domain: dict[str, dict[str, float]] = {}
    baseline_pred = baseline.predict(x_state_test)
    history_pred = candidate.predict(hstack([x_state_test, x_hist_test]))
    for domain, indexes in test.groupby("domain").groups.items():
        positions = test.index.get_indexer(indexes)
        y = test.loc[indexes, "target"]
        if len(y) == 0:
            continue
        per_domain[str(domain)] = {
            "n": int(len(y)),
            "state_accuracy": float(accuracy_score(y, baseline_pred[positions])),
            "history_accuracy": float(accuracy_score(y, history_pred[positions])),
        }

    metrics = {
        "state_accuracy": baseline_metrics["accuracy"],
        "history_accuracy": history_metrics["accuracy"],
        "gain_history": history_metrics["accuracy"] - baseline_metrics["accuracy"],
        "state_balanced_accuracy": baseline_metrics["balanced_accuracy"],
        "history_balanced_accuracy": history_metrics["balanced_accuracy"],
        "gain_history_balanced": history_metrics["balanced_accuracy"] - baseline_metrics["balanced_accuracy"],
        "state_brier": baseline_metrics["brier"],
        "history_brier": history_metrics["brier"],
        "brier_improvement": baseline_metrics["brier"] - history_metrics["brier"],
        "state_log_loss": baseline_metrics["log_loss"],
        "history_log_loss": history_metrics["log_loss"],
    }
    return BenchmarkAnalysis(
        metrics,
        {
            "train_n": int(len(train)),
            "test_n": int(len(test)),
            "classes": int(f["target"].nunique()),
            "domains": f.groupby("domain").size().astype(int).to_dict(),
            "per_domain": per_domain,
            "state_vocabulary_features": int(x_state.shape[1]),
            "history_vocabulary_features": int(x_hist.shape[1]),
            "candidate_total_features": int(x_state.shape[1] + x_hist.shape[1]),
            "interpretation_limit": (
                "Benchmark exploratoire dérivé de données réelles. Les cibles binaires et les divisions "
                "ont été construites avant l'ajustement; aucune confirmation hors étude n'est revendiquée."
            ),
        },
    )


def compression_score(frame: pd.DataFrame) -> BenchmarkAnalysis:
    raw = frame[["history_json", "state_json", "future_json"]].astype(str).apply(lambda c: c.str.len()).sum(axis=1)
    oric = frame.get("oric_features", pd.Series([""] * len(frame))).astype(str).str.len()
    ratio = oric / raw.replace(0, np.nan)
    finite = ratio.replace([np.inf, -np.inf], np.nan).dropna()
    return BenchmarkAnalysis(
        {
            "median_compression_ratio": float(finite.median()) if len(finite) else float("nan"),
            "mean_compression_ratio": float(finite.mean()) if len(finite) else float("nan"),
            "cases": float(len(frame)),
        },
        {
            "measured_cases": int(len(finite)),
            "interpretation_limit": "Mesure de longueur d'encodage, pas mesure de vérité scientifique ni de clarté humaine.",
        },
    )
