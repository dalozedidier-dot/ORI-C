# WP-CLIM-MEM-2026 — inscription durable ou relaxation, sur l'enregistrement réel

**Gelé le 8 août 2026, avant toute exécution.**

Ce protocole est écrit et scellé **avant** que la moindre statistique n'ait été
calculée sur la table. Son empreinte et celle du code sont inscrites dans
`GEL.json` avant l'exécution.

---

## Hypothèse ORI-C testée

L'histoire d'un système laisse une trace mesurable dans son état présent. Appliqué
ici : connaître la trajectoire passée du compartiment de mémoire améliore la
prédiction de son état actuel, **au-delà** de ce que donne le forçage présent, et
**au-delà** de ce que donne une histoire permutée de même complexité.

**Hypothèse nulle.** La trajectoire passée n'apporte rien qu'une histoire
permutée de même complexité n'apporterait aussi. Ce qui ressemble à une
inscription n'est qu'une relaxation vers l'état imposé par le forçage courant.

## Variables obligatoires

Toutes présentes dans `data/processed/memoire_climatique_bintanja_insolation.csv`,
1 070 lignes, 0 à 1 069 ka BP au pas de 1 ka, complètes à 100 %.

| rôle | colonne |
|---|---|
| âge | `age_ka_bp` |
| forçage externe indépendant | `insolation_65N_jul_Wm2` |
| compartiment de mémoire, cible | `ice_volume_total_sle` |
| forçage secondaire | `obliquity_deg`, `precession`, `eccentricity` |

`sea_level_m` est **exclu** : il corrèle à +1,000 avec le compartiment de mémoire
dans cette reconstruction. L'utiliser serait circulaire.

## Les trois modèles comparés

Régression linéaire, même famille pour les trois, ajustée sur les mêmes plis.

| modèle | prédicteurs | nombre de paramètres |
|---|---|---|
| `etat_seul` | insolation, obliquité, précession, excentricité à l'instant t | 4 |
| `etat_plus_histoire` | les mêmes, plus le compartiment aux décalages −10, −20, −40 ka | 7 |
| `histoire_permutee` | les mêmes, plus **les mêmes décalages issus d'un bloc temporel permuté** | 7 |

Le troisième modèle est le témoin apparié : **même nombre de paramètres, même
type de prédicteurs, seule la correspondance temporelle est détruite.** Un gain
de `etat_plus_histoire` sur `etat_seul` qui ne survivrait pas à cette comparaison
ne mesurerait que la complexité ajoutée.

## Validation croisée

**Par blocs contigus, dix blocs de 107 ka.** L'enregistrement est fortement
autocorrélé : une validation croisée aléatoire mettrait des points voisins de part
et d'autre de la séparation et rendrait n'importe quel modèle historique
trivialement bon. Les décalages sont calculés à l'intérieur du bloc
d'apprentissage uniquement.

## Métrique et test

Métrique : **RMSE agrégée sur les dix blocs de test**.

Test : **permutation sur le bloc d'histoire**, 2 000 tirages, valeur de p
unilatérale. La plus petite valeur atteignable vaut 1/2001, soit 5,0 × 10⁻⁴, bien
en deçà d'alpha.

**Aucun test de signe sur dix plis n'est employé.** Avec dix unités, un tel test
exigerait 9 plis favorables sur 10 pour descendre sous 0,05 — le défaut recensé
dans `ATTEIGNABILITE_DES_CRITERES_2026-08-08.md`. Le critère retenu ici est
atteignable par construction.

## Règle de décision, écrite avant l'exécution

| issue | condition |
|---|---|
| **soutient** | RMSE(`etat_plus_histoire`) < RMSE(`etat_seul`) **ET** RMSE(`etat_plus_histoire`) < RMSE(`histoire_permutee`) **ET** p ≤ 0,05 |
| **ne soutient pas** | l'une des trois conditions n'est pas remplie |
| **indéterminé** | moins de 8 blocs exploitables, ou une variable obligatoire incomplète |

Aucune autre issue n'est admise. Aucun seuil, aucun décalage, aucun nombre de
blocs ne peut être modifié après lecture du moindre résultat.

## Statut épistémique — à lire avec le verdict

La table repose sur deux produits de modèle : Bintanja est une **modélisation
inverse** du δ¹⁸O benthique de LR04, Berger et Loutre une **solution
astronomique calculée**. Au sens de `EMPIRICAL_POLICY.json`, ce sont
`mixed_observation_and_external_model_output` et `ephemeris_model_input`.

**Quel que soit le verdict, ce protocole ne produit pas une preuve empirique
primaire.** Il tranche sur une reconstruction largement acceptée, ce qui est une
information réelle mais d'un niveau inférieur à une mesure directe. Le verdict
sera inscrit dans `ETAT_DES_PREUVES.md` avec ce niveau et pas un autre.

## Portée

Ce protocole porte sur le compartiment de glace de l'enregistrement pléistocène.
Il ne dit rien de la branche 2 dans son ensemble, ni du modèle M2, qui est une
formulation distincte évaluée par son propre pipeline et déjà non soutenue.
