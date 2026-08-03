"""Assemble STRESS_REPORT.md à partir des artefacts de la campagne.

Le rapport est généré, pas rédigé à la main : chaque chiffre cité provient d'un
fichier produit par les campagnes A à E.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from core import OUTPUT_ROOT, PROJECT_ROOT

MPT = OUTPUT_ROOT / "mpt"
EXO = OUTPUT_ROOT / "exoplanet"
IND = OUTPUT_ROOT / "independence"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def fmt(value, digits=4):
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "oui" if value else "non"
    if isinstance(value, (int,)):
        return str(value)
    try:
        value = float(value)
    except (TypeError, ValueError):
        return str(value)
    if value != value:
        return "—"
    if value == 0.0:
        return "0"
    if abs(value) < 1e-3 or abs(value) >= 1e5:
        return f"{value:.3e}"
    return f"{value:.{digits}f}"


def verdict_section() -> str:
    data = load(MPT / "e_hardened_verdict.json")
    if not data:
        return ""
    lines = ["## 1. Les cinq critères MPT préenregistrés, recalculés\n"]
    lines.append(
        "Aucun seuil n'est modifié. Seules changent la qualité de "
        "l'optimisation, la correction d'autocorrélation du BIC et l'ajout d'un "
        "témoin à nombre de paramètres égal.\n"
    )
    for key, block in data.items():
        bounds, reference = key.split("_vs_")
        label = "bornes livrées" if bounds == "reference" else "bornes élargies"
        lines.append(
            f"\n### Témoin {reference}, {label} — "
            f"{block['passed']}/{block['total']} critères réussis\n"
        )
        lines.append("| Critère | Valeur | Seuil | Verdict |")
        lines.append("|---|---:|---:|---:|")
        for row in block["detail"]:
            verdict = "RÉUSSI" if row["passed"] else "NON RÉUSSI"
            lines.append(
                f"| {row['criterion']} | {fmt(row['value'])} | "
                f"{fmt(row['threshold'])} | {verdict} |"
            )
        lines.append(
            f"\nAutocorrélation de rang 1 des résidus de M2 : "
            f"{fmt(block['residual_lag1_autocorrelation_M2'])}. "
            f"Taille d'échantillon nominale {block['actual_sample_size']}, "
            f"efficace {fmt(block['effective_sample_size_M2'], 1)}."
        )
    return "\n".join(lines) + "\n"


def budget_section() -> str:
    ladder = MPT / "d_budget_ladder.csv"
    if not ladder.exists():
        return ""
    frame = pd.read_csv(ladder)
    lines = ["\n## 2. Le gain dépend-il du budget d'optimisation ?\n"]
    lines.append(
        "Mêmes données, mêmes graines, même fenêtre. Seul le budget de "
        "l'optimiseur varie.\n"
    )
    lines.append("| Bornes | Budget | itérations | RMSE prédiction M1 | "
                 "RMSE prédiction M2 | RMSE prédiction M1P | gain M2/M1 | "
                 "gain M2/M1P |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for _, row in frame.iterrows():
        lines.append(
            f"| {row['bounds']} | {row['budget']} | {int(row['max_iterations'])} | "
            f"{fmt(row['pred_rmse_M1'], 3)} | {fmt(row['pred_rmse_M2'], 3)} | "
            f"{fmt(row['pred_rmse_M1P'], 3)} | {fmt(row['gain_M2_vs_M1'])} | "
            f"{fmt(row['gain_M2_vs_M1P'])} |"
        )
    return "\n".join(lines) + "\n"


def robust_section() -> str:
    data = load(MPT / "a_report.json")
    if not data or "robust" not in data:
        return ""
    robust = data["robust"]
    lines = ["\n## 3. Statistiques robustes sur la fenêtre de prédiction\n"]
    lines.append(
        f"Autocorrélation de rang 1 des résidus de M1 : "
        f"{fmt(robust['residual_lag1_autocorrelation_M1'])}, soit un temps de "
        f"décorrélation de {fmt(robust['decorrelation_time_kyr'], 1)} ka. "
        f"La fenêtre contient {robust['n_actual']} points de grille mais "
        f"seulement {fmt(robust['n_effective_M1'], 1)} points indépendants.\n"
    )
    lines.append("| Témoin | gain ponctuel | IC 95 % bootstrap par blocs | "
                 "P(gain < 5 %) | P(gain < 0) | Wilcoxon par blocs |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for row in robust["comparisons"]:
        lines.append(
            f"| {row['reference']} | {fmt(row['rmse_gain_point'])} | "
            f"[{fmt(row['rmse_gain_ci_2.5'])} ; {fmt(row['rmse_gain_ci_97.5'])}] | "
            f"{fmt(row['bootstrap_probability_gain_below_5pct'])} | "
            f"{fmt(row['bootstrap_probability_gain_negative'])} | "
            f"{fmt(row['blockwise_wilcoxon_p'])} |"
        )
    return "\n".join(lines) + "\n"


def split_section() -> str:
    path = MPT / "a_split_sensitivity.csv"
    if not path.exists():
        return ""
    frame = pd.read_csv(path)
    lines = ["\n## 4. Sensibilité à la fenêtre de séparation\n"]
    lines.append("| Séparation (ka) | gain M2/M1 | gain M2/M1P | "
                 "corrélation M2 | rapport 100/41 de M2 | cible observée |")
    lines.append("|---:|---:|---:|---:|---:|---:|")
    for _, row in frame.iterrows():
        lines.append(
            f"| {int(row['split_age_kyr'])} | {fmt(row['gain_M2_vs_M1'])} | "
            f"{fmt(row['gain_M2_vs_M1P'])} | {fmt(row['correlation_M2'])} | "
            f"{fmt(row['power_ratio_M2'])} | {fmt(row['power_ratio_observed'])} |"
        )
    return "\n".join(lines) + "\n"


def surrogate_section() -> str:
    data = load(MPT / "a_report.json")
    if not data or "surrogate" not in data:
        return ""
    surrogate = data["surrogate"]
    lines = ["\n## 5. Distribution nulle du gain\n"]
    lines.append(
        f"{surrogate['draws_per_kind']} tirages par type de nul. Le budget "
        "d'optimisation est identique pour tous les modèles à l'intérieur d'un "
        "tirage.\n"
    )
    lines.append("| Nul | gain moyen M2/M1 | 95e centile | maximum | "
                 "fraction ≥ 5 % | fraction ≥ 5 % contre M1P |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for kind in ("cible", "forcage"):
        block = surrogate.get(kind)
        if not block:
            continue
        lines.append(
            f"| {kind} | {fmt(block['gain_M2_vs_M1_mean'])} | "
            f"{fmt(block['gain_M2_vs_M1_p95'])} | "
            f"{fmt(block['gain_M2_vs_M1_max'])} | "
            f"{fmt(block['fraction_above_5pct'])} | "
            f"{fmt(block['fraction_above_5pct_vs_M1P'])} |"
        )
    return "\n".join(lines) + "\n"


def ablation_section() -> str:
    data = load(MPT / "a_report.json")
    if not data or "ablation" not in data:
        return ""
    ablation = data["ablation"]
    lines = ["\n## 6. Ablation de la mémoire carbone de M2\n"]
    lines.append("| Quantité | Valeur |")
    lines.append("|---|---:|")
    for key, value in ablation.items():
        lines.append(f"| {key} | {fmt(value)} |")
    return "\n".join(lines) + "\n"


def independence_section() -> str:
    data = load(IND / "c_report.json")
    if not data:
        return ""
    lines = ["\n## 7. Indépendance, identifiabilité et capacité structurelle\n"]

    path = IND / "c_forcing_robustness.csv"
    if path.exists():
        frame = pd.read_csv(path)
        lines.append("### 7.1 Définition du forçage astronomique\n")
        lines.append("| Forçage | gain M2/M1 | gain M2/M1P | corrélation M2 | "
                     "rapport 100/41 de M2 |")
        lines.append("|---|---:|---:|---:|---:|")
        for _, row in frame.iterrows():
            lines.append(
                f"| {row['forcing']} | {fmt(row['gain_M2_vs_M1'])} | "
                f"{fmt(row['gain_M2_vs_M1P'])} | {fmt(row['correlation_M2'])} | "
                f"{fmt(row['power_ratio_M2'])} |"
            )
        lines.append("")

    capacity = data.get("capacity")
    if capacity:
        lines.append("\n### 7.2 Capacité spectrale et compromis\n")
        lines.append(
            f"Rapport 100/41 ka observé sur la fenêtre de prédiction : "
            f"{fmt(capacity['observed_power_ratio'])}. "
            f"Borne inférieure du facteur 2 : "
            f"{fmt(capacity['factor_2_lower_bound'])}.\n"
        )
        lines.append(
            "Ce test utilise délibérément la fenêtre de prédiction comme "
            "oracle. Une réussite ne vaut pas validation ; un échec vaut "
            "réfutation structurelle.\n"
        )
        lines.append("| Modèle | rapport atteignable sans contrainte | "
                     "RMSE à ce point | capable structurellement | "
                     "RMSE minimale (× M1) pour atteindre la bande |")
        lines.append("|---|---:|---:|---:|---:|")
        for model, block in capacity.get("tradeoff", {}).items():
            lines.append(
                f"| {model} | {fmt(block['free_best_power_ratio'])} | "
                f"{fmt(block['free_prediction_rmse'], 3)} | "
                f"{fmt(block['structurally_capable'])} | "
                f"{fmt(block['min_rmse_ratio_reaching_band'], 2)} |"
            )
        lines.append("")

    reverse = data.get("reverse")
    if reverse:
        lines.append("\n### 7.3 Inversion du sens de prédiction\n")
        lines.append(
            "Ajustement sur 1,2–0 Ma, prédiction sur 2,6–1,2 Ma.\n"
        )
        lines.append("| Modèle | RMSE prédiction | corrélation |")
        lines.append("|---|---:|---:|")
        for model in ("M0", "M1", "M2", "M1P"):
            block = reverse.get(model)
            if block:
                lines.append(
                    f"| {model} | {fmt(block['prediction_rmse'], 3)} | "
                    f"{fmt(block['correlation'])} |"
                )
        lines.append(
            f"\nGain de M2 sur M1 : {fmt(reverse['gain_M2_vs_M1'])}. "
            f"Sur M1P : {fmt(reverse['gain_M2_vs_M1P'])}."
        )

    profile = data.get("profile")
    if profile:
        lines.append("\n\n### 7.4 Identifiabilité des paramètres de M2\n")
        lines.append(
            "Chaque paramètre est gelé sur une grille, les autres sont "
            "réoptimisés. « Plat » signifie que geler le paramètre n'importe "
            "où sur sa grille coûte moins de 1 % de RMSE d'apprentissage.\n"
        )
        lines.append("| Paramètre | excès relatif maximal | "
                     "fraction plate à 1 % | identifié |")
        lines.append("|---|---:|---:|---:|")
        for name, block in profile["parameters"].items():
            lines.append(
                f"| {name} | {fmt(block['max_relative_excess'])} | "
                f"{fmt(block['flat_fraction_within_1pct'])} | "
                f"{fmt(block['identified'])} |"
            )

    stability = data.get("stability")
    if stability:
        lines.append("\n\n### 7.5 Stabilité des paramètres ajustés\n")
        lines.append("| Paramètre | minimum | médiane | maximum | "
                     "ordres de grandeur | change de signe |")
        lines.append("|---|---:|---:|---:|---:|---:|")
        for name, block in stability.items():
            lines.append(
                f"| {name} | {fmt(block['min'])} | {fmt(block['median'])} | "
                f"{fmt(block['max'])} | "
                f"{fmt(block['orders_of_magnitude_spanned'], 2)} | "
                f"{fmt(block['sign_changes'])} |"
            )
    return "\n".join(lines) + "\n"


def exoplanet_section() -> str:
    data = load(EXO / "b_report.json")
    regime = load(EXO / "b_final_regime_report.json")
    if not data:
        return ""
    lines = ["\n## 8. Test exoplanétaire durci\n"]

    convergence = data.get("convergence")
    if convergence:
        lines.append("### 8.1 Convergence numérique\n")
        lines.append("| Variable | Δ à 0,02 Ma (pas livré) | Δ à 0,0025 Ma | "
                     "écart relatif | Δ du modèle classique | rapport M2/classique |")
        lines.append("|---|---:|---:|---:|---:|---:|")
        for variable, block in convergence.items():
            lines.append(
                f"| {variable} | {fmt(block['delta_M2_at_delivered_step'])} | "
                f"{fmt(block['delta_M2_at_finest_step'])} | "
                f"{fmt(block['relative_change_delivered_to_finest'])} | "
                f"{fmt(block['delta_classic_at_finest_step'])} | "
                f"{fmt(block['ratio_M2_to_classic_at_finest_step'])} |"
            )
        lines.append("")

    relaxation = data.get("relaxation")
    if relaxation:
        lines.append("\n### 8.2 Test de relaxation (décisif)\n")
        lines.append(
            "Le protocole livré maintient le forçage final commun pendant "
            "10 Ma. On le prolonge.\n"
        )
        lines.append("| Variable | Δ à 10 Ma | Δ au palier le plus long | "
                     "fraction conservée | temps d'e-folding (Ma) | "
                     "jamais matériel |")
        lines.append("|---|---:|---:|---:|---:|---:|")
        for variable, block in relaxation.items():
            lines.append(
                f"| {variable} | {fmt(block['delta_M2_at_10myr_hold'])} | "
                f"{fmt(block['delta_M2_at_longest_hold'])} | "
                f"{fmt(block['retained_fraction'])} | "
                f"{fmt(block['efolding_myr'], 2)} | "
                f"{fmt(not block['ever_material'])} |"
            )
        lines.append("")

    multistability = data.get("multistability")
    if multistability:
        lines.append("\n### 8.3 Sonde de multistabilité sous le forçage final livré\n")
        lines.append(
            f"{multistability['probe_count']} états initiaux très dispersés, "
            f"intégrés {fmt(multistability['duration_myr'], 0)} Ma sous le seul "
            "forçage final.\n"
        )
        lines.append("| Variable | dispersion initiale | dispersion finale | "
                     "seuil de matérialité |")
        lines.append("|---|---:|---:|---:|")
        for variable in ("temperature_k", "ice_fraction", "co2_ppm", "productivity"):
            block = multistability.get(variable)
            if block:
                lines.append(
                    f"| {variable} | {fmt(block['initial_spread'])} | "
                    f"{fmt(block['final_spread'])} | "
                    f"{fmt(block['materiality_threshold'])} |"
                )
        lines.append("")

    materiality = data.get("materiality")
    if materiality:
        lines.append(
            f"\n### 8.4 Carte de matérialité "
            f"({materiality['grid_points']} combinaisons de paramètres)\n"
        )
        lines.append("| Variable | seuil | Δ maximal au palier de 10 Ma | "
                     "Δ maximal au palier de 200 Ma | fraction matérielle à 10 Ma | "
                     "fraction matérielle à 200 Ma |")
        lines.append("|---|---:|---:|---:|---:|---:|")
        for variable in ("temperature_k", "ice_fraction", "co2_ppm", "productivity"):
            block = materiality.get(variable)
            if block:
                lines.append(
                    f"| {variable} | {fmt(block['threshold'])} | "
                    f"{fmt(block['max_delta_10myr_hold'])} | "
                    f"{fmt(block['max_delta_200myr_hold'])} | "
                    f"{fmt(block['fraction_material_at_10myr'])} | "
                    f"{fmt(block['fraction_material_at_200myr'])} |"
                )
        lines.append("")

    if regime:
        lines.append(
            f"\n### 8.5 Balayage du régime de forçage final "
            f"({regime['grid_points']} points)\n"
        )
        lines.append("| Variable | dispersion maximale des attracteurs | "
                     "points à attracteurs multiples | Δ matériel à 10 Ma | "
                     "Δ matériel à 200 Ma |")
        lines.append("|---|---:|---:|---:|---:|")
        for variable, block in regime["variables"].items():
            lines.append(
                f"| {variable} | {fmt(block['max_attractor_spread'])} | "
                f"{block['points_with_multiple_attractors']}/"
                f"{regime['grid_points']} | "
                f"{block['points_material_at_10myr']}/{regime['grid_points']} | "
                f"{block['points_material_at_200myr']}/{regime['grid_points']} |"
            )
    return "\n".join(lines) + "\n"


def main() -> None:
    verification = load(OUTPUT_ROOT / "00_core_verification.json")
    header = [
        "# Campagne de tests de stress — mémoire historique ORI-C",
        "",
        "Ce rapport est généré par `stress/make_report.py` à partir des "
        "artefacts des campagnes A à E. Il ne remplace pas `REPORT.md` : il "
        "soumet le résultat livré à des contrôles que le protocole initial "
        "n'exécutait pas.",
        "",
        "## 0. Contrôle du harnais",
        "",
    ]
    if verification:
        header.append(
            f"Le simulateur MPT compilé reproduit `simulate_mpt` à l'identique "
            f"({fmt(verification['mpt_bit_identical'])}) et l'EMIC compilé "
            f"reproduit `simulate_reduced_climate` à moins de 1e-12 en écart "
            f"relatif ({fmt(verification['exoplanet_within_1e-12'])}), pour un "
            f"gain de vitesse de {fmt(verification['speedup'], 0)}×. "
            f"Toute la campagne repose sur ce noyau."
        )
        header.append("")
    body = [
        verdict_section(),
        budget_section(),
        robust_section(),
        split_section(),
        surrogate_section(),
        ablation_section(),
        independence_section(),
        exoplanet_section(),
    ]
    path = PROJECT_ROOT / "STRESS_REPORT.md"
    path.write_text("\n".join(header) + "\n".join(body), encoding="utf-8")
    print(f"écrit : {path}")


if __name__ == "__main__":
    main()
