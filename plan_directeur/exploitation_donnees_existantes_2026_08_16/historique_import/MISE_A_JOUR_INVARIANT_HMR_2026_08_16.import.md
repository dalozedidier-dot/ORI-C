# Mise à jour scientifique — invariant H → m → R/P_acc

Cette mise à jour exploite deux jeux réels déjà acquis et resserre la proposition testable d'ORI-C. Le principe transversal recherché n'est pas la simple présence d'une corrélation avec le passé. Une histoire `H` n'est pertinente que si son information reste irréductible à un état présent `X` suffisamment riche, ou si elle est portée par une trace physique `m` dont l'intervention modifie la réponse future `R` ou le domaine d'accessibilité `P_acc`.

## Yen & Papin 2017 : contrôle d'un X enrichi

Sur 2 100 mesures futures et 16 unités indépendantes, le modèle état + histoire améliore la RMSE de 1,945 %, avec IC95 bootstrap [0,058 ; 5,155] et permutation p = 0,001998. Le seuil gelé de 5 % n'est pas atteint. Lorsque la MIC mesurée au jour 20 est ajoutée à `X`, le gain résiduel de `H` tombe à 0,265 %, IC95 [-0,799 ; 1,595], p = 0,1049. Ce résultat falsifie l'interprétation forte selon laquelle toute dépendance statistique au passé constitue une mémoire autonome. Ici, l'information historique est largement absorbée par une meilleure mesure de l'état présent.

## Gajrani et al. 2025 : trace externe manipulable

Dans le système microbien à deux espèces, le lavage retire la modification environnementale accumulée et le transfert de surnageant la réintroduit. Sous faible dilution, l'identité de la mémoire environnementale déplace de 40,724 points le seuil de composition initiale séparant les gagnants. Sous forte dilution, l'écart tombe à 7,857 points. Avec les deux populations lavées et uniquement le surnageant historique changé, le déplacement médian atteint 91,914 points. Cette géométrie expérimentale soutient directement une chaîne `H -> m -> R` : la trace est localisée dans l'environnement extracellulaire et son transfert suffit à modifier le futur du système.

## Conséquence pour l'invariant ORI-C

L'hypothèse transversale doit désormais être évaluée avec deux filtres obligatoires :

1. **irréductibilité à X** : tester `I(R;H|X)` après enrichissement raisonnable de l'état présent ;
2. **intervention sur m** : lorsqu'une trace physique candidate existe, montrer que `do(m)` modifie `R` ou `P_acc` sous `X`, contraintes et architecture appariés.

Yen/Papin fournit un contrôle négatif du premier filtre. Gajrani fournit un soutien rétrospectif fort au second. Aucun de ces jeux ne ferme une condition §XIV parce qu'ils étaient publics avant leur mapping ORI-C. Ils font néanmoins progresser le cœur scientifique en séparant une histoire redondante avec `X` d'une histoire physiquement inscrite et manipulable.

## Prochaine cible matière gelée sans ouverture des données

`PRED-MATIERE-WAVE-HISTORY-001` cible le métamatériau bistable de Watkins et al., données Zenodo `10.5281/zenodo.21476531`. L'archive expérimentale `exp.zip` reste fermée côté ORI-C. Le fichier de gel fixe le mapping, le témoin et le critère d'échec avant toute analyse brute. Cette route sert d'abord à tester la même distinction `X` statique contre forme temporelle du forçage `H`, sans requalifier a posteriori le résultat publié.

## État §XIV

Le score reste 7/12. Ce maintien est volontaire : la mise à jour ajoute des résultats réels et un nouveau verrou expérimental sans abaisser les critères 3, 4, 9, 10 ou 11.

## Route paléoclimatique débloquée sans inventer d'incertitudes

Une source publiée contient un stack benthique nord-atlantique avec **1 000 réalisations de modèle d'âge** et une version **non accordée astronomiquement** sur l'échelle de profondeur composite. Cette source fournit enfin un moyen propre de propager l'incertitude chronologique au lieu d'attribuer artificiellement une erreur à LR04. Le protocole gelé `PRED-PALEO-HISTORY-02` reste inchangé et son verrou LR04 est conservé. La nouvelle route doit recevoir un nouvel identifiant afin de comparer histoire et état sous ensembles chronologiques publiés, avec l'âge non accordé comme contrôle de sensibilité. Voir `plan_directeur/PALEO_AGE_ENSEMBLE_ROUTE.json`.
