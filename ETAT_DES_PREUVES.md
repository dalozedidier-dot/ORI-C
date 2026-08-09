# État des preuves

Ce tableau est le seul lieu du dossier où les trois branches sont regardées
ensemble. Il compare des **statuts**, jamais des résultats.

> **Avant de lire un échec comme un résultat négatif.**
> Un critère du dossier ne peut pas être satisfait, quelle que soit l’ampleur
> réelle de l’effet cherché : la **vallée des rayons**, dont le seuil n’est
> franchi à aucune taille disponible et dont la profondeur mesurée est négative.
> Son échec ne réfute rien.
> Voir [`ATTEIGNABILITE_DES_CRITERES_2026-08-08.md`](ATTEIGNABILITE_DES_CRITERES_2026-08-08.md).
>
> Sur 23 critères discrets, 20 sont atteignables et 3 — des bootstraps — ne sont
> pas évaluables par cette voie, un bootstrap n’ayant pas de plancher de p
> général.
>
> **Correction du 8 août 2026.** Cet encadré citait auparavant « les deux tests
> de signe du benchmark antibiotique longitudinal, qui exigent 9 plis favorables
> sur 10 ». Le benchmark n’emploie pas un test de signe mais un test de
> **sign-flip**, qui prend les magnitudes en compte et n’exige aucun nombre
> minimal d’unités favorables. Ces deux critères sont atteignables ; l’auditeur
> les modélisait par le mauvais test.
>
> **Premier test prospectif.** `WP-EXO-PACC-2026`, gelé le 7 août 2026 et
> vérifiable le 7 août 2028, est le seul protocole du dossier dont la conclusion
> ne peut plus être ajustée après lecture. Il est le seul candidat à un statut
> confirmatoire ; tous les autres résultats restent rétrospectifs ou de modèle.

## Échelle employée

| Niveau | Définition |
|---|---|
| **Établi** | mesuré directement ou reproduit par des modèles largement validés |
| **Validé dans le modèle réduit** | test numérique explicite réussi, sans transposition automatique au réel |
| **Fortement appuyé** | plusieurs observations indépendantes convergent, mécanisme ou chronologie partiellement ouverts |
| **Plausible** | mécanisme possible, causalité ou portée incertaines |
| **Preuve de concept** | la méthode s'applique sans contradiction, sans démonstration de supériorité |
| **Non testé** | aucune procédure exécutée |
| **Réfuté** | test exécuté, critère préenregistré non atteint |


## Règle de lecture

Un verdict appartient au protocole qui l’a produit. Un échec de M2 ne devient pas un échec de la branche Système solaire. Un résultat sur l’amikacine ou Card 2019 ne résume pas la branche vivant. L’absence de filiation dans les données ARN ne s’applique pas aux expériences de vésicules, qui contiennent des cartes parent-descendant réelles. Les synthèses courantes doivent présenter les résultats D’Onofrio, vésicules, H011 et `Pacc` avant les états historiques qu’ils ont dépassés.

## Résultats positifs actuels

| Résultat | Mesure principale | Statut |
|---|---|---|
| Causalité architecturale astronomique | effet interventionnel minimal 4 964 fois supérieur aux écarts numériques sélectionnés ; 13/15 critères | **Validé dans le modèle réduit** |
| Persistance dans le chémostat | relation démontrée symboliquement ; 11/11 sections réussies | **Établi dans le modèle** |
| Histoire antibiotique D’Onofrio | RMSE 1,1309 → 0,8042 ; témoin permuté 1,1415 ; p = 0,00498 | **Soutenu contre les deux témoins** |
| Lignées de vésicules | 11 760 couples ; quatre composantes préenregistrées soutenues ; permutation p = 0,00050 | **Soutenu dans le protocole préenregistré** |
| Seuil H011 | seuil monotone avec la turbulence ; rapport extrême 3,33 | **Soutenu dans les simulations publiées** |
| Organisation de l’hypergraphe matériel | 46/53 en fermeture stricte ; 34 relations critiques ; 0,595 bit, p = 0,00005 | **Structure et information mesurées** |
| Distinction relaxation/mémoire | convergence sous forçage final commun ; temps caractéristique 7,02 Ma | **Critère opératoire établi dans le modèle** |
| Mémoire matérielle réelle, transversalité | 5 familles positives sur au moins une relation, mais 0 famille porte la chaîne complète sous les quatre contrôles, 3 exigées | **C-MAT-MEM-05 ne soutient pas la transversalité** |

Pour la mémoire matérielle, « positive sur une relation » signifie **preuve
partielle**, pas admission au schéma confirmatoire complet. IODP soutient
fortement l'ablation physique, tandis que `C03` complet reste non testable ; ses associations trace-réponse, sa résistance à
20 mT et la comparaison NRM/IRM-ARM ne satisfont pas les plans gelés de `C01`,
`C02` et `C04`. Les permutations servent de contrôles statistiques et ne sont
pas comptées comme contrôles négatifs physiques.

## Socle

L'audit transversal distingue désormais quatre objets du cadre qui ne
produisent encore **aucune mesure** dans les sorties générées : la chaîne ORI-C
complète, le diagnostic `D-H-L`, la séparation `X/m/A` et le critère
d'altération architecturale. Ils organisent le programme et ses futurs tests ;
ils ne doivent pas être présentés comme des résultats empiriquement établis.

