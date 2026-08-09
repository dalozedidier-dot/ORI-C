#!/usr/bin/env python3
"""Construit la synthèse intégrée des campagnes présentes dans le dépôt."""
from __future__ import annotations

import json
import sys
from analyse_matiere import run as run_matter
from analyse_systeme_solaire import run as run_solar
from analyse_vivant import run as run_living
from common import RESULTS, ROOT, read_json, write_json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load_current_evidence() -> dict:
    """Charge les campagnes plus récentes que le runner historique.

    Le dossier conserve les anciens calculs antibiotique/ARN pour leur portée
    propre, mais la synthèse du dépôt doit aussi inclure D'Onofrio, les
    vésicules et la campagne de mémoire matérielle exécutés par la CI.
    """
    return {
        "donofrio": read_json(
            ROOT / "03_branche_vivant/benchmark_histoire_antibiotique_2026/"
            "resultats/RESULTAT.json"
        ),
        "vesicules": read_json(
            ROOT / "03_branche_vivant/lignees_vesicules/resultats/RESULTAT.json"
        ),
        "memoire_materielle": read_json(
            ROOT / "01_branche_matiere/memoire_materielle_reelle/derive/"
            "SYNTHESE_CAMPAGNE.json"
        ),
    }


def fmt(value: float, digits: int = 4) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def build_summary(matter: dict, solar: dict, living: dict, current: dict) -> dict:
    antibiotic = living["antibiotic_history_robustness"]
    cv = antibiotic["group_cross_validation"]["models"]
    donofrio = current["donofrio"]
    vesicules = current["vesicules"]
    memoire = current["memoire_materielle"]["transversalite"]
    return {
        "status": "completed",
        "campaign": "integrated_repository_evidence_synthesis",
        "scope_note": (
            "synthèse des campagnes versionnées ; le nom historique du dossier "
            "est conservé pour la stabilité des chemins, pas comme revendication "
            "d'exhaustivité absolue"
        ),
        "branches": {
            "matiere": {
                "tests_executed": [
                    "suppression de chaque hyperarête",
                    "suppression de chaque nœud",
                    "ablation de chaque famille de processus",
                    "retrait un par un des coefficients de partage",
                    "audit de complétude des 40 transitions",
                    "campagne de mémoire matérielle réelle et matrice d'admission",
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
                    "material_memory_partial_positive_families": len(
                        memoire["familles_soutenantes"]
                    ),
                    "material_memory_complete_chain_families": memoire[
                        "familles_au_schema_complet"
                    ],
                    "material_memory_transversality_verdict": memoire["verdict"],
                },
                "evidence_level": (
                    "structural_and_descriptive_plus_partial_real_material_evidence"
                ),
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
                    "benchmark D'Onofrio contre état seul et histoire mélangée",
                    "lignées de vésicules, filiation, sélection et ablation",
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
                    "legacy_prebiotic_real_lineage_data": False,
                    "donofrio_rows": donofrio["rows"],
                    "donofrio_groups": donofrio["group_count"],
                    "donofrio_rmse_state_only": donofrio["rmse_state_only"],
                    "donofrio_rmse_state_plus_history": donofrio[
                        "rmse_state_plus_history"
                    ],
                    "donofrio_permutation_p": donofrio[
                        "permutation_p_history_better_than_shuffled"
                    ],
                    "vesicle_parent_offspring_pairs": vesicules["pairs"],
                    "vesicle_permutation_p": vesicules["lineage_permutation_test"][
                        "permutation_p_one_sided"
                    ],
                    "vesicle_global_verdict": vesicules["global_verdict"],
                    "current_real_biological_results_included": True,
                },
                "evidence_level": (
                    "legacy_tests_mixed_plus_two_positive_real_data_protocols"
                ),
            },
        },
        "global_verdict": (
            "Le dépôt contient un résultat fort de causalité architecturale dans un "
            "modèle astronomique, plusieurs effets matériels réels partiels et deux "
            "résultats biologiques positifs sur données réelles (D'Onofrio et "
            "vésicules). La chaîne matérielle confirmatoire complète reste ouverte et "
            "C-MAT-MEM-05 ne soutient pas la transversalité. Cet ensemble ne valide "
            "pas ORI-C comme théorie générale."
        ),
        "next_data_bottlenecks": [
            "flux, temps de résidence et stocks opératoires pour C, H et S",
            "simulations climatiques interventionnelles et ensembles GCM indépendants",
            "réplication externe indépendante des résultats D'Onofrio",
            "réplication indépendante des lignées de vésicules",
            "trois familles matérielles admises portant histoire → trace → réponse et ablation",
        ],
    }


