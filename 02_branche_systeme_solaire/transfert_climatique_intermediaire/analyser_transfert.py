#!/usr/bin/env python3
"""Teste le transfert orbite -> insolation -> réponse climatique hors échantillon.

Le calcul hybride remplace uniquement l'excentricité La2004 par l'excentricité
issue de l'intégration N-corps ORI-C. L'obliquité et la longitude du périhélie
restent celles de La2004. Ce paquet n'est donc ni un GCM ni un modèle complet
Terre-Lune-rotation-marées.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASTRO = ROOT / "02_branche_systeme_solaire" / "couche_astronomique"
MEMORY = ROOT / "02_branche_systeme_solaire" / "couche_memoire_historique"
OUT = HERE / "resultats"


def daily_mean_insolation(latitude_deg, solar_longitude_rad, eccentricity, obliquity_rad, varpi_rad, solar_constant=1365.0):
    latitude = np.deg2rad(latitude_deg)
    solar_longitude = np.asarray(solar_longitude_rad, dtype=float)
    eccentricity = np.asarray(eccentricity, dtype=float)
    obliquity = np.asarray(obliquity_rad, dtype=float)
    varpi = np.asarray(varpi_rad, dtype=float)
    declination = np.arcsin(np.sin(obliquity) * np.sin(solar_longitude))
    sunset_angle = np.arccos(np.clip(-np.tan(latitude) * np.tan(declination), -1.0, 1.0))
    inverse_distance_squared = ((1.0 + eccentricity * np.cos(solar_longitude - varpi)) ** 2 / (1.0 - eccentricity**2) ** 2)
    geometry = sunset_angle * np.sin(latitude) * np.sin(declination) + np.cos(latitude) * np.cos(declination) * np.sin(sunset_angle)
    return solar_constant / np.pi * inverse_distance_squared * geometry


def ridge_fit(x, y, alpha=1e-3):
    x = np.asarray(x, float); y = np.asarray(y, float)
    means = x.mean(axis=0); scales = x.std(axis=0); scales[scales == 0] = 1.0
    z = (x - means) / scales
    design = np.column_stack([np.ones(len(z)), z])
    penalty = np.eye(design.shape[1]) * alpha; penalty[0, 0] = 0.0
    coef = np.linalg.solve(design.T @ design + penalty, design.T @ y)
    return {"coef": coef, "means": means, "scales": scales}


def ridge_predict(model, x):
    z = (np.asarray(x, float) - model["means"]) / model["scales"]
    return np.column_stack([np.ones(len(z)), z]) @ model["coef"]


def rmse(y, pred):
    return float(np.sqrt(np.mean((np.asarray(y) - np.asarray(pred)) ** 2)))


def corr(y, pred):
    return float(np.corrcoef(np.asarray(y), np.asarray(pred))[0, 1])


def rolling_features(values, windows=(10, 40, 100)):
    s = pd.Series(np.asarray(values, float))
    cols = [s.to_numpy()]
    for window in windows:
        cols.append(s.rolling(window, min_periods=1).mean().to_numpy())
    return np.column_stack(cols)


def lag_features(values, lags=(1, 10, 40, 100)):
    values = np.asarray(values, float)
    cols = []
    for lag in lags:
        col = np.empty_like(values)
        col[:lag] = values[0]
        col[lag:] = values[:-lag]
        cols.append(col)
    return np.column_stack(cols)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    climate_path = MEMORY / "data" / "processed" / "mpt_lr04_la2004.csv"
    nbody_path = ASTRO / "resultats" / "real_science_max" / "baseline_20myr_dt10" / "earth.csv.gz"
    climate = pd.read_csv(climate_path)
    nbody = pd.read_csv(nbody_path)

    age = climate["age_kyr_bp"].to_numpy(float)
    nbody_age = -nbody["time_years"].to_numpy(float) / 1000.0
    order = np.argsort(nbody_age)
    nbody_e = np.interp(age, nbody_age[order], nbody["eccentricity"].to_numpy(float)[order])

    ref_e = climate["eccentricity"].to_numpy(float)
    obliq_rad = np.deg2rad(climate["obliquity_deg"].to_numpy(float))
    varpi = climate["varpi_rad"].to_numpy(float)
    hybrid_insolation = daily_mean_insolation(65.0, np.pi / 2.0, nbody_e, obliq_rad, varpi)
    reference_insolation = climate["insolation_65n_june_wm2"].to_numpy(float)
    target = climate["d18o_permil"].to_numpy(float)

    # Chronologie : apprentissage sur 2,6-0,8 Ma, test sur les 0,8 Ma les plus récents.
    train = age >= 800.0
    test = age < 800.0

    astro_ref = rolling_features(reference_insolation)
    astro_hybrid = rolling_features(hybrid_insolation)
    state = lag_features(target)
    models = {
        "climatologie": np.ones((len(target), 1)),
        "astro_la2004": astro_ref,
        "astro_nbody_hybride": astro_hybrid,
        "etat_seul": state,
        "etat_plus_la2004": np.column_stack([state, astro_ref]),
        "etat_plus_nbody_hybride": np.column_stack([state, astro_hybrid]),
    }

    rows = []
    predictions = pd.DataFrame({"age_kyr_bp": age, "d18o_observe": target})
    for name, features in models.items():
        model = ridge_fit(features[train], target[train], alpha=1e-2)
        pred = ridge_predict(model, features)
        predictions[name] = pred
        rows.append({
            "model": name,
            "feature_count": int(features.shape[1]),
            "train_rmse": rmse(target[train], pred[train]),
            "test_rmse": rmse(target[test], pred[test]),
            "test_correlation": corr(target[test], pred[test]),
        })

    metrics = pd.DataFrame(rows).sort_values("test_rmse")
    metrics.to_csv(OUT / "benchmark_hors_echantillon.csv", index=False)
    predictions.to_csv(OUT / "predictions_hors_echantillon.csv", index=False)

    # Trois origines temporelles supplémentaires. Chaque modèle est ajusté
    # uniquement sur des âges plus anciens que son bloc de test. Les variables
    # d'état utilisent les observations antérieures disponibles : il s'agit
    # d'une prévision à un pas avec état observé, pas d'une trajectoire libre.
    rolling_rows = []
    rolling_splits = [
        (1200.0, 800.0, 1200.0),
        (800.0, 400.0, 800.0),
        (400.0, 0.0, 400.0),
    ]
    for train_age_min, test_age_min, test_age_max in rolling_splits:
        fold_train = age >= train_age_min
        fold_test = (age >= test_age_min) & (age < test_age_max)
        fold_metrics = {}
        for name, features in models.items():
            model = ridge_fit(features[fold_train], target[fold_train], alpha=1e-2)
            pred = ridge_predict(model, features)
            value = rmse(target[fold_test], pred[fold_test])
            fold_metrics[name] = value
            rolling_rows.append({
                "train_age_min_kyr": train_age_min,
                "test_age_min_kyr": test_age_min,
                "test_age_max_kyr": test_age_max,
                "model": name,
                "test_rows": int(fold_test.sum()),
                "test_rmse": value,
            })
        rolling_rows.append({
            "train_age_min_kyr": train_age_min,
            "test_age_min_kyr": test_age_min,
            "test_age_max_kyr": test_age_max,
            "model": "gain_nbody_vs_etat_percent",
            "test_rows": int(fold_test.sum()),
            "test_rmse": 100.0 * (fold_metrics["etat_seul"] - fold_metrics["etat_plus_nbody_hybride"]) / fold_metrics["etat_seul"],
        })
        rolling_rows.append({
            "train_age_min_kyr": train_age_min,
            "test_age_min_kyr": test_age_min,
            "test_age_max_kyr": test_age_max,
            "model": "gain_la2004_vs_etat_percent",
            "test_rows": int(fold_test.sum()),
            "test_rmse": 100.0 * (fold_metrics["etat_seul"] - fold_metrics["etat_plus_la2004"]) / fold_metrics["etat_seul"],
        })
    rolling = pd.DataFrame(rolling_rows)
    rolling.to_csv(OUT / "validation_temporelle_roulante.csv", index=False)
    nbody_fold_gains = rolling.loc[rolling.model == "gain_nbody_vs_etat_percent", "test_rmse"].to_numpy(float)
    la2004_fold_gains = rolling.loc[rolling.model == "gain_la2004_vs_etat_percent", "test_rmse"].to_numpy(float)

    orbital = {
        "rows": int(len(age)),
        "age_max_kyr": float(age.max()),
        "eccentricity_rmse_nbody_vs_la2004": rmse(ref_e, nbody_e),
        "eccentricity_correlation_nbody_vs_la2004": corr(ref_e, nbody_e),
        "insolation_rmse_hybrid_vs_la2004_wm2": rmse(reference_insolation, hybrid_insolation),
        "insolation_correlation_hybrid_vs_la2004": corr(reference_insolation, hybrid_insolation),
        "split": {"train_age_kyr": [800.0, 2600.0], "test_age_kyr": [0.0, 799.0]},
    }
    best = metrics.iloc[0].to_dict()
    baseline = metrics.loc[metrics.model == "etat_seul"].iloc[0]
    hybrid_state = metrics.loc[metrics.model == "etat_plus_nbody_hybride"].iloc[0]
    ref_state = metrics.loc[metrics.model == "etat_plus_la2004"].iloc[0]
    verdict = {
        "orbital_transfer": orbital,
        "best_model": best,
        "nbody_hybrid_improvement_vs_state_only_percent": float(100 * (baseline.test_rmse - hybrid_state.test_rmse) / baseline.test_rmse),
        "la2004_improvement_vs_state_only_percent": float(100 * (baseline.test_rmse - ref_state.test_rmse) / baseline.test_rmse),
        "nbody_hybrid_gap_vs_la2004_percent": float(100 * (hybrid_state.test_rmse - ref_state.test_rmse) / ref_state.test_rmse),
        "rolling_origin_validation": {
            "folds": int(len(nbody_fold_gains)),
            "nbody_gain_vs_state_percent": [float(value) for value in nbody_fold_gains],
            "la2004_gain_vs_state_percent": [float(value) for value in la2004_fold_gains],
            "nbody_positive_folds": int((nbody_fold_gains > 0).sum()),
            "mean_nbody_gain_percent": float(nbody_fold_gains.mean()),
        },
        "forecast_type": "one-step prediction with observed lagged climate state",
        "independence_limit": "LR04 chronology is orbitally tuned and is not an independent validation of astronomical forcing",
        "status": "benchmark intermédiaire hors échantillon, non GCM",
    }
    (OUT / "verdict_transfert.json").write_text(json.dumps(verdict, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Transfert orbital vers une réponse climatique intermédiaire",
        "",
        "## Ce qui est réellement testé",
        "",
        "L'excentricité issue de l'intégration N-corps ORI-C remplace l'excentricité La2004 dans le calcul de l'insolation du 21 juin à 65° N. L'obliquité et la longitude du périhélie restent celles de La2004. Les modèles sont ajustés sur 2,6 à 0,8 Ma et évalués sans réajustement sur les 0,8 Ma les plus récentes.",
        "",
        f"Corrélation de l'excentricité N-corps avec La2004 sur 0-2,6 Ma : **{orbital['eccentricity_correlation_nbody_vs_la2004']:.4f}**. Corrélation des insolations : **{orbital['insolation_correlation_hybrid_vs_la2004']:.4f}**.",
        "",
        "## Benchmark hors échantillon",
        "",
        "| Modèle | Variables | RMSE apprentissage | RMSE test | Corrélation test |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in metrics.to_dict("records"):
        lines.append(f"| {row['model']} | {row['feature_count']} | {row['train_rmse']:.4f} | {row['test_rmse']:.4f} | {row['test_correlation']:.4f} |")
    lines += [
        "",
        "## Verdict",
        "",
        f"L'ajout du forçage hybride N-corps au modèle d'état **réduit la RMSE test de {verdict['nbody_hybrid_improvement_vs_state_only_percent']:.2f} %** par rapport au modèle d'état seul. Le forçage La2004 la réduit de **{verdict['la2004_improvement_vs_state_only_percent']:.2f} %**. Les deux modèles appariés diffèrent de seulement **{abs(verdict['nbody_hybrid_gap_vs_la2004_percent']):.3f} %** en RMSE.",
        "",
        f"La validation à origines temporelles roulantes donne un gain positif dans **{verdict['rolling_origin_validation']['nbody_positive_folds']} blocs sur {verdict['rolling_origin_validation']['folds']}**, avec une amélioration moyenne de **{verdict['rolling_origin_validation']['mean_nbody_gain_percent']:.2f} %** face à l'état seul.",
        "",
        "Ce benchmark reste une prévision à un pas utilisant l'état climatique observé aux temps précédents, pas une simulation climatique libre. La chronologie LR04 est accordée orbitalement et ne constitue donc pas une validation indépendante du forçage astronomique.",
        "",
        "Le résultat mesure un transfert statistique intermédiaire. Il ne comprend pas une Terre-Lune résolue, une dynamique propre de rotation-obliquité, les marées, les rétroactions spatiales ou un GCM. Il ne constitue donc pas la chaîne causale complète demandée, mais fournit un banc hors échantillon apparié pour juger chaque extension future.",
    ]
    (OUT / "RAPPORT_TRANSFERT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(verdict, ensure_ascii=False))


if __name__ == "__main__":
    main()
