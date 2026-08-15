"""Approfondissement NIT sur les donnees reelles Petrungaro 2026.

L'analyse distingue strictement les populations phenotypees de la sous-cohorte
sequencee. Aucune jointure n'est inventee entre leurs identifiants incompatibles.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "resultats"
POPULATIONS = OUT / "PETRUNGARO_POPULATIONS.csv"
MUTATIONS = ROOT / "donnees_externes/petrungaro_2026/41467_2026_76025_MOESM3_ESM.csv"
SEED = 20260815
N_BOOT = 5000
N_PERM = 199


def ridge_predictions(y: np.ndarray, blocks: list[np.ndarray], split: np.ndarray) -> np.ndarray:
    result = np.empty(len(y))
    for fold in sorted(set(split)):
        test = split == fold
        train = ~test
        train_blocks = []
        test_blocks = []
        for block in blocks:
            values = block.astype(float)
            mean = values[train].mean(axis=0)
            scale = values[train].std(axis=0)
            scale[scale == 0] = 1.0
            train_blocks.append((values[train] - mean) / scale)
            test_blocks.append((values[test] - mean) / scale)
        x_train = np.column_stack(train_blocks)
        x_test = np.column_stack(test_blocks)
        # Le centrage separe conserve un intercept non penalise.
        feature_mean = x_train.mean(axis=0)
        response_mean = y[train].mean()
        centered_train = x_train - feature_mean
        centered_test = x_test - feature_mean
        beta = np.linalg.solve(centered_train.T @ centered_train + np.eye(centered_train.shape[1]), centered_train.T @ (y[train] - response_mean))
        result[test] = response_mean + centered_test @ beta
    return result


def rmse(y: np.ndarray, prediction: np.ndarray, indices: np.ndarray | None = None) -> float:
    if indices is None:
        indices = np.arange(len(y))
    return float(np.sqrt(np.mean((y[indices] - prediction[indices]) ** 2)))


def icc_groups(groups: list[np.ndarray]) -> float:
    n_total = sum(map(len, groups))
    grand = np.concatenate(groups).mean()
    between = sum(len(g) * (g.mean() - grand) ** 2 for g in groups) / (len(groups) - 1)
    within = sum(((g - g.mean()) ** 2).sum() for g in groups) / (n_total - len(groups))
    harmonic_n = (n_total - sum(len(g) ** 2 for g in groups) / n_total) / (len(groups) - 1)
    return float((between - within) / (between + (harmonic_n - 1) * within))


def icc_one_way(frame: pd.DataFrame) -> float:
    groups = [g.future_log10_IC50.to_numpy(float) for _, g in frame.groupby("genetic_background") if len(g) >= 2]
    return icc_groups(groups)


def phenotype_nit(rng: np.random.Generator) -> tuple[pd.DataFrame, dict[str, object]]:
    frame = pd.read_csv(POPULATIONS)
    frame = frame.loc[frame.antibiotic.eq("NIT")].copy().reset_index(drop=True)
    x = frame[["initial_log10_IC50"]].to_numpy(float)
    y = frame.future_log10_IC50.to_numpy(float)
    split = frame.groupby("genetic_background", sort=True).cumcount().to_numpy() % 3
    px = ridge_predictions(y, [x], split)
    frame["X_cross_validated_residual"] = y - px
    by_background = frame.groupby("genetic_background", as_index=False).agg(
        n_populations=("population_id", "size"),
        initial_log10_IC50=("initial_log10_IC50", "first"),
        mean_future_log10_IC50=("future_log10_IC50", "mean"),
        sd_future_log10_IC50=("future_log10_IC50", "std"),
        mean_resistance_change_log10=("resistance_change_log10", "mean"),
        background_effect_after_X=("X_cross_validated_residual", "mean"),
        sd_effect_after_X=("X_cross_validated_residual", "std"),
    )
    icc = icc_one_way(frame)
    replicate_groups = [g.future_log10_IC50.to_numpy(float) for _, g in frame.groupby("genetic_background") if len(g) >= 2]
    boot = [icc_groups([replicate_groups[i] for i in rng.integers(0, len(replicate_groups), len(replicate_groups))]) for _ in range(N_BOOT)]
    return by_background.sort_values("background_effect_after_X", ascending=False), {
        "n_populations": int(len(frame)),
        "n_backgrounds": int(frame.genetic_background.nunique()),
        "background_effect_range_log10_IC50": [float(by_background.background_effect_after_X.min()), float(by_background.background_effect_after_X.max())],
        "replicate_ICC_future_log10_IC50": icc,
        "replicate_ICC_background_bootstrap_ci95": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))],
        "unit_of_bootstrap": "genetic background",
    }


def sequenced_nit(rng: np.random.Generator) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    raw = pd.read_csv(MUTATIONS)
    raw = raw.loc[raw.treatment.eq("NIT")].dropna(subset=["title", "gene_deletion_in_ancestor", "ini_IC50", "IC50", "mutated_gene_name"]).copy()
    raw = raw.drop_duplicates(["title", "mutated_gene_name"])
    population = raw.groupby("title", as_index=False).agg(
        genetic_background=("gene_deletion_in_ancestor", "first"),
        background_COG_family=("COG_cat_gene_deletion", "first"),
        initial_IC50=("ini_IC50", "first"),
        future_IC50=("IC50", "first"),
        mutation_genes=("mutated_gene_name", lambda x: "|".join(sorted(set(map(str, x))))),
        n_distinct_mutated_genes=("mutated_gene_name", "nunique"),
    )
    population["initial_log10_IC50"] = np.log10(population.initial_IC50.astype(float))
    population["future_log10_IC50"] = np.log10(population.future_IC50.astype(float))
    population["resistance_change_log10"] = population.future_log10_IC50 - population.initial_log10_IC50
    prevalence = raw.groupby("mutated_gene_name").title.nunique()
    # Un singleton ne peut jamais etre appris puis retrouve hors echantillon.
    genes = sorted(map(str, prevalence.loc[prevalence >= 2].index))
    gene_matrix = np.column_stack([population.mutation_genes.str.split("|").map(lambda values, gene=gene: gene in values).to_numpy(float) for gene in genes])
    backgrounds = sorted(population.genetic_background.astype(str).unique())
    background_matrix = np.column_stack([(population.genetic_background.astype(str) == bg).to_numpy(float) for bg in backgrounds])
    x = population[["initial_log10_IC50"]].to_numpy(float)
    y = population.future_log10_IC50.to_numpy(float)
    split = population.groupby("genetic_background", sort=True).cumcount().to_numpy() % 3
    predictions = {
        "X": ridge_predictions(y, [x], split),
        "X_plus_m": ridge_predictions(y, [x, background_matrix], split),
        "X_plus_mutations": ridge_predictions(y, [x, gene_matrix], split),
        "X_plus_m_plus_mutations": ridge_predictions(y, [x, background_matrix, gene_matrix], split),
    }
    rmses = {name: rmse(y, pred) for name, pred in predictions.items()}
    background_ids = population.genetic_background.astype(str).unique()
    boot = []
    for _ in range(N_BOOT):
        selected = rng.choice(background_ids, len(background_ids), replace=True)
        indices = np.concatenate([np.flatnonzero(population.genetic_background.astype(str).eq(bg)) for bg in selected])
        boot.append({name: rmse(y, pred, indices) for name, pred in predictions.items()})
    original_m = rmses["X"] - rmses["X_plus_m"]
    residual_m = rmses["X_plus_mutations"] - rmses["X_plus_m_plus_mutations"]
    mutation_gain = 100 * (rmses["X"] - rmses["X_plus_mutations"]) / rmses["X"]
    boot_mutation_gain = [100 * (b["X"] - b["X_plus_mutations"]) / b["X"] for b in boot]
    attenuation = 100 * (1 - residual_m / original_m) if original_m != 0 else None

    bins = pd.qcut(population.initial_log10_IC50, q=min(5, population.initial_log10_IC50.nunique()), duplicates="drop")
    strata = population.groupby(bins, observed=True).indices
    null = []
    for _ in range(N_PERM):
        permuted = gene_matrix.copy()
        for indices in strata.values():
            permuted[indices] = permuted[rng.permutation(indices)]
        pred = ridge_predictions(y, [x, permuted], split)
        null.append(100 * (rmses["X"] - rmse(y, pred)) / rmses["X"])

    population["X_residual"] = y - predictions["X"]
    family = population.groupby("background_COG_family", as_index=False).agg(
        n_populations=("title", "size"),
        n_backgrounds=("genetic_background", "nunique"),
        mean_resistance_change_log10=("resistance_change_log10", "mean"),
        mean_effect_after_X=("X_residual", "mean"),
        median_distinct_mutated_genes=("n_distinct_mutated_genes", "median"),
    ).sort_values("mean_effect_after_X", ascending=False)
    replicated_families = family.loc[family.n_backgrounds >= 2]
    mutation_robust = np.quantile(boot_mutation_gain, 0.025) > 0 and (1 + np.sum(np.asarray(null) >= mutation_gain)) / (N_PERM + 1) <= 0.05
    result = {
        "n_sequenced_populations": int(len(population)),
        "n_genetic_backgrounds": int(population.genetic_background.nunique()),
        "n_recurrent_mutated_genes_encoded": int(len(genes)),
        "gene_eligibility": "observed in at least two independent sequenced populations; singleton genes excluded before modelling",
        "cross_validation": "replicate-position folds within genetic background; ridge penalty fixed at 1",
        "rmse_log10_IC50": rmses,
        "mutation_incremental_gain_vs_X_percent": mutation_gain,
        "mutation_gain_background_bootstrap_ci95_percent": [float(np.quantile(boot_mutation_gain, 0.025)), float(np.quantile(boot_mutation_gain, 0.975))],
        "mutation_profile_permutation_p_one_sided_within_initial_IC50_bins": float((1 + np.sum(np.asarray(null) >= mutation_gain)) / (N_PERM + 1)),
        "mutation_profile_permutations": N_PERM,
        "minimum_attainable_permutation_p": 1 / (N_PERM + 1),
        "m_incremental_rmse_before_mutations": original_m,
        "m_incremental_rmse_after_mutations": residual_m,
        "m_effect_attenuation_after_mutations_percent": attenuation,
        "replicated_background_families_ranked_by_effect_after_X": replicated_families[["background_COG_family", "n_backgrounds", "mean_effect_after_X"]].to_dict(orient="records"),
        "mutation_incremental_prediction_verdict": "supports" if mutation_robust else "does_not_support_bootstrap_crosses_zero",
        "chain_verdict": "indeterminate_associative_attenuation_without_robust_mutation_increment",
        "interpretation_limit": "retrospective predictive decomposition; mutations are post-treatment and this is not causal mediation",
    }
    return population, family, result


def main() -> None:
    rng = np.random.default_rng(SEED)
    backgrounds, phenotype = phenotype_nit(rng)
    sequenced, families, chain = sequenced_nit(rng)
    backgrounds.to_csv(OUT / "PETRUNGARO_NIT_BACKGROUND_EFFECTS.csv", index=False, lineterminator="\n")
    sequenced.to_csv(OUT / "PETRUNGARO_NIT_SEQUENCED_CHAIN.csv", index=False, lineterminator="\n")
    families.to_csv(OUT / "PETRUNGARO_NIT_BACKGROUND_FAMILIES.csv", index=False, lineterminator="\n")
    result = {
        "schema": "oric.petrungaro-nit-deepening.v1",
        "status": "retrospective_real_data_analysis",
        "phenotype_replicability": phenotype,
        "m_to_mutation_path_to_R": chain,
        "qualification": {
            "real_data": True,
            "synthetic_or_simulated_scientific_data": False,
            "independent_external_validation": False,
            "causal_mediation_claimed": False,
        },
    }
    (OUT / "RESULTAT_PETRUNGARO_NIT_APPROFONDI.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
