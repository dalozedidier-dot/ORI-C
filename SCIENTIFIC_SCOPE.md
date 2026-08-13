# Portée scientifique de l’archive canonique

Cette archive utilise des observations, des reconstructions publiées et des intégrations numériques explicitement identifiées dans ses campagnes réelles.

GISTEMP v4 est une reconstruction observationnelle de l’anomalie de température accompagnée d’un ensemble d’incertitude. Les membres de cet ensemble ne sont ni des modèles climatiques indépendants ni des scénarios d’émissions. GISTEMP permet donc un audit observationnel et une description de l’incertitude. Il ne suffit pas à conclure à une hystérésis climatique, à un dépassement, à une réversibilité après arrêt des émissions ou à une réponse au retrait du CO₂. Les moteurs exigeant ces expériences restent bloqués lorsque les variables nécessaires manquent.

Le jeu NASA Exoplanet Archive sert à une analyse démographique des solutions publiées `default_flag=1`. Il ne justifie aucune inférence automatique sur l’habitabilité, la composition interne ou la causalité.

Les données biologiques sont séparées par protocole. Windels documente des cycles d’exposition à l’amikacine. D’Onofrio fournit 288 mesures permettant de comparer état seul, état + histoire et histoire permutée de même complexité. Santos-Lopez 2021 est conservé dans un dossier distinct comme benchmark externe rétrospectif et non comme réussite prospective. Les douze classeurs de vésicules produisent 11 760 couples parent-descendant. Papastavrou, Horning et Joyce documentent des fréquences de séquences d’ARN catalytique sans généalogie de compartiments. Aucun verdict obtenu sur l’un de ces jeux ne doit être étendu aux autres.

La couche astronomique conserve l’intégration N-corps et ses validations séparées. Le témoin N-corps maximal contient déjà les huit planètes, de Mercure à Neptune ; un contrôle séparé ajoute Pluton et cinq astéroïdes. Une couche distincte, `couche_spin_orbite/`, propage maintenant la normale orbitale N-corps jusqu’au spin, à l’obliquité et à l’insolation. Elle utilise `α = 54,93″/an` comme couple luni-solaire effectif et `α ≈ 20″/an` pour l’ablation lunaire, puis confronte le témoin à La2004. À 1 Ma, l’obliquité calculée atteint une corrélation de 0,9899 avec La2004 pour une RMSE de 0,079°. Cette couche reste un modèle séculaire : l’orbite lunaire et les marées ne sont pas résolues. La distinction de références est conservée : La2010 sert à la validation orbitale N-corps, La2004 à l’obliquité et à l’insolation.

La campagne consolidée reste exploratoire lorsque aucun critère confirmatoire n’a été gelé. Une réussite technique signifie qu’un moteur a traité ses données. Elle ne vaut pas soutien scientifique d’ORI-C.

Le seuil scientifique interne du §XIV est maintenant audité par machine. L’état courant reste **7/12** : les conditions 3, 4, 9, 10 et 11 sont ouvertes. Aucune validation croisée sur un jeu déjà publié n’est comptée comme prédiction prospective propre. Aucun proxy de classes observées n’est compté comme `Pacc` causal. Un résultat de modèle ne ferme pas une condition empirique et une réplication conceptuelle ne remplace pas une reproduction stricte par une équipe indépendante.

La définition interventionnelle `PACC-INT-CHALLENGE-V1` fixe pour les futurs tests causaux un dénominateur de défis × dimensions déclaré avant observation, avec `X`, `Theta` et l’architecture non ciblée appariés, intervention sur `m`, sham et unités indépendantes. Elle ne requalifie pas les mesures rétrospectives déjà présentes dans le dépôt.

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

## Généalogie cosmique quantitative intégrée à 0.9.6-research

`01_branche_matiere/genealogie_cosmique_quantitative/` est une extension empirique de la branche matière, développée après `v0.9.5-research` et intégrée à `v0.9.6-research`. Elle ne transforme aucune certification existante.

