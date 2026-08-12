# Autorité des documents

L'échelle transversale de force des résultats est définie dans
[`00_socle/ECHELLE_PREUVE_E0_E6.md`](00_socle/ECHELLE_PREUVE_E0_E6.md). Elle ne
remplace ni les critères gelés ni leurs verdicts ; elle indique les contrôles
effectivement franchis.

Quand deux fichiers se contredisent, celui-ci tranche.

## Document principal

| Rôle | Fichier | Statut |
|---|---|---|
| Dossier scientifique complet | `documentation/dossier_scientifique/DOSSIER_SCIENTIFIQUE_ORI-C.pdf` | synthèse de lecture, ne remplace pas les résultats générés |
| Architecture générale | `ORI-C_Architecture_generale_du_programme.pdf` | orientation générale |

Il donne une lecture continue du programme. Il **ne remplace pas** les articles
de branche, ne transforme pas le socle en quatrième branche et ne propage aucun
niveau de preuve d'un domaine à l'autre. Les copies racine du dossier
scientifique sont des alias de livraison décrits dans
`documentation/ALIASES_DOCUMENTAIRES.md`. Sur tout chiffre de test ou de statut,
les fichiers générés priment sur lui, conformément à la règle générale
ci-dessous.

## Règle générale

1. Un **rapport généré** prime sur un document rédigé, parce qu'il est
   recalculé à chaque exécution.
2. Un **erratum** prime sur l'article qu'il accompagne.
3. Un **article** prime sur ses variantes et versions antérieures.
4. En dernier ressort, `preuves/PREUVES.json` fixe le statut machine de chaque résultat. `ETAT_DES_PREUVES.md` en est la vue générée destinée à la lecture humaine. `preuves/CHIFFRES.json` fixe les nombres canoniques rendus publiquement. Pour la publication `0.9.7-research`, **13/15 en astronomie et M2 à 1/10 restent des invariants documentaires contrôlés par CI** ; les nouveaux résultats `INV-A` ne peuvent pas les reclasser.

## Règles de lecture et de mise à jour

1. Un résultat négatif reste limité au protocole qui l’a produit. Il ne peut pas être étendu à une branche entière ni au programme.
1 bis. **Un résultat négatif dont le critère est inatteignable n’est pas un résultat.** Avant de citer un échec, vérifier son statut dans `ATTEIGNABILITE_DES_CRITERES_2026-08-08.md`. Sur 23 critères discrets, 20 sont atteignables et 3 ne sont pas évaluables par cette voie.

Un seul critère reste écarté pour inatteignabilité : la **vallée des rayons**, dont le seuil n’est franchi à aucune taille disponible et dont la profondeur mesurée est négative, −0,002420, sur 0 succès en 40 tirages à n = 200, 400, 800 et 1600.

Les trois critères « non évaluables » sont des **bootstraps** — `mpt/bootstrap_draws`, à 20 000 et 200 tirages. Un bootstrap rééchantillonne la distribution observée et estime un intervalle ; il ne construit pas une distribution nulle par ré-étiquetage. Il n’a donc pas de plancher de p général, contrairement à une permutation dont la plus petite valeur vaut 1/(N+1). Leur atteignabilité doit être établie protocole par protocole, et ne peut pas être déduite du nombre de tirages.

**Correction du 8 août 2026.** Cette règle citait auparavant deux critères supplémentaires, « les deux tests de signe du benchmark antibiotique longitudinal, qui exigent 9 plis favorables sur 10 ». C’était faux. Le benchmark n’emploie pas un test de signe mais un test de **sign-flip** : `plan_directeur/campagne_maximale_trois_branches/analyse_vivant.py`, ligne 179, calcule `abs(np.mean(differences * signs))`. Le test de signe ne compte que les unités favorables et jette les magnitudes ; le sign-flip énumère les 2ⁿ attributions de signe et compare la moyenne signée observée, magnitudes comprises. Il n’exige aucun nombre minimal d’unités favorables, et sa plus petite valeur de p vaut 2/2¹⁰ = 1,95 × 10⁻³. Ces deux critères sont **atteignables**. L’auditeur les modélisait par le mauvais test ; il distingue désormais les trois familles.

1 ter. **Un compteur empirique et un compteur de modèle ne s’additionnent pas, et un moteur non déclaré n’est pas empirique.** `plateforme/campagne_maximale_reelle/resultats_integration_maximale/COMPTEURS_SEPARES.json` répartit les 683 entrées en trois colonnes qui ne se somment jamais :

