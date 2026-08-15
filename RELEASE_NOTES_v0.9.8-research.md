# ORI-C v0.9.8-research

Publication stable du snapshot scientifique du **15 août 2026**, postérieur à `v0.9.7-research`. Cette version consolide les travaux ajoutés depuis le 12 août : nouvelles données réelles, protocoles causaux, extension du benchmark transversal, audits de réplication et amélioration de la couche publique et de la reproductibilité.

## Données réelles et analyses supplémentaires

La branche vivant reçoit plusieurs jeux et audits séparés : Card 2019 complet, Lamrabet 2019, Petrungaro 2026, Nader 2026, Wong & Seguin 2015 et Santos-Lopez 2021. Aucun de ces protocoles n’est fusionné dans un verdict global de branche.

Trois analyses réelles auparavant sous-exploitées sont maintenant recalculées, versionnées et intégrées au benchmark transversal :

- `FIT-ORIGIN-N-01` : sous limitation azotée, les souches évoluées indépendamment issues d’une même origine ancestrale sont plus similaires que sous tous les appariements parfaits possibles, **p exact = 0,03069**. Le carbone ne montre pas ce signal dans le même test, p = 0,13045. Le résultat est rétrospectif et ne possède ni trace physique `m` isolée ni `P_acc`.
- `MAT-NBOT-PART-01` : sur **32 expériences réelles** issues de **7 groupes de sources**, l’ajout de NBO/T à P, T et ΔIW réduit la RMSE hors-source de 0,73895 à 0,53003, soit **28,27 % de gain**, avec permutation intra-source **p = 0,001999**. NBO/T est qualifié comme état structural `X`, pas comme mémoire `m`.
- `RNA-PAP-TRAJ-01` : sur deux branches ARN suivies pendant huit cycles, la divergence maximale des trajectoires partagées atteint **17,733 log2** pour Seq5. Le faible nombre de branches limite le résultat à une description rétrospective inter-branche.

## Benchmark transversal et §XIV

Le benchmark transversal passe de **21 à 24 cas**. La complétude reste à **6 cas 7/7** pour **5 systèmes distincts**. Le registre machine passe à **56 preuves**.

Les trois nouveaux cas sont volontairement incomplets lorsque les variables n’existent pas :

- `FIT-ORIGIN-N-01` : 5/7, `m` et `P_acc` manquants ;
- `RNA-PAP-TRAJ-01` : 5/7, `m` et `P_acc` manquants ;
- `MAT-NBOT-PART-01` : 3/7, sans réinterprétation de NBO/T comme trace historique.

Le seuil scientifique reste **7/12**. Les conditions **3, 4, 9, 10 et 11** restent ouvertes. Il n’y a toujours aucune réussite prospective stricte dans les trois branches, aucune branche qualifiée pour le `P_acc` causal empirique strict, aucune double réplication indépendante stricte et aucun transfert qualifié entre deux branches sous la même définition.

## INV-A et Pacc causal

`INV-A` reste `candidate_operationalized_exploratory_not_validated`. Deux systèmes disposent d’un `do(m)` direct. Le cas vésiculaire est empirique mais ne soutient pas la direction positive locale de son contraste `P_acc`. `EXO-DOM-01` soutient un effet non nul au niveau modèle et ne remplace pas une réplication empirique.

La définition `PACC-INT-CHALLENGE-V1` est installée comme règle commune pour les futurs tests causaux. Les paquets `VES-PACC-INT-01` et `PACC-MAG-INT-01` séparent désormais conception, gel des champs, exécution et résultat. Aucun crédit n’est attribué avant acquisition réelle admissible.

## Matière et fermeture

Le baseline strict de l’hypergraphe reste **46/53**. L’audit H052 et l’extension `HC02-E1` documentent une voie empirique indépendante permettant d’atteindre **53/53 en extension**, sans modifier le baseline scellé ni le §XIV.

La chaîne MAG reçoit son schéma d’entrée, le pilote, l’analyseur, les gates et le design `PACC-MAG-INT-01`. Ces éléments rendent l’expérience exécutable lorsqu’une acquisition physique admissible sera disponible, sans fabriquer de résultat à partir d’un protocole.

## Réplications et benchmarks vivant

Les benchmarks externes supplémentaires sont conservés avec leur verdict propre. Santos-Lopez soutient un gain prédictif rétrospectif dans sa spécification, tandis que Wong & Seguin ne reproduit pas le signal recherché. Lamrabet montre une persistance descriptive modérée. Petrungaro, particulièrement sous nitrofurantoïne, fournit un signal fort de dépendance au fond génétique et un approfondissement de la chaîne vers les mutations, sans intervention causale directe sur `m`. Nader est utilisé comme caractérisation physique et calibration, pas comme substitution aux mesures vésiculaires historiques.

## Reproductibilité et couche publique

La release ajoute ou renforce les workflows dédiés aux données réelles étendues, à la campagne centrale, aux données vivant et aux contrôles transversaux. Les résultats sont comparés aux sorties versionnées et les manifestes sont vérifiés avant publication.

GitHub Pages est mis à jour pour afficher la version 0.9.8, le benchmark à **24 cas**, le registre à **56 preuves**, le §XIV à **7/12** et les trois nouvelles analyses réelles. La page interactive et le noyau public restent reconstruits et comparés en CI.

## Frontière scientifique conservée

Cette publication ne reclasse pas les résultats antérieurs :

- astronomie N-corps : **13 / 15** ;
- paléoclimat M2 : **1 / 10**, non soutenu ;
- `C-MAT-MEM-05` : non soutenu ;
- généalogie cosmique quantitative : pare-feu empirique strict, **0 simulation**, **0 donnée synthétique** et **0 imputation comme preuve** ;
- PCMCI+ et formalismes externes : exploratoires ou méthodologiques ;
- aucun invariant transversal général ORI-C n’est déclaré validé.

Le snapshot de préparation du tag contient **1 847 contenus manifestés**, **56 preuves** et **90 chiffres canoniques**. Le workflow de release reconstruit les sous-manifestes puis le manifeste racine en dernier avant de créer l’archive canonique hydratée et son SHA-256.
