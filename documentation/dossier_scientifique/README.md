# Dossier scientifique ORI-C

Ce dossier regroupe :

- `DOSSIER_SCIENTIFIQUE_ORI-C.docx` : version modifiable
- `DOSSIER_SCIENTIFIQUE_ORI-C.pdf` : version de lecture
- `annexes/` : tables et fichiers machine lisibles
- `assets/` : figures intégrées au document

Le dossier rassemble le socle, les branches, les résultats, les données et la généalogie intégrée. Les résultats probants, exploratoires, négatifs et non testés restent explicitement distingués.

## Régénération

Depuis le dossier `documentation/dossier_scientifique/` :

```bash
python generer_dossier_scientifique.py
```

Le script produit le DOCX et régénère les figures et annexes. La conversion en PDF utilise ensuite le moteur de rendu documentaire disponible dans l'environnement de publication.
