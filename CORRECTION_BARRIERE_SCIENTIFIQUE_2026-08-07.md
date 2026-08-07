# ORI-C — correction de la barrière scientifique

Date : 7 août 2026

## Pourquoi cette correction est nécessaire

L'audit du mode `--real-data-only` a montré qu'un nombre élevé de `pass` techniques pouvait être obtenu alors que certains protocoles n'étaient pas réellement couverts par les mesures disponibles. Le problème n'est pas la présence de données réelles : le dépôt en contient beaucoup. Le défaut est dans la logique d'autorisation du moteur de campagne.

Deux mécanismes étaient en cause :

1. le mode réel était **fail-open** lorsqu'un dataset n'avait pas d'entrée dans `REAL_DATA_COVERAGE.json` ; l'existence d'un CSV portant le bon nom pouvait alors suffire à laisser exécuter tous les tests qui le réclamaient ;
2. plusieurs tests différents partageaient un moteur générique dont le calcul ne répondait pas à la question scientifique détaillée du test.

Le compteur technique `pass` n'est donc pas un compteur de preuves. La classe `ScientificVerdict` reste séparée, et sans critère gelé le verdict scientifique demeure `undetermined`.

## Corrections appliquées

### 1. Mode données réelles désormais fail-closed

Dans `plateforme/source_corrigee/src/oric_full/runner.py`, tout dataset requis doit maintenant :

- être présent dans `REAL_DATA_COVERAGE.json` ;
- utiliser `scope_mode = allow_list` ;
- citer explicitement le `test_id` courant dans `supported_test_ids`.

Sinon le test est `blocked`. La présence physique d'un fichier n'est plus suffisante.

### 2. Quarantaine de quatre moteurs historiques

Les moteurs suivants ne peuvent plus produire un `pass` en mode données réelles strict :

- `condensation` ;
- `volatile_budget` ;
- `late_accretion` ;
- `planetary_value`.

La liste exacte des 46 tests concernés est enregistrée dans :

`audit/TESTS_QUARANTAINE_SCIENTIFIQUE_2026-08-07.csv`

La quarantaine reste active jusqu'à l'existence d'un analyseur spécifique répondant au protocole individuel.

### 3. Condensation : retrait du faux minimum global de Gibbs

L'ancien calcul choisissait la phase ayant le plus petit `gibbs_energy` à chaque couple température/pression, y compris entre compositions chimiques différentes. Ce calcul n'est pas un calcul d'équilibre thermodynamique.

`analyze_condensation()` est maintenant un audit descriptif de la table. Il publie explicitement `equilibrium_valid = false`. Un véritable test d'équilibre devra imposer au minimum un bilan élémentaire fermé, une composition globale, les phases admissibles et une minimisation thermodynamique sous contraintes.

### 4. Volatils : aucune valeur manquante transformée en zéro

L'ancien `volatile_closure()` faisait `fillna(0.0)` sur les masses initiale, noyau, manteau, atmosphère et perdue. Une valeur inconnue pouvait ainsi devenir artificiellement une masse nulle.

La nouvelle version :

- conserve les valeurs absentes ;
- calcule une fermeture uniquement sur les lignes où les cinq termes sont réellement mesurés ou explicitement fournis ;
- bloque le moteur s'il n'existe aucune ligne complète.

### 5. Accrétion tardive : plus aucune moyenne brute entre traceurs incompatibles

L'ancien moteur moyennait `final_value` par source candidate, indépendamment du traceur. Il pouvait donc mélanger des valeurs de Mo, Ru, W, Os, Ir et Au ayant des unités et des échelles différentes.

La nouvelle version :

- travaille traceur par traceur ;
- n'effectue une comparaison que si plusieurs sources candidates existent pour le même traceur ;
- standardise le contraste par la dispersion interne du traceur ;
- n'agrège ensuite que des contrastes sans dimension.

Ce calcul reste placé en quarantaine pour les verdicts empiriques tant qu'un protocole P5 spécifique n'est pas raccordé.

### 6. `planetary_value` : proxy de mémorisation retiré

L'ancien proxy mesurait la proportion de groupes d'histoires qui conduisaient à une partition finale unique. À forte cardinalité, ce mécanisme peut mémoriser les lignes et augmenter mécaniquement avec l'ajout de colonnes.

Il est retiré. Le moteur est bloqué jusqu'à son remplacement par :

- unités indépendantes définies avant l'analyse ;
- groupes complètement tenus hors échantillon ;
- cible quantitative gelée ;
- modèle de même complexité sans histoire ;
- prédictions enregistrées avant ouverture du groupe tenu à l'écart.

Il n'existe donc **aucun `planetary_histories.csv` à fabriquer comme pseudo-donnée réelle**.

### 7. Dates climatiques ISO

`compare_memory_families()` accepte désormais soit un axe numérique, soit des dates ISO. Les dates sont converties en années écoulées depuis la première observation. Une date invalide provoque une erreur ; elle n'est pas imputée.

### 8. Fichiers Excel fermés explicitement

Les utilisations de `pd.ExcelFile` dans `integrer_donnees_existantes.py` sont encapsulées dans des context managers afin d'éviter les verrous de fichier sous Windows.

### 9. Lecture UTF-8 explicite

`scripts/valider_publication_stable.py` lit maintenant tous ses fichiers texte avec `encoding="utf-8"`.

### 10. Publication bloquée si la barrière régresse

Nouveau script :

`scripts/valider_barriere_scientifique_publication.py`

Il vérifie avant une publication stable :

