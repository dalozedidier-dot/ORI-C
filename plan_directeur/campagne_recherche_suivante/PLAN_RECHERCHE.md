# Plan de recherche opérationnel

## Matière

### H011, instabilité de streaming

Le test transforme H011 en relation à seuil. À taille de particules fixée, l'abondance critique de solides doit augmenter lorsque la turbulence augmente. Le contraste local utilise les trois points publiés à `tau_s = 0.01`. La valeur minimale publiée pour les tailles optimales reste une borne de contexte et ne participe pas à la régression.

Le résultat soutient un mécanisme dans des simulations contrôlées. Il ne compte pas comme intervention naturelle.

### Cycle des interfaces

Les relations `H030`, `H031`, `H052` et `H053` sont auditées séparément. Une fermeture empirique exige les quatre relations quantitatives dans un même système suivi au cours du temps. Des sources différentes pour chaque segment ne suffisent pas.

## Système solaire

### Mesure interventionnelle de Pacc

Les six interventions déjà calculées sur Jupiter et Saturne sont comparées à une enveloppe conservatrice construite avec trois variantes de référence : pas de temps raffiné, conditions initiales sous forme d'éléments et ensemble étendu de corps. Deux mesures sont conservées :

- `Pacc_interventions`, fraction d'interventions qui dépassent l'enveloppe sur au moins deux métriques.
- `Pacc_dimensions`, fraction des couples intervention-métrique qui dépassent l'enveloppe.

### WP-C2b

Le protocole réparé sélectionne seulement les points non saturés du scan historique. Les classes de régime, les huit graines de validation, la métrique principale et les règles d'échec sont écrites avant toute nouvelle exécution.

### Chronologie climatique indépendante

La compilation NOAA 0-22 ka est acquise et auditée. Elle sert à vérifier l'existence d'âges radiométriques, de valeurs isotopiques et de sites indépendants. Elle ne remplace pas une archive longue couvrant plusieurs cycles de 100 ka.

## Vivant

### Lignées de vésicules

Les cartes donneur-receveur servent à reconstruire les couples parent-descendant. Les analyses séparent :

1. réponse moyenne à la sélection,
2. corrélation parent-descendant,
3. signal de lignée contre permutation intra-génération,
4. contraste entre le régime complet et les ablations d'alimentation ou de resuspension.

Un gain de moyenne sans signal de filiation ne compte pas comme inscription.

### Histoire antibiotique

Le modèle d'état utilise l'antibiotique et la limitation élémentaire présente. Le modèle historique ajoute l'ascendance LTEE. L'évaluation exclut chaque souche du jeu d'apprentissage lorsqu'elle est prédite. Le modèle historique doit battre à la fois le modèle d'état et un modèle de même complexité dont l'ascendance est permutée.

## Règle de décision

Les données manquantes produisent `waiting_for_external_data`. Les erreurs techniques produisent `execution_error`. Aucun de ces statuts ne peut être transformé en résultat scientifique positif.
