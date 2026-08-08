# ORI-C — dossier unique

[![Validation](https://github.com/dalozedidier-dot/ORI-C/actions/workflows/ci.yml/badge.svg)](https://github.com/dalozedidier-dot/ORI-C/actions/workflows/ci.yml)
[![Analyses structurelles](https://github.com/dalozedidier-dot/ORI-C/actions/workflows/analyse-structure.yml/badge.svg)](https://github.com/dalozedidier-dot/ORI-C/actions/workflows/analyse-structure.yml)
[![Code MIT](https://img.shields.io/badge/code-MIT-green.svg)](LICENSE)
[![Données CC BY 4.0](https://img.shields.io/badge/données-CC%20BY%204.0-blue.svg)](LICENSING.md)

Didier Daloze | Version 0.9.4-research | 6 août 2026

**Site public de présentation scientifique :** https://dalozedidier-dot.github.io/ORI-C/

## Vérifier en deux minutes

```bash
python demo_minimale.py
```

Une commande, aucun argument, aucun accès réseau. Elle **recalcule** les trois
résultats phares depuis les données réelles du dépôt — interventions
astronomiques, antibiotiques D'Onofrio, lignées de vésicules — et compare chaque
valeur obtenue à la valeur publiée. Douze contrôles, une trentaine de secondes.

Elle affiche aussi, dans le même rapport, **ce qui ne marche pas** : le résultat
paléoclimatique négatif, la dissolution de la dépendance au chemin à 600 Ma, et
les critères dont la puissance est nulle. Un dossier qui ne montrerait que ses
succès ne serait pas vérifiable.

Installation complète, si le dépôt vient d'être cloné :

```bash
git lfs pull
python -m pip install -r plateforme/source_corrigee/requirements-lock.txt
python demo_minimale.py
```

## Licence

Code sous **MIT**, données produites par ORI-C sous **CC BY 4.0**. Les forks, la
réutilisation du code et la citation des données sont libres, avec attribution.
Deux tables dérivées portent une licence virale héritée de leur source — GEOROC
en CC BY-SA 4.0, CHNOSZ OBIGT en GPL-3 — et les textes restent sous droits
réservés. La carte complète est dans [`LICENSING.md`](LICENSING.md).

Ce dossier rassemble **l'état intégré du programme ORI-C consacré à la
chronologie des architectures matérielles, à l'architecture du Système solaire
et au vivant**, sous une forme unique : un socle commun et trois branches
autonomes.

D'autres développements d'ORI-C, notamment ses dimensions cognitives et ses
autres branches formelles, ne figurent pas ici.

Le socle ne contient aucun résultat **empirique** propre à une branche. Il
porte en revanche un résultat formel commun, le test interventionnel. Il
rassemble ce que les trois branches partagent : le vocabulaire, la
chaîne relationnelle, les règles d'emploi des liens typés, les niveaux de
preuve et la carte des transitions. Ce n'est pas une quatrième branche.

Les branches ne fusionnent pas leurs résultats. Elles ont des objets, des
méthodes et des niveaux de validation différents, et le dossier les maintient
séparés.

```text
                         SOCLE COMMUN ORI-C
       architecture, histoire, inscription, persistance, possibles
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
        BRANCHE 1            BRANCHE 2           BRANCHE 3
        MATIÈRE           SYSTÈME SOLAIRE          VIVANT
      Régimes 1 à 4        Régimes 5 et 6       Régimes 7 et 8
              │                   │                   │
              └── héritage ──────►│── conditions ────►│
                                  │◄── rétroactions ──┘
```


## Résultats établis dans l’état courant du dépôt

ORI-C montre que **l’architecture d’un système modifie les trajectoires qui lui restent accessibles**. Dans la couche astronomique réduite, les interventions sur Jupiter et Saturne produisent des effets au moins 4 964 fois supérieurs aux écarts numériques sélectionnés, et 13 critères préenregistrés sur 15 sont réussis.

Le dépôt contient aussi deux résultats positifs sur données biologiques réelles. Dans le jeu D’Onofrio, l’histoire améliore la prédiction de la résistance antibiotique : la RMSE passe de 1,1309 pour l’état seul à 0,8042 avec l’histoire, et le modèle historique bat également le témoin d’histoire permutée de même complexité, avec p = 0,00498. Dans les expériences de vésicules, 11 760 couples parent-descendant sont analysés et les quatre composantes préenregistrées sont soutenues : réponse à la sélection, contraste d’ablation, signal de filiation supérieur au témoin permuté et codage complet des lignées.

La branche matière mesure une structure cumulative de 53 nœuds, une fermeture stricte de 46 nœuds, 34 hyperarêtes critiques pour cette fermeture et 40 relations ayant un effet mesurable sur au moins une métrique. Le test H011 établit en simulation un seuil critique qui augmente avec la turbulence, avec un rapport extrême de 3,33.

La couche mémoire distingue désormais une dépendance au chemin d’une mémoire persistante : sous un même forçage final prolongé, les écarts exoplanétaires se relaxent avec un temps caractéristique de 7,02 Ma. Une différence historique qui disparaît ainsi correspond à un retard de relaxation, pas à une inscription durable.

Les résultats négatifs restent attachés à leurs protocoles précis. L’échec de M2 concerne cette formulation paléoclimatique. Le résultat non concluant sur l’amikacine, le résultat négatif Card 2019 et l’absence de filiation dans les seules données ARN ne décrivent ni toute la branche vivant ni les résultats D’Onofrio et vésicules obtenus ensuite.

La campagne générique des 683 entrées, réauditée le 7 août 2026 avec le pare-feu empirique `fail_closed_v2`, produit **9 réussites techniques, 626 blocages, 48 protocoles non exécutables informatiquement, 0 échec et 0 erreur**. Elle produit **0 verdict scientifique `supports`**. Ce compteur décrit uniquement la plateforme d’intégration et ne remplace ni les verdicts ciblés sur données réelles ni les résultats explicitement issus de modèles.

Le résumé détaillé et actualisé se trouve dans [`AVANCEES_ET_DECOUVERTES_2026-08-06.md`](AVANCEES_ET_DECOUVERTES_2026-08-06.md).

### Atteignabilité des critères — à lire avant tout résultat négatif

Un critère peut échouer parce que l’effet n’existe pas, ou parce que le test ne peut pas le détecter. [`ATTEIGNABILITE_DES_CRITERES_2026-08-08.md`](ATTEIGNABILITE_DES_CRITERES_2026-08-08.md) sépare les deux cas pour l’ensemble du dossier.

Sur 23 critères discrets audités, 20 sont atteignables et 3 — des bootstraps — ne sont pas évaluables par cette voie, un bootstrap n’ayant pas de plancher de p général contrairement à une permutation. Un seul critère est écarté pour inatteignabilité :

- la **vallée des rayons**, dont le seuil n’est franchi à aucune taille disponible : la profondeur du creux mesurée est négative, il n’y a pas de creux à mesurer.

> **Correction du 8 août 2026.** Cette section citait « les deux tests de signe du benchmark antibiotique longitudinal, qui exigent 9 plis favorables sur 10 ». C’était faux : le benchmark emploie un test de **sign-flip**, qui prend les magnitudes en compte et n’exige aucun nombre minimal d’unités favorables. Ces deux critères sont atteignables. L’auditeur les modélisait par le mauvais test.

### Ce que vaut un témoin — hiérarchie à six niveaux

Un verdict exige deux choses, et la force du témoin n’en est qu’une. La hiérarchie va du mélange simple (1) à la réplication sur données indépendantes (6), avec **IAAFT au niveau 4 comme minimum exigé pour tout critère temporel**. Le second axe est l’adéquation de la statistique : un témoin de niveau 6 sur une statistique qui ne teste pas l’hypothèse ne produit rien.

Le dossier a payé cette règle deux fois le même jour. `WP-CLIM-MEM-2026` avait un témoin de niveau 1, une permutation qui ramenait l’autocorrélation de +0,450 à +0,013. Son successeur `WP-CLIM-MEM-2026-B` avait un témoin correct et une statistique asymétrique : rejouée sur l’**obliquité terrestre**, une oscillation à 41 ka calculée par mécanique céleste qui n’inscrit rien, elle accordait `soutient` avec un gain de 77,3 % — supérieur à celui de la cible glaciaire. Les deux protocoles sont clos sur `invalide`. Le contrôle qui les a rétractés n’utilise aucune donnée synthétique : il substitue la cible par d’autres colonnes réelles de la même table. Il tourne en CI, dans [`scripts/controle_negatif_reel_surrogats.py`](scripts/controle_negatif_reel_surrogats.py).

### Campagne « mémoire matérielle réelle » — protocole gelé, sources non encore inspectées

[`01_branche_matiere/memoire_materielle_reelle/`](01_branche_matiere/memoire_materielle_reelle/) porte `WP-MAT-MEM-2026`, cinq critères scellés le 8 août 2026 **avant inspection du moindre jeu de données**.

L’intérêt de cette campagne est qu’elle vise le **niveau 6**, hors de portée de toute campagne à surrogats. Démagnétiser un échantillon ou recuire un acier écroui sont des ablations physiques, pas des permutations : le témoin est un autre échantillon réel ayant subi un traitement réel. Un seul schéma relationnel est testé sur des familles physiques sans rapport entre elles :

> histoire appliquée → trace physique persistante mesurée → réponse ultérieure modifiée sous stimulus identique

| famille | histoire | trace | réponse |
|---|---|---|---|
| magnétisme | champ et cycles antérieurs | rémanence, coercivité | boucle B-H suivante, pertes |
| plasticité | déformation antérieure | dislocations, écrouissage | courbe σ-ε, ratcheting |
| verre | recuit sous `Tg` | enthalpie résiduelle | cinétique de relaxation |
| transition de phase | traitement thermique | fractions de phase | transformation ultérieure |

**Aucun jeu n’a encore été inspecté.** Le registre des candidats liste des pistes, pas des sources vérifiées, et le filtre d’admission tourne à vide tant qu’aucune fiche n’est renseignée depuis la source elle-même. Un jeu offrant moins de six paires indépendantes ne peut produire aucun verdict positif à alpha = 0,05, et ce constat se fait à l’admission.

### Premier test prospectif préenregistré

[`02_branche_systeme_solaire/tests_suivants/preenregistrement_exoplanetes_2026_08_07/`](02_branche_systeme_solaire/tests_suivants/preenregistrement_exoplanetes_2026_08_07/) porte `WP-EXO-PACC-2026`, gelé le 7 août 2026 et vérifiable le 7 août 2028. Hypothèse, seuil, témoin, instantané de référence et code d’analyse sont scellés par empreinte SHA-256 avant que les données à tester n’existent. C’est le premier protocole du dossier dont la conclusion ne peut pas être ajustée après lecture.

Un second protocole, sur les éléments sidérophiles de GEOROC, a été **écarté après mesure** : la compilation ne gagne qu’environ six couples Os+Ir par an, ce qui repousserait toute conclusion à cinq ans. Le raisonnement est conservé dans [`protocoles_geles/GEOROC_HSE_PROSPECTIF_ECARTE.md`](protocoles_geles/GEOROC_HSE_PROSPECTIF_ECARTE.md).

## Contenu

| Dossier | Contenu | Rôle |
|---|---|---|
| `00_socle/` | vocabulaire, carte des 40 transitions et 47 relations, test interventionnel, suite de tests | langage transversal |
| `01_branche_matiere/` | Chronologie des architectures de la matière, hypergraphe mécanistique de 53 nœuds, campagne d'inventaire accessible | régimes 1 à 4 |
| `02_branche_systeme_solaire/` | article, couche astronomique N-corps, couche mémoire historique, application climatique séparée | régimes 5 et 6 |
| `plan_directeur/` | plan de campagne, registre des 35 hypothèses, avancement | transversal |
| `methodologie_puissance/` | plans de puissance et analyses de sensibilité méthodologiques ; aucune sortie de ce dossier ne constitue une preuve empirique | transversal |
| `03_branche_vivant/` | Le vivant comme terrain ORI-C | régimes 7 et 8 |

## Par où commencer

0. `documentation/dossier_scientifique/DOSSIER_SCIENTIFIQUE_ORI-C.pdf` — document de synthèse pour une lecture continue. Il ne suffit pas, à lui seul, pour déterminer l’état exact des preuves. Les fichiers `ETAT_DES_PREUVES.md`, `ETAT_DES_TESTS.md`, `SCIENTIFIC_SCOPE.md` et les résultats machine lisibles font autorité pour les verdicts.
1. `documentation/POINT_D_ENTREE.md` — la carte des documents faisant autorité et des fichiers machine lisibles.
2. `ORI-C_Architecture_generale_du_programme.pdf` — l'architecture générale du programme.
3. `ARCHITECTURE.md` — ce qui relie les branches, ce qui les sépare, et pourquoi le socle n'en est pas une.
4. `ETAT_DES_PREUVES.md` — le tableau transversal des niveaux de validation, y compris les résultats négatifs.
5. `00_socle/CODEBOOK.md` — les définitions communes, à lire avant toute branche.
6. `AUTORITE_DES_DOCUMENTS.md` — le fichier qui tranche lorsque deux documents se contredisent.
7. `ETAT_DES_TESTS.md` — les compteurs de tests générés.
8. `plan_directeur/campagne_maximale_trois_branches/resultats/RAPPORT_CAMPAGNE_MAXIMALE.md` — la campagne de robustesse maximale disponible avec les données du dépôt.
   Pour les 683 entrées en données réelles, le résultat machine courant est `plateforme/campagne_maximale_reelle/resultats_integration_maximale/results.json`. Le dossier `resultats_consolides/` est conservé comme état historique.
9. `plan_directeur/campagne_priorites_v093/resultats/RAPPORT_PRIORITES_V093.md` — les travaux ciblés sur les verrous matière, climat, mémoire et vivant.
10. `01_branche_matiere/hypergraphe_transformations/calibrage_v094/resultats/RAPPORT_CALIBRAGE.md` — le tri documentaire et structurel des 53 relations matérielles.

## Ce que le dossier établit, en une phrase par branche

**Branche 1, matière.** L’hypergraphe relie 53 nœuds, en atteint 46 en fermeture stricte et localise un noyau cyclique précis. Trente-quatre hyperarêtes sont critiques pour la fermeture, quarante modifient au moins une métrique et l’échelle des capacités porte 0,595 bit d’information nette. H011 fournit un seuil quantitatif dont le rapport extrême vaut 3,33 sous variation de la turbulence.

**Branche 2, Système solaire.** La couche dynamique réduite réussit 13 critères préenregistrés sur 15. Les interventions sur Jupiter et Saturne produisent des effets au moins 4 964 fois supérieurs aux écarts numériques sélectionnés. Le test de relaxation à 600 Ma distingue une dépendance temporaire au chemin d’une mémoire persistante, avec un temps caractéristique de 7,02 Ma.

**Branche 3, vivant.** Deux résultats positifs sont distingués des anciens tests. Le jeu D’Onofrio montre un gain prédictif de l’histoire contre l’état seul et contre une histoire permutée de même complexité, avec p = 0,00498. Les vésicules fournissent 11 760 couples parent-descendant et soutiennent les quatre composantes préenregistrées de sélection, filiation et ablation. Le benchmark intégré sur l’amikacine, le jeu Card 2019 et les trajectoires ARN restent des protocoles séparés et ne peuvent pas être généralisés à toute la branche.


## Nouveaux travaux v0.9.3

- **Matière.** Le noyau du verrou 46/53 est isolé sur `N029`, `N030`, `N053` et `N054`. Une réparation candidate ferme 53/53, mais reste hors graphe canonique car la littérature disponible ne démontre pas l'hyperarête exacte proposée.
- **Transfert climatique.** Le signal d'excentricité N-corps est injecté dans un modèle intermédiaire. Il améliore la RMSE dans trois fenêtres temporelles sur trois, de 3,12 % en moyenne, mais il s'agit d'une prédiction à un pas utilisant l'état climatique observé. Ce test ne remplace ni Terre-Lune complet, ni marées, ni GCM.
- **Mémoire.** M2 et son témoin apparié M2P possèdent chacun deux bassins dans les régimes testés. Des boucles d'hystérèse apparaissent à 30 degrés, mais aucun état matériellement différent ne subsiste après le retour complet au faible forçage.
- **Vivant.** Le jeu Card 2019 fournit une réplication externe temporelle. Le modèle état + histoire est moins bon dans chacun des quatre groupes de test et le bootstrap groupé conserve un écart défavorable. Le protocole prospectif suivant est gelé avant acquisition du prochain jeu.
- **Prébiotique.** Deux trajectoires expérimentales de populations d'ARN catalytique sur huit cycles sont intégrées. Elles ne contiennent aucune filiation parent-descendant de compartiments, donc la continuité héréditaire reste non testable.

## Nouveaux travaux v0.9.4

- **Graphe gelé.** Les fichiers canoniques v0.9.3 sont scellés par empreinte. Le calibrage ne modifie ni les 53 nœuds ni les 53 hyperarêtes.
- **Tri documentaire et structurel.** Les statuts de preuve et les types de source sont séparés des effets d’ablation, des voies alternatives, des cycles et de la portée en aval. Aucun score causal unique n’est déclaré.
- **Stabilité.** Sous stress limité aux six relations dont le plancher documentaire est inférieur à 0,65, 31 nœuds restent dans le noyau stable, 15 deviennent sensibles et les 7 nœuds du verrou hydrothermal restent classés séparément.
- **Priorité.** `H011`, l’instabilité de streaming, est la relation documentaire la plus urgente hors du verrou des interfaces, car elle contrôle un ensemble important de nœuds planétaires.
- **Transfert externe.** Le même schéma de relations, seuils et fermeture stricte représente deux trajectoires MESA indépendantes, une étoile de 1 masse solaire vers une naine blanche et une étoile de 12 masses solaires vers l’effondrement du cœur. Le test valide la portabilité de la représentation, pas une loi universelle ORI-C.

## Portée du résultat négatif de la branche 2

Il ferme une implémentation particulière de la mémoire climatique. Il ne remet
pas en cause la couche astronomique, qui est validée séparément et dont les
résultats sont conservés dans un dossier distinct. Il ne réfute pas les deux
autres branches, qui portent sur d'autres objets et d'autres mécanismes.

Cette séparation est le motif principal de l'organisation du dossier : un
échec localisé doit rester localisé, et une réussite localisée ne doit pas
s'étendre par contagion de vocabulaire.

## Vérification

Après un clonage Git complet :

```bash
cd ORI-C
git lfs pull
python verifier_dossier.py
python scripts/valider_tout.py --strict-lfs
python plan_directeur/campagne_maximale_trois_branches/run_all.py
python plan_directeur/campagne_priorites_v093/run_all.py
python 01_branche_matiere/hypergraphe_transformations/calibrage_v094/calibrage_relations.py
```

Dans un ZIP source automatique de GitHub, les objets volumineux peuvent rester
sous forme de pointeurs. Le contrôle suivant vérifie alors l'arbre source sans
le déclarer autonome :

```bash
python verifier_dossier.py --allow-lfs-pointers
python scripts/valider_tout.py
```

Le vérificateur distingue les fichiers réellement modifiés des objets Git LFS
non hydratés. Une archive canonique doit afficher zéro objet LFS non hydraté.
Sa construction est automatisée par
`python scripts/construire_archive_canonique.py`.

## Reconstruction et contrôles

Les scripts de construction conservés à la racine reconstruisent les composants historiques et les campagnes dont ils dépendent. L'archive complète livrée, son manifeste et ses fichiers de clôture constituent l'état canonique à contrôler. La généalogie dispose de ses propres scripts de validation dans `00_socle/genealogie/` et `01_branche_matiere/genealogie/`.

Deux suites de tests s'exécutent séparément :

```bash
cd 00_socle && python -m pytest -q
cd 02_branche_systeme_solaire/couche_memoire_historique
PYTHONPATH="$PWD/src" python -m unittest discover -s tests
```

Les compteurs courants sont générés par `etat_des_tests.py` et consignés
dans `ETAT_DES_TESTS.md`. Certains instantanés historiques conservent les
nombres de leur exécution, mais ils sont clairement marqués et ne font pas
autorité.

La reconstruction se vérifie sans rien écraser :

```bash
python construire_dossier.py --sources <rep> --verifier-reconstruction
```

## Livraison, licence et citation

- `DATA_AVAILABILITY.md` distingue le dépôt Git, le ZIP source GitHub et
  l'archive canonique hydratée.
- `LICENSE` fixe définitivement le régime général « tous droits réservés » pour cette version.
- `CITATION.cff` contient le dépôt réel et la version courante.
- `documentation/ALIASES_DOCUMENTAIRES.md` identifie le dossier scientifique
  canonique et ses copies de livraison.

## État du dossier

Cette archive constitue un dossier scientifique unique. Le socle, les trois branches, les généalogies, les données, le code, les résultats positifs, les résultats négatifs et les limites sont conservés dans une même arborescence. Les identifiants de transition restent stables parce qu’ils décrivent le contenu, et non une étape de publication.


## Inventaire complet et recherche d’architectures

- `01_branche_matiere/inventaire_hierarchique/documents/INVENTAIRE_DE_LA_MATIERE_DANS_LE_CADRE_ORI-C.pdf` : document de lecture.
- `01_branche_matiere/inventaire_hierarchique/analyses/INVENTAIRE_ORI-C_ANALYSE_ARCHITECTURES.xlsx` : criblage des familles et relations.
- `audit/coherence_et_extensions/` : anomalies, architectures manquantes et liens causaux candidats.
- `TRI_ET_CORRECTIONS.md` : corrections appliquées lors de la reconstruction.

## Recherche suivante exécutée

La campagne `plan_directeur/campagne_recherche_suivante/` est intégrée et reproductible hors ligne. Elle produit notamment :

- le seuil H011, monotone avec la turbulence dans les simulations publiées ;
- une mesure interventionnelle de `Pacc` sur six interventions astronomiques ;
- 11 760 couples parent-descendant dans les lignées de vésicules, avec quatre composantes préenregistrées soutenues ;
- un gain prédictif de l’histoire dans le jeu antibiotique D’Onofrio contre l’état seul et l’histoire permutée ;
- un audit de 27 721 couples âge-isotope dans les spéléothèmes NOAA ;
- le protocole `WP-C2b` gelé avec points non saturés et graines réservées.

Exécution complète :

```bash
python plan_directeur/campagne_recherche_suivante/run_all.py
python scripts/valider_recherche_suivante.py
```
