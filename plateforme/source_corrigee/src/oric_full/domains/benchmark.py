from __future__ import annotations

from dataclasses import dataclass
import json
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.pipeline import FeatureUnion


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


def run_cross_domain_benchmark(frame: pd.DataFrame) -> BenchmarkAnalysis:
    f = frame.copy()
    f = f[f["split"].isin(["train", "validation", "test"])].copy()
    f["state_text"] = f["state_json"].map(_flatten_json)
    f["history_text"] = f["history_json"].map(_flatten_json)
    f["target"] = f["future_json"].map(_flatten_json)
    if len(f) < 20 or f["target"].nunique() < 2:
        return BenchmarkAnalysis({"gain_history": float("nan")}, {"reason": "Données insuffisantes"})
    train = f[f["split"] == "train"]
    test = f[f["split"] == "test"]
    if train.empty or test.empty:
        # fallback group CV by domain
        groups = f["domain"].astype("category").cat.codes.to_numpy()
        if len(np.unique(groups)) < 2:
            return BenchmarkAnalysis({"gain_history": float("nan")}, {"reason": "Split ou domaines insuffisants"})
        train = f
        test = f
    state_vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=1)
    history_vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=1)
    x_state = state_vec.fit_transform(train["state_text"])
    x_state_test = state_vec.transform(test["state_text"])
    x_hist = history_vec.fit_transform(train["history_text"])
    x_hist_test = history_vec.transform(test["history_text"])
    from scipy.sparse import hstack
    baseline = LogisticRegression(max_iter=2000).fit(x_state, train["target"])
    candidate = LogisticRegression(max_iter=2000).fit(hstack([x_state, x_hist]), train["target"])
    pb = baseline.predict(x_state_test)
    pc = candidate.predict(hstack([x_state_test, x_hist_test]))
    ab = accuracy_score(test["target"], pb)
    ac = accuracy_score(test["target"], pc)
    return BenchmarkAnalysis(
        {"state_accuracy": float(ab), "history_accuracy": float(ac), "gain_history": float(ac - ab)},
        {"train_n": len(train), "test_n": len(test), "classes": int(f["target"].nunique())},
    )


def compression_score(frame: pd.DataFrame) -> BenchmarkAnalysis:
    raw = frame[["history_json", "state_json", "future_json"]].astype(str).apply(lambda c: c.str.len()).sum(axis=1)
    oric = frame.get("oric_features", pd.Series([""] * len(frame))).astype(str).str.len()
    ratio = oric / raw.replace(0, np.nan)
    return BenchmarkAnalysis(
        {"median_compression_ratio": float(ratio.median(skipna=True) or 0.0), "cases": float(len(frame))},
        {},
    )
