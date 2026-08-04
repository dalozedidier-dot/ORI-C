# Benchmark antibiotique externe Card 2019

## Données

Série Ara+5 du LTEE, tétracycline, 130 mesures appariées parent-descendant. Les identifiants 0.5, 1, 1.5, 2, 5 et 10 correspondent à des milliers de générations. L'évolvabilité est `log2(MIC fille) - log2(MIC parent)`.

## Test temporel

Apprentissage jusqu'à 2 000 générations. Évaluation hors échantillon sur 5 000 et 10 000 générations.

- meilleur modèle : **moyenne_apprentissage** ;
- RMSE du modèle état présent seul : **0.9292** ;
- RMSE état + histoire : **2.2244** ;
- gain de l'histoire sur l'état seul : **-139.39 %** ;
- différence de RMSE histoire moins état : **1.2952** ;
- intervalle bootstrap groupé à 95 % : **[0.5177, 1.7918]**.

Le modèle historique est moins bon dans les quatre groupes de test. Sur 10 000 rééchantillonnages groupés, aucun ne donne une RMSE historique inférieure à celle de l'état seul.

## Verdict

Ce jeu est indépendant des données Windels et fournit une vraie séparation temporelle. Il reste **rétrospectif** car le protocole a été construit après accès au jeu. Il qualifie l'instrument et ne compte pas comme confirmation prospective d'ORI-C.
