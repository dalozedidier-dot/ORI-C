"""Analyses maximales possibles avec les données biologiques actuellement présentes.

Deux ensembles sont séparés :
- survie longitudinale sous amikacine, pour tester une valeur prédictive de l'histoire ;
- fréquences de séquences d'ARN catalytique, pour décrire une dynamique de composition.

Aucun de ces ensembles ne fournit des lignées prébiotiques. Le script ne transforme
donc pas un enrichissement de séquence en preuve d'hérédité ou d'origine du vivant.
"""
from __future__ import annotations

import itertools
import math
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

from common import ROOT, RESULTS, read_csv, write_json

DATA = ROOT / "plateforme" / "campagne_maximale_reelle" / "data"
OUTPUT = RESULTS / "vivant_robustesse.json"
SEED = 20260804
RIDGES = (0.0, 0.01, 0.1, 1.0, 10.0, 100.0)


def load_antibiotic_series() -> tuple[dict[str, list[tuple[int, float]]], dict[str, float]]:
    exposure_rows = read_csv(DATA / "antibiotic_cycles.csv")
    dose_by_lineage = {row["lineage_id"]: float(row["dose"]) for row in exposure_rows}
    series: dict[str, list[tuple[int, float]]] = defaultdict(list)
    for row in read_csv(DATA / "antibiotic_measurements.csv"):
        cycle = row["cycle"].strip()
        survival = row["survival"].strip()
        lineage = row["lineage_id"]
        if not cycle or not survival or lineage not in dose_by_lineage:
            continue
        value = float(survival)
        if value > 0:
            series[lineage].append((int(float(cycle)), math.log10(value)))
    for lineage in series:
        series[lineage] = sorted(series[lineage])
    return dict(series), dose_by_lineage


def build_prediction_rows(
    series: dict[str, list[tuple[int, float]]],
    dose_by_lineage: dict[str, float],
) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for lineage, values in series.items():
        for index in range(2, len(values) - 1):
            history = values[: index + 1]
            cycles = np.asarray([item[0] for item in history], dtype=float)
            survival = np.asarray([item[1] for item in history], dtype=float)
            rows.append({
                "lineage": lineage,
                "cycle": float(cycles[-1]),
                "dose_raw": float(dose_by_lineage[lineage]),
                "dose": float(math.log10(dose_by_lineage[lineage])),
                "current": float(survival[-1]),
                "mean": float(survival.mean()),
                "std": float(survival.std(ddof=1)),
                "slope": float(np.polyfit(cycles, survival, 1)[0]),
                "target": float(values[index + 1][1]),
                "is_final_prediction": index == len(values) - 2,
            })
    return rows


def feature_vector(row: dict, model: str) -> list[float]:
    base = [float(row["current"]), float(row["dose"]), float(row["cycle"])]
    if model == "equal_complexity":
        base += [
            float(row["cycle"]) ** 2,
            float(row["current"]) * float(row["cycle"]),
            float(row["dose"]) * float(row["cycle"]),
        ]
    elif model == "history":
        base += [float(row["mean"]), float(row["std"]), float(row["slope"])]
    elif model == "history_no_slope":
        base += [float(row["mean"]), float(row["std"])]
    elif model == "history_slope_only":
        base += [float(row["slope"])]
    elif model != "state_only":
        raise ValueError(f"Modèle inconnu: {model}")
    return base


def matrices(rows: list[dict], model: str) -> tuple[np.ndarray, np.ndarray]:
    x = np.asarray([feature_vector(row, model) for row in rows], dtype=float)
    y = np.asarray([float(row["target"]) for row in rows], dtype=float)
    return x, y


def fit_predict(train: list[dict], test: list[dict], model: str, ridge: float) -> np.ndarray:
    x_train, y_train = matrices(train, model)
    x_test, _ = matrices(test, model)
    mean = x_train.mean(axis=0)
    std = x_train.std(axis=0)
    std[std == 0] = 1.0
    x_train = np.column_stack([np.ones(len(x_train)), (x_train - mean) / std])
    x_test = np.column_stack([np.ones(len(x_test)), (x_test - mean) / std])
    penalty = np.eye(x_train.shape[1]) * ridge
    penalty[0, 0] = 0.0
    beta = np.linalg.pinv(x_train.T @ x_train + penalty) @ x_train.T @ y_train
    return x_test @ beta


