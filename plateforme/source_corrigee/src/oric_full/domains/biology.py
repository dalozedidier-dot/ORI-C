from __future__ import annotations

from dataclasses import dataclass
import json
import numpy as np
import pandas as pd
import networkx as nx
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, brier_score_loss, log_loss


@dataclass(frozen=True)
class BiologyAnalysis:
    metrics: dict[str, float]
    details: dict


def analyze_cell_architecture(frame: pd.DataFrame) -> BiologyAnalysis:
    graph = nx.DiGraph()
    for row in frame.itertuples(index=False):
        taxon = str(row.taxon)
        component = str(row.component)
        function = str(row.function)
        graph.add_edge(f"taxon:{taxon}", f"component:{component}", relation="HAS")
        graph.add_edge(f"component:{component}", f"function:{function}", relation="ENABLES")
        dependency = str(row.dependency)
        if dependency and dependency not in {"nan", "None", ""}:
            graph.add_edge(f"component:{component}", f"component:{dependency}", relation="DEPENDS")
    centrality = nx.pagerank(graph) if len(graph) else {}
    component_centrality = {k: v for k, v in centrality.items() if k.startswith("component:")}
    evidence = pd.to_numeric(frame["evidence_level"], errors="coerce")
    return BiologyAnalysis(
        {
            "components": float(frame["component"].nunique()),
            "functions": float(frame["function"].nunique()),
            "dependency_edges": float(sum(1 for _, _, d in graph.edges(data=True) if d.get("relation") == "DEPENDS")),
            "mean_evidence_level": float(evidence.mean(skipna=True) or 0.0),
        },
        {"component_centrality": component_centrality},
    )


def analyze_endosymbiosis(frame: pd.DataFrame) -> BiologyAnalysis:
    f = frame.copy()
    for col in ["gene_transfer", "metabolic_integration", "dependency", "evidence_level"]:
        f[col] = pd.to_numeric(f[col], errors="coerce")
    integration = f[["gene_transfer", "metabolic_integration", "dependency"]].mean(axis=1)
    return BiologyAnalysis(
        {
            "events": float(len(f)),
            "median_integration": float(integration.median(skipna=True) or 0.0),
            "integration_evidence_correlation": float(integration.corr(f["evidence_level"]) or 0.0),
        },
        {"integration_scores": dict(zip(f["event_id"].astype(str), integration.fillna(0).tolist()))},
    )


def _flatten_json(value: object) -> str:
    try:
        obj = json.loads(str(value))
        if isinstance(obj, dict):
            return " ".join(f"{key}={obj[key]}" for key in sorted(obj))
        return str(obj)
    except Exception:
        return str(value)


def _classification_metrics(
    y_true: pd.Series,
    prediction: np.ndarray,
    probabilities: np.ndarray,
    classes: list[str],
) -> dict[str, float]:
    metrics = {
        "accuracy": float(accuracy_score(y_true, prediction)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, prediction)),
        "log_loss": float(log_loss(y_true, probabilities, labels=classes)),
    }
    if len(classes) == 2:
        positive = "increase" if "increase" in classes else classes[-1]
        positive_index = classes.index(positive)
        truth_binary = (y_true.astype(str).to_numpy() == positive).astype(int)
        metrics["brier"] = float(brier_score_loss(truth_binary, probabilities[:, positive_index]))
    else:
        metrics["brier"] = float("nan")
    return metrics