| colonne | entrées | réussites techniques |
|---|---:|---:|
| empirique | **40** | 5 |
| modèle | 156 | 0 |
| indéterminé | **487** | 4 |

**Correction du 8 août 2026.** Cette règle annonçait auparavant « 479 entrées empiriques dont les 9 réussites techniques ». C’était le produit d’un défaut *fail open* : `separer_compteurs.py` classait en empirique tout moteur absent de `EMPIRICAL_POLICY.json`. Or 439 des 479 entrées ainsi comptées avaient un moteur dont l’admissibilité comme preuve empirique n’était déclarée nulle part. Le classement est désormais *fail closed* : un moteur non déclaré est **indéterminé**, jamais empirique. Un dépôt qui se réclame du pare-feu empirique ne peut pas classer par optimisme ce qu’il n’a pas vérifié. Les 9 réussites techniques se répartissent en 5 empiriques et 4 indéterminées ; aucune n’est un résultat de modèle.

1 quater. **La matrice des 683 est un diagnostic de couverture, pas une source de preuves.** Ses 626 blocages ne sont pas 626 expériences échouées. Le relevé des `coverage_gaps` contient 343 occurrences `test_hors_portee_mesuree`, 300 `non_admissible_comme_preuve_empirique` et 63 `aucun_jeu_empirique_declare`. Comme un test peut cumuler plusieurs causes, cela correspond respectivement à 320, 255 et 63 tests distincts, sans addition possible. Le classement régénérable `PRIORITES_ACQUISITION_DONNEES` déduplique aussi les tests par dataset. Aucun rapport ne doit présenter ce compteur comme une mesure de l’avancement scientifique : il sert à choisir les acquisitions capables de lever le plus de blocages.

1 quinquies. **Un verdict exige deux choses, et la force du témoin n’en est qu’une.**

*Premier axe — force du témoin.* Par ordre croissant :

| niveau | témoin |
|---|---|
| 1 | mélange simple |
| 2 | randomisation de phase de Fourier |
| 3 | AAFT |
| 4 | **IAAFT — minimum exigé pour tout critère temporel ORI-C** |
| 5 | IAAFT plus plusieurs statistiques indépendantes : prédiction, dimension, réversibilité temporelle |
| 6 | réplication sur données indépendantes, mêmes surrogats |

*Second axe — adéquation de la statistique.* Un témoin de niveau 6 sur une
statistique qui ne teste pas l’hypothèse ne produit rien. La statistique doit être
**recalculée entièrement sur le surrogat**, qui sert alors à la fois de cible et de
prédicteur : c’est la construction de Schreiber et Schmitz. Toute construction
asymétrique — cible réelle, prédicteurs issus du surrogat — handicape le témoin par
construction et rend le verdict trivialement positif.

*Contrôle négatif obligatoire.* Avant tout gel, la construction doit être rejouée
sur des séries **réelles** dont on sait par leur source qu’elles ne portent pas le
phénomène visé. Aucune série synthétique : le contrôle se fait par substitution de
la cible dans la table réelle. Si un contrôle négatif propre obtient un verdict
positif, le protocole ne peut pas être gelé. `scripts/controle_negatif_reel_surrogats.py`
tient ce rôle pour la couche mémoire ; l’obliquité terrestre y est le contrôle de
référence.

Les deux précédents sont instructifs parce qu’ils échouent sur des axes différents.
`WP-CLIM-MEM-2026` avait un témoin de niveau 1 : permuter ramenait l’autocorrélation
de +0,450 à +0,013. `WP-CLIM-MEM-2026-B` avait un témoin de niveau 4, correct, et une
statistique asymétrique : elle accordait `soutient` à l’obliquité terrestre avec un
gain de 77,3 % et p nul, soit plus que la cible glaciaire. Les deux sont clos sur
`invalide`. Un bon témoin ne rachète pas une mauvaise statistique.

*Enfin, aucun test de non-linéarité n’est universel.* IAAFT correctement appliqué
teste la non-linéarité, ce qui n’est pas l’inscription historique : la précession
vaut e·sin(ω), sa modulation d’amplitude est une non-linéarité réelle, et elle
n’inscrit rien. Une statistique nouvelle reste à construire pour l’hypothèse ORI-C.

