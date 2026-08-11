# Méthodologie de recherche — généalogie cosmique quantitative

## Objet

Cette branche ne cherche pas à raconter une chronologie générale. Elle teste une proposition plus étroite : **des produits de l'histoire physique peuvent rester incorporés dans la composition, les isotopes, les grains, les réservoirs, les gradients ou l'architecture, puis modifier les transformations accessibles au stade suivant**.

Le parcours couvert est le raccordement entre la nucléosynthèse stellaire déjà versionnée dans ORI-C et l'architecture du Système solaire utilisée comme entrée de la couche C-AST.

## Recherche bibliographique

La revue privilégie les articles primaires, les jeux de données et les échantillons retournés. Une revue de synthèse peut être conservée pour cartographier un débat, mais elle est explicitement marquée `revue` et ne compte pas comme observation indépendante. Les DOI et la nature de la preuve sont enregistrés dans `SOURCES_PRIMAIRES.csv`.

Les sources sont séparées en cinq familles de preuve :

1. échantillons directs et analyses isotopiques ;
2. observations astronomiques d'analogues actuels ;
3. reconstructions historiques par chronomètres/isotopes ;
4. thermodynamique et mécanismes physicochimiques ;
5. simulations dynamiques ou hydrodynamiques.

Les sorties de modèles ne sont jamais renommées « observations ». Les analogues extrasolaires ne sont jamais présentés comme des mesures du disque solaire disparu.

## Règle de raccordement ORI-C

Pour chaque stade `GC-xxx`, la table exige :

- un état antérieur ;
- un processus ;
- des contraintes ;
- une inscription historique ;
- un nouvel ensemble d'états accessibles ;
- ce qui reste non démontré ;
- une observable ;
- des sources ;
- un mode de preuve ;
- un statut.

Une relation `GC-i → GC-j` signifie seulement que le premier fournit une condition, un constituant, une contrainte ou une architecture pertinente pour le second. Elle ne signifie ni nécessité universelle ni suffisance.

## Contrôles contre la confirmation facile

La branche contient des modèles concurrents et des contre-exemples structurels. L'hypothèse « Jupiter est l'unique cause de la dichotomie NC/CC » n'est pas admise comme fait : un disque structuré fournit un mécanisme concurrent. Le Grand Tack, le modèle Nice, les anneaux de planétésimaux et l'accrétion de galets restent des familles de modèles. Le résultat de 2026 sur l'infall tardif est enregistré en séparant les mesures isotopiques de l'inférence de masse du modèle.

Le succès aval `C-AST-01` ne ferme pas l'amont. Il démontre l'efficacité causale de l'architecture actuelle **dans le modèle orbital réduit**, pas la trajectoire qui l'a produite.

## Réfutabilité

Les claims locales peuvent être contredites par de nouvelles mesures, un recalcul ou une comparaison de modèle. La claim end-to-end reste `open_not_certified` tant qu'aucun pipeline de formation ne produit une distribution d'architectures compatible avec les observables du Système solaire et un handoff quantifié vers les variables utilisées par C-AST.
