# Instructions de mise à jour

## Fichiers à supprimer avant copie

**Aucun fichier à supprimer.**

La copie du ZIP complet peut remplacer directement le contenu existant. Tous les fichiers ajoutés et remplacés doivent être publiés dans le même commit.

## Objet de cette mise à jour

Cette version cesse de limiter l'analyse aux trois jeux du workflow `Recherche suivante`. Elle raccorde à la campagne maximale tout jeu réel déjà présent dans les trois branches dès que sa structure permet une conversion sans invention ni imputation.

La campagne complète passe de :

- 211 à **278 réussites techniques**
- 440 à **357 blocages**
- 32 à **48 protocoles explicitement non exécutables informatiquement**
- 0 échec et 0 erreur dans les deux versions

Les 67 réussites supplémentaires restent exploratoires. Le nombre de verdicts scientifiques confirmatoires demeure nul.

## Fichiers ajoutés

- `plateforme/campagne_maximale_reelle/integrer_donnees_existantes.py`
- `plateforme/campagne_maximale_reelle/resumer_integration_maximale.py`
- `plateforme/campagne_maximale_reelle/AUDIT_DONNEES_DEPOT.json`
- `plateforme/campagne_maximale_reelle/AUDIT_DONNEES_DEPOT.md`
- `plateforme/campagne_maximale_reelle/DONNEES_UTILISEES_MAXIMUM.md`
- `plateforme/campagne_maximale_reelle/INTEGRATION_MAXIMALE_DONNEES_EXISTANTES.md`
- `plateforme/campagne_maximale_reelle/PROVENANCE_INTEGRATION_DEPOT.json`
- `plateforme/campagne_maximale_reelle/data/REAL_DATA_COVERAGE.json`
- `plateforme/campagne_maximale_reelle/data/partition_experiments.csv`
- `plateforme/campagne_maximale_reelle/data/prebiotic_design.csv`
- `plateforme/campagne_maximale_reelle/data/prebiotic_lineages.csv`
- `plateforme/campagne_maximale_reelle/data/prebiotic_parent_offspring_pairs.csv`
- `plateforme/campagne_maximale_reelle/data/prebiotic_timecourses.csv`
- `plateforme/campagne_maximale_reelle/data/prebiotic_timecourse_summary.csv`
- `plateforme/campagne_maximale_reelle/data/prebiotic_auxiliary_measurements.csv`
- `plateforme/campagne_maximale_reelle/data/prebiotic_log_auxiliary_measurements.csv`
- `plateforme/campagne_maximale_reelle/data/cell_architecture.csv`
- `plateforme/campagne_maximale_reelle/data/antibiotic_design.csv`
- `plateforme/campagne_maximale_reelle/data/antibiotic_fitness_real.csv`
- `plateforme/campagne_maximale_reelle/data/benchmark_cases.csv`
- `plateforme/campagne_maximale_reelle/data/biology_cases.csv`
- `plateforme/campagne_maximale_reelle/resultats_integration_maximale/REPORT.md`
- `plateforme/campagne_maximale_reelle/resultats_integration_maximale/results.csv`
- `plateforme/campagne_maximale_reelle/resultats_integration_maximale/results.json`
- `plateforme/source_corrigee/tests/test_real_data_scope.py`

## Fichiers remplacés

- `.github/workflows/analyse-donnees-reelles.yml`
- `03_branche_vivant/lignees_vesicules/analyser_lignees.py`
- `DATA_AVAILABILITY.md`
- `INSTRUCTIONS_MISE_A_JOUR.md`
- `plateforme/campagne_maximale_reelle/BILAN_CANONIQUE.md`
- `plateforme/source_corrigee/src/oric_full/data_registry.py`
- `plateforme/source_corrigee/src/oric_full/domains/benchmark.py`
- `plateforme/source_corrigee/src/oric_full/domains/biology.py`
- `plateforme/source_corrigee/src/oric_full/domains/planetary.py`
- `plateforme/source_corrigee/src/oric_full/domains/prebiotic.py`
- `plateforme/source_corrigee/src/oric_full/engines.py`
- `plateforme/source_corrigee/src/oric_full/runner.py`
- `plateforme/source_corrigee/tests/test_runner.py`
- `MANIFEST.sha256`
- `MANIFEST.sha256.json`

## Données désormais exploitées

- 21 439 nœuds de lignées de vésicules
- 13 680 transferts parent-descendant
- 59 328 mesures temporelles réparties en 576 séries
- 448 mesures brutes de la Figure 3
- 19 392 mesures supplémentaires : Nile Red, turbidité pré-amphiphiles et vésicules alimentaires
- 9 expériences de partage métal-silicate
- 13 entrées d'architecture cellulaire
- 10 conditions antibiotiques et 72 mesures de fitness indépendantes
- 17 506 cas de benchmark dans huit domaines
- 14 777 cas biologiques dans quatre domaines

## Problèmes explicitement conservés

La mise à jour ne transforme pas un fichier partiel en validation générale. Les 357 blocages restants sont documentés dans `AUDIT_DONNEES_DEPOT.md`.

Les principaux jeux encore réellement absents sont les rendements de nucléosynthèse, le réseau astro-chimique quantitatif, les phases thermochimiques quantitatives, les traceurs isotopiques, les inventaires volatils, les traceurs d'accrétion tardive, les histoires planétaires, les événements d'endosymbiose et l'ensemble climatique requis.

L'ancien bilan mentionnait 338 400 lignes d'incertitude GISTEMP, mais le fichier n'est pas présent dans l'archive actuelle. Cette incohérence est maintenant signalée.

## Exécution GitHub recommandée

1. Copier le contenu complet du ZIP dans le dépôt.
2. Publier tous les fichiers ajoutés et remplacés dans le même commit.
3. Ouvrir `Campagne maximale ORI-C - trois branches`.
4. Choisir `maximum`.
5. Télécharger l'artefact `analyses-donnees-reelles-*` produit par la branche réutilisable.

Le journal doit contenir l'étape :

`Intégrer toutes les données réelles déjà présentes`

puis :

`Produire le bilan transparent des 683 entrées`

Le bilan attendu est : 278 réussites, 357 blocages, 48 non exécutés, 0 échec et 0 erreur.
