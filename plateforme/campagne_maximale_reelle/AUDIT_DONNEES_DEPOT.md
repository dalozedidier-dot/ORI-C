# Audit maximal des données du dépôt

## Résultat des 683 entrées

- Réussites techniques : **9**
- Blocages : **626**
- Protocoles non exécutables informatiquement : **48**
- Échecs : **0**
- Erreurs : **0**

Verdicts scientifiques confirmatoires : **0 soutien**, **0 rejet**, **635 indéterminés**.

Le pare-feu est fail-closed : présence d'un fichier, taille d'un jeu ou exécution d'un moteur ne suffisent jamais à créer une preuve. Une réussite technique reste distincte d'un verdict scientifique.

## Données réellement raccordées

- `prebiotic_lineage_nodes` : 21439
- `prebiotic_parent_offspring_pairs` : 13680
- `prebiotic_timecourse_rows` : 59328
- `prebiotic_timecourse_series` : 576
- `prebiotic_figure3_measurements` : 448
- `prebiotic_log_auxiliary_measurements` : 19392
- `partition_experiments` : 41
- `cell_architecture_rows` : 13
- `antibiotic_design_rows` : 10
- `antibiotic_independent_fitness_rows` : 72
- `benchmark_cases` : 17506
- `biology_cases` : 14777
- `modern_climate_ensemble_rows` : 142745
- `reaction_network_rows` : 16434
- `molecular_inventory_rows` : 19
- `nucleosynthesis_element_yields` : 1383
- `nucleosynthesis_isotope_yields` : 56507
- `isotope_tracer_rows` : 362
- `endosymbiosis_events` : 85
- `endosymbiont_hmm_rows` : 15810
- `murchison_degassing_rows` : 3648
- `thermochemical_phase_rows` : 64512
- `late_accretion_tracer_rows` : 122159
- `volatile_inventory_rows` : 10
- `modern_climate_timeseries_rows` : 7193
- `benchmark_domains` : {"antibiotic": 288, "antibiotic_longitudinal": 739, "matter_transition": 40, "modern_climate": 1152, "orbital": 1020, "paleoclimate": 517, "rna_evolution": 70, "vesicle": 13680}

## Causes racines des blocages restants

