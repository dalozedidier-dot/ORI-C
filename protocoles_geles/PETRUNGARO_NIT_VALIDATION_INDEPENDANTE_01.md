# PRED-VIVANT-PETRUNGARO-NIT-001 — prédiction indépendante gelée localement

Statut : **gelée localement le 15 août 2026, non publique, non testée**.

## Prédiction

Dans un nouveau jeu réel d'évolution d'*E. coli* sous nitrofurantoïne, jamais
utilisé dans Petrungaro 2026, connaître le fond génétique initial en plus de la
résistance initiale doit réduire la RMSE de prédiction de la résistance future
d'au moins 20 %. La valeur attendue est 31,762 %, avec une plage prédite de
20–45 %. La reproductibilité entre répétitions d'un même fond doit donner un
ICC d'au moins 0,60.

## Données admissibles

Le jeu doit fournir au moins 30 populations indépendantes, 10 fonds génétiques
et deux répétitions par fond, avec `X`, `m`, `R` et l'identifiant de répétition.
Une sous-table de Petrungaro, une simulation ou un jeu synthétique est interdit.

## Décision immuable

Le résultat soutient la prédiction seulement si les cinq conditions du fichier
JSON associé passent simultanément : gain ≥ 20 %, bootstrap par fond excluant
zéro, permutation stratifiée `p ≤ 0,05`, ICC ≥ 0,60 et direction positive dans
chaque lot préspécifié. Sinon le résultat est négatif ou non testable.

Ce gel ne devient public qu'après publication du commit ou archivage horodaté,
avec l'autorisation explicite du propriétaire du dépôt, et impérativement avant
l'ouverture des résultats du jeu externe.
