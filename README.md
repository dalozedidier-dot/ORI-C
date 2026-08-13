# ORI-C — prochaines portes scientifiques, 13 août 2026

Ce paquet est un **candidat d'intégration au-dessus de `main`**, sans création de version et sans modification des quatre fichiers sources `PRED-*.json` gelés le 11 août.

## 1. VES-PACC-INT-01 finalisé

Le protocole vivant est maintenant scientifiquement rempli : `do(m)`, sham, appariement `X/Theta/A`, 12 défis futurs, 4 dimensions `R`, seuils exacts, SESOI, puissance, 48 unités parentales indépendantes, règles d'exclusion, randomisation et décision finale.

Le `do(m)` est une réinitialisation physique de la distribution de taille vésiculaire par **11 passages à travers 100 nm**. Le sham utilise **5 µm** avec la même séquence de manipulation. `m` est mesuré par DLS et reste exclu de `X`.

Le protocole est **prêt à préenregistrer, mais l'exécution reste bloquée** tant que l'URL/identifiant OSF public et les SHA-256 des fichiers gelés ne sont pas attachés. Aucune nouvelle donnée de test avant cela.

## 2. PRED-VIVANT-HISTOIRE-001 réellement lancé

Le jeu externe Santos-Lopez et al. 2021 (`eLife 10:e70676`) a été ouvert après le gel du 11 août et analysé sans déplacement du seuil.

Résultat :

- RMSE état seul : `0.937482`
- RMSE état + histoire : `0.732492`
- gain relatif : `21.866 %`
- bootstrap 95 % : `[7.235 % ; 33.967 %]`
- permutation : `p = 0.00019996`
- verdict : **success under frozen rule**

Le signe du gain est conservé séparément sous ceftazidime (`+23.154 %`) et imipénème (`+20.494 %`). La qualification correcte est **validation externe aveugle sur données publiques préexistantes**, pas nouvelle collecte prospective.

## 3. Matière

`MAG-PAIR-001` est sélectionné pour l'exécution physique de `PRED-MATIERE-ABLATION-001`. Il est le plus directement conforme à la formule gelée, avec trace physique, ablation AF, sham, appariement et interaction histoire×ablation. Aucun jeu public déjà audité ne remplace encore cette exécution.

## 4. Cosmos et paléo

`PRED-COSMOS-NCCC-001` reste fermé en attente d'une cohorte indépendante réellement nouvelle.

`PRED-PALEO-HISTORY-02` reste fermé. PALMOD v2 fournit maintenant une ressource chronologique avec ensembles âge-profondeur, mais le **vrai contrôle négatif physique** manque toujours. La ressource n'est donc pas ouverte comme test.

## Intégration

Ce paquet ne doit pas être fusionné aveuglément sur un snapshot plus ancien. Les fichiers sont conçus comme remplacement/addition ciblés au-dessus de l'état `main` rapporté (`1b968...`). Les manifestes du dépôt complet doivent être régénérés seulement après application sur le vrai checkout `main`.
