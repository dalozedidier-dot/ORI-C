# Petrungaro NIT — approfondissement du fond génétique et des chemins mutationnels

## Résultat principal

Sur 803 populations réelles réparties entre 258 fonds, l'issue NIT est
fortement reproductible entre répétitions d'un même fond : ICC = **0,7156**,
IC95 % bootstrap par fond **[0,6380 ; 0,7783]**. L'effet moyen résiduel après
contrôle de la résistance initiale s'étend de **−1,0213 à +0,7000 log10 IC50**.

Les effets positifs les plus élevés sont notamment `uvrD`, `mutT`, `recR`,
`uvrA` et `mutL`. Les effets négatifs les plus élevés en valeur absolue sont
notamment `yobH`, `tolC`, `lon`, `gntY` et `erfK`. La table complète conserve
les effectifs et la dispersion entre répétitions pour chaque fond.

## Chaîne m → mutations → R

La sous-cohorte séquencée contient 102 populations et 36 fonds. Les modèles
croisés donnent les RMSE suivantes en log10 IC50 :

| Modèle | RMSE |
|---|---:|
| `X` | 0,4252 |
| `X + m` | 0,3584 |
| `X + mutations` | 0,4184 |
| `X + m + mutations` | 0,4006 |

Les 31 gènes présents dans au moins deux populations sont seuls utilisés pour
la prédiction hors échantillon. L'ajout des mutations à `X` apporte seulement
**1,60 %**, avec un IC95 % bootstrap par fond **[−21,75 % ; +18,81 %]**. La
permutation stratifiée donne `p = 0,005`, mais ce résultat isolé ne suffit pas :
le bootstrap traverse largement zéro. Le verdict incrémental mutationnel est
donc **ne soutient pas**.

Après ajout des mutations, l'avantage RMSE de `m` diminue de **73,35 %**. Cette
atténuation est compatible avec un chemin partiellement partagé, mais ne
démontre pas une médiation : les mutations sont mesurées après l'exposition et
leur apport prédictif propre n'est pas robuste. La chaîne complète reste donc
**indéterminée**.

Parmi les familles COG représentées par au moins deux fonds, `E`, `D` et `L`
ont un effet moyen positif après `X`, tandis que `O`, `M`, `K` et `Φ` ont un
effet moyen négatif. Ces comparaisons sont exploratoires et limitées aux 36
fonds séquencés ; elles ne doivent pas être généralisées aux 258 fonds.

## Prédiction indépendante

`PRED-PETRUNGARO-NIT-001` fige une réplication quantitative sur un futur jeu
réel indépendant : gain RMSE attendu 31,762 %, plage prédite 20–45 %, seuil
minimal 20 %, bootstrap par fond excluant zéro, permutation `p ≤ 0,05`, ICC
`≥ 0,60` et signe positif dans chaque lot préspécifié.

Cette prédiction est **gelée localement, non publique et non testée**. Aucun
jeu externe ne peut être ouvert avant son enregistrement public. Aucun résultat
rétrospectif actuel n'est rebaptisé prédiction indépendante.
