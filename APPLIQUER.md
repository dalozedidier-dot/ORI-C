# Mise à jour Git — noyau probant 366/317

Branche recommandée : `agent/tri-noyau-probant-366`.

Cette mise à jour conserve `plateforme/catalogue_tests.csv` à 683 entrées et ajoute une politique séparée classant chaque ID exactement une fois : 366 `GARDER` dans le noyau probant et 317 `VIRER` vers QA/exploration. Les 27 tests confirmatoires restent tous dans le noyau.

Validation déjà exécutée :

- `PYTHONPATH=plateforme/source_corrigee/src python -m pytest -q plateforme/source_corrigee/tests/test_catalogue.py` → 2 passed
- `python plateforme/valider_noyau_probant.py ...` → 683 / 366 / 317, 27/27 confirmatoires
- parsing YAML de `.github/workflows/audit-empirique-strict.yml` → ok

Commandes Git recommandées après copie des fichiers dans le dépôt :

```bash
git switch main
git pull --ff-only
git switch -c agent/tri-noyau-probant-366
python plateforme/valider_noyau_probant.py --sortie-csv /tmp/noyau.csv --sortie-json /tmp/noyau.json
PYTHONPATH=plateforme/source_corrigee/src python -m pytest -q plateforme/source_corrigee/tests/test_catalogue.py
git add .github/workflows/audit-empirique-strict.yml plateforme/POLITIQUE_NOYAU_PROBANT.csv plateforme/NOYAU_PROBANT.md plateforme/valider_noyau_probant.py plateforme/README.md
git commit -m "research: séparer le noyau probant actif des 683 tests"
git push -u origin agent/tri-noyau-probant-366
```

Ne pas mélanger automatiquement le commit divergent `dc45f303674ffcdec24ab7e86e6d59692b254d94` dans cette branche. Le rebaser ou le fusionner séparément après résolution explicite de sa divergence avec `main`.
