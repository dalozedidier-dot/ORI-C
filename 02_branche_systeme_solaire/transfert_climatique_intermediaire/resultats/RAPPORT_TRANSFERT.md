# Transfert orbital vers une réponse climatique intermédiaire

## Ce qui est réellement testé

L'excentricité issue de l'intégration N-corps ORI-C remplace l'excentricité La2004 dans le calcul de l'insolation du 21 juin à 65° N. L'obliquité et la longitude du périhélie restent celles de La2004. Les modèles sont ajustés sur 2,6 à 0,8 Ma et évalués sans réajustement sur les 0,8 Ma les plus récentes.

Corrélation de l'excentricité N-corps avec La2004 sur 0-2,6 Ma : **0.9853**. Corrélation des insolations : **0.9978**.

## Benchmark hors échantillon

| Modèle | Variables | RMSE apprentissage | RMSE test | Corrélation test |
|---|---:|---:|---:|---:|
| etat_plus_nbody_hybride | 8 | 0.0541 | 0.0971 | 0.9769 |
| etat_plus_la2004 | 8 | 0.0541 | 0.0972 | 0.9768 |
| etat_seul | 4 | 0.0560 | 0.0993 | 0.9757 |
| astro_la2004 | 4 | 0.3032 | 0.5835 | 0.1682 |
| astro_nbody_hybride | 4 | 0.3033 | 0.5836 | 0.1664 |
| climatologie | 1 | 0.3089 | 0.5876 | 0.0000 |

## Verdict

L'ajout du forçage hybride N-corps au modèle d'état **réduit la RMSE test de 2.23 %** par rapport au modèle d'état seul. Le forçage La2004 la réduit de **2.17 %**. Les deux modèles appariés diffèrent de seulement **0.057 %** en RMSE.

La validation à origines temporelles roulantes donne un gain positif dans **3 blocs sur 3**, avec une amélioration moyenne de **3.12 %** face à l'état seul.

Ce benchmark reste une prévision à un pas utilisant l'état climatique observé aux temps précédents, pas une simulation climatique libre. La chronologie LR04 est accordée orbitalement et ne constitue donc pas une validation indépendante du forçage astronomique.

Le résultat mesure un transfert statistique intermédiaire. Il ne comprend pas une Terre-Lune résolue, une dynamique propre de rotation-obliquité, les marées, les rétroactions spatiales ou un GCM. Il ne constitue donc pas la chaîne causale complète demandée, mais fournit un banc hors échantillon apparié pour juger chaque extension future.