**Règle causale transversale.** Un gain prédictif de l'histoire ne suffit pas à attribuer un effet causal à `m`. Une telle attribution exige une intervention ou une ablation ciblée de la trace, avec `X` et les composantes non visées de `A` appariés selon des tolérances gelées, puis une réponse future supérieure au témoin de complexité appariée et au plancher de bruit. La causalité sur `A` exige de la même manière une intervention explicite sur l'architecture. `C-AST-01` est le prototype méthodologique actuel dans un modèle réduit, pas une preuve transférable aux autres branches.

**Règle d’or pour tout nouveau résultat.** Les avancées viennent des pipelines ciblés, jamais de la matrice générique. L’ordre est contraignant et ne se réarrange pas :

1. écrire le critère exact et la liste des variables obligatoires ;
2. vérifier qu’une source publique les contient **toutes**, sans imputation ;
3. préenregistrer le protocole et sceller son empreinte SHA-256 ;
4. seulement ensuite intégrer la donnée et lancer le test ciblé.

Intégrer d’abord et chercher ensuite ce que la donnée permet de tester produit des résultats non préenregistrés, donc non confirmatoires.
2. Les jeux Windels, Card 2019, D’Onofrio, Papastavrou et vésicules sont distincts. Aucun rapport ne peut utiliser le résultat de l’un pour qualifier les autres.
3. `MISE_A_JOUR_RECHERCHE.md` et les fichiers machine de `campagne_recherche_suivante/` priment sur les synthèses antérieures lorsqu’ils décrivent D’Onofrio, les vésicules, H011, `Pacc` ou les spéléothèmes.
4. Une campagne historique reste autorité sur son propre calcul, mais pas sur l’état courant global du dépôt.
5. Toute mise à jour part de la dernière archive ou du dernier commit validé. Les tests susceptibles de régénérer des résultats sont exécutés avant la construction des manifestes.
6. Le dépôt porte **trois** manifestes : la racine, `02_branche_systeme_solaire/couche_memoire_historique/` et `plan_directeur/revue_systematique/`. Chacun gouverne son périmètre et **tous** doivent être reconstruits avant un push, le manifeste racine en dernier puisqu'il hache les deux autres. Le contrôle unique est `scripts/controle_avant_push.py`, qui croise l'index Git avec les trois manifestes puis enchaîne `verifier_dossier.py` et `scripts/verifier_fins_de_ligne.py`. Ce dernier est indispensable : `verifier_dossier.py` compare le manifeste à la copie de travail et ne peut donc pas voir qu’un fichier écrit en CRLF sera restitué en LF au clonage. Sans lui, le contrôle passe en local et échoue après le `push`. Le 8 août 2026, cinq étapes de trois workflows ont échoué pour une seule cause : `scripts/surrogats.py` poussé hors du manifeste racine et neuf fichiers importés dans la couche mémoire hors de son manifeste local. Aucun contrôle ne croisait alors l'index Git avec les manifestes de sous-périmètre.
7. Une livraison de correction contient uniquement les fichiers modifiés et les suppressions explicitement demandées. Les données tierces brutes exclues ne doivent jamais être réintroduites.
8. Le contrôle de publication doit refuser les formulations périmées qui décrivent les vésicules ou D’Onofrio comme encore en attente.

## Socle

| Rôle | Fichier | Statut |
|---|---|---|
| Référence du vocabulaire | `00_socle/CODEBOOK.md` | canonique |
| Protocole de données | `00_socle/PROTOCOLE_DONNEES.md` | canonique ; ses trois tables sont vérifiées par `valider_donnees.py` |
| Données de la carte | `00_socle/carte_relationnelle/data/*.csv` | canonique |
| Figures de la carte | `00_socle/carte_relationnelle/resultats/*` | à régénérer, voir `REGENERATION_REQUISE.md` |
| Écarts de codage | `00_socle/carte_relationnelle/REGENERATION_REQUISE.md` | canonique |
| Test interventionnel, code | `00_socle/test_interventionnel/scripts/` | canonique |
| Test interventionnel, verdict | `00_socle/test_interventionnel/resultats_exhaustifs/rapport_exhaustif.txt` | généré, prime |
| Historique des corrections | `…/resultats_exhaustifs/CORRECTION_ANALYSE_EXHAUSTIVE.md` | canonique |
| Compteurs de tests | `ETAT_DES_TESTS.md` | généré, prime sur tout compteur cité ailleurs |
| Mémoire, architecture, possibles | `00_socle/CODEBOOK.md` §13 | canonique ; le socle prime sur l'article d'application dont il est extrait |
| Analyse de graphe de la carte | `00_socle/carte_relationnelle/ANALYSE_GRAPHE.md` | généré, prime ; **exploratoire** |
| Portée du test interventionnel | `00_socle/test_interventionnel/PORTEE_WP_S2.md` | généré, prime ; **exploratoire** |
| Rapports antérieurs | `00_socle/sources/` | archives, ne priment sur rien |

