# HC02 — croûte primitive + hydrosphère → interface eau-roche-gaz

`HC02` est une **hyperarête candidate non canonique**. Elle ne modifie ni `hyperaretes.csv` ni le résultat 46/53.

## Pourquoi cette voie est plus propre que le recodage de H052

Le cycle canonique exige `N030` pour déclencher `H052`. Au lieu de demander à `H052` de produire l'interface qu'elle entretient, `HC02` teste une étape antérieure et indépendante :

`N051 Croûte primitive + N028 Atmosphère/hydrosphère → N030 Interfaces eau-roche-gaz`.

Si cette relation est admissible, le reste de la fermeture suit les hyperarêtes canoniques déjà présentes : `H052 → N053`, `H053 → N054`, `H030 → N029`, puis les nœuds aval. L'ajout de `HC02` ferme mathématiquement 53/53 sans toucher à `H052`.

## Sources primaires actuellement pertinentes

**Hao & Li 2018 — doi:10.3389/feart.2018.00180.** Des expériences en autoclave font réagir komatiite, péridotite et basalte avec un système H2O-CO2 entre 200 et 500 °C pour simuler l'interaction entre la croûte rocheuse post-océan magmatique et la proto-atmosphère. Des phases secondaires et des gaz sont mesurés. C'est le support le plus direct pour l'existence expérimentale d'une interface réactive croûte-fluides-gaz dans un contexte explicitement Terre primitive.

**Ueda et al. 2021 — doi:10.1029/2021GC009827.** Des expériences hydrothermales sur komatiite synthétique et eau de mer hadéenne riche en CO2 suivent la chimie des fluides à plusieurs températures. Elles renforcent la partie « gradients / chimie de l'interface ».

**Lazar et al. 2012 — doi:10.1016/j.chemgeo.2012.07.019.** La serpentinisation expérimentale de komatiites produit du méthane abiotique et explore le rôle catalytique de minéraux accessoires. Cette source soutient la plausibilité d'une capacité catalytique, sans isoler assez proprement un mécanisme unique pour promouvoir HC02 à elle seule.

## Ce qui manque encore pour une promotion canonique

Le label `N030` est « Interfaces eau roche gaz » mais sa capacité principale est « gradients et catalyse ». Les sources ci-dessus soutiennent fortement l'interface réactive et la chimie/les gradients. Le mot **catalyse** doit encore être relié de façon suffisamment directe à la même chaîne, sans affaiblir silencieusement la définition du nœud.

Le verdict courant reste donc : **HC02 candidat, 46/53 canonique**. Le test de sensibilité 53/53 est un résultat structurel, pas une preuve de l'occurrence naturelle complète.
