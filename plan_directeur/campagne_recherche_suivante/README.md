# Campagne de recherche suivante

Cette campagne ouvre des tests qui répondent directement aux verrous scientifiques déjà localisés. Elle ajoute des données externes, des témoins de complexité égale, des interventions explicites et des protocoles gelés.

## Exécution locale sans données externes

```bash
python plan_directeur/campagne_recherche_suivante/run_all.py
python -m pytest -q \
  01_branche_matiere/tests_causaux/tests \
  02_branche_systeme_solaire/tests_suivants/tests \
  03_branche_vivant/lignees_vesicules/tests \
  03_branche_vivant/benchmark_histoire_antibiotique_2026/tests \
  plan_directeur/campagne_recherche_suivante/tests
python scripts/valider_recherche_suivante.py
```

Les blocs qui nécessitent une source externe restent explicitement en attente.

## Exécution complète

```bash
python plan_directeur/campagne_recherche_suivante/fetch_external_data.py
python plan_directeur/campagne_recherche_suivante/run_all.py
```

Le workflow GitHub `Recherche suivante ORI-C` réalise ces opérations et conserve les rapports comme artefact. Les données brutes tierces ne sont pas redistribuées par l'artefact.

## Fichiers directeurs

- `PLAN_RECHERCHE.md` : contenu scientifique des tests.
- `MATRICE_TESTS.csv` : question, données, témoin, métrique et règle de décision.
- `DECISIONS_SCIENTIFIQUES.md` : ce qui peut et ne peut pas être conclu.
- `sources_externes.json` : provenance et téléchargement des jeux externes.
- `resultats/SYNTHESE.json` : état machine lisible de tous les blocs.
