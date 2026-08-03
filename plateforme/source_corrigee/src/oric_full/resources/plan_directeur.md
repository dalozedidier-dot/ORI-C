# Plan directeur complet de tests ORI-C

## Portée

Ce plan couvre l’intégralité du dossier `ORI-C_dossier_unique(10)` :

- le socle commun
- la branche 1, matière
- la branche 2, Système solaire et Terre
- la couche astronomique
- les filtrages historiques planétaires
- la couche mémoire historique et le climat
- l’application climatique séparée
- la branche 3, vivant
- le programme prébiotique
- l’endosymbiose et l’architecture cellulaire
- l’expérience sur la résistance aux antibiotiques
- les tests transversaux de valeur ajoutée d’ORI-C

Les dimensions cognitives et les autres branches formelles annoncées ailleurs ne figurent pas dans cette archive. Elles devront recevoir un protocole séparé lorsqu’elles seront réintégrées.

## Objectif général

Le programme doit passer d’une architecture conceptuelle solide à un ensemble de propositions falsifiables, comparées à des modèles concurrents, testées sur données indépendantes et reproduites par des tiers.

La règle générale est :

**Une affirmation ORI-C = une variable mesurable + un témoin apparié + une intervention ou une comparaison causale + un critère préenregistré + une fenêtre assez longue + une réplication indépendante.**

---

# I. Organisation générale de la campagne

## Étape 0. Geler l’état de départ

1. Conserver la version 10 comme référence historique en lecture seule.
2. Attribuer un identifiant permanent à chaque hypothèse, test, donnée, script et résultat.
3. Créer un registre central `REGISTRE_HYPOTHESES.csv`.
4. Distinguer les analyses exploratoires des tests confirmatoires.
5. Empêcher toute modification des critères après consultation des résultats confirmatoires.
6. Créer un dossier distinct par campagne avec son manifeste SHA-256.
7. Enregistrer les versions de Python, bibliothèques, compilateurs, systèmes et matériels.
8. Produire une image de conteneur reproductible.
9. Exécuter chaque suite sous Linux, Windows et macOS lorsque le code le permet.
10. Répéter les calculs sur deux architectures matérielles différentes.

## Étape 1. Transformer toutes les affirmations en hypothèses testables

Pour chaque proposition du Codebook, des articles et des trois branches, enregistrer :

- identifiant de l’affirmation
- formulation exacte
- domaine concerné
- variables observables
- prédiction ORI-C
- modèle nul
- modèle concurrent
- témoin de complexité égale
- intervention ou contraste causal
- métrique principale
- seuil de réussite
- fenêtre temporelle
- conditions d’arrêt
- données d’apprentissage
- données de validation
- statut final

Aucune proposition générale ne doit recevoir un statut positif à partir d’un exemple unique.

## Étape 2. Appliquer la grille universelle à chaque mécanisme

Chaque mécanisme doit subir les familles de tests suivantes :

1. cohérence mathématique
2. cohérence dimensionnelle
3. identifiabilité
4. sensibilité aux paramètres
5. robustesse aux conditions initiales
6. convergence numérique
7. comparaison à plusieurs algorithmes
8. contrôle positif
9. contrôle négatif
10. témoin instantané
11. témoin historique
12. témoin de complexité égale
13. ablation du mécanisme
14. permutation de l’ordre des événements
15. même état final obtenu par des histoires différentes
16. retrait de la contrainte
17. durée de relaxation
18. hystérésis aller-retour
19. perte de composants ou de chemins de récupération
20. estimation de `Pth`
21. estimation de `Pacc(T,C,ε)`
22. prédiction hors échantillon
23. réplication sur une autre base de données
24. réplication par un autre code
25. réplication par une autre équipe
26. test adversarial conçu pour faire échouer l’hypothèse
27. analyse des cas où ORI-C et le modèle concurrent font la même prédiction
28. analyse des cas où leurs prédictions divergent
29. correction pour comparaisons multiples
30. publication des résultats positifs, négatifs et non concluants

Cette grille est la base commune. Les sections suivantes ajoutent les tests propres à chaque branche.

---

# II. Socle commun

## WP-S1. Définitions et cohérence formelle

### S1.1 Les six dimensions `n, G, I, E, Π, H`

1. Vérifier qu’elles peuvent être codées sans chevauchement complet sur au moins 100 systèmes provenant des trois branches.
2. Mesurer l’accord entre plusieurs codeurs indépendants.
3. Calculer la stabilité du codage après retrait du nom du domaine.
4. Tester des cas limites où une variable peut appartenir à deux dimensions.
5. Comparer une version à six dimensions à des versions réduites à cinq, quatre et trois dimensions.
6. Tester si l’ajout de chaque dimension améliore réellement une tâche de classification ou de prédiction.
7. Mesurer la redondance entre dimensions par information mutuelle et corrélations conditionnelles.
8. Vérifier l’invariance des conclusions sous plusieurs normalisations.

### S1.2 Séparation `X`, `m` et `A`

1. Construire des systèmes synthétiques où la vérité est connue.
2. Produire des changements d’état sans changement d’opérateur.
3. Produire des changements de paramètres structurels.
4. Produire des changements de topologie.
5. Tester si la règle ORI-C classe correctement les trois cas.
6. Comparer cette classification à des méthodes de détection de changement de régime.
7. Tester la dépendance au niveau de description.
8. Mesurer l’accord entre codeurs sur des cas empiriques.
9. Vérifier si un changement classé architectural améliore la prédiction d’une réponse future.
10. Rechercher des faux positifs où une dérive lente de paramètres ressemble à une transformation architecturale.

### S1.3 Mémoire distribuée

