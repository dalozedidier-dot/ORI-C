# Mise à jour de recherche ORI-C

Cette mise à jour poursuit les tests scientifiques sans modifier les métadonnées de publication, le DOI ou le numéro de version existant.

## Nouveaux blocs

1. `H011` est testée comme relation à seuil sous intervention numérique sur la turbulence.
2. le cycle `H030-H031-H052-H053` est audité pour distinguer ancrages séparés et fermeture empirique réelle.
3. `Pacc` est mesuré par les six interventions Jupiter-Saturne, à l'échelle des interventions et des dimensions de réponse.
4. `WP-C2b` est gelé avec appariement par régime, points non saturés et huit graines réservées.
5. une compilation NOAA de spéléothèmes est enregistrée pour audit indépendant de chronologie et de proxy.
6. les lignées de vésicules Dryad sont acquises et analysées par cartes donneur-receveur, sélection, permutation et ablations.
7. un jeu antibiotique externe Dryad est analysé avec séparation groupée par souche et témoin d'histoire permutée de même complexité.

## État local avant acquisition réseau

- `H011` : seuil monotone, rapport 3,33 dans les simulations publiées, intervention naturelle non mesurée.
- cycle des interfaces : quatre relations ancrées, aucune trajectoire quantitative unique.
- `Pacc` astronomique : 6 interventions sur 6 et 17 dimensions sur 18 au-dessus de l'enveloppe de référence.
- `WP-C2b` : protocole gelé avec quatre points non saturés et huit graines réservées.
- spéléothèmes, vésicules et antibiotique : `waiting_for_external_data` dans la construction locale.

## Exécution complète

```bash
python plan_directeur/campagne_recherche_suivante/fetch_external_data.py
python plan_directeur/campagne_recherche_suivante/run_all.py
python scripts/valider_recherche_suivante.py
```

Dans GitHub Actions, lancer `Recherche suivante ORI-C`. Le workflow télécharge les jeux externes, calcule leur provenance, exécute les analyses et publie les rapports sous forme d'artefact. Les données brutes tierces ne sont pas redistribuées.

## Validation de la mise à jour

- 13 nouveaux tests réussis.
- 5 tests du calibrage matière réussis.
- 2 tests du transfert climatique réussis.
- 2 tests du benchmark Card 2019 réussis.
- 2 tests du programme prébiotique existant réussis.
- 1 136 contenus conformes après reconstruction du manifeste.
