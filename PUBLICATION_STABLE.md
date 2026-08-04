# Publication stable v0.9.4-research

## Automatisation

Le tag `v0.9.4-research` déclenche `.github/workflows/release.yml`. Le workflow hydrate Git LFS, exécute les validations, construit l’archive canonique, calcule son SHA-256 et joint les deux fichiers à une release GitHub.

## DOI

`.zenodo.json` est prêt. L’obtention d’un DOI exige l’activation de l’intégration GitHub dans Zenodo puis la publication de la release. Le DOI ne peut pas être inventé ni créé hors du compte Zenodo de l’auteur.

## Commandes locales

```bash
git lfs pull
python verifier_dossier.py
python scripts/valider_tout.py --strict-lfs
python plan_directeur/campagne_priorites_v093/run_all.py
python scripts/valider_publication_stable.py
python scripts/construire_archive_canonique.py --output-dir dist
```
