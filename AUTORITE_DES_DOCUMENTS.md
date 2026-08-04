# Autorité des documents

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
4. En dernier ressort, `ETAT_DES_PREUVES.md` fixe le statut de chaque couche.

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
2. **Sur les cinq notions transversales qui en ont été extraites — mémoire
   distribuée, diagnostic `D-H-L`, `Pth`/`Pacc`, séparation `X`/`m`/`A`,
   critère d'altération architecturale — c'est le `CODEBOOK.md` §13 qui fait
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
| Registre des hypothèses | `plan_directeur/REGISTRE_HYPOTHESES.csv` | généré, prime sur tout statut cité ailleurs sauf `ETAT_DES_PREUVES.md` |
| Avancement | `plan_directeur/AVANCEMENT_DU_PLAN.md` | généré ; descriptif, ne fixe aucun statut |
| Grille de l'Étape 2 | `plan_directeur/GRILLE_ETAPE_2.md` | généré ; audit, ne fixe aucun statut |
| Audit transversal | `plan_directeur/AUDIT_TRANSVERSAL.md` | généré, prime ; **exploratoire** |
| Contrôles d’intégrité | `CONTROLES_INTEGRITE.md` | décrit les contrôles de structure et de livraison |
| Campagne réelle consolidée | `plateforme/campagne_maximale_reelle/BILAN_CANONIQUE.md` | prime pour les compteurs et l’interprétation de la réexécution finale |
| Campagne réelle corrigée | `plateforme/campagne_maximale_reelle/BILAN_CORRIGE.md` | autorité sur la correction La2004, le retrait du gabarit synthétique et la comparaison N-corps/La2004 ; ses compteurs précèdent les extensions exoplanètes, antibiotiques et ARN |
| Information des six dimensions | `01_branche_matiere/base_transitions/information_dimensions.json` | généré, prime sur `qualite_dimensions.json` |
| Campagne plateforme | `plan_directeur/campagne_plateforme/README.md` | généré ; **ne fixe aucun statut** |
| Préenregistrement de la campagne | `…/campagne_plateforme/preenregistrement/catalogue_frozen.json` | gelé, autorité unique sur les critères de la campagne |
| Environnement d'exécution | `ENVIRONNEMENT.md` | généré ; informatif, n'invalide rien |

Le plan directeur **n'établit rien**. Il décrit une campagne à mener. Cocher
un de ses items ne rend aucune hypothèse valide : sur les neuf tests
climatiques exécutés au titre du WP-C1, sept concluent à une réfutation.

En cas de désaccord entre le registre et `ETAT_DES_PREUVES.md`, c'est ce
dernier qui tranche, conformément à la règle générale.

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
