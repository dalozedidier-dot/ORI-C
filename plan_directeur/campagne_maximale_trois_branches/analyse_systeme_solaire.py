"""Post-analyses maximales de la branche Système solaire avec les sorties existantes.

Le script n'exécute pas de nouveau calcul N-corps long. Il teste la robustesse,
la symétrie des interventions, la séparation des échelles temporelles et la
cohérence entre les verdicts astronomiques et paléoclimatiques déjà produits.
"""
from __future__ import annotations

import math
from collections import defaultdict

from common import ROOT, RESULTS, read_csv, read_json, write_json

ASTRO = (
    ROOT
    / "02_branche_systeme_solaire"
    / "couche_astronomique"
    / "resultats"
    / "real_science_max"
    / "analysis"
)
MEMORY = ROOT / "02_branche_systeme_solaire" / "couche_memoire_historique"
OUTPUT = RESULTS / "systeme_solaire_robustesse.json"


def as_float(value: str | float | int | None) -> float | None:
    if value in (None, "", "nan", "NaN"):
        return None
    result = float(value)
    return result if math.isfinite(result) else None


def acceptance_summary() -> dict:
    rows = read_csv(ASTRO / "acceptance_tests.csv")
    passed = [row for row in rows if row["passed"].strip().lower() == "true"]
    failed = [row for row in rows if row["passed"].strip().lower() != "true"]
    return {
        "criteria": len(rows),
        "passed": len(passed),
        "failed": len(failed),
        "failed_tests": [
            {
                "test": row["test"],
                "observed": as_float(row["observed"]),
                "operator": row["operator"],
                "threshold": as_float(row["threshold"]),
                "meaning": row["meaning"],
            }
            for row in failed
        ],
    }


def intervention_pairs() -> dict:
    rows = read_csv(ASTRO / "counterfactual_effects.csv")
    by_job = {row["job"]: row for row in rows}
    pair_specs = {
        "jupiter_semimajor_axis": (
            "jupiter_a_minus_0p5pct_2myr",
            "jupiter_a_plus_0p5pct_2myr",
        ),
        "jupiter_mass": (
            "jupiter_mass_minus_5pct_2myr",
            "jupiter_mass_plus_5pct_2myr",
        ),
        "saturn_mass": (
            "saturn_mass_minus_5pct_2myr",
            "saturn_mass_plus_5pct_2myr",
        ),
    }
    result = {}
    for name, (minus_name, plus_name) in pair_specs.items():
        minus, plus = by_job[minus_name], by_job[plus_name]
        minus_rmse = float(minus["rmse"])
        plus_rmse = float(plus["rmse"])
        minus_delta = float(minus["mean_eccentricity_delta"])
        plus_delta = float(plus["mean_eccentricity_delta"])
        rmse_asymmetry = abs(plus_rmse - minus_rmse) / ((plus_rmse + minus_rmse) / 2)
        delta_magnitude_asymmetry = abs(abs(plus_delta) - abs(minus_delta)) / max(
            (abs(plus_delta) + abs(minus_delta)) / 2, 1e-30
        )
        result[name] = {
            "minus_job": minus_name,
            "plus_job": plus_name,
            "minus_rmse": minus_rmse,
            "plus_rmse": plus_rmse,
            "rmse_relative_asymmetry": rmse_asymmetry,
            "minus_mean_eccentricity_delta": minus_delta,
            "plus_mean_eccentricity_delta": plus_delta,
            "mean_delta_changes_sign": minus_delta * plus_delta < 0,
            "mean_delta_magnitude_asymmetry": delta_magnitude_asymmetry,
            "minimum_effect_to_ensemble_floor": min(
                float(minus["effect_to_ensemble_floor_ratio"]),
                float(plus["effect_to_ensemble_floor_ratio"]),
            ),
            "interpretation": (
                "Exploratoire : une réponse antisymétrique serait compatible avec un régime local quasi linéaire. "
                "L'absence d'antisymétrie signale seulement qu'une approximation linéaire simple est insuffisante "
                "sur l'intervalle testé."
            ),
        }
    return result


def band_selectivity() -> dict:
    rows = read_csv(ASTRO / "counterfactual_band_metrics.csv")
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    unresolved = set()
    for row in rows:
        ratio = as_float(row["power_ratio_vs_baseline"])
        if ratio is None:
            unresolved.add(row["band"])
        else:
            grouped[row["band"]].append(row)
    result = {}
    for band, values in sorted(grouped.items()):
        ordered = sorted(values, key=lambda row: float(row["power_ratio_vs_baseline"]))
        result[band] = {
            "evaluated_interventions": len(values),
            "strongest_suppression": {
                "job": ordered[0]["job"],
                "power_ratio_vs_baseline": float(ordered[0]["power_ratio_vs_baseline"]),
            },
            "strongest_amplification": {
                "job": ordered[-1]["job"],
                "power_ratio_vs_baseline": float(ordered[-1]["power_ratio_vs_baseline"]),
            },
            "range": [
                float(ordered[0]["power_ratio_vs_baseline"]),
                float(ordered[-1]["power_ratio_vs_baseline"]),
            ],
        }
    return {
        "resolved_bands_in_2myr_interventions": result,
        "unresolved_bands_in_2myr_interventions": sorted(unresolved),
        "warning": (
            "Les interventions de 2 Ma ne permettent pas de quantifier proprement les bandes de 405 ka "
            "et 2,4 Ma dans ces sorties. Les valeurs absentes ne sont pas des effets nuls."
        ),
    }


