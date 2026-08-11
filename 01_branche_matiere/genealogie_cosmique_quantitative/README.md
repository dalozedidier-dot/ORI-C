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

## Campagne quantitative réelle v2

La couche quantitative ne prend plus comme résultat scientifique le simple comptage « 23 stades / 40 relations / 24 observations / 12 synthèses ». Ces fichiers v1 sont conservés pour provenance et leur statut est documenté dans `STATUT_APPROFONDISSEMENT_V1.md`.

L’autorité quantitative est désormais `GEL_ANALYSE_QUANTITATIVE_V2.json` + `src/analyser_quantitatif_reel.py`. Elle calcule huit tests/audits directement sur les mesures empiriques : réplication Bennu/Ryugu, comparaison V883 Ori/67P, chronologie avec propagation d’incertitudes, contraste temporel EC 53, réplication de streamers, réactivation tardive de Ryugu, robustesse du graphe et ablations par famille de preuve.

Les sorties d’autorité sont `resultats/TESTS_QUANTITATIFS_REELS.json`, `CHRONOLOGIE_QUANTITATIVE.csv`, `REPLICATION_ECHANTILLONS.csv`, `ROBUSTESSE_GRAPHE.json`, `REDONDANCE_PAR_STAGE.csv`, `ABLATIONS_FAMILLES_PREUVES.csv`, `VERDICT_QUANTITATIF.json` et `RAPPORT_QUANTITATIF.md`.

Le corpus v3 contient **48 sources/datasets empiriques admissibles et 120 enregistrements empiriques**. La v2 reste conservée comme étape méthodologique, mais l’autorité quantitative courante est désormais `GEL_ANALYSE_QUANTITATIVE_V3.json` + `src/analyser_quantitatif_complet.py`.

## Campagne quantitative complète v3

La v3 ne se contente plus de tester la cohérence du corpus. Elle quantifie directement des transformations historiques à partir d’entrées mesurées ou de produits empiriques officiels, avec propagation analytique des incertitudes et sans échantillonnage aléatoire.

Les huit résultats `GCQ-T09` à `GCQ-T16` établissent notamment :

- la décroissance de l’inventaire relatif de `26Al` encore disponible à quatre événements datés : **34,5 %** à l’archive angritique, **18,6 %** à EC 002, **8,18 %** au chondre jeune sélectionné et **2,30 %** à l’événement carbonate CM ;
- une fenêtre de formation de noyaux de météorites de fer vers 1,0–1,5 Myr après CAI correspondant encore à **23,5–38,0 %** de l’inventaire initial de `26Al` ;
- une séparation NC/CC persistant 2–3 Myr pendant que cet inventaire diminue d’un facteur **6,9–18,2** ;
- un contrôle post-hoc montrant qu’à ~2 Myr la référence canonique de décroissance seule (`7,56×10^-6`) ne fixe pas un inventaire local unique : deux CAI à matériel chondritique mesurent `4,7±1,4×10^-6` et `<1,2×10^-6`, tandis qu’une autre archive du corpus rapporte une hétérogénéité `26Al` d’un facteur 3–4 ;
- une borne conservatrice de persistance des porteurs présolaires supérieure à **4,567 Gyr** ;
- une réactivation fluide enregistrée dans Ryugu plus de 1 000 Myr après formation, soit plus de **1 394 demi-vies** de `26Al` ;
- une provenance terrestre laissée **empiriquement contestée** lorsque les reconstructions publiées ne convergent pas ;
- un endpoint orbital actuel quantifié sans le transformer en reconstruction historique ;
- six nœuds et six relations critiques dans la chaîne stricte produits stellaires → endpoint, tandis que la fermeture stricte baseline primordiale → endpoint reste ouverte.

Les artefacts d’autorité v3 sont `resultats/RESULTATS_QUANTITATIFS_COMPLETS.json`, `TESTS_QUANTITATIFS_COMPLETS.json`, `CLAIMS_QUANTITATIFS_COMPLETS.json`, `resultats/claims_quantitatifs_v3/`, `INVENTAIRE_26AL_PAR_EVENEMENT.csv`, `FERMETURE_RELATIONS_EMPIRIQUES.csv`, `VERROUS_BOUT_EN_BOUT.json` et `RAPPORT_QUANTITATIF_COMPLET.md`.

Le verdict v3 est `quantified_history_dependent_accessibility_with_explicit_open_links`. Il signifie que la dépendance au chemin est désormais **quantifiée sur au moins un inventaire physique réel**, tout en conservant explicitement ouverts les raccords que les données ne ferment pas.


## Extension data-rich v4

La branche exploite désormais des distributions au niveau grain/échantillon, sans remplacer les résultats v3. Le corpus d’autorité comprend 48 sources/datasets empiriques admissibles. La couche massive importe 11 467 lignes utiles normalisées, dont 11 207 grains présolaires publiés ou partiellement publiés. Les 11 567 lignes SiC marquées `Data Published = no` sont exclues des claims. Les doublons XLSX/CSV, valeurs synthétiques, priors, Monte-Carlo, imputations et sorties de simulation ne comptent pas comme preuves.

Les nouveaux claims `GCQ-T17` à `GCQ-T21` testent les distributions présolaires, la séparation multivariée NC/CC, l’hétérogénéité O-Cr-Ti des chondres d’Allende, l’hétérogénéité ε50Ti de sous-échantillons d’Allende et des contrastes isotopiques individuels dans les échantillons retournés de Bennu. Le rapport d’autorité est `resultats/RAPPORT_QUANTITATIF_DATA_RICH_V4.md`.