1. Simuler une mémoire unique à noyau fixe.
2. Simuler plusieurs mémoires indépendantes.
3. Simuler plusieurs mémoires couplées.
4. Rendre les noyaux dépendants de l’état.
5. Faire varier les constantes de temps sur plusieurs ordres de grandeur.
6. Comparer une intégrale cumulée unique à un modèle multi-mémoires.
7. Tester l’identifiabilité du nombre de mémoires.
8. Tester la capacité à distinguer mémoire longue et attracteur multiple.
9. Tester le transfert d’une trace rapide vers un compartiment lent.
10. Tester le transfert inverse.
11. Mesurer la durée nécessaire pour éviter de confondre relaxation et inscription.
12. Comparer modèles convolutionnels, espaces d’état, équations différentielles retardées et réseaux récurrents contraints.

### S1.4 Diagnostic `D-H-L`

1. Générer des systèmes présentant `D` seul.
2. Générer des systèmes présentant `H` seul.
3. Générer des systèmes présentant `L` seul.
4. Générer les quatre combinaisons doubles et la combinaison triple.
5. Vérifier que les métriques restent séparables.
6. Tester la sensibilité au bruit et aux données manquantes.
7. Comparer plusieurs estimateurs du temps de relaxation.
8. Comparer plusieurs définitions de seuil aller-retour.
9. Tester la détection de pertes topologiques.
10. Vérifier que `L` distingue perte réelle et coût d’accès accru.

### S1.5 `Pth` et `Pacc(T,C,ε)`

1. Définir un estimateur opérationnel par domaine.
2. Tester la dépendance à l’horizon `T`.
3. Tester la dépendance aux ressources et contraintes `C`.
4. Tester la dépendance au seuil probabiliste `ε`.
5. Comparer échantillonnage Monte-Carlo, continuation numérique, méthodes de viabilité et apprentissage de variétés.
6. Mesurer le volume accessible avant et après une transition.
7. Mesurer les états nouvellement accessibles.
8. Mesurer les états devenus inaccessibles.
9. Mesurer le coût énergétique et temporel d’accès.
10. Vérifier la robustesse des conclusions à la métrique de distance choisie.

## WP-S2. Test interventionnel du socle

Le test actuel réussit dans son modèle réduit. La campagne suivante doit tester la portée du mécanisme.

1. Remplacer la cinétique de Monod par Hill, Contois, Haldane et Droop.
2. Ajouter une ressource secondaire limitante.
3. Ajouter plusieurs espèces concurrentes.
4. Ajouter coopération et cross-feeding.
5. Ajouter prédation ou phage.
6. Ajouter bruit démographique.
7. Ajouter bruit environnemental coloré.
8. Ajouter délais et mémoire physiologique.
9. Ajouter hétérogénéité spatiale.
10. Ajouter biofilm et diffusion.
11. Tester des pertes dépendantes de la densité.
12. Tester des pertes pulsées.
13. Tester des pertes corrélées à la ressource.
14. Rechercher les domaines où réduire une perte diminue la persistance globale par effet indirect.
15. Comparer le résultat à des modèles de contrôle optimal.
16. Tester le seuil de lavage sur données expérimentales de chémostat publiées.
17. Concevoir une expérience de laboratoire simple avec intervention préenregistrée.
18. Répliquer dans au moins deux espèces et deux milieux.
19. Tester la généralisation hors chémostat.
20. Séparer clairement le théorème local, la robustesse structurelle et la validité biologique.

## WP-S3. Carte relationnelle et transitions

1. Régénérer la carte avec `CLOS` et `INTG` instanciés.
2. Vérifier automatiquement l’absence de cycles interdits.
3. Vérifier la cohérence chronologique de chaque relation.
4. Vérifier la compatibilité du type de relation avec les définitions.
5. Faire coder les 47 relations par trois experts indépendants.
6. Mesurer l’accord inter-évaluateurs.
7. Publier les désaccords.
8. Tester des relations candidates refusées.
9. Ajouter des contre-exemples pour chaque type de lien.
10. Tester la stabilité de la carte lorsque les transitions incertaines sont retirées.
11. Tester la stabilité sous fusion ou division de transitions.
12. Mesurer centralité, modularité, chemins et goulets d’étranglement.
13. Vérifier que les propriétés de graphe ne proviennent pas du choix manuel des nœuds.
14. Comparer à des graphes nuls conservant le degré.
15. Tester si la carte prédit correctement des relations masquées.
16. Comparer cette prédiction à des méthodes simples de proximité temporelle.
17. Comparer à des graph embeddings.
18. Tester la capacité à proposer des relations nouvelles qui seront ensuite validées par la littérature.
19. Mesurer le taux de faux positifs.
20. Geler une version confirmatoire de la carte avant toute nouvelle recherche bibliographique.

---

# III. Branche 1, matière

La branche matière possède une chronologie et un inventaire. Son apport propre reste à tester.

## WP-M1. Base de données des transitions matérielles

Pour chacune des 40 transitions :

1. définir l’état antérieur
2. définir l’état postérieur
3. définir les variables `n, G, I, E, Π, H`
4. dater la transition avec intervalle d’incertitude
5. lister les preuves directes
6. lister les preuves indirectes
7. lister les modèles concurrents
8. identifier le seuil ou la plage de transition
9. identifier la vitesse de variation
10. identifier les états devenus accessibles
11. identifier les états fermés
12. identifier les pertes
13. identifier les mécanismes de persistance
14. identifier les contre-exemples
15. attribuer un niveau de preuve par évaluateurs indépendants

## WP-M2. Nucléosynthèse et enrichissement

1. Reproduire les abondances primordiales avec plusieurs codes publics.
2. Comparer aux observations de deutérium, hélium et lithium.
3. Quantifier les incertitudes nucléaires.
4. Tester l’effet des masses stellaires sur les rendements.
5. Tester métallicité, rotation et binarité.
6. Comparer supernovæ, étoiles AGB, fusions d’objets compacts et autres sources.
7. Construire des histoires d’enrichissement différentes atteignant une métallicité finale comparable.
8. Mesurer les différences de rapports isotopiques résiduels.
9. Tester si l’histoire reste récupérable à partir de l’état final.
10. Mesurer l’expansion du réseau de réactions accessible après chaque famille d’éléments.

