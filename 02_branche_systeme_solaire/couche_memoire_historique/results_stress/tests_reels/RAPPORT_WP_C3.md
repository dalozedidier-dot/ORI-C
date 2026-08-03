# Familles alternatives de mémoire — WP-C3

Script : `stress/l_familles_memoire_wp_c3.py`. Sorties :
`l_familles_memoire_wp_c3.json`, `.csv`.

M2 place sa mémoire dans un seul mécanisme. Le WP-C3 en énumère seize et exige
que chacun reçoive une ablation, un témoin de complexité égale et une
prédiction hors échantillon.

**Sept mécanismes sont implémentables** sur LR04 et l'insolation seules. Les
neuf autres — carbone océanique, circulation, sédiments marins, poussières,
méthane et pergélisol, végétation et albédo, plateformes glaciaires,
isostasie observée, événements stochastiques rares — exigent des séries que le
dossier ne contient pas.

Structure commune, pour que la comparaison soit à structure égale. Seul le
**moteur** de l'état lent change.

## Résultats

RMSE hors échantillon, calibration 2600–1200 ka, prédiction 1200–0 ka.

| Mécanisme | Moteur | Complet | Ablation | **Apparié** | Gain / ablation | **Gain / apparié** |
|---|---|---:|---:|---:|---:|---:|
| érosion du régolithe | `\|dy\|` | 1,888 | 2,097 | **1,717** | +0,100 | **−0,100** |
| altération continentale | `cumul(y)` | 2,159 | 2,097 | **1,760** | −0,029 | **−0,226** |
| seuil de calotte | `max(y,0)` | 2,102 | 2,097 | **1,683** | −0,002 | **−0,249** |
| délais distribués | `moyenne(y)` | 2,075 | 2,097 | **1,637** | +0,011 | **−0,267** |
| isostasie | `retard(y)` | 2,075 | 2,097 | **1,637** | +0,011 | **−0,267** |
| volume de glace | `y` | 2,037 | 2,097 | **1,595** | +0,029 | **−0,277** |
| couplage état-dépendant | `y·\|dy\|` | **divergé** | 2,097 | — | — | — |

## Verdict

**Quatre mécanismes sur sept battent leur ablation.** Les gains sont faibles :
+1,1 % à +10,0 %. Le meilleur est l'érosion du régolithe.

**Zéro mécanisme sur sept bat son témoin de complexité égale.** Les gains sont
tous négatifs, de −10 % à −27,7 %. Le témoin apparié — même structure, même
nombre de paramètres, état lent piloté par le forçage externe avec une plage
d'exploitation imposée — fait mieux que le mécanisme ORI-C dans les sept cas.

C'est le même verdict que pour M2, obtenu sur sept mécanismes distincts au lieu
d'un seul. **Le problème n'est pas le choix du mécanisme de mémoire ; il est
dans le fait que la mémoire suive la réponse passée plutôt qu'un forçage
externe.**

## Deux réserves

**Le couplage état-dépendant a divergé.** Sa RMSE de 20 566 n'est pas un
résultat : l'optimiseur a trouvé une région instable et le garde-fou
d'amplitude n'a pas suffi. Ce mécanisme doit être réimplémenté avec une
saturation avant d'être compté. Il est laissé dans le tableau plutôt que
supprimé, mais il ne compte pas dans le décompte 0/7 — lequel porte donc sur
six mécanismes évalués.

**`isostasie` et `délais distribués` donnent exactement les mêmes chiffres.**
Ce n'est pas une coïncidence : dans mon implémentation, les deux emploient la
même variable auxiliaire — une moyenne glissante de la réponse. Ils ne sont pas
deux mécanismes distincts mais un seul, compté deux fois. Le décompte réel est
donc **0 sur 5 mécanismes réellement distincts**.

## Ce que le WP-C3 exigeait et qui est tenu

| Exigence | État |
|---|---|
| témoin instantané | l'ablation joue ce rôle, `beta = 0` |
| **témoin de complexité égale** | **fait**, avec plages d'exploitation publiées |
| ablation | **fait** pour les sept |
| prédiction hors échantillon | **fait**, 1200 ka jamais ajustés |
| fenêtre longue | **partiel** — 1200 ka pour des `tau_lent` ajustés jusqu'à 600 ka, soit seulement deux constantes de temps |
| variable mesurée directement | **non** — aucun des sept moteurs n'est observé, tous sont dérivés de la réponse |

Les deux dernières lignes sont des limites réelles. Le §3 du
`PROTOCOLE_DONNEES.md` demande une fenêtre longue devant **toutes** les
constantes de temps ; deux fois `tau_lent` est court. Et un mécanisme dont le
moteur n'est jamais observé directement reste une hypothèse de structure, pas
une mesure.
