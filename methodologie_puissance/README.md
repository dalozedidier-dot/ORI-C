# Puissance statistique a priori dans ORI-C

Ce module impose une discipline commune aux nouveaux protocoles. Il ne recalcule pas une puissance après avoir vu le résultat. Il demande, avant l’acquisition ou avant l’ouverture du jeu tenu à l’écart, quel effet le protocole cherche et quelle probabilité il possède de le détecter si cet effet existe.

## Déclaration obligatoire

Tout nouveau protocole promu par `FOCUS_PROGRAMME.md` doit posséder un fichier `POWER_PLAN.json` gelé avec le protocole. Ce plan déclare :

- le SESOI, avec une justification scientifique ;
- `alpha` et la puissance cible ;
- l’unité réellement indépendante ;
- la taille disponible ou la grille de tailles à étudier ;
- l’origine de l’estimation du bruit ;
- la métrique principale et le test exact ;
- les témoins appariés ;
- la règle conjointe de succès ;
- l’adaptateur qui réexécute le pipeline complet ;
- la graine et le nombre de simulations.

Un fold de validation croisée n’est jamais accepté comme unité indépendante. Les unités possibles sont par exemple une souche, une lignée, une expérience, un groupe entièrement laissé hors apprentissage ou un jeu externe.

## Simulation du pipeline réel

Le moteur commun ne fabrique pas directement des différences normales de MAE ou de RMSE. L’adaptateur du protocole reçoit une graine, le plan, le nombre d’unités indépendantes et l’effet injecté. Il doit ensuite :

1. simuler les observations ou trajectoires avec leur structure de groupe et leur dépendance temporelle ;
2. réexécuter l’apprentissage et la validation croisée groupée ;
3. réexécuter les ablations, témoins de même complexité et permutations du protocole ;
4. retourner chaque critère préenregistré sous forme booléenne.

La puissance principale est la proportion de simulations où tous les critères de `success_rule` réussissent simultanément. Le JSON de sortie fournit aussi la fréquence de réussite de chaque critère séparé.

## Effets pris en charge

Le plan distingue quatre formes :

- `absolute_difference` ;
- `relative_improvement`, convertie avec la valeur de référence déclarée ;
- `standardized_difference`, convertie avec l’échelle déclarée ;
- `ratio_to_numerical_noise`, converti avec le bruit numérique déclaré.

Ainsi, une amélioration relative de 5 % sur une RMSE de référence de 0,80 devient une différence absolue de 0,04. Les exemples de seuils ne deviennent jamais des règles communes. Chaque SESOI doit être justifié par le changement scientifiquement utile dans le protocole concerné.

## Recherche de la taille ou de l’effet nécessaire

`scan-n` explore une grille de tailles. Une première passe localise les candidats, puis au moins 10 000 simulations confirment les tailles proches du seuil. La taille retenue est la plus petite dont la borne inférieure de l’intervalle de Wilson atteint la puissance cible.

Lorsque la taille est déjà fixée, `mde` cherche le plus petit effet détectable sur une grille préenregistrée avec la même règle sur la borne inférieure de Wilson.

## Commandes

Depuis la racine du dépôt :

```bash
python methodologie_puissance/power_monte_carlo.py validate methodologie_puissance/exemple_power_plan.json
python methodologie_puissance/power_monte_carlo.py validate-all .
python methodologie_puissance/power_monte_carlo.py estimate PLAN/POWER_PLAN.json --output PLAN/resultats/power.json
python methodologie_puissance/power_monte_carlo.py scan-n PLAN/POWER_PLAN.json --output PLAN/resultats/power_n.json
python methodologie_puissance/power_monte_carlo.py mde PLAN/POWER_PLAN.json --output PLAN/resultats/power_mde.json
```

Les sorties sont écrites atomiquement en JSON. Elles contiennent les empreintes SHA-256 du plan et de l’adaptateur, la graine, le nombre de simulations, la puissance conjointe, l’intervalle de Wilson et le taux de réussite de chaque critère.

`exemple_power_plan.json` et `examples/grouped_demo_adapter.py` servent uniquement à montrer l’interface. Ils ne portent aucun résultat scientifique.
