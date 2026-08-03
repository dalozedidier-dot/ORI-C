# Environnement d'exécution

Généré par `enregistrer_environnement.py`, Étape 0.7 du plan
directeur. Ce fichier décrit la machine sur laquelle les résultats du
dossier ont été produits. **Il n'est pas une exigence de
reproduction** : un environnement différent n'invalide rien, il
explique un écart.

## Plateforme

| Élément | Valeur |
|---|---|
| Python | 3.12.10 (CPython) |
| Compilateur | MSC v.1943 64 bit (AMD64) |
| Système | Windows 11 |
| Version du système | 10.0.26200 |
| Architecture | AMD64 |
| Processeur | Intel64 Family 6 Model 186 Stepping 2, GenuineIntel |
| Algèbre linéaire | openblas |

## Bibliothèques suivies

| Bibliothèque | Version |
|---|---|
| `numpy` | 2.4.6 |
| `scipy` | 1.18.0 |
| `pandas` | 3.0.5 |
| `matplotlib` | 3.11.1 |
| `networkx` | 3.6.1 |
| `sympy` | 1.14.0 |
| `numba` | 0.66.0 |
| `llvmlite` | 0.48.0 |
| `pytest` | 9.1.1 |
| `rebound` | absent |
| `python-docx` | 1.2.0 |

## Exécution des suites de sous-projets

Trois suites ont leur propre racine de paquet et ne se collectent pas depuis
la racine du dossier. Elles se lancent ainsi :

```bash
cd 02_branche_systeme_solaire/couche_memoire_historique && PYTHONPATH=src python -m pytest -q
```

Deux conditions supplémentaires, découvertes le 2026-08-02 :

**Dépendances.** `scikit-learn` et `statsmodels` sont requis par la
plateforme et n'étaient pas suivis ici. Sans eux, cinq modules de test
échouent à la collecte avec `ModuleNotFoundError`.

**Longueur des chemins Windows.** Les suites de la plateforme et de la couche
astronomique écrivent des jeux de données dans le répertoire temporaire de
`pytest`. Si le chemin de base dépasse la limite historique de 260 caractères,
l'écriture échoue en `PermissionError` puis en `FileNotFoundError` — deux
symptômes trompeurs pour une seule cause. Il faut un chemin de base court :

```bash
PYTHONPATH=src python -m pytest tests -q --basetemp=C:/oric_tmp/pf
```

Sans cela, ces deux suites paraissent cassées alors qu'elles ne le sont pas.
C'est une contrainte de plateforme, pas un défaut du code.

## Portée

Le plan directeur demande en outre l'exécution sous trois systèmes
d'exploitation, sur deux architectures matérielles et dans une image
de conteneur — Étape 0.8 à 0.10. **Rien de cela n'est fait.** Le
dossier n'a été exécuté que sur la plateforme ci-dessus.

Un écart déjà constaté et documenté relève de cette catégorie :
l'écart maximal du contrôle d'attractivité globale vaut `2,00 × 10⁻¹⁶`
dans une exécution et `2,00 × 10⁻¹⁵` dans une autre, selon la version
de la bibliothèque d'algèbre linéaire. Voir
`AUTORITE_DES_DOCUMENTS.md`.