## WP-M3. Molécules, grains et glaces

1. Construire un réseau chimique interstellaire versionné.
2. Tester température, densité, ionisation, UV et chocs.
3. Comparer chimie gazeuse et chimie de surface.
4. Tester la composition des grains.
5. Tester l’épaisseur et la stratification des glaces.
6. Tester plusieurs ordres d’irradiation, chauffage et refroidissement.
7. Rechercher des dépendances au chemin à état final macroscopique égal.
8. Mesurer les molécules nouvellement accessibles.
9. Mesurer les molécules détruites ou rendues inaccessibles.
10. Comparer les prédictions aux inventaires moléculaires astronomiques.
11. Tester la robustesse aux incertitudes de taux réactionnels.
12. Faire une analyse globale de sensibilité.
13. Identifier les réactions qui contrôlent le plus `Pacc`.
14. Tester la généralisation à plusieurs nuages et disques.
15. Répliquer avec un second réseau chimique indépendant.

## WP-M4. Condensation, chondres et solides

1. Reproduire plusieurs séquences de condensation à l’équilibre.
2. Faire varier pression, C/O, redox et composition.
3. Ajouter cinétique et systèmes ouverts.
4. Ajouter séparation gaz-solides.
5. Ajouter transport radial.
6. Tester plusieurs vitesses de refroidissement.
7. Comparer aux CAI, chondres et matrices météoritiques.
8. Tester l’héritage présolaire.
9. Mesurer les minéraux accessibles selon l’ordre des traitements.
10. Rechercher des états finaux de composition globale proche mais de minéralogie différente.
11. Mesurer la fermeture de voies par évaporation ou séquestration.
12. Comparer aux bases de données minérales terrestres et météoritiques.
13. Tester la croissance combinatoire du nombre de phases.
14. Comparer cette croissance à des graphes chimiques nuls.
15. Évaluer si ORI-C prédit mieux les phases observées qu’un simple gradient de volatilité.

## WP-M5. Valeur ajoutée de la branche matière

1. Masquer 20 % des transitions et tenter de les reconstruire avec ORI-C.
2. Comparer à une chronologie descriptive simple.
3. Comparer à un graphe causal standard.
4. Comparer à un modèle de réseau sans histoire.
5. Tester si les dimensions ORI-C améliorent la prédiction de la transition suivante.
6. Tester si elles améliorent la prédiction des états fermés.
7. Tester si elles améliorent l’inférence de l’histoire depuis l’état final.
8. Tester la calibration probabiliste des prédictions.
9. Répéter sur des sous-domaines indépendants.
10. Faire évaluer les prédictions à l’aveugle par des spécialistes.

---

# IV. Filtrages historiques et architecture planétaire

## WP-P1. Provenance des matériaux

1. Compiler les isotopes Ti, Cr, Mo, W, Ni, Ru, Pd et autres traceurs disponibles.
2. Tester la dichotomie carbonée et non carbonée par plusieurs méthodes de clustering.
3. Quantifier l’incertitude de classification.
4. Tester les météorites intermédiaires et les exceptions.
5. Comparer plusieurs modèles de barrière dans le disque.
6. Tester les scénarios de transport radial.
7. Reconstruire les mélanges possibles.
8. Vérifier si la provenance améliore la prédiction de la composition finale des corps.
9. Tester cette prédiction hors échantillon sur des groupes météoritiques masqués.
10. Comparer à un modèle fondé uniquement sur la distance au Soleil.

## WP-P2. Date d’accrétion et chauffage radiogénique

1. Compiler les chronomètres Al-Mg, Hf-W, Mn-Cr et Pb-Pb.
2. Propager toutes les incertitudes de datation.
3. Tester distribution homogène et hétérogène de l’aluminium 26.
4. Simuler des corps de tailles et porosités variées.
5. Tester conduction, convection, fusion et migration des fluides.
6. Comparer les prédictions aux achondrites et corps primitifs.
7. Produire des paires à composition initiale semblable et dates différentes.
8. Mesurer l’effet causal sur fusion, différenciation et perte de volatils.
9. Tester la capacité d’inférer la date d’accrétion depuis la structure finale.
10. Comparer à des modèles thermiques standards sans variables ORI-C.

## WP-P3. Différenciation métal-silicate

1. Compiler les expériences de partage disponibles.
2. Harmoniser pression, température, redox et composition.
3. Construire une méta-analyse hiérarchique.
4. Tester les interactions entre variables.
5. Comparer plusieurs lois de partage.
6. Tester les trajectoires d’accrétion continues et par épisodes.
7. Permuter l’ordre des apports oxydés et réduits.
8. Mesurer les différences de noyau, manteau et surface à inventaire global comparable.
9. Tester Fe, Ni, Co, Nb, Ta, W, Mo, N, P, C, S et éléments hautement sidérophiles.
10. Quantifier l’accessibilité ultérieure des éléments de surface.
11. Tester la sensibilité aux océans magmatiques.
12. Tester l’équilibration complète et incomplète.
13. Comparer Terre, Mars, Vesta et corps différenciés.
14. Étendre aux exoplanètes rocheuses simulées.
15. Faire une validation aveugle sur expériences non utilisées à l’ajustement.

## WP-P4. Volatils, dégazage et pertes

1. Compiler eau, carbone, azote et soufre dans les météorites différenciées.
2. Tester taille, température, durée de fusion et gravité.
3. Tester atmosphère présente ou absente pendant le dégazage.
4. Tester impacts et érosion atmosphérique.
5. Tester photodissociation et échappement.
6. Comparer pertes précoces et tardives.
7. Mesurer `inventaire initial` et `inventaire conservé`.
8. Produire des courbes de transfert vers noyau, manteau, atmosphère et espace.
9. Tester l’hystérésis de rétention.
10. Comparer aux observations des planètes et météorites.

