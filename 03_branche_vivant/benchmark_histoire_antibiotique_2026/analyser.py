from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "donnees_externes/histoire_antibiotique_donofrio_2026/extracted"
OUT = HERE / "resultats"




def canonicalize_numbers(value: object, significant_digits: int = 13) -> object:
    """Stabilise les nombres sérialisés entre versions de Python/NumPy.

    Les calculs et les décisions utilisent les valeurs complètes. Seule la
    représentation persistée est ramenée à 13 chiffres significatifs, bien
    au-delà de la précision utile de ces mesures et suffisante pour absorber
    les écarts d'arrondi de l'ordre de 10⁻¹⁶ observés entre Python 3.12 et 3.13.
    """
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

def source_reference(path: Path) -> str:
    """Chemin stable, indépendant du dossier local d’extraction."""
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def locate(name: str) -> Path | None:
    matches = sorted(DATA.rglob(name))
    return matches[0] if matches else None


def find_column(columns: list[str], needles: tuple[str, ...]) -> str:
    for needle in needles:
        matches = [column for column in columns if needle in column.lower()]
        if matches:
            return matches[0]
    raise KeyError(f"aucune colonne correspondant à {needles}")


def predictions(data: pd.DataFrame, y: pd.Series, groups: pd.Series, features: list[str]) -> np.ndarray:
    folds = min(5, int(groups.nunique()))
    if folds < 2:
        raise ValueError("au moins deux groupes de souches sont nécessaires")
    preprocessor = ColumnTransformer(
        [("categorical", OneHotEncoder(handle_unknown="ignore"), features)],
        remainder="drop",
    )
    model = Pipeline([("preprocessor", preprocessor), ("model", Ridge(alpha=1.0))])
    return cross_val_predict(model, data, y, groups=groups, cv=GroupKFold(n_splits=folds))


def rmse(y: pd.Series, prediction: np.ndarray) -> float:
    return float(mean_squared_error(y, prediction) ** 0.5)


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
        valid = (
            numeric_y.gt(0)
            & data[[strain, limitation, ancestor, antibiotic]].notna().all(axis=1)
        )
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


if __name__ == "__main__":
    main()
