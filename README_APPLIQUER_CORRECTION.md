# ORI-C — appliquer la correction de barrière scientifique

Cette archive est un **overlay**, pas un dépôt complet. Elle ne contient aucune donnée artificielle destinée à servir de preuve.

## But

Corriger le mode `--real-data-only` avant toute nouvelle publication stable :

- politique réelle **fail-closed** ;
- quarantaine de `condensation`, `volatile_budget`, `late_accretion`, `planetary_value` ;
- retrait de l'imputation zéro des budgets volatils ;
- retrait du pseudo-équilibre par minimum Gibbs global ;
- retrait du proxy de mémorisation `planetary_value` ;
- comparaison des traceurs d'accrétion tardive uniquement à l'intérieur d'un même traceur ;
- barrière automatique de publication ;
- workflow d'audit scientifique strict ;
- corrections de portabilité UTF-8, dates ISO et fermeture des classeurs Excel.

## Application

1. Faire une sauvegarde/commit de l'état actuel du dépôt.
2. Vérifier `PATCH_MANIFEST.json` : les fichiers existants indiquent le blob GitHub attendu avant remplacement.
3. Extraire le contenu de l'archive **à la racine du dépôt ORI-C** en remplaçant les fichiers correspondants.
4. Ne pas recopier un ancien `MANIFEST.sha256` : cette archive n'en fournit volontairement aucun.
5. Reconstruire les manifestes sur le vrai dépôt courant :

```bash
python build_manifest.py build
python verifier_dossier.py
```

6. Lancer les barrières et tests :

```bash
python scripts/valider_barriere_scientifique_publication.py
python -m pytest -q plateforme/source_corrigee/tests
python scripts/valider_publication_stable.py
```

7. Dans GitHub Actions, lancer **Audit scientifique strict ORI-C**.
8. Ne publier aucune nouvelle version Zenodo avant que ces contrôles soient verts.

## Important

`pass` est un statut technique. Il n'est jamais converti en preuve scientifique par le compteur global. Les résultats dédiés D'Onofrio, Sokolskyi-Baum, etc. restent évalués dans leurs propres pipelines.

Le fichier `audit/RECLASSEMENT_46_TESTS_2026-08-07.csv` remplace l'affirmation incorrecte « quatre CSV manquants = 46 tests empiriques ». Six tests seulement disposent actuellement d'une voie empirique externe identifiée ; les autres exigent un vrai protocole/modèle, un benchmark prédictif gelé, une simulation explicitement séparée ou une revue humaine.
