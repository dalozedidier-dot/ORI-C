# Tests sur données réelles — première batterie

Script : `stress/f_tests_reels.py`. Sorties : `f_tests_reels.json`,
`t2_enregistrement_complet.csv`, `t4_chronologie_spectrale.csv`.

Quatre tests exploitant des données présentes dans le dossier mais jamais
utilisées : l'étendue complète de LR04 (5,32 Ma au lieu de 2,6), sa colonne
d'erreur publiée, et les quatre solutions orbitales La2010.

Tous comparent M2 à **M1P**, témoin de complexité égale — même nombre de
paramètres, état lent piloté par un forçage externe et non par la réponse
passée.

---

## T1 — Plancher d'incertitude de l'archive

LR04 publie une colonne `d18O_error` que le protocole n'avait jamais lue. Un
gain de RMSE inférieur à cette erreur ne peut pas être attribué au modèle.

| Modèle | RMSE hors échantillon |
|---|---:|
| M0 | 2,094 |
| M1 | 2,118 |
| M2 | 2,042 |
| **M1P** | **1,553** |

Erreur publiée, ramenée à l'échelle standardisée : moyenne 0,201, médiane 0,183.

| Quantité | Valeur |
|---|---:|
| Gain absolu de M2 sur M1 | 0,076 |
| Rapport gain / incertitude | **0,377** |
| Gain absolu de M2 sur M1P | **−0,489** |

**Verdict.** Le gain de M2 sur M1 vaut 0,38 fois l'incertitude propre de
l'archive : il n'est pas interprétable, quel que soit son signe. Le déficit de
M2 contre le témoin apparié vaut 2,4 fois cette incertitude : celui-là est
au-dessus du plancher et doit être retenu.

C'est un critère nouveau. Les tests antérieurs comparaient des modèles entre
eux ; celui-ci compare l'effet à l'incertitude des données.

---

## T2 — L'enregistrement complet, transition entièrement hors échantillon

Calibration sur 5,32–2,6 Ma (2701 points), prédiction sur 2,6–0 Ma (2600
points). La transition du Pléistocène moyen est ici **entièrement** hors
échantillon, ce que la fenêtre 2,6–1,2 Ma du protocole ne permettait pas.

| Modèle | RMSE | Corrélation | Rapport 100/41 | n_eff |
|---|---:|---:|---:|---:|
| M0 | 3,874 | 0,427 | 0,032 | 25,9 |
| M1 | 4,267 | 0,388 | 0,041 | 25,0 |
| **M2** | **6,757** | **0,522** | **1,695** | **7,4** |
| M1P | 2,767 | 0,489 | 0,030 | 28,8 |

Observé : rapport 100/41 = 1,290.

Gains relatifs de M2, bootstrap par blocs mobiles (longueur 170, 20 000
tirages) :

| Référence | Gain | IC 95 % |
|---|---:|---|
| contre M1 | −0,583 | [−0,812 ; −0,132] |
| contre **M1P** | **−1,442** | **[−1,789 ; −0,810]** |

**Verdict, deux lectures qu'il faut donner ensemble.**

*Contre M2.* C'est le pire des quatre modèles en RMSE. Le déficit contre le
témoin apparié est franc et son intervalle ne s'approche pas de zéro. Sur le
critère préenregistré — RMSE hors échantillon — M2 est réfuté, plus nettement
que sur la fenêtre courte.

*Pour M2.* C'est le **seul** modèle qui produit un rapport 100/41 supérieur à
1. Les trois autres restent à 0,03, c'est-à-dire un monde purement obliquité.
M2 est aussi le mieux corrélé à l'observation.

M2 produit donc le bon **caractère spectral** et la mauvaise **amplitude**. Son
n_eff de 7,4 contre 25–29 dit la même chose autrement : ses résidus sont
massivement autocorrélés, il dérive. Cette dissociation entre spectre et niveau
n'était pas visible sur la fenêtre courte, où tous les modèles échouaient
ensemble.

**Cela ne convertit pas le verdict.** Le critère préenregistré est la RMSE. Un
modèle qui reproduit une signature en dégradant la prédiction reste réfuté sur
ce critère. La dissociation est un fait à documenter, pas un résultat positif.

---

## T3 — Plancher de dispersion orbitale

Quatre solutions La2010 (a, b, c, d), toutes également admissibles, comparées
sur 2601 ka.

