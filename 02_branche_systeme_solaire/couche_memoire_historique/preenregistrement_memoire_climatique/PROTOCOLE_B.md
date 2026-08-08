# WP-CLIM-MEM-2026-B — inscription durable, témoin IAAFT

**Gelé le 8 août 2026, avant toute exécution.** Successeur de `WP-CLIM-MEM-2026`,
clos sur `invalide` parce que son témoin permuté détruisait le spectre en même
temps que la correspondance temporelle.

## Ce qui change, et pourquoi

Le compartiment de mémoire a une autocorrélation de **+0,450 à 10 ka**. Une
permutation naïve la ramène à **+0,013** : le témoin devient du bruit blanc, et
le modèle historique gagne trivialement parce qu'une série lisse se prédit par
son propre passé. Le gain de 34,5 % mesuré ainsi ne portait aucune information.

Le témoin devient donc un **surrogat IAAFT** de la série du compartiment,
construit avant tout ajustement. Mesuré sur cette série, IAAFT préserve
l'histogramme exactement, le spectre de puissance à **1,7 % près** en écart
relatif moyen, et une autocorrélation de **+0,460** à 10 ka. Il ne détruit que la
correspondance temporelle avec le forçage et la structure de phase.

Un gain qui ne dépasse pas ce témoin n'est pas distinguable de ce que produit une
série linéaire de même spectre et de même distribution.

## Hypothèse

Connaître la trajectoire passée du compartiment améliore la prédiction de son
état présent au-delà du forçage courant, **et au-delà de ce que permet une série
de même spectre et de même distribution dont la correspondance temporelle avec le
forçage a été détruite**.

**Nulle.** Le gain observé ne dépasse pas le 95ᵉ percentile de la distribution
obtenue sur les surrogats IAAFT.

## Variables obligatoires

Identiques à `WP-CLIM-MEM-2026`, table `memoire_climatique_bintanja_insolation.csv`,
1 070 lignes complètes. `sea_level_m` reste exclu, corrélé à +1,000 avec la cible.

| rôle | colonne |
|---|---|
| forçage indépendant | `insolation_65N_jul_Wm2`, `obliquity_deg`, `precession`, `eccentricity` |
| compartiment, cible | `ice_volume_total_sle` |

## Modèles

| modèle | prédicteurs |
|---|---|
| `etat_seul` | les quatre forçages à l'instant t |
| `etat_plus_histoire` | les quatre forçages, plus le compartiment aux décalages −10, −20, −40 ka |
| `temoin_iaaft` | les quatre forçages, plus les **mêmes décalages calculés sur un surrogat IAAFT** du compartiment |

Le témoin a le même nombre de paramètres, la même famille de modèle, le même
spectre et la même distribution. Seule la correspondance temporelle diffère.

## Validation croisée et embargo

Dix blocs contigus. **Embargo de 40 ka de chaque côté de chaque bloc de test**,
soit le décalage maximal employé : aucune valeur du compartiment utilisée comme
prédicteur en test ne peut provenir d'une région d'apprentissage adjacente. Cette
clause corrige la non-conformité relevée sur le protocole précédent.

## Paramètres du témoin, fixés avant exécution

| paramètre | valeur |
|---|---|
| surrogats IAAFT | **500** |
| itérations IAAFT | 200, tolérance 1e-8 |
| graine | **20260808** |
| percentile de décision | **95** |

La statistique de test est la RMSE agrégée du modèle historique. La valeur de p
est la fraction des surrogats dont la RMSE est inférieure ou égale à celle
observée. Plus petite valeur atteignable : 1/501, soit 2,0 × 10⁻³, en deçà
d'alpha. Aucun test de signe discret n'est employé.

## Règle de décision

| issue | condition |
|---|---|
| **soutient** | RMSE(`etat_plus_histoire`) < RMSE(`etat_seul`) **ET** RMSE(`etat_plus_histoire`) inférieure au 5ᵉ percentile de la distribution des surrogats, soit p ≤ 0,05 |
| **ne soutient pas** | l'une des deux conditions n'est pas remplie |
| **indéterminé** | moins de 8 blocs exploitables après embargo |

Aucun paramètre ne peut être modifié après lecture du moindre résultat.

## Statut épistémique

Inchangé : Bintanja est une modélisation inverse de LR04, Berger une solution
astronomique calculée. **Quel que soit le verdict, ce n'est pas une preuve
empirique primaire.** C'est un verdict sur une reconstruction largement acceptée,
avec un témoin de force adéquate.
