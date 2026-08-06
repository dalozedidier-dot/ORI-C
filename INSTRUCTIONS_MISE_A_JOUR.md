# Instructions de mise à jour

## Fichiers à supprimer avant copie

**Aucun fichier à supprimer.**

Copier le contenu complet du ZIP en remplaçant les fichiers existants.

## Corrections apportées

1. Le workflow conserve désormais le registre de portée du lot scientifique lorsque les archives brutes volumineuses ne sont pas présentes dans le dépôt.
2. Les 32 expériences de partage du carbone sont reconstruites depuis une petite source brute conservée dans le dépôt. `partition_experiments.csv` reste à 41 lignes, dont 35 complètes, après plusieurs exécutions.
3. `REAL_DATA_COVERAGE.json` conserve 13 jeux couverts et empêche les moteurs de débloquer des protocoles hors de leur portée réelle.
4. Le workflow ne remplace plus les rapports produits pendant l’exécution par des copies statiques plus anciennes.
5. `BILAN_CANONIQUE.md`, `AUDIT_DONNEES_DEPOT.json` et les résultats consolidés correspondent au même calcul strict de 683 entrées.
6. Le benchmark transversal est décrit correctement comme couvrant huit domaines.
7. La page principale GitHub distingue les résultats robustes, exploratoires, négatifs et indéterminés.

## Résultat vérifié

- 298 réussites techniques
- 337 blocages
- 48 protocoles non exécutables informatiquement
- 0 échec
- 0 erreur
- 0 soutien confirmatoire
- 0 rejet confirmatoire
- 635 résultats indéterminés
- 48 non applicables

## Fichiers ajoutés

- `AVANCEES_ET_DECOUVERTES_2026-08-06.md`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/SOURCE.json`
- `donnees_externes/partage_carbone_2026/SOURCE.json`
- `donnees_externes/partage_carbone_2026/raw/Dataset_Fig4_FigS1_FigS2_DC_1.csv`

## Fichiers remplacés

- `.github/workflows/analyse-donnees-reelles.yml`
- `DATA_AVAILABILITY.md`
- `INSTRUCTIONS_MISE_A_JOUR.md`
- `MANIFEST.sha256`
- `MANIFEST.sha256.json`
- `README.md`
- `plateforme/campagne_maximale_reelle/AUDIT_DONNEES_DEPOT.json`
- `plateforme/campagne_maximale_reelle/BILAN_CANONIQUE.md`
- `plateforme/campagne_maximale_reelle/INTEGRATION_MAXIMALE_DONNEES_EXISTANTES.md`
- `plateforme/campagne_maximale_reelle/LOT_SCIENTIFIQUE_2026_08_05.md`
- `plateforme/campagne_maximale_reelle/PROVENANCE_INTEGRATION_DEPOT.json`
- `plateforme/campagne_maximale_reelle/data/REAL_DATA_COVERAGE.json`
- `plateforme/campagne_maximale_reelle/integrer_donnees_existantes.py`
- `plateforme/campagne_maximale_reelle/integrer_lot_scientifique_2026_08_05.py`
- `plateforme/campagne_maximale_reelle/resumer_integration_maximale.py`
- `plateforme/campagne_maximale_reelle/resultats_consolides/REPORT.md`
- `plateforme/source_corrigee/tests/test_external_scientific_bundle.py`

## Vérification locale

```bash
python verifier_dossier.py --allow-lfs-pointers
python scripts/valider_tout.py
python -m pytest -q plateforme/source_corrigee/tests/test_external_scientific_bundle.py
```

La campagne stricte peut être reproduite avec `Campagne maximale ORI-C - trois branches`, option `niveau = maximum`.
