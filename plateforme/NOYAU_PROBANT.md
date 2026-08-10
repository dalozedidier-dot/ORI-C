# Noyau probant actif

Le catalogue canonique conserve **683 tests**. Le tri ne supprime aucun identifiant et ne modifie aucun verdict scientifique.

La politique d'organisation est portée par `POLITIQUE_NOYAU_PROBANT.csv` :

- **366 `GARDER`** : tests qui restent dans le programme probant actif ;
- **317 `VIRER`** : tests sortis du noyau probant et conservés, si utiles, comme QA, exploration, documentation ou sous-analyses ;
- **27/27 tests confirmatoires** restent dans le noyau probant.

`VIRER` signifie uniquement « sortir du noyau probant ». Cela ne signifie ni effacer le code, ni effacer un résultat négatif, ni réécrire l'historique du catalogue.

## Colonnes de la politique

- `test_id` : identifiant canonique du catalogue ;
- `decision` : `GARDER` ou `VIRER` ;
- `destination` : `noyau_probant` ou `qa_exploratoire` ;
- `rang_action` : ordre d'action interne au tri (`1`, `2`, `3`) pour les tests gardés. Ce champ n'est **ni** la colonne `priority` du catalogue **ni** un niveau de preuve E0–E6 ;
- `motif_code` : motif contrôlé, sans verdict scientifique implicite.

Les motifs autorisés sont validés par `valider_noyau_probant.py`. Le validateur est fail-closed : il exige une bijection exacte avec les 683 IDs, les compteurs 366/317, des destinations cohérentes et la conservation de tous les tests confirmatoires.

Le workflow matérialise `NOYAU_PROBANT_ACTIF.csv` et `NOYAU_PROBANT_RESUME.json` dans les sorties de l'audit. Ces fichiers générés sont des vues de travail et ne remplacent ni `catalogue_tests.csv`, ni les critères gelés, ni `RESULTATS_SCIENTIFIQUES_CERTIFIES.json`.