| Élément | Statut | Où |
|---|---|---|
| Vocabulaire des six dimensions | Preuve de concept | `00_socle/CODEBOOK.md` |
| Mémoire distribuée, `D-H-L`, filtres `P^adm/P^att/P^kin`, persistance vectorielle `P_pers/Π*/Q`, `S`/`m`/`A`, `ℓ_ana/{ℓ_phys}`, régimes `(D_i,G_i)`, raccords `T(i→j)`, mise à jour `U_i`, chaînes physique/épistémique | Définitions et critères, non preuve empirique | `00_socle/CODEBOOK.md` §13 |
| Carte des 40 transitions, 47 relations | Cohérence structurelle vérifiée | `00_socle/carte_relationnelle/` |
| Suite de tests de la carte | voir `ETAT_DES_TESTS.md` | `00_socle/tests/` |
| Représentation des fermetures | attribut de nœud, 5 transitions ; `CLOS` et `INTG` définis, non instanciés | `ARCHITECTURE.md` |
| Test interventionnel du chémostat | Validé dans le modèle réduit | `00_socle/test_interventionnel/` |

Le test interventionnel établit qu'une réduction du terme de perte augmente
strictement l'équilibre positif, sur 115 120 tirages où les deux systèmes sont
viables, avec un facteur de rétention supérieur à 1 dans 100 % des cas. Il
identifie aussi le seuil de lavage au-delà duquel l'affirmation causale perd
son sens.

L'analyse exhaustive conclut **11 sections réussies sur 11**, après la
correction de deux défauts documentée dans
`00_socle/test_interventionnel/resultats_exhaustifs/CORRECTION_ANALYSE_EXHAUSTIVE.md`.

Les trois niveaux de conclusion du rapport restent distincts et ne changent
pas : niveau 1, théorème dans le modèle, **établi** ; niveau 2, robustesse
structurelle, **établi avec réserve** ; niveau 3, validité biologique, **non
établi**.

L'exhaustivité porte sur le système d'équations défini et son domaine
admissible. Elle ne constitue ni une preuve sur toutes les structures
mathématiques possibles, ni une validation empirique dans le vivant.

## Branche 1 — Matière

La campagne de mémoire matérielle utilise désormais des rangs moyens pour les
ex æquo et des permutations au sein des strates expérimentales. Aucun jeu ne
dispose encore d'une fiche d'admission confirmatoire : IODP, FABEST, polymères,
traces de fission et jeux associés restent donc des preuves partielles. IODP
apporte une preuve forte d'ablation physique, mais pas le plan A/B complet de
C-MAT-MEM-03. La CI rejoue les résultats versionnés lorsque les sources
primaires IODP, aciers à outils ou hystérésis dynamique sont absentes ; elle ne
démontre alors pas la chaîne primaire intégrale pour ces étapes.

| Élément | Statut | Remarque |
|---|---|---|
| Chronologie en huit régimes | Fortement appuyé à Établi selon les régimes | s'appuie sur la littérature, pas sur un calcul propre |
| Inventaire des 40 transitions | Établi à Hypothétique selon l'entrée | chaque entrée porte son propre niveau |
| Voies prébiotiques | Plausible | mécanismes candidats, non séquence historique démontrée |
| Apport spécifique dans l’article initial | **Non testé dans cet article historique** | les campagnes hypergraphe, H011 et inventaire sont évaluées séparément ci-dessous |

La branche est explicite sur ce point : « L'article théorique ouvre le
programme ; la base de données et les tests viendront ensuite. »

### Couche généalogie annotée

Complémentaire de l'hypergraphe, elle ne s'y substitue pas et n'y est pas
contenue. 39 transitions, 25 champs, dont treize que l'hypergraphe n'a pas et
quatre axes de certitude indépendants.

| Élément | Statut | Remarque |
|---|---|---|
| Clôture, entrées externes déclarées | **Cohérence structurelle vérifiée** | 53 produits, 77 relations, 0 anomalie |
| Séparation parent matériel / condition permissive | **Établi comme règle machine** | le validateur rejette toute confusion |
| Séparation actinides / aluminium 26 | **Corrigé** | capture neutronique d'un côté, capture protonique de l'autre |
| Quatre axes de certitude | **Établi comme règle** | mécanisme, milieu naturel, transition historique, rôle causal |
| Correspondance entre représentations | **Publiée** | 24 lignes, l'équivalence n'est plus implicite |
| Possibilités ouvertes et fermées | Preuve de concept | **seul endroit du dossier où le terme final de la chaîne ORI-C est instancié** |
| Mesure d'information sur la version antérieure | **Retirée** | saturée par mémorisation, archivée comme non probante |

La version antérieure est conservée **pour traçabilité et ne doit pas être
citée**. Elle porte le défaut corrigé depuis : la gravité et le flux ultraviolet
y figurent comme parents matériels, alors que ce sont des conditions. Un test
verrouille ce constat et vérifie que le défaut n'est pas remonté dans la version
courante.

### Inventaire hiérarchique de la matière

Registre de ce qui existe, distinct de la généalogie qui dit d'où cela vient.
6 392 entrées détaillées, 550 entrées d'index, dix sources institutionnelles
datées.

