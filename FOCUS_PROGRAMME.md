# Gel du périmètre ORI-C

ORI-C cesse d’ajouter des domaines et des concepts. Le travail courant porte sur cinq livrables, en tenant compte des résultats déjà obtenus.

| Livrable | État courant | Prochaine étape utile |
|---|---|---|
| Prédiction antibiotique hors échantillon | **Premier résultat positif obtenu** sur le jeu D’Onofrio : RMSE 1,1309 pour l’état seul, 0,8042 avec l’histoire, témoin permuté 1,1415, p = 0,00498 | réplication sur un autre jeu indépendant avec le même protocole gelé |
| Recodage indépendant des dimensions matière | à exécuter | accord inter-codeurs sur un échantillon gelé |
| Environnement astronomique reproductible | résultat scientifique obtenu, CI reproductible | simplifier l’exécution en une commande portable et produire le paquet de figures et tableaux |
| Protocole climatique remplaçant M2 | M2 fermé comme formulation | construire un protocole minimal centré sur relaxation, attracteurs et franchissement de bassin |
| Mesure commune de `Pacc` | mesurée dans la branche astronomique sur 6 interventions et 17 dimensions sur 18 | appliquer la même définition interventionnelle dans la matière puis comparer sans redéfinition |

Les lignées de vésicules ne sont plus une donnée manquante. La campagne analyse **11 760 couples parent-descendant** et soutient les quatre composantes préenregistrées de sélection, filiation, ablation et codage des lignées. Les données ARN constituent un autre protocole et leur absence de filiation ne doit jamais être étendue aux vésicules ni à toute la branche vivant.

La chaîne `Histoire → Architecture → Contraintes → Réponse → Inscription → Possibilités` organise les mécanismes déjà mesurés. Les prochains travaux doivent relier davantage de termes dans un même protocole, sans effacer les résultats locaux déjà établis.

Trois règles s’appliquent à tout rapport :

1. un résultat négatif reste limité au jeu de données, au modèle et au témoin qui l’ont produit ;
2. des jeux distincts ne sont jamais fusionnés dans un verdict de branche, notamment amikacine, Card 2019, D’Onofrio, ARN et vésicules ;
3. l’état courant des preuves prime sur les synthèses historiques antérieures à la campagne de recherche suivante.

## Puissance statistique a priori

Tout nouveau protocole lié aux cinq livrables doit être accompagné d’un `POWER_PLAN.json` gelé avant l’acquisition ou avant l’ouverture du jeu tenu à l’écart. Ce plan déclare le SESOI et sa justification scientifique, `alpha`, la puissance cible, l’unité réellement indépendante, la taille disponible ou nécessaire, l’estimation du bruit, le test, les témoins et la règle conjointe de succès.

Les folds de validation croisée ne sont jamais comptés comme observations indépendantes. La simulation Monte-Carlo doit générer les observations ou trajectoires puis réexécuter le pipeline complet, y compris les groupes, les dépendances temporelles, les ablations, les témoins de même complexité, les permutations et le verdict final.

La taille nécessaire est retenue lorsque la borne inférieure de l’intervalle de Wilson atteint la puissance cible après au moins 10 000 simulations de confirmation. Lorsque la taille est déjà fixée, le protocole rapporte le plus petit effet détectable à 80 % ou 90 % de puissance. Une puissance recalculée après observation du résultat ne constitue pas une preuve.

Le format, le validateur et le moteur commun se trouvent dans `methodologie_puissance/`.