## WP-P5. Apports tardifs

1. Compiler Mo, Ru, W, Os, Ir, Au et autres traceurs.
2. Tester plusieurs dates et masses d’apport.
3. Tester l’équilibrage avec le noyau.
4. Tester les scénarios d’impact lunaire.
5. Tester les apports carbonés et non carbonés.
6. Quantifier la contribution aux volatils de surface.
7. Séparer matière tardive et conservation pendant la formation du noyau.
8. Comparer plusieurs modèles de mélange.
9. Tester la récupération de l’histoire d’apport depuis les isotopes finaux.
10. Réaliser une validation croisée par familles d’éléments.

## WP-P6. Valeur ajoutée ORI-C sur les planètes

1. Prédire la distribution noyau-manteau-surface à partir de la seule composition initiale.
2. Ajouter la provenance.
3. Ajouter la date d’accrétion.
4. Ajouter l’histoire thermique.
5. Ajouter le redox.
6. Ajouter les pertes.
7. Ajouter les apports tardifs.
8. Mesurer le gain incrémental de chaque couche.
9. Comparer à un modèle géochimique standard de même complexité.
10. Tester hors échantillon sur Mars, Vesta et groupes météoritiques.
11. Tester sur populations synthétiques d’exoplanètes.
12. Préenregistrer les prédictions avant d’ajouter de nouvelles données.

---

# V. Couche astronomique du Système solaire

## WP-A1. Reproductibilité numérique

1. Reproduire tous les 25 calculs dans un conteneur propre.
2. Répéter sur plusieurs systèmes d’exploitation.
3. Répéter en simple et double précision lorsque possible.
4. Tester plusieurs compilateurs.
5. Tester plusieurs versions de REBOUND.
6. Comparer WHFast, IAS15, Mercurius et un intégrateur indépendant.
7. Tester une grille plus fine de pas temporels.
8. Tester les critères sur énergie et moment angulaire adaptés à la relativité.
9. Tester l’aller-retour sur plusieurs horizons.
10. Publier la convergence de chaque observable, pas seulement de l’excentricité.

## WP-A2. Conditions initiales et références

1. Utiliser plusieurs éphémérides JPL.
2. Propager les covariances des conditions initiales.
3. Générer des ensembles d’états initiaux cohérents avec les incertitudes.
4. Comparer coordonnées cartésiennes et éléments orbitaux.
5. Tester les transformations de repère.
6. Tester plusieurs époques initiales.
7. Comparer aux solutions La2004, La2010 et autres références indépendantes.
8. Valider sur des horizons croissants.
9. Mesurer le temps de divergence chaotique.
10. Ne jamais interpréter au-delà de l’horizon de fiabilité.

## WP-A3. Physique manquante

Ajouter séparément puis conjointement :

1. la Lune résolue
2. la rotation terrestre
3. l’obliquité dynamique
4. le J2 solaire
5. les marées
6. la relativité cohérente dans tous les diagnostics
7. les principaux astéroïdes
8. la perte de masse solaire
9. les effets de figures planétaires lorsque pertinents
10. les interactions spin-orbite

Pour chaque ajout :

- test d’ablation
- gain contre référence
- coût numérique
- effet sur le spectre
- effet sur l’incertitude
- interaction avec les autres ajouts

## WP-A4. Interventions et causalité

1. Perturber masses de Jupiter et Saturne sur une grille fine.
2. Perturber demi-grands axes.
3. Perturber excentricités et inclinaisons.
4. Perturber phases orbitales.
5. Retirer chaque planète à tour de rôle dans un modèle exploratoire.
6. Ajouter des perturbations combinées.
7. Tester des scénarios de migration historique.
8. Mesurer la réponse spectrale de la Terre.
9. Mesurer la stabilité des résonances.
10. Construire des surfaces de réponse causale.
11. Comparer à des ensembles d’états initiaux quasi identiques.
12. Séparer effet de l’intervention et divergence chaotique.

## WP-A5. Spectres et transfert de fréquences

1. Tester plusieurs méthodes spectrales.
2. Comparer fenêtres, résolution et detrending.
3. Quantifier l’incertitude des pics.
4. Tester 405 ka, 2,4 Ma et autres bandes.
5. Mesurer stabilité des phases.
6. Mesurer transfert entre planètes et variables orbitales.
7. Tester la robustesse aux horizons d’analyse.
8. Comparer spectres aux solutions de référence.
9. Utiliser des signaux synthétiques pour mesurer les faux pics.
10. Préenregistrer les bandes avant l’analyse confirmatoire.

## WP-A6. Validation indépendante

1. Réimplémenter le calcul dans un second code N-corps.
2. Faire reproduire les résultats par une autre équipe.
3. Masquer les critères pendant l’exécution.
4. Archiver les sorties brutes.
5. Faire auditer les transformations et figures.
6. Publier les deux échecs préenregistrés avec les réussites.

---

# VI. Réponse terrestre et couche mémoire historique

La forme actuelle de M2 est réfutée. Elle doit servir de point de départ négatif, jamais de résultat à sauver par ajustements successifs.

## WP-C1. Réplication du résultat négatif

1. Reproduire tous les tests avec l’environnement verrouillé.
2. Répliquer sur toute l’étendue LR04.
3. Répliquer avec incertitudes d’âge et de mesure.
4. Répliquer avec autres piles benthiques.
5. Répliquer avec niveau marin indépendant.
6. Répliquer avec CO2, température et poussières.
7. Répliquer sous plusieurs conventions d’insolation.
8. Répliquer par validation croisée temporelle.
9. Répliquer avec modèles nuls supplémentaires.
10. Faire confirmer le verdict par une équipe indépendante.

## WP-C2. Réparer le test prospectif avant toute nouvelle exécution

