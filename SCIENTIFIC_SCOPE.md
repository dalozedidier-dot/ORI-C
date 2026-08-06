# Portée scientifique de l’archive canonique

Cette archive utilise des observations, des reconstructions publiées et des intégrations numériques explicitement identifiées dans ses campagnes réelles.

GISTEMP v4 est une reconstruction observationnelle de l’anomalie de température accompagnée d’un ensemble d’incertitude. Les membres de cet ensemble ne sont ni des modèles climatiques indépendants ni des scénarios d’émissions. GISTEMP permet donc un audit observationnel et une description de l’incertitude. Il ne suffit pas à conclure à une hystérésis climatique, à un dépassement, à une réversibilité après arrêt des émissions ou à une réponse au retrait du CO₂. Les moteurs exigeant ces expériences restent bloqués lorsque les variables nécessaires manquent.

Le jeu NASA Exoplanet Archive sert à une analyse démographique des solutions publiées `default_flag=1`. Il ne justifie aucune inférence automatique sur l’habitabilité, la composition interne ou la causalité.

Les données biologiques sont séparées par protocole. Windels documente des cycles d’exposition à l’amikacine. D’Onofrio fournit 288 mesures permettant de comparer état seul, état + histoire et histoire permutée de même complexité. Les douze classeurs de vésicules contiennent des cartes donneur-receveur et produisent 11 760 couples parent-descendant. Papastavrou, Horning et Joyce documentent des fréquences de séquences d’ARN catalytique sur plusieurs cycles, sans généalogie de compartiments. Aucun verdict obtenu sur l’un de ces jeux ne doit être étendu aux autres.

La couche astronomique conserve l’intégration N-corps et ses validations séparées. La série orbitale réelle utilisée par la campagne est La2004 à 51 001 pas avec excentricité, obliquité et précession. La référence La2010 est conservée séparément et tronquée à son horizon de fiabilité déclaré.

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
