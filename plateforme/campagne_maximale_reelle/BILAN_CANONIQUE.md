# Campagne réelle consolidée - bilan canonique

Date d’exécution : 2026-08-03. Catalogue : 683 entrées.

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
| Réussites | 211 |
| Échecs | 0 |
| Bloqués | 440 |
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

## Pourquoi le total diffère du bilan précédent

Le bilan précédent comptait 213 réussites et 438 blocages. La réexécution stricte du 3 août 2026 a reclassé deux opérations qui dépendaient de la table absente `modern_climate_ensemble.csv`. Elles sont désormais correctement enregistrées comme bloquées au lieu d’être comptées comme réussites techniques.

## Interprétation

La campagne ne produit aucun soutien scientifique confirmatoire à ORI-C. Elle établit qu’une partie des 59 moteurs traite correctement les 33 jeux présents et documente précisément les analyses impossibles avec les données actuelles. Une réussite technique ne devient jamais automatiquement une preuve scientifique.
