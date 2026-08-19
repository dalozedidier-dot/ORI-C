from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "donnees_externes/histoire_antibiotique_donofrio_2026/extracted"
OUT = HERE / "resultats"
FROZEN_GAIN_THRESHOLD_PERCENT = 5.0


def canonicalize_numbers(value: object, significant_digits: int = 13) -> object:
    """Stabilise la sérialisation sans modifier les calculs ni les décisions."""
    if isinstance(value, float):
        if not np.isfinite(value):
            return value
        return float(format(value, f".{significant_digits}g"))
    if isinstance(value, dict):
        return {key: canonicalize_numbers(item, significant_digits) for key, item in value.items()}
    if isinstance(value, list):
        return [canonicalize_numbers(item, significant_digits) for item in value]
    if isinstance(value, tuple):
        return [canonicalize_numbers(item, significant_digits) for item in value]
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_reference(path: Path) -> str:
    """Chemin portable quand la donnée est dans le dépôt, sinon chemin fourni."""
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(resolved)


def locate(name: str) -> Path | None:
    matches = sorted(DATA.rglob(name))
    return matches[0] if matches else None


def find_column(columns: list[str], needles: tuple[str, ...]) -> str:
    for needle in needles:
        matches = [column for column in columns if needle in column.lower()]
        if matches:
            return matches[0]
    raise KeyError(f"aucune colonne correspondant à {needles}")


def load_table(path: Path, sheet: str | int | None = None) -> pd.DataFrame:
    """Charge directement les formats tabulaires réels utilisés par les dépôts publics."""
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".tsv", ".tab"}:
        return pd.read_csv(path, sep="\t")
    if suffix == ".txt":
        return pd.read_csv(path, sep=None, engine="python")
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path, sheet_name=0 if sheet is None else sheet)
    raise ValueError(f"format tabulaire non pris en charge: {suffix}")


def _preprocessor(data: pd.DataFrame, features: list[str]) -> ColumnTransformer:
    categorical = [name for name in features if not is_numeric_dtype(data[name])]
    numeric = [name for name in features if is_numeric_dtype(data[name])]
    transformers = []
    if categorical:
        transformers.append(("categorical", OneHotEncoder(handle_unknown="ignore"), categorical))
    if numeric:
        transformers.append(("numeric", StandardScaler(), numeric))
    if not transformers:
        raise ValueError("au moins une variable prédictive est requise")
    return ColumnTransformer(transformers, remainder="drop")


def predictions(data: pd.DataFrame, y: pd.Series, groups: pd.Series, features: list[str]) -> np.ndarray:
    folds = min(5, int(groups.nunique()))
    if folds < 2:
        raise ValueError("au moins deux groupes indépendants sont nécessaires")
    model = Pipeline(
        [
            ("preprocessor", _preprocessor(data, features)),
            ("model", Ridge(alpha=1.0)),
        ]
    )
    return cross_val_predict(model, data, y, groups=groups, cv=GroupKFold(n_splits=folds))


def rmse(y: pd.Series | np.ndarray, prediction: np.ndarray) -> float:
    return float(mean_squared_error(y, prediction) ** 0.5)


def _gain_percent(y: np.ndarray, state_prediction: np.ndarray, history_prediction: np.ndarray) -> float:
    state_rmse = rmse(y, state_prediction)
    if state_rmse <= 0.0:
        raise ValueError("state-only RMSE must be > 0")
    history_rmse = rmse(y, history_prediction)
    return 100.0 * (state_rmse - history_rmse) / state_rmse


def _group_bootstrap_gain(
    y: np.ndarray,
    state_prediction: np.ndarray,
    history_prediction: np.ndarray,
    groups: np.ndarray,
    *,
    repeats: int,
    seed: int,
) -> tuple[float, float]:
    """Rééchantillonne les unités indépendantes, jamais les lignes isolées."""
    if repeats < 100:
        raise ValueError("bootstrap_repeats must be >= 100")
    unique = np.asarray(pd.unique(groups), dtype=object)
    if len(unique) < 5:
        raise ValueError("at least five independent groups are required")
    by_group = {group: np.flatnonzero(groups == group) for group in unique}
    rng = np.random.default_rng(seed)
    gains = np.empty(repeats, dtype=float)
    for i in range(repeats):
        sampled = rng.choice(unique, size=len(unique), replace=True)
        indices = np.concatenate([by_group[group] for group in sampled])
        gains[i] = _gain_percent(y[indices], state_prediction[indices], history_prediction[indices])
    return float(np.quantile(gains, 0.025)), float(np.quantile(gains, 0.975))


def _permuted_group_history(
    data: pd.DataFrame,
    *,
    group_column: str,
    history_feature: str,
    rng: np.random.Generator,
) -> pd.DataFrame:
    counts = data.groupby(group_column, sort=False)[history_feature].nunique(dropna=False)
    if int(counts.max()) != 1:
        raise ValueError("history must be constant within each independent group")
    group_history = data.groupby(group_column, sort=False)[history_feature].first()
    shuffled = group_history.to_numpy(copy=True)
    rng.shuffle(shuffled)
    mapping = dict(zip(group_history.index.tolist(), shuffled.tolist()))
    result = data.copy()
    result[history_feature] = result[group_column].map(mapping)
    return result


