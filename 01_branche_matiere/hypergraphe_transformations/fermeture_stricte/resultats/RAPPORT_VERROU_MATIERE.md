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

Le scénario `R3/HC02` conserve aussi `H052` intacte et ajoute seulement `N051|N028 -> N030`. Il atteint lui aussi **53/53** mathématiquement. Cette voie est maintenant **qualifiée en extension** : Hao & Li 2018 couvre le bootstrap croûte–H2O/CO2, Ueda et al. 2021 les gradients hydrothermaux et Zhong et al. 2026 la capacité catalytique de carbonates/phyllosilicates compatibles avec l’altération primitive.

## Statut scientifique

Le baseline gelé reste **46/53**. La couche auditable `HC02-E1`, appuyée par trois expériences primaires complémentaires, ferme **53/53 en reachabilité stricte** sans modifier `hyperaretes.csv`. Cette fermeture structurelle ne valide ni une histoire naturelle unique, ni `H033`, ni le §XIV.
