"""Analyse rétrospective Wong–Seguin 2015 sur données Dryad réelles.

Cette analyse répond à une question compatible avec le plan publié : la
mutation fondatrice apporte-t-elle une information sur la MIC finale au-delà
de la MIC et du gène du progéniteur ? Elle ne constitue pas une réplication
stricte de D'Onofrio et ne reçoit aucun crédit §XIV.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "donnees_externes/wong_seguin_2015/extracted"
OUTPUT = HERE / "resultats/RESULTAT_WONG_SEGUIN_2015.json"
TABLE = HERE / "resultats/WONG_SEGUIN_2015_ANALYSIS_READY.tsv"
SEED = 20260814
BOOTSTRAP_REPEATS = 5000
PERMUTATION_REPEATS = 5000


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare() -> pd.DataFrame:
    mic = pd.read_csv(SOURCE / "MIC-data.tsv", sep="\t")
    fitness = pd.read_csv(SOURCE / "Fitness_evolved.tsv", sep="\t")
    progenitors = pd.read_csv(SOURCE / "Data_by_progenitor.tsv", sep="\t")

    evolved = mic.loc[mic["Progenitor"].notna()].copy()
    evolved["Population"] = evolved["Strain"].astype(str)
    evolved["Progenitor_id"] = evolved["Progenitor"].astype(int)
    fitness = fitness.copy()
    fitness["Population"] = fitness["Population"].astype(str)
    progenitors = progenitors.rename(
        columns={
            "Genotype": "Progenitor_id",
            "MIC_baseline": "Progenitor_MIC_ng_mL",
            "Gene": "Progenitor_gene_source",
            "Mutation": "Progenitor_mutation_source",
        }
    )

    baseline = mic.loc[mic["Progenitor"].isna() & mic["Strain"].astype(str).ne("WT"), ["Strain", "MIC (ng/mL)"]].copy()
    baseline["Progenitor_id"] = baseline["Strain"].astype(int)
    baseline = baseline.rename(columns={"MIC (ng/mL)": "Progenitor_MIC_ng_mL"})

    joined = evolved.merge(
        fitness[["Population", "Progenitor_gene", "Progenitor_mutation"]],
        on="Population",
        how="left",
        validate="one_to_one",
    ).merge(
        baseline[["Progenitor_id", "Progenitor_MIC_ng_mL"]],
        on="Progenitor_id",
        how="left",
        validate="many_to_one",
    ).merge(
        progenitors[["Progenitor_id", "Progenitor_gene_source", "Progenitor_mutation_source"]],
        on="Progenitor_id",
        how="left",
        validate="many_to_one",
    )
    if joined.isna().any().any():
        missing = joined.columns[joined.isna().any()].tolist()
        raise ValueError(f"appariement incomplet: {missing}")
    if not (joined["Progenitor_gene"] == joined["Progenitor_gene_source"]).all():
        raise ValueError("désaccord sur le gène progéniteur")
    normalized_fitness_mutation = joined["Progenitor_mutation"].str.replace("marR_", "", regex=False).str.replace("gyrA_", "", regex=False)
    if not (normalized_fitness_mutation == joined["Progenitor_mutation_source"]).all():
        raise ValueError("désaccord sur la mutation progénitrice")

    result = joined[[
        "Population", "Progenitor_id", "Progenitor_MIC_ng_mL",
        "Progenitor_gene", "Progenitor_mutation", "MIC (ng/mL)", "Fold-MIC",
    ]].rename(columns={"MIC (ng/mL)": "Evolved_MIC_ng_mL"})
    if len(result) != 46 or result["Population"].nunique() != 46:
        raise ValueError("46 populations évoluées indépendantes étaient attendues")
    return result.sort_values("Population").reset_index(drop=True)


def design(train: pd.DataFrame, test: pd.DataFrame, features: list[str]) -> tuple[np.ndarray, np.ndarray]:
    train_parts = [np.ones((len(train), 1), dtype=float)]
    test_parts = [np.ones((len(test), 1), dtype=float)]
    for feature in features:
        if pd.api.types.is_numeric_dtype(train[feature]):
            mean = float(train[feature].mean())
            scale = float(train[feature].std(ddof=0)) or 1.0
            train_parts.append(((train[[feature]].to_numpy(dtype=float) - mean) / scale))
            test_parts.append(((test[[feature]].to_numpy(dtype=float) - mean) / scale))
        else:
            levels = sorted(train[feature].astype(str).unique())
            train_parts.append(np.column_stack([(train[feature].astype(str) == level).to_numpy(float) for level in levels]))
            test_parts.append(np.column_stack([(test[feature].astype(str) == level).to_numpy(float) for level in levels]))
    return np.column_stack(train_parts), np.column_stack(test_parts)


def cross_validated_prediction(frame: pd.DataFrame, features: list[str]) -> np.ndarray:
    y = np.log2(frame["Evolved_MIC_ng_mL"].to_numpy(dtype=float))
    prediction = np.empty(len(frame), dtype=float)
    folds = np.arange(len(frame)) % 5
    for fold in range(5):
        test_mask = folds == fold
        train = frame.loc[~test_mask]
        test = frame.loc[test_mask]
        x_train, x_test = design(train, test, features)
        penalty = np.eye(x_train.shape[1])
        penalty[0, 0] = 0.0
        coefficients = np.linalg.solve(x_train.T @ x_train + penalty, x_train.T @ y[~test_mask])
        prediction[test_mask] = x_test @ coefficients
    return prediction


def gain(y: np.ndarray, state: np.ndarray, history: np.ndarray) -> tuple[float, float, float]:
    state_rmse = float(np.sqrt(np.mean((y - state) ** 2)))
    history_rmse = float(np.sqrt(np.mean((y - history) ** 2)))
    return state_rmse, history_rmse, 100.0 * (state_rmse - history_rmse) / state_rmse


def main() -> dict[str, object]:
    frame = prepare()
    TABLE.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(TABLE, sep="\t", index=False, lineterminator="\n")
    y = np.log2(frame["Evolved_MIC_ng_mL"].to_numpy(dtype=float))
    state_features = ["Progenitor_MIC_ng_mL", "Progenitor_gene"]
    history_features = [*state_features, "Progenitor_mutation"]
    state_prediction = cross_validated_prediction(frame, state_features)
    history_prediction = cross_validated_prediction(frame, history_features)
    state_rmse, history_rmse, observed_gain = gain(y, state_prediction, history_prediction)

    rng = np.random.default_rng(SEED)
    bootstrap = np.empty(BOOTSTRAP_REPEATS)
    for index in range(BOOTSTRAP_REPEATS):
        sample = rng.integers(0, len(frame), len(frame))
        bootstrap[index] = gain(y[sample], state_prediction[sample], history_prediction[sample])[2]

    permutation = np.empty(PERMUTATION_REPEATS)
    strata = frame.groupby(state_features, sort=False).indices
    for index in range(PERMUTATION_REPEATS):
        shuffled = frame.copy()
        for indices in strata.values():
            values = shuffled.loc[indices, "Progenitor_mutation"].to_numpy(copy=True)
            rng.shuffle(values)
            shuffled.loc[indices, "Progenitor_mutation"] = values
        permuted_prediction = cross_validated_prediction(shuffled, history_features)
        permutation[index] = gain(y, state_prediction, permuted_prediction)[2]
    p_value = float((1 + np.sum(permutation >= observed_gain)) / (1 + PERMUTATION_REPEATS))

    result = {
        "schema": "oric.wong-seguin-real-retrospective.v1",
        "status": "analysed_real_external_retrospective_dataset",
        "dataset_doi": "10.5061/dryad.36td2",
        "source": "donnees_externes/wong_seguin_2015/SOURCE.json",
        "analysis_ready_table": str(TABLE.relative_to(ROOT)).replace("\\", "/"),
        "analysis_ready_sha256": sha256(TABLE),
        "mapping": {
            "independent_unit": "evolved population",
            "n_independent_units": int(frame["Population"].nunique()),
            "outcome_R": "endpoint evolved-population ciprofloxacin MIC (ng/mL), log2 transformed",
            "present_state_X": ["progenitor ciprofloxacin MIC", "progenitor target gene"],
            "history_H": "exact founding resistance mutation",
            "history_defined_before_outcome": True,
            "history_distinct_from_X": True,
        },
        "method": {
            "validation": "five-fold held-out evolved populations",
            "model": "ridge alpha=1 with training-fold scaling and one-hot encoding",
            "bootstrap": "5000 resamples of evolved populations",
            "permutation": "5000 shuffles of founding mutation within progenitor-MIC × target-gene strata",
            "seed": SEED,
        },
        "results": {
            "rmse_state_only_log2_MIC": state_rmse,
            "rmse_state_plus_history_log2_MIC": history_rmse,
            "history_gain_percent": observed_gain,
            "bootstrap_gain_q025_percent": float(np.quantile(bootstrap, 0.025)),
            "bootstrap_gain_q975_percent": float(np.quantile(bootstrap, 0.975)),
            "permutation_p_one_sided": p_value,
            "permutation_null_gain_mean_percent": float(np.mean(permutation)),
        },
        "decision_components": {
            "history_gain_positive": bool(observed_gain > 0.0),
            "bootstrap_lower_bound_positive": bool(np.quantile(bootstrap, 0.025) > 0.0),
            "permutation_p_at_most_0_05": bool(p_value <= 0.05),
        },
        "verdict": "does_not_support_incremental_founder_mutation_information",
        "qualification": {
            "real_data": True,
            "synthetic_or_simulated_scientific_data": False,
            "post_hoc_dataset_specific_analysis": True,
            "strict_donofrio_replication": False,
            "prediction_PRED_VIVANT_HISTOIRE_001_credit": False,
            "section_XIV_credit": False,
            "reason": "founding genotype is not the frozen C/N treatment-history construct and this mapping was specified after the public data were inspected",
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


if __name__ == "__main__":
    main()
