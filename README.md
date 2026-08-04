# ORI-C — dossier unique

Didier Daloze | Version 0.9.0-research | 4 août 2026

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
| `plan_directeur/` | plan de campagne, registre des 28 hypothèses, avancement | transversal |
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

## Ce que le dossier établit, en une phrase par branche

**Branche 1, matière.** Une chronologie descriptive en huit régimes, un
inventaire de 40 transitions et une grille d'analyse. L'hypergraphe de 53
nœuds possède une projection connectée, mais sa fermeture stricte n'atteint
que 46 nœuds sur 53. Un noyau cyclique de quatre nœuds bloque trois nœuds
supplémentaires. Sur cet ensemble accessible, 34 hyperarêtes sont critiques
pour la joignabilité. Le contrôle métal-silicate est robuste pour le
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
- `LICENSE` fixe un statut conservatoire tous droits réservés tant qu'une
  politique ouverte n'a pas été choisie explicitement par l'auteur.
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
