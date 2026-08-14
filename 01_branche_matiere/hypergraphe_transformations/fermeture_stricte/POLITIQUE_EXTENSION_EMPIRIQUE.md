# Politique d’extension empirique de l’hypergraphe

Cette politique ne modifie jamais les fichiers canoniques scellés. Une extension est une couche amovible et auditée.

Une hyperarête d’extension peut être dite `evidence_qualified_extension` uniquement si :

1. ses entrées et sorties conservent exactement la sémantique des nœuds existants ;
2. chaque composante indispensable du nœud de sortie est reliée à au moins une source primaire empirique ;
3. les sources peuvent être complémentaires, mais l’enchaînement doit rester dans une même classe physique sans introduire un état intermédiaire non déclaré ;
4. une matrice machine liste chaque composante, source, DOI et verdict ;
5. le calcul de fermeture est séparé de la qualification empirique ;
6. le baseline scellé reste publié à côté du résultat de l’extension ;
7. une contradiction ou une composante non soutenue fait retomber l’extension en fail-closed ;
8. une extension ne vaut ni validation d’une histoire naturelle unique, ni validation des relations aval qui restent hypothétiques, ni fermeture du §XIV.

## Application à HC02-E1

`N051 + N028 -> N030` est évaluée composante par composante dans `HC02_EVIDENCE_MATRIX.csv`. La qualification actuelle est 4/4, et l’extension ferme 53/53. Le baseline v0.9.3 reste 46/53.
