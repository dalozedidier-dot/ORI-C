# Mise à jour scientifique - invariant H → m → R/P_acc

Cette mise à jour exploite trois jeux réels déjà acquis et resserre la proposition testable d'ORI-C. Le principe transversal recherché n'est pas la simple présence d'une corrélation avec le passé. Une histoire `H` n'est pertinente que si son information reste irréductible à un état présent `X` suffisamment riche, ou si elle est portée par une trace physique `m` dont l'intervention modifie la réponse future `R` ou le domaine d'accessibilité `P_acc`.

## Yen & Papin 2017 : contrôle d'un X enrichi

Sur 2 100 mesures futures et 16 unités indépendantes, le modèle état + histoire améliore la RMSE de 1,945 %, avec IC95 bootstrap [0,058 ; 5,155] et permutation p = 0,001998. Le seuil gelé de 5 % n'est pas atteint. Lorsque la MIC mesurée au jour 20 est ajoutée à `X`, le gain résiduel de `H` tombe à 0,265 %, IC95 [-0,799 ; 1,595], p = 0,1049. Ce résultat falsifie l'interprétation forte selon laquelle toute dépendance statistique au passé constitue une mémoire autonome. Ici, l'information historique est largement absorbée par une meilleure mesure de l'état présent.

## Gajrani et al. 2025 : trace externe manipulable

Dans le système microbien à deux espèces, le lavage retire la modification environnementale accumulée et le transfert de surnageant la réintroduit. Sous faible dilution, l'identité de la mémoire environnementale déplace de 40,724 points le seuil de composition initiale séparant les gagnants. Sous forte dilution, l'écart tombe à 7,857 points. Avec les deux populations lavées et uniquement le surnageant historique changé, le déplacement médian atteint 91,914 points. Cette géométrie expérimentale soutient directement une chaîne `H -> m -> R` : la trace est localisée dans l'environnement extracellulaire et son transfert suffit à modifier le futur du système.

La réanalyse rétrospective de `P_acc` sur les six compositions indépendantes du jour 12 donne un delta moyen de -0,080729, avec IC95 bootstrap [-0,114583 ; -0,041667]. Ce résultat ne remplit pas `PACC-INT-CHALLENGE-V1`, puisque les seuils et les poids n'avaient pas été gelés avant inspection. Il reste attaché au benchmark Gajrani comme mesure exploratoire de complétude des champs.

## Watkins et al. : test matière après gel local

L'archive expérimentale `exp.zip` a été ouverte après le gel local du protocole `PRED-MATIERE-WAVE-HISTORY-001`. La reconstruction des états finaux est reproductible sur 209 essais. Le plus grand déplacement classé sans bascule vaut 0,998657 et le plus petit déplacement classé avec bascule vaut 48,799896 pour un seuil fixé à 25. Le résultat classifieur conservé est négatif pour la règle gelée : l'exactitude passe de 0,267943 avec `X` seul à 0,306220 avec `X+H`, soit +3,828 points, avec IC95 [-2,871 ; 10,526]. La permutation donne p = 0,005, mais le seuil de gain de 10 points et la borne bootstrap strictement positive échouent. Le résultat ne reçoit aucun crédit §XIV et le classifieur historique n'est pas présenté comme un rerun exact, le script d'extraction original n'étant plus disponible.

## Conséquence pour l'invariant ORI-C

L'hypothèse transversale doit être évaluée avec deux filtres obligatoires :

1. **irréductibilité à X** : tester `I(R;H|X)` après enrichissement raisonnable de l'état présent ;
2. **intervention sur m** : lorsqu'une trace physique candidate existe, montrer que `do(m)` modifie `R` ou `P_acc` sous `X`, contraintes et architecture appariés.

Yen/Papin fournit un contrôle négatif du premier filtre. Gajrani fournit un soutien rétrospectif fort au second. Watkins ajoute un contrôle matière où l'information temporelle ne franchit pas la règle de gain gelée. Aucun de ces jeux ne ferme une condition §XIV parce qu'ils étaient publics avant leur mapping ORI-C ou ne satisfont pas la chaîne prospective stricte.

## État §XIV

Le score reste 7/12. Ce maintien est volontaire : la mise à jour ajoute des résultats réels sans abaisser les critères 3, 4, 9, 10 ou 11.

## Route paléoclimatique

Une source publiée contient un stack benthique nord-atlantique avec **1 000 réalisations de modèle d'âge** et une version **non accordée astronomiquement** sur l'échelle de profondeur composite. Cette source fournit un moyen propre de propager l'incertitude chronologique au lieu d'attribuer artificiellement une erreur à LR04. Le protocole gelé `PRED-PALEO-HISTORY-02` reste inchangé et son verrou LR04 est conservé. L'audit AICC2023 ajoute désormais des incertitudes chronologiques publiées pour les carottes de glace, avec une médiane EDC passant de 0,066 ka entre 0 et 100 ka à 2,37 ka entre 600 et 850 ka. Il lève partiellement le verrou d'incertitude pour cette famille de chronologies, sans fournir à lui seul la cible indépendante ni le contrôle négatif nécessaires au test paléoclimatique complet. La route nord-atlantique reste décrite dans `plan_directeur/PALEO_AGE_ENSEMBLE_ROUTE.json`.
