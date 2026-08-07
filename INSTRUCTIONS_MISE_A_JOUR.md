# État de la mise à jour du 7 août 2026

La correction est intégrée directement dans l’arborescence ORI-C. Aucun dossier `payload`, aucun installateur de patch et aucun manifeste de paquet ne fait partie du dépôt scientifique.

## État empirique strict

La matrice générique de 683 entrées sous `fail_closed_v2` produit :

- 9 réussites techniques
- 626 blocages
- 48 protocoles non exécutables informatiquement
- 0 échec
- 0 erreur
- 0 verdict scientifique `supports`
- 635 verdicts `undetermined`
- 48 `not_applicable`

Ces compteurs décrivent la plateforme générique. Les résultats ciblés de branche restent évalués dans leurs pipelines propres.

## Données du corpus réel du 7 août

Sont conservés avec provenance et portée explicite : la compilation GEOROC de traceurs, la grille thermodynamique calculée depuis des paramètres publiés, l’inventaire volatil documentaire, les séries GISTEMP/HadCRUT5 et les séries longues EPICA, Vostok et LR04. `planetary_histories.csv` reste absent faute de provenance primaire complète par cellule.

## Contrôles de cohérence

Les deux manifestes SHA-256 sont reconstruits à partir de l’arbre final, après toutes les corrections et sorties canoniques. `EMPIRICAL_POLICY.json` et `REAL_DATA_COVERAGE.json` restent les verrous de portée du mode réel strict.