def build_report(summary: dict, matter: dict, solar: dict, living: dict,
                 current: dict) -> str:
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
    donofrio = current["donofrio"]
    vesicules = current["vesicules"]
    memoire = current["memoire_materielle"]["transversalite"]

    lines = [
        "# Synthèse intégrée des preuves du dépôt",
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
        f"La campagne de mémoire matérielle trouve **{len(memoire['familles_soutenantes'])} familles positives sur au moins une relation locale**, mais **{memoire['familles_au_schema_complet']} famille** admise porte la chaîne complète histoire → trace → réponse sous les contrôles gelés. `C-MAT-MEM-05` reste donc `{memoire['verdict']}`. Les effets de démagnétisation, plasticité cyclique, vieillissement thermique et recuit sont des résultats matériels réels ; ils ne doivent être ni effacés de la synthèse, ni promus en validation transversale complète.",
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
        f"Ces anciens jeux ne résument plus la branche. Sur les **{donofrio['rows']} mesures** D'Onofrio réparties en **{donofrio['group_count']} groupes**, la RMSE passe de **{donofrio['rmse_state_only']:.4f}** pour l'état seul à **{donofrio['rmse_state_plus_history']:.4f}** avec l'histoire ; le témoin d'histoire mélangée vaut {donofrio['same_complexity_shuffled_history_rmse_mean']:.4f} et la permutation donne p = {donofrio['permutation_p_history_better_than_shuffled']:.6f}. Le verdict est `{donofrio['verdict']}`.",
        "",
        f"Les expériences de vésicules fournissent **{vesicules['pairs']} relations parent-descendant**. Le signal observé vaut r = {vesicules['lineage_permutation_test']['observed_parent_offspring_r']:.4f}, contre {vesicules['lineage_permutation_test']['null_mean_r']:.4f} sous permutation, avec p = {vesicules['lineage_permutation_test']['permutation_p_one_sided']:.8f}. Les quatre composantes préenregistrées sont soutenues (`{vesicules['global_verdict']}`). Ce résultat reste unique et demande une réplication indépendante.",
        "",
        "## Ce qui peut encore être calculé",
        "",
        "Les données actuelles permettent encore des variantes de sensibilité et des contrôles secondaires. Elles ne permettent plus de franchir les principaux verrous par simple multiplication des calculs. Les données nouvelles prioritaires sont :",
        "",
        "1. flux et stocks opératoires pour étendre la chaîne matière au-delà de l'azote ;",
        "2. simulations climatiques interventionnelles indépendantes pour relier le spectre orbital à une réponse terrestre ;",
        "3. réplication externe indépendante du résultat D'Onofrio ;",
        "4. réplication indépendante des lignées de vésicules ;",
        "5. trois familles matérielles admises avec chaîne complète et ablation.",
        "",
        "## Verdict",
        "",
        "La synthèse actuelle conserve les résultats négatifs et les limites propres à chaque protocole, tout en intégrant les résultats positifs matériels et biologiques désormais présents. Plusieurs systèmes indépendants montrent une dépendance empirique à l'histoire, mais la chaîne opérationnelle commune et transversale n'est pas encore démontrée. ORI-C n'est donc pas validé comme théorie générale.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    matter = run_matter()
    solar = run_solar()
    living = run_living()
    current = load_current_evidence()
    summary = build_summary(matter, solar, living, current)
    write_json(RESULTS / "synthese_trois_branches.json", summary)
    report = build_report(summary, matter, solar, living, current)
    (RESULTS / "RAPPORT_CAMPAGNE_MAXIMALE.md").write_text(
        report, encoding="utf-8", newline="\n"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
