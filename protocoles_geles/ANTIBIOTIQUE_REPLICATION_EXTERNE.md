# Réplication antibiotique externe prospective

Ce protocole s'applique au **prochain** jeu de données indépendant, qui ne doit pas être inspecté avant gel du plan.

1. Déclarer la variable temporelle, l'état initial et la mesure de persistance ou d'évolvabilité.
2. Réserver les deux derniers temps, ou les 25 % les plus récents, comme test hors échantillon.
3. Comparer au minimum un témoin état présent seul et un modèle état + histoire de complexité appariée.
4. Critère principal : amélioration de RMSE supérieure à 5 %, intervalle bootstrap à 95 % entièrement positif.
5. Critères de garde : calibration, stabilité à l'ablation, absence de fuite temporelle et réplication sur une seconde lignée.
6. Aucun changement de seuil après accès au test.

Le benchmark Card 2019 ne compte pas pour ce protocole car il a été conçu après accès aux données.
