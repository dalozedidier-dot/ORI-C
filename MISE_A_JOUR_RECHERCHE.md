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

## État après intégration des données

- `H011` : seuil monotone, rapport 3,33 dans les simulations publiées, intervention naturelle non mesurée.
- cycle des interfaces : quatre relations ancrées, aucune trajectoire quantitative unique.
- `Pacc` astronomique : 6 interventions sur 6 et 17 dimensions sur 18 au-dessus de l'enveloppe de référence.
- `WP-C2b` : protocole gelé avec quatre points non saturés et huit graines réservées.
- spéléothèmes : audit exécuté sur 27 721 couples âge-isotope répartis dans la compilation NOAA.
- vésicules : les quatre composantes préenregistrées sont soutenues sur les 12 classeurs réels.
- antibiotique : l’histoire améliore la prédiction contre le modèle d’état et le témoin d’histoire permutée.

## Exécution complète

```bash
python plan_directeur/campagne_recherche_suivante/fetch_external_data.py
python plan_directeur/campagne_recherche_suivante/run_all.py
python scripts/valider_recherche_suivante.py
```

Dans GitHub Actions, lancer `Recherche suivante ORI-C` avec les valeurs par défaut. Le workflow contrôle les jeux intégrés hors ligne, exécute les analyses et publie les rapports sous forme d'artefact. Le rafraîchissement réseau reste facultatif.

## Validation de la mise à jour

- 28 tests ciblés réussis.
- 0 erreur d'exécution dans `run_all.py`.
- 0 bloc en attente de données externes.
- workflow YAML valide.
- 1 161 fichiers inscrits dans le manifeste.
- 0 fichier modifié, absent ou non listé.
- 69 objets Git LFS restent sous forme de pointeurs dans l'archive source, comme dans la version fournie.


## Maintenance de l'acquisition, 5 août 2026

La mise à jour intègre directement la correction Dryad au dossier complet. Les liens individuels sont désormais résolus depuis le DOI et la version publique courante. Le client conserve le chemin exact des redirections signées, valide les formats, tente l'archive complète en repli et remplace le cache de façon atomique. Un cache complet antérieur est conservé si un rafraîchissement réseau échoue.

Le fichier temporaire `fix_dryad_403.patch`, responsable de l'échec des contrôles d'intégrité Python 3.12 et 3.13, a été supprimé. Six tests de régression couvrent la nouvelle acquisition. Le détail se trouve dans `CORRECTION_ACQUISITION_DRYAD_2026-08-05.md`.
