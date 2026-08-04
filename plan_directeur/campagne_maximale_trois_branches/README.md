# Campagne maximale sur les trois branches

Cette campagne exécute les contrôles supplémentaires qui peuvent être menés avec les données déjà présentes dans le dépôt. Elle couvre séparément la matière, le Système solaire et la Terre, puis le vivant.

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

## Limites

La campagne ne possède toujours ni données réelles de lignées prébiotiques, ni jeu antibiotique confirmatoire externe, ni ensemble climatique interventionnel indépendant, ni stocks opératoires pour les éléments autres que l'azote. Ces absences bornent les conclusions, même lorsque tous les scripts s'exécutent correctement.