**Politique de preuve : données réelles uniquement.** Sont admis les observations astronomiques/spatiales, échantillons retournés, mesures isotopiques et chronométriques, expériences de laboratoire, reconstructions planétaires fondées sur des isotopes mesurés et produits observationnels officiels. Sont exclus des verdicts : simulation, donnée synthétique ou construite, imputation, sortie numérique de modèle, rendement stellaire théorique, calcul thermochimique et intégration orbitale.

La couche courante couvre **20 stades, 22 liens qualifiés, 48 sources/datasets empiriques admissibles et 120 enregistrements empiriques historiques**. Elle ajoute **11 467 lignes utiles normalisées**, dont **11 207 grains présolaires admissibles**, et conserve **15 résultats empiriques initiaux soutenus et 1 limite ouverte**. Les continuités matérielles directes, les archives du même Système solaire, les analogues astrophysiques et les expériences de laboratoire sont marqués séparément ; un analogue inter-systèmes n'est jamais présenté comme l'histoire observée du Soleil.

Le résultat global `supports_empirical_historical_accessibility_mechanism` signifie que des constituants, poussières, grains présolaires, molécules, isotopes, réservoirs, âges, structures et histoires d'accrétion conservent des conséquences mesurables d'étapes antérieures. Il soutient le mécanisme d'inscription historique formulé par ORI-C. Il ne démontre ni une loi universelle ni une trajectoire cosmologique/orbitale unique.

L'endpoint planétaire actuel est observé. Le chemin orbital précis qui y conduit reste `undetermined_empirical_only`. `C-AST-01` et les autres résultats de modèle restent hors du décompte empirique de cette branche.

## Snapshot stable 0.9.7-research

La publication stable du 12 août 2026 conserve explicitement la dissymétrie des résultats : la couche astronomique N-corps reste à **13/15**, tandis que la formulation paléoclimatique M2 reste à **1/10** et `does_not_support` dans son protocole. La couche spin-orbite est exécutée au niveau modèle mais ne résout pas la Lune en N-corps ni les marées. Le benchmark transversal compte **21 cas**, **6 claims complets** et **5 systèmes distincts**. Deux systèmes possèdent un `do(m)` direct ; `EXO-DOM-01` mesure au niveau modèle `P_acc = 0,91` contre `0,87` sous intervention ciblée de `m`, avec `X/Theta/A` appariés et sham nul. Ce résultat ne constitue pas une réplication empirique et `INV-A` reste exploratoire non validé transversalement. Le résultat PCMCI+ est exploratoire, fondé sur des p-values brutes dans la configuration publiée, et ne modifie pas M2. Les formalismes externes ne reclassent aucune certification par leur seule exécution.

### Généalogie cosmique — approfondissement quantitatif empirique
La branche `01_branche_matiere/genealogie_cosmique_quantitative/` conserve son autorité empirique (48 sources/datasets admissibles, 120 enregistrements historiques et 16 claims empiriques initiaux) et ajoute une couche quantitative fondée sur 11 467 lignes utiles normalisées, toutes dérivées exclusivement de mesures admises. Aucune simulation, donnée synthétique, imputation, rendement théorique ou sortie thermochimique n’entre dans ces résultats.

## Pacc causal : validation de l'outil et prochain test empirique

La définition `PACC-INT-CHALLENGE-V1` est l'estimateur strict pour les futurs tests causaux d'accessibilité. Son test de sanité sur `EXO-DOM-01` reproduit exactement le contraste modèle déjà gelé, sans modifier son niveau de preuve. Aucun proxy rétrospectif et aucun résultat de modèle ne compte comme mesure empirique de la condition 9 du §XIV.

Le cas vésiculaire historique reste un cas empirique rétrospectif complet mais non prospectif pour `P_acc`. `VES-PACC-INT-01` est désormais scientifiquement gelé : contrôle, extrusion `do(m)` 100 nm en 11 passages, sham 5 µm, `X/Theta/A` appariés, 12 défis, quatre dimensions, seuils gelés, `n=48`, SESOI `0,08` et plan de puissance. L’exécution reste interdite jusqu’au préenregistrement public des empreintes du protocole et du script d’analyse.

Les quatre prédictions prospectives locales ne pourront recevoir le statut de réussite hors échantillon qu'avec une registration publique antérieure aux données de test. Cette exigence est maintenant vérifiée par l'audit exécutable du §XIV.