| Élément | Statut | Remarque |
|---|---|---|
| Constituants fondamentaux, nuclides, éléments | **Établi, exhaustif** | registres fermés ou évalués : 18, 5 843, 118 |
| Molécules, phases, matériaux, réservoirs, biologique | Structurant | **ouvert, non clos**, le fichier ne prétend pas l'inverse |
| Séparation confirmé / hypothétique | **Établi comme règle** | aucun candidat de matière noire ne porte « confirmé » |
| Chaîne présence → accessibilité → mobilisabilité → opérativité | **Mesurée partiellement pour l’azote terrestre** | présence, accessibilité et mobilisabilité calculées ; opérativité sans donnée |
| Sourçage | **Établi** | 100 % des lignes contrôlées portent une URL |

Les effectifs annoncés ont été recomptés feuille par feuille : **treize sur
treize concordent**, le total détaillé tombe exactement sur 6 392, la hiérarchie
est close avec une racine unique et aucun parent orphelin.

Cette couche éclaire une limite constatée ailleurs. Les vingt-huit
enregistrements d'inventaire accessible sans valeur chiffrée mesurent une
**présence** par réservoir. Une première chaîne quantitative est maintenant
calculée pour l'azote terrestre. Selon le scénario de noyau, la fraction
accessible vaut 1,93 %, 3,05 % ou 21,94 %. Avec un flux naturel total de
228 Tg/an, la fraction mobilisable passe de 6 × 10⁻⁶ à 100 ans à 0,0554 à
1 Ma, puis 0,631 à 20 Ma. Le résultat établit dans ce modèle que la
mobilisabilité dépend de l'horizon. `Q_operatoire` reste vide, faute de stock
d'azote effectivement incorporé dans les architectures vivantes.

### Couche hypergraphe mécanistique

La représentation linéaire de la branche a été remplacée par un hypergraphe :
53 nœuds, 53 hyperarêtes multi-entrées et multi-sorties, du socle baryonique
jusqu'aux interfaces réactives. La base historique
`base_transitions/transitions_matiere.csv` reste intacte comme objet audité.

| Élément | Statut | Remarque |
|---|---|---|
| Connectivité de la projection paire à paire | **Cohérence structurelle vérifiée** | racine unique `N036`, 53/53 nœuds reliés dans la projection |
| Fermeture hypergraphique stricte | **Écart structurel détecté** | 46/53 nœuds atteignables ; noyau cyclique de 4 nœuds et 3 nœuds bloqués en aval |
| Filtre NC–CC paramétré | Fortement appuyé | 3 mécanismes concurrents conservés, aucun tranché |
| Échelle des dix capacités, monotonie | **Réfuté** | critère préenregistré non atteint, 11 arcs sur 117 |
| Échelle des dix capacités, information | **Établi dans le graphe** | gain net 0,595 bit, p = 5·10⁻⁵, ρ = 0,74 |
| Inventaire accessible, azote carbone hydrogène soufre | Fortement appuyé | 31 enregistrements sourcés, répartition mesurée |
| Bouclage des budgets publiés | **Établi** | noyau + silicate reconstitue le total, écart max 2,88 % |
| Coefficients de partage métal-silicate | Fortement appuyé | 9 valeurs expérimentales, N C H S, bornes déclarées |
| Prédiction de la répartition par les coefficients | **Établi pour C, H, N — désaccord pour S** | épreuve indépendante, sans circularité |
| Facteurs de mobilisation à horizon donné | **Calculés pour l’azote terrestre dans un modèle de premier ordre** | fonction explicite de l’horizon ; opérativité non mesurée |

Deux résultats méritent d'être lus ensemble, parce qu'ils vont en sens
contraire.

Le premier contrôle de connectivité a révélé que la chaîne poussière
`N008 → N009 → N010 → N008` tournait sur elle-même sans alimentation
matérielle. L'hyperarête `H047` a rétabli cette jonction dans la projection.

Le contrôle hypergraphique strict ajouté ensuite change la conclusion de
clôture. Une hyperarête multi-entrée ne peut produire ses sorties que lorsque
toutes ses entrées sont disponibles. Avec cette règle, seuls 46 nœuds sur 53
sont atteignables. `N029`, `N030`, `N053` et `N054` forment le noyau cyclique. `N031`, `N032` et `N035` sont bloqués en aval. Un seul apport déclaré sur le noyau suffit à fermer mathématiquement la représentation, sans démontrer qu'un tel apport existe dans la nature. L'hypergraphe reste connecté dans sa projection, mais il n'est pas strictement clos.

La monotonie de l'échelle des capacités est **réfutée, et ne peut pas être
rétablie par un réétiquetage**. La raison est structurelle : une production
pointe toujours vers le bas. Une étoile de niveau 6 produit des éléments de
niveau 1 ; un système hydrothermal de niveau 9 produit des espèces mobiles de
niveau 8. L'échelle ordonne des **objets**, pas des **processus**. Deux niveaux
ont été corrigés après lecture des violations avant que la poursuite ne soit
arrêtée : ces corrections sont consignées, et un accord obtenu ainsi ne
compterait pas comme preuve.

Ce qui subsiste est le test B. Les six dimensions portaient 0,000 bit propre.
L'échelle des capacités porte 0,595 bit **net du tirage par permutation**, avec
un rho de 0,74 : corrélée à la profondeur dans le graphe sans lui être
redondante. C'est, à ce jour, le seul attribut de branche dont l'apport propre
survive à un témoin apparié. Sa portée reste interne au graphe : il mesure un
codage, pas le monde.

