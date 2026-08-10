# Protocole de réplication spin-orbite

Le calcul livré ici est une extension exécutée du modèle. Pour une future réplication confirmatoire indépendante, les critères suivants sont gelés avant nouveau calcul sur un environnement ou une implémentation indépendante :

1. `α = 54,93 arcsec/an`, obliquité initiale J2000 `23,43929111°` et même forçage orbital.
2. Sur `0-100 ka`, corrélation d'obliquité avec La2004 `>= 0,99` et RMSE `<= 0,05°`.
3. Sur `0-1 Ma`, corrélation d'obliquité avec La2004 `>= 0,95` et RMSE `<= 0,20°`.
4. Période dominante d'obliquité entre `35 ka` et `50 ka` sur 2 Ma.
5. La réduction du sous-pas de spin de 100 ans à 50 ans doit changer l'obliquité avec une RMSE `< 1e-4°` sur 2 Ma.
6. L'ablation lunaire (`α = 20 arcsec/an`) doit augmenter l'étendue de l'obliquité sur 2 Ma par rapport au témoin avec Lune effective. Aucun critère `0-85°` n'est imposé.
7. Les six interventions Jupiter/Saturne sont propagées sans retoucher leurs sorties N-corps. Leur effet sur l'obliquité et l'insolation est comparé à la dispersion des huit réalisations orbitales quasi identiques.

Ces critères de réplication ne reclassent pas rétroactivement le calcul initial comme préenregistré.
