# Données utilisées au maximum dans la campagne réelle

La campagne utilise désormais automatiquement tout jeu réel déjà présent qui peut être raccordé sans inventer de colonne ou de mesure.

## Matière

- 40 transitions matérielles
- 9 coefficients de partage H, C, N et S
- inventaire biologique pour l'audit de l'architecture cellulaire
- trajectoires matérielles intégrées au benchmark transversal

## Système solaire et climat

- La2004
- La2010
- JPL Horizons DE441
- LR04
- GISTEMP observationnel
- NASA Exoplanet Archive

Les états orbitaux ne sont pas transformés en histoires géochimiques planétaires. GISTEMP observationnel n'est pas transformé en ensemble climatique multi-modèles.

## Vivant et prébiotique

- Papastavrou, Horning et Joyce : évolution d'ARN catalytique
- Windels : cycles, survie, MIC et persistance
- Donofrio : MIC et fitness sous limitations carbone et azote
- Sokolskyi et Baum : seize expériences de transfert, quatre séries temporelles, Figure 3, Nile Red, turbidités pré-amphiphiles et vésicules alimentaires

## Tables produites

- `partition_experiments.csv`
- `prebiotic_design.csv`
- `prebiotic_lineages.csv`
- `prebiotic_parent_offspring_pairs.csv`
- `prebiotic_timecourses.csv`
- `prebiotic_timecourse_summary.csv`
- `prebiotic_auxiliary_measurements.csv`
- `prebiotic_log_auxiliary_measurements.csv`
- `cell_architecture.csv`
- `antibiotic_design.csv`
- `antibiotic_fitness_real.csv`
- `benchmark_cases.csv`
- `biology_cases.csv`
- `REAL_DATA_COVERAGE.json`

## Règle de sécurité

L'existence d'un fichier ne suffit jamais à valider tous les tests qui portent son nom. `REAL_DATA_COVERAGE.json` contient la liste des protocoles réellement couverts. Toute variable non publiée reste vide et les tests qui l'exigent restent bloqués.
