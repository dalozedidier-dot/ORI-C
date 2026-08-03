# Reproduction

## Vérification immédiate

```bash
python scripts/verifier_paquet.py
```

## Refaire seulement l’analyse

```bash
python -m venv .venv-science
source .venv-science/bin/activate
python -m pip install -r code/ORI-C_Systeme_solaire_tests/requirements.science.lock.txt
python -m pip install --no-build-isolation --no-deps -e code/ORI-C_Systeme_solaire_tests
cd code/ORI-C_Systeme_solaire_tests
python scripts/analyze_real_science_suite.py \
  --config configs/real_science_max.yaml \
  --runs ../../../resultats/real_science_max \
  --output ../../../analyse_recalculee
```

## Refaire les 25 calculs

Depuis le dossier de code et dans le même environnement :

```bash
python scripts/run_real_science_suite.py \
  --config configs/real_science_max.yaml \
  --overwrite
python scripts/analyze_real_science_suite.py \
  --config configs/real_science_max.yaml
```

L’exécution utilise jusqu’à neuf cœurs. Sa durée dépend fortement du processeur. Les jobs intacts peuvent être conservés avec `--resume` après une interruption.

Les données JPL et IMCCE sont figées dans `data/`. Les scripts d’acquisition permettent aussi de refaire les requêtes réseau.