def lineage_folds(rows: list[dict], folds: int, seed: int) -> list[set[str]]:
    lineages = np.asarray(sorted({str(row["lineage"]) for row in rows}))
    rng = np.random.default_rng(seed)
    shuffled = list(rng.permutation(lineages))
    return [set(shuffled[index::folds]) for index in range(folds)]


def choose_ridge(train: list[dict], model: str, seed: int) -> float:
    folds = lineage_folds(train, folds=5, seed=seed)
    scores = []
    for ridge in RIDGES:
        errors = []
        for validation_ids in folds:
            fit_rows = [row for row in train if row["lineage"] not in validation_ids]
            validation = [row for row in train if row["lineage"] in validation_ids]
            if not fit_rows or not validation:
                continue
            truth = np.asarray([float(row["target"]) for row in validation])
            pred = fit_predict(fit_rows, validation, model, ridge)
            errors.extend(np.abs(truth - pred))
        scores.append((float(np.mean(errors)), ridge))
    return min(scores)[1]


def cross_validate(
    rows: list[dict],
    models: tuple[str, ...],
    folds: int = 10,
    seed: int = SEED,
) -> dict:
    split = lineage_folds(rows, folds=folds, seed=seed)
    errors: dict[str, list[float]] = {model: [] for model in models}
    paired_fold_mae: list[dict[str, float]] = []
    for index, test_ids in enumerate(split):
        train = [row for row in rows if row["lineage"] not in test_ids]
        test = [row for row in rows if row["lineage"] in test_ids]
        truth = np.asarray([float(row["target"]) for row in test])
        fold_result = {}
        for model in models:
            ridge = choose_ridge(train, model, seed + index * 31 + len(model))
            absolute = np.abs(truth - fit_predict(train, test, model, ridge))
            errors[model].extend(float(value) for value in absolute)
            fold_result[model] = float(absolute.mean())
        paired_fold_mae.append(fold_result)
    return {
        "folds": folds,
        "rows": len(rows),
        "lineages": len({row["lineage"] for row in rows}),
        "models": {
            model: {
                "mae": float(np.mean(values)),
                "median_absolute_error": float(np.median(values)),
                "p90_absolute_error": float(np.percentile(values, 90)),
            }
            for model, values in errors.items()
        },
        "paired_fold_mae": paired_fold_mae,
    }


def paired_difference(cv: dict, left: str, right: str) -> dict:
    differences = np.asarray([
        fold[left] - fold[right] for fold in cv["paired_fold_mae"]
    ])
    observed = abs(float(differences.mean()))
    sign_flip_means = []
    for signs in itertools.product((-1.0, 1.0), repeat=len(differences)):
        sign_flip_means.append(abs(float(np.mean(differences * np.asarray(signs)))))
    exact_p = float(np.mean(np.asarray(sign_flip_means) >= observed - 1e-15))
    return {
        "definition": f"MAE({left}) - MAE({right}); positif favorise {right}",
        "mean": float(differences.mean()),
        "median": float(np.median(differences)),
        "min": float(differences.min()),
        "max": float(differences.max()),
        "fraction_favoring_right": float(np.mean(differences > 0)),
        "exact_two_sided_sign_flip_p": exact_p,
        "sign_flip_combinations": len(sign_flip_means),
        "warning": (
            "Les plis partagent une grande partie de leurs données d'apprentissage. Le test exact de "
            "changement de signe est un diagnostic apparié, pas une réplication indépendante."
        ),
    }


def final_transition_holdout(rows: list[dict]) -> dict:
    test = [row for row in rows if bool(row["is_final_prediction"])]
    train = [row for row in rows if not bool(row["is_final_prediction"])]
    models = ("state_only", "equal_complexity", "history")
    truth = np.asarray([float(row["target"]) for row in test])
    results = {}
    for model in models:
        ridge = choose_ridge(train, model, SEED + 300 + len(model))
        error = np.abs(truth - fit_predict(train, test, model, ridge))
        results[model] = {
            "ridge": ridge,
            "mae": float(error.mean()),
            "median_absolute_error": float(np.median(error)),
        }
    return {
        "train_rows": len(train),
        "test_rows": len(test),
        "test_lineages": len({row["lineage"] for row in test}),
        "note": (
            "Les mêmes lignées peuvent apparaître dans l'apprentissage par leurs cycles antérieurs. "
            "Ce test mesure une extrapolation temporelle, pas une généralisation à une lignée inconnue."
        ),
        "models": results,
    }


