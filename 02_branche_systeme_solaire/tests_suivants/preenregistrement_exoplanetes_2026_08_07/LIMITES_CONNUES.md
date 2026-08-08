# Limites connues du protocole gelé WP-EXO-2026

Ce protocole est **gelé** : son code et sa référence sont scellés par empreinte
dans `PROTOCOLE.json`, et rien n'y sera modifié avant la vérification du
7 août 2028. Les limites ci-dessous sont donc **déclarées, non corrigées**. Les
corriger reviendrait à casser le gel, c'est-à-dire à détruire la seule chose qui
fasse la valeur d'un préenregistrement.

## Déduplication dépendante de l'ordre du fichier

`verifier_bande_accessible.py`, lignes 66 et 67 :

```python
reference = pd.read_csv(REFERENCE, ...).drop_duplicates("pl_name")
candidat  = pd.read_csv(arguments.candidat, ...).drop_duplicates("pl_name")
```

La table NASA *Planetary Systems* contient **plusieurs lignes par planète**, une
par publication de référence. `drop_duplicates` conserve la première rencontrée,
donc celle que l'ordre du CSV présente en tête. Cet ordre n'est garanti par
aucune spécification de l'archive.

**Conséquence.** Si l'ordre des lignes change entre l'instantané gelé de 2026 et
l'instantané de vérification de 2028, la valeur retenue pour une planète donnée
peut changer sans que la planète ait été redécouverte ni ses paramètres révisés.
Le test porte sur l'appartenance à une bande de rayons ; une planète proche d'une
borne peut donc basculer pour une raison purement documentaire.

**Ce qu'il aurait fallu faire.** Filtrer sur `default_flag == 1`, la colonne par
laquelle la NASA désigne elle-même le jeu de paramètres de référence d'une
planète. Ce filtre est stable, explicite et indépendant de l'ordre du fichier.

**Ampleur.** Non mesurée à ce jour. Elle se mesure en comparant, sur
l'instantané gelé, la sélection obtenue par `drop_duplicates` à celle obtenue par
`default_flag == 1`, et en comptant les planètes dont l'appartenance à la bande
diffère. Cette mesure ne modifie pas le protocole : elle en borne la fragilité.

## Ce qui reste valide

La bande `[1,5130 ; 19,1765]`, le nul de 0,5808, l'effet de 0,7997 et le
dimensionnement à n = 28 pour 80 % de puissance ont été fixés avant toute
observation et ne dépendent pas de ce défaut. Le test à blanc sur candidat
synthétique a retrouvé exactement les 60 événements injectés, dont 40 dans la
bande. Le défaut porte sur la **stabilité de la sélection entre deux
instantanés**, pas sur la logique du test.

## Successeur

Tout protocole successeur doit employer `default_flag == 1` et le déclarer dans
son gel. Aucune correction rétroactive de `WP-EXO-2026`.
