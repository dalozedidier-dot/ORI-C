# Préenregistrement local gelé — antibiotiques ORIC-ABX-001

Statut : **gelé localement, non préenregistré publiquement, calcul bloqué par données non joignables**.

## Hypothèse unique

À état final observable comparable, l'histoire d'exposition améliore la prédiction de la réponse future au-delà d'un modèle classique de complexité égale.

## Unité, partition et fuite interdite

L'unité de groupement est la lignée/population expérimentale. Aucune lignée ne peut apparaître dans plusieurs partitions. Les partitions, produites une seule fois par graine publique avant ajustement, sont 60 % apprentissage, 20 % validation et 20 % test. Une validation externe doit laisser entièrement de côté une souche ou un antibiotique.

## Modèles comparés

- B0 : état final observable, sans histoire ;
- B1 : B0 + cumul simple de dose/exposition ;
- B2 : autorégressif, sans représentation ORI-C ;
- B3 : témoin de complexité égale au modèle ORI-C ;
- O1 : histoire ORI-C ;
- P0 : histoires permutées entre lignées dans les seules données d'apprentissage ;
- A1–Ak : ablation séparée de chaque composante de mémoire.

Le budget d'hyperparamètres, le nombre de degrés de liberté et le budget d'optimisation de B3 et O1 doivent être appariés et publiés.

## Sortie, métrique et seuil gelés

Sortie primaire : réponse future quantitative mesurée après l'état d'ancrage, sans utiliser une mesure ayant servi à construire les prédicteurs.

Métrique primaire : différence de MAE groupée par lignée, `MAE(B3) - MAE(O1)`, sur le test final. Succès seulement si :

1. l'amélioration relative contre B3 est au moins 10 % ;
2. l'intervalle de confiance bootstrap groupé à 95 % de la différence exclut 0 ;
3. O1 bat B0, B1 et B2 ;
4. P0 supprime l'avantage ;
5. le signe de l'avantage est conservé dans la validation externe laissée de côté.

Tout autre résultat est négatif ou indéterminé selon les règles publiées avant ouverture du test.

## Verrou actuel

Le dépôt Windels fournit 942 cycles et 1 068 mesures, mais les phénotypes finaux ne portent pas une clé de population permettant de les joindre sans ambiguïté aux trajectoires longitudinales. Aucun split par lignée ni test de la prédiction centrale n'est donc revendiqué avec ces seules tables. Il faut obtenir la table de correspondance auprès des auteurs ou choisir un jeu publié possédant cette clé.

