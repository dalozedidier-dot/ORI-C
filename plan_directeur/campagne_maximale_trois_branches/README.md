# Synthèse intégrée des campagnes sur les trois branches

Le nom du répertoire est historique et reste inchangé pour préserver les chemins
des workflows. Le runner ne se présente plus comme le « maximum possible avec
les données du dépôt ». Il exécute ses contrôles historiques, puis importe les
résultats versionnés des campagnes plus récentes : D'Onofrio, lignées de
vésicules et mémoire matérielle réelle.

Elle ne complète aucune donnée manquante par estimation implicite. Les sorties sont classées comme structurelles, descriptives, exploratoires ou validées dans un modèle réduit. Aucun résultat n'est automatiquement converti en soutien général à ORI-C.

## Exécution

```bash
python plan_directeur/campagne_maximale_trois_branches/run_all.py
python -m pytest -q plan_directeur/campagne_maximale_trois_branches/tests
```

Les sorties sont écrites dans `resultats/` :

- `matiere_robustesse.json`
- `systeme_solaire_robustesse.json`
- `vivant_robustesse.json`
- `synthese_trois_branches.json`
- `RAPPORT_CAMPAGNE_MAXIMALE.md`

## Matière

- suppression successive des 53 hyperarêtes
- suppression successive des nœuds
- ablation des familles de processus
- retrait un par un des coefficients de partage métal-silicate
- audit de complétude de la base des 40 transitions
- intégration des preuves relationnelles partielles de mémoire matérielle
- conservation du verdict négatif de transversalité `C-MAT-MEM-05`

## Système solaire et Terre

- symétrie et non-linéarité des interventions appariées
- sensibilité des bandes de 95 et 125 ka
- séparation entre effets interventionnels et erreurs numériques sélectionnées
- perte de phase face à La2010 selon l'horizon
- localisation de la puissance de 100 ka non reproduite
- persistance sur palier long du test exoplanétaire

## Vivant

- validation croisée groupée par lignée
- ablation de la pente historique
- prédiction de la dernière transition observée
- exclusion successive de chaque dose
- permutation de l'ordre historique
- diversité et changement de composition des séquences ARN suivies
- contrôle exécutable du schéma de lignées prébiotiques synthétique
- intégration du résultat D'Onofrio contre l'état seul et l'histoire mélangée
- intégration des quatre composantes préenregistrées des lignées de vésicules

## Limites

La synthèse ne constitue pas un méta-test homogène entre domaines. Les données
D'Onofrio et vésicules sont réelles et positives dans leurs protocoles propres,
mais demandent encore des réplications externes indépendantes. La mémoire
matérielle contient plusieurs relations positives, sans trois familles admises
portant la chaîne complète. L'ensemble climatique interventionnel indépendant
et les stocks opératoires hors azote restent également absents.
