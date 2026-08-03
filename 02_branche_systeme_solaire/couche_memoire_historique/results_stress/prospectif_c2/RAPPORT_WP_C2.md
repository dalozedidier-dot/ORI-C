# Test prospectif réparé — WP-C2

Script : `stress/m_prospectif_wp_c2.py`. Sorties : `PROTOCOLE_C2.json`
(protocole gelé), `prospectif_c2.json`.

Protocole scellé avant toute lecture de résultat, empreinte SHA-256
`6647085d3ca16742f3d9851a…`.

Le test prospectif d'origine était non concluant pour deux raisons de
protocole. Le WP-C2 en demande la réparation en dix items. Les dix sont
exécutés. **Le résultat reste non concluant, mais pour une raison nouvelle et
plus profonde que la précédente.**

---

## Ce qui est réparé

**Item 3 — deux entrées externes distinctes.** Le témoin d'origine employait
une seule entrée pour les deux états lents, alors que dans M2 le régolithe suit
la fraction de glace et la mémoire suit la productivité. Le témoin corrigé a
désormais une entrée par état lent.

**Item 5 — normalisation indépendante du point testé.** Chaque entrée est
calibrée sur la valeur de la variable motrice qu'elle remplace, au forçage de
référence (23,5°, e = 0,05), qui n'appartient à aucun point testé.

**Le point de référence est monostable**, vérifié : dispersion de la fraction
de glace finale **exactement nulle** sur les 24 états initiaux. La calibration
ne dépend donc pas du bassin atteint — c'est ce que l'item 5 exige, et c'est
vérifié plutôt que supposé.

| Entrée calibrée | Valeur |
|---|---:|
| régolithe ← fraction de glace | 0,9998 |
| mémoire ← productivité | 0,2636 |

**Item 1 — cartographie.** Grille de 5 obliquités × 4 excentricités, 8 états
initiaux, 120 Ma.

| Mode | Points multistables |
|---|---:|
| `classic` | 1 / 20 |
| `M2` | 2 / 20 |

**Item 6 — puissance.** L'étendue mesurée sature dès 4 états initiaux
(0,9241) et ne bouge plus à 8, 16 et 24. La puissance est suffisante : le
protocole en emploie 24.

**Item 8 — durée.** 400 Ma, soit plus de six mille fois la plus grande
constante de temps du modèle (τ_régolithe = 60).

---

## Résultats, exécution unique

| Point | Mode | Étendue de la glace finale | Multistable |
|---|---|---:|---|
| 30°, e = 0,10 | `classic` | 0,0000 | non |
| | **M2** | **0,9243** | **oui** |
| | **M2P corrigé** | **0,8586** | **oui** |
| 40°, e = 0,00 | `classic` | 0,0000 | non |
| | **M2** | **0,8690** | **oui** |
| | **M2P corrigé** | **0,8191** | **oui** |

**Le témoin corrigé est multistable lui aussi.** Aux deux points
discriminants, M2P atteint 93 % et 94 % de l'étendue de M2.

Cela confirme et renforce le seul acquis du rapport d'origine : la
multistabilité vient des **états lents**, pas du fait que ces états suivent la
réponse passée. Avec un témoin qui n'était pas apparié, on pouvait croire que
la monostabilité de M2P disait quelque chose. Avec deux entrées distinctes,
elle disparaît : le témoin devient multistable.

---

## Pourquoi le résultat reste non concluant

**La vérification d'appariement échoue.**

| Point | Rapport des plages, canal régolithe | canal mémoire | Apparié ? |
|---|---:|---:|---|
| 30°, e = 0,10 | **6,50** | 3,46 | **non** |
| 40°, e = 0,00 | **6,97** | 3,43 | **non** |

Le seuil de matérialité, fixé à 2,0 avant exécution, n'est pas tenu. Le témoin
reste mal apparié — moins gravement qu'avant, où le facteur était d'environ 40,
mais toujours au-delà de ce que le protocole déclare acceptable.

**Et la cause est une contradiction entre les items du WP-C2 lui-même.**

L'item 5 impose que la normalisation soit calibrée à un forçage de référence
**indépendant du point testé**. Or, au forçage de référence, le modèle est
entièrement englacé : la fraction de glace y vaut 0,9998. Aux deux points
discriminants, elle vaut 0,02 en médiane — le modèle y est libre de glace.

Une entrée calibrée à 0,9998 vaut donc environ cinquante fois la variable
qu'elle remplace au point où elle est employée. **Respecter l'item 5 rend
l'appariement des items 3 et 4 impossible dès que le point de référence et les
points testés se trouvent dans des régimes différents.**

C'est le même type de défaut que celui découvert dans le protocole d'origine —
une clause contradictoire dans ses propres termes — mais il porte cette fois
sur le plan directeur et non sur mon protocole antérieur.

---

## Ce qu'il faudrait pour trancher

Trois voies, aucune ne pouvant être choisie après lecture des résultats sans
violer le §XIII du plan.

1. **Calibrer par régime**, et non par point unique : une valeur de référence
   pour l'état englacé, une autre pour l'état libre de glace, chacune déclarée
   à l'avance. L'item 5 serait respecté au sens de son intention — ne pas
   ajuster sur le point testé — sans imposer une valeur hors régime.
2. **Choisir des points discriminants dans le même régime que la référence.**
   La cartographie montre qu'il en existe, mais ils sont peu nombreux : 2 sur
   20 pour M2.
3. **Abandonner l'appariement par plage** et apparier sur une autre grandeur —
   par exemple la variance temporelle du moteur plutôt que sa médiane.

Le WP-C2 doit donc recevoir un **nouvel identifiant et une nouvelle
préinscription**, ce que le §XIII autorise explicitement lorsque « l'échec
révèle un défaut précis de protocole avant consultation du résultat
confirmatoire ». La condition est remplie : le défaut est dans la clause
d'appariement, pas dans le modèle, et il est constaté par un contrôle
préenregistré.

---

## Statut des dix items

| Item | État |
|---|---|
| 1. cartographie mono/multistable | **fait** |
| 2. points discriminants | **fait**, choisis sur la carte |
| 3. appariement des variables motrices | **fait dans la structure**, échoué en valeur |
| 4. publication des plages | **fait** — c'est ce qui révèle l'échec |
| 5. normalisation indépendante du point testé | **fait**, référence vérifiée monostable |
| 6. simulation de puissance | **fait**, saturation dès 4 états |
| 7. seuils de matérialité | **fait**, 0,05 et 2,0 |
| 8. durée au-delà des constantes de temps | **fait**, 6 600 × τ_max |
| 9. protocole gelé | **fait**, empreinte SHA-256 |
| 10. exécution unique | **fait** |

Les dix items sont exécutés. **L'hypothèse testée n'est pas tranchée**, et le
protocole doit être reformulé avant toute nouvelle exécution.

## Ce que ce test établit malgré tout

Un acquis solide, indépendant de l'échec d'appariement : **`classic` est
monostable aux deux points discriminants — étendue exactement nulle — tandis
que M2 et son témoin le sont tous deux.** La multistabilité de cet EMIC réduit
est une propriété des états lents, quels qu'ils soient, et non du noyau
climatique ni de la mémoire ORI-C.
