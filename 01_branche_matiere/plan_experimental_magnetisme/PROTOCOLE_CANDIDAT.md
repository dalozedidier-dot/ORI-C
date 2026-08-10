# Protocole candidat — mémoire magnétique assignée

**Statut : candidat non gelé. Aucun résultat expérimental n'est revendiqué.**

Ce plan est dérivé du simulateur `methodologie_puissance/puissance_conjointe_matiere.py`. Sous les hypothèses standardisées actuellement déclarées (`b_ht=1,5`, `b_tr=1,2`, rétention `0,85`, six strates, ablation sur 50 %), **n=60** est le premier point de la grille à dépasser 90 % de puissance conjointe dans 250 répétitions Monte Carlo (`0,92`). Ce n'est pas une garantie empirique ; les hypothèses doivent être stress-testées avant gel.

## Unités et assignation

- 60 unités matérielles issues d'un même lot et caractérisées avant traitement.
- 6 niveaux d'histoire assignée aléatoirement, dose zéro incluse, 10 unités par niveau.
- Mesure de trace sur la **même unité** après histoire assignée.
- Délai fixé avant réponse pour tester la persistance.
- Stimulus de réponse identique pour toutes les unités.
- Ablation physique randomisée dans chaque dose sur 50 % des unités, avec méthode choisie avant acquisition.
- Grandeur négative physique mesurée sur les mêmes unités et attendue insensible à l'histoire.

## Règle de succès candidate

Le verdict ne dépend pas d'une corrélation isolée : tous les maillons histoire→trace, trace→réponse, persistance et effet d'ablation doivent réussir, ainsi qu'une robustesse de signe par retrait d'une strate. La version confirmatoire devra reprendre exactement les critères C-MAT-MEM applicables et geler le pipeline, le SESOI, la puissance et le critère d'arrêt avant mesure.

## Avant scellement

1. porter la simulation à au moins 5 000 répétitions par n ;
2. balayer une grille d'effets plus faibles que le scénario central ;
3. choisir le matériel et l'instrumentation réels ;
4. déterminer l'ablation physiquement appropriée sans confondre effacement de trace et destruction de l'échantillon ;
5. geler le protocole seulement après ces étapes.
