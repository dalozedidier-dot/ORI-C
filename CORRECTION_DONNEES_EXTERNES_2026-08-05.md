# Correction des données externes — 5 août 2026

Cette mise à jour supprime la dépendance opérationnelle aux téléchargements Dryad pendant l'exécution GitHub. Les données nécessaires sont intégrées avec leur provenance et vérifiées avant analyse.

## Corrections effectuées

1. Intégration des deux archives Dryad téléchargées depuis les DOI officiels.
2. Intégration du CSV NOAA/NCEI complet.
3. Correction du lecteur NOAA pour distinguer la table de métadonnées de la table de mesures.
4. Correction du lecteur des classeurs de vésicules :
   - sélection du premier bloc réel de 96 puits A1-H12 ;
   - exclusion des colonnes auxiliaires `PM` et `-F` ;
   - récupération d'une génération dont l'en-tête est absent mais encadré par deux générations explicites ;
   - priorité aux couples donneur-receveur explicites des feuilles `drcode` et `selcode` ;
   - refus de transformer une génération absente en filiation directe.
5. Suppression du cache GitHub Actions devenu inutile pour ces jeux intégrés.
6. Validation hors ligne des données avant chaque exécution de la campagne.

## Résultats vérifiés

- le test antibiotique s'exécute sur 288 mesures ;
- le test des vésicules s'exécute sur les 12 classeurs réels ;
- l'audit NOAA détecte la chronologie, le proxy isotopique, les sites, latitudes et longitudes ;
- aucun module ne reste en attente de données externes ;
- 28 tests ciblés réussissent ;
- la campagne complète termine avec 0 erreur d’exécution et 0 bloc en attente ;
- le test de permutation des vésicules a été optimisé sans modifier sa règle statistique.
