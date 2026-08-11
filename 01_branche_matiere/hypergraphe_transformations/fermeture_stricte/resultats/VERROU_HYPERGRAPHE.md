# Verrou de fermeture stricte de la branche matière

## Résultat canonique

La fermeture stricte atteint **46 nœuds sur 53**. Les sept nœuds inaccessibles sont `N029`, `N030`, `N031`, `N032`, `N035`, `N053`, `N054`.

Le noyau de dépendance circulaire est `N029`, `N030`, `N053` et `N054`. `N031`, `N032` et `N035` sont bloqués en aval. Le verrou n'est donc pas dispersé dans tout l'hypergraphe.

## Diagnostic minimal

Le cycle vient de la combinaison suivante : l'inventaire accessible exige déjà des espèces solubles, la circulation entre réservoirs exige l'inventaire accessible, le système hydrothermal exige déjà l'interface eau-roche, et les espèces solubles exigent le système hydrothermal.

L'énumération des apports externes montre qu'un seul nœud injecté dans le noyau suffit à fermer mathématiquement tout le graphe. Cette observation localise le verrou, mais ne justifie aucun apport dans la nature.

## Réparation structurelle candidate

Le scénario `R1` recode `H052` de `N051|N028|N030 -> N053` vers `N051|N028 -> N053|N030`. La circulation hydrothermale produit alors l'interface eau-roche qu'elle entretient au lieu de la présupposer.

Avec ce seul changement, la fermeture atteint **53 nœuds sur 53**. Le scénario `R2` conserve le graphe canonique et ajoute la même proposition sous la forme d'une hyperarête candidate séparée `HC01`.

## Statut scientifique

Le verrou courant est expliqué comme une circularité de représentation localisée. Une réparation minimale existe et ferme le graphe, mais elle reste une hypothèse de codage à valider contre les sources primaires. Le fichier canonique `hyperaretes.csv` n'est pas modifié.