L'inventaire accessible donne un résultat du même ordre. La part d'azote
mobilisable en surface varie de 8 % à 94 % du total terrestre selon que l'on
retient la voie chondritique ou le calcul ab initio pour le noyau. Ce n'est pas
une barre d'erreur, c'est un désaccord publié non tranché, conservé comme tel.

Une épreuve indépendante a été conduite sur cette répartition. Les coefficients
de partage métal-silicate mesurés en laboratoire prédisent un rapport de masses
noyau sur silicate égal à `D` fois le rapport des masses de réservoirs. Les
deux côtés viennent de sources indépendantes — expériences à haute pression
d'un côté, budgets géochimiques de l'autre — donc un accord n'est pas une
tautologie.

| Élément | Attendu par `D` | Observé | |
|---|---|---|---|
| C | 6,7 à 305,8 | 3,4 à 46,8 | recouvre |
| H | 13,9 et au-delà | 22,2 à 60,4 | recouvre |
| N | 8,6 à 14,8 | 0,07 à 11,1 | recouvre |
| **S** | 3,8 à 26,3 | **34,4** | **désaccord** |

Trois éléments sur quatre recouvrent. Le désaccord sur le soufre n'est pas un
artefact du contrôle : la source des coefficients conclut elle-même à un noyau
pauvre en soufre, contre l'estimation classique de 1,8 wt% tirée de la tendance
de volatilité. Le contrôle retrouve donc une tension publiée sans l'avoir
cherchée, ce qui vaut pour lui une première validation.

Une erreur du contrôle lui-même a été corrigée au passage : `D_H ≥ 29` est une
borne inférieure publiée. La traiter comme une valeur ponctuelle fabriquait un
désaccord inexistant sur l'hydrogène. Le type de chaque valeur — point ou
borne — est désormais déclaré dans `coefficients_partage.csv` et vérifié.

## Branche 2 — Filtrages historiques de l'architecture planétaire

| Élément | Statut | Nature de la preuve |
|---|---|---|
| Tri des matériaux du disque par provenance | **Établi** | anomalies isotopiques, dichotomie carbonée / non carbonée |
| Contrôle du destin thermique par la date d'accrétion | **Établi** | radiochronologie, excès de magnésium 26 |
| Rôle de la température et du redox dans la différenciation | **Établi** | pétrologie expérimentale, partage métal-silicate |
| Perte précoce des volatils par dégazage | **Établi** | teneurs en eau des achondrites |
| Apports postérieurs à la ségrégation du noyau | **Établi** | isotopes du molybdène, éléments fortement sidérophiles |
| Apport spécifique d'ORI-C sur cette chaîne | **Non testé** | aucun test comparatif proposé |

C'est le seul endroit du programme où la dépendance au chemin est **matériellement
enregistrée** plutôt que modélisée ou postulée. Plusieurs étapes de l'histoire
d'une planète restent lisibles dans sa matière et causalement actives dans son
architecture présente.

La portée doit rester exacte. Ces résultats appartiennent à la cosmochimie, à la
radiochronologie et à la pétrologie expérimentale. ORI-C ne les produit pas, il
les organise. Ils établissent la **prémisse** du cadre, non sa valeur ajoutée :
aucun test ne mesure ici ce qu'ORI-C apporte par rapport aux disciplines qui ont
mis cette chaîne au jour.

Détail : `02_branche_systeme_solaire/FILTRAGES_HISTORIQUES.md`.

## Branche 2 — Système solaire, couche astronomique

| Critère préenregistré | Observé | Seuil | Statut |
|---|---:|---:|:--:|
| Tous les corps restent liés | oui | oui | RÉUSSI |
| Conservation de l'énergie | 1,325 × 10⁻¹¹ | ≤ 10⁻⁸ | RÉUSSI |
| Moment angulaire newtonien | 5,276 × 10⁻¹⁰ | ≤ 10⁻¹⁰ | **ÉCHEC** |
| Excentricité initiale contre La2010 | 2,192 × 10⁻¹⁰ | ≤ 10⁻⁸ | RÉUSSI |
| Corrélation Horizons à 6 ka | 1,000000 | ≥ 0,99 | RÉUSSI |
| RMSE Horizons à 6 ka | 4,826 × 10⁻⁷ | ≤ 2 × 10⁻⁴ | RÉUSSI |
| Corrélation La2010 à 100 ka | 0,999971 | ≥ 0,95 | RÉUSSI |
| Corrélation La2010 à 500 ka | 0,998760 | ≥ 0,80 | RÉUSSI |
| Corrélation La2010 à 1 Ma | 0,997270 | ≥ 0,60 | RÉUSSI |
| Convergence du pas sur 2 Ma | 8,427 × 10⁻⁷ | ≤ 10⁻⁴ | RÉUSSI |
| WHFast contre IAS15 à 20 ka | 3,131 × 10⁻⁷ | ≤ 10⁻⁶ | RÉUSSI |
| Aller-retour à 100 ka | 2,763 × 10⁻⁵ | ≤ 10⁻⁵ | **ÉCHEC** |
| Pic spectral de 405 ka | 0,007861 | ≤ 0,05 | RÉUSSI |
| Pic spectral de 2,4 Ma | 0,166625 | ≤ 0,20 | RÉUSSI |
| Contrefactuels au-dessus du plancher | 6,27 × 10⁶ | ≥ 3 | RÉUSSI |

**13 réussis sur 15.** Statut : *validé dans le modèle réduit*.

