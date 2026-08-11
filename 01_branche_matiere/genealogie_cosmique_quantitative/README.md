# Généalogie cosmique quantitative — de la nucléosynthèse stellaire à l’architecture du Système solaire

Cette couche prolonge la généalogie qualitative `../genealogie/genealogie_matiere.csv` sans la réécrire. Son objectif est de traiter comme un **problème de transmission historique vérifiable** la chaîne allant de la production stellaire des constituants au Système solaire actuel.

La thèse testée n’est pas qu’une chronologie existe. La question ORI-C est plus stricte : **une transformation antérieure laisse-t-elle une inscription matérielle, chimique, isotopique ou architecturale qui modifie ce qui devient accessible ensuite ?**

La couche distingue cinq modes de preuve : échantillon direct, observation astronomique, reconstruction isotopique/géochronologique, expérience/thermodynamique et simulation. Une simulation ne devient jamais une observation; un analogue extrasolaire ne devient jamais une mesure du disque solaire disparu.

## Résultat central de cette version

La chaîne est documentée sur 23 stades de `GC-001` à `GC-023`. Plusieurs mécanismes de transmission historique disposent de preuves indépendantes fortes, notamment les grains présolaires conservés dans des matériaux primitifs, l’héritage de glaces dans un disque analogue, les hétérogénéités isotopiques du disque solaire, l’effet du temps d’accrétion et du 26Al sur le destin thermique, et la transition de concentrations de solides vers des planétésimaux dans les simulations.

Le **raccordement quantitatif unique** d’un scénario de formation planétaire aux conditions initiales J2000 utilisées par C-AST reste explicitement **ouvert**. La branche ne revendique donc pas une preuve end-to-end « nucléosynthèse → architecture actuelle ».

## Exécution

```bash
python 01_branche_matiere/genealogie_cosmique_quantitative/run_all.py
python -m pytest -q 01_branche_matiere/genealogie_cosmique_quantitative/tests
```

Les sorties se trouvent dans `resultats/` et sont couvertes par `RESULTATS.sha256`.
