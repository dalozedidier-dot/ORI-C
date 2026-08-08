# Puissance du benchmark antibiotique longitudinal — 7 août 2026

Ce document ne rend aucun verdict scientifique.

> **Correction du 8 août 2026 — ce n'est pas une puissance expérimentale.**
> Les dix plis sont des **partitions de la même donnée** : ils partagent les mêmes
> 148 lignées et les mêmes 358 mesures, et sont donc corrélés entre eux. Une
> taille d'effet calculée sur leurs différences appariées mesure la **stabilité de
> l'écart entre modèles d'un pli à l'autre**, c'est-à-dire la séparabilité du
> dispositif d'évaluation. Elle ne mesure pas la capacité d'un plan expérimental à
> détecter un effet biologique sur des lignées, ce qui demanderait une taille
> d'effet estimée entre unités indépendantes. Les nombres ci-dessous — 0,109,
> 0,212, 129 plis, 50 plis — sont des diagnostics internes à la validation
> croisée. Le titre et le vocabulaire d'origine sont conservés pour la traçabilité,
> mais toute lecture en termes de dimensionnement d'expérience est fautive.

Reproduction :

```bash
python plan_directeur/campagne_maximale_trois_branches/analyser_puissance_vivant.py
```

Résultat machine : `plan_directeur/campagne_maximale_trois_branches/resultats/POWER_VIVANT_LONGITUDINAL.json`

---

## Le dispositif actuel

10 plis appariés, 358 mesures, 148 lignées, soit 14,8 lignées par pli.

| comparaison | gain moyen apparié | dz | plis favorables | p apparié | **séparabilité entre plis** |
|---|---:|---:|---:|---:|---:|
| histoire contre `state_only` | 0,00741 MAE | 0,249 | 7/10 | 0,452 | **0,109** |
| histoire contre `equal_complexity` | 0,00958 MAE | 0,408 | 7/10 | 0,229 | **0,212** |

## Ce que ces deux nombres impliquent

La valeur 0,109 dit que l'écart entre le modèle historique et `state_only` n'est
**pas stable d'un pli à l'autre** au regard de sa propre dispersion. Contre le
témoin de complexité appariée, il l'est un peu plus, sans l'être assez.

**Le résultat non concluant du benchmark n'est donc pas une preuve d'absence
d'effet.** Mais il ne permet pas non plus d'affirmer que « le dispositif n'a pas
la puissance de détecter l'effet » : cette phrase suppose une puissance
expérimentale que ces données ne fournissent pas. Ce qui est établi est plus
étroit et plus sûr — l'écart mesuré n'est pas séparable du bruit de partition.
La distinction interdit aussi bien d'annoncer un effet historique que de le
déclarer réfuté par ce benchmark.

## Un défaut de la règle de décision

Le protocole conclut par un test de signe exact sur dix plis. Les valeurs
bilatérales exactes sont :

| plis favorables | p bilatéral |
|---:|---:|
| 7/10 | 0,344 |
| 8/10 | 0,109 |
| **9/10** | **0,021** |
| 10/10 | 0,002 |

Avec dix plis, **aucun résultat inférieur à 9 sur 10 ne peut atteindre
p ≤ 0,05**, quelle que soit l'ampleur réelle de l'effet. La règle de décision
est donc quasi inatteignable à cette taille. Ce n'est pas un problème de
données, c'est un problème de conception du test.

## Ce qu'il faudrait pour conclure

À taille de pli constante, en supposant l'effet réellement de l'ampleur mesurée :

| objectif | contre `equal_complexity` | contre `state_only` |
|---|---|---|
| puissance 80 % | 50 plis, ~740 lignées, **×5** | 129 plis, ~1 909 lignées, **×12,9** |
| puissance 90 % | 66 plis, ~977 lignées, **×6,6** | 172 plis, ~2 546 lignées, **×17,2** |

Le jeu actuel compte 148 lignées. Il faudrait donc entre cinq et dix-sept fois
plus de lignées indépendantes.

Ces nombres supposent que l'effet vaut ce que l'échantillon actuel suggère. Comme
cette estimation vient d'un échantillon sous-dimensionné, elle est elle-même
imprécise et probablement optimiste : un effet estimé sur peu de données et non
significatif est en moyenne surestimé.

## Conséquence pour le programme

Trois options, et une seule est honnête à court terme.

1. **Acquérir cinq à dix-sept fois plus de lignées.** Hors de portée sans un
   partenariat expérimental dédié.
2. **Redéfinir la règle de décision** avant toute nouvelle exécution, avec un
   nombre de plis compatible avec le seuil visé, et un SESOI justifié avant
   acquisition plutôt que lu sur les données.
3. **Déclarer le protocole non concluant par construction** et cesser de le
   citer, dans un sens ou dans l'autre, tant que l'un des deux points précédents
   n'est pas réglé.

L'option 3 est celle que l'état actuel des données impose. Les options 1 et 2
sont des travaux à préenregistrer, pas des résultats.

## Portée

Ce document concerne le **benchmark longitudinal** de
`plan_directeur/campagne_maximale_trois_branches`. Il ne porte ni sur le
résultat D'Onofrio, qui possède son propre pipeline, ses propres témoins et sa
propre valeur de p, ni sur les lignées de vésicules. Ces deux résultats restent
évalués séparément, comme le prévoit `AUTORITE_DES_DOCUMENTS.md`.
