# Erratum scientifique — ORI-C v0.9.4-research

Date : 7 août 2026

Cet erratum concerne la **plateforme générique des 683 entrées**, pas les résultats issus de pipelines scientifiques dédiés.

## Correction principale

Le statut technique `pass` de la plateforme ne doit pas être interprété comme une preuve scientifique ni comme la réussite individuelle de tous les protocoles qui partagent le même moteur.

L'audit du 7 août 2026 a identifié deux défauts :

1. le mode `--real-data-only` était fail-open pour les datasets absents de `REAL_DATA_COVERAGE.json` ;
2. quatre moteurs génériques étaient trop permissifs pour répondre aux protocoles individuels auxquels ils étaient raccordés : `condensation`, `volatile_budget`, `late_accretion`, `planetary_value`.

Ces moteurs sont désormais placés en quarantaine scientifique dans la correction du 7 août 2026 et ne peuvent plus produire de `pass` en mode données réelles strict.

## Ce qui est retiré comme argument de preuve

- tout compteur global de `pass` de la plateforme utilisé comme nombre de preuves ;
- toute interprétation empirique d'un résultat provenant des quatre moteurs génériques ci-dessus ;
- toute prétention selon laquelle l'ajout des quatre CSV manquants suffirait à tester les 46 protocoles concernés.

## Ce qui n'est pas annulé par cet erratum

Les résultats obtenus par des pipelines dédiés et traçables restent séparés et doivent être évalués sur leurs propres données, protocoles et contrôles. Cela inclut notamment les analyses D'Onofrio et Sokolskyi-Baum, ainsi que les validations astronomiques explicitement présentées comme résultats de modèle physique et non comme observations directes.

## Remplacement

La correction complète est documentée dans :

`CORRECTION_BARRIERE_SCIENTIFIQUE_2026-08-07.md`

Une nouvelle publication stable doit exécuter :

`scripts/valider_barriere_scientifique_publication.py`

avant la construction de l'archive de release.
