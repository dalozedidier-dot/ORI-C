# Pacc interventionnel apparié — définition PACC-INT-CHALLENGE-V1

Statut : **définition prospective stricte**. Elle ne requalifie aucun résultat
antérieur et ne remplace pas les proxys rétrospectifs déjà publiés.

## Question mesurée

Pour un état d'ancrage `X`, un ensemble de défis futurs `Theta_c` et une trace
ciblée `m`, la quantité locale est :

`Pacc = somme_c,d w_c,d * 1(|R_c,d - X_d| >= epsilon_d)`

avec `somme w_c,d = 1`.

Le dénominateur est donc l'ensemble **pré-déclaré** des cellules
`défi × dimension de réponse`, pas le nombre de classes observées au moins une
fois. Cette construction évite qu'une longue série rende mécaniquement
`Pacc = 1` simplement parce que toutes les classes ont fini par apparaître.

## Qualification causale stricte

Un contraste `Delta Pacc = Pacc_do(m) - Pacc_control` ne reçoit le label
interventionnel causal que si toutes les conditions suivantes sont documentées
avant l'ouverture du test :

1. unités réellement indépendantes ;
2. `X` apparié entre contrôle et intervention ;
3. mêmes contraintes/défis futurs `Theta` ;
4. même architecture non ciblée `A` ;
5. seule la trace annoncée `m` est ciblée ;
6. ensemble de défis gelé ;
7. seuils de matérialité `epsilon_d` gelés ;
8. réponse `R` mesurée après l'intervention ;
9. sham apparié disponible et sous la tolérance annoncée.

Si une condition manque, la quantité peut être calculée à titre descriptif mais
**ne compte pas comme Pacc causal** dans le seuil scientifique du §XIV.

## Règle de décision

L'unité de réplication statistique est le système/échantillon indépendant, pas
la cellule `défi × dimension`. L'intervalle est obtenu par bootstrap des unités
indépendantes. Le signe est publié tel quel. Une contraction, une expansion ou
une absence d'effet restent toutes admissibles.

## Comparaison entre domaines

La même définition d'indicateur peut être utilisée dans plusieurs branches,
mais les amplitudes brutes ne deviennent comparables que si la construction des
défis, dimensions, seuils, poids et unités de réplication est elle-même
appariée. À défaut, on compare seulement la structure de l'effet et son statut.

Implémentation de référence : `methodologie_puissance/pacc_causal.py`.