def numerical_separation() -> dict:
    numerical = read_csv(ASTRO / "numerical_comparisons.csv")
    selected_names = {
        "whfast_dt10_vs_dt5",
        "whfast_dt5_vs_dt4p8828125",
        "whfast_vs_ias15",
    }
    selected = [row for row in numerical if row["comparison_type"] in selected_names]
    max_numerical_rmse = max(float(row["rmse"]) for row in selected)
    interventions = read_csv(ASTRO / "counterfactual_effects.csv")
    ratios = [
        {
            "job": row["job"],
            "intervention_rmse": float(row["rmse"]),
            "ratio_to_largest_selected_numerical_rmse": float(row["rmse"]) / max_numerical_rmse,
        }
        for row in interventions
    ]
    return {
        "selected_numerical_comparisons": [row["comparison_type"] for row in selected],
        "largest_selected_numerical_rmse": max_numerical_rmse,
        "intervention_to_numerical_ratios": ratios,
        "minimum_ratio": min(row["ratio_to_largest_selected_numerical_rmse"] for row in ratios),
        "scope": (
            "Ce rapport sépare les effets des interventions des écarts de pas et d'intégrateur retenus. "
            "Il ne couvre pas toutes les erreurs physiques du modèle réduit."
        ),
    }


def phase_horizon() -> dict:
    rows = sorted(
        read_csv(ASTRO / "reference_metrics_by_horizon.csv"),
        key=lambda row: float(row["horizon_years"]),
    )
    thresholds = {}
    for threshold in (0.99, 0.95, 0.90, 0.50):
        first = next(
            (row for row in rows if float(row["correlation"]) < threshold),
            None,
        )
        thresholds[str(threshold)] = None if first is None else float(first["horizon_years"])
    return {
        "metrics": [
            {
                "horizon_years": float(row["horizon_years"]),
                "correlation": float(row["correlation"]),
                "rmse": float(row["rmse"]),
            }
            for row in rows
        ],
        "first_sampled_horizon_below_correlation": thresholds,
        "interpretation": (
            "La baisse de corrélation point par point mesure une perte de phase dans une dynamique chaotique. "
            "Elle ne signifie pas que les bandes spectrales disparaissent."
        ),
    }


def paleoclimate_localization() -> dict:
    discriminants = read_json(
        MEMORY / "results_stress/tests_reels/i_criteres_discriminants.json"
    )
    nulls = read_json(
        MEMORY / "results_stress/tests_reels/n_nulls_spectraux_lr04.json"
    )
    exoplanet = read_json(MEMORY / "results_stress/exoplanet/b_report.json")
    bands = discriminants["C6_5_bandes_spectrales"]
    observed_100 = bands["LR04"]["part_100_ka"]
    model_100 = {
        model: bands[model]["part_100_ka"] for model in ("M0", "M1", "M2", "M1P")
    }
    residual_fraction = {
        model: max(0.0, 1.0 - value / observed_100) if observed_100 else None
        for model, value in model_100.items()
    }
    significant_windows_100 = []
    for window in nulls["window_stability"]:
        p = window["bands"]["100_ka"]["p_bonferroni_2_bands"]
        significant_windows_100.append({
            "age_ka": window["age_ka"],
            "p_corrected": p,
            "significant_at_0.05": p < 0.05,
        })
    relaxation = exoplanet["relaxation"]
    return {
        "prediction_window_100ka_observed_power_share": observed_100,
        "prediction_window_100ka_model_power_share": model_100,
        "approximate_unexplained_fraction_of_observed_100ka_share": residual_fraction,
        "100ka_null_test_by_window": significant_windows_100,
        "41ka_resolved": bands["LR04"]["resolue_41_ka"],
        "100ka_resolved": bands["LR04"]["resolue_100_ka"],
        "405ka_resolved": bands["LR04"]["resolue_405_ka"],
        "exoplanet_long_hold": {
            variable: {
                "longest_hold_myr": values["longest_hold_myr"],
                "retained_fraction": values["retained_fraction"],
                "ever_material": values["ever_material"],
            }
            for variable, values in relaxation.items()
        },
        "conclusion": (
            "La bande de 100 ka est forte dans la fenêtre récente mais instable dans les fenêtres plus anciennes. "
            "Les quatre modèles testés n'en reproduisent qu'une faible part sur la fenêtre de prédiction. "
            "Le test exoplanétaire converge vers un attracteur unique sur palier long."
        ),
    }


def run() -> dict:
    payload = {
        "status": "completed",
        "branch": "systeme_solaire_et_terre",
        "astronomical_acceptance": acceptance_summary(),
        "paired_intervention_symmetry": intervention_pairs(),
        "band_selectivity": band_selectivity(),
        "numerical_effect_separation": numerical_separation(),
        "phase_horizon": phase_horizon(),
        "paleoclimate_and_path_dependence": paleoclimate_localization(),
        "limitations": [
            "Aucun nouveau calcul N-corps long n'est produit par ce script.",
            "Les interventions spectrales disponibles durent 2 Ma et ne résolvent pas toutes les longues périodes.",
            "Le modèle réduit n'inclut pas une Lune résolue, la rotation terrestre, les marées ni un GCM.",
            "Les tests paléoclimatiques portent sur LR04 et ne démontrent pas un mécanisme causal unique.",
        ],
    }
    write_json(OUTPUT, payload)
    return payload


if __name__ == "__main__":
    result = run()
    summary = result["astronomical_acceptance"]
    print(f"Système solaire: {summary['passed']} critères réussis sur {summary['criteria']}.")
