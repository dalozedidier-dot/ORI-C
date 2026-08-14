# MAG-PAIR-001 — pilote technique non confirmatoire

Le pilote sert uniquement à figer les paramètres instrumentaux qui ne peuvent pas être honnêtement inventés dans le dépôt : palier AF, champ test sous-coercitif et fenêtre de température. **Aucun spécimen du pilote ne peut compter dans le test confirmatoire.**

## Entrées

- `af_sweep.csv` : balayage de niveaux AF réellement appliqués sur spécimens sacrifiables, séparément pour les deux histoires IRM.
- `test_field_sweep.csv` : champs tests réellement appliqués avec mesure du signal, du bruit instrumental et de la réécriture éventuelle de la trace.

## Décision AF

Le script propose le plus petit niveau AF **effectivement testé** où la réduction médiane de trace atteint au moins 80 % dans chacune des deux histoires. Le seuil 80 % vient du protocole confirmatoire existant. Aucune interpolation n'est autorisée.

## Décision champ test

Le script ne fabrique aucun seuil de laboratoire. Il publie, pour chaque champ réellement testé, le rapport signal/bruit et la fraction de réécriture de la trace. Le laboratoire choisit ensuite ses seuils instrumentaux avant de figer `test_field_mT`.

## Sortie

`MAG-PAIR-001.pilot-report.json` est une aide au gel, jamais une preuve scientifique. Le gate confirmatoire reste fermé jusqu'au remplissage des champs restants, empreinte de la clé aveugle et préenregistrement public.
