# Intégration indépendante — résultats partiels, non retenus

`integration_reelle.json` et `excentricite_terre.csv` proviennent d'un essai
de **20 ka seulement**, pas des 2 Ma visés. L'exécution longue a calé à 60 %,
et `integration_2Ma.log` en conserve la trace.

Ces fichiers sont versés pour la traçabilité, **pas comme résultat**.

Ils sont de toute façon surclassés par l'intégration N-corps du dossier,
`resultats/real_science_max/baseline_20myr_dt10/` : 20 Ma au lieu de 20 ka, et
une dérive d'énergie de 1,33 × 10⁻¹¹ contre 7 × 10⁻⁵ ici — quatre ordres de
grandeur. C'est cette intégration-là, et non celle-ci, qui fonde le résultat
sur le spectre et la phase.

Le script `integrer_systeme_solaire.py` garde son intérêt comme troisième
implémentation indépendante, à confronter aux deux autres. Son critère de
conservation d'énergie, fixé à 10⁻⁸ avant exécution, n'est **pas** tenu par un
saute-mouton cartésien à pas fixe : c'est un défaut de méthode, documenté et
non corrigé après coup.
