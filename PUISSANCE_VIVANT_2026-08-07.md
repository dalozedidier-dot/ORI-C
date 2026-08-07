# Puissance du benchmark antibiotique longitudinal — 7 août 2026

Ce document ne rend aucun verdict scientifique. Il caractérise la **capacité de
détection** du benchmark longitudinal de la branche vivant, à partir de ses dix
plis appariés déjà publiés.

Reproduction :

```bash
python plan_directeur/campagne_maximale_trois_branches/analyser_puissance_vivant.py
```

Résultat machine : `plan_directeur/campagne_maximale_trois_branches/resultats/POWER_VIVANT_LONGITUDINAL.json`

---

## Le dispositif actuel

10 plis appariés, 358 mesures, 148 lignées, soit 14,8 lignées par pli.

| comparaison | gain moyen apparié | dz | plis favorables | p apparié | **puissance atteinte** |
|---|---:|---:|---:|---:|---:|
| histoire contre `state_only` | 0,00741 MAE | 0,249 | 7/10 | 0,452 | **0,109** |
| histoire contre `equal_complexity` | 0,00958 MAE | 0,408 | 7/10 | 0,229 | **0,212** |

## Ce que ces deux nombres impliquent

Une puissance de 0,109 signifie que si l'effet mesuré était réel et de cette
ampleur, le protocole aurait **environ une chance sur neuf** de le détecter.
Contre le témoin de complexité appariée, une chance sur cinq.

**Le résultat non concluant du benchmark n'est donc pas une preuve d'absence
d'effet.** C'est le constat qu'un dispositif de cette taille ne tranche pas. La
distinction est décisive : elle interdit aussi bien d'annoncer un effet
historique que de le déclarer réfuté par ce benchmark.

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
