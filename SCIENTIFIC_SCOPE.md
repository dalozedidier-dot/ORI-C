# Portée scientifique de l’archive canonique

Cette archive utilise des observations, des reconstructions publiées et des intégrations numériques explicitement identifiées dans ses campagnes réelles.

GISTEMP v4 est une reconstruction observationnelle de l’anomalie de température accompagnée d’un ensemble d’incertitude. Les membres de cet ensemble ne sont ni des modèles climatiques indépendants ni des scénarios d’émissions. GISTEMP permet donc un audit observationnel et une description de l’incertitude. Il ne suffit pas à conclure à une hystérésis climatique, à un dépassement, à une réversibilité après arrêt des émissions ou à une réponse au retrait du CO₂. Les moteurs exigeant ces expériences restent bloqués lorsque les variables nécessaires manquent.

Le jeu NASA Exoplanet Archive sert à une analyse démographique des solutions publiées `default_flag=1`. Il ne justifie aucune inférence automatique sur l’habitabilité, la composition interne ou la causalité.

Les données biologiques sont séparées par protocole. Windels documente des cycles d’exposition à l’amikacine. D’Onofrio fournit 288 mesures permettant de comparer état seul, état + histoire et histoire permutée de même complexité. Les douze classeurs de vésicules contiennent des cartes donneur-receveur et produisent 11 760 couples parent-descendant. Papastavrou, Horning et Joyce documentent des fréquences de séquences d’ARN catalytique sur plusieurs cycles, sans généalogie de compartiments. Aucun verdict obtenu sur l’un de ces jeux ne doit être étendu aux autres.

La couche astronomique conserve l’intégration N-corps et ses validations séparées. Le témoin N-corps maximal contient déjà les huit planètes, de Mercure à Neptune ; un contrôle séparé ajoute Pluton et cinq astéroïdes. Une couche distincte, `couche_spin_orbite/`, propage maintenant la normale orbitale N-corps jusqu’au spin, à l’obliquité et à l’insolation. Elle utilise `α = 54,93″/an` comme couple luni-solaire effectif et `α ≈ 20″/an` pour l’ablation lunaire, puis confronte le témoin à La2004. À 1 Ma, l’obliquité calculée atteint une corrélation de 0,9899 avec La2004 pour une RMSE de 0,079°. Cette couche reste un modèle séculaire : l’orbite lunaire et les marées ne sont pas résolues. La distinction de références est conservée : La2010 sert à la validation orbitale N-corps, La2004 à l’obliquité et à l’insolation.

La campagne consolidée reste exploratoire lorsque aucun critère confirmatoire n’a été gelé. Une réussite technique signifie qu’un moteur a traité ses données. Elle ne vaut pas soutien scientifique d’ORI-C.

## Portée de la campagne maximale sur les trois branches

La campagne `plan_directeur/campagne_maximale_trois_branches/` est une
post-analyse des données, modèles et sorties déjà présents. Elle n'ajoute ni
nouvelle observation, ni nouvelle intégration N-corps, ni expérience
biologique. Elle mesure la robustesse de résultats existants et localise les
blocages qui ne peuvent plus être levés par un calcul supplémentaire.

Dans la branche matière, la projection paire à paire et la fermeture
hypergraphique stricte répondent à deux questions différentes. La première
relie les 53 nœuds, tandis que la seconde n'en atteint que 46 parce qu'elle
exige toutes les entrées de chaque processus. Cet écart est une propriété de la
représentation publiée, pas la preuve qu'un processus naturel est impossible.
La suppression d'une hyperarête ou d'un nœud mesure la fragilité de cette
représentation. Elle ne démontre pas qu'une transformation naturelle dépend
d'un chemin physique unique. Les retraits unitaires des coefficients de partage
testent la dépendance aux valeurs présentes dans le dossier. Ils ne remplacent
pas une méta-analyse de la littérature expérimentale.

Dans la branche Système solaire, la comparaison entre les interventions et les
écarts de pas ou d'intégrateur retenus confirme que les effets calculés ne sont
pas de simples artefacts numériques de ces contrôles. Elle ne couvre pas les
erreurs dues aux simplifications physiques du modèle. Les bandes de 405 ka et
2,4 Ma ne sont pas interprétées à partir des interventions limitées à 2 Ma. La
part dite inexpliquée de la bande de 100 ka est un diagnostic descriptif de
puissance relative, pas une fraction causale du climat.

Dans la branche vivant, la campagne maximale historique sur l’amikacine reste non concluante dans son protocole propre. Elle ne résume plus l’état courant de la branche. La campagne suivante ajoute un jeu antibiotique externe D’Onofrio où l’histoire bat l’état seul et un témoin d’histoire permutée, ainsi que des lignées de vésicules où les quatre composantes préenregistrées sont soutenues. Les fréquences ARN restent un troisième protocole distinct consacré à la dynamique de composition.

