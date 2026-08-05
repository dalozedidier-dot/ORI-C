# ORI-C — dossier unique

Didier Daloze | Version 0.9.4-research | 4 août 2026

**Site public de présentation scientifique :** https://dalozedidier-dot.github.io/ORI-C/

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

## Contenu

| Dossier | Contenu | Rôle |
|---|---|---|
| `00_socle/` | vocabulaire, carte des 40 transitions et 47 relations, test interventionnel, suite de tests | langage transversal |
| `01_branche_matiere/` | Chronologie des architectures de la matière, hypergraphe mécanistique de 53 nœuds, campagne d'inventaire accessible | régimes 1 à 4 |
| `02_branche_systeme_solaire/` | article, couche astronomique N-corps, couche mémoire historique, application climatique séparée | régimes 5 et 6 |
| `plan_directeur/` | plan de campagne, registre des 35 hypothèses, avancement | transversal |
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
9. `plan_directeur/campagne_priorites_v093/resultats/RAPPORT_PRIORITES_V093.md` — les travaux ciblés sur les verrous matière, climat, mémoire et vivant.
10. `01_branche_matiere/hypergraphe_transformations/calibrage_v094/resultats/RAPPORT_CALIBRAGE.md` — le tri documentaire et structurel des 53 relations matérielles.

## Ce que le dossier établit, en une phrase par branche

**Branche 1, matière.** Une chronologie descriptive en huit régimes, un
inventaire de 40 transitions et une grille d'analyse. L'hypergraphe de 53
nœuds possède une projection connectée, mais sa fermeture stricte n'atteint
que 46 nœuds sur 53. Un noyau cyclique de quatre nœuds bloque trois nœuds
supplémentaires. Le calibrage v0.9.4 distingue 31 nœuds stables, 15 nœuds sensibles aux six relations les moins documentées et 7 nœuds bloqués par le verrou canonique. Quarante hyperarêtes produisent une perte mesurable lors d’une ablation de projection ou de fermeture stricte. Le contrôle métal-silicate est robuste pour le
carbone, fragile pour l'azote, non évaluable en retrait unitaire pour
l'hydrogène et durablement en désaccord pour le soufre. L'échelle des dix
capacités porte 0,595 bit net de permutation, tandis que sa monotonie est
réfutée.

**Branche 2, Système solaire.** La couche dynamique réduite réussit 13 critères
préenregistrés sur 15. Les effets des interventions restent au minimum 4 964 fois plus
grands que les écarts numériques sélectionnés. La couche paléoclimatique reste
négative face au témoin apparié et le verrou est localisé dans la bande de 100
ka, sans mécanisme identifié.

**Branche 3, vivant.** La grille reste une preuve de concept. Sur l'amikacine,
un léger gain historique apparaît en validation groupée, mais il disparaît à
l'ablation de la pente et s'inverse sur la dernière transition. Les données ARN
montrent une dynamique de composition, pas une hérédité. Universalité,
supériorité explicative et pouvoir prédictif restent non établis.


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

## Recherche active suivante

Le dossier contient maintenant une campagne consacrée aux verrous qui ne peuvent plus être franchis par de simples variantes sur les mêmes données.

```text
plan_directeur/campagne_recherche_suivante/
```

Elle ajoute :

- un test à seuil de `H011` sous intervention sur la turbulence ;
- un audit de fermeture empirique du cycle `H030-H031-H052-H053` ;
- une mesure interventionnelle de `Pacc` dans la couche astronomique ;
- le protocole gelé `WP-C2b`, réparé par calibration selon le régime ;
- une acquisition automatisée de données externes pour des lignées de vésicules, un benchmark antibiotique et un audit de spéléothèmes ;
- des témoins de complexité égale, des permutations de l'histoire et des tests de filiation parent-descendant.

Exécution sans données tierces :

```bash
python plan_directeur/campagne_recherche_suivante/run_all.py
python scripts/valider_recherche_suivante.py
```

Exécution complète avec acquisition des sources :

```bash
python plan_directeur/campagne_recherche_suivante/fetch_external_data.py
python plan_directeur/campagne_recherche_suivante/run_all.py
```