- **89** entrées : pare-feu empirique:paleoclimate_timeseries:test_hors_portee_mesuree
- **85** entrées : pare-feu empirique:prebiotic_lineages:test_hors_portee_mesuree
- **63** entrées : pare-feu empirique:aucun_dataset:aucun_jeu_empirique_declare
- **48** entrées : pare-feu empirique:benchmark_cases:non_admissible_comme_preuve_empirique
- **37** entrées : pare-feu empirique:orbital_initial_conditions:non_admissible_comme_preuve_empirique
- **23** entrées : pare-feu empirique:matter_transitions:non_admissible_comme_preuve_empirique
- **23** entrées : pare-feu empirique:antibiotic_cycles:test_hors_portee_mesuree,antibiotic_measurements:test_hors_portee_mesuree
- **18** entrées : pare-feu empirique:modern_climate_timeseries:test_hors_portee_mesuree
- **18** entrées : pare-feu empirique:modern_climate_ensemble:non_admissible_comme_preuve_empirique
- **18** entrées : pare-feu empirique:antibiotic_measurements:test_hors_portee_mesuree
- **16** entrées : pare-feu empirique:relations:non_admissible_comme_preuve_empirique,states:non_admissible_comme_preuve_empirique
- **15** entrées : pare-feu empirique:molecular_inventory:non_admissible_comme_preuve_empirique,reaction_network:non_admissible_comme_preuve_empirique
- **15** entrées : pare-feu empirique:thermochemical_phases:non_admissible_comme_preuve_empirique
- **13** entrées : pare-feu empirique:partition_experiments:test_hors_portee_mesuree
- **11** entrées : pare-feu empirique:planetary_histories:non_admissible_comme_preuve_empirique
- **11** entrées : pare-feu empirique:prebiotic_rna_evolution:test_hors_portee_mesuree
- **11** entrées : pare-feu empirique:endosymbiosis_events:test_hors_portee_mesuree
- **11** entrées : pare-feu empirique:antibiotic_cycles:test_hors_portee_mesuree
- **10** entrées : pare-feu empirique:nucleosynthesis_yields:non_admissible_comme_preuve_empirique
- **10** entrées : pare-feu empirique:isotope_tracers:test_hors_portee_mesuree
- **10** entrées : pare-feu empirique:body_properties:non_admissible_comme_preuve_empirique,chronometers:test_hors_portee_mesuree
- **10** entrées : pare-feu empirique:ephemerides:non_admissible_comme_preuve_empirique,orbital_initial_conditions:non_admissible_comme_preuve_empirique
- **9** entrées : pare-feu empirique:volatile_inventory:non_admissible_comme_preuve_empirique
- **9** entrées : pare-feu empirique:late_accretion_tracers:test_hors_portee_mesuree
- **9** entrées : pare-feu empirique:orbital_timeseries:non_admissible_comme_preuve_empirique
- **9** entrées : pare-feu empirique:cell_architecture:non_admissible_comme_preuve_empirique
- **9** entrées : pare-feu empirique:biology_cases:non_admissible_comme_preuve_empirique
- **5** entrées : pare-feu empirique:prebiotic_design:test_hors_portee_mesuree
- **4** entrées : pare-feu empirique:orbital_reference:non_admissible_comme_preuve_empirique,orbital_timeseries:non_admissible_comme_preuve_empirique
- **4** entrées : pare-feu empirique:antibiotic_design:test_hors_portee_mesuree
- **2** entrées : pare-feu empirique:modern_climate_ensemble:non_admissible_comme_preuve_empirique,modern_climate_timeseries:test_hors_portee_mesuree
- **1** entrées : pare-feu empirique:exoplanet_observations:test_hors_portee_mesuree

## Ressources nouvelles et verrous scientifiques

### `thermochemical_phases.csv` — present_non_empirical

Grille calculée depuis des paramètres thermodynamiques publiés. Elle audite le domaine T-P-G mais ne constitue pas une séquence de condensation à l'équilibre.

Condition pour aller plus loin : Composition globale, bilans élémentaires, activités/fugacités et solveur d'équilibre préenregistré avant tout test M4.

### `planetary_histories.csv` — absent_by_design

Aucune source publique harmonisée ne fournit les sept couches historiques demandées avec provenance primaire par cellule.

Condition pour aller plus loin : Compilation primaire cellule par cellule ou redéfinition préenregistrée des protocoles P6.

### `late_accretion_tracers.csv` — present_partial_empirical

122 159 mesures GEOROC réelles couvrent Mo-Ru-W-Os-Ir-Au, mais candidate_source décrit une famille géologique et non un pôle de mélange; les incertitudes analytiques par mesure sont absentes.

Condition pour aller plus loin : Modèle de mélange documenté avec pôles physiquement définis, unités et incertitudes avant P5-002 à P5-010. P5-001 seul est exécutable techniquement.

### `volatile_inventory.csv` — present_incomplete

Les compartiments non publiés restent vides. Aucune des dix lignes ne contient simultanément masse initiale, noyau, manteau, atmosphère et pertes.

Condition pour aller plus loin : Inventaires fermés ou protocole explicitement conçu pour des bornes partielles; aucune valeur absente ne peut être remplacée par zéro.

### `modern_climate_timeseries.csv` — present_temperature_only

7 193 lignes réelles issues de GISTEMP/HadCRUT5, mais les quatre variables sont des reconstructions de température et ne représentent ni forçages ni compartiments de mémoire.

Condition pour aller plus loin : Variables causales indépendantes et protocole mémoire/D-H-L gelé avant déblocage CL1/CL2.

## Règle de portée

`EMPIRICAL_POLICY.json` est la politique gelée; `REAL_DATA_COVERAGE.json` en est l'état d'exécution. Une table ne débloque que les identifiants explicitement autorisés et admissibles comme preuve empirique.
