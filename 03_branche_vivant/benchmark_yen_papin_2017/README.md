# Yen & Papin 2017 — histoire antibiotique et état présent

Source : Yen & Papin, PLOS Biology, DOI `10.1371/journal.pbio.2001586`, supplément `pbio.2001586.s018.xlsx`.

Cette analyse teste si l'histoire de phase 1 améliore la prédiction de la MIC pendant les jours 21 à 40 après branchement vers une nouvelle condition. Les descendants d'une même combinaison histoire × réplicat restent dans le même groupe de validation afin d'éviter toute fuite entre branches apparentées.

Le test principal reprend le seuil gelé de `PRED-VIVANT-HISTOIRE-001` : gain RMSE d'au moins 5 %, IC bootstrap strictement positif et permutation p <= 0,05. Il échoue sur le seuil d'amplitude malgré un faible signal rétrospectif. Une analyse de sensibilité ajoute à `X` la MIC réellement mesurée au jour 20, juste avant le branchement. Le gain résiduel de l'histoire devient alors proche de zéro et non soutenu.

Rôle ORI-C : résultat négatif discriminant. Il montre qu'une différence associée à `H` ne doit pas être assimilée à une mémoire autonome si une mesure enrichie de l'état présent `X` absorbe cette information. Aucun crédit §XIV n'est accordé.

Reproduction : `python analyser.py`.
