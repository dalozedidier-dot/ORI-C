# Intégration maximale des données déjà présentes

Aucun gabarit de `examples/data` n'est utilisé. Aucune valeur absente n'est imputée.

## Tables produites

### partition_experiments

```json
{
  "complete_regression_rows": 3,
  "elements": [
    "C",
    "H",
    "N",
    "S"
  ],
  "rows": 9,
  "source": "01_branche_matiere/hypergraphe_transformations/coefficients_partage.csv",
  "source_sha256": "10a7a9c3acfa91a5e91b3cfb14cbb7c7f265ff252664b62d9b637c1e5292321b"
}
```

### prebiotic_lineages

```json
{
  "coded_lineage_fraction": 1.0,
  "conditions": [
    "FR",
    "FU",
    "UR",
    "UU"
  ],
  "figure3_measurements": 448,
  "generation_durations_h": [
    0.5,
    1.5,
    5.0,
    24.0
  ],
  "lineage_nodes": 21439,
  "log_auxiliary_measurements": 19392,
  "log_auxiliary_types": {
    "food_vesicle_turbidity_A400": 10944,
    "nile_red_fluorescence": 6336,
    "pre_amphiphile_turbidity_A400": 2112
  },
  "log_files": 16,
  "parent_offspring_pairs": 13680,
  "source": "donnees_externes/vesicules_sokolskyi_baum_2026/raw/doi_10_5061_dryad_fbg79cp99__v20260309.zip",
  "source_sha256": "2cf96ae6906c5d41a889d8deced000237cb1da2e083a1df526dc730130687863",
  "timecourse_rows": 59328,
  "timecourse_series": 576
}
```

### prebiotic_design

```json
{
  "rows": 32,
  "source": "donnees_externes/vesicules_sokolskyi_baum_2026/raw/doi_10_5061_dryad_fbg79cp99__v20260309.zip"
}
```

### prebiotic_timecourses

```json
{
  "conditions": [
    "FR",
    "FU",
    "UR",
    "UU"
  ],
  "rows": 59328,
  "series": 576,
  "source_files": [
    "FR_inc.xlsx",
    "FU_inc.xlsx",
    "UR_inc.xlsx",
    "UU_inc.xlsx"
  ]
}
```

### prebiotic_auxiliary_measurements

```json
{
  "panels": [
    "Calcein",
    "DLS",
    "Eu SDIP",
    "Nile Red",
    "Rhodamine B",
    "Turbidity"
  ],
  "rows": 448,
  "source_file": "Fig3-data.xlsx"
}
```

### prebiotic_log_auxiliary_measurements

```json
{
  "measurements": {
    "food_vesicle_turbidity_A400": 10944,
    "nile_red_fluorescence": 6336,
    "pre_amphiphile_turbidity_A400": 2112
  },
  "rows": 19392,
  "source_files": 8
}
```

### cell_architecture

```json
{
  "cell_types": [
    "Archée",
    "Bactérie",
    "Cellule animale",
    "Cellule fongique",
    "Cellule végétale",
    "Protiste"
  ],
  "rows": 13,
  "source": "01_branche_matiere/inventaire_hierarchique/tables/11_Biologique.csv",
  "source_sha256": "f08cb815e74a0068959722334c747fec6007c4417b85820db40efe6a1c5bd2e5"
}
```

### antibiotic_design

```json
{
  "conditions_with_12_or_more": 9,
  "design_rows": 10,
  "fitness_rows": 72,
  "measurement_coverage": {
    "fitness": 0.0,
    "growth_rate": 0.0,
    "lag_time": 0.0,
    "mic": 0.11797752808988764,
    "persister_fraction": 0.11797752808988764,
    "survival": 0.8820224719101124
  },
  "replicates_max": 33,
  "replicates_min": 4,
  "sources": [
    "donnees_externes/histoire_antibiotique_donofrio_2026/extracted/Figure_2_C-limited_Fitness.csv",
    "donnees_externes/histoire_antibiotique_donofrio_2026/extracted/Figure_2_N-limited_Fitness.csv"
  ]
}
```

### benchmark_cases

```json
{
  "benchmark_domains": {
    "antibiotic": 288,
    "antibiotic_longitudinal": 739,
    "matter_transition": 40,
    "modern_climate": 1152,
    "orbital": 1020,
    "paleoclimate": 517,
    "rna_evolution": 70,
    "vesicle": 13680
  },
  "benchmark_rows": 17506,
  "benchmark_splits": {
    "test": 6552,
    "train": 6405,
    "validation": 4549
  },
  "biology_domains": {
    "antibiotic": 288,
    "antibiotic_longitudinal": 739,
    "rna_evolution": 70,
    "vesicle": 13680
  },
  "biology_rows": 14777
}
```

### biology_cases

```json
{
  "domains": {
    "antibiotic": 288,
    "antibiotic_longitudinal": 739,
    "rna_evolution": 70,
    "vesicle": 13680
  },
  "rows": 14777
}
```

## Portée réelle dans le catalogue

- **partition_experiments** : 2 tests couverts. Neuf coefficients pour H, C, N et S. Trois lignes seulement possèdent simultanément P, T, ΔIW et logD; aucune trajectoire d'accrétion, planète ou validation aveugle n'est déduite.
- **prebiotic_design** : 4 tests couverts. Plan réel des transferts de vésicules. Température, pH, UV, minéral et cycles humide-sec ne sont pas renseignés dans ces fichiers et restent absents.
- **prebiotic_lineages** : 22 tests couverts. Turbidité A400, cartes de transfert, sélection/dérive, alimentation/résuspension, durées de génération, séries temporelles et mesures auxiliaires. Aucune longueur de polymère, fidélité de copie, fusion/division directe ou autonomie métabolique n'est inventée.
- **cell_architecture** : 1 tests couverts. Inventaire qualitatif couvrant archées, bactéries et plusieurs cellules eucaryotes. Pas de perturbations publiques, survie, récupération ou validation masquée.
- **biology_cases** : 3 tests couverts. Cas dérivés de deux domaines biologiques réels, avec séparation train/validation/test. Les six dimensions complètes et Pacc ne sont pas mesurés.
- **antibiotic_design** : 3 tests couverts. Audit du nombre de lignées, séparation MIC/survie/persistance et mesures de fitness Donofrio. Randomisation, aveuglement, biofilms et plusieurs espèces ne sont pas documentés.
- **benchmark_cases** : 32 tests couverts. Benchmark exploratoire dérivé de données réelles dans cinq domaines. Les cibles sont des directions binaires dérivées avant analyse. Aucune réplication externe ni prédiction confirmatoire n'est revendiquée.
