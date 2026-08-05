# Audit maximal des données du dépôt

## Résultat des 683 entrées

- Réussites techniques : **298**
- Blocages : **337**
- Protocoles non exécutables informatiquement : **48**
- Échecs : **0**
- Erreurs : **0**

Verdicts scientifiques confirmatoires : **0 soutien**, **0 rejet**, **635 indéterminés**.

Une réussite technique signifie seulement que l'analyse couverte a été exécutée. Elle ne transforme pas le résultat en preuve confirmatoire.

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
- `benchmark_domains` : {"antibiotic": 288, "antibiotic_longitudinal": 739, "matter_transition": 40, "modern_climate": 1152, "orbital": 1020, "paleoclimate": 517, "rna_evolution": 70, "vesicle": 13680}

## Causes racines des blocages restants

- **63** entrées : portée partielle:prebiotic_lineages
- **48** entrées : simulation/génération interdite:core_formal
- **16** entrées : simulation/génération interdite:astronomy_physics
- **16** entrées : portée partielle:benchmark_cases
- **15** entrées : simulation/génération interdite:intervention
- **15** entrées : fichier absent:thermochemical_phases.csv
- **12** entrées : portée partielle:molecular_inventory,reaction_network
- **12** entrées : simulation/génération interdite:astronomy_causality
- **11** entrées : fichier absent:planetary_histories.csv
- **11** entrées : portée partielle:endosymbiosis_events
- **10** entrées : simulation/génération interdite:planetesimal_thermal
- **10** entrées : portée partielle:partition_experiments
- **10** entrées : fichier absent:late_accretion_tracers.csv
- **10** entrées : GISTEMP ne contient ni forçage externe ni expérience multi-mémoires
- **9** entrées : portée partielle:nucleosynthesis_yields
- **9** entrées : portée partielle:isotope_tracers
- **9** entrées : fichier absent:volatile_inventory.csv
- **9** entrées : simulation/génération interdite:astronomy_repro
- **9** entrées : portée partielle:modern_climate_ensemble
- **8** entrées : GISTEMP n'observe pas une phase de retrait/restauration permettant d'estimer D-H-L
- **8** entrées : portée partielle:cell_architecture
- **6** entrées : portée partielle:biology_cases
- **4** entrées : simulation/génération interdite:astronomy_validation
- **4** entrées : portée partielle:antibiotic_design
- **3** entrées : portée partielle:prebiotic_design

## Données réellement absentes ou incompatibles

### `thermochemical_phases.csv` — 15 entrées concernées

Les fichiers reçus ne contiennent pas une grille homogène phase-température-pression-énergie de Gibbs permettant les calculs de condensation.

Source complémentaire nécessaire : Base thermodynamique quantitative Perple_X/JANAF ou équivalent avec licence et provenance.

### `planetary_histories.csv` — 11 entrées concernées

Les états orbitaux et les mesures noyau/bulk reçues ne constituent pas des histoires géochimiques complètes d'accrétion, redox, pertes et apports tardifs.

Source complémentaire nécessaire : Cas planétaires ou météoritiques harmonisés avec étapes historiques et composition finale.

### `late_accretion_tracers.csv` — 10 entrées concernées

Les isotopes reçus ne relient pas encore des observations finales à plusieurs sources candidates d'accrétion tardive dans un modèle de mélange commun.

Source complémentaire nécessaire : Compilation Mo-Ru-W-Os-Ir-Au et modèles de mélange documentés.

### `volatile_inventory.csv` — 9 entrées concernées

Le dégazage de Murchison et les modèles H-C noyau/bulk sont utiles mais ne ferment pas, par échantillon, les masses initiale, noyau, manteau, atmosphère et pertes.

Source complémentaire nécessaire : Inventaires volatils quantitatifs fermés de corps différenciés et météorites.

## Règle de portée

Les tables partielles ne débloquent que les identifiants explicitement couverts dans `REAL_DATA_COVERAGE.json`. Les autres restent bloqués même lorsque le fichier existe.
