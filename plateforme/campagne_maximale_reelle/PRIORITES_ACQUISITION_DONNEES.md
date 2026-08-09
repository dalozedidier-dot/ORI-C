# Priorités d'acquisition de données

Cette sortie transforme la matrice stricte en **carte des données manquantes**. Les 683 lignes sont des tests possibles, pas 683 expériences disponibles. Un nombre de tests potentiellement débloqués est une borne supérieure : il ne préjuge ni de l'exécution ni du verdict.

- 683 tests catalogués ;
- 626 bloqués ;
- 48 non exécutables automatiquement ;
- 9 exécutés techniquement ;
- 0 échec technique et 0 erreur informatique.

## Causes des blocages

| Cause | Occurrences | Tests distincts |
|---|---:|---:|
| `aucun_jeu_empirique_declare` | 63 | 63 |
| `non_admissible_comme_preuve_empirique` | 300 | 255 |
| `test_hors_portee_mesuree` | 343 | 320 |

Les occurrences ne s'additionnent pas aux 626 blocages : un même test peut cumuler plusieurs lacunes.

## Données à acquérir ou remplacer

| Rang | Dataset cible | Tests distincts potentiellement débloqués | Action |
|---:|---|---:|---|
| 1 | `paleoclimate_timeseries` | 89 | acquérir une source réelle mesurant exactement les variables, traces, interventions ou réponses exigées par le protocole |
| 2 | `prebiotic_lineages` | 85 | acquérir une source réelle mesurant exactement les variables, traces, interventions ou réponses exigées par le protocole |
| 3 | `aucun_dataset_declare` | 63 | identifier puis déclarer un jeu réel adapté au test |
| 4 | `benchmark_cases` | 48 | remplacer la simulation, reconstruction ou benchmark par une source empirique admissible ; télécharger davantage du même objet ne suffit pas |
| 5 | `orbital_initial_conditions` | 47 | remplacer la simulation, reconstruction ou benchmark par une source empirique admissible ; télécharger davantage du même objet ne suffit pas |
| 6 | `antibiotic_measurements` | 41 | acquérir une source réelle mesurant exactement les variables, traces, interventions ou réponses exigées par le protocole |
| 7 | `antibiotic_cycles` | 34 | acquérir une source réelle mesurant exactement les variables, traces, interventions ou réponses exigées par le protocole |
| 8 | `matter_transitions` | 23 | remplacer la simulation, reconstruction ou benchmark par une source empirique admissible ; télécharger davantage du même objet ne suffit pas |
| 9 | `modern_climate_ensemble` | 20 | remplacer la simulation, reconstruction ou benchmark par une source empirique admissible ; télécharger davantage du même objet ne suffit pas |
| 10 | `modern_climate_timeseries` | 20 | acquérir une source réelle mesurant exactement les variables, traces, interventions ou réponses exigées par le protocole |
| 11 | `relations` | 16 | remplacer la simulation, reconstruction ou benchmark par une source empirique admissible ; télécharger davantage du même objet ne suffit pas |
| 12 | `states` | 16 | remplacer la simulation, reconstruction ou benchmark par une source empirique admissible ; télécharger davantage du même objet ne suffit pas |
| 13 | `molecular_inventory` | 15 | remplacer la simulation, reconstruction ou benchmark par une source empirique admissible ; télécharger davantage du même objet ne suffit pas |
| 14 | `reaction_network` | 15 | remplacer la simulation, reconstruction ou benchmark par une source empirique admissible ; télécharger davantage du même objet ne suffit pas |
| 15 | `thermochemical_phases` | 15 | remplacer la simulation, reconstruction ou benchmark par une source empirique admissible ; télécharger davantage du même objet ne suffit pas |
| 16 | `orbital_timeseries` | 13 | remplacer la simulation, reconstruction ou benchmark par une source empirique admissible ; télécharger davantage du même objet ne suffit pas |
| 17 | `partition_experiments` | 13 | acquérir une source réelle mesurant exactement les variables, traces, interventions ou réponses exigées par le protocole |
| 18 | `endosymbiosis_events` | 11 | acquérir une source réelle mesurant exactement les variables, traces, interventions ou réponses exigées par le protocole |
| 19 | `planetary_histories` | 11 | remplacer la simulation, reconstruction ou benchmark par une source empirique admissible ; télécharger davantage du même objet ne suffit pas |
| 20 | `prebiotic_rna_evolution` | 11 | acquérir une source réelle mesurant exactement les variables, traces, interventions ou réponses exigées par le protocole |
| 21 | `body_properties` | 10 | remplacer la simulation, reconstruction ou benchmark par une source empirique admissible ; télécharger davantage du même objet ne suffit pas |
| 22 | `chronometers` | 10 | acquérir une source réelle mesurant exactement les variables, traces, interventions ou réponses exigées par le protocole |
| 23 | `ephemerides` | 10 | remplacer la simulation, reconstruction ou benchmark par une source empirique admissible ; télécharger davantage du même objet ne suffit pas |
| 24 | `isotope_tracers` | 10 | acquérir une source réelle mesurant exactement les variables, traces, interventions ou réponses exigées par le protocole |
| 25 | `nucleosynthesis_yields` | 10 | remplacer la simulation, reconstruction ou benchmark par une source empirique admissible ; télécharger davantage du même objet ne suffit pas |
| 26 | `biology_cases` | 9 | remplacer la simulation, reconstruction ou benchmark par une source empirique admissible ; télécharger davantage du même objet ne suffit pas |
| 27 | `cell_architecture` | 9 | remplacer la simulation, reconstruction ou benchmark par une source empirique admissible ; télécharger davantage du même objet ne suffit pas |
| 28 | `late_accretion_tracers` | 9 | acquérir une source réelle mesurant exactement les variables, traces, interventions ou réponses exigées par le protocole |
| 29 | `volatile_inventory` | 9 | remplacer la simulation, reconstruction ou benchmark par une source empirique admissible ; télécharger davantage du même objet ne suffit pas |
| 30 | `prebiotic_design` | 5 | acquérir une source réelle mesurant exactement les variables, traces, interventions ou réponses exigées par le protocole |
| 31 | `antibiotic_design` | 4 | acquérir une source réelle mesurant exactement les variables, traces, interventions ou réponses exigées par le protocole |
| 32 | `orbital_reference` | 4 | remplacer la simulation, reconstruction ou benchmark par une source empirique admissible ; télécharger davantage du même objet ne suffit pas |
| 33 | `exoplanet_observations` | 1 | acquérir une source réelle mesurant exactement les variables, traces, interventions ou réponses exigées par le protocole |