- que le registre réel est fail-closed ;
- qu'aucun moteur en quarantaine n'est déclaré comme preuve empirique ;
- qu'aucun ancien résultat `real_data_only` ne contient un `pass` d'un moteur en quarantaine ;
- qu'aucune imputation zéro n'est réintroduite dans le bilan volatil ;
- que le faux minimum Gibbs n'est pas réintroduit ;
- que la gestion des dates, UTF-8 et classeurs Excel reste corrigée.

Le workflow `.github/workflows/release.yml` exécute cette barrière avant de pouvoir construire une publication stable.

## Effet sur le compteur de la campagne plateforme

Sur la copie isolée utilisée pour cette correction, la campagne des 683 entrées, exécutée avec la nouvelle politique `--real-data-only`, donne :

- 86 `pass` techniques ;
- 549 `blocked` ;
- 0 `fail` ;
- 0 `error` ;
- 48 `not_run`.

Les 635 protocoles computationnels restent `scientific_verdict = undetermined` dans cette campagne générique, car aucun critère gelé n'a été fourni à cette exécution.

Cette chute par rapport aux anciens compteurs n'est pas une perte de données. Elle montre que l'ancienne logique laissait exécuter des protocoles qui n'avaient pas de portée réelle explicitement enregistrée. **Le nouveau compteur est volontairement conservateur.**

Les résultats scientifiques produits par des pipelines dédiés, par exemple D'Onofrio et les lignées de vésicules, ne sont pas recalculés par ce compteur générique et ne sont pas annulés par cette correction.

## Sources réelles retenues pour la suite

Le registre :

`donnees_externes/SOURCES_EMPIRIQUES_PRIORITAIRES_2026-08-07.json`

sépare désormais trois catégories :

1. observations empiriques exploitables ;
2. données de référence servant uniquement d'entrée de modèle ;
3. objets qui ne peuvent pas être transformés honnêtement en « dataset réel ».

Sources déjà identifiées avec DOI ou dépôt persistant :

- NIST-JANAF SRD 13, DOI `10.18434/T42S31` : entrée thermodynamique de modèle, **pas preuve empirique de condensation** ;
- Cloutis et al. 2013, DOI `10.1016/j.icarus.2013.02.003` : minéralogie HED mesurée par XRD/Rietveld ;
- Peterson et al. 2023, DOI `10.1016/j.epsl.2023.118341` : CO2, H2O, F, Cl d'aubrites par NanoSIMS ;
- Abernethy et al. 2013, DOI `10.1111/maps.12184` : C et N d'angrites par combustion/mass spectrometry ;
- Defouilloy et al. 2016, DOI `10.1016/j.gca.2015.10.009` : S et isotopes du soufre, incluant des aubrites ;
- Budde et al. 2019, DOI `10.1038/s41550-019-0779-y` : données Mo et séparation CC/NC ;
- Fischer-Gödde & Kleine, dataset DOI `10.1594/IEDA/100622` : isotopes Ru, fichier EarthChem publié ;
- Goodrich et al. 2013, DOI `10.1016/j.gca.2012.06.022` : Re, Os, W, Ir, Ru, Mo, Au et autres éléments dans les ureilites ;
- Shirai et al. 2016, DOI `10.1016/j.epsl.2015.12.024` : PGE de météorites HED et matériaux projectiles.

Aucune de ces sources n'est autorisée à déverrouiller automatiquement tous les tests d'un work package. Les `eligible_test_ids` sont déclarés source par source dans le registre.

## Tests exécutés sur la correction

- `scripts/valider_barriere_scientifique_publication.py` : **OK** ;
- suite complète `plateforme/source_corrigee/tests` : **28 passés, 0 échec** ;
- tests spécifiques de barrière scientifique : **7 passés, 0 échec** ;
- compilation Python des fichiers modifiés : **OK** ;
- `scripts/valider_publication_stable.py` doit être exécuté **après application sur la branche principale actuelle**. Sur la copie canonique historique utilisée comme bac à sable, il refuse correctement les pages publiques périmées de cette ancienne copie ; ce refus n’est pas masqué.

## Décision de publication

La version Zenodo déjà publiée reste un objet historique et ne peut pas être modifiée rétroactivement. Une nouvelle version ne doit être publiée qu'après intégration de cette barrière et passage de la CI.

Les compteurs techniques de la plateforme ne doivent plus être présentés comme un nombre de « preuves ». Seuls les résultats de protocoles spécifiques, avec source réelle, portée explicite, contrôle approprié et verdict scientifique propre, peuvent entrer dans l'état des preuves.

## Reclassement des 46 tests anciennement présentés comme « déblocables par quatre fichiers »

Le reclassement complet est dans `audit/RECLASSEMENT_46_TESTS_2026-08-07.csv`.

Conclusion conservatrice :

- **6 tests** ont aujourd'hui une voie empirique externe sérieuse identifiée (`M4-007`, `M4-012`, `P4-001`, `P5-001`, `P5-005`, `P5-010`) ;
- **28 tests** exigent d'abord un modèle, une intervention, une cinétique ou un protocole spécifique et ne peuvent pas être déverrouillés par un CSV ;
- **10 tests P6** exigent un nouveau benchmark prédictif gelé construit à partir de contraintes réelles séparées ;
- `P6-011` exige explicitement une simulation et reste exclu du mode empirique ;
- `P6-012` est un préenregistrement humain, pas une analyse de données.

La formulation antérieure « quatre fichiers manquants = 46 tests réels à ouvrir » est donc retirée. Elle confondait disponibilité d'un schéma avec couverture scientifique du protocole.