Les fichiers de `00_socle/sources/` décrivent l'état du dossier consolidé
d'origine. Ils emploient encore ses anciens chemins et ses anciens compteurs.
Ils sont conservés comme archives et **ne font pas autorité**.

`CONTROLES_INTEGRITE.md` et `audit/validation_archive.json` sont également des
instantanés historiques. Leurs compteurs sont conservés pour la traçabilité,
mais `ETAT_DES_TESTS.md` reste l'unique état courant.

## Branche 1 — Matière

| Rôle | Fichier | Statut |
|---|---|---|
| Article de référence | `01_branche_matiere/article/Chronologie_des_architectures_de_la_matiere_ORI-C.docx` | canonique, format source |
| Diffusion | `…/Chronologie_des_architectures_de_la_matiere_ORI-C.pdf` | canonique, format de lecture |
| Variante | `…/variantes/ORI-C_document_unique_sans_fusion_des_contenus.pdf` | archive, remplacée |

La variante est une version antérieure, sans fusion des contenus. Elle est
conservée pour traçabilité et ne doit pas être citée.

| Rôle | Fichier | Statut |
|---|---|---|
| Inventaire historique des transitions | `01_branche_matiere/base_transitions/transitions_matiere.csv` | canonique, objet audité, **conservé tel quel** |
| Représentation de travail | `01_branche_matiere/hypergraphe_transformations/noeuds.csv` et `hyperaretes.csv` | canonique pour la structure |
| Chiffres de structure | `…/validation_hypergraphe.json` | prime sur toute prose |
| Chiffres d'inventaire | `…/inventaire_accessible_resultats.json` | prime sur toute prose |
| Épreuves de l'échelle | `…/test_hierarchie_execution_1_prereglee.json` | **préenregistré, prime sur les exécutions ultérieures** |

L'hypergraphe corrige la représentation linéaire **sans effacer** la base
historique, qui reste l'objet audité. En cas de divergence entre les deux sur
une filiation, l'hypergraphe tranche pour la structure, la base pour la
traçabilité de ce qui avait été affirmé auparavant.

Sur l'échelle des dix capacités, l'exécution préenregistrée prime sur toutes
les suivantes. Elle porte une réfutation. Les exécutions postérieures
incorporent deux corrections de niveau faites après lecture des violations :
elles sont explicitement marquées exploratoires et ne doivent jamais être
citées comme une validation.

### Généalogie cosmique empirique post-v0.9.5

| Rôle | Fichier | Statut |
|---|---|---|
| Politique d'admissibilité | `01_branche_matiere/genealogie_cosmique_quantitative/EMPIRICAL_ONLY_POLICY.json` | **autorité : données réelles uniquement ; simulations/synthétique/imputation interdits comme preuve** |
| Protocole de raccordement cosmique → Système solaire | `01_branche_matiere/genealogie_cosmique_quantitative/PROTOCOLE.md` | canonique pour le nouveau front de recherche |
| Sources et mesures | `SOURCES_EMPIRIQUES.csv` et `data/MESURES_EMPIRIQUES.csv` | sources primaires/officielles et valeurs mesurées admissibles ; portions modélisées explicitement exclues |
| Chaîne et liens | `CHAINE_EMPIRIQUE.csv` et `LIENS_EMPIRIQUES.csv` | distinguent continuité matérielle, même archive, analogue, laboratoire et liens non uniques |
| Audit d'admissibilité | `.../resultats/AUDIT_ADMISSIBILITE.json` | doit afficher 0 simulation, 0 synthétique, 0 imputation |
| Résultat machine | `.../resultats/SYNTHESE.json` | généré, prime sur les résumés rédigés |
| Claims locaux | `.../resultats/claims/C-GC-E*.json` | synthèse empirique initiale non préenregistrée ; aucune certification héritée |
| Raccordement Système solaire | `.../resultats/HANDOFF_SYSTEME_SOLAIRE.json` | endpoint présent observé ; trajectoire orbitale unique `undetermined_empirical_only` |

