# Périmètre de recherche ORI-C — publication v0.9.7-research

## Plan directeur central actif

Depuis le 11 août 2026, le point d'entrée opérationnel est
`plan_directeur/campagne_centrale_2026_08_11/`. Il ordonne les trente axes en
quatre campagnes : fermeture mécanistique, quantification, transversalité et
prédiction. Son lanceur publie l'admissibilité des données, les dépendances et
les blocages ; il ne transforme jamais un axe documenté en résultat exécuté.

`PALEO-HISTORY-01` reste prioritaire. Les neuf familles de sources sont
désormais présentes, mais la campagne reste `non_testable` tant que leurs
incertitudes chronologiques et leur table normalisée ne satisfont pas le schéma
gelé. Les défauts d'admission sont publiés dans
`resultats/ADMISSION_PALEO_HISTORY_01.json` ; le protocole reste inchangé.

La gouvernance centrale retient uniquement les travaux qui ferment un verrou,
mesurent `P_acc`, testent un invariant, ajoutent une intervention, fournissent
une réplication, produisent une prédiction prospective ou peuvent falsifier une
hypothèse importante. Le reste demeure dans le backlog.

Le tag `v0.9.6-research` reste gelé comme snapshot antérieur. La publication `v0.9.7-research` conserve la généalogie cosmique quantitative introduite en 0.9.6 et ajoute l’opérationnalisation exécutable de `INV-A`, avec un second système `do(m)` au niveau modèle (`EXO-DOM-01`). Les verdicts antérieurs restent inchangés et cette extension ne transforme pas le résultat modèle en réplication empirique.

| Livrable | État courant | Prochaine étape utile |
|---|---|---|
| D’Onofrio et prédiction antibiotique prospective | D’Onofrio reste le **benchmark externe rétrospectif positif** : RMSE 1,1309 état seul, 0,8042 avec histoire, p = 0,00498. Santos-Lopez 2021 donne dans un benchmark séparé RMSE 0,937482 contre 0,732492, gain 21,866 %, bootstrap 95 % [7,235 % ; 33,967 %], p ≈ 0,00020. Ce second résultat reste rétrospectif : la spécification propre au jeu a été fixée après son ouverture et il ne ferme ni §XIV-3 ni §XIV-10. | conserver `PRED-VIVANT-HISTOIRE-001` intact et attendre un nouveau jeu longitudinal indépendant tenu caché jusqu’au gel complet et au préenregistrement public |
| Recodage indépendant des dimensions matière | à exécuter | accord inter-codeurs sur un échantillon gelé |
| Ablation matérielle prospective | `MAG-PAIR-001` est retenu comme premier protocole physique pour `PRED-MATIERE-ABLATION-001`; aucune mesure confirmatoire n’existe encore | geler laboratoire, palier AF, champ test, randomisation, aveugle et analyse avant la première mesure |
| Environnement astronomique reproductible | résultat scientifique obtenu, CI reproductible, `C-AST-01` à `E4_modele` | conserver cette couche comme référence méthodologique du patron causal, sans transférer son niveau de preuve aux autres branches |
| Protocole climatique remplaçant M2 | M2 fermé comme formulation ; M1P a correctement joué le rôle de témoin de complexité appariée | définir une nouvelle architecture de mémoire avant analyse, isoler `m` autant que les données le permettent et conserver le témoin apparié et les contrôles négatifs réels |
| Mesure commune de `Pacc` | Plusieurs mesures locales existent mais **aucune ne ferme la condition empirique §XIV-9 dans les trois branches**. `VES-PACC-INT-01` est désormais scientifiquement gelé : `do(m)` par 11 passages 100 nm, sham 5 µm, 48 populations parentales, 12 défis, 4 dimensions et SESOI `|ΔP_acc|=0,08`. Il reste non exécuté et administrativement bloqué avant préenregistrement public. | déposer publiquement le paquet VES avec ses SHA-256 avant toute nouvelle donnée, puis exécuter exactement le protocole gelé |

