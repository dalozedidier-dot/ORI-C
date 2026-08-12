# EXO-DOM-01 — intervention directe sur la trace `m` dans le modèle exoplanétaire

## Statut

Ce test est **exploratoire au niveau modèle** (`E4_modele`). Il est gelé pour les réexécutions futures, mais il n'est pas présenté comme préenregistré : le modèle M2, ses paramètres et ses résultats antérieurs étaient déjà connus au moment de sa définition.

## Question

Le test isole explicitement la trace lente `m` du reste de l'état. Pour chaque histoire contrôlée A et B, on conserve exactement le même état rapide `X`, la même architecture dynamique et le même forçage futur `Theta`. La seule opération est :

```text
do(m) : (regolith_fraction, carbon_memory) -> (0.5, 0.5)
```

Les valeurs `(0.5, 0.5)` ne sont pas choisies après observation du résultat : ce sont les références déjà utilisées par le mode `ablated` du modèle existant. Après l'intervention ponctuelle, les deux variables lentes évoluent à nouveau normalement sous M2.

## Appariement

`X = (temperature_k, ice_fraction, co2_ppm, productivity)` est pris à la fin de chacune des deux histoires de 50 Ma. Pour le contrôle et `do(m)`, `X` est identique par construction. Les équations, paramètres et 25 challenges futurs sont également identiques. Un sham reconstruit le même état sans modifier `m` et doit être numériquement nul.

## `P_acc` local

Le jeu de challenges est le produit cartésien de cinq obliquités `(10, 23.5, 40, 55, 70 deg)` et cinq excentricités `(0.01, 0.05, 0.10, 0.20, 0.30)`, soit 25 conditions maintenues 10 Ma. Les réponses sont lues sur les 2 dernières Ma.

Pour chaque challenge et chacune des quatre dimensions déjà utilisées par le test exoplanétaire (`temperature_k`, `ice_fraction`, `co2_ppm`, `productivity`), une réponse est comptée accessible si son écart à l'état de départ dépasse le seuil de matérialité déjà présent dans le modèle. Le dénominateur est donc fixé à `25 × 4 = 100` et la résolution de `P_acc` vaut `0.01`.

Cette métrique est **locale**. Sa magnitude n'est pas comparable directement aux `P_acc` biologiques, orbitaux ou radiogéniques.

## Décision

Le test soutient localement `INV-A` si la médiane de `|Delta P_acc|` atteint au moins une cellule (`epsilon_acc = 0.01`), si la borne basse bootstrap à 95 % atteint également ce seuil, et si le sham reste nul à la tolérance numérique. Le signe de `Delta P_acc` est publié séparément : `INV-A` teste ici une modification de l'accessibilité, pas une augmentation universelle.

## Portée

Un succès de ce test démontrerait une intervention propre sur `m` **dans ce modèle réduit**. Il ne constitue ni une intervention sur le vrai Système solaire ni une réplication empirique. Il doit rester distinct du test `C-AST-01`, qui intervient sur l'architecture `A`.
