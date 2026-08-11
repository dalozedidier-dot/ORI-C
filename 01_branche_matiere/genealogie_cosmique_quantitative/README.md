# Généalogie cosmique empirique — du Big Bang chaud à l’architecture du Système solaire

Cette couche développe le raccordement historique qui manquait entre l’inventaire cosmique primordial, l’enrichissement stellaire, la matière présolaire, le disque protoplanétaire et l’architecture planétaire observée.

## Règle de preuve

Cette branche est **empirique uniquement**. Aucune simulation, donnée synthétique, donnée construite, imputation, table de rendement théorique, sortie thermochimique ou intégration orbitale n’entre dans les verdicts. Lorsqu’un article combine observations et modèles, seules les grandeurs effectivement mesurées et explicitement déclarées dans `SOURCES_EMPIRIQUES.csv` sont transcrites dans `data/MESURES_EMPIRIQUES.csv`.

Les sorties de C-AST restent séparées. Elles peuvent tester les conséquences d’une architecture donnée, mais elles ne servent jamais de preuve de la genèse de cette architecture.

## Question scientifique

Le test n’est pas « l’Univers change-t-il avec le temps ? ». Il cherche des **porteurs physiques d’histoire** mesurables : composition, poussières, grains présolaires, molécules, isotopes, réservoirs, âges, structures de disque, corps différenciés, protoplanètes et signatures d’accrétion. La question ORI-C est de savoir si ces inscriptions issues d’étapes antérieures persistent assez pour modifier les constituants, contraintes ou architectures disponibles aux étapes suivantes.

## Chaîne couverte

La campagne couvre 20 stades : inventaire primordial observationnel → produits stellaires observés → poussière dans les éjecta → grains présolaires retournés → nuages denses → apport nuage/disque → molécules dans les disques → solides réfractaires → réservoirs isotopiques solaires → redistribution enregistrée dans Wild 2 → chronologie CAI/chondres → agrégation et instabilité collective en laboratoire → petits corps différenciés/hydratés → disques structurés → protoplanètes en accrétion → histoires isotopiques de Mars et de la Terre → architecture actuelle.

Les liens ne sont pas tous de même nature. `LIENS_EMPIRIQUES.csv` distingue les continuités matérielles directes, les séquences chronométriques du Système solaire, les analogues astrophysiques inter-systèmes et les ponts mécanisme→observation non uniques.

## Résultat courant

`resultats/SYNTHESE.json` porte le verdict machine. La synthèse initiale soutient le **mécanisme de transmission historique** au niveau empirique : plusieurs classes indépendantes d’archives montrent que des produits d’étapes antérieures persistent et sont encore mesurables dans des étapes ultérieures. Elle ne démontre ni une loi universelle ORI-C ni une trajectoire orbitale unique.

Le problème inverse « quelle unique histoire orbitale conduit exactement aux éléments orbitaux actuels ? » reste `undetermined_empirical_only`. Cette limite est volontaire : elle n’est pas fermée par une simulation.

## Fichiers d’autorité

- `EMPIRICAL_ONLY_POLICY.json` : ce qui est admissible ou interdit comme preuve.
- `SOURCES_EMPIRIQUES.csv` : sources primaires/officielles, portion utilisée et portion exclue.
- `data/MESURES_EMPIRIQUES.csv` : grandeurs transcrites depuis les mesures publiées.
- `CHAINE_EMPIRIQUE.csv` : stades et porteurs d’histoire.
- `LIENS_EMPIRIQUES.csv` : liens et force de lecture autorisée.
- `CRITERES_REPLICATION_FUTURE.json` : critères gelés après la synthèse initiale, sans rétroactivité.
- `resultats/AUDIT_ADMISSIBILITE.json` : audit machine du pare-feu empirique.
- `resultats/RESULTATS_CLEFS.csv` : verdicts locaux.
- `resultats/MATRICE_PREUVES_EMPIRIQUES.csv` : ce que chaque résultat établit et ce qu’il n’établit pas.
- `resultats/RESULTATS.sha256` : empreintes des sorties.

## Exécution

```bash
python 01_branche_matiere/genealogie_cosmique_quantitative/run_all.py
python -m pytest -q 01_branche_matiere/genealogie_cosmique_quantitative/tests
```

Le recalcul doit être byte-for-byte reproductible à partir des tables empiriques versionnées.