| Quantité | Valeur |
|---|---:|
| Excentricité moyenne | 0,0276 |
| Dispersion moyenne | 1,44 × 10⁻⁵ |
| Dispersion maximale | 1,06 × 10⁻⁴ |
| **Dispersion relative moyenne** | **5,19 × 10⁻⁴** |

**Verdict.** Le plancher astronomique est trois ordres de grandeur sous les
effets discutés. Contrairement à T1, ce test ne disqualifie rien : il **ferme
une objection**. Aucun résultat de ce dossier n'est menacé par l'indétermination
de la solution orbitale.

---

## T4 — Chronologie spectrale, et un critère préenregistré défectueux

Rapport de puissance 100/41 ka en fenêtre glissante de 800 ka, pas de 50 ka,
sur 5,32 Ma.

### Le critère préenregistré n'est pas utilisable

Le critère annoncé était la **date de premier franchissement du rapport 1**.
Appliqué à l'observation elle-même, il échoue : **LR04 franchit 1 six fois** —
à 4350, 3600, 3450, 2050, 1850 et 1150 ka — parce que le rapport oscille
autour de 1 pendant tout le Pliocène. « Le premier franchissement » n'est pas
une quantité définie sur cette série.

Le défaut est dans mon protocole, pas dans les modèles. **Aucun verdict n'est
tiré de T4.**

### Ce que la sortie montre néanmoins, à titre descriptif

Ces quantités sont **post hoc et non préenregistrées**. Elles décrivent, elles
ne tranchent pas.

| Série | Rapport maximal | Demi-maximum atteint à | Pearson avec LR04 | Spearman |
|---|---:|---:|---:|---:|
| LR04 | 6,63 | 750 ka | — | — |
| M0 | 0,32 | 4300 ka | −0,092 | +0,026 |
| M1 | 1,02 | 3250 ka | −0,013 | +0,168 |
| **M2** | **15,75** | **900 ka** | **+0,859** | **+0,347** |
| M1P | 0,38 | 4250 ka | −0,115 | −0,007 |

Trois observations, avec leurs réserves.

1. **M0, M1 et M1P ne produisent jamais de monde à 100 ka.** Leurs maxima
   plafonnent à 0,32–1,02 sur 5,32 Ma. Le témoin apparié, en particulier, n'y
   parvient pas : ce que M2 fait ici, M1P ne le fait pas du tout.
2. **M2 place son basculement à peu près où il faut** — demi-maximum à 900 ka
   contre 750 ka observés — mais **avec une amplitude 2,4 fois trop forte**
   (15,75 contre 6,63).
3. **Le Pearson de +0,859 est trompeur pris seul.** Il est porté par la montée
   commune des dernières fenêtres. Le Spearman, insensible à l'échelle, tombe à
   +0,347 : l'accord de rang est modeste. C'est le second chiffre qui doit être
   cité.

Ces trois points sont cohérents avec T2 : M2 possède un mécanisme qui produit
la bonne signature au bon moment, et le calibre mal.

---

## Ce que la batterie établit

| | Établi |
|---|---|
| T1 | Le gain de M2 sur M1 est sous le plancher d'incertitude de l'archive et n'est pas interprétable. Son déficit contre le témoin apparié est au-dessus de ce plancher. |
| T2 | Avec la transition entièrement hors échantillon, M2 est le pire modèle en RMSE, gain −1,44 contre M1P, IC [−1,79 ; −0,81]. Il est en même temps le seul à produire le rapport 100/41. |
| T3 | L'indétermination orbitale est trois ordres de grandeur sous les effets discutés. Elle ne menace aucun résultat. |
| T4 | Critère préenregistré défectueux, aucun verdict. Descriptivement, M0, M1 et M1P ne produisent jamais de monde à 100 ka ; M2 le produit, au bon moment, avec une amplitude 2,4 fois trop forte. |

## Ce que la batterie ne change pas

Le verdict de la couche mémoire historique reste **négatif** : 1/5 contre M1,
0/5 contre M1P. T1 et T2 le renforcent sur deux critères nouveaux et
indépendants — l'incertitude propre des données, et une fenêtre où la
transition est entièrement hors échantillon.

La dissociation entre signature spectrale et amplitude, visible en T2 et T4,
est un fait nouveau qui n'appuie aucune revendication en l'état. Elle indique
où chercher, pas ce qui est démontré.