La nouvelle couche ne modifie pas les transitions historiques antérieures. Elle les réévalue sous un pare-feu empirique séparé et interdit qu'une simulation ou une sortie de modèle ferme un maillon manquant. `C-AST-01` reste hors de cette preuve de genèse et conserve son statut modèle propre.

## Branche 2 — Système solaire

| Rôle | Fichier | Statut |
|---|---|---|
| **Erratum** | `02_branche_systeme_solaire/article/ERRATUM.md` | **prime sur l'article** |
| Article | `…/article/Architecture_historique_du_Systeme_solaire_ORI-C.pdf` | canonique sauf sur les points de l'erratum |
| Filtrages historiques | `…/FILTRAGES_HISTORIQUES.md` | canonique ; fixe aussi les formulations correctes sur noyau, tectonique et chaîne cosmique |
| Couche astronomique, statut | `…/couche_astronomique/STATUT_SCIENTIFIQUE.md` | canonique |
| Couche mémoire, document maître | `…/couche_memoire_historique/RAPPORT_CORRIGE.md` | canonique |
| Couche mémoire, verdict | `…/couche_memoire_historique/REPORT.md` | généré, prime |
| Couche mémoire, contrôles | `…/couche_memoire_historique/STRESS_REPORT.md` | généré |
| Tests réels, batterie 1 | `…/results_stress/tests_reels/RAPPORT_TESTS_REELS.md` | généré, prime |
| Tests réels, batterie 2 | `…/results_stress/tests_reels/RAPPORT_TESTS_REELS_2.md` | généré, prime ; le G2 corrigé **remplace** le G2 d'origine |
| WP-C2, test prospectif réparé | `…/results_stress/prospectif_c2/RAPPORT_WP_C2.md` | généré, prime ; **remplace** `RAPPORT_PROSPECTIF.md` |
| WP-C3, familles de mémoire | `…/results_stress/tests_reels/RAPPORT_WP_C3.md` | généré, prime |
| WP-C4, familles de modèles | `…/RAPPORT_WP_C4.md` | généré, prime |
| WP-C6, critères discriminants | `…/RAPPORT_WP_C6.md` | généré, prime |
| WP-C7, mécanismes nouveaux | `…/RAPPORT_WP_C7.md` | généré, prime |

L'article est antérieur à l'exécution des tests de la couche mémoire. Sur tout
ce qui concerne la réponse climatique dépendante de l'histoire, l'erratum et le
rapport corrigé font foi.

### Application climatique — article séparé

| Rôle | Fichier | Statut |
|---|---|---|
| Article d'application | `…/application_climat/Le_climat_comme_architecture_historique_ORI-C.docx` | canonique **dans son périmètre propre** |
| Périmètre et extraction | `…/application_climat/README.md` | canonique |

Cet article est une **étude de cas autonome**, pas une quatrième branche et pas
un complément de l'article de branche 2. Trois règles s'y appliquent.

1. **Il ne propage aucun niveau de preuve.** Ses repères empiriques viennent de
   la littérature qu'il cite ; aucun test de ce dossier ne porte sur eux, et il
   ne reçoit rien des résultats de la couche mémoire historique.
2. **Sur les notions transversales qui en ont été extraites — mémoire
   distribuée, diagnostic `D-H-L`, filtres des possibles, persistance
   vectorielle, séparation `S`/`m`/`A`, distinction `ℓ_ana/{ℓ_phys}`,
   régimes `(D_i,G_i)`, raccords `T(i→j)`, mise à jour `U_i`, critère
   d'altération architecturale et séparation des chaînes physique et
   épistémique — c'est le `CODEBOOK.md` §13 qui fait
   foi**, conformément à la règle générale : le socle prime, l'article
   d'application illustre.
3. **Son contenu de domaine reste chez lui.** Océan, cryosphère, pergélisol,
   sols, biosphère, AMOC, engagement d'émissions nulles, seuils de basculement
   et implications de décision n'appartiennent pas au socle et ne doivent pas y
   remonter.

## Branche 3 — Vivant

| Rôle | Fichier | Statut |
|---|---|---|
| Article de référence | `03_branche_vivant/article/Le_vivant_comme_terrain_ORI-C.docx` | canonique |
| Diffusion PDF | — | **absent**, à produire |

Le PDF de diffusion n'a pas encore été produit. Tant qu'il manque, le DOCX est
le seul document de référence de cette branche.

### Régime 7 — programme prébiotique