Les deux échecs sont documentés à leur source. Le premier concerne un
diagnostic newtonien dans le seul contrôle relativiste complet ; tous les jobs
de production restent sous 4,33 × 10⁻¹². Le second est corrigé au pas raffiné
de 0,005 an, qui atteint 7,54 × 10⁻⁶, mais le seuil préenregistré porte sur le
maximum des deux essais et l'échec est conservé.

Portée : le modèle réduit ne résout ni la Lune, ni la rotation terrestre, ni le
J₂ solaire, ni les marées, ni l'obliquité dynamique. Une ressemblance orbitale,
même forte, ne valide pas le cadre général.

## Branche 2 — Système solaire, couche mémoire historique

| Test | Contre M1 (moins complexe) | Contre M1P (complexité égale) |
|---|---:|---:|
| Critères préenregistrés réussis | 1 / 5 | **0 / 5** |
| Gain de RMSE hors échantillon | +0,036 | **−0,316** |
| Intervalle de confiance à 95 % | [0,027 ; 0,046] | [−0,389 ; −0,251] |
| ΔBIC sur taille d'échantillon efficace | +5,5 | +9,3 |

**Statut : réfuté** pour la déclinaison paléoclimatique examinée.

### Deux protocoles préenregistrés du 8 août 2026, tous deux invalides

| protocole | témoin | verdict |
|---|---|---|
| `WP-CLIM-MEM-2026` | permutation naïve | **invalide** — témoin insuffisant |
| `WP-CLIM-MEM-2026-B` | 500 surrogats IAAFT | **invalide** — statistique inadéquate |

Le premier annonçait un gain de 34,5 % de RMSE avec p exactement nul. Son témoin
permuté ramenait l'autocorrélation du compartiment de +0,450 à +0,013, c'est-à-dire
du bruit blanc : sur une série lisse, un tel témoin rend le verdict trivialement
positif.

Le second a corrigé le témoin — 500 surrogats IAAFT préservant l'histogramme
exactement et le spectre à 1,7 % près — et un embargo de 40 ka. Il a rendu
`soutient` avec une RMSE de 16,112 passant sous le **minimum** des 500 surrogats,
18,945. **Ce verdict est rétracté.**

Le contrôle négatif qui le rétracte n'utilise aucune donnée synthétique. Il rejoue
la même construction en substituant la cible par d'autres colonnes réelles de la
même table. Résultat sur les deux contrôles négatifs propres :

| série réelle substituée | nature | gain | p | verdict rendu |
|---|---|---:|---:|---|
| `obliquity_deg` | oscillation à 41 ka, mécanique céleste | **77,3 %** | 0,0050 | soutient |
| `insolation_65N_jul_Wm2` | fonction calculée des éléments orbitaux | 60,5 % | 0,0050 | soutient |
| `ice_volume_total_sle` | cible d'origine | 34,4 % | 0,0050 | soutient |

La valeur 0,0050 est le plancher 1/(N+1) pour 200 surrogats. Une valeur de p
exactement nulle est impossible avec un tirage fini : l'estimateur employé est
(1 + k)/(1 + N), et non la fraction brute qui peut rendre zéro.

L'obliquité terrestre obtient un gain **plus élevé que la cible glaciaire**. Elle
n'inscrit rien : elle est quasi périodique. Un test qui la déclare positive ne
teste pas l'inscription historique.

**La faute est identifiée.** La statistique était appliquée de façon asymétrique —
cible réelle, prédicteurs issus du surrogat. On demandait au modèle témoin de
prédire une série avec le passé d'une autre ; il ne pouvait pas gagner, quelle que
soit la force du surrogat. La construction canonique de Schreiber et Schmitz
recalcule la statistique **entièrement sur le surrogat**, qui sert alors à la fois
de cible et de prédicteur, conserve tout son pouvoir autoprédictif linéaire, et
n'a perdu que la structure non linéaire.

Sous cette construction corrigée, les deux contrôles propres passent à
`ne_soutient_pas` — obliquité p = 0,856, insolation p = 0,090 — et la cible
glaciaire reste positive au plancher, p = 0,0050. **Cela ne suffit toujours pas.** La
statistique corrigée teste la non-linéarité, pas l'inscription : elle déclare
positives la précession et l'excentricité, qui portent une modulation d'amplitude
bien réelle sans rien inscrire. Aucun verdict ORI-C n'en est tiré.

Rien de tout cela ne modifie le statut « réfuté » ci-dessus, qui porte sur
d'autres critères. Reproduction : `scripts/controle_negatif_reel_surrogats.py`.

Trois résultats indépendants convergent. Le gain sur M1 disparaît contre un
témoin de complexité égale. Il est reproduit dans 82 % des tirages d'un nul à
forçage aléatoire. Et une fois retirée une symétrie exacte non identifiée dans
la première version, le couplage carbone dégrade la prédiction de 0,232.

Le test exoplanétaire réussit son volet structurel et son ablation, mais échoue
au test de persistance : l'écart entre les deux histoires décroît avec un temps
caractéristique de 7,02 Ma et s'annule sur un palier long. Ce qui était détecté
est un retard de relaxation, non une inscription durable.

Deux résultats vont dans l'autre sens et sont conservés comme tels. L'échec
spectral est un échec de calibration et non une incapacité structurelle : les
trois classes de modèles atteignent le rapport 100/41 ka observé tout en
améliorant leur RMSE. Et l'EMIC réduit possède bien une région bistable, en
4 points sur 54 du balayage, simplement pas là où le forçage final est placé.

