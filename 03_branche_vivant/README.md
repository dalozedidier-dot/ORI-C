# Branche 3 — Le vivant

**Régimes 7 et 8.**

7. voies prébiotiques candidates
8. persistance biologique active

## Objet

Appliquer les six dimensions du socle à un régime où la continuité ne dépend
plus d'une liaison ni d'un simple flux, mais de l'entretien, de la réparation,
de la reproduction et d'une histoire héréditaire.

Trois actes :

| Acte | Objet | Rôle |
|---|---|---|
| 1 | cellule eucaryote | description architecturale |
| 2 | endosymbiose mitochondriale | reconstruction historique avec liens typés |
| 3 | résistance aux antibiotiques | passage aux variables et aux tests |

## Statut

| Élément | Statut |
|---|---|
| Acte 1 | Preuve de concept |
| Acte 2 | Preuve de concept ; faits biologiques sous-jacents fortement appuyés |
| Acte 3 | **Analyse exploratoire exécutée**, résultat non confirmatoire ; protocole externe confirmatoire non exécuté |
| Programme prébiotique, régime 7 | **Validateur exécuté sur le schéma**, aucune vraie table de lignées prébiotiques disponible |
| Universalité, supériorité explicative, pouvoir prédictif | **Non établis** |

L'analyse antibiotique actuelle porte sur les données Windels déjà présentes
dans le dépôt. Le léger gain historique n'est pas robuste à l'ablation de la
pente et ne constitue pas un test confirmatoire externe. Le document reste
explicite : il ne démontre ni universalité, ni supériorité explicative, ni
pouvoir prédictif.

Les identifiants comme `TR-039` pour l'endosymbiose mitochondriale sont
internes. La littérature valide les événements biologiques, pas l'identifiant
ni la place que la carte lui attribue.

## Régime 7 — le programme prébiotique

Le régime 7 n'avait aucun protocole. `programme_prebiotique/` le fournit.
Son objet n'est ni l'ARN, ni les membranes, ni les réactions prébiotiques
prises séparément — ce sont des briques — mais leur **couplage** :
compartimentation, copie par matrice, variation héritable et persistance
intégrées en une architecture capable de poursuivre sa propre continuité.

**Il est strictement distinct de l'acte 3.** L'expérience sur les
antibiotiques porte sur une population déjà vivante, qui possède déjà tout
ce que le programme prébiotique cherche à voir apparaître. Les deux ne se
mélangent ni dans les données ni dans les verdicts, et un succès de l'un
n'appuie pas l'autre.

La ligne de partage du programme est exécutable : sans table de lignées
conforme, on observe une production chimique et non une hérédité.
`valider_lignees.py` vérifie la table et évalue les six conditions du
critère minimal.

## Ce qu'hérite la branche

De la branche 2, par les conditions planétaires :

```text
planète différenciée → hydrosphère, atmosphère, minéraux, gradients, cycles → voies prébiotiques accessibles
```

## Boucle retour vers la branche 2

```text
vivant → transformation de l'atmosphère, des sols, des minéraux, des cycles et des sédiments → nouvelle inscription terrestre
```

Le vivant n'est pas seulement l'aboutissement de la branche planétaire. Il
modifie le domaine de possibilités des architectures qui l'entourent.

## Contenu

- `article/` — Le vivant comme terrain ORI-C
- `programme_prebiotique/` — programme dirigé du régime 7, schéma de
  lignées et validateur exécutable

## Nouveaux bancs externes

Deux bancs externes sont ajoutés sans modifier les verdicts antérieurs.

`lignees_vesicules/` télécharge douze classeurs expérimentaux et reconstruit les filiations à partir des cartes donneur-receveur. Le test sépare réponse à la sélection, signal parent-descendant, permutation de la filiation et ablation du mécanisme.

`benchmark_histoire_antibiotique_2026/` évalue la MIC avec séparation groupée par souche. Le modèle historique doit battre le modèle d'état présent et un témoin de même complexité où l'ascendance est permutée.

Sans les jeux externes, les deux bancs retournent `waiting_for_external_data`. Ce statut n'est pas un résultat.