| Rôle | Fichier | Statut |
|---|---|---|
| Programme dirigé | `03_branche_vivant/programme_prebiotique/PROGRAMME_PREBIOTIQUE.md` | canonique |
| Schéma de lignées, validateur | `…/valider_lignees.py` | canonique ; rend exécutables le §4.2 et le §6 du programme |
| Gabarit de lignées | `…/schema_lignees/gabarit/lignees.csv` | **synthétique**, aucune valeur de mesure |

Le programme est **distinct de l'acte 3** de l'article, qui porte sur une
population déjà vivante. Aucun statut ne circule entre les deux. Le gabarit
porte le marqueur `GABARIT_SYNTHETIQUE` : toute lecture de ses valeurs comme
résultat est une erreur, et le validateur l'annonce à chaque exécution.

## Plan directeur et registre

| Rôle | Fichier | Statut |
|---|---|---|
| Plan de campagne | `plan_directeur/PLAN_DIRECTEUR_TESTS.md` | canonique ; **plan, pas résultat** |
| Protocole transversal de causalité `X/m/A` | `plan_directeur/PROTOCOLE_CAUSALITE_ARCHITECTURALE_XMA.md` | méthodologique et prospectif ; **ne fixe aucun verdict** ; chaque instanciation confirmatoire doit être gelée séparément |
| Extension astronomie globale | `02_branche_systeme_solaire/couche_astronomique/code/ORI-C_Systeme_solaire_tests/docs/EXTENSION_ARCHITECTURE_GLOBALE_SPIN_ORBITE.md` | feuille de route historique de l’extension ; la partie spin réduite a depuis été exécutée séparément |
| Couche spin-orbite, résultat | `02_branche_systeme_solaire/couche_spin_orbite/resultats/RAPPORT.md` | généré, prime pour les résultats spin/obliquité/insolation ; **niveau modèle, ne modifie pas la certification de `C-AST-01`** |
| Couche spin-orbite, méthode et limites | `02_branche_systeme_solaire/couche_spin_orbite/README.md` et `PROVENANCE.md` | canonique pour l’équation, les constantes de précession et la distinction couple lunaire effectif / Lune N-corps résolue |
| Registre des hypothèses | `plan_directeur/REGISTRE_HYPOTHESES.csv` | généré, prime sur tout statut cité ailleurs sauf `preuves/PREUVES.json` |
| Avancement | `plan_directeur/AVANCEMENT_DU_PLAN.md` | généré ; descriptif, ne fixe aucun statut |
| Grille de l'Étape 2 | `plan_directeur/GRILLE_ETAPE_2.md` | généré ; audit, ne fixe aucun statut |
| Audit transversal | `plan_directeur/AUDIT_TRANSVERSAL.md` | généré, prime ; **exploratoire** |
| Audit du seuil scientifique §XIV | `plan_directeur/campagne_centrale_2026_08_11/resultats/SEUIL_XIV.json` | généré ; diagnostique les 12 conditions, **ne crée aucun verdict scientifique** ; état courant 7/12, verrous 3, 4, 9, 10, 11 |
| Qualification stricte de `Pacc` | `plan_directeur/campagne_centrale_2026_08_11/resultats/PACC_QUALIFICATION_STRICTE.json` et `protocoles_geles/PACC_INTERVENTIONNEL_V1.md` | fail-closed ; distingue support rétrospectif, causalité de modèle et `Pacc` causal empirique |
| Contrôles d’intégrité | `CONTROLES_INTEGRITE.md` | décrit les contrôles de structure et de livraison |
| Puissance a priori | `methodologie_puissance/README.md`, le `POWER_PLAN.json` du protocole et sa sortie JSON | le plan gelé prime pour le SESOI, l’unité indépendante, les témoins et la règle de succès |
| Campagne réelle consolidée | `plateforme/campagne_maximale_reelle/BILAN_CANONIQUE.md` | prime pour les compteurs et l’interprétation de la réexécution finale |
| Campagne de recherche suivante | `MISE_A_JOUR_RECHERCHE.md` et `plan_directeur/campagne_recherche_suivante/resultats/` | prime pour H011, Pacc, vésicules, D’Onofrio et spéléothèmes |
| Campagne réelle corrigée | `plateforme/campagne_maximale_reelle/BILAN_CORRIGE.md` | autorité sur la correction La2004, le retrait du gabarit synthétique et la comparaison N-corps/La2004 ; ses compteurs précèdent les extensions exoplanètes, antibiotiques et ARN |
| Information des six dimensions | `01_branche_matiere/base_transitions/information_dimensions.json` | généré, prime sur `qualite_dimensions.json` |
| Campagne plateforme | `plan_directeur/campagne_plateforme/README.md` | généré ; **ne fixe aucun statut** |
| Politique du noyau probant | `plateforme/POLITIQUE_NOYAU_PROBANT.csv` et `plateforme/NOYAU_PROBANT.md` | organisation des cibles de preuve ; **ne fixe aucun verdict** et ne remplace ni les 683 entrées canoniques ni les critères gelés |
| Préenregistrement de la campagne | `…/campagne_plateforme/preenregistrement/catalogue_frozen.json` | gelé, autorité unique sur les critères de la campagne |
| Environnement d'exécution | `ENVIRONNEMENT.md` | généré ; informatif, n'invalide rien |