def evaluate_independent_replication(
    data: pd.DataFrame,
    *,
    outcome_column: str,
    group_column: str,
    state_features: list[str],
    history_feature: str,
    gain_threshold_percent: float = FROZEN_GAIN_THRESHOLD_PERCENT,
    bootstrap_repeats: int = 5000,
    permutation_repeats: int = 1000,
    seed: int = 20260811,
) -> dict[str, object]:
    """Applique la règle gelée de PRED-VIVANT-HISTOIRE-001 à une table réelle indépendante."""
    if float(gain_threshold_percent) != FROZEN_GAIN_THRESHOLD_PERCENT:
        raise ValueError("PRED-VIVANT-HISTOIRE-001 frozen gain threshold is exactly 5 percent")
    required = [outcome_column, group_column, *state_features, history_feature]
    missing = [name for name in required if name not in data.columns]
    if missing:
        raise ValueError("missing columns: " + ", ".join(missing))
    if not state_features:
        raise ValueError("state_features must contain at least one present-state variable")

    frame = data[required].copy()
    numeric = pd.to_numeric(frame[outcome_column], errors="coerce")
    valid = numeric.gt(0) & frame[[group_column, *state_features, history_feature]].notna().all(axis=1)
    frame = frame.loc[valid].reset_index(drop=True)
    numeric = numeric.loc[valid].reset_index(drop=True)
    if frame.empty:
        raise ValueError("no valid positive MIC rows")

    groups = frame[group_column].astype(str)
    if int(groups.nunique()) < 5:
        raise ValueError("at least five independent groups are required")
    history_counts = frame.groupby(group_column, sort=False)[history_feature].nunique(dropna=False)
    if int(history_counts.max()) != 1:
        raise ValueError("history_feature must be constant within each independent group")

    y = np.log2(numeric.to_numpy(dtype=float))
    y_series = pd.Series(y)
    state_prediction = predictions(frame, y_series, groups, state_features)
    history_features = [*state_features, history_feature]
    history_prediction = predictions(frame, y_series, groups, history_features)
    rmse_state = rmse(y, state_prediction)
    rmse_history = rmse(y, history_prediction)
    gain = 100.0 * (rmse_state - rmse_history) / rmse_state

    q025, q975 = _group_bootstrap_gain(
        y,
        state_prediction,
        history_prediction,
        groups.to_numpy(),
        repeats=bootstrap_repeats,
        seed=seed + 1,
    )

    if permutation_repeats < 20:
        raise ValueError("permutation_repeats must be >= 20")
    rng = np.random.default_rng(seed + 2)
    perm_gains = np.empty(permutation_repeats, dtype=float)
    for i in range(permutation_repeats):
        shuffled = _permuted_group_history(
            frame,
            group_column=group_column,
            history_feature=history_feature,
            rng=rng,
        )
        shuffled_prediction = predictions(shuffled, y_series, groups, history_features)
        perm_gains[i] = 100.0 * (rmse_state - rmse(y, shuffled_prediction)) / rmse_state
    p_value = float((1 + np.sum(perm_gains >= gain)) / (1 + permutation_repeats))

    components = {
        "gain_at_least_5_percent": bool(gain >= gain_threshold_percent),
        "bootstrap_gain_strictly_positive": bool(q025 > 0.0),
        "permutation_p_at_most_0_05": bool(p_value <= 0.05),
    }
    return canonicalize_numbers(
        {
            "schema": "oric.pred-vivant-histoire-independent.v1",
            "prediction_id": "PRED-VIVANT-HISTOIRE-001",
            "rows": int(len(frame)),
            "independent_groups": int(groups.nunique()),
            "grouped_folds": min(5, int(groups.nunique())),
            "outcome_transform": "log2(MIC)",
            "rmse_state_only": rmse_state,
            "rmse_state_plus_history": rmse_history,
            "history_gain_percent": gain,
            "gain_threshold_percent": gain_threshold_percent,
            "bootstrap_gain_q025_percent": q025,
            "bootstrap_gain_q975_percent": q975,
            "bootstrap_unit": group_column,
            "bootstrap_repeats": int(bootstrap_repeats),
            "permutation_scheme": "history labels permuted between independent groups; within-group identity preserved",
            "permutation_repeats": int(permutation_repeats),
            "permutation_p": p_value,
            "decision_components": components,
            "success": bool(all(components.values())),
            "thresholds_moved": False,
        }
    )


def analyse_independent_file(
    path: Path,
    *,
    outcome_column: str,
    group_column: str,
    state_features: list[str],
    history_feature: str,
    sheet: str | int | None = None,
    bootstrap_repeats: int = 5000,
    permutation_repeats: int = 1000,
    seed: int = 20260811,
) -> dict[str, object]:
    data = load_table(path, sheet=sheet)
    result = evaluate_independent_replication(
        data,
        outcome_column=outcome_column,
        group_column=group_column,
        state_features=state_features,
        history_feature=history_feature,
        bootstrap_repeats=bootstrap_repeats,
        permutation_repeats=permutation_repeats,
        seed=seed,
    )
    return {
        "status": "analysed_independent_real_dataset",
        "source_file": source_reference(path),
        "source_sha256": sha256(path),
        **result,
    }


