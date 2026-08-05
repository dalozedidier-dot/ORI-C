# Instructions de mise à jour

## Fichiers à supprimer avant copie

Aucun fichier à supprimer pour cette mise à jour.

## Installation

1. Décompresser le ZIP.
2. Copier le contenu du dossier `ORI-C-main` dans le dépôt en remplaçant les fichiers existants.
3. Vérifier que les trois sous-dossiers de `donnees_externes` ont bien été copiés.
4. Publier également les nouveaux fichiers de données, désormais explicitement autorisés par `donnees_externes/.gitignore`.
5. Relancer le workflow `Recherche suivante ORI-C` avec les valeurs par défaut.

## Contrôle avant publication

```bash
python plan_directeur/campagne_recherche_suivante/fetch_external_data.py --offline
python plan_directeur/campagne_recherche_suivante/run_all.py
python scripts/valider_recherche_suivante.py
```

## Fichiers principaux remplacés

- `.github/workflows/recherche-suivante.yml`
- `02_branche_systeme_solaire/tests_suivants/auditer_speleothemes.py`
- `02_branche_systeme_solaire/tests_suivants/tests/test_suivants.py`
- `03_branche_vivant/lignees_vesicules/analyser_lignees.py`
- `03_branche_vivant/lignees_vesicules/tests/test_parser.py`
- `donnees_externes/.gitignore`
- `donnees_externes/README.md`
- `plan_directeur/campagne_recherche_suivante/sources_externes.json`
- `MANIFEST.sha256`
- `MANIFEST.sha256.json`

## Nouveaux contenus

- les 12 classeurs Dryad nécessaires au test des vésicules ;
- les 3 CSV Dryad nécessaires au test antibiotique ;
- le CSV NOAA complet ;
- un `SOURCE.json` vérifiable pour chacun des trois jeux ;
- les deux archives Dryad originales dans les sous-dossiers `raw`.
