# ORI-C v0.9.6-research

Publication stable du snapshot scientifique du **12 août 2026**.

## Résultats conservés sans embellissement

- **Astronomie N-corps : 13 / 15.** Les deux critères échoués restent visibles.
- **Paléoclimat M2 : 1 / 10.** M2 reste non soutenu ; face à M1P de même complexité, 0 critère sur 5 est réussi.
- **D’Onofrio : E2**, **vésicules : E2 et E4**, **astronomie : E4_model**, **matière transversale : does_not_support**. Les certifications spécialisées existantes sont conservées.
- Le contraste exploratoire `P_acc` autour de l’ablation vésiculaire reste négatif pour la direction attendue ; il ne remplace pas le critère de réponse `C-VES-03`.

## Généalogie cosmique quantitative

La couche `01_branche_matiere/genealogie_cosmique_quantitative/` est intégrée à cette publication avec un pare-feu empirique strict :

- **48 sources/datasets empiriques admissibles** ;
- **120 enregistrements empiriques historiques** ;
- **11 467 lignes utiles normalisées**, dont **11 207 grains présolaires admissibles** ;
- **41 / 41 groupes NC/CC classés** sur 11 systèmes isotopiques dans la couche publiée ;
- **0 simulation utilisée comme preuve**, **0 ligne synthétique**, **0 imputation comme preuve**.

Les claims quantitatifs mesurent notamment la dépendance temporelle de l’inventaire accessible de `26Al` et la persistance de porteurs matériels ou isotopiques. Ils ne reconstruisent pas une trajectoire orbitale naturelle unique et ne ferment pas artificiellement la chaîne primordiale → présent.

## Benchmark transversal

La campagne centrale compare 20 cas selon les sept champs `X, H, m, Θ, τ, P_acc, R`. **5 claims** remplissent les sept champs, pour **4 systèmes distincts** : vésicules, antibiotique, Système solaire au niveau modèle et `26Al` cosmique.

Cette complétude est une opérationnalisation, pas un niveau de preuve. **Aucun invariant transversal général ORI-C n’est validé** dans cette version. `INV-A` reste au mieux prêt pour une comparaison exploratoire.

## Reproductibilité et intégrité

Le workflow `Publication stable ORI-C` hydrate Git LFS, exécute les validations, la campagne maximale et la généalogie cosmique, restaure les sorties transitoires, reconstruit les sous-manifestes puis le manifeste racine en dernier, et construit l’archive canonique déterministe avec son SHA-256.

La licence du code est MIT. Les autres contenus suivent `LICENSING.md`.
