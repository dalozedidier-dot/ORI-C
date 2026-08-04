#!/usr/bin/env python3
"""Exécute la campagne maximale réalisable avec les données déjà présentes."""
from __future__ import annotations

import json
from analyse_matiere import run as run_matter
from analyse_systeme_solaire import run as run_solar
from analyse_vivant import run as run_living
from common import RESULTS, write_json


def fmt(value: float, digits: int = 4) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def build_summary(matter: dict, solar: dict, living: dict) -> dict:
    antibiotic = living["antibiotic_history_robustness"]
    cv = antibiotic["group_cross_validation"]["models"]
    return {
        "status": "completed",
        "campaign": "maximum_possible_with_repository_data",
        "branches": {
            "matiere": {
                "tests_executed": [
                    "suppression de chaque hyperarête",
                    "suppression de chaque nœud",
                    "ablation de chaque famille de processus",
                    "retrait un par un des coefficients de partage",
                    "audit de complétude des 40 transitions",
                ],
                "main_results": {
                    "strict_nodes_reachable": matter["hypergraph_robustness"]["baseline_reachable"],
                    "strict_nodes_total": matter["hypergraph_robustness"]["baseline_nodes"],
                    "strict_unreachable_nodes": matter["hypergraph_robustness"]["baseline_unreachable"],
                    "strict_cycle_kernel_nodes": matter["hypergraph_robustness"][
                        "strict_gap_diagnostics"
                    ]["cycle_kernel_nodes"],
                    "critical_hyperedges": matter["hypergraph_robustness"]["critical_edges"],
                    "hyperedges": matter["hypergraph_robustness"]["single_edge_deletions"],
                    "fragile_partition_overlap_elements": matter[
                        "partition_coefficient_robustness"
                    ]["fragile_overlap_elements"],
                    "empty_transition_fields": len(
                        matter["transition_database_completeness"]["empty_fields"]
                    ),
                },
                "evidence_level": "structural_and_descriptive",
            },
            "systeme_solaire_et_terre": {
                "tests_executed": [
                    "symétrie des interventions appariées",
                    "sélectivité des bandes 95 et 125 ka",
                    "séparation effet interventionnel et erreur numérique",
                    "perte de phase selon l'horizon",
                    "localisation de la bande paléoclimatique de 100 ka",
                    "persistance exoplanétaire sur palier long",
                ],
                "main_results": {
                    "astronomical_criteria_passed": solar["astronomical_acceptance"]["passed"],
                    "astronomical_criteria_total": solar["astronomical_acceptance"]["criteria"],
                    "minimum_intervention_to_numerical_ratio": solar[
                        "numerical_effect_separation"
                    ]["minimum_ratio"],
                    "unresolved_long_bands_in_2myr_interventions": solar[
                        "band_selectivity"
                    ]["unresolved_bands_in_2myr_interventions"],
                },
                "evidence_level": "validated_in_reduced_astronomical_model_and_negative_climate_tests",
            },
            "vivant": {
                "tests_executed": [
                    "validation croisée groupée par lignée",
                    "ablation de la pente historique",
                    "prédiction de la dernière transition",
                    "exclusion successive de chaque dose",
                    "permutation de l'ordre historique",
                    "dynamique de composition ARN sur huit cycles",
                    "validation du schéma prébiotique synthétique",
                ],
                "main_results": {
                    "antibiotic_prediction_rows": antibiotic["prediction_rows"],
                    "group_cv_mae_equal_complexity": cv["equal_complexity"]["mae"],
                    "group_cv_mae_history": cv["history"]["mae"],
                    "group_cv_mae_history_without_slope": cv["history_no_slope"]["mae"],
                    "paired_history_vs_equal_complexity_p": antibiotic[
                        "primary_paired_comparison"
                    ]["exact_two_sided_sign_flip_p"],
                    "slope_ablation_p": antibiotic["slope_ablation"][
                        "exact_two_sided_sign_flip_p"
                    ],
                    "ordered_history_null_p": antibiotic["ordered_history_null"][
                        "one_sided_fraction_null_at_least_observed"
                    ],
                    "rna_observations": living["catalytic_rna_frequency_dynamics"][
                        "observations"
                    ],
                    "prebiotic_real_lineage_data": False,
                },
                "evidence_level": "exploratory_only",
            },
        },
        "global_verdict": (
            "La campagne renforce la causalité architecturale dans le modèle astronomique, "
            "quantifie la fragilité de certaines représentations matérielles et ne trouve "
            "aucun appui biologique confirmatoire robuste. Elle ne valide pas ORI-C comme "
            "théorie générale."
        ),
        "next_data_bottlenecks": [
            "flux, temps de résidence et stocks opératoires pour C, H et S",
            "simulations climatiques interventionnelles et ensembles GCM indépendants",
            "jeu antibiotique final externe avec séquences d'exposition manipulées",
            "données réelles de lignées prébiotiques avec témoins appariés",
        ],
    }