def main() -> dict[str, object]:
    path = locate("Figure_3_N-lim_Expt_MIC_Raw_Data.csv")
    if path is None:
        result = {
            "status": "waiting_for_external_data",
            "missing": ["Figure_3_N-lim_Expt_MIC_Raw_Data.csv"],
        }
    else:
        data = pd.read_csv(path)
        columns = [str(column) for column in data.columns]
        y_column = find_column(columns, ("mic",))
        strain = find_column(columns, ("strain", "isolate", "clone"))
        limitation = find_column(columns, ("limitation", "environment", "treatment"))
        ancestor = find_column(columns, ("ancestor", "history", "lineage"))
        antibiotic = find_column(columns, ("antibiotic", "drug"))
        numeric_y = pd.to_numeric(data[y_column], errors="coerce")
        valid = numeric_y.gt(0) & data[[strain, limitation, ancestor, antibiotic]].notna().all(axis=1)
        data = data.loc[valid].copy().reset_index(drop=True)
        y = np.log2(numeric_y.loc[valid].reset_index(drop=True))
        groups = data[strain].astype(str)

        state_features = [limitation, antibiotic]
        history_features = [limitation, antibiotic, ancestor]
        state_prediction = predictions(data, y, groups, state_features)
        history_prediction = predictions(data, y, groups, history_features)
        rmse_state = rmse(y, state_prediction)
        rmse_history = rmse(y, history_prediction)

        rng = np.random.default_rng(20260805)
        shuffled_rmses: list[float] = []
        for _ in range(200):
            shuffled = data.copy()
            shuffled[ancestor] = rng.permutation(shuffled[ancestor].to_numpy())
            shuffled_prediction = predictions(shuffled, y, groups, history_features)
            shuffled_rmses.append(rmse(y, shuffled_prediction))
        shuffled_mean = float(np.mean(shuffled_rmses))
        p_history_vs_shuffled = float(
            (1 + sum(value <= rmse_history for value in shuffled_rmses)) / (1 + len(shuffled_rmses))
        )
        result = {
            "status": "analysed",
            "source_file": source_reference(path),
            "rows": int(len(data)),
            "group_count": int(groups.nunique()),
            "grouped_folds": min(5, int(groups.nunique())),
            "columns": {
                "outcome": y_column,
                "strain_group": strain,
                "present_limitation": limitation,
                "history": ancestor,
                "antibiotic": antibiotic,
            },
            "rmse_state_only": rmse_state,
            "rmse_state_plus_history": rmse_history,
            "history_gain_percent": 100.0 * (rmse_state - rmse_history) / rmse_state,
            "same_complexity_shuffled_history_rmse_mean": shuffled_mean,
            "history_vs_shuffled_gain_percent": 100.0 * (shuffled_mean - rmse_history) / shuffled_mean,
            "permutation_p_history_better_than_shuffled": p_history_vs_shuffled,
            "permutations": len(shuffled_rmses),
            "decision_components": {
                "history_beats_state": rmse_history < rmse_state,
                "history_beats_same_complexity_shuffled_control": rmse_history < shuffled_mean,
                "permutation_support": p_history_vs_shuffled < 0.05,
            },
        }
        result["verdict"] = (
            "history_supported_against_both_controls"
            if all(result["decision_components"].values())
            else "history_not_supported_against_all_controls"
        )
        result["limit"] = (
            "Le jeu est externe mais public avant l'analyse ORI-C. Le test est confirmatoire dans sa "
            "structure, sans être une collecte prospective aveugle."
        )
    result = canonicalize_numbers(result)
    OUT.mkdir(exist_ok=True)
    (OUT / "RESULTAT.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline=""
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--independent-data", type=Path)
    parser.add_argument("--outcome-column")
    parser.add_argument("--group-column")
    parser.add_argument("--state-features", nargs="+")
    parser.add_argument("--history-feature")
    parser.add_argument("--sheet")
    parser.add_argument("--bootstrap-repeats", type=int, default=5000)
    parser.add_argument("--permutation-repeats", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20260811)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.independent_data is None:
        raise SystemExit("--independent-data is required; the original D'Onofrio analysis remains in analyser.py")
    else:
        required = {
            "--outcome-column": args.outcome_column,
            "--group-column": args.group_column,
            "--state-features": args.state_features,
            "--history-feature": args.history_feature,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise SystemExit("required with --independent-data: " + ", ".join(missing))
        result = analyse_independent_file(
            args.independent_data,
            outcome_column=args.outcome_column,
            group_column=args.group_column,
            state_features=list(args.state_features),
            history_feature=args.history_feature,
            sheet=args.sheet,
            bootstrap_repeats=args.bootstrap_repeats,
            permutation_repeats=args.permutation_repeats,
            seed=args.seed,
        )
        output = args.output or (OUT / "RESULTAT_REPLICATION_INDEPENDANTE.json")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, ensure_ascii=False))
