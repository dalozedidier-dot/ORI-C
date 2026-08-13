# Réplication indépendante de D'Onofrio — Santos-Lopez et al. 2021

Cette ouverture applique `PRED-VIVANT-HISTOIRE-001` à un jeu externe qui n'avait pas servi au benchmark D'Onofrio. Le jeu eLife contient six histoires ancestrales distinctes (`B1–B3`, `P1–P3`), deux nouvelles pressions de sélection antibiotique (ceftazidime et imipénème), trois populations évoluées répliquées par histoire et par antibiotique, et des MIC aux jours 0, 3 et 12.

Le test primaire utilise le jour 3 comme état présent `X` et le jour 12 comme réponse future. Les trois populations parallèles définissent trois folds hors échantillon. Le modèle état seul reçoit `X + antibiotique`; le modèle histoire reçoit `X + antibiotique + histoire ancestrale`. Les deux sont des Ridge `alpha=1`, conformément à la famille d'analyse déjà utilisée pour D'Onofrio. L'histoire est permutée dans les strates antibiotique × fold pour le null.

## Résultat primaire

- RMSE état seul : **0,937482**
- RMSE état + histoire : **0,732492**
- gain relatif : **21,866 %**
- bootstrap 95 % du gain : **[7,235 % ; 33,967 %]**
- permutation : **p = 0,00019996** (5000 permutations)

La règle gelée demandait simultanément un gain `>=5 %`, une borne bootstrap basse `>0` et `p<=0,05`. **Verdict : succès sous la règle gelée.**

Contrôle de garde : le gain garde le même signe sur les deux antibiotiques, `+23,154 %` pour la ceftazidime et `+20,494 %` pour l'imipénème.

## Portée

C'est une validation externe aveugle relativement au gel ORI-C du 11 août 2026, mais les données ont été publiées en 2021. Elle constitue donc une **réplication hors échantillon sur données publiques préexistantes**, et non une collecte prospective nouvelle. Cette distinction doit rester visible dans l'audit §XIV.

Source : Santos-Lopez A. et al., *eLife* 10:e70676 (2021), doi:10.7554/eLife.70676. Le CSV source est conservé avec son empreinte dans le résultat machine.
