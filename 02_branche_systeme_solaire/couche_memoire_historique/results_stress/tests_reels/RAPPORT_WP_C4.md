# Familles de modèles à budget égal — WP-C4

Script : `stress/k_familles_wp_c4.py`. Sorties : `k_familles_wp_c4.json`,
`k_familles_wp_c4.csv`.

Le verdict de la couche mémoire opposait M2 à trois modèles de **la même
famille**. Le WP-C4 demande de le confronter à des familles entièrement
différentes, à complexité, budget d'optimisation et données égales.

Sept familles concurrentes, toutes ajustées sur 2600–1200 ka et prédisant
**en roue libre** sur 1200–0 ka — sans réinjecter l'observation, exactement
comme M0 à M1P. Sans cette contrainte, les modèles autorégressifs seraient
avantagés artificiellement.

## Classement

| Rang | Famille | Paramètres | RMSE | Corrélation | BIC | Gain sur M1P |
|---:|---|---:|---:|---:|---:|---:|
| 1 | **ORI-C M1P** | 9 | **1,553** | 0,175 | 1120,7 | 0,000 |
| 2 | **persistance** | **0** | **1,720** | — | 1301,6 | −0,107 |
| 3 | retards distribués | 7 | 2,015 | 0,090 | 1731,1 | −0,297 |
| 4 | **ORI-C M2** | 9 | 2,042 | **0,260** | 1777,2 | −0,315 |
| 5 | espace d'état | 7 | 2,087 | 0,158 | 1814,8 | −0,343 |
| 6 | linéaire ARX2 | 4 | 2,093 | 0,100 | 1800,8 | −0,347 |
| 7 | ORI-C M0 | 3 | 2,095 | 0,086 | 1795,6 | −0,348 |
| 8 | seuils | 5 | 2,095 | 0,088 | 1809,9 | −0,349 |
| 9 | linéaire AR1 | 3 | 2,095 | 0,086 | 1795,9 | −0,349 |
| 10 | bilan énergétique | 3 | 2,095 | 0,087 | 1796,2 | −0,349 |
| 11 | ORI-C M1 | 6 | 2,118 | 0,086 | 1843,4 | −0,363 |

## Le résultat

**Le modèle `persistance` — `y(t) = y(0)`, zéro paramètre, aucune dynamique,
aucun forçage — se classe deuxième sur onze.** Il bat M2 de 16 %, et il bat
sept des dix autres familles, dont toutes les familles ORI-C sauf M1P.

Neuf modèles sur onze se pressent entre 2,015 et 2,118 de RMSE — un intervalle
de 5 %. Filtre linéaire, espace d'état, seuils, bilan énergétique, M0, M1, M2 :
à cette échelle, **ils font tous la même chose**, et cette chose est moins bonne
que ne rien faire.

## Ce que cela signifie

Sur la fenêtre 1200–0 ka, aucune des familles testées n'extrait de signal
prédictif exploitable du forçage astronomique. Les deux modèles en tête sont
précisément **ceux dont la trajectoire est la plus plate** : la constante, et
M1P dont l'état lent externe produit une dérive très lente.

Cela ne dit pas que le climat est imprévisible. Cela dit que **ces familles-là,
sur cette fenêtre-là, avec ce forçage-là, ne prédisent rien**, et qu'une partie
de leur RMSE apparente vient de leur agitation plutôt que de leur information.

Le §XIII du plan directeur, motif d'arrêt n° 6 : « un modèle plus simple produit
la même prédiction ». Ici un modèle plus simple produit une **meilleure**
prédiction, avec zéro paramètre.

## Le seul point où M2 se distingue

M2 a la **meilleure corrélation des onze**, 0,260 contre 0,175 pour M1P et
0,086 à 0,158 pour tout le reste. La `persistance` n'a pas de corrélation
définie — sa variance est nulle.

C'est la troisième fois que cette dissociation apparaît, après T2, T4 et
C6.2-4 : M2 capte davantage de **forme** que les autres et se trompe davantage
sur le **niveau**. Aucun des dix autres modèles ne fait mieux sur ce plan.

## Réserves

**La `persistance` n'est pas un modèle utile.** Sa bonne RMSE vient de ce que
la série standardisée reste proche de sa valeur initiale sur cette fenêtre.
Elle est ininterprétable, sans corrélation, et ne prédirait rien sur une autre
fenêtre. Son rôle ici est celui d'un **plancher** : tout modèle qu'elle bat
n'a pas justifié son existence.

**Le classement dépend de la fenêtre.** Il est établi sur 1200–0 ka avec
calibration 2600–1200. T2 a montré que le comportement de M2 change
radicalement quand la calibration porte sur 5320–2600 ka. Le WP-C4 devrait
être répété sur au moins deux découpages.

**Les familles ne sont pas toutes appariées en paramètres.** Elles vont de 0 à
9. Le BIC corrige partiellement, et il donne le même ordre que la RMSE en tête
de classement.

**Huit familles du WP-C4 ne sont pas couvertes** : modèles stochastiques, de
viabilité, réseaux causaux dynamiques, hybrides événementiels, conceptuels
glaciaires, EMIC, calotte simplifiée, émulateurs. Les quatre dernières
demandent des implémentations qui ne sont pas dans le dossier.