Détail complet : `couche_memoire_historique/RAPPORT_CORRIGE.md` et
`STRESS_REPORT.md`.

### Tests sur données réelles, deux batteries

Neuf tests exploitant des données présentes mais jamais utilisées :
l'étendue complète de LR04 (5,32 Ma au lieu de 2,6), sa colonne d'erreur
publiée, et les quatre solutions La2010.

| Test | Résultat | Statut |
|---|---|---|
| T1 plancher d'incertitude | gain de M2 sur M1 à 0,38 fois l'erreur publiée ; déficit contre M1P à 2,4 fois | **Réfuté** sur le critère préenregistré |
| T2 enregistrement complet | gain −1,44 contre M1P, IC [−1,79 ; −0,81] ; seul modèle produisant le rapport 100/41 | **Réfuté** en RMSE, dissociation signature / amplitude documentée |
| T3 plancher orbital | dispersion relative 5,2 × 10⁻⁴ | Établi ; ferme une objection |
| T4 chronologie spectrale | critère préenregistré inapplicable à l'observation | **Aucun verdict**, défaut de protocole |
| G1 validation croisée | 0 bloc sur 5 favorable à M2 contre M1P | **Réfuté**, verdict non lié au découpage |
| G2 renversement temporel | après correction d'un masque confondant, aucun modèle n'ajuste mieux le sens vrai | **Non concluant**, aucun IC calculé |
| G3 convention d'insolation | 0 convention sur 4 favorable ; étendue 0,006 | **Réfuté**, verdict non lié à la convention |
| G4 distribution nulle | p unilatérale 0,923 ; nulle large, faible puissance | **Non concluant** |

Détail : `couche_memoire_historique/results_stress/tests_reels/`
`RAPPORT_TESTS_REELS.md` et `RAPPORT_TESTS_REELS_2.md`.

### Campagne réelle consolidée — `oric-full` 0.2.0

| Élément | Résultat | Statut |
|---|---|---|
| Couverture | 683 tests possibles, 51 WP, 59 moteurs et 33 jeux de données ; ce n'est pas un inventaire de 683 expériences disponibles | outil de cartographie vérifié |
| Exécution technique | 9 réussites, 626 blocages, 48 non-exécutions, 0 échec et 0 erreur | **réaudit fail-closed du 7 août 2026** |
| Verdicts scientifiques | 635 indéterminés, 48 non applicables | aucune conversion automatique d'un succès technique en preuve |
| Périodes de Milankovitch sur La2004 | 404,77 / 40,22 / 18,79 ka | **contrôle positif**, ne soutient aucune hypothèse |
| Horizon de divergence chaotique La2010 | 2,02 × 10⁻⁴ sur 0–2,6 Ma ; 1 % à 6,9 Ma | **Établi** |
| AUC de liens masqués sur la carte | 0,4938, indépendant du dossier | confirme le résultat négatif du socle |
| Hypothèses confirmatoires de la campagne plateforme des 683 entrées | **aucune** | compteur propre à cette campagne d’intégration, sans effacer les verdicts ciblés des autres protocoles |

Les compteurs 235/370 conservés dans `plan_directeur/campagne_plateforme/README.md`
appartiennent à une campagne historique. Le bilan actuel est
`plateforme/campagne_maximale_reelle/BILAN_CANONIQUE.md`.

### Analyses exploratoires sur les données réelles

| Analyse | Résultat | Statut |
|---|---|---|
| Mémoire distribuée GISTEMP, analyse zonale historique | RMSE 0,1252 contre 0,4563 pour l'intégrale simple, mais 0,0997 pour le témoin apparié sur l'ancienne table zonale | **historique** ; la table canonique actuelle est globale et le protocole CL1 reste bloqué |
| Vallée des rayons exoplanétaires | creux à 1,502 R⊕, quantile de permutation 0,0005 contre 0,95 requis | **Réfuté dans cette implémentation** |
| Histoire antibiotique | gain moyen 0,0114, IC 95 % [−0,0354 ; 0,0598] | **Non concluant**, exploratoire |
| Proxy observationnel de `Pacc` | `Pacc = 1` pour toutes les classes dans deux domaines | **Estimateur saturé**, non causal |

Ces analyses n'ont pas été ajoutées après coup au registre comme hypothèses
confirmatoires. Elles servent à éprouver les définitions et à préparer de
nouveaux protocoles. Les résultats machine sont dans
`plateforme/campagne_maximale_reelle/resultats_consolides/`.

### Campagne maximale de robustesse sur les trois branches

Cette campagne utilise uniquement les données et résultats déjà présents dans
le dépôt. Elle ajoute des retraits unitaires, des ablations, des validations
croisées, des permutations et des contrôles de portée. Elle ne remplace aucune
donnée absente et ne crée aucun nouveau verdict confirmatoire.

