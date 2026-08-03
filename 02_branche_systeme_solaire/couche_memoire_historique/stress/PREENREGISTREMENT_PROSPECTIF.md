# Préenregistrement — test prospectif à témoin de complexité égale

**Écrit et scellé avant tout calcul.** Son empreinte SHA-256 est consignée dans
`results_stress/prospectif/preenregistrement.sha256` au moment de l'exécution.
Aucun seuil, aucune hypothèse et aucun critère de ce document ne peut être
modifié après lecture des résultats.

## 1. Question

Le dossier conclut que la seule couche soumise à un test avec témoin apparié a
échoué, et pose la question ouverte suivante :

> ORI-C produit-il, quelque part, une prédiction qu'un modèle classique de
> complexité égale ne produit pas ?

Ce test l'exécute dans l'EMIC exoplanétaire réduit, sur un régime de forçage
final où le modèle possède **plusieurs attracteurs**. C'est le seul endroit du
programme où une dépendance au chemin permanente est structurellement possible.

## 2. Ce que le balayage précédent a déjà établi

Il faut l'écrire ici pour que la nouveauté du présent test soit lisible.

- Sous le forçage final livré (obliquité 23,5°, excentricité 0,05), l'EMIC
  possède un **attracteur unique**. Mille sondes très dispersées convergent à
  3 × 10⁻¹⁴ K près après 800 Ma.
- L'écart entre les deux histoires y décroît exponentiellement, e-folding
  7,0 Ma, et s'annule sur palier long. C'est un retard de relaxation.
- Le balayage de 54 couples (obliquité, excentricité) a trouvé **4 points à
  attracteurs multiples**, avec une dispersion finale de 2,4 à 2,7 K en
  température et de 0,87 à 0,92 en fraction de glace :

  | Obliquité finale | Excentricité finale | Glace de l'attracteur moyen |
  |---:|---:|---:|
  | 12° | 0,30 | 0,193 |
  | 23,5° | 0,18 | 0,344 |
  | **30°** | **0,10** | **0,422** |
  | 40° | 0,00 | 0,272 |

- Aux quatre points, les trajectoires A et B du protocole livré retombent dans
  le **même bassin** : 0 point sur 54 conserve un écart matériel à 200 Ma.

Le présent test change donc deux choses, et seulement deux : le forçage final
est placé au point bistable, et les histoires sont dessinées pour encadrer la
frontière de bassin.

## 3. Le témoin de complexité égale : M2P

`M2P` reprend `M2` avec **exactement le même nombre d'états dynamiques et de
paramètres**, et la même paire de constantes de temps lentes.

Une seule chose diffère : ce qui alimente les états lents.

| | État lent 1, régolithe | État lent 2, mémoire |
|---|---|---|
| **M2** | érodé par la **fraction de glace**, réponse du système | relaxe vers la **productivité**, réponse du système |
| **M2P** | érodé par le **forçage polaire**, entrée externe | relaxe vers une fonction du **forçage annuel**, entrée externe |

M2 inscrit la réponse passée du système. M2P filtre l'entrée. C'est la
transposition exacte de la logique M1P, qui a fait échouer la couche mémoire.

Le terme d'entrée de M2P est normalisé pour occuper la même plage que la
productivité de M2, afin qu'aucune différence d'échelle ne se substitue à la
différence de nature.

## 4. Hypothèses préenregistrées

**H1 — la bistabilité seule suffit-elle ?**
Sous un forçage final bistable, deux histoires encadrant la frontière de bassin
produisent un écart permanent **dans tous les modes, y compris `classic`**, qui
n'a aucun état lent.

Si H1 est vraie, la dépendance au chemin permanente est une propriété de la
bistabilité et non de la mémoire.

**H2 — la mémoire ajoute-t-elle quelque chose ?**
Il existe un forçage final pour lequel `M2` conserve un écart matériel après un
palier long **alors que `M2P` n'en conserve pas**.

H2 est la revendication propre à ORI-C. C'est elle qui est testée.

**H3 — asymétrie de bassin.**
La mémoire de M2 déplace la frontière de bassin par rapport à M2P : la valeur
critique du paramètre d'histoire qui fait basculer A et B d'un bassin à l'autre
diffère entre les deux modèles de plus de 5 % en valeur relative.

## 5. Protocole

1. Forçage final placé au point bistable **(30°, e = 0,10)**, le plus séparé
   des quatre, ainsi qu'aux trois autres à titre de réplication.
2. Les deux histoires A et B partent d'états initiaux choisis de part et
   d'autre de la frontière de bassin, déterminée au préalable par bissection
   sur la fraction de glace initiale, **avec le mode `classic`** afin que la
   frontière ne soit pas définie par le modèle testé.
3. Palier final de 10 Ma puis de 300 Ma. Le verdict porte sur 300 Ma.
4. Ensemble apparié de 60 réplicats. Les quatre modes — `classic`, `ablated`,
   `M2`, `M2P` — reçoivent les mêmes forçages et les mêmes conditions
   initiales.
5. Pas d'intégration 0,02 Ma, contrôlé à 0,005 Ma sur le point principal.

## 6. Critères, fixés avant lecture

| Critère | Seuil |
|---|---|
| Matérialité de l'écart | 0,1 K ; 0,01 de fraction de glace ; 1 ppm de CO₂ ; 0,01 de productivité |
| Persistance | l'écart à 300 Ma reste au-dessus du seuil de matérialité |
| **H1 réussie** | `classic` conserve un écart matériel et persistant sur ≥ 2 variables |
| **H2 réussie** | `M2` conserve un écart matériel et persistant sur ≥ 2 variables **et** `M2P` sur 0 variable, à au moins un point de forçage final |
| **H3 réussie** | frontières de bassin de M2 et M2P séparées de > 5 % en relatif |
| Convergence numérique | écart relatif < 5 % entre pas 0,02 et 0,005 Ma |

## 7. Ce que le test ne peut pas établir

Il porte sur un EMIC réduit, non calibré sur ROCKE-3D, WACCM6 ou GEOCLIM, et
sur des trajectoires orbitales prescrites plutôt que produites par une
intégration N-corps-spin. Une réussite de H2 serait un **résultat de niveau 1,
théorème dans le modèle**. Elle n'établirait ni la validité biologique, ni la
pertinence climatique quantitative, ni la supériorité d'ORI-C sur une archive
réelle.

Un échec de H2, en revanche, fermerait cette implémentation-ci de la mémoire
dans le seul régime où elle avait une chance structurelle de se manifester.

## 8. Engagement

Les résultats sont rapportés quels qu'ils soient. Aucun critère n'est ajouté,
retiré ou déplacé après lecture. Si un critère se révèle mal posé, le défaut est
documenté et l'échec conservé, comme pour `E01` dans l'analyse exhaustive.
