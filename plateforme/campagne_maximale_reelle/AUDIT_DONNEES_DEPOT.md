# Audit maximal des données du dépôt

## Résultat des 683 entrées

- Réussites techniques : **278**
- Blocages : **357**
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
- `partition_experiments` : 9
- `cell_architecture_rows` : 13
- `antibiotic_design_rows` : 10
- `antibiotic_independent_fitness_rows` : 72
- `benchmark_cases` : 17506
- `biology_cases` : 14777
- `benchmark_domains` : {"antibiotic": 288, "antibiotic_longitudinal": 739, "matter_transition": 40, "modern_climate": 1152, "orbital": 1020, "paleoclimate": 517, "rna_evolution": 70, "vesicle": 13680}

## Causes racines des blocages restants

- **63** entrées : portée partielle:prebiotic_lineages
- **48** entrées : simulation/génération interdite:core_formal
- **20** entrées : fichier absent:modern_climate_ensemble.csv
- **16** entrées : simulation/génération interdite:astronomy_physics
- **16** entrées : portée partielle:benchmark_cases
- **15** entrées : simulation/génération interdite:intervention
- **15** entrées : fichier absent:reaction_network.csv
- **15** entrées : fichier absent:thermochemical_phases.csv
- **13** entrées : portée partielle:partition_experiments
- **12** entrées : simulation/génération interdite:astronomy_causality
- **12** entrées : fichier absent:endosymbiosis_events.csv
- **11** entrées : fichier absent:planetary_histories.csv
- **10** entrées : fichier absent:nucleosynthesis_yields.csv
- **10** entrées : fichier absent:isotope_tracers.csv
- **10** entrées : simulation/génération interdite:planetesimal_thermal
- **10** entrées : fichier absent:late_accretion_tracers.csv
- **10** entrées : GISTEMP ne contient ni forçage externe ni expérience multi-mémoires
- **9** entrées : fichier absent:volatile_inventory.csv
- **9** entrées : simulation/génération interdite:astronomy_repro
- **8** entrées : GISTEMP n'observe pas une phase de retrait/restauration permettant d'estimer D-H-L
- **8** entrées : portée partielle:cell_architecture
- **6** entrées : portée partielle:biology_cases
- **4** entrées : simulation/génération interdite:astronomy_validation
- **4** entrées : portée partielle:antibiotic_design
- **3** entrées : portée partielle:prebiotic_design

## Données réellement absentes ou incompatibles

### `modern_climate_ensemble.csv` — 20 entrées concernées

Le dépôt contient GISTEMP observationnel, mais pas l'archive d'incertitude à 200 membres ni un ensemble multi-modèles/scénarios. L'ancien bilan annonçait 338 400 lignes sans que le fichier soit présent dans l'archive actuelle.

Source complémentaire nécessaire : NASA GISTEMP KeySeries.zip pour les deux audits observationnels; CMIP/expériences dédiées restent nécessaires pour les trajectoires et restaurations.

### `reaction_network.csv + molecular_inventory.csv` — 15 entrées concernées

L'inventaire hiérarchique contient des molécules qualitatives, mais aucun réseau versionné avec réactifs, produits, taux et plages de température, ni abondances observationnelles assorties d'incertitudes.

Source complémentaire nécessaire : KIDA/UMIST et un inventaire astronomique quantitatif.

### `thermochemical_phases.csv` — 15 entrées concernées

La table 08_Phases.csv est un inventaire qualitatif. Elle ne contient pas les triplets température-pression-énergie de Gibbs nécessaires aux calculs de condensation.

Source complémentaire nécessaire : Base thermodynamique quantitative Perple_X/JANAF ou équivalent avec licence et provenance.

### `endosymbiosis_events.csv` — 12 entrées concernées

Le dépôt mentionne mitochondrie et chloroplaste, mais ne fournit pas des événements documentés avec transfert génique, intégration métabolique, dépendance et niveau de preuve.

Source complémentaire nécessaire : Jeu phylogénomique et métabolique construit depuis des sources publiées.

### `planetary_histories.csv` — 11 entrées concernées

Les éléments orbitaux J2000 et DE441 sont des états dynamiques, pas des histoires géochimiques complètes d'accrétion, redox, pertes et apports tardifs.

Source complémentaire nécessaire : Cas planétaires/météoritiques harmonisés avec couches historiques et partition finale.

### `nucleosynthesis_yields.csv` — 10 entrées concernées

Les trajectoires MESA présentes décrivent des transitions stellaires, pas des rendements élémentaires par masse, métallicité et incertitude.

Source complémentaire nécessaire : Tables de rendements NuGrid ou équivalent.

### `isotope_tracers.csv` — 10 entrées concernées

Aucune table échantillon-traceur-valeur-incertitude permettant le clustering des groupes météoritiques n'est présente.

Source complémentaire nécessaire : Compilation isotopique Ti-Cr-Mo-W-Ni-Ru-Pd avec provenance ligne par ligne.

### `late_accretion_tracers.csv` — 10 entrées concernées

Aucune table d'observations finales associées à des sources candidates d'accrétion tardive n'est présente.

Source complémentaire nécessaire : Compilation Mo-Ru-W-Os-Ir-Au et modèles de mélange documentés.

### `volatile_inventory.csv` — 9 entrées concernées

Les inventaires généraux du dépôt ne donnent pas, par échantillon, les masses initiale, noyau, manteau, atmosphère et pertes nécessaires à la fermeture de masse.

Source complémentaire nécessaire : Inventaires volatils quantitatifs de corps différenciés et météorites.

## Règle de portée

Les tables partielles ne débloquent que les identifiants explicitement couverts dans `REAL_DATA_COVERAGE.json`. Les autres restent bloqués même lorsque le fichier existe.
