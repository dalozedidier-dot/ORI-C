# Test prospectif à témoin de complexité égale — rapport

Protocole préenregistré : `stress/PREENREGISTREMENT_PROSPECTIF.md`,
empreinte `bf907b458410a898316b75e7ad756d0ee5539ae1cef88b073542786dcb4e19e4`,
scellée avant tout calcul.

**Verdict : le test n'a pas pu être exécuté tel que préenregistré. Deux
défauts de conception, tous deux dans mon protocole et non dans le modèle,
sont documentés ici conformément au §8 du préenregistrement.**

Aucune hypothèse n'est déclarée réussie.

## 1. Ce qui est solidement établi au passage

Le contrôle préalable des attracteurs, mode par mode, sur 150 états initiaux
très dispersés intégrés 400 Ma, donne un résultat net et inattendu.

| Forçage final | `classic` | `ablated` | `M2` | `M2P` |
|---|---:|---:|---:|---:|
| 30°, e = 0,10 | **0,0000** | 0,0000 | **0,9243** | 0,0000 |
| 23,5°, e = 0,18 | **0,0000** | 0,0000 | **0,9226** | 0,0000 |
| 12°, e = 0,30 | **0,0000** | 0,0000 | **0,8953** | 0,8591 |
| 40°, e = 0,00 | **0,0000** | 0,0000 | **0,8690** | 0,0000 |

Étendue de la fraction de glace finale. Zéro signifie attracteur unique.

**`classic` et `ablated` sont monostables aux quatre points.** La bistabilité
relevée par le balayage précédent n'est donc pas une propriété du noyau
climatique : elle est **produite par les états lents**. Sans eux, le modèle n'a
qu'un seul état final, et aucune dépendance au chemin permanente n'y est
possible.

C'est un résultat propre, indépendant des deux défauts qui suivent, et il
corrige une lecture implicite du balayage précédent, qui sondait les
attracteurs en mode M2 seulement.

## 2. Premier défaut : la frontière de bassin est indéterminable comme prévu

Le §5 du préenregistrement impose de déterminer la frontière de bassin **avec
le mode `classic`**, pour qu'elle ne soit pas définie par le modèle testé.

C'était la bonne intention et c'est inapplicable : `classic` n'a pas de
frontière de bassin, puisqu'il n'a qu'un attracteur. La bissection ne converge
sur rien aux quatre points.

Le protocole est donc contradictoire dans ses propres termes. Toute frontière
utilisable devrait être définie par M2 ou M2P, c'est-à-dire par le modèle
testé — précisément ce que la clause voulait éviter.

Ce défaut n'était pas visible à la rédaction : il supposait connu le fait,
établi seulement au §1 ci-dessus, que la bistabilité vient des états lents.

## 3. Second défaut : le témoin n'est pas apparié sur le canal régolithe

Le §3 du préenregistrement exige que l'entrée externe de M2P soit normalisée
pour occuper la même plage que la variable de réponse qu'elle remplace, afin
qu'aucune différence d'échelle ne se substitue à la différence de nature.

J'ai normalisé une seule entrée, contre la **productivité**, et je l'ai
employée pour les deux états lents. Or les deux états lents de M2 sont
alimentés par des variables différentes.

| | Variable motrice dans M2 | Substitut dans M2P | Valeur d'exploitation |
|---|---|---|---|
| Mémoire | productivité ≈ 0,91 | entrée ≈ 0,89 | **apparié** |
| Régolithe | fraction de glace ≈ 0,02 | entrée ≈ 0,89 | **facteur ≈ 40** |

Conséquence directe : dans M2 le terme d'érosion `−érosion × glace × régolithe`
est presque éteint dans l'attracteur libre de glace, et le régolithe remonte à
0,87. Dans M2P il est toujours actif, et le régolithe s'effondre à 0,15. Le
socle rocheux passe de 0,13 à 0,85, ce qui déplace le seuil de glace de
`1,5 × 0,72 ≈ 1,1`, une valeur considérable.

**M2P se retrouve donc verrouillé en régime englacé pour une raison d'échelle,
non de structure.** Conclure de sa monostabilité que la mémoire ORI-C ajoute
quelque chose serait exactement l'artefact que le préenregistrement interdisait.

## 4. Pourquoi je ne corrige pas le témoin dans ce rapport

Une normalisation correcte suppose de fixer l'échelle de chaque entrée sur la
valeur que prend sa variable motrice **à un état de référence indépendant du
point testé** — par exemple le forçage de référence (23,5°, e = 0,05). Cette
correction est faisable, mais elle change le témoin après lecture d'un
résultat, ce que le §8 interdit.

Le test doit donc être **repréenregistré et réexécuté** avec :

1. une définition de la frontière de bassin qui ne dépende pas de `classic`,
   et qui soit déclarée comme telle plutôt que présentée comme neutre ;
2. deux entrées externes distinctes dans M2P, une par état lent, chacune
   calibrée sur la valeur de sa variable motrice au forçage de référence ;
3. un contrôle explicite, à publier avec le résultat, des valeurs
   d'exploitation des quatre variables motrices, pour que l'appariement soit
   vérifiable et non affirmé.

## 5. Statut

| Hypothèse | Verdict |
|---|---|
| H1, la bistabilité seule suffit | **Réfutée** : `classic` est monostable aux quatre points, il n'y a pas de bistabilité sans états lents |
| H2, la mémoire ajoute quelque chose | **Non concluant** : le témoin n'est pas apparié sur le canal régolithe |
| H3, asymétrie de bassin | **Non évaluée** : dépend d'une frontière indéterminable au sens du protocole |

Le seul acquis est celui du §1, et il ne concerne aucune des trois hypothèses :
dans cet EMIC réduit, la multistabilité est une propriété des états lents et
non du noyau climatique.

## 6. Ce que cela ne change pas

Le résultat négatif de la couche mémoire historique sur LR04 reste inchangé, et
ce test ne le concerne pas. La couche astronomique n'est pas concernée non
plus. Les branches 1 et 3 non plus.

Ce rapport ne fournit **aucun appui** à la revendication propre d'ORI-C. Il ne
la réfute pas davantage dans ce régime : il constate que l'instrument que
j'avais construit pour la tester n'était pas apte à le faire.
