# PALEO-HISTORY-01 — protocole préenregistré

## Question primaire

À état climatique et forçages astronomiques comparables, l'histoire antérieure
améliore-t-elle la prédiction de la trajectoire climatique suivante hors
échantillon ?

Le protocole compare exclusivement des modèles de complexité contrôlée :

1. état présent et forçages présents ;
2. mêmes variables plus histoire réelle ;
3. mêmes variables plus histoire permutée dans le bloc temporel ;
4. témoin de complexité égale sans ordre historique.

## Données obligatoires

- LR04 complet et incertitudes chronologiques ;
- une pile benthique indépendante ;
- un proxy indépendant du niveau marin ;
- EPICA Dome C température, CO₂ et poussières ;
- Vostok ;
- au moins deux conventions publiées d'insolation.

Une donnée déjà présente ne vaut pas admission. La campagne ne démarre que si
le validateur confirme les variables, unités, chronologies, incertitudes,
provenances et empreintes exigées par `SCHEMA_DONNEES.json`.

## Variable cible et horizons

La cible primaire est la variation future du proxy climatique à 10 ka. Les
horizons secondaires sont 20 et 50 ka. Les fenêtres historiques sont fixées à
20, 50 et 100 ka. Aucun horizon ni fenêtre ne sera choisi après observation du
score.

## Validation hors échantillon

L'intervalle commun 0–800 ka est partagé en quatre blocs fixés avant analyse :
0–200, 200–400, 400–600 et 600–800 ka. Chaque bloc est successivement tenu hors
apprentissage. Aucun point, voisin temporel ou dérivé de la cible du bloc test
ne peut entrer dans l'ajustement.

La robustesse exige en plus : apprentissage sur 400–800 ka et prédiction de
0–400 ka, puis sens inverse. Ces deux tests sont secondaires et ne peuvent
remplacer le critère primaire.

## Chronologie et dépendance temporelle

Les incertitudes d'âge sont propagées sur 2 000 réalisations chronologiques.
Les modèles nuls sont AR(1) et IAAFT, recalculés symétriquement de bout en bout.
Les permutations de l'histoire restent internes au bloc et conservent les
distributions marginales. Toute autocorrélation résiduelle est publiée.

## Critère primaire PALEO-HISTORY-01

Le résultat `supports` exige simultanément :

- gain de RMSE d'au moins 5 % de l'histoire réelle sur l'état seul dans au
  moins trois des quatre blocs ;
- histoire réelle meilleure que l'histoire permutée et que le témoin de
  complexité égale, avec p < 0,01 ;
- signe du gain conservé sous les réalisations chronologiques ;
- réplication du signe sur une pile benthique indépendante ;
- absence de succès du même test sur le contrôle négatif réel préenregistré.

Un échec rend `does_not_support`. Une donnée obligatoire absente, une p-value
inatteignable ou une chronologie non propageable rend `non_testable`, jamais
`supports`.

## Tentatives de destruction obligatoires

État seul, histoire permutée, variables confondantes, paramètres alternatifs
préenregistrés, autre époque, autre dataset, reconstruction chronologique et
contrôle négatif réel sont tous obligatoires. Aucun résultat spectral à 41,
100 ou 405 ka ne remplace ce test prédictif.

## Statut

Protocole gelé avant toute exécution de PALEO-HISTORY-01. Les anciennes analyses
paléoclimatiques, déjà observées, ne sont pas réinterprétées rétroactivement
comme résultats de ce protocole.
