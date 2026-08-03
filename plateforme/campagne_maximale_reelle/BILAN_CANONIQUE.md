# Campagne réelle consolidée - bilan canonique

Date d’exécution : 2026-08-01. Catalogue : 683 entrées.

## Composition des données actives

| Jeu | Lignes | Statut |
|---|---:|---|
| La2004, séries orbitales | 51 001 | excentricité, obliquité, précession |
| La2010, référence orbitale | 1 381 | excentricité et incertitude |
| JPL Horizons DE441, éphémérides | 15 | schéma validé |
| JPL Horizons DE441, conditions initiales | 15 | schéma validé |
| LR04, paléoclimat | 2 601 | schéma validé |
| GISTEMP, séries modernes | 3 802 | observations multi-régionales |
| GISTEMP, incertitude observationnelle | 338 400 | 200 membres, pas des modèles climatiques |
| NASA Exoplanet Archive | 6 333 | solutions `default_flag=1` |
| Antibiotiques, cycles | 942 | Windels et al. |
| Antibiotiques, mesures | 1 068 | Windels et al. |
| ARN catalytique | 80 | Papastavrou, Horning et Joyce |

## Résultat de la réexécution consolidée

| Statut technique | Nombre |
|---|---:|
| Réussites | 213 |
| Échecs | 0 |
| Bloqués | 438 |
| Erreurs | 0 |
| Non exécutés | 32 |

| Verdict scientifique | Nombre |
|---|---:|
| Soutient | 0 |
| Ne soutient pas | 0 |
| Indéterminé | 651 |
| Inconclusif | 0 |
| Non applicable | 32 |

Les sorties complètes sont dans `resultats_consolides/`.

## Pourquoi le nombre de réussites est inférieur à 249

Les anciens résultats étendus comptaient certaines opérations GISTEMP comme des réussites alors que le jeu ne contient ni modèles climatiques indépendants, ni scénarios d’émissions, ni phase de retrait ou de restauration. La fusion rétablit les garde-fous de portée scientifique. Ces opérations deviennent des blocages explicites au lieu de réussites techniques. Le total consolidé est donc plus prudent et plus cohérent avec la nature réelle des données.

## Interprétation

La campagne ne produit aucun soutien scientifique confirmatoire à ORI-C. Elle établit qu’une partie des moteurs traite correctement les jeux présents et documente précisément les analyses impossibles avec les données actuelles.
