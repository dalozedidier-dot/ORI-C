# Dictionnaire des données empiriques

## SOURCES_EMPIRIQUES.csv

`source_id` identifie la source. `evidence_mode` fixe le type de preuve. `source_class` doit être `primary_peer_reviewed` ou `official_observation_product`. `portion_used` décrit les mesures admissibles. `portion_excluded` documente explicitement ce qui n’entre pas dans la preuve, en particulier les modèles et simulations présents dans certains articles. `stage_ids` liste les stades concernés.

## MESURES_EMPIRIQUES.csv

`record_id` est stable. `value_numeric` contient seulement une mesure publiée ou une valeur directement codable de cette mesure. `uncertainty_minus` et `uncertainty_plus` conservent l’asymétrie lorsqu’elle existe. `value_text` sert aux booléens ou descriptions qui accompagnent une valeur numérique. `scope_note` interdit les extrapolations silencieuses.

## CHAINE_EMPIRIQUE.csv

`empirical_anchor` nomme l’observation ou l’archive réelle. `history_carrier` décrit ce qui persiste physiquement. `evidence_class` indique la nature de l’ancrage.

## LIENS_EMPIRIQUES.csv

`link_class` est essentiel. Une continuité matérielle directe n’a pas le même statut qu’une séquence inter-systèmes. Les liens `analogue`, `cross_system` ou `non_unique` ne doivent jamais être cités comme reconstruction causale du Système solaire.

## Sorties

`AUDIT_ADMISSIBILITE.json` doit afficher zéro simulation, zéro ligne synthétique et zéro imputation. `CLAIMS.json` porte les verdicts. `SYNTHESE.json` contient seulement les nombres canoniques destinés à la synchronisation du dépôt.
