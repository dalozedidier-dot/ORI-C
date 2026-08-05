# ORI-C - point d'entrée canonique

Ce fichier indique où trouver le contenu scientifique et les résultats contrôlables. Les numéros de publication ne définissent pas l'autorité d'un document. L'autorité dépend de sa fonction, de son niveau de preuve et de son lien avec les données ou calculs reproduisibles.

## Synthèse de lecture

- `dossier_scientifique/DOSSIER_SCIENTIFIQUE_ORI-C.pdf` : synthèse continue du programme. Ce document ne suffit pas, à lui seul, pour déterminer l’état exact des preuves.
- `dossier_scientifique/DOSSIER_SCIENTIFIQUE_ORI-C.docx` : source modifiable de la même synthèse.
- `../ORI-C_Architecture_generale_du_programme.pdf` : présentation de l’architecture générale du programme.

Pour les verdicts, les limites et les résultats reproductibles, les fichiers de la section suivante et les sorties machine lisibles priment sur cette synthèse.

## Autorité transversale

- `../AUTORITE_DES_DOCUMENTS.md` : règle de priorité entre documents.
- `../ETAT_DES_PREUVES.md` : statut scientifique des couches et résultats.
- `../ETAT_DES_TESTS.md` : état généré des tests.
- `../ARCHITECTURE.md` : articulation du socle et des trois branches.
- `../00_socle/CODEBOOK.md` : vocabulaire commun.

## Généalogie calculable

- `../00_socle/genealogie/arbre_genealogique.csv` : arbre global matière, planétaire et vivant.
- `../00_socle/genealogie/cloture_arbre.json` : résultat de clôture de l'arbre global.
- `../01_branche_matiere/genealogie/genealogie_matiere.csv` : généalogie détaillée de la matière.
- `../01_branche_matiere/genealogie/cloture_genealogie.json` : résultat de clôture de la généalogie détaillée.
- `../00_socle/genealogie/correspondance_GM_GA.csv` : correspondance entre les deux niveaux de représentation.
- `../00_socle/genealogie/REFERENCES_TRANSITIONS.csv` : registre de sourçage à compléter par références primaires.
- `../01_branche_matiere/genealogie/PROTOCOLE_INFORMATION_GENEALOGIQUE.md` : protocole exigé pour toute mesure d'information.

## Données, modèles et résultats

Chaque branche conserve ses données, ses scripts, ses critères et ses rapports dans sa propre arborescence. Les résultats générés et les fichiers machine lisibles priment sur les résumés narratifs lorsqu'ils décrivent le même calcul. Les résultats positifs, négatifs, exploratoires et non testés restent séparés.

### Campagne maximale sur les trois branches

- `../plan_directeur/campagne_maximale_trois_branches/resultats/RAPPORT_CAMPAGNE_MAXIMALE.md` : synthèse de la robustesse maximale calculable avec les données présentes.
- `../plan_directeur/campagne_maximale_trois_branches/resultats/matiere_robustesse.json` : retraits de nœuds, d'hyperarêtes, coefficients de partage et complétude des transitions.
- `../plan_directeur/campagne_maximale_trois_branches/resultats/systeme_solaire_robustesse.json` : interventions, bandes orbitales, horizon de phase, 100 ka et relaxation exoplanétaire.
- `../plan_directeur/campagne_maximale_trois_branches/resultats/vivant_robustesse.json` : validation antibiotique, permutation historique, ARN et contrôle du gabarit prébiotique.
- `../plan_directeur/campagne_maximale_trois_branches/resultats/synthese_trois_branches.json` : verdict machine transversal, sans fusion des niveaux de preuve.

## Vérification

Depuis la racine `ORI-C/` :

```bash
python verifier_dossier.py
python scripts/valider_tout.py
python plan_directeur/campagne_maximale_trois_branches/run_all.py
python 00_socle/genealogie/arbre_genealogique.py
python 01_branche_matiere/genealogie/construire_genealogie.py
```
## Calibrage de l’architecture matérielle v0.9.4

- Protocole : `01_branche_matiere/hypergraphe_transformations/calibrage_v094/PROTOCOLE_CALIBRAGE.md`
- Synthèse machine : `01_branche_matiere/hypergraphe_transformations/calibrage_v094/resultats/SYNTHESE_CALIBRAGE.json`
- Rapport : `01_branche_matiere/hypergraphe_transformations/calibrage_v094/resultats/RAPPORT_CALIBRAGE.md`
- Table complète : `01_branche_matiere/hypergraphe_transformations/calibrage_v094/resultats/calibrage_hyperaretes.csv`
- Référence gelée : `protocoles_geles/v0.9.3_architecture_matiere/FROZEN.json`

Le calibrage affine la priorité des relations. Il ne transforme pas la criticité d’une hyperarête dans le graphe en preuve causale naturelle.

## Campagne de recherche suivante

- `plan_directeur/campagne_recherche_suivante/README.md` : point d'entrée de la recherche active.
- `plan_directeur/campagne_recherche_suivante/MATRICE_TESTS.csv` : questions, données, témoins et seuils.
- `plan_directeur/campagne_recherche_suivante/resultats/SYNTHESE.json` : état machine lisible local.
- `scripts/valider_recherche_suivante.py` : contrôle des invariants de la campagne.
