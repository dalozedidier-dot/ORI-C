# Revue quantitative empirique complète — v3

Cette revue décrit l’autorité quantitative courante de `genealogie_cosmique_quantitative`. La v1 et la v2 restent conservées pour provenance, mais leurs comptages et audits ne constituent plus le résultat final de la campagne.

## Politique de données

Le corpus v3 contient **43 sources primaires/officielles** et **120 enregistrements empiriques**. Les verdicts utilisent 0 simulation, 0 donnée synthétique, 0 imputation et 0 échantillonnage aléatoire. Les sorties théoriques, thermochimiques et N-corps sont exclues. Lorsqu’une publication combine mesures et traitement dépendant de données synthétiques ou de Monte-Carlo, seule la portion empirique explicitement admissible est conservée.

## Résultat 1 — transformation quantitative d’un inventaire hérité

À partir du rapport initial canonique `26Al/27Al`, d’âges Pb-Pb mesurés et de la demi-vie évaluée de `26Al`, la campagne calcule la fraction de radionucléide parent encore disponible, sans modèle thermique :

- angrite, 1,10 ± 0,19 Myr après CAI : **34,5 %** ;
- EC 002, 1,74 ± 0,20 Myr : **18,6 %** ;
- chondre jeune sélectionné, 2,59 ± 0,34 Myr : **8,18 %** ;
- carbonate CM, 3,90 ± 0,52 Myr : **2,30 %**.

Ce résultat répond directement à la question ORI-C locale : deux incorporations de matière à des moments différents n’héritent pas du même inventaire radiogénique accessible, même si la loi de décroissance est identique. La campagne ne transforme pas cette fraction en température, fusion ou différenciation simulée.

## Résultat 2 — différenciation précoce dans une fenêtre d’inventaire plus élevé

La fenêtre Hf-W publiée pour la formation de noyaux de météorites de fer, environ 1,0–1,5 Myr après CAI, correspond à **23,5–38,0 %** de l’inventaire initial de `26Al` encore présent. Cette fenêtre dispose de **2,87–4,65 fois** l’inventaire du chondre jeune du test et de **10,18–16,50 fois** celui de l’événement carbonate CM. Il s’agit d’une mise en correspondance déterministe entre deux horloges empiriques indépendantes, pas d’une simulation thermique.

## Résultat 3 — persistance d’une architecture pendant un changement physique majeur

La séparation NC/CC enregistrée dans les météorites persiste pendant au moins 2–3 Myr. Sur cette durée, l’inventaire relatif de `26Al` diminue d’un facteur **6,91–18,18**, soit une perte de **85,5–94,5 %** entre le début et la fin de la fenêtre utilisée. Une structure historique peut donc persister alors qu’une condition physique héritée change de presque un ordre de grandeur à plus d’un ordre de grandeur.

## Contrôle post-hoc — la décroissance temporelle ne fixe pas un inventaire local unique

Le calcul canonique est volontairement traité comme une **référence de décroissance**. À environ 2 Myr après CAI, cette référence donne `26Al/27Al = 7,56×10^-6`. Deux CAI à matériel chondritique du corpus donnent respectivement `4,7±1,4×10^-6` et `<1,2×10^-6`, soit environ **62,1 %** et **<15,9 %** de la référence temporelle. Une archive indépendante rapporte par ailleurs une hétérogénéité `26Al` d’un facteur 3–4.

Ce contrôle `GCQ-X01` a été ajouté après les huit tests gelés et est donc explicitement marqué **post-hoc**. Il ne reçoit aucun test de significativité artificiel, car le délai publié de ~2 Myr n’a pas d’incertitude numérique transcrite. Son rôle est de borner l’interprétation : le temps transforme fortement l’inventaire radiogénique, mais l’histoire locale des réservoirs/mélanges intervient également.

## Résultat 4 — porteurs de mémoire sur plusieurs échelles

Les grains présolaires identifiés dans des matériaux retournés imposent une borne conservatrice de persistance matérielle supérieure à **4,567 Gyr**. À l’autre extrême, Ryugu enregistre une réactivation fluide plus de 1 000 Myr après sa formation. Cette borne correspond à plus de **1 394 demi-vies** de `26Al`; l’horloge radiogénique initiale est donc physiquement séparée de cet épisode tardif. La campagne ne déduit pas la cause de la réactivation.

## Résultat 5 — provenance terrestre : conflit empirique conservé

Les reconstructions isotopiques de la provenance terrestre ne convergent pas dans le corpus retenu. Une reconstruction antérieure soutient une contribution CC tardive, tandis qu’une étude plus récente indique que les 10–20 derniers pourcents massiques sont dominés par du matériel NC, avec une petite contribution CC encore possible dans les 0,5–1 derniers pourcents. Les valeurs BSE Mo rapportées en 2026 sont enregistrées, mais la conclusion multivariée de cette étude est exclue du registre de preuve parce que son pipeline publié utilise des priors synthétiques et du Monte-Carlo. Le verdict est donc `empirically_contested_not_closed`.

## Résultat 6 — endpoint et fermeture du graphe

L’endpoint officiel retenu comprend huit corps et couvre un facteur **77,68** en demi-grand axe entre Mercure et Neptune dans la table utilisée. Il décrit l’état actuel approché, sans reconstruire l’histoire qui y mène.

L’ablation exacte des relations documentées identifie **6 nœuds critiques** et **6 relations critiques** pour le chemin strict produits stellaires → endpoint actuel. Ce chemin existe. En revanche, le chemin strict baseline primordiale → endpoint actuel reste ouvert. La branche transforme ainsi un ancien « trou » narratif en liste machine de verrous localisés.

## Claims machine v3

Les huit tests `GCQ-T09` à `GCQ-T16` sont générés individuellement sous `resultats/claims_quantitatifs_v3/` et agrégés dans `resultats/CLAIMS_QUANTITATIFS_COMPLETS.json`. Chaque claim contient son verdict, ses sources, ses stades, ses données de résultat et sa limite d’interprétation.

## Verdict global

`quantified_history_dependent_accessibility_with_explicit_open_links`

La campagne démontre quantitativement, sur des entrées empiriques, qu’un changement de moment historique modifie une ressource physique accessible et que des porteurs/architectures peuvent persister à travers ce changement. Elle ne certifie ni une trajectoire orbitale unique ni une chaîne primordiale→présent entièrement fermée.
