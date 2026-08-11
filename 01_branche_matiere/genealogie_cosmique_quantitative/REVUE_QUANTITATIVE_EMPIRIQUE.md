# Revue quantitative empirique approfondie — v2

Cette couche n’utilise **ni simulation, ni donnée synthétique, ni imputation, ni rendement stellaire théorique, ni sortie thermochimique**. Elle travaille directement sur le registre empirique de la branche et distingue résultat quantitatif, audit de robustesse et limite d’identifiabilité.

## Base de données d’autorité

La branche contient désormais **38 sources primaires/officielles** et **90 enregistrements de mesures réelles** répartis sur les 20 stades empiriques. Les 16 claims `C-GC-E*` restent l’autorité de synthèse empirique : 15 sont soutenus et l’histoire orbitale détaillée unique reste `undetermined_empirical_only`.

Cinq renforcements empiriques ont été ajoutés sans changer le pare-feu :

- EC 53 : suivi temporel JWST du même objet, avec forstérite et enstatite détectées pendant le burst et absentes dans l’état quiescent retenu pour la comparaison ;
- Ryugu : systématique Lu–Hf d’échantillons retournés enregistrant une circulation de fluide plus de 1 Gyr après la formation ;
- VLA1623 B : second système indépendant avec un streamer protostellaire d’environ 2 000 au et une température d’excitation SO de 33 ± 9 K ;
- SN 1987A : une seconde campagne instrumentale primaire, ALMA, résout spatialement la poussière dans les éjecta internes et fournit une borne >0,2 M☉ ;
- CAI/chondres : une seconde chronométrie primaire Al-Mg fournit un cross-check d’environ 2 Myr après les CAI canoniques, sans être artificiellement convertie en mesure >5σ.

Les interprétations dépendantes de modèles présentes dans ces publications sont explicitement exclues du registre machine.

## Pourquoi la v1 n’est plus l’autorité quantitative

La v1 avait ajouté 23 stades analytiques, 40 relations, une sélection de 24 observations et 12 synthèses. Ces objets sont conservés pour provenance, mais leurs **comptages ne constituent pas un résultat scientifique**. Leur statut est documenté dans `STATUT_APPROFONDISSEMENT_V1.md`.

La v2 remplace cette logique de comptage par huit tests/audits reproductibles `GCQ-T01` à `GCQ-T08`.

## Résultats quantitatifs v2

### GCQ-T01 — réplication inter-missions des grains présolaires

Les abondances SiC mesurées dans Bennu et Ryugu sont toutes deux nominalement de 25 ppm. L’écart standardisé descriptif est donc 0. Pour les grains O-rich/O-anormaux, Bennu = 4 ± 2 ppm et Ryugu = 4,8 ppm avec incertitude asymétrique publiée ; l’écart standardisé descriptif calculé par la campagne vaut environ 0,19. Ces comparaisons soutiennent une cohérence inter-missions des ordres de grandeur sans être traitées comme une méta-analyse populationnelle.

### GCQ-T02 — eau lourde V883 Ori / 67P

Le produit des deux rapports ROSINA mesurés pour 67P donne `D2O/H2O = 1,89×10^-5` avec propagation des incertitudes publiées. Comparé à V883 Ori, l’écart standardisé vaut environ 0,85, donc inférieur à 2. Le résultat soutient une compatibilité observationnelle, sans établir une filiation directe entre les deux systèmes.

### GCQ-T03 — ordre chronologique du Système solaire primitif

Quatre écarts sont calculés avec propagation conservative des erreurs publiées :

- CAI → EC 002 : ~1,74 Myr, ~8,7σ ;
- CAI → angrite : ~1,10 Myr, ~5,83σ ;
- CAI → plus jeune chondre sélectionné : ~2,59 Myr, ~7,62σ ;
- angrite → carbonate CM : ~2,80 Myr, ~5,49σ.

La séquence temporelle utilisée par la branche n’est donc plus seulement narrative : plusieurs ordres sont quantitativement résolus au-delà de 5σ dans les données sélectionnées.

### GCQ-T04 — changement d’état dans le même objet

EC 53 apporte un test temporel plus fort qu’un simple analogue inter-systèmes : les signatures de forstérite et d’enstatite retenues sont absentes en quiescence et présentes pendant le burst. La branche code ce résultat comme **association événement–changement d’état dans le même système**, sans prétendre observer le transport ultérieur de ces grains.

### GCQ-T05 — réplication des streamers

Deux systèmes indépendants présentent des structures de type streamer à l’échelle de milliers d’au : Per-emb-2 (>10 500 au) et VLA1623 B (~2 000 au). Cela renforce l’existence observationnelle du canal physique nuage/environnement → échelles du disque, sans l’identifier à l’histoire protosolaire.

### GCQ-T06 — réactivation tardive d’un corps primitif

Ryugu conserve une archive isotopique d’une circulation de fluide **plus de 1 000 Myr après la formation**. Ce résultat montre qu’un corps primitif peut subir une transformation historique tardive et en conserver une trace mesurable. La cause dynamique proposée dans l’article n’est pas importée comme preuve.

### GCQ-T07 — robustesse du graphe empirique

Sur 22 liens, 12 sont classés comme séquences d’archive, continuités matérielles, mêmes systèmes ou mêmes histoires ; 9 restent analogues/non uniques et 1 est un contraste historique. Une séquence stricte d’archives relie les produits stellaires à un endpoint planétaire actuel, mais **la fermeture stricte depuis la baseline primordiale jusqu’à l’endpoint reste ouverte**.

### GCQ-T08 — ablations par familles de preuve

Chaque famille de preuve est retirée à tour de rôle et la campagne recalcule la couverture des stades et la persistance de la séquence stricte. Il s’agit d’un audit de dépendance du corpus, pas d’une simulation physique. Les résultats sont enregistrés dans `resultats/ABLATIONS_FAMILLES_PREUVES.csv`.

## Verrous résiduels

Sept stades restent soutenus par une seule source dans la version actuelle : `GC-E11`, `GC-E12`, `GC-E13`, `GC-E16`, `GC-E17`, `GC-E18` et `GC-E19`. La fermeture de bout en bout n’est donc pas certifiée. La priorité scientifique suivante n’est pas d’ajouter des relations théoriques : elle consiste à **répliquer empiriquement les stades à source unique** et à remplacer, quand c’est possible, les ponts analogues par des archives solaires ou des observations temporelles plus directes.

Le verdict quantitatif machine est :

`supports_history_dependent_material_and_temporal_constraints_with_open_end_to_end_closure`