def leave_one_dose_out(rows: list[dict]) -> dict:
    models = ("equal_complexity", "history")
    result = {}
    for dose in sorted({float(row["dose_raw"]) for row in rows}):
        train = [row for row in rows if float(row["dose_raw"]) != dose]
        test = [row for row in rows if float(row["dose_raw"]) == dose]
        truth = np.asarray([float(row["target"]) for row in test])
        models_result = {}
        for model in models:
            ridge = choose_ridge(train, model, SEED + int(dose * 10) + len(model))
            error = np.abs(truth - fit_predict(train, test, model, ridge))
            models_result[model] = {"mae": float(error.mean()), "ridge": ridge}
        result[str(dose)] = {
            "test_rows": len(test),
            "test_lineages": len({row["lineage"] for row in test}),
            "models": models_result,
            "equal_complexity_minus_history": (
                models_result["equal_complexity"]["mae"] - models_result["history"]["mae"]
            ),
        }
    return result


def slope_permutation_null(rows: list[dict], draws: int = 100) -> dict:
    folds = lineage_folds(rows, folds=5, seed=SEED + 700)
    true_diffs = []
    ridge_by_fold = []
    for index, test_ids in enumerate(folds):
        train = [row for row in rows if row["lineage"] not in test_ids]
        test = [row for row in rows if row["lineage"] in test_ids]
        truth = np.asarray([float(row["target"]) for row in test])
        ridge_history = choose_ridge(train, "history", SEED + 701 + index)
        ridge_equal = choose_ridge(train, "equal_complexity", SEED + 801 + index)
        history_mae = float(np.mean(np.abs(truth - fit_predict(train, test, "history", ridge_history))))
        equal_mae = float(np.mean(np.abs(truth - fit_predict(train, test, "equal_complexity", ridge_equal))))
        true_diffs.append(equal_mae - history_mae)
        ridge_by_fold.append((ridge_history, ridge_equal))

    rng = np.random.default_rng(SEED + 900)
    null_means = []
    dose_groups: dict[float, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        dose_groups[float(row["dose_raw"])].append(index)
    for _ in range(draws):
        permuted = [dict(row) for row in rows]
        for indices in dose_groups.values():
            slopes = [float(rows[index]["slope"]) for index in indices]
            slopes = list(rng.permutation(slopes))
            for index, slope in zip(indices, slopes):
                permuted[index]["slope"] = float(slope)
        fold_diffs = []
        for fold_index, test_ids in enumerate(folds):
            train = [row for row in permuted if row["lineage"] not in test_ids]
            test = [row for row in permuted if row["lineage"] in test_ids]
            truth = np.asarray([float(row["target"]) for row in test])
            ridge_history, ridge_equal = ridge_by_fold[fold_index]
            history_mae = float(np.mean(np.abs(truth - fit_predict(train, test, "history", ridge_history))))
            equal_mae = float(np.mean(np.abs(truth - fit_predict(train, test, "equal_complexity", ridge_equal))))
            fold_diffs.append(equal_mae - history_mae)
        null_means.append(float(np.mean(fold_diffs)))
    observed = float(np.mean(true_diffs))
    null_array = np.asarray(null_means)
    return {
        "draws": draws,
        "observed_equal_complexity_minus_history": observed,
        "null_mean": float(null_array.mean()),
        "null_ci_2.5": float(np.percentile(null_array, 2.5)),
        "null_ci_97.5": float(np.percentile(null_array, 97.5)),
        "one_sided_fraction_null_at_least_observed": float(
            (1 + np.sum(null_array >= observed)) / (draws + 1)
        ),
        "scope": (
            "La permutation conserve la dose, l'état courant, la moyenne et la dispersion de l'histoire, "
            "mais détruit l'association entre la pente historique et la cible. Elle teste surtout l'apport "
            "de l'ordre temporel résumé par la pente."
        ),
    }


def antibiotic_analysis() -> dict:
    series, doses = load_antibiotic_series()
    rows = build_prediction_rows(series, doses)
    models = (
        "state_only",
        "equal_complexity",
        "history",
        "history_no_slope",
        "history_slope_only",
    )
    cv = cross_validate(rows, models=models, folds=10)
    return {
        "longitudinal_lineages": len(series),
        "prediction_rows": len(rows),
        "dose_levels": sorted({float(row["dose_raw"]) for row in rows}),
        "group_cross_validation": cv,
        "primary_paired_comparison": paired_difference(
            cv, "equal_complexity", "history"
        ),
        "slope_ablation": paired_difference(cv, "history_no_slope", "history"),
        "final_transition_holdout": final_transition_holdout(rows),
        "leave_one_dose_out": leave_one_dose_out(rows),
        "ordered_history_null": slope_permutation_null(rows, draws=1000),
        "limitations": [
            "Un seul antibiotique, l'amikacine.",
            "Les séquences d'exposition ne sont pas manipulées indépendamment des lignées.",
            "Aucun jeu final externe n'est disponible.",
            "Les lignes MIC et persisters de fin d'expérience ne sont pas reliées individuellement aux lignées longitudinales.",
        ],
    }


def shannon(probabilities: np.ndarray) -> float:
    positive = probabilities[probabilities > 0]
    return float(-np.sum(positive * np.log(positive)))


def js_divergence(left: np.ndarray, right: np.ndarray) -> float:
    mean = (left + right) / 2
    return 0.5 * (
        np.sum(np.where(left > 0, left * np.log(left / mean), 0.0))
        + np.sum(np.where(right > 0, right * np.log(right / mean), 0.0))
    )


def exact_slope_permutation_p(values: list[float]) -> dict:
    x = np.arange(1, len(values) + 1, dtype=float)
    observed = float(np.polyfit(x, np.asarray(values), 1)[0])
    slopes = []
    for permutation in itertools.permutations(values):
        slopes.append(float(np.polyfit(x, np.asarray(permutation), 1)[0]))
    slopes_array = np.asarray(slopes)
    return {
        "observed_slope_per_round": observed,
        "exact_two_sided_p": float(
            np.mean(np.abs(slopes_array) >= abs(observed) - 1e-15)
        ),
        "permutations": len(slopes),
    }


def benjamini_hochberg(pvalues: list[float]) -> list[float]:
    count = len(pvalues)
    order = np.argsort(pvalues)
    adjusted = np.empty(count, dtype=float)
    running = 1.0
    for rank_index in range(count - 1, -1, -1):
        original_index = order[rank_index]
        rank = rank_index + 1
        running = min(running, pvalues[original_index] * count / rank)
        adjusted[original_index] = min(1.0, running)
    return adjusted.tolist()


def rna_analysis() -> dict:
    rows = read_csv(DATA / "prebiotic_rna_evolution.csv")
    by_branch_round: dict[tuple[str, int], list[dict[str, str]]] = defaultdict(list)
    by_branch_sequence: dict[tuple[str, str], list[tuple[int, float]]] = defaultdict(list)
    for row in rows:
        branch = row["branch"]
        round_number = int(row["round"])
        frequency = float(row["frequency"])
        by_branch_round[(branch, round_number)].append(row)
        by_branch_sequence[(branch, row["sequence_id"])].append((round_number, frequency))

    branch_metrics = {}
    for branch in sorted({row["branch"] for row in rows}):
        rounds = []
        vectors = []
        sequence_order = sorted({
            row["sequence_id"] for row in rows if row["branch"] == branch
        })
        for round_number in sorted({int(row["round"]) for row in rows if row["branch"] == branch}):
            current = {row["sequence_id"]: float(row["frequency"]) for row in by_branch_round[(branch, round_number)]}
            vector = np.asarray([current.get(sequence, 0.0) for sequence in sequence_order], dtype=float)
            tracked_total = float(vector.sum())
            probability = vector / tracked_total if tracked_total > 0 else np.zeros_like(vector)
            entropy = shannon(probability)
            rounds.append({
                "round": round_number,
                "tracked_frequency_total": tracked_total,
                "shannon_tracked_composition": entropy,
                "effective_tracked_diversity": float(math.exp(entropy)),
                "largest_tracked_share": float(probability.max()) if len(probability) else None,
            })
            vectors.append(probability)
        consecutive_js = [
            {
                "from_round": rounds[index]["round"],
                "to_round": rounds[index + 1]["round"],
                "jensen_shannon_divergence": js_divergence(vectors[index], vectors[index + 1]),
            }
            for index in range(len(vectors) - 1)
        ]
        branch_metrics[branch] = {
            "tracked_sequences": sequence_order,
            "round_metrics": rounds,
            "consecutive_composition_change": consecutive_js,
            "entropy_trend_exact_permutation": exact_slope_permutation_p(
                [row["shannon_tracked_composition"] for row in rounds]
            ),
            "largest_share_trend_exact_permutation": exact_slope_permutation_p(
                [row["largest_tracked_share"] for row in rounds]
            ),
        }

    sequence_tests = []
    for (branch, sequence), values in sorted(by_branch_sequence.items()):
        ordered = sorted(values)
        rho, pvalue = spearmanr(
            [item[0] for item in ordered], [item[1] for item in ordered]
        )
        sequence_tests.append({
            "branch": branch,
            "sequence_id": sequence,
            "spearman_rho_frequency_vs_round": float(rho),
            "p_raw": float(pvalue),
            "first_frequency": ordered[0][1],
            "last_frequency": ordered[-1][1],
            "fold_change_last_over_first": (
                None if ordered[0][1] == 0 else ordered[-1][1] / ordered[0][1]
            ),
        })
    adjusted = benjamini_hochberg([row["p_raw"] for row in sequence_tests])
    for row, qvalue in zip(sequence_tests, adjusted):
        row["q_bh"] = qvalue

    return {
        "observations": len(rows),
        "branches": sorted({row["branch"] for row in rows}),
        "rounds_per_branch": 8,
        "branch_dynamics": branch_metrics,
        "sequence_trends": sequence_tests,
        "significant_sequence_trends_q_0.05": [
            {"branch": row["branch"], "sequence_id": row["sequence_id"], "rho": row["spearman_rho_frequency_vs_round"], "q": row["q_bh"]}
            for row in sequence_tests if row["q_bh"] < 0.05
        ],
        "scope": (
            "Les métriques sont calculées sur les seules séquences suivies dans les tables sources. "
            "Leur fréquence totale ne vaut pas nécessairement 1. La normalisation interne décrit la "
            "composition du sous-ensemble suivi, pas toute la population moléculaire."
        ),
        "not_demonstrated": [
            "filiation entre compartiments",
            "transmission héréditaire de variantes",
            "couplage entre copie, compartimentation et persistance",
            "origine historique du vivant",
        ],
    }


def validate_prebiotic_schema() -> dict:
    validator = ROOT / "03_branche_vivant/programme_prebiotique/valider_lignees.py"
    directory = ROOT / "03_branche_vivant/programme_prebiotique/schema_lignees/gabarit"
    result = subprocess.run(
        [sys.executable, str(validator), "--repertoire", str(directory), "--critere"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return {
        "returncode": result.returncode,
        "schema_valid": result.returncode == 0,
        "synthetic_marker_detected": "synthétique" in result.stdout.lower(),
        "warning": (
            "Le gabarit est volontairement synthétique. Sa validation démontre seulement que le "
            "protocole sait lire et contrôler une future table de lignées."
        ),
        "stdout_tail": result.stdout.strip().splitlines()[-12:],
        "stderr": result.stderr.strip(),
    }


def run() -> dict:
    payload = {
        "status": "completed",
        "branch": "vivant",
        "antibiotic_history_robustness": antibiotic_analysis(),
        "catalytic_rna_frequency_dynamics": rna_analysis(),
        "prebiotic_lineage_schema": validate_prebiotic_schema(),
        "overall_limit": (
            "La branche vivant dispose de données exploratoires pour l'antibiotique et de fréquences "
            "de séquences ARN, mais d'aucune donnée de lignées prébiotiques conforme au protocole."
        ),
    }
    write_json(OUTPUT, payload)
    return payload


if __name__ == "__main__":
    result = run()
    antibiotic = result["antibiotic_history_robustness"]
    print(
        "Vivant: "
        f"{antibiotic['prediction_rows']} prédictions longitudinales et "
        f"{result['catalytic_rna_frequency_dynamics']['observations']} observations ARN."
    )