Les cinq livrables utilisent désormais le même patron expérimental : définir `X/m/A`, intervenir sur le levier causal annoncé, mesurer une réponse future, battre un témoin de complexité appariée, séparer l'effet du bruit et répliquer. Pour la mémoire, l'intervention doit porter sur `m` et non simplement modifier `X`. Ce patron est défini dans `plan_directeur/PROTOCOLE_CAUSALITE_ARCHITECTURALE_XMA.md` et ne crée aucun verdict par lui-même.

## Seuil scientifique §XIV : porte active

L’audit exécutable `plan_directeur/campagne_centrale_2026_08_11/evaluer_seuil_xiv.py` reproduit l’état courant du plan : **7 conditions sur 12** sont remplies. Les conditions ouvertes sont **3, 4, 9, 10 et 11** : prédiction propre hors échantillon par branche, victoire contre témoin apparié, `Pacc` causal empirique par branche, deux reproductions strictes par équipes indépendantes et un résultat traversant deux branches sans redéfinition. La sortie machine `resultats/SEUIL_XIV.json` est diagnostique et fail-closed : une validation croisée rétrospective, un proxy observationnel ou un résultat de modèle ne peut fermer ces conditions.

La définition `PACC-INT-CHALLENGE-V1` est implémentée dans `methodologie_puissance/pacc_causal.py` et documentée dans `protocoles_geles/PACC_INTERVENTIONNEL_V1.md`. Elle remplace **pour les futurs tests causaux** le comptage de classes observées qui se sature avec la longueur de série ; elle ne réécrit aucun `Pacc` historique déjà publié.

Dans la branche astronomique, le module **spin-orbite réduit est désormais exécuté** : la normale orbitale N-corps force un axe de spin dynamique, le témoin avec couple lunaire effectif est confronté à La2004, l'ablation lunaire est calculée et les six interventions Jupiter/Saturne sont propagées jusqu'à l'insolation. Les priorités restantes sont maintenant les interventions symétriques Uranus/Neptune, l'extraction explicite des modes `g_i/s_i`, une réplication indépendante du module de spin, puis une Terre-Lune explicitement résolue avec marées si l'on veut traiter l'évolution tidale longue durée.

Les lignées de vésicules ne sont plus une donnée manquante. La campagne analyse **11 760 couples parent-descendant** et soutient les quatre composantes préenregistrées de sélection, filiation, ablation et codage des lignées. Elle mesure désormais aussi un `P_acc` rétrospectif moyen de **0,66** sur 100 strates. Le test exploratoire de ce support autour de l’ablation donne un contraste FR moins contrôles de **−0,0375**, intervalle bootstrap [−0,1458 ; 0,0625] : il ne soutient pas la direction positive attendue et reste distinct du contraste de réponse `C-VES-03`. Les données ARN constituent un autre protocole et leur absence de filiation ne doit jamais être étendue aux vésicules ni à toute la branche vivant.

La chaîne `Histoire → Architecture → Contraintes → Réponse → Inscription → Possibilités` organise les mécanismes déjà mesurés. Les prochains travaux doivent relier davantage de termes dans un même protocole, sans effacer les résultats locaux déjà établis.

Trois règles s’appliquent à tout rapport :

1. un résultat négatif reste limité au jeu de données, au modèle et au témoin qui l’ont produit ;
2. des jeux distincts ne sont jamais fusionnés dans un verdict de branche, notamment amikacine, Card 2019, D’Onofrio, ARN et vésicules ;
3. l’état courant des preuves prime sur les synthèses historiques antérieures à la campagne de recherche suivante.

## Puissance statistique a priori

Tout nouveau protocole lié aux cinq livrables doit être accompagné d’un `POWER_PLAN.json` gelé avant l’acquisition ou avant l’ouverture du jeu tenu à l’écart. Ce plan déclare le SESOI et sa justification scientifique, `alpha`, la puissance cible, l’unité réellement indépendante, la taille disponible ou nécessaire, l’estimation du bruit, le test, les témoins et la règle conjointe de succès.

