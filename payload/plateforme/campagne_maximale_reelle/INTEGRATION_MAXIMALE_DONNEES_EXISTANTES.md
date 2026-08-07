# Intégration maximale des données déjà présentes

Aucun gabarit de `examples/data` n'est utilisé. Aucune valeur absente n'est imputée.

## Tables produites

### partition_experiments

```json
{
  "complete_regression_rows": 35,
  "elements": [
    "C",
    "H",
    "N",
    "S"
  ],
  "extension_source": "donnees_externes/partage_carbone_2026/raw/Dataset_Fig4_FigS1_FigS2_DC_1.csv",
  "extension_source_sha256": "6040c58d3c19f069c2397f4a71b5de3da0ebb791ae3064e4baa8e407b3a2c583",
  "new_carbon_rows": 32,
  "rows": 41,
  "source": "01_branche_matiere/hypergraphe_transformations/coefficients_partage.csv",
  "source_sha256": "10a7a9c3acfa91a5e91b3cfb14cbb7c7f265ff252664b62d9b637c1e5292321b",
  "sources": [
    "Blanchard 21",
    "Dasugpta 2013 101",
    "Fichtner 2021 41",
    "Fischer 2020 121",
    "Kuwahara 2019 61",
    "Kuwahara 2021 81",
    "S28",
    "S29",
    "S30",
    "S31",
    "this study"
  ],
  "total_rows": 41
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
  "benchmark_preserved": true,
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

### modern_climate_ensemble

```json
{
  "models": 83,
  "regions": [
    "North_Atlantic",
    "global"
  ],
  "rows": 142745,
  "scenarios": [
    "amip_control",
    "historical-ssp126",
    "historical-ssp245",
    "historical-ssp585",
    "idealized_4xCO2",
    "idealized_plus2K",
    "idealized_plus4K",
    "observational_uncertainty"
  ],
  "source_mode": "committed_canonical_table",
  "variables": [
    "NASST_anomaly",
    "near_surface_air_temperature_C",
    "surface_temperature_response_C",
    "temperature_anomaly_C"
  ]
}
```

### astrochemistry

```json
{
  "molecular_inventory": {
    "environments": 1,
    "rows": 19,
    "scope": "Table canonique versionnée; aucune archive brute n'est reconstruite pendant le workflow.",
    "species": 19
  },
  "networks": {
    "KIDA_UVA_2024": 7667,
    "UMIST_RATE22": 8767
  },
  "rate_uncertainty_coverage": 0.46653279785809904,
  "reaction_rows": 16434,
  "source_mode": "committed_canonical_tables",
  "species_in_reactions": 642
}
```

### nucleosynthesis_yields

```json
{
  "element_rows": 1383,
  "isotope_rows": 56507,
  "model_families": [
    "LC18",
    "La22",
    "Pi16",
    "Ra02",
    "Ri18",
    "Si18"
  ],
  "models": 18,
  "source_mode": "committed_canonical_tables"
}
```

### isotope_tracers

```json
{
  "dh_groups": 85,
  "dh_rows": 362,
  "dh_uncertainty_coverage": 0.6298342541436464,
  "source_mode": "committed_canonical_table"
}
```

### endosymbiosis_events

```json
{
  "genomes": 85,
  "hmm_rows": 15810,
  "source_mode": "committed_canonical_tables",
  "symbionts": 79
}
```

### partition_experiments_extension

```json
{
  "complete_regression_rows": 35,
  "extension_source": "donnees_externes/partage_carbone_2026/raw/Dataset_Fig4_FigS1_FigS2_DC_1.csv",
  "extension_source_sha256": "6040c58d3c19f069c2397f4a71b5de3da0ebb791ae3064e4baa8e407b3a2c583",
  "new_carbon_rows": 32,
  "rows": 41,
  "sources": [
    "Blanchard 21",
    "Dasugpta 2013 101",
    "Fichtner 2021 41",
    "Fischer 2020 121",
    "Kuwahara 2019 61",
    "Kuwahara 2021 81",
    "S28",
    "S29",
    "S30",
    "S31",
    "this study"
  ],
  "total_rows": 41
}
```

## Portée réelle dans le catalogue

- **antibiotic_cycles** : 0 tests couverts. Histoires d’exposition expérimentales réelles; aucun test générique n’est autorisé sans critère ciblé.
- **antibiotic_design** : 3 tests couverts. Audit du nombre de lignées, séparation MIC/survie/persistance et mesures de fitness Donofrio. Randomisation, aveuglement, biofilms et plusieurs espèces ne sont pas documentés.
- **antibiotic_lineages** : 0 tests couverts. Lignées expérimentales réelles; aucun test générique n’est autorisé sans pipeline dédié.
- **antibiotic_measurements** : 0 tests couverts. Mesures expérimentales réelles; aucun test générique n’est autorisé par simple présence.
- **benchmark_cases** : 0 tests couverts. Benchmark exploratoire dérivé de données réelles dans 8 domaines. Les cibles sont des directions binaires dérivées avant analyse. Aucune réplication externe ni prédiction confirmatoire n'est revendiquée. Utilisable pour développement exploratoire, pas comme preuve empirique confirmatoire.
- **biology_cases** : 0 tests couverts. Cas dérivés de deux domaines biologiques réels, avec séparation train/validation/test. Les six dimensions complètes et Pacc ne sont pas mesurés. Les étiquettes sont dérivées; la matrice générique ne remplace pas les pipelines expérimentaux dédiés.
- **body_properties** : 0 tests couverts. Propriétés de corps utilisées comme entrées de modèle; elles ne constituent pas un test causal empirique.
- **cell_architecture** : 0 tests couverts. Inventaire qualitatif couvrant archées, bactéries et plusieurs cellules eucaryotes. Pas de perturbations publiques, survie, récupération ou validation masquée.
- **chronometers** : 0 tests couverts. Chronomètres publiés potentiellement empiriques, mais aucun test générique n’est autorisé avant audit source-échantillon-incertitude.
- **endosymbiosis_events** : 1 tests couverts. Réduction génomique mesurée par matrice HMM sur 85 génomes. Hôtes, phylogénies, transferts nucléaires, dépendances directes et systèmes d'import protéique ne sont pas reliés dans cette source.
- **ephemerides** : 0 tests couverts. Éphémérides calculées/assimilées; référence de modèle, pas observation brute indépendante pour la matrice générique.
- **exoplanet_observations** : 0 tests couverts. Catalogue observationnel réel NASA Exoplanet Archive; aucun test générique n’est autorisé sans protocole ciblé gelé.
- **isotope_tracers** : 0 tests couverts. Compilation D/H, mesures Cr d'Ivuna et Ca lunaires avec provenance. Elle compile des traceurs disponibles, mais ne suffit pas à tester la dichotomie carbonée/non carbonée. P1-001 demande explicitement Ti, Cr, Mo, W, Ni, Ru, Pd; la table canonique actuelle ne couvre pas cet ensemble complet.
- **late_accretion_tracers** : 1 tests couverts. 122 159 mesures GEOROC de Mo, W et HSE. candidate_source est une famille rocheuse/tectonique, pas un pôle de mélange; uncertainty est vide dans cette extraction. La table couvre seulement la compilation P5-001. Dates/masses d’apport, équilibration noyau, impact lunaire, CC/NC, modèles de mélange et validation croisée restent bloqués.
- **matter_transitions** : 0 tests couverts. Transitions historiques codées et documentaires; pas de test empirique générique autorisé.
- **modern_climate_ensemble** : 0 tests couverts. Observations avec incertitude, trajectoires CMIP6 multi-modèles/scénarios et expériences idéalisées. Aucun coût matériel, overshoot explicite, retrait ou restauration n'est fourni. Le jeu mélange observations et sorties de modèles climatiques; il est exclu du mode preuve empirique stricte.
- **modern_climate_timeseries** : 0 tests couverts. 7 193 points issus de GISTEMP LSAT/SST/combiné et HadCRUT5. Ce sont quatre reconstructions de température, pas quatre compartiments de mémoire ni un forçage. Elles ne débloquent donc aucun test CL1/CL2 de mémoire, D-H-L ou restauration.
- **molecular_inventory** : 0 tests couverts. Conditions initiales Rate22 directement compatibles avec les espèces du réseau. La compilation d'acides aminés est auxiliaire; aucun inventaire radioastronomique n'est prétendu.
- **nucleosynthesis_yields** : 0 tests couverts. Dix-huit modèles CCSN, six familles et trois masses : utilisables pour l'effet de masse. Pas de BBN, AGB, fusions compactes, rotation/binarité contrôlée ni incertitudes publiées dans le conteneur. Les rendements sont des sorties de modèles stellaires, pas des observations directes.
- **orbital_initial_conditions** : 0 tests couverts. Conditions initiales issues d’éphémérides et utilisées comme entrées de simulation; pas une preuve interventionnelle empirique.
- **orbital_reference** : 0 tests couverts. Référence orbitale calculée; contrôle de modèle, pas preuve empirique directe.
- **orbital_timeseries** : 0 tests couverts. Séries orbitales issues de solutions ou d’intégrations numériques; sorties de modèle.
- **paleoclimate_timeseries** : 0 tests couverts. Séries paléoclimatiques publiées; aucun test générique n’est autorisé avant protocole long, chronologie et contrôles gelés.
- **partition_experiments** : 2 tests couverts. Compilation étendue par des expériences de partage du carbone avec P, T, redox et logD. Trajectoires planétaires, ordre des apports, océans magmatiques et validation aveugle restent absents. Seules la compilation et l’harmonisation P-T-redox-composition sont admises en mode empirique strict; méta-analyse hiérarchique, interactions et lois concurrentes restent à implémenter.
- **planetary_histories** : 0 tests couverts. Contrat composite non rempli; le fichier doit rester absent jusqu’à provenance primaire par cellule.
- **prebiotic_design** : 2 tests couverts. Plan réel des transferts de vésicules. Température, pH, UV, minéral et cycles humide-sec ne sont pas renseignés dans ces fichiers et restent absents.
- **prebiotic_lineages** : 0 tests couverts. Turbidité A400, cartes de transfert, sélection/dérive, alimentation/résuspension, durées de génération, séries temporelles et mesures auxiliaires. Aucune longueur de polymère, fidélité de copie, fusion/division directe ou autonomie métabolique n'est inventée. Les preuves vésicules restent portées par le pipeline dédié préenregistré; la matrice générique de 683 tests ne les convertit pas automatiquement en pass empiriques.
- **prebiotic_rna_evolution** : 0 tests couverts. Mesures expérimentales réelles d’évolution ARN; aucun protocole générique n’est autorisé en dehors des analyses dédiées.
- **reaction_network** : 0 tests couverts. Deux réseaux gazeux indépendants avec taux, températures et incertitudes KIDA. Pas de chimie de surface, glaces, ordre d'irradiation ni inventaire radioastronomique. Les taux mélangent mesures, estimations et calculs; ce réseau sert à la modélisation, pas à une preuve empirique directe.
- **relations** : 0 tests couverts. Relations typées construites par ORI-C; elles ne sont pas des observations indépendantes.
- **states** : 0 tests couverts. États ORI-C dérivés; aucune observation primaire autonome n’est attribuée à cette table.
- **thermochemical_phases** : 0 tests couverts. 64 512 points calculés à partir de paramètres CHNOSZ/OBIGT et Berman publiés. La table est utile comme entrée thermodynamique mais ne constitue ni une séquence de condensation à l’équilibre ni une observation de phases formées. Aucun test M4 n’est débloqué par la table seule.
- **volatile_inventory** : 0 tests couverts. Dix scénarios C-H-N-S issus de valeurs publiées, mais aucun ne publie simultanément tous les compartiments initial+noyau+manteau+atmosphère+pertes. Les cellules vides restent inconnues et ne sont jamais traitées comme zéro; aucune fermeture exacte ni test P4 n’est donc revendiqué.
