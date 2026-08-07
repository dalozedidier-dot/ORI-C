# Application de la mise à jour ORI-C du 7 août 2026

Ce paquet ne remplace pas le dépôt entier. Il applique uniquement les données, le code, les politiques, les audits et les corrections nécessaires au pare-feu empirique `fail_closed_v2`.

## Avant d'écrire

```bash
python APPLIQUER_MISE_A_JOUR.py --repo "C:\chemin\vers\ORI-C" --check
```

## Application avec validation complète

```bash
python APPLIQUER_MISE_A_JOUR.py --repo "C:\chemin\vers\ORI-C" --full-validation
```

L'installateur :

1. vérifie le SHA-256 de chaque fichier du payload ;
2. vérifie les blobs Git critiques de la base avant modification ;
3. crée une sauvegarde hors du dépôt ;
4. copie les ressources sélectionnées et corrige les documents publics sans écraser leurs autres évolutions ;
5. exécute l'audit réel et les tests du pare-feu ;
6. reconstruit ensuite `MANIFEST.sha256` **et** `MANIFEST.sha256.json` ;
7. vérifie les manifestes, le dossier, la barrière empirique et la publication ;
8. en mode `--full-validation`, réexécute aussi les 683 entrées dans un dossier temporaire et exige exactement `9 pass / 626 blocked / 48 not_run / 0 fail / 0 error`, avec `0 supports`.

En cas d'échec, les fichiers sont restaurés automatiquement depuis la sauvegarde.

`planetary_histories.csv` n'est volontairement pas créé. Les données thermochimiques et volatiles incomplètes ne sont pas promues en preuves empiriques.