Le plan directeur **n'établit rien**. Il décrit une campagne à mener. Cocher
un de ses items ne rend aucune hypothèse valide : sur les neuf tests
climatiques exécutés au titre du WP-C1, sept concluent à une réfutation.

En cas de désaccord entre une prose et `preuves/PREUVES.json`, le registre machine tranche. `ETAT_DES_PREUVES.md` doit être régénéré depuis ce registre ; une divergence entre les deux est une erreur de CI.

## Publication stable 0.9.7-research

`PUBLICATION_STABLE.md` fixe la procédure de publication du snapshot du 12 août 2026. `RELEASE_NOTES_v0.9.7-research.md` décrit le snapshot courant mais ne prime jamais sur les sorties machine. `RELEASE_NOTES_v0.9.6-research.md` reste l’archive du snapshot antérieur. La publication doit conserver simultanément les résultats positifs et négatifs, notamment **13/15** pour la couche astronomique, **1/10** pour M2 et le contraste vésiculaire `P_acc` tel qu’il a été mesuré.

`02_branche_systeme_solaire/couche_memoire_historique/exploratoire_causalite/resultats/PCMCI_PLUS_RESULTAT.json` est une sortie exploratoire du run complet. Elle ne constitue ni un préenregistrement confirmatoire ni une correction du verdict M2.

## Fichiers retirés du paquet

| Fichier | Raison |
|---|---|
| `.claude/settings.local.json` | configuration d'outil, sans rapport avec le contenu scientifique |
| `carte_relationnelle/resultats/carte_relationnelle_oric_47` | doublon sans extension du fichier `.dot` |
| `MANIFEST_SHA256.txt`, `MANIFEST.sha256` des paquets sources | décrivaient d'autres arborescences, remplacés par le manifeste du dossier |
| caches `__pycache__` et `.pytest_cache` | artefacts d'exécution |

Les paquets d'origine conservent tous leurs fichiers. Le dossier unique ne les
modifie jamais.

## Contradiction résolue : l'analyse exhaustive passe à 11/11

Le dossier a porté un temps une contradiction entre le document principal, qui
annonçait 11 sections sur 11, et le rapport publié, qui en donnait 9. Elle est
levée, et c'est le document principal qui avait raison.

Deux défauts distincts expliquaient l'écart.

**`A01`, nécessité de `m > 0`.** La sortie publiée était antérieure au script
présent dans le dossier. Après régénération sans aucune modification de code, le
cas dégénéré `m = delta + l = 0` réussit le contrôle prévu : `P` croît sans
borne, sa pente tend vers `D·S_in`, `S` tend vers zéro. Le cas reste exclu du
domaine non dégénéré par la condition `m > 0`. C'était un défaut de publication,
pas de méthode.

**`E01`, bifurcation transcritique.** Le test du ralentissement critique
incluait le point situé à un écart relatif de `10⁻¹` du seuil dans un critère
censé vérifier une **loi asymptotique**. Ce point est hors du régime
asymptotique et provoquait un faux échec.

Le verdict porte désormais sur les quatre points les plus proches du seuil,
entre `10⁻²` et `10⁻⁵`, avec deux contrôles complémentaires : pente log-log de
`tau` en fonction de l'écart, et stabilité du produit `tau × écart`.

| Contrôle | Valeur | Attendu |
|---|---:|---|
| Pente log-log asymptotique | −1,015951 | proche de −1 |
| Rapport max/min de `tau × écart` | 1,126199 | < 1,5 |
| Échange de stabilité | confirmé | — |
| Décroissance au seuil en `1/t` | confirmée | — |