def biological_history_value(frame: pd.DataFrame) -> BiologyAnalysis:
    """Mesure exploratoire de la valeur prédictive de l'histoire sur cas réels.

    Les données restent séparées selon le champ ``split`` produit avant
    l'analyse. Aucun statut confirmatoire n'est déduit de ce benchmark dérivé.
    """
    f = frame.copy()
    if "split" not in f.columns:
        # Compatibilité des fixtures logicielles : séparation déterministe par
        # position. Les campagnes réelles fournissent leur split préconstruit.
        fractions = np.arange(len(f)) / max(len(f), 1)
        f["split"] = np.where(fractions < 0.6, "train", np.where(fractions < 0.8, "validation", "test"))
    f = f[f["split"].isin(["train", "validation", "test"])].copy()
    f["state_text"] = f["state"].map(_flatten_json)
    f["history_text"] = f["history"].map(_flatten_json)
    f["oric_text"] = f["oric_features"].map(_flatten_json)
    f["target"] = f["future_outcome"].astype(str)

    # Collision exacte conservée comme diagnostic descriptif, sans faire croire
    # que des états continus proches sont identiques.
    state_future = f.groupby("state")["target"].nunique()
    ambiguous_states = state_future[state_future > 1]
    history_resolves = []
    for state in ambiguous_states.index:
        sub = f[f["state"] == state]
        deterministic = sub.groupby("history")["target"].nunique()
        history_resolves.append(float((deterministic == 1).mean()))

    train = f[f["split"].isin(["train", "validation"])].copy()
    test = f[f["split"] == "test"].copy()
    details: dict = {
        "rows": int(len(f)),
        "domains": f.groupby("domain").size().astype(int).to_dict(),
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "exact_ambiguous_states": ambiguous_states.to_dict(),
        "interpretation_limit": (
            "Benchmark exploratoire dérivé de mesures réelles. Les cibles sont des directions binaires; "
            "aucune réplication externe ni causalité biologique générale n'est revendiquée."
        ),
    }
    metrics = {
        "ambiguous_state_fraction": float(len(ambiguous_states) / max(len(state_future), 1)),
        "history_resolution_fraction": float(np.mean(history_resolves)) if history_resolves else 0.0,
        "rows": float(len(f)),
        "domains": float(f["domain"].nunique()),
    }
    if len(train) < 20 or len(test) < 10 or train["target"].nunique() < 2 or test["target"].nunique() < 2:
        details["predictive_reason"] = "Split ou classes insuffisants"
        return BiologyAnalysis(metrics, details)

    state_vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=5000, token_pattern=r"(?u)\b[\w.=+-]+\b")
    history_vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=5000, token_pattern=r"(?u)\b[\w.=+-]+\b")
    oric_vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=5000, token_pattern=r"(?u)\b[\w.=+-]+\b")
    x_state = state_vec.fit_transform(train["state_text"])
    x_state_test = state_vec.transform(test["state_text"])
    x_history = history_vec.fit_transform(train["history_text"])
    x_history_test = history_vec.transform(test["history_text"])
    x_oric = oric_vec.fit_transform(train["oric_text"])
    x_oric_test = oric_vec.transform(test["oric_text"])

    models = {
        "state": (x_state, x_state_test),
        "state_history": (hstack([x_state, x_history]), hstack([x_state_test, x_history_test])),
        "state_history_oric": (
            hstack([x_state, x_history, x_oric]),
            hstack([x_state_test, x_history_test, x_oric_test]),
        ),
    }
    model_metrics: dict[str, dict[str, float]] = {}
    for name, (x_train, x_test) in models.items():
        model = LogisticRegression(max_iter=3000, random_state=0, class_weight="balanced")
        model.fit(x_train, train["target"])
        prediction = model.predict(x_test)
        classes = [str(value) for value in model.classes_]
        probabilities = model.predict_proba(x_test)
        model_metrics[name] = _classification_metrics(test["target"], prediction, probabilities, classes)

    details["predictive_models"] = model_metrics
    for name, values in model_metrics.items():
        for metric_name, value in values.items():
            metrics[f"{name}_{metric_name}"] = value
    metrics["history_balanced_accuracy_gain"] = (
        model_metrics["state_history"]["balanced_accuracy"] - model_metrics["state"]["balanced_accuracy"]
    )
    metrics["oric_balanced_accuracy_gain"] = (
        model_metrics["state_history_oric"]["balanced_accuracy"] - model_metrics["state_history"]["balanced_accuracy"]
    )
    state_brier = model_metrics["state"]["brier"]
    history_brier = model_metrics["state_history"]["brier"]
    metrics["history_brier_improvement"] = (
        state_brier - history_brier if np.isfinite(state_brier) and np.isfinite(history_brier) else float("nan")
    )
    return BiologyAnalysis(metrics, details)