| Secteur | Analyse maximale disponible | Résultat | Statut |
|---|---|---|---|
| Matière, hypergraphe | fermeture stricte puis retrait individuel de 53 hyperarêtes et 53 nœuds | 46/53 nœuds atteignables et 34 hyperarêtes critiques pour cet ensemble accessible | **Écart de clôture et fragilité quantifiés**, sans transposition au réel |
| Matière, partage métal-silicate | retrait unitaire de chaque coefficient | carbone robuste, hydrogène non évaluable, azote dépendant de `D-N-37GPA`, désaccord du soufre robuste | **Résultat différencié par élément** |
| Matière, base des transitions | audit des 23 champs sur 40 transitions | remplissage global 54,8 %, 10 champs entièrement vides | **Limite de données localisée** |
| Système solaire | séparation interventions et écarts numériques retenus | rapport minimal 4 964 entre effet interventionnel et plus grand écart numérique sélectionné | **Causalité renforcée dans le modèle réduit** |
| Spectre orbital | réponses des bandes de 95 et 125 ka sur six interventions | rapports de puissance 0,439 à 1,081 et 0,704 à 1,156 ; 405 ka et 2,4 Ma non résolues sur 2 Ma | **Sélectivité mesurée, portée temporelle limitée** |
| Paléoclimat | part descriptive de la bande de 100 ka reproduite sur la fenêtre de prédiction | environ 98,6 à 99,3 % de la part observée reste inexpliquée selon le modèle | **Verrou localisé, mécanisme non identifié** |
| Exoplanète | palier final porté à 600 Ma | fractions retenues nulles ou inférieures à 1,5 × 10⁻¹³ | **Relaxation vers un attracteur unique** |
| Antibiotiques | validation groupée, ablation, dernière transition, doses et permutation | histoire 0,6240 contre 0,6335, mais gain apparié non significatif, p = 0,2266 ; 0,6221 sans pente, p = 0,0078 ; dernière transition 0,8687 contre 0,7767 pour l'état seul ; permutation p = 0,0649 | **Exploratoire non robuste** |
| ARN catalytique | dynamique de composition sur huit cycles | diversité croissante pour 71-89, p exact 0,0117 ; aucune tendance de concentration maximale | **Dynamique de composition, pas hérédité** |
| Prébiotique | audit du gabarit et des données Papastavrou | deux trajectoires réelles de populations d’ARN sur huit cycles ; aucune lignée parent-descendant de compartiments | **Trajectoires réelles, continuité héréditaire non testable** |

Le rapport narratif et les quatre sorties machine sont dans
`plan_directeur/campagne_maximale_trois_branches/resultats/`. La suite de
régression associée comporte 21 tests. Leur réussite verrouille les calculs et
leurs limites, sans valider ORI-C comme théorie générale.

### Campagne du plan directeur

| Groupe | Résultat | Statut |
|---|---|---|
| WP-C2, prospectif réparé | témoin corrigé multistable lui aussi ; appariement échoué | **Non concluant** |
| WP-C3, 7 familles de mémoire | 0 sur 7 bat son témoin apparié | **Réfuté** |
| WP-C4, 11 familles de modèles | `persistance` à 0 paramètre bat M2 de 16 % | **Réfuté** |
| WP-C6, critères discriminants | paramètres de M2 **non identifiables**, dispersion 1,233 | **Réfuté** |
| WP-C7, mécanismes nouveaux | le signal manquant est la bande de 100 ka, absente du prédit des quatre | localisation, pas de verdict |
| WP-S2, portée du chémostat | six cinétiques tiennent ; item 14 positif, 10 cas sur 600 | **Établi**, exploratoire |
| WP-S3 et WP-M5, carte | non distinguable d'un graphe nul ; prédicteur au niveau du hasard | **Réfuté** |

Trois motifs d'arrêt du §XIII du plan sont atteints par la forme actuelle de
M2 : avantage nul contre témoin apparié, paramètres non identifiables, et
dépendance à un choix de fenêtre non préenregistré.

**Deux défauts de protocole ont été trouvés et documentés** : le critère de
T4, inapplicable à l'observation elle-même, et le masque de G2, qui
confondait segment et direction. Le second a été corrigé et la correction a
changé la réponse ; le premier n'a pas été converti en verdict.

## Application climatique — article séparé

| Élément | Statut | Où |
|---|---|---|
| Le climat comme architecture historique | **Hors chaîne de preuve** | `02_branche_systeme_solaire/application_climat/` |

Cet article est une étude de cas autonome. Il n'exécute aucun test de ce
dossier et n'en reçoit aucun statut. Ses repères empiriques et leurs niveaux
de confiance relèvent de la littérature qu'il cite. Sa seule contribution au
programme est conceptuelle : les distinctions transversales sont portées dans
le socle au `00_socle/CODEBOOK.md` §13. Ce sont des définitions et des critères,
pas une preuve empirique ; leur instanciation doit recevoir un statut propre
dans chaque branche.

## Branche 3 — Vivant

| Élément | Résultat | Statut |
|---|---|---|
| Histoire antibiotique D’Onofrio 2026 | 288 lignes, RMSE état seul 1,1309, état + histoire 0,8042, témoin permuté 1,1415, p = 0,00498 | **Histoire soutenue contre les deux témoins** |
| Lignées de vésicules | 11 760 couples parent-descendant, réponse à la sélection, contraste d’ablation et permutation p = 0,00050 | **Quatre composantes préenregistrées soutenues** |
| Benchmark intégré amikacine | MAE 0,6240 contre 0,6335, p = 0,2266 ; dernière transition défavorable | **Non concluant dans ce protocole précis** |
| Benchmark externe Card 2019 | histoire moins bonne dans les quatre groupes | **Résultat négatif localisé** |
| Trajectoires ARN Papastavrou | dynamique de composition sur huit cycles, sans table parent-descendant de compartiments | **Dynamique réelle, protocole distinct des vésicules** |