1. Cartographier entièrement les régions mono et multistables.
2. Choisir des points réellement discriminants.
3. Apparier les variables motrices du témoin de complexité égale.
4. Publier leurs plages d’exploitation.
5. Définir une normalisation indépendante du point testé.
6. Simuler la puissance avant préenregistrement.
7. Fixer les seuils de matérialité.
8. Fixer la durée d’observation au-delà de toutes les constantes de temps.
9. Geler le protocole.
10. Exécuter une seule fois sur données confirmatoires.

## WP-C3. Familles alternatives de mémoire

Tester séparément et en combinaison :

1. mémoire du volume de glace
2. géométrie et hauteur des calottes
3. érosion du régolithe
4. altération continentale
5. carbone océanique
6. circulation océanique
7. sédiments marins
8. poussières et fertilisation
9. méthane et pergélisol pour périodes adaptées
10. isostasie et topographie
11. végétation et albédo
12. seuils de plateformes glaciaires
13. couplages état-dépendants
14. délais distribués
15. événements stochastiques rares
16. interactions entre mémoires rapides et lentes

Chaque mécanisme doit avoir :

- un témoin instantané
- un témoin de complexité égale
- une ablation
- une prédiction hors échantillon
- une fenêtre longue
- une variable mesurée directement lorsque possible

## WP-C4. Familles de modèles

1. régression et filtres linéaires
2. modèles d’espace d’état
3. modèles à retards distribués
4. systèmes dynamiques non linéaires
5. modèles à seuils
6. modèles à attracteurs multiples
7. modèles stochastiques
8. modèles de viabilité
9. réseaux causaux dynamiques
10. modèles hybrides événementiels
11. modèles conceptuels glaciaires
12. modèles de bilan énergétique
13. EMIC
14. modèles de calotte simplifiés
15. émulateurs de modèles complexes

Comparer chaque famille à complexité, budget d’optimisation et données égales.

## WP-C5. Données et chronologies

1. Propager l’incertitude des modèles d’âge.
2. Tester plusieurs alignements chronologiques.
3. Travailler sur données brutes et piles.
4. Tester la sensibilité aux résolutions.
5. Tester les biais de préservation.
6. Tester l’autocorrélation et la taille efficace.
7. Tester les ruptures de proxy.
8. Utiliser des proxys multiples dans un modèle hiérarchique.
9. Réserver des carottes ou périodes entières pour validation.
10. Préenregistrer les transformations.

## WP-C6. Critères discriminants

Mesurer séparément :

1. RMSE hors échantillon
2. log-vraisemblance prédictive
3. calibration probabiliste
4. corrélation et phase
5. spectre 41, 100 et 405 ka
6. chronologie des terminaisons
7. stabilité des paramètres
8. identifiabilité
9. persistance après convergence des forçages
10. hystérésis
11. pertes de régimes ou de chemins de retour
12. valeur de `Pacc`
13. performance sur périodes jamais ajustées
14. performance sur un autre jeu de proxys
15. avantage contre témoin de complexité égale

## WP-C7. Recherche de mécanismes nouveaux

1. Utiliser l’échec de M2 pour localiser les résidus structurés.
2. Chercher les périodes où M2 capte la signature de 100 ka mais rate l’amplitude.
3. Tester si le mécanisme correct est additif, multiplicatif ou conditionnel.
4. Tester si la mémoire dépend du régime climatique.
5. Tester des changements d’architecture plutôt qu’un noyau fixe.
6. Tester des ruptures de connectivité entre bassins.
7. Tester si une variable lente modifie l’opérateur de réponse.
8. Générer des prédictions qui divergent de tous les témoins standards.
9. Rechercher les données capables de trancher.
10. Abandonner toute famille qui échoue sur deux validations confirmatoires indépendantes.

---

# VII. Application climatique moderne

L’article est actuellement hors chaîne de preuve. Pour l’y faire entrer, il faut extraire des prédictions opérationnelles.

## WP-CL1. Mémoire distribuée du climat

1. Quantifier les noyaux de mémoire océanique, cryosphérique, carbonée, écologique et géologique.
2. Estimer leurs constantes de temps et incertitudes.
3. Tester leur dépendance à l’état.
4. Tester les couplages entre compartiments.
5. Comparer un modèle multi-mémoires à une intégrale unique du forçage.
6. Valider sur simulations historiques.
7. Valider sur expériences d’arrêt des émissions et de retrait du forçage.
8. Tester sur plusieurs modèles climatiques.
9. Vérifier la généralisation entre scénarios.
10. Mesurer la part irréversible transférée entre compartiments.

## WP-CL2. Diagnostic `D-H-L`

Pour chaque élément climatique étudié :

1. mesurer `D`
2. mesurer `H`
3. mesurer `L`
4. tester leur indépendance
5. quantifier les incertitudes
6. comparer modèles et observations
7. identifier les cas où un terme est élevé et les deux autres faibles
8. publier les horizons temporels
9. distinguer retour spontané et restauration active
10. mesurer le coût de restauration

## WP-CL3. Domaine des possibles climatiques

1. Définir `Pth` et `Pacc` pour chaque cas.
2. Déclarer `T`, `C` et `ε`.
3. Cartographier les états climatiques accessibles.
4. Cartographier les chemins de récupération.
5. mesurer les coûts énergétiques, temporels et matériels.
6. tester les changements après différentes trajectoires d’émissions.
7. comparer même réchauffement final avec vitesses et histoires différentes.
8. tester les overshoots.
9. tester les interventions de restauration.
10. distinguer bassin réduit et attracteur supprimé.

## WP-CL4. Validation sur données et ensembles de modèles

