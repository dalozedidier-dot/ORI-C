# Protocole sourcé — carte temporelle contre chronologie

Hypothèses visées : H-S-004 et H-M-001.

La revue ORI-C identifie les réseaux temporels et d'ordre supérieur comme moyens de distinguer ordre, mémoire et structure. Les sources primaires retenues pour le protocole sont les notices arXiv 1108.1780, 1409.1805, 2004.12784 et la revue 2203.06601. Elles justifient l'usage d'un ordre temporel explicite et la comparaison avec des modèles sans mémoire ; elles ne valident pas ORI-C.

## Test

Une transition cible est entièrement laissée hors apprentissage. Tous ses liens entrants possibles depuis le passé constituent le jeu test. Le témoin donne un score uniquement par distance chronologique. Le modèle augmenté ajoute les seuls attributs ORI-C actuellement disponibles sans lire le lien : identité de régime et distance entre régimes.

La métrique primaire est l'AUC agrégée hors nœud. L'apport ORI-C exige une différence positive contre la chronologie et un test de permutation unilatéral des régimes inférieur à 0,05. Une absence de gain maintient la carte au statut descriptif.

Cette analyse reste conservatrice : les régimes sont eux-mêmes fortement liés à la chronologie. Un futur test ne deviendra vraiment indépendant qu'après ajout préenregistré d'attributs non chronologiques (mécanisme causal, flux d'énergie, fermeture, persistance, nécessité/suffisance et accessibilité).

