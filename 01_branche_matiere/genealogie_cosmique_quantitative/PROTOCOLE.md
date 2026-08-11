# Protocole — Généalogie cosmique quantitative

## 1. Question

Tester, stade par stade, si l’histoire physique transforme les constituants, les contraintes ou l’architecture de manière à modifier l’ensemble des états et trajectoires physiquement accessibles au stade suivant.

## 2. Unité d’analyse

Chaque stade `GC-xxx` contient : état antérieur, processus, contraintes, inscription historique, nouveaux accessibles, ce qui n’est pas démontré, observable, sources et mode de preuve.

Une flèche `GC-i → GC-j` n’est admise que comme **relation conditionnelle**. La présence d’un stade ne signifie pas que toutes ses sorties sont nécessaires ni suffisantes pour le suivant.

## 3. Hiérarchie de preuve

1. **Échantillon direct** : matière retournée ou météoritique portant une signature mesurée.
2. **Observation astronomique** : mesure d’un système actuel, qui peut être un analogue du passé solaire.
3. **Reconstruction historique** : isotopes/chronomètres qui contraignent un événement non observé directement.
4. **Expérience / thermodynamique** : mécanisme reproductible sous conditions contrôlées.
5. **Simulation** : causalité dans un modèle explicite, avec domaine de validité.

Aucun niveau n’est automatiquement transposé à un autre.

## 4. Tests quantitatifs exécutés ici

### NUC-01 — expansion de l’inventaire élémentaire dans les rendements stellaires

Le dépôt contient six familles de rendements stellaires. On compare le set élémentaire représenté par ces rendements au baseline élémentaire BBN `H, He, Li`. Ce test ne prétend pas calculer l’évolution chimique galactique; il mesure seulement si les modèles stellaires versionnés produisent un espace de constituants plus large.

### PHASE-01 — filtre stoichiométrique des phases accessibles

La table thermochimique versionnée est filtrée par les éléments effectivement disponibles. Une composition de phase n'est dite *stoichiométriquement admissible* que si tous les éléments de sa formule appartiennent à l'inventaire considéré. Le baseline BBN `H, He, Li` est comparé à l'inventaire couvert par les rendements stellaires. Ce test vérifie une **condition nécessaire de constituants uniquement** : il ne calcule ni équilibre de condensation, ni activités, ni pression partielle, ni cinétique, ni réalisation historique dans le disque.

### GEN-01 — fermeture topologique de la chaîne

Tous les parents doivent être résolus, aucun cycle n’est admis, chaque stade doit avoir au moins une source ou être le raccordement explicite vers une certification existante.

### SRC-01 — séparation des modes de preuve

Le catalogue doit permettre de distinguer les preuves primaires, les revues et les sorties de modèles. Les observations numériques importées de la littérature sont marquées `mesure`, `reconstruction`, `sortie de modèle` ou `inférence de modèle`.

### HANDOFF-01 — raccordement vers C-AST

Le point aval doit retrouver la certification C-AST sans la modifier. Le handoff est déclaré `open` tant qu’aucun pipeline de formation planétaire ne produit, avec incertitudes et contrôle hors-échantillon, les mêmes variables nécessaires à la couche N-corps actuelle.

## 5. Critères de non-surinterprétation

- Les grains présolaires démontrent une transmission matérielle locale, pas le budget total de matière stellaire du disque.
- V883 Ori est un analogue externe, pas une observation du disque solaire.
- Les rapports >30 % d’infall tardif de 2026 sont des inférences du modèle de l’article, pas une mesure directe de masse du disque solaire.
- Le 26Al ne reçoit pas une valeur initiale universelle imposée : une hétérogénéité 3–4 est rapportée par une analyse récente.
- Streaming, Grand Tack, Nice, anneaux de planétésimaux et accrétion de galets conservent leur statut de modèles.
- C-AST mesure l’efficacité causale de l’architecture actuelle **dans le modèle**; il ne reconstruit pas sa formation.

## 6. Réfutabilité locale

Une claim locale est réfutée si les données ou recalculs requis contredisent son énoncé sous le protocole défini. La proposition end-to-end reste `open_not_certified` jusqu’à fermeture du handoff.
