# Campagne réelle consolidée - bilan canonique

Date de réexécution : 5 août 2026. Catalogue : 683 entrées.

## Changement de méthode

La campagne commence désormais par `integrer_donnees_existantes.py`. Cette étape parcourt les jeux réels déjà présents dans les trois branches, les convertit vers les schémas de la plateforme sans inventer de valeur et écrit `REAL_DATA_COVERAGE.json`. Une table partielle ne débloque que les protocoles explicitement couverts par ses mesures.

Les gabarits de `plateforme/source_corrigee/examples/data/` restent exclus.

## Données nouvellement raccordées

| Jeu raccordé | Volume réellement utilisé |
|---|---:|
| Lignées de vésicules | 21 439 nœuds |
| Transferts parent-descendant | 13 680 paires |
| Séries temporelles de turbidité | 59 328 mesures, 576 séries |
| Mesures Figure 3 | 448 valeurs |
| Mesures auxiliaires des classeurs log | 19 392 valeurs |
| Expériences de partage métal-silicate | 9 lignes, dont 3 complètes pour P-T-redox-logD |
| Architecture cellulaire | 13 lignes |
| Plans antibiotiques réels | 10 conditions |
| Fitness antibiotique indépendante | 72 mesures |
| Benchmark multi-domaines | 17 506 cas dans 8 domaines |
| Cas biologiques | 14 777 cas dans 4 domaines |

Le benchmark exploite les transitions matérielles, La2004, LR04, GISTEMP, les vésicules, l'évolution expérimentale de l'ARN, Windels et Donofrio. Ses cibles binaires sont dérivées avant ajustement. Il reste exploratoire.

## Résultat des 683 entrées

| Statut technique | Avant intégration | Après intégration |
|---|---:|---:|
| Réussites | 211 | **278** |
| Blocages | 440 | **357** |
| Protocoles non exécutés informatiquement | 32 | **48** |
| Échecs | 0 | **0** |
| Erreurs | 0 | **0** |

L'intégration produit 67 réussites techniques supplémentaires. Seize anciens blocages ont été reclassés correctement comme protocoles humains, de laboratoire ou de réplication externe.

## Résultats exploratoires calculés

Dans le benchmark biologique, l'ajout de l'histoire à l'état présent améliore l'exactitude équilibrée de 0,6241 à 0,6791, soit un gain de 0,0550. L'ajout des variables ORI-C disponibles porte cette valeur à 0,6802. Le score de Brier passe de 0,2262 à 0,1981 avec l'histoire.

Dans le benchmark multi-domaines, l'exactitude passe de 0,6103 avec l'état seul à 0,6741 avec l'histoire, soit un gain de 0,0638. L'exactitude équilibrée gagne 0,0637 et le score de Brier s'améliore de 0,0277. Les effets varient selon les domaines et deviennent négatifs dans certains cas, notamment le paléoclimat de cette construction. Ces différences sont conservées comme contre-exemples internes.

Pour les vésicules, les quatre conditions FR, FU, UR et UU, les bras sélection et dérive, les durées de 0,5 h, 1,5 h, 5 h et 24 h, les cartes de transfert, les séries temporelles, Nile Red, les turbidités avant amphiphiles et les turbidités des vésicules alimentaires sont maintenant intégrés. Aucun paramètre moléculaire absent n'est imputé.

Pour le partage métal-silicate, les neuf coefficients sont compilés et harmonisés. Trois lignes seulement possèdent simultanément pression, température, redox et logD. La méta-régression reste donc non revendiquée.

## Statut scientifique

| Verdict scientifique | Nombre |
|---|---:|
| Soutient | 0 |
| Ne soutient pas | 0 |
| Indéterminé | 635 |
| Non applicable | 48 |

Les 278 réussites sont des réussites techniques ou exploratoires. Elles ne constituent pas automatiquement des confirmations d'ORI-C. Aucun critère confirmatoire gelé propre à ces 635 entrées n'autorise encore un verdict de soutien ou de rejet.

## Pourquoi 357 entrées restent bloquées

Les causes racines sont détaillées dans `AUDIT_DONNEES_DEPOT.md` et `AUDIT_DONNEES_DEPOT.json` :

- 113 entrées demandent des mesures que les tables réelles partielles ne couvrent pas
- 114 entrées nécessitent une génération ou une simulation interdite en mode réel strict
- 112 entrées dépendent encore de jeux quantitatifs réellement absents
- 18 entrées climatiques demandent des forçages, retraits, restaurations ou trajectoires que GISTEMP observationnel ne contient pas

L'ancien bilan indiquait 338 400 lignes d'incertitude GISTEMP. Le fichier correspondant n'est pas présent dans l'archive actuelle. Cette incohérence est désormais signalée au lieu d'être comptée comme donnée active.
