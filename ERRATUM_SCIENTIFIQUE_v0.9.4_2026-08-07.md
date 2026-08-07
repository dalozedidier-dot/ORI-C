# Erratum scientifique ORI-C v0.9.4-research — 7 août 2026

Cet erratum concerne l’interprétation de la **campagne générique de 683 entrées** publiée avec l’état v0.9.4-research. Il ne réécrit pas rétroactivement les fichiers de la publication Zenodo : il documente la correction méthodologique appliquée à l’état courant du dépôt.

## Correction du compteur générique

Les anciens nombres `298 réussites techniques / 337 blocages / 48 non-exécutions` décrivaient des statuts d’exécution de la plateforme. Ils **ne constituaient pas 298 preuves scientifiques**. Le réaudit du 7 août a montré que le mode `--real-data-only` devait être durci : la présence d’un fichier ou l’exécution d’un moteur ne suffisent pas à rendre un protocole empirique.

Le pare-feu `fail_closed_v2` exige désormais, pour chaque `test_id`, une ressource déclarée dans `EMPIRICAL_POLICY.json`, admissible comme preuve empirique et explicitement autorisée pour ce protocole. Avec cette règle, la même matrice de 683 entrées donne :

- 9 réussites techniques ;
- 626 blocages ;
- 48 protocoles non exécutables informatiquement ;
- 0 échec et 0 erreur ;
- 0 verdict scientifique `supports` dans cette matrice générique ;
- 635 verdicts `undetermined` et 48 `not_applicable`.

Les neuf réussites techniques sont `P3-001`, `P3-002`, `P5-001`, `V1-001`, `V1-004`, `B2-003`, `R1-005`, `R1-009` et `R1-010`. Un `pass` technique indique seulement que l’analyse autorisée a pu s’exécuter. Il ne vaut pas, à lui seul, confirmation d’une hypothèse.

## Résultats ciblés qui restent séparés

Les analyses dédiées possèdent leurs propres données, critères et contrôles. Le résultat D’Onofrio sur 288 mesures antibiotiques et le protocole des vésicules sur des lignées parent-descendant réelles ne doivent ni être promus par l’ancien compteur 298, ni être annulés par le nouveau compteur 9. Ils restent évalués par leurs pipelines ciblés.

De même, les intégrations N-corps, H011 et les autres expériences numériques restent des **résultats de modèle ou de simulation**, jamais des observations empiriques. Leur statut doit être lu dans leur protocole propre.

## Nouvelles ressources du 7 août

Le corpus `DONNEES_REELLES_ORI-C_2026-08-07(1).zip` a été vérifié par empreinte. La mise à jour retient uniquement les ressources utiles et leur provenance. Elle n’utilise pas leur simple présence pour fabriquer de nouveaux verdicts :

- les traceurs GEOROC ouvrent uniquement l’audit `P5-001` ;
- la grille thermochimique reste une table calculée depuis des paramètres publiés, sans prétention d’équilibre de condensation ;
- l’inventaire volatil reste incomplet et aucune masse absente n’est remplacée par zéro ;
- les séries climatiques longues sont conservées pour de futurs protocoles préenregistrés ;
- `planetary_histories.csv` reste volontairement absent faute de provenance primaire suffisante par cellule.

## Fichiers faisant autorité après correction

- `MISE_A_JOUR_PREUVES_EMPIRIQUES_2026-08-07.md`
- `plateforme/campagne_maximale_reelle/EMPIRICAL_POLICY.json`
- `plateforme/campagne_maximale_reelle/data/REAL_DATA_COVERAGE.json`
- `plateforme/campagne_maximale_reelle/resultats_integration_maximale/results.json`
- `plateforme/campagne_maximale_reelle/BILAN_CANONIQUE.md`
- `plateforme/campagne_maximale_reelle/AUDIT_DONNEES_DEPOT.md`

Les manifestes SHA-256 doivent être reconstruits après application de cette correction.
