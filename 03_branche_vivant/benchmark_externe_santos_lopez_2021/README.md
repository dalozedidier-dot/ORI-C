# Benchmark externe Santos-Lopez et al. 2021

Ce dossier conserve un test de transport de l’idée « état + histoire » sur le jeu public de Santos-Lopez et al. (*eLife* 10:e70676, 2021). Il reste **séparé de D’Onofrio** et ne devient pas une réussite prospective de `PRED-VIVANT-HISTOIRE-001`.

Le calcul utilise 36 populations évoluées indépendantes, six histoires ancestrales (`B1–B3`, `P1–P3`) et deux antibiotiques, ceftazidime et imipénème. L’état présent est la MIC médiane log2 au jour 3 et la réponse future la MIC médiane log2 au jour 12. Les trois indices de populations servent de folds hors échantillon. Le modèle état seul utilise `X + antibiotique`; le modèle avec histoire ajoute l’identité ancestrale. Les deux utilisent Ridge `alpha=1`.

Le résultat reproductible donne RMSE état seul ≈ `0,937482`, RMSE état + histoire ≈ `0,732492`, soit un gain ≈ `21,866 %`, bootstrap 95 % ≈ `[7,235 % ; 33,967 %]` et permutation `p ≈ 0,00019996`. Cette combinaison satisfait numériquement la règle de 5 % utilisée comme référence.

Elle **ne compte toutefois pas comme succès strict** : le jeu était public et la spécification propre à ce jeu — choix jour 3 → jour 12, folds et Ridge — a été fixée après sélection/ouverture du dataset, sans préenregistrement public antérieur. Le résultat est donc conservé comme benchmark externe rétrospectif, sans modifier `PRED-VIVANT-HISTOIRE-001`, le §XIV-3 ou le §XIV-10.

Source : Santos-Lopez A. et al., *eLife* 10:e70676 (2021), doi:10.7554/eLife.70676.