**Ce changement de critère doit rester visible.** Il est intervenu après un
échec, ce que la méthodologie du dossier interdit normalement de convertir en
réussite. Deux éléments le rendent néanmoins recevable, et il faut que le
lecteur puisse en juger : la quantité préenregistrée est inchangée — la loi
reste `tau ~ 1/|l − l_crit|` — seule la fenêtre d'ajustement est corrigée ; et
le nouveau critère est **plus strict** que l'ancien, puisqu'il ajoute une
contrainte de pente qui n'existait pas.

Le correctif a été reproduit indépendamment dans le script du dossier : la pente
et le rapport obtenus concordent à six décimales avec ceux du rapport fourni. Le
script `analyse_exhaustive.py` produit désormais 11/11 par lui-même, sans quoi
le rapport aurait été non reproductible.

Une seule ligne du rapport diffère entre les deux exécutions : l'écart maximal
du contrôle d'attractivité globale vaut `2,00 × 10⁻¹⁶` dans un cas et
`2,00 × 10⁻¹⁵` dans l'autre. C'est du bruit numérique dépendant de la version de
la bibliothèque d'algèbre linéaire, à près de neuf ordres de grandeur sous le
seuil de `10⁻⁶`. Le verdict est identique.

## Points ouverts

- Le dossier scientifique principal est livré en DOCX et en PDF.
- Le PDF de la branche 3 reste à produire.
- Les figures de la carte doivent être régénérées après ajout de `CLOS` et
  `INTG` au générateur.
- L'article de la branche 2 devra intégrer l'erratum lors de sa prochaine
  révision, après quoi l'erratum pourra être archivé.


## Inventaire et extensions

| Rôle | Fichier | Statut |
|---|---|---|
| Inventaire de lecture | `01_branche_matiere/inventaire_hierarchique/documents/INVENTAIRE_DE_LA_MATIERE_DANS_LE_CADRE_ORI-C.pdf` | document de synthèse |
| Inventaire source | `01_branche_matiere/inventaire_hierarchique/Inventaire_hierarchique_matiere_ORI-C.xlsx` | registre source |
| Analyse architecturale | `01_branche_matiere/inventaire_hierarchique/analyses/INVENTAIRE_ORI-C_ANALYSE_ARCHITECTURES.xlsx` | criblage, non canonique |
| Audit et liens candidats | `audit/coherence_et_extensions/` | programme de correction et de recherche |

## Calibrage matière v0.9.4

Le graphe canonique de la matière reste défini par `noeuds.csv`, `hyperaretes.csv` et `sources.csv` dans `01_branche_matiere/hypergraphe_transformations/`. La campagne `calibrage_v094/` ne modifie aucun de ces trois fichiers. Leur état v0.9.3 est gelé dans `protocoles_geles/v0.9.3_architecture_matiere/FROZEN.json`.

Les fichiers faisant autorité pour le calibrage sont :

- `calibrage_v094/PROTOCOLE_CALIBRAGE.md` pour les conventions et les limites ;
- `calibrage_v094/resultats/SYNTHESE_CALIBRAGE.json` pour les compteurs consolidés ;
- `calibrage_v094/resultats/calibrage_hyperaretes.csv` pour le tri relation par relation ;
- `calibrage_v094/resultats/RAPPORT_CALIBRAGE.md` pour l’interprétation scientifique ;
- `calibrage_v094/benchmark_externe_stellaire/PROVENANCE.md` pour la portée du test MESA.

Les coefficients documentaires sont des conventions de stress. Ils ne représentent ni des probabilités de vérité, ni des estimations de force causale naturelle. Une hyperarête critique sous ablation est indispensable à la représentation actuelle, ce qui reste distinct d’une nécessité empirique démontrée.

## Registre machine des preuves et chiffres

À partir du 10 août 2026, `preuves/PREUVES.json` est l'index machine des verdicts. Les cinq certifications spécialisées restent dérivées de `plateforme/campagne_maximale_reelle/RESULTATS_SCIENTIFIQUES_CERTIFIES.json` et doivent y conserver exactement verdict, niveau et portée. `ETAT_DES_PREUVES.md` est généré et ne doit plus être édité manuellement.

`preuves/CHIFFRES.json` relie les nombres publiés à leurs sorties machine. `scripts/valider_registre_preuves.py` contrôle source → registre → rendu déclaré. Une analyse exploratoire ajoutée au registre n'acquiert aucun niveau de preuve par ce seul fait.