Les folds de validation croisée ne sont jamais comptés comme observations indépendantes. La simulation Monte-Carlo doit générer les observations ou trajectoires puis réexécuter le pipeline complet, y compris les groupes, les dépendances temporelles, les ablations, les témoins de même complexité, les permutations et le verdict final.

La taille nécessaire est retenue lorsque la borne inférieure de l’intervalle de Wilson atteint la puissance cible après au moins 10 000 simulations de confirmation. Lorsque la taille est déjà fixée, le protocole rapporte le plus petit effet détectable à 80 % ou 90 % de puissance. Une puissance recalculée après observation du résultat ne constitue pas une preuve.

Le format, le validateur et le moteur commun se trouvent dans `methodologie_puissance/`.

## Nouveau front d'intégration formelle

Les tâches purement prospectives ont été remplacées par des modules exécutables lorsque les données le permettent : viabilité de trajectoire sur spin-orbite, PID D'Onofrio, états prédictifs finis, topologie persistante, puissance conjointe matière, CCM et réanalyse LTEE. COT et Assembly Theory restent explicitement non évaluables sur les objets courants faute de stœchiométrie ou d'observables appariées. Les deux hypothèses séparantes du cadre sont enregistrées comme candidates et non comme lois.

### Priorité structurante : raccordement empirique Big Bang chaud → architecture solaire

La couche `01_branche_matiere/genealogie_cosmique_quantitative/` est désormais **strictement empirique** : 20 stades, 22 liens qualifiés, 48 sources primaires/officielles, 120 enregistrements empiriques historiques, auxquels s’ajoute une couche de **11 467 lignes normalisées utiles dont 11 207 grains présolaires admissibles**, avec 15 claims empiriques initiaux soutenus et 1 limite ouverte. Son audit machine impose **0 simulation, 0 donnée synthétique, 0 imputation**.

Le travail prioritaire n’est plus d’ajouter des scénarios de formation. Il consiste à renforcer les continuités matérielles et isotopiques observables : produits stellaires → poussières → grains présolaires retournés → glaces/molécules → réservoirs et chronologie du disque solaire → petits corps → histoires planétaires. La branche atteint l’architecture actuelle comme endpoint observationnel, tout en laissant `undetermined_empirical_only` la reconstruction d’une trajectoire orbitale unique. Aucun modèle n’est autorisé à combler ce trou.

`C-AST-01` demeure séparé : il teste l’efficacité causale d’une architecture déjà donnée au niveau modèle et ne sert pas de preuve de sa genèse.

## Frontière de publication stable 0.9.7-research

Le snapshot stable du 12 août conserve N-corps **13/15**, spin-orbite exécuté et reproductible, M2 **1/10** et non soutenu. Il porte désormais le benchmark transversal à **21 cas**, **6 claims complets** et **5 systèmes distincts**, dont **2 systèmes avec intervention directe sur `m`**. `EXO-DOM-01` soutient un effet local `do(m) -> Delta P_acc` au niveau modèle avec `X/Theta/A` appariés ; la porte transversale générale reste fermée. Les prochains travaux doivent viser une nouvelle réplication empirique `do(m)` indépendante, sans réécrire les verdicts existants.

## Mise à jour opérationnelle du 13 août 2026 — Pacc causal et préenregistrement

`PACC-INT-CHALLENGE-V1` a désormais passé un test de sanité machine sur `EXO-DOM-01`. La nouvelle implémentation restitue `P_acc = 0,91 -> 0,87`, `Delta P_acc = -0,04` et sham nul à partir des réponses défi×dimension. Ce contrôle valide le comportement de l'outil sur un cas modèle déjà connu ; il ne relève pas `EXO-DOM-01` au-dessus de `E4_modele` et ne ferme pas le §XIV-9.