1. Utiliser réanalyses et observations.
2. Utiliser ensembles climatiques multi-modèles.
3. Utiliser expériences idéalisées.
4. Utiliser paléoclimats comme contraintes externes.
5. Réserver des modèles entiers pour validation.
6. Tester robustesse aux définitions de seuil.
7. Tester robustesse aux scénarios.
8. comparer aux cadres classiques de résilience.
9. mesurer la valeur prédictive ajoutée d’ORI-C.
10. publier les cas où ORI-C ne change aucune conclusion.

---

# VIII. Branche 3, programme prébiotique

## WP-V1. Préparation expérimentale

1. Geler le schéma des lignées.
2. Vérifier le validateur sur données synthétiques positives et négatives.
3. Ajouter les incertitudes et limites de détection.
4. Définir les cycles et générations.
5. Définir les événements de fusion, division et disparition.
6. Définir les critères de transmission.
7. Définir les critères fonctionnels.
8. Préenregistrer les six conditions minimales.
9. Préenregistrer les huit témoins.
10. Faire auditer le protocole par chimistes prébiotiques et biologistes de l’évolution.

## WP-V2. Briques prébiotiques

### Formation des briques

1. plusieurs compositions initiales
2. plusieurs atmosphères et gaz
3. plusieurs sources d’énergie
4. plusieurs surfaces minérales
5. plusieurs températures et pressions
6. plusieurs séquences temporelles
7. rendements et sous-produits
8. stabilité et dégradation
9. répétabilité inter-laboratoires
10. bilan de masse complet

### Polymérisation

1. distributions de longueurs
2. distributions de séquences
3. fidélité de liaison
4. vitesse de croissance
5. vitesse de dégradation
6. cycles humide-sec
7. gel-dégel
8. gradients hydrothermaux
9. surfaces minérales
10. alternance d’environnements

### Copie par matrice

1. fidélité
2. taux d’erreur
3. vitesse
4. dépendance à la séquence
5. blocages
6. copies partielles
7. compétition entre matrices
8. effet du compartiment
9. effet de l’énergie renouvelée
10. persistance sur plusieurs cycles

### Compartimentation

1. types de lipides
2. tailles de vésicules
3. perméabilité
4. encapsulation
5. croissance
6. division
7. fusion
8. fuite
9. stabilité sous cycles
10. partage du contenu aux descendants

## WP-V3. Couplage, verrou central

1. copie à l’intérieur et à l’extérieur des compartiments
2. matrice copiable contre polymère non copiable apparié
3. même longueur
4. même charge
5. même concentration
6. même encombrement
7. même apport énergétique
8. même nombre d’espèces chimiques
9. copie sans division
10. division sans copie
11. copie et division sans variation
12. copie, division et variation
13. transmission sur plusieurs générations
14. effet fonctionnel des variantes
15. maintien sans réinitialisation complète
16. ablation de la membrane
17. ablation de la matrice
18. ablation du flux énergétique
19. ablation de la variation
20. permutation de l’ordre des environnements

## WP-V4. Matrice environnementale complète

Tester au minimum :

- humide-sec
- gel-dégel
- gradients hydrothermaux
- irradiation UV
- surfaces minérales
- cycles de salinité
- cycles de pH
- cycles redox
- chocs thermiques
- alternances combinées

Pour chaque trajectoire :

1. état initial identique
2. ordre différent
3. état final environnemental identique
4. mesure des lignées
5. mesure de transmission
6. mesure de fonction
7. retrait du forçage
8. durée longue devant toutes les mémoires
9. réplication biologique et technique
10. comparaison à trajectoire aléatoire

## WP-V5. Cartographie de l’espace prébiotique

1. Construire `Pth` chimique.
2. Estimer `Pacc(T,C,ε)` par expérience à haut débit.
3. Cartographier les produits accessibles.
4. Cartographier les lignées viables.
5. Cartographier les trajectoires fermées.
6. Mesurer les coûts énergétiques.
7. Identifier les goulets d’étranglement.
8. Tester la robustesse des résultats aux seuils.
9. Reproduire dans un second système chimique.
10. Faire une réplication inter-laboratoires.

## WP-V6. Critère de transition matière-hérédité

Le test confirmatoire exige simultanément :

1. copies avec variations
2. association au compartiment
3. croissance et division
4. transmission aux descendants
5. effet des variantes sur persistance ou reproduction
6. maintien sur plusieurs cycles sans reconstruction complète externe

Ajouter :

7. avantage contre témoin de complexité égale
8. ablation qui supprime l’effet
9. persistance après retrait d’une contrainte temporaire
10. reproduction dans un second laboratoire

---

# IX. Vivant, architecture cellulaire et endosymbiose

## WP-B1. Acte 1, cellule eucaryote

1. Coder les six dimensions sur plusieurs types cellulaires.
2. Inclure bactéries, archées et eucaryotes.
3. Tester l’accord entre codeurs.
4. Perturber chaque organite ou fonction dans des données publiques.
5. Mesurer survie, réparation, reproduction et évolution.
6. Construire des graphes de dépendances fonctionnelles.
7. Tester la redondance et la compensation.
8. Mesurer les chemins de récupération.
9. Tester si le vecteur `Π` prédit mieux la viabilité qu’un ensemble classique de variables.
10. Valider sur types cellulaires masqués.

## WP-B2. Acte 2, endosymbiose mitochondriale

1. Compiler phylogénies des gènes mitochondriaux et nucléaires.
2. Compiler transferts de gènes vers le noyau.
3. Compiler réduction génomique.
4. Compiler systèmes d’import protéique.
5. Compiler dépendances métaboliques.
6. Comparer plusieurs scénarios d’endosymbiose.
7. Tester la relation `INTG` sur critères explicites.
8. Tester les étapes de fermeture d’alternatives.
9. Rechercher des transitions analogues dans plastes et symbioses récentes.
10. Tester la capacité du cadre à prédire quelles symbioses deviennent obligatoires.
11. Comparer à des modèles standards de dépendance symbiotique.
12. Valider sur cas non utilisés pour construire les critères.

