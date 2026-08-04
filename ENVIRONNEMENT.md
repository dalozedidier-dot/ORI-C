# Environnements d'exécution

ORI-C distingue l'environnement canonique de reproduction, les environnements
de compatibilité et les instantanés de provenance. Une différence de version
n'invalide pas automatiquement un résultat, mais elle doit rester visible.

## 1. Environnement canonique de reproduction

| Élément | Valeur |
|---|---|
| Python | 3.12 |
| Dépendances exactes | `plateforme/source_corrigee/requirements-lock.txt` |
| Système CI | Ubuntu, GitHub Actions |
| Threads numériques | `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1` |
| Plugins pytest externes | désactivés avec `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` |
| Données volumineuses | Git LFS hydraté avant validation |

Cet environnement est celui des workflows canoniques. Le fichier
`plateforme/requirements.txt` contient seulement des bornes minimales et ne
constitue pas un verrou.

## 2. Matrice de compatibilité

La CI contrôle Python 3.12 et 3.13. Les résultats scientifiques canoniques
restent rattachés à Python 3.12 tant qu'une nouvelle version n'est pas gelée.
La portabilité numérique est évaluée avec les tolérances documentées dans les
tests, sans confondre reproductibilité numérique et égalité binaire.

## 3. Instantané de provenance Windows

L'environnement ayant servi à une partie des résultats livrés était :

| Élément | Valeur |
|---|---|
| Python | 3.12.10, CPython |
| Système | Windows 11, AMD64 |
| Processeur | Intel64 Family 6 Model 186 Stepping 2 |
| Algèbre linéaire | OpenBLAS |
| numpy | 2.4.6 |
| scipy | 1.18.0 |
| pandas | 3.0.5 |
| matplotlib | 3.11.1 |
| networkx | 3.6.1 |
| sympy | 1.14.0 |
| numba | 0.66.0 |
| llvmlite | 0.48.0 |
| pytest | 9.1.1 |
| python-docx | 1.2.0 |

Cet instantané est une information de provenance. Il ne remplace pas le verrou
canonique et ne signifie pas que toutes les campagnes ont été recalculées avec
cet ensemble exact.

## 4. Métadonnées à conserver avec chaque campagne

Chaque nouvel artefact de calcul doit enregistrer :

- la version Python ;
- le système et l'architecture ;
- `pip freeze` ;
- les informations BLAS et LAPACK disponibles ;
- les graines aléatoires ;
- l'identifiant du commit ;
- l'empreinte des jeux de données ;
- la commande exacte.

Le script `enregistrer_environnement.py` fournit le socle de cet enregistrement.

## 5. Exécution des suites particulières

```bash
cd 02_branche_systeme_solaire/couche_memoire_historique
PYTHONPATH=src python -m pytest -q
```

Sous Windows, utiliser un répertoire temporaire court pour les suites qui
écrivent de nombreux fichiers :

```bash
PYTHONPATH=src python -m pytest tests -q --basetemp=C:/oric_tmp/pf
```

`scikit-learn` et `statsmodels` sont requis par la plateforme. Une absence de
ces modules ou un chemin Windows trop long peut produire des erreurs de
collecte sans rapport avec le code scientifique.