La priorité empirique vivant est `VES-PACC-INT-01`. Le protocole prospectif est installé dans `03_branche_vivant/lignees_vesicules/PROTOCOLE_PACC_CAUSAL_PROSPECTIF_V1.*`. Les 11 760 couples historiques restent calibration/conception uniquement. Les champs scientifiques sont désormais gelés : opérateur `do(m)`, sham, niveaux ciblés, défis `Theta`, dimensions `R`, seuils, SESOI, puissance et unités indépendantes. La porte d'exécution reste fermée uniquement tant que la fiche administrative n'atteste pas l'enregistrement public préalable. Le schéma d'entrée et le préparateur canonique des tables de laboratoire sont installés sans ouvrir cette porte ni produire de donnée de test.

Les quatre prédictions prospectives disposent de paquets de registration OSF. Pour qu'un futur résultat compte comme réussite stricte du §XIV-3, le protocole doit désormais être non seulement gelé avant les données, mais aussi enregistré publiquement avant leur ouverture. Le §XIV reste donc à **7/12**, avec les verrous `3, 4, 9, 10, 11` inchangés.

## Mise à jour opérationnelle du 14 août 2026 — fermeture et lisibilité

La roadmap active est désormais `ROADMAP.md`. Elle réduit le programme à quatre fronts capables de changer le niveau de preuve : `VES-PACC-INT-01`, le verrou matière `H052/HC01`, `PRED-VIVANT-HISTOIRE-001` et `MAG-PAIR-001`. Cette couche d'orientation ne remplace ni les prédictions gelées ni l'audit §XIV.

Le verrou `H052` a fait l'objet d'un audit ciblé dans `01_branche_matiere/hypergraphe_transformations/fermeture_stricte/AUDIT_H052_2026-08-14.*`. Le verdict reste **46/53** : Okamoto et al. 2025 soutient un mécanisme auto-généré de fracture/permeabilité sur analogue expérimental, Alexander et al. 2026 soutient la création de perméabilité de croûte primitive au niveau modèle, mais aucune source ne suffit encore à promouvoir `HC01` comme relation empirique canonique.

La couche publique gagne une page `site/exploration.html` qui expose uniquement des tables versionnées, des scénarios N-corps déjà calculés et un modèle jouet explicitement pédagogique. La CI vérifie désormais aussi la démonstration minimale reproductible, le registre de preuves, le contrôle négatif réel et la synchronisation des données de cette page interactive.

## Mise à jour opérationnelle du 14 août 2026 — noyau externe et portes fail-closed

La lecture externe courte est désormais `CORE_RESULTS.md` : 16 résultats tirés du registre d’autorité, avec succès, résultats négatifs, non-concluants et résultats de modèle conservés sous leur statut exact. `GETTING_STARTED_10_MIN.md` donne le chemin minimal de reproduction et trois notebooks de branche complètent le notebook général.

La démonstration astronomique distingue maintenant deux quantités auparavant présentées sous le même mot « plancher » : le ratio certifié de `C-AST-01` (**4 964,415...**) est recalculé depuis le plus grand écart numérique sélectionné de la campagne de robustesse, tandis que `effect_to_ensemble_floor_ratio` reste un diagnostic séparé du CSV contrefactuel. Les deux analyses biologiques continuent d’être réexécutées depuis les données versionnées.

Côté causal prospectif, `MAG-PAIR-001` possède un paquet d’exécution machine complet jusqu’aux paramètres qui dépendent réellement du laboratoire. L’analyse et la préparation refusent toute donnée tant que le laboratoire, le palier AF, le champ test, les températures, la randomisation, l’aveugle et les règles opérationnelles ne sont pas gelés et enregistrés publiquement. `PRED-VIVANT-HISTOIRE-001` dispose en parallèle d’un registre des jeux déjà vus qui exclut explicitement D’Onofrio, Card 2019 et Santos-Lopez 2021 du futur test strict.
