# ORI-C — plateforme complète de tests

Cette plateforme transforme le plan directeur ORI-C en un système exécutable couvrant tout le programme : socle formel, matière, planètes, Système solaire, mémoire climatique, climat moderne, prébiotique, cellule, endosymbiose, antibiotiques et benchmarks transversaux.

## Portée réelle

Le catalogue contient **683 entrées** réparties dans **51 work packages**, **59 moteurs analytiques** et **33 schémas de données**. Le code automatise les calculs, validations, comparaisons, ablations, plans expérimentaux, préenregistrements, rapports et contrôles de provenance.

Les expériences de laboratoire, les évaluations humaines et les réplications externes restent des protocoles à exécuter réellement. Le logiciel les prépare et contrôle leurs données, sans inventer de résultats.

## Séparation essentielle

- `technical_outcome` : le moteur informatique s'est-il exécuté correctement ?
- `scientific_verdict` : le résultat satisfait-il un critère confirmatoire gelé avant l'analyse ?

Sans critère gelé, le verdict scientifique reste `undetermined`, même lorsque le statut technique vaut `pass`.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate       # Windows
python -m pip install -U pip
python -m pip install -e .
```

Pour la couche astronomique optionnelle :

```bash
python -m pip install -e ".[science]"
```

## Démarrage complet

Créer un espace de travail avec tous les modèles de données, les 51 protocoles, la grille des 683 critères et les rapports initiaux :

```bash
oric-full bootstrap travail_ORI-C
```

Créer une démonstration intégrale avec des données synthétiques destinées uniquement à tester le code :

```bash
oric-full bootstrap travail_demo --synthetic --seed 20260801
```

## Commandes principales

```bash
oric-full catalog
oric-full audit
oric-full init-data --data-dir data
oric-full validate-data --data-dir data
oric-full import-existing /chemin/vers/ORI-C_dossier_unique
oric-full protocols --output-dir protocols
oric-full criteria-template --output preregistration/criteria.csv
oric-full preregister --output preregistration/catalogue.json
oric-full run --all --data-dir data --output-dir results/full
oric-full run-config configs/campaign_full.yaml
oric-full manifest .
oric-full demo-all --workspace demo_workspace
```

## Flux scientifique recommandé

1. Créer l'espace de travail.
2. Remplacer les CSV vides ou synthétiques par les données réelles.
3. Valider les schémas.
4. Remplir la grille des critères.
5. Geler les critères et le préenregistrement.
6. Exécuter les analyses exploratoires.
7. Geler les modèles confirmatoires.
8. Exécuter les tests hors échantillon.
9. Produire le manifeste et le rapport.
10. Faire répliquer les résultats importants par une autre équipe.

## Organisation

- `catalogue/` : les 683 tests extraits du plan directeur
- `src/oric_full/core/` : socle ORI-C, mémoire, viabilité, diagnostics, interventions
- `src/oric_full/domains/` : moteurs matière, planètes, astronomie, climat, prébiotique, vivant, antibiotiques
- `examples/data/` : jeux synthétiques illustratifs
- `schemas/` : index des 33 tables attendues
- `configs/` : campagnes prêtes à lancer
- `tests/` : tests logiciels de la plateforme
- `docs/` : plan directeur complet

## Limites

La plateforme fournit l'infrastructure nécessaire à l'ensemble du programme. Elle ne remplace ni les instruments, ni les données publiques à télécharger, ni les cultures biologiques, ni la pétrologie expérimentale, ni l'expertise externe. Les modules numériques de démonstration ne doivent pas être présentés comme des modèles de haute précision sans validation indépendante.
