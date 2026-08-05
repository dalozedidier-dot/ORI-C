# Instructions de mise à jour

## Fichiers à supprimer avant copie

Aucun fichier à supprimer pour cette mise à jour.

## Problème corrigé

Le workflow passait sous Python 3.12 mais échouait sous Python 3.13 à l'étape
`git diff --exit-code`. Les calculs produisaient les mêmes verdicts, mais quelques
nombres à virgule flottante différaient d'environ 10⁻¹⁶ selon la version de
Python, NumPy et scikit-learn. Git interprétait ces écarts de dernier bit comme
des modifications des résultats scientifiques.

Les deux analyses concernées sérialisent désormais leurs nombres avec une
représentation canonique à 13 chiffres significatifs. Les calculs, comparaisons,
tests statistiques et décisions sont toujours effectués avec la précision
complète. Seule l'écriture des fichiers JSON est stabilisée.

## Fichiers remplacés

- `03_branche_vivant/lignees_vesicules/analyser_lignees.py`
- `03_branche_vivant/lignees_vesicules/tests/test_parser.py`
- `03_branche_vivant/lignees_vesicules/resultats/RESULTAT.json`
- `03_branche_vivant/benchmark_histoire_antibiotique_2026/analyser.py`
- `03_branche_vivant/benchmark_histoire_antibiotique_2026/tests/test_analysis.py`
- `03_branche_vivant/benchmark_histoire_antibiotique_2026/resultats/RESULTAT.json`
- `plan_directeur/campagne_recherche_suivante/resultats/SYNTHESE.json`
- `INSTRUCTIONS_MISE_A_JOUR.md`
- `MANIFEST.sha256`
- `MANIFEST.sha256.json`

## Installation

1. Décompresser le ZIP.
2. Copier tout le contenu du dossier `ORI-C-main` dans le dépôt en remplaçant les
   fichiers existants.
3. Aucun ancien fichier ne doit être supprimé pour cette mise à jour.
4. Publier tous les fichiers remplacés dans le même commit.
5. Relancer les workflows GitHub.

## Contrôle attendu

Les jobs `Contrôles portables Python 3.12` et `Contrôles portables Python 3.13`
doivent tous deux passer l'étape :

```bash
git diff --exit-code -- \
  plan_directeur/campagne_recherche_suivante/resultats \
  01_branche_matiere/tests_causaux/resultats \
  02_branche_systeme_solaire/tests_suivants/resultats \
  03_branche_vivant/lignees_vesicules/resultats \
  03_branche_vivant/benchmark_histoire_antibiotique_2026/resultats
```

Les verdicts scientifiques restent inchangés :

- vésicules : `all_pre_registered_components_supported`
- antibiotique : `history_supported_against_both_controls`
- erreurs d'exécution : `0`
- blocs en attente de données : `0`