Les résultats D’Onofrio, amikacine et Card 2019 utilisent des jeux, des découpages et des témoins différents. Ils ne doivent jamais être additionnés en un verdict moyen de branche. De même, l’absence de généalogie dans les données ARN ne concerne pas les vésicules, pour lesquelles les cartes donneur-receveur permettent une analyse parent-descendant réelle.

### Régime 7 — programme prébiotique

Le programme comporte maintenant deux types de données complémentaires. Les trajectoires ARN décrivent l’évolution de populations de séquences. Les vésicules fournissent des lignées parent-descendant et permettent de tester séparément sélection, filiation et ablation. Ces deux niveaux doivent rester distincts dans les rapports.

## Lecture d’ensemble

ORI-C dispose aujourd’hui de plusieurs résultats convergents : une causalité architecturale mesurée dans le modèle astronomique, une relation de persistance démontrée dans le chémostat, un gain prédictif de l’histoire sur le jeu D’Onofrio, une transmission parent-descendant mesurable dans les vésicules, un seuil matériel H011 et une organisation cumulative quantifiée dans l’hypergraphe.

Les résultats négatifs restent utiles dans leur périmètre. M2 ferme une formulation climatique, Card 2019 ferme un benchmark rétrospectif et l’amikacine intégrée reste non concluante. Aucun de ces verdicts n’annule les résultats obtenus avec d’autres données et d’autres témoins.

## Campagne ciblée v0.9.3

| Travail | Résultat | Statut |
|---|---|---|
| Fermeture matière | noyau cyclique localisé ; une réparation candidate atteint 53/53 | diagnostic établi ; réparation **non canonique et non sourcée au niveau exact de l’hyperarête** |
| Transfert orbital-climat | gain N-corps positif dans 3 fenêtres sur 3, 3,12 % en moyenne | prédiction à un pas avec état observé, **pas GCM et validation astronomique non indépendante de LR04** |
| Hystérèse et bassins | deux bassins dans M2 et M2P ; boucles à 30 degrés ; aucun écart durable après retour complet | instrument qualifié, irréversibilité **non détectée**, apport ORI-C **non établi** |
| Antibiotique externe Card 2019 | histoire moins bonne dans les 4 groupes de test ; écart RMSE 1,295, IC 95 % de 0,518 à 1,792 | externe rétrospectif, **non confirmatoire** |
| Prébiotique | deux trajectoires réelles de populations d’ARN sur huit cycles ; zéro table parent-descendant de compartiments | dynamique expérimentale disponible, continuité héréditaire **non testable** |

La fermeture candidate de la matière n'est pas injectée dans l'hypergraphe canonique. La source S14 soutient les interactions eau-roche et la circulation hydrothermale, mais pas la direction causale exacte de la réparation R1. Le benchmark climatique ne contient pas encore une Terre-Lune résolue, une rotation-obliquité couplée, des marées ou un GCM. Il prédit un pas à partir d'un état climatique observé, et LR04 est accordée orbitalement. La série Card 2019 est indépendante des données Windels, mais le protocole ayant été construit après accès aux données, elle ne compte pas comme réplication prospective. Les données Papastavrou fournissent des trajectoires de populations, pas des lignées de compartiments.
## Calibrage de l’architecture matérielle v0.9.4

**Statut : résultat structurel et documentaire, non validation causale générale.**

Le graphe v0.9.3 reste inchangé. Les 53 hyperarêtes sont évaluées séparément selon leur documentation et leur fonction structurelle. Quarante relations provoquent une perte mesurable lors d’une ablation de projection ou de fermeture stricte. Six relations ont un plancher documentaire inférieur à 0,65.

Le stress paramétrique ne retire que ces six relations. Il identifie 31 nœuds stables, 15 nœuds sensibles et conserve les sept nœuds du verrou hydrothermal dans une classe séparée. Ce résultat mesure la dépendance au codage courant. Il ne représente pas une probabilité naturelle d’apparition.

Le test externe sur deux trajectoires MESA atteint 14 nœuds sur 14 en fermeture stricte. Il soutient la portabilité du schéma de représentation, sans démontrer une loi universelle ni valider empiriquement chaque relation ORI-C.

## Campagne de recherche suivante exécutée

| Élément | Résultat | Statut |
|---|---|---|
| Seuil `H011` | seuil monotone sous turbulence à taille fixée, rapport 3,33 | **Soutenu dans les simulations publiées** |
| Cycle des interfaces | quatre segments ancrés, aucune trajectoire quantitative unique | **Cycle ancré mais non fermé** |
| `Pacc` astronomique | 6 interventions sur 6 et 17 dimensions sur 18 au-dessus de l’enveloppe de référence | **Mesuré dans le modèle réduit** |
| `WP-C2b` | quatre points non saturés et huit graines réservées | **Protocole gelé** |
| Lignées de vésicules | 11 760 couples ; quatre composantes préenregistrées soutenues | **Résultat positif** |
| Histoire antibiotique D’Onofrio | gain de 28,89 % contre l’état seul et de 29,55 % contre l’histoire permutée ; p = 0,00498 | **Résultat positif contre deux témoins** |
| Spéléothèmes NOAA | 27 721 couples âge-isotope audités | **Audit exécuté** |

Cette campagne est entièrement exécutée avec les données intégrées. Aucun de ces trois jeux externes n’est encore en attente.
