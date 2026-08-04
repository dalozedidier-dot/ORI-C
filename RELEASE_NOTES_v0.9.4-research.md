# ORI-C v0.9.4-research

Cette version conserve l’architecture matérielle v0.9.3 comme référence gelée et ajoute un calibrage reproductible des 53 hyperarêtes.

## Ajouts

- séparation de la solidité documentaire et de la fonction structurelle ;
- ablation unitaire des 53 hyperarêtes ;
- ablation groupée des 31 sources ;
- cinq profils de seuils documentaires ;
- 4 000 tirages déterministes de stress limités aux six relations les moins documentées ;
- classement de 31 nœuds stables, 15 nœuds sensibles et 7 nœuds appartenant au verrou canonique ;
- identification de `H011` comme priorité documentaire majeure hors du verrou hydrothermal ;
- benchmark externe sur deux trajectoires stellaires MESA, 14 nœuds sur 14 atteignables en fermeture stricte ;
- cinq nouveaux tests de régression ;
- workflows CI, structure et release mis à jour.

## Limites

Le calibrage ne transforme pas une relation critique dans le graphe en causalité démontrée. La nécessité empirique, la suffisance, la temporalité quantitative, la réversibilité physique et les interventions directes restent à mesurer.