Les 21 tests de régression de cette campagne vérifient que les scripts
reproduisent les résultats publiés et conservent les limites annoncées. Ils ne
sont pas 21 preuves scientifiques indépendantes.

## Portée du protocole transversal `X/m/A`

`plan_directeur/PROTOCOLE_CAUSALITE_ARCHITECTURALE_XMA.md` est un patron
méthodologique prospectif. Il formalise une séquence commune : architecture et
état définis, intervention explicite sur `A` ou `m`, réponse future mesurée,
témoin de complexité appariée, séparation de l'effet et du bruit, puis
réplication. Il ne crée aucun soutien scientifique par lui-même.

`C-AST-01` illustre ce patron dans un modèle N-corps réduit et reste
`E4_modele`. D’Onofrio reste `E2`. L'ablation des vésicules reste `E4` dans son
protocole actuel. Le résultat négatif de `C-MAT-MEM-05` et la fermeture de M2
restent inchangés. Toute nouvelle instanciation doit être préenregistrée
séparément et ne peut hériter du verdict d'une autre branche.

## Portée du calibrage v0.9.4

Le calibrage permet de trier les relations documentaires faibles, les voies uniques, les relations redondantes, les hyperarêtes critiques par ablation et les cycles d’entretien mutuel. Il ne mesure pas encore la nécessité empirique, la suffisance, la temporalité quantitative, la réversibilité physique ni l’effet d’une intervention directe.

Le noyau stable obtenu est conditionnel aux conventions de stress publiées. Il ne doit pas être présenté comme une probabilité de vérité ou comme une validation universelle de l’architecture matérielle.

## Portée des tests de recherche suivants

La campagne de recherche suivante ajoute des tests ciblés, sans étendre automatiquement les conclusions existantes.

- le seuil de `H011` est soutenu dans les simulations publiées ;
- le cycle des interfaces reste ancré mais non fermé dans une trajectoire unique ;
- `Pacc` est mesuré dans le domaine des six interventions astronomiques calculées ;
- `WP-C2b` est un protocole gelé avec points non saturés et graines réservées ;
- le jeu D’Onofrio soutient l’histoire contre l’état seul et l’histoire permutée ;
- les vésicules soutiennent les quatre composantes préenregistrées sur 11 760 couples parent-descendant ;
- l’audit des spéléothèmes est exécuté sur 27 721 couples âge-isotope.

Les données nécessaires à ces tests sont intégrées et les analyses s’exécutent hors ligne dans le dépôt.

## Formalismes importés, portée scientifique

Les ponts vers théorie de la viabilité, PID, états causaux finis, Chemical Organization Theory, topologie persistante, CCM, LTEE et Assembly Theory sont des **extensions méthodologiques**. Ils ne modifient pas les certifications `C-AST-01`, `C-ANT-01`, `C-VES-02`, `C-VES-03` ou le verdict négatif `C-MAT-MEM-05`. Le PCMCI+ est isolé dans une CI dédiée et reste exploratoire. M2 reste fermé dans sa formulation testée.

## Développement post-publication : généalogie cosmique quantitative

`01_branche_matiere/genealogie_cosmique_quantitative/` est une extension de recherche de la branche matière, pas une nouvelle certification globale et pas une modification rétroactive de `v0.9.5-research`. Elle relie 23 stades depuis les produits de nucléosynthèse stellaire jusqu'au raccordement avec l'architecture orbitale actuelle. Les sources et sorties distinguent systématiquement échantillon direct, chronométrie/reconstruction isotopique, analogue astrophysique, simulation et modèle.

La présence de grains présolaires, d'hétérogénéités isotopiques, de glaces héritées ou de mécanismes de formation des planétésimaux soutient des maillons locaux. Elle n'établit pas une histoire unique du Système solaire. Les scénarios de structuration du disque, de croissance des géantes, de migration et d'instabilité restent concurrents dans `MODELES_CONCURRENTS.csv`. Le verdict end-to-end reste `open_not_certified` et l'interface `HANDOFF_SYSTEME_SOLAIRE.json` reste `open` tant que la branche ne dérive pas les conditions initiales de `C-AST-01` avec leurs incertitudes.

## Snapshot stable 0.9.5-research

La publication stable du 10 août 2026 conserve explicitement la dissymétrie des résultats : la couche astronomique N-corps reste à **13/15**, tandis que la formulation paléoclimatique M2 reste à **1/10** et `does_not_support` dans son protocole. La couche spin-orbite est exécutée au niveau modèle mais ne résout pas la Lune en N-corps ni les marées. Le résultat PCMCI+ est exploratoire, fondé sur des p-values brutes dans la configuration publiée, et ne modifie pas M2. Les formalismes externes ne reclassent aucune certification par leur seule exécution.
