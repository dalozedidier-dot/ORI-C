# Résultats de la validation scientifique maximale

Date d’exécution : 29 juillet 2026

## Portée du calcul

- 25 jobs terminés sans échec d’exécution
- 6,11 heures-cœur cumulées
- témoin rétrospectif de 20 millions d’années
- huit planètes dans le témoin long
- contrôle séparé à quatorze corps avec Pluton et cinq astéroïdes
- huit trajectoires perturbées de \(10^{-10}\) radian sur 10 Myr
- six interventions architecturales sur 2 Myr
- relativité REBOUNDx, WHFast et IAS15
- références indépendantes JPL Horizons DE441 et La2010a–d

Le protocole préenregistré réussit 13 critères sur 15.

## Accord avec des références indépendantes

### JPL Horizons DE441

Sur 6 000 ans, l’excentricité du barycentre Terre–Lune atteint :

- corrélation : `0,9999998095`
- RMSE : `4,826436 × 10⁻⁷`
- erreur absolue maximale : `2,023288 × 10⁻⁶`

### La2010a

| Horizon | Corrélation | RMSE |
|---:|---:|---:|
| 100 kyr | 0,999971 | 0,000114 |
| 500 kyr | 0,998760 | 0,000678 |
| 1 Myr | 0,997270 | 0,000947 |
| 2 Myr | 0,991424 | 0,001777 |
| 5 Myr | 0,942333 | 0,004406 |
| 10 Myr | 0,826740 | 0,007725 |
| 20 Myr | 0,495006 | 0,013244 |

La baisse de corrélation à long terme mesure surtout la perte de phase dans un
système chaotique. Elle ne supprime pas l’accord spectral.

## Bandes d’excentricité sur 20 Myr

| Bande | Pic calculé | Pic La2010a | Puissance calculée / La2010a |
|---:|---:|---:|---:|
| 95 kyr | 95 243 ans | 95 243 ans | 0,961 |
| 125 kyr | 124 230 ans | 125 006 ans | 1,026 |
| 405 kyr | 408 184 ans | 408 184 ans | 1,007 |
| 2,4 Myr | 2 000 100 ans | 2 222 333 ans | 1,363 |

La bande longue réussit la tolérance préenregistrée de 20 %, mais sa période
reste moins bien reproduite que les bandes de 95, 125 et 405 kyr.

## Contrôles numériques et physiques

| Comparaison | Corrélation | RMSE |
|---|---:|---:|
| WHFast, pas 0,01 contre 0,005 an sur 2 Myr | 0,999999998 | \(8,43\times10^{-7}\) |
| WHFast, pas 0,005 contre 0,0048828125 an | 0,999999992 | \(1,73\times10^{-6}\) |
| WHFast contre IAS15 sur 20 kyr | 0,999999930 | \(3,13\times10^{-7}\) |
| `gr_potential` contre `gr_full` sur 20 kyr | 0,999999872 | \(4,27\times10^{-7}\) |
| avec contre sans relativité sur 2 Myr | 0,903217 | 0,005969 |
| Horizons contre éléments approximatifs | 0,987630 | 0,002175 |
| huit planètes contre quatorze corps | 0,999999924 | \(5,28\times10^{-6}\) |

Tous les corps restent liés dans tous les jobs. La dérive énergétique maximale
vaut \(1,33\times10^{-11}\).

## Deux critères échoués

1. L’aller-retour sur 100 kyr au pas 0,01 an atteint une erreur relative
   maximale de \(2,76\times10^{-5}\), au-dessus du seuil \(10^{-5}\). Le pas
   0,005 an atteint \(7,54\times10^{-6}\) et réussit, ce qui montre la
   convergence attendue.
2. Le moment angulaire mécanique newtonien du job `gr_full` atteint
   \(5,28\times10^{-10}\), au-dessus du seuil \(10^{-10}\). `gr_full` est un
   modèle 1PN dépendant des vitesses. Le diagnostic exporté n’est pas son
   invariant canonique 1PN complet. Tous les autres jobs restent sous
   \(4,33\times10^{-12}\). L’échec est conservé parce que le seuil avait été
   fixé avant le calcul.

## Sensibilité et interventions

La dispersion RMS des huit conditions quasi identiques sur les deux premiers
Myr vaut \(1,37\times10^{-9}\). Le temps d’e-folding descriptif vaut environ
3,01 Myr, avec \(R^2=0,937\).

Les six interventions sur Jupiter et Saturne donnent des RMSE comprises entre
0,00859 et 0,01893. Elles dépassent le plancher de l’ensemble par des facteurs
de 6,27 à 13,83 millions.

Cela démontre une causalité numérique à l’intérieur du modèle. Cela ne démontre
pas que ces architectures alternatives ont existé.

## Limite de précision

À 1 Myr, la RMSE du modèle réduit vaut environ 2 858 fois la dispersion moyenne
entre La2010a–d. Le modèle suit donc très bien la phase séculaire et les bandes
principales, mais n’atteint pas la précision interne d’une solution La2010.

Le calcul ne résout pas explicitement la Lune, le J2 solaire, les marées,
l’obliquité dynamique, la rotation terrestre ni une archive géologique
indépendante. Il valide le mécanisme astronomique réduit, pas encore le cadre
général ORI-C contre des données géologiques hors échantillon.
