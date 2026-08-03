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

## Vérification

Depuis la racine `ORI-C/` :

```bash
python verifier_dossier.py
python 00_socle/genealogie/arbre_genealogique.py
python 01_branche_matiere/genealogie/construire_genealogie.py
```