## WP-B3. Valeur ajoutée biologique générale

1. Prédire persistance et récupération à partir des six dimensions.
2. Comparer à des modèles de réseaux biologiques.
3. Comparer à des modèles de fitness.
4. Comparer à des modèles de résilience.
5. Tester les données hors domaine.
6. Mesurer calibration et faux positifs.
7. Tester si les notions `D-H-L` ajoutent une information indépendante.
8. Tester si `Pacc` prédit les transitions observées.
9. Publier les domaines où le cadre reste descriptif.
10. Réserver le statut prédictif aux cas confirmés hors échantillon.

---

# X. Acte 3, résistance aux antibiotiques

## WP-R1. Conception générale

1. Utiliser plusieurs espèces bactériennes.
2. Utiliser plusieurs familles d’antibiotiques.
3. Inclure milieux riches, pauvres et structurés.
4. Inclure populations planctoniques et biofilms.
5. Prévoir au moins 12 à 24 lignées indépendantes par condition.
6. Randomiser les traitements.
7. Aveugler l’analyse lorsque possible.
8. Préenregistrer les critères.
9. Séparer résistance, tolérance et persistance.
10. Suivre les coûts de fitness.

## WP-R2. Histoires d’exposition

Tester :

1. exposition constante
2. augmentation progressive
3. diminution progressive
4. impulsions courtes
5. impulsions longues
6. alternance de deux antibiotiques
7. ordre A puis B
8. ordre B puis A
9. combinaison simultanée
10. périodes sans antibiotique
11. stress environnemental avant antibiotique
12. stress après antibiotique
13. trajectoires aléatoires appariées
14. même dose cumulée avec ordres différents
15. même MIC finale obtenue par histoires différentes

## WP-R3. Mesures

À chaque cycle :

1. MIC
2. courbe dose-réponse
3. temps de latence
4. taux de croissance
5. survie après choc
6. fraction persistante
7. fitness sans antibiotique
8. mutations
9. fréquences alléliques
10. expression génique
11. métabolisme
12. morphologie
13. hétérogénéité cellule par cellule
14. stabilité après retrait
15. transmissibilité aux descendants

## WP-R4. Tests ORI-C

1. dépendance au chemin à état final égal
2. hystérésis des seuils de résistance
3. durée `D`
4. asymétrie `H`
5. pertes `L`
6. changements d’état contre changements architecturaux
7. modification du domaine de viabilité
8. états devenus inaccessibles
9. coût des chemins de retour
10. ablation génétique des mécanismes candidats
11. réversion ou remplacement d’allèles
12. transfert dans un fond génétique naïf
13. témoin de complexité égale dans les modèles prédictifs
14. prédiction de la prochaine mutation ou du prochain phénotype
15. validation sur lignées masquées

## WP-R5. Comparaisons concurrentes

Comparer ORI-C à :

1. modèles de fitness landscape
2. chaînes de Markov
3. modèles de population classiques
4. apprentissage supervisé sans histoire
5. modèles récurrents avec histoire
6. modèles causaux dynamiques
7. modèles de collateral sensitivity
8. modèles génétiques mécanistes

Le succès exige un avantage hors échantillon contre un modèle de complexité égale, pas seulement une bonne reconstruction rétrospective.

## WP-R6. Réplication

1. seconde espèce
2. second antibiotique
3. second laboratoire
4. répétition à partir de stocks indépendants
5. analyse bioinformatique indépendante
6. validation des mutations par reconstruction
7. dépôt des lignées et séquences
8. publication des trajectoires complètes

---

# XI. Tests transversaux de l’apport propre d’ORI-C

## WP-T1. Benchmark multi-domaines

Créer un benchmark commun contenant des cas de :

- transition de phase
- différenciation planétaire
- dynamique orbitale
- mémoire climatique
- protocellules
- évolution bactérienne

Pour chaque cas :

1. masquer une partie de l’histoire
2. masquer une partie des états futurs
3. demander la reconstruction
4. demander la prédiction
5. demander la détection de seuil
6. demander la détection de perte
7. demander l’estimation de `Pacc`
8. comparer ORI-C aux cadres concurrents
9. mesurer performance et calibration
10. mesurer coût de données et complexité

## WP-T2. Généralité réelle

1. Tester les mêmes définitions dans les trois branches.
2. Mesurer les adaptations nécessaires.
3. Identifier les notions réellement invariantes.
4. Identifier les notions seulement analogiques.
5. Retirer les notions qui ne produisent aucune mesure.
6. Vérifier qu’un résultat d’une branche ne modifie pas le statut d’une autre.
7. Tester la portabilité des schémas de données.
8. Tester l’accord de codage entre disciplines.
9. Faire auditer le langage par experts externes.
10. Réviser le Codebook à partir des échecs.

## WP-T3. Valeur prédictive

1. Définir au moins une prédiction nouvelle par branche.
2. Geler ces prédictions avant collecte des données.
3. Fixer un témoin de complexité égale.
4. Fixer un seuil d’amélioration minimal.
5. Utiliser des données jamais examinées.
6. Répliquer la prédiction.
7. Calculer la puissance statistique.
8. Corriger les comparaisons multiples.
9. Publier les échecs.
10. Refuser le statut prédictif sans réplication.

## WP-T4. Test de compression explicative

1. Mesurer le nombre de concepts et paramètres nécessaires.
2. Comparer à des descriptions disciplinaires séparées.
3. Vérifier si ORI-C réduit la complexité sans perdre de précision.
4. Mesurer les erreurs introduites par la compression.
5. Faire évaluer la clarté par des lecteurs indépendants.
6. Distinguer utilité pédagogique et valeur scientifique.

## WP-T5. Red team

Créer une équipe chargée de :

