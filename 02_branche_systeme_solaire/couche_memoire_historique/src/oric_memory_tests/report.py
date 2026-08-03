from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def _yes_no(value: bool) -> str:
    return "RÉUSSI" if value else "NON RÉUSSI"


def _format_number(value: float) -> str:
    value = float(value)
    if value != value:
        return "—"
    if abs(value) >= 100:
        return f"{value:.1f}"
    if abs(value) >= 1:
        return f"{value:.3f}"
    if abs(value) >= 0.001:
        return f"{value:.4f}"
    if value == 0.0:
        return "0"
    return f"{value:.3e}"


def write_report(project_root: Path) -> Path:
    mpt_dir = project_root / "results" / "mpt"
    exo_dir = project_root / "results" / "exoplanet"
    mpt_summary = json.loads((mpt_dir / "summary.json").read_text(encoding="utf-8"))
    exo_summary = json.loads((exo_dir / "summary.json").read_text(encoding="utf-8"))
    mpt_metrics = pd.read_csv(mpt_dir / "metrics.csv")
    mpt_acceptance = pd.read_csv(mpt_dir / "acceptance_tests.csv")
    exo_statistics = pd.read_csv(exo_dir / "statistical_tests.csv")

    prediction = mpt_metrics.loc[mpt_metrics["interval"] == "prediction"].copy()
    prediction = prediction.loc[
        prediction["model"].isin(["M0", "M1", "M2", "M1P"])
    ]
    comparisons = mpt_summary["comparisons"]

    lines = [
        "# Tests ORI-C de mémoire historique",
        "",
        "## Conclusion",
        "",
        (
            "L’implémentation est complète et reproductible. Le calcul sur LR04 "
            "ne valide pas la déclinaison paléoclimatique d’ORI-C. M2 réduit "
            "l’erreur de prédiction par rapport à M1, mais M1, avec ses six "
            "paramètres, n’est pas un témoin équitable. Face à M1P, qui possède "
            "le même nombre de paramètres que M2 mais dont l’état lent filtre le "
            "forçage externe au lieu d’inscrire la réponse passée, M2 perd. "
            "L’avantage mesuré contre M1 provient donc de degrés de liberté "
            "supplémentaires et non d’une mémoire historique."
        ),
        "",
        (
            "Le test exoplanétaire contrôlé réussit le test structurel de "
            "dépendance au chemin et son test d’ablation, mais échoue au test de "
            "persistance : l’écart entre les deux histoires s’efface lorsque le "
            "forçage final commun est maintenu au-delà des constantes de temps "
            "lentes du modèle. Ce qui est détecté est un retard de relaxation, "
            "non une inscription durable."
        ),
        "",
        "## Statut synthétique",
        "",
        "| Branche | Résultat | Portée |",
        "|---|---:|---|",
        (
            f"| MPT LR04, M2 contre M1 (moins complexe) | "
            f"{mpt_summary['passed_criteria_vs_M1']}/5 critères "
            "| Comparaison non appariée en complexité |"
        ),
        (
            f"| MPT LR04, M2 contre M1P (complexité égale) | "
            f"{mpt_summary['passed_criteria_vs_M1P']}/5 critères "
            "| Test décisif de la mémoire ORI-C |"
        ),
        (
            f"| Exoplanète, dépendance au chemin | "
            f"{_yes_no(exo_summary['structural_pass'])} "
            "| Validation structurelle du code et de l’ablation |"
        ),
        (
            f"| Exoplanète, persistance de l’écart | "
            f"{_yes_no(exo_summary['persistence_pass'])} "
            f"| Palier final prolongé à "
            f"{_format_number(exo_summary['persistence_hold_myr'])} Ma |"
        ),
        (
            f"| Exoplanète, amplitude physique | "
            f"{_yes_no(exo_summary['physical_relevance_pass'])} "
            "| Non calibrée sur un GCM ou une archive réelle |"
        ),
        "",
        "## Test MPT",
        "",
        (
            "Les quatre modèles sont ajustés uniquement entre 2,6 et 1,2 Ma. Les "
            "paramètres sont ensuite figés et propagés jusqu’au présent. M0 est "
            "une réponse fixe. M1 ajoute une mémoire classique du régolithe. M2 "
            "reprend M1 et ajoute une mémoire lente du carbone, pilotée par le "
            "volume de glace passé. M1P reprend M1 et ajoute un état lent de même "
            "structure, mais piloté par le forçage astronomique."
        ),
        "",
        (
            "M1P est le témoin décisif. Il possède exactement le même nombre de "
            "paramètres que M2 et la même constante de temps lente "
            "supplémentaire. Il ne diffère que sur un point : son état lent "
            "n’enregistre pas la réponse passée du système. Un avantage de M2 sur "
            "M1 mesure de la flexibilité ; seul un avantage de M2 sur M1P "
            "mesurerait l’inscription revendiquée par ORI-C."
        ),
        "",
        (
            "Trois symétries exactes sont retirées par définition : les échelles "
            "de R et de C, qui rendaient α/R* et β/γ non identifiables, et le "
            "décalage de l’état lent, exactement compensable par le décalage du "
            "forçage. Sans cette troisième correction, le test d’ablation carbone "
            "n’est pas défini : deux ajustements donnant la même prédiction "
            "donnent des ablations différentes."
        ),
        "",
        "| Modèle | Paramètres | RMSE prédiction | Corrélation | "
        "Rapport 100/41 ka | BIC (n efficace) | BIC (n brut) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in prediction.itertuples():
        lines.append(
            f"| {row.model} | {row.parameter_count} | "
            f"{_format_number(row.rmse_standardized)} | "
            f"{_format_number(row.correlation)} | "
            f"{_format_number(row.power_ratio_100k_to_41k)} | "
            f"{_format_number(row.bic)} | {_format_number(row.bic_naive)} |"
        )

    lines.extend([
        "",
        (
            f"LR04 présente un rapport de puissance 100/41 ka de "
            f"{_format_number(mpt_summary['observed_power_ratio_100k_to_41k'])} "
            f"sur la fenêtre de prédiction. M2 produit "
            f"{_format_number(mpt_summary['M2_power_ratio_100k_to_41k'])}, soit "
            "un écart de plus de deux ordres de grandeur. Ce constat est le plus "
            "robuste du test : il ne dépend ni du témoin choisi ni de la qualité "
            "de l’optimisation."
        ),
        "",
        "### Comparaison aux deux témoins",
        "",
        "| Témoin | gain de RMSE | IC 95 % (blocs mobiles) | P(gain < 5 %) | "
        "ΔBIC (n efficace) | ΔBIC (n brut) | Wilcoxon par blocs |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for reference, block in comparisons.items():
        lines.append(
            f"| {reference} | {_format_number(block['rmse_gain'])} | "
            f"[{_format_number(block['rmse_gain_ci_low'])} ; "
            f"{_format_number(block['rmse_gain_ci_high'])}] | "
            f"{_format_number(block['probability_gain_below_threshold'])} | "
            f"{_format_number(block['delta_bic_effective'])} | "
            f"{_format_number(block['delta_bic_naive'])} | "
            f"{_format_number(block['blockwise_wilcoxon_p'])} |"
        )

    lines.extend([
        "",
        (
            f"Les résidus de prédiction ont une autocorrélation de rang 1 de "
            f"{_format_number(mpt_summary['M2_residual_lag1_autocorrelation'])}. "
            f"La fenêtre contient "
            f"{mpt_summary['prediction_sample_size']} points de grille mais "
            f"{_format_number(mpt_summary['prediction_effective_sample_size'])} "
            "points indépendants. Le BIC calculé sur le compte brut surestime "
            "donc massivement le support des paramètres supplémentaires ; c’est "
            "la version corrigée qui est retenue pour le verdict."
        ),
        "",
        (
            "Contrôle d’optimisation : "
            + ", ".join(
                f"{model}={'convergé' if converged else 'non convergé'}"
                for model, converged in mpt_summary["optimizer_converged"].items()
            )
            + ". Dispersion relative de la RMSE d’apprentissage entre "
            "redémarrages : "
            + ", ".join(
                f"{model}={_format_number(spread)}"
                for model, spread in mpt_summary[
                    "optimizer_restart_spread"
                ].items()
            )
            + f". Noyau compilé : "
            f"{'oui' if mpt_summary['compiled_kernel'] else 'non'}."
        ),
        (
            "Paramètres aux bornes : "
            + "; ".join(
                f"{model}: {', '.join(hits) if hits else 'aucun'}"
                for model, hits in mpt_summary["parameter_boundary_hits"].items()
            )
            + "."
        ),
        "",
        "### Critères préenregistrés",
        "",
        (
            "Les cinq critères sont évalués contre chacun des deux témoins. Le "
            "verdict global exige la réussite de tous les critères contre les "
            "deux."
        ),
        "",
        "| Témoin | Critère | Valeur | Seuil | Verdict |",
        "|---|---|---:|---:|---:|",
    ])
    for row in mpt_acceptance.itertuples():
        lines.append(
            f"| {row.reference} | {row.criterion} | "
            f"{_format_number(row.value)} | "
            f"{_format_number(row.threshold)} | {_yes_no(bool(row.passed))} |"
        )

    helps = mpt_summary["carbon_coupling_helps_prediction"]
    lines.extend([
        "",
        "### Ablation de la mémoire carbone",
        "",
        (
            f"Retirer le couplage carbone des paramètres ajustés de M2 porte la "
            f"RMSE de prédiction à "
            f"{_format_number(mpt_summary['carbon_ablation_rmse'])}. "
            f"L’effet du couplage sur la RMSE vaut "
            f"{_format_number(mpt_summary['carbon_coupling_rmse_effect'])} "
            "(positif si le couplage aide)."
        ),
        "",
        (
            "Le couplage carbone améliore la prédiction hors échantillon."
            if helps
            else (
                "Le couplage carbone dégrade la prédiction hors échantillon : "
                "aux paramètres retenus par l’ajustement sur la calibration, la "
                "mémoire est activement nuisible une fois les paramètres figés. "
                "C’est un symptôme de surajustement, cohérent avec le fait que "
                "le couplage reste sur sa borne et que sa constante de temps "
                "n’est pas identifiée."
            )
        ),
        "",
        "### Limite d’indépendance",
        "",
        (
            "LR04 est une pile δ18O majeure, mais son modèle d’âge a été accordé "
            "à un modèle de glace fondé sur l’insolation du 21 juin à 65°N. "
            "Employer La2004 contre cette chronologie crée donc une dépendance "
            "méthodologique. Le test reste utile pour comparer des prévisions "
            "figées, mais une validation forte exigera des archives et des "
            "chronologies indépendantes."
        ),
        "",
        "## Test exoplanétaire contrôlé",
        "",
        (
            f"Deux histoires spin-orbitales différentes sont imposées pendant "
            f"50 Ma, puis exactement le même état final est maintenu pendant "
            f"{_format_number(exo_summary['final_hold_myr'])} Ma. Les ensembles "
            "sont appariés. Le modèle classique, M2 et M2 avec mémoires figées "
            "reçoivent les mêmes forçages et les mêmes conditions initiales."
        ),
        "",
        (
            f"Le protocole ajoute un palier de persistance à "
            f"{_format_number(exo_summary['persistence_hold_myr'])} Ma. Les "
            "constantes de temps lentes du modèle valent 8 Ma pour le carbone et "
            "60 Ma pour le régolithe : un palier de 10 Ma est plus court que la "
            "mémoire qu’il prétend mesurer, si bien que les deux histoires y "
            "sont encore en train de converger."
        ),
        "",
        "| Variable | Δ classique | Δ M2 sans mémoire | Δ M2 | Δ M2 palier long | "
        "fraction conservée | p corrigé | Matérialité | Persistance |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in exo_statistics.itertuples():
        lines.append(
            f"| {row.variable} | {_format_number(row.median_delta_classic)} | "
            f"{_format_number(row.median_delta_ablated)} | "
            f"{_format_number(row.median_delta_M2)} | "
            f"{_format_number(row.median_delta_M2_long_hold)} | "
            f"{_format_number(row.retained_fraction_after_long_hold)} | "
            f"{_format_number(row.holm_adjusted_p)} | "
            f"{_yes_no(bool(row.materiality_pass))} | "
            f"{_yes_no(bool(row.persistence_pass))} |"
        )

    lines.extend([
        "",
        (
            f"La dépendance au chemin est significative pour "
            f"{exo_summary['structural_variables_passed']} variables sur "
            f"{exo_summary['variables_tested']}, et son retrait ramène les "
            f"écarts au niveau nul pour "
            f"{exo_summary['ablation_variables_passed']} variables. "
            f"{exo_summary['material_variables_passed']} variables franchissent "
            "le seuil d’amplitude défini avant le calcul, et "
            f"{exo_summary['persistent_variables_passed']} conservent un écart "
            "matériel après le palier long."
        ),
        "",
        "## Ce que le paquet permet maintenant",
        "",
        "- relancer les calculs avec les mêmes données, graines et critères",
        "- comparer le modèle testé à un témoin de complexité égale",
        "- séparer un gain de mémoire d’un gain de flexibilité",
        "- distinguer une inscription durable d’un retard de relaxation",
        "- remplacer LR04 par des archives indépendantes sans modifier les modèles",
        "- remplacer les trajectoires prescrites par des sorties N-corps-spin",
        "- remplacer l’EMIC réduit par des sorties ROCKE-3D, WACCM6 ou GEOCLIM",
        "- conserver séparément validation structurelle et validation physique",
        "",
        "## Sources primaires",
        "",
        (
            "- Lisiecki, L. E. et Raymo, M. E. (2005), LR04, "
            "doi:10.1029/2004PA001071, jeu NOAA doi:10.25921/k88j-0106"
        ),
        (
            "- Laskar et al. (2004), La2004, "
            "doi:10.1051/0004-6361:20041335, données IMCCE"
        ),
        "",
        "## Fichiers de résultat",
        "",
        "- `results/mpt/` : prédictions, métriques, paramètres, blocs et figures",
        "- `results/exoplanet/` : forçages, ensembles, ablation, tests et figures",
        "- `data/processed/mpt_lr04_la2004.csv` : grille commune à 1 ka",
        "- `STRESS_REPORT.md` : campagne de stress complète et ses annexes",
        "- `MANIFEST.sha256` : empreintes de l’ensemble du paquet",
    ])
    output_path = project_root / "REPORT.md"
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path
