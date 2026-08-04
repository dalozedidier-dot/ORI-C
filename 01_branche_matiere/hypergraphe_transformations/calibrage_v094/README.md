# Calibrage v0.9.4 de l'architecture matérielle

Ce paquet applique le programme approuvé après la validation de l'architecture v0.9.3 :

- gel de la structure canonique ;
- calibrage des 53 hyperarêtes ;
- tests de stabilité sous ablations et seuils documentaires ;
- identification du noyau stable et des zones sensibles ;
- test de transfert externe sur deux trajectoires stellaires MESA.

## Exécution

```bash
python 01_branche_matiere/hypergraphe_transformations/calibrage_v094/calibrage_relations.py
python -m pytest -q 01_branche_matiere/hypergraphe_transformations/calibrage_v094/tests
```

## Résultats

- `resultats/calibrage_hyperaretes.csv`
- `resultats/profils_seuils.csv`
- `resultats/ablation_sources.csv`
- `resultats/stabilite_noeuds.csv`
- `resultats/modules_cycliques.csv`
- `resultats/monte_carlo_resume.json`
- `resultats/benchmark_stellaire_mesa.json`
- `resultats/SYNTHESE_CALIBRAGE.json`
- `resultats/RAPPORT_CALIBRAGE.md`

Le paquet ne modifie pas `hyperaretes.csv` ni `noeuds.csv`.