1. trouver des contre-exemples
2. produire des codages alternatifs
3. construire des témoins plus forts
4. rechercher les fuites de données
5. tester les choix de métriques
6. chercher les hypothèses non identifiables
7. reproduire les analyses depuis zéro
8. proposer des expériences qui maximisent le risque de réfutation
9. publier un rapport contradictoire
10. intégrer les critiques sans changer rétroactivement les critères

---

# XII. Ordre d’exécution recommandé

## Niveau 1. Immédiat, faible coût, forte valeur scientifique

1. registre complet des hypothèses
2. base de données des 40 transitions
3. tests synthétiques du socle
4. régénération et audit indépendant de la carte
5. benchmark de valeur ajoutée sur données existantes
6. réplication complète du résultat négatif climatique
7. réparation du protocole prospectif
8. extension de la couche astronomique avec physique manquante par ablations
9. méta-analyse des filtrages planétaires
10. préparation confirmatoire de l’expérience antibiotique
11. durcissement du schéma de lignées prébiotiques
12. préenregistrement public des tests confirmatoires

## Niveau 2. Calcul intensif et données publiques

1. ensembles N-corps élargis
2. propagation des incertitudes orbitales
3. réseaux chimiques interstellaires
4. modèles de condensation hors équilibre
5. simulations thermiques de planétésimaux
6. modèles d’accrétion et différenciation
7. familles alternatives de mémoire climatique
8. benchmark multi-domaines
9. analyses comparatives d’endosymbioses
10. modélisation prospective des expériences biologiques

## Niveau 3. Collaborations expérimentales

1. chémostat interventionnel
2. pétrologie expérimentale ciblée
3. tests de dégazage et partage
4. évolution expérimentale sous antibiotiques
5. protocellules et lignées
6. réplication inter-laboratoires

## Niveau 4. Validation externe

1. audit statistique indépendant
2. réplication de code indépendante
3. réplication expérimentale
4. revue contradictoire
5. publication avec données brutes et résultats négatifs

---

# XIII. Règles d’arrêt

Une piste est arrêtée ou reformulée lorsque :

1. elle échoue deux fois sur des jeux confirmatoires indépendants
2. son avantage disparaît contre un témoin de complexité égale
3. ses paramètres restent non identifiables malgré des données suffisantes
4. son effet disparaît sur une fenêtre plus longue que toutes les constantes de temps
5. l’ablation du mécanisme ne modifie pas le résultat
6. un modèle plus simple produit la même prédiction
7. la prédiction dépend d’un choix de fenêtre, métrique ou transformation non préenregistré
8. les résultats ne se reproduisent pas dans un second environnement ou laboratoire

Une piste reste ouverte lorsque l’échec révèle un défaut précis de protocole avant consultation du résultat confirmatoire. Le nouveau protocole reçoit un nouvel identifiant et une nouvelle préinscription.

---

# XIV. Critères pour considérer ORI-C comme sérieusement avancé

Le programme franchit un premier seuil scientifique lorsque les conditions suivantes sont réunies :

1. toutes les affirmations majeures possèdent un identifiant et un statut
2. la branche matière dispose d’une base de données testable
3. au moins une prédiction propre à ORI-C réussit hors échantillon dans chaque branche
4. chaque réussite bat un témoin de complexité égale
5. chaque mécanisme est soutenu par une ablation
6. la dépendance au chemin est testée à conditions finales vérifiées identiques
7. la persistance est observée au-delà de toutes les constantes de temps pertinentes
8. `D`, `H` et `L` sont publiés séparément
9. `Pacc(T,C,ε)` est mesuré dans au moins un système par branche
10. deux résultats sont reproduits par des équipes indépendantes
11. au moins un résultat général traverse deux branches sans modification de définition
12. les résultats négatifs restent visibles et versionnés

Le seuil fort est atteint lorsqu’une prédiction nouvelle, formulée avant les données, réussit dans plusieurs domaines et apporte un gain reproductible face aux cadres concurrents. C’est à ce moment que le programme dépasse clairement la synthèse conceptuelle.

---

# XV. Première séquence de travail concrète

## Bloc A, fondations

1. créer `REGISTRE_HYPOTHESES.csv`
2. extraire toutes les affirmations du dossier
3. attribuer les métriques et témoins
4. classer exploratoire ou confirmatoire
5. définir les priorités par valeur d’information

## Bloc B, socle

1. construire le banc synthétique `X-m-A`, `D-H-L`, `Pth-Pacc`
2. tester la carte avec relations masquées
3. mesurer l’accord inter-codeurs
4. comparer ORI-C à des modèles standards

## Bloc C, matière et planètes

1. construire la base des 40 transitions
2. construire la base des filtrages planétaires
3. lancer les méta-analyses isotopiques et expérimentales
4. tester l’inférence de trajectoire depuis l’état final

## Bloc D, Système solaire et climat

1. reproduire la couche astronomique
2. ajouter la Lune, obliquité, J2 et marées par ablations
3. réparer le test prospectif climatique
4. lancer les familles alternatives de mémoire
5. réserver des données confirmatoires

## Bloc E, vivant

1. finaliser le protocole antibiotique
2. simuler sa puissance
3. préparer les lignées et témoins prébiotiques
4. lancer les tests de codage cellulaire et d’endosymbiose
5. trouver des laboratoires partenaires

## Bloc F, intégration

1. construire le benchmark multi-domaines
2. tester la valeur ajoutée
3. lancer le red team
4. geler les prédictions confirmatoires
5. publier le plan avant exécution

---

# Conclusion opérationnelle

La totalité des possibilités théoriques est infinie. Une campagne finie peut cependant couvrir systématiquement l’espace des tests en combinant :

**domaines × mécanismes × données × modèles × témoins × interventions × histoires × fenêtres temporelles × métriques × réplications.**

Le programme ci-dessus transforme cette combinatoire en plan contrôlé. Il évite de multiplier des essais isolés et concentre les ressources sur les tests capables de distinguer ORI-C d’une reformulation descriptive des connaissances existantes.
