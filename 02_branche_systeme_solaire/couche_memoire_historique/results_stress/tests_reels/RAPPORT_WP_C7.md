# Recherche de mécanismes nouveaux — WP-C7

Script : `stress/j_mecanismes_wp_c7.py`. Sorties : `j_mecanismes_wp_c7.json`,
`j_fenetres_wp_c7.csv`.

« Utiliser l'échec de M2 pour localiser les résidus structurés. » Ce rapport ne
propose aucun modèle nouveau : il dit ce qu'un modèle nouveau devrait
expliquer.

---

## C7.1 — Où est le signal manquant : dans la bande de 100 ka, pour les quatre

Part de la puissance du **résidu** par bande, fenêtre de prédiction :

| Modèle | 41 ka | **100 ka** | σ du résidu | n_eff |
|---|---:|---:|---:|---:|
| M0 | 0,091 | **0,383** | 1,529 | 17,6 |
| M1 | 0,080 | **0,394** | 1,533 | 17,6 |
| **M2** | **0,026** | **0,412** | 1,481 | 18,1 |
| M1P | 0,086 | **0,383** | 1,509 | 18,5 |

**La bande de 100 ka est entièrement dans le résidu, pour les quatre modèles.**
Aucun n'en absorbe quoi que ce soit — les parts résiduelles sont toutes autour
de 38–41 %, exactement la part que l'observation y met (0,394 en C6.5).

M2 se distingue sur l'autre bande : son résidu ne contient que **2,6 %** de
puissance à 41 ka, contre 8–9 % pour les trois autres. **M2 absorbe
l'obliquité mieux que les autres et ne touche pas au 100 ka.**

C'est la localisation la plus précise que la campagne ait produite : le
mécanisme manquant doit produire la bande de 100 ka sans dégrader la
restitution de l'obliquité.

---

## C7.2 — La dissociation existe, mais pas là où on la cherchait

Régression glissante de l'observé sur le prédit, fenêtres de 200 ka, pas
de 25 ka, 40 fenêtres.

| Modèle | Corrélation médiane | Pente médiane | Fenêtres à corrélation > 0,5 |
|---|---:|---:|---:|
| M0 | +0,103 | 0,596 | **0 / 40** |
| M1 | +0,075 | 0,348 | **0 / 40** |
| **M2** | **+0,260** | **0,765** | **0 / 40** |
| M1P | +0,110 | 0,588 | **0 / 40** |

**Aucune fenêtre, pour aucun modèle, n'atteint une corrélation de 0,5.** La
dissociation « forme correcte, amplitude fausse » que T2 et T4 suggéraient ne
se vérifie **pas** à l'échelle de 200 ka : à cette échelle, aucun modèle ne
capte la forme.

Ce que M2 a de mieux est réel mais modeste : corrélation médiane de 0,260
contre 0,075 à 0,110, et pente médiane de 0,765 — la plus proche de 1. Les
quatre pentes sont inférieures à 1, c'est-à-dire que **tous les modèles
sous-amplifient**.

Je corrige donc ma lecture antérieure. La dissociation observée en T2 et T4
portait sur des statistiques globales — rapport spectral, corrélation sur toute
la fenêtre. Elle n'est pas une propriété locale : M2 ne réussit pas la forme
sur des tronçons puis n'échoue que sur le gain.

---

## C7.3 — Le correctif manquant est une échelle, pas une condition

Quatre formes emboîtées, comparées par BIC : brut, additif, affine, et
conditionnel — le gain multiplié par un état lent, ce qui est l'hypothèse du
§13.4 du CODEBOOK.

| Modèle | Forme retenue | Gain de RMSE |
|---|---|---:|
| M0 | affine | +0,273 |
| M1 | **conditionnel** | +0,286 |
| **M2** | **affine** | **+0,277** |
| M1P | additif | +0,029 |

**Pour M2, le BIC retient la forme affine** — une échelle et un décalage — et
non la forme conditionnelle. Un simple recalibrage de gain récupère **27,7 %**
de RMSE.

Deux conséquences.

**L'hypothèse du §13.4 n'est pas sélectionnée pour M2.** L'idée qu'une variable
lente modifie l'opérateur de réponse est séduisante et le cadre la met en
avant ; sur ces données, elle ne bat pas une simple remise à l'échelle. Elle
n'est retenue que pour M1, qui n'a pas d'état lent — ce qui suggère qu'elle y
compense l'absence de mémoire plutôt qu'elle n'y révèle une architecture.

**M1P n'a presque rien à corriger** : +2,9 % seulement, et par un simple
décalage. Son échelle est déjà bonne. C'est cohérent avec sa première place en
RMSE et sa calibration à 88,5 %.

---

## C7.4 — L'opérateur change de régime, pour les quatre modèles

Paramètres réajustés séparément avant et après la transition du Pléistocène
moyen.

| Modèle | Écart relatif max | Stable entre régimes |
|---|---:|---|
| M0 | 1,845 | **non** |
| M1 | 0,971 | **non** |
| M2 | 0,939 | **non** |
| M1P | 1,965 | **non** |

Les paramètres varient de 94 % à 197 % entre les deux régimes. **Aucun modèle
n'a d'opérateur constant sur 2,6 Ma.**

C'est le constat que le §13.4 prédit — l'histoire transforme la loi de réponse
— mais il ne l'appuie pas : **M0, avec trois paramètres et aucune mémoire,
dérive davantage que M2**. Une dérive commune aux quatre structures ne
distingue pas le mécanisme ORI-C ; elle dit que la forme fonctionnelle
elle-même est inadéquate, quelle qu'elle soit.

---

## Ce que le WP-C7 établit

| Point | Constat |
|---|---|
| Où chercher | la bande de **100 ka**, absente du prédit de tous les modèles et présente à 38–41 % dans tous les résidus |
| Ce que M2 apporte déjà | la meilleure absorption de l'obliquité — résidu à 2,6 % contre 8–9 % |
| Ce qui manque à M2 | une **échelle**, pas une condition : +27,7 % de RMSE par simple correction affine |
| Ce qui n'est pas soutenu | l'hypothèse « une variable lente modifie l'opérateur » n'est pas sélectionnée par BIC pour M2 |
| Ce qui est commun aux quatre | dérive des paramètres entre régimes de 94 % à 197 % |

## Items non couverts

C7.5 — changements d'architecture plutôt qu'un noyau fixe — et C7.6 — ruptures
de connectivité entre bassins — demandent d'écrire de nouveaux modèles, ce que
le WP-C7 ne fait pas par construction : il localise, il ne propose pas.

C7.8 et C7.9 — générer des prédictions divergentes et chercher les données qui
trancheraient — supposent qu'une famille candidate ait été retenue. Aucune ne
l'est.

C7.10 est en revanche déclenché : la forme actuelle de M2 a échoué sur deux
jeux confirmatoires indépendants — la fenêtre 1200 ka et la fenêtre 2600 ka —
et le WP-C6 y ajoute la non-identifiabilité de ses paramètres.
