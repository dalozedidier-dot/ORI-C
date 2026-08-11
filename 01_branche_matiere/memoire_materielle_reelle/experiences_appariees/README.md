# Trois expériences matérielles appariées

Ces protocoles sont des plans expérimentaux exécutables, pas des résultats. Une
chaîne n'est déclarée confirmatoire qu'après acquisition de mesures réelles sur
les mêmes unités : `histoire -> trace -> persistance -> réponse -> ablation`.

Les trois plans imposent : randomisation bloquée, mesure de trace distincte de
la réponse, ablation réelle et factice, évaluateur aveugle, identifiant stable de
l'unité, exclusions gelées et conservation des données brutes. Le script
`valider_protocoles.py` refuse une fiche qui omet un de ces éléments.

1. `MAG-PAIR-001.json` : rémanence magnétique, démagnétisation et lecture finale.
2. `PLAST-PAIR-001.json` : précyclage, trace microstructurale, recuit de récupération et rechargement.
3. `POLY-PAIR-001.json` : vieillissement, trace chimique, traitement d'effacement et essai mécanique.

Une exécution physique reste nécessaire. Le dépôt ne transforme pas ces plans en
« expériences réalisées » tant que les tables conformes au schéma et les données
brutes ne sont pas déposées.