def build_report(summary: dict, matter: dict, solar: dict, living: dict) -> str:
    matter_robust = matter["hypergraph_robustness"]
    partition = matter["partition_coefficient_robustness"]["per_element"]
    solar_pairs = solar["paired_intervention_symmetry"]
    solar_bands = solar["band_selectivity"]
    paleo = solar["paleoclimate_and_path_dependence"]
    antibiotic = living["antibiotic_history_robustness"]
    cv = antibiotic["group_cross_validation"]["models"]
    primary = antibiotic["primary_paired_comparison"]
    slope = antibiotic["slope_ablation"]
    final_holdout = antibiotic["final_transition_holdout"]["models"]
    rna = living["catalytic_rna_frequency_dynamics"]

    lines = [
        "# Campagne maximale sur les trois branches",
        "",
        "Cette campagne utilise uniquement les données, résultats et modèles déjà présents dans le dépôt. Elle ajoute des contrôles de robustesse et des ablations. Elle ne remplace pas les données absentes par des valeurs inventées et ne transforme jamais un succès technique en preuve scientifique.",
        "",
        "## Résultat global",
        "",
        summary["global_verdict"],
        "",
        "## 1. Matière",
        "",
        f"La projection paire à paire relie les 53 nœuds, mais la fermeture hypergraphique stricte, qui exige toutes les entrées de chaque processus, n'en atteint que **{matter_robust['baseline_reachable']} sur {matter_robust['baseline_nodes']}**. Le noyau cyclique est formé par `{', '.join(matter_robust['strict_gap_diagnostics']['cycle_kernel_nodes'])}`. Les nœuds `{', '.join(matter_robust['strict_gap_diagnostics']['downstream_nodes_blocked_by_cycle'])}` sont bloqués en aval. Déclarer disponible un seul des quatre nœuds du noyau suffit mathématiquement à fermer la représentation, sans démontrer qu'un tel apport existe dans la nature.",
        "",
        f"Sur cette fermeture stricte, la suppression individuelle des {matter_robust['single_edge_deletions']} hyperarêtes montre que **{matter_robust['critical_edges']} sont critiques pour la joignabilité des nœuds déjà atteignables**. Les premières arêtes de la chaîne peuvent rendre inaccessibles presque tout l'aval. Ce résultat mesure la fragilité de la représentation actuelle. Il ne prouve pas qu'un processus physique possède un chemin unique dans la nature.",
        "",
        f"Le contrôle des coefficients de partage donne trois situations distinctes. Le recouvrement du carbone résiste au retrait de chacune des trois valeurs. L'hydrogène reste non testable en retrait unitaire parce qu'une seule borne inférieure est disponible. Le recouvrement de l'azote devient faux lorsque la valeur `{partition['N']['leave_one_out'][1]['removed_record']}` est retirée. Il est donc **fragile à une mesure publiée**. Le désaccord du soufre reste présent quel que soit le coefficient retiré.",
        "",
        f"La base des 40 transitions reste remplie à {fmt(matter['transition_database_completeness']['global_fill_rate'] * 100, 1)} %. **{len(matter['transition_database_completeness']['empty_fields'])} champs sont entièrement vides**, notamment les preuves directes, les modèles concurrents, les seuils, les vitesses, les mécanismes de persistance et les contre-exemples. Les prochains progrès quantitatifs nécessitent donc des sources externes, pas un nouveau calcul sur les mêmes colonnes.",
        "",
        "## 2. Système solaire et Terre",
        "",
        f"Les interventions astronomiques restent séparées des erreurs numériques retenues par un facteur minimal de **{solar['numerical_effect_separation']['minimum_ratio']:.0f}**. La causalité architecturale est donc nette dans le modèle réduit.",
        "",
        f"La réponse n'est toutefois pas une simple relation linéaire. Pour le demi-grand axe de Jupiter, les perturbations opposées produisent toutes deux un déplacement moyen positif de l'excentricité terrestre. Pour la masse de Jupiter et celle de Saturne, le signe s'inverse, mais les amplitudes restent asymétriques. Cela indique qu'une dérivée locale unique ne résume pas tout le comportement sur les perturbations testées.",
        "",
        f"Sur les simulations d'intervention de 2 Ma, la puissance de la bande de 95 ka varie d'un facteur {solar_bands['resolved_bands_in_2myr_interventions']['95 kyr']['range'][0]:.3f} à {solar_bands['resolved_bands_in_2myr_interventions']['95 kyr']['range'][1]:.3f} par rapport au témoin. Pour 125 ka, elle varie de {solar_bands['resolved_bands_in_2myr_interventions']['125 kyr']['range'][0]:.3f} à {solar_bands['resolved_bands_in_2myr_interventions']['125 kyr']['range'][1]:.3f}. Les bandes de 405 ka et 2,4 Ma ne sont pas interprétables dans une fenêtre de 2 Ma et restent explicitement non résolues.",
        "",
        f"Dans LR04, la bande de 100 ka est très significative sur 0 à 1,2 Ma, mais elle ne dépasse pas le bruit rouge dans les deux fenêtres plus anciennes testées. Sur la fenêtre de prédiction, les quatre modèles ne reproduisent qu'une très faible part de sa puissance relative. L'estimation descriptive laisse environ **{min(paleo['approximate_unexplained_fraction_of_observed_100ka_share'].values()) * 100:.1f} à {max(paleo['approximate_unexplained_fraction_of_observed_100ka_share'].values()) * 100:.1f} %** de la part observée inexpliquée selon le modèle. Cette comparaison localise le verrou, sans identifier le mécanisme.",
        "",
        "Le test exoplanétaire confirme la différence entre retard et mémoire durable. Après un palier de 600 Ma, les fractions retenues sont nulles ou numériquement négligeables pour les quatre variables. Le modèle rejoint un attracteur unique.",
        "",
        "## 3. Vivant",
        "",
        f"Le benchmark antibiotique fournit {antibiotic['prediction_rows']} prédictions à partir de {antibiotic['longitudinal_lineages']} lignées longitudinales. En validation croisée groupée par lignée, la MAE vaut {cv['equal_complexity']['mae']:.4f} pour le témoin de même complexité et {cv['history']['mae']:.4f} pour le modèle historique. Le gain moyen par pli est de {primary['mean']:.4f}, avec {primary['fraction_favoring_right'] * 100:.0f} % des plis favorables et un test exact de changement de signe p = {primary['exact_two_sided_sign_flip_p']:.4f}.",
        "",
        f"L'ablation est plus révélatrice : retirer la pente historique améliore légèrement la MAE, de {cv['history']['mae']:.4f} à {cv['history_no_slope']['mae']:.4f}, avec un test apparié exact p = {slope['exact_two_sided_sign_flip_p']:.4f}. La distribution nulle à 1 000 permutations de la pente donne p = {antibiotic['ordered_history_null']['one_sided_fraction_null_at_least_observed']:.4f}. Dans le test temporel sur la dernière transition, le modèle historique atteint {final_holdout['history']['mae']:.4f}, contre {final_holdout['state_only']['mae']:.4f} pour l'état seul. L'avantage historique n'est donc ni stable entre les tests, ni attribuable clairement à l'ordre du passé.",
        "",
        f"Les {rna['observations']} observations ARN montrent plusieurs tendances de fréquences individuelles après correction pour comparaisons multiples. Dans la branche 71-89, la diversité du sous-ensemble suivi augmente avec les cycles (permutation exacte p = {rna['branch_dynamics']['71-89']['entropy_trend_exact_permutation']['exact_two_sided_p']:.4f}), tandis que la branche 52-2 ne montre pas de tendance globale significative. La concentration maximale n'évolue significativement dans aucune des deux branches. Ces données décrivent une dynamique de composition. Elles ne contiennent aucune filiation entre compartiments et ne testent pas l'hérédité prébiotique.",
        "",
        "## Ce qui peut encore être calculé",
        "",
        "Les données actuelles permettent encore des variantes de sensibilité et des contrôles secondaires. Elles ne permettent plus de franchir les principaux verrous par simple multiplication des calculs. Les données nouvelles prioritaires sont :",
        "",
        "1. flux et stocks opératoires pour étendre la chaîne matière au-delà de l'azote ;",
        "2. simulations climatiques interventionnelles indépendantes pour relier le spectre orbital à une réponse terrestre ;",
        "3. jeu antibiotique confirmatoire externe et laissé intact ;",
        "4. véritables tables de lignées prébiotiques avec témoins de complexité égale.",
        "",
        "## Verdict",
        "",
        "La campagne maximale disponible aujourd'hui **renforce un résultat astronomique localisé**, **révèle la fragilité de certaines conclusions structurelles de la branche matière** et **affaiblit l'interprétation d'un effet historique robuste dans le benchmark biologique actuel**. Elle améliore la précision du programme, sans fournir la prédiction positive transversale qui manque encore à ORI-C.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    matter = run_matter()
    solar = run_solar()
    living = run_living()
    summary = build_summary(matter, solar, living)
    write_json(RESULTS / "synthese_trois_branches.json", summary)
    report = build_report(summary, matter, solar, living)
    (RESULTS / "RAPPORT_CAMPAGNE_MAXIMALE.md").write_text(report, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
