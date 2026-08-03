# Publication sur GitHub

## Dépôt préparé

Le dépôt conserve le code, les données légères, les protocoles, les résultats synthétiques et les documents canoniques. Les données brutes volumineuses retirées sont listées dans `EXTERNAL_DATA_MANIFEST.csv` avec leur empreinte SHA-256 et leur chemin dans le dossier scientifique complet.

## Étapes

```bash
git init
git add .
git commit -m "Initialisation du programme ORI-C"
git branch -M main
git remote add origin <URL_DU_DEPOT>
git push -u origin main
```

Installer Git LFS avant d’ajouter de nouveaux fichiers NetCDF, ZIP, GZIP, bundles ou grands jeux de données :

```bash
git lfs install
git lfs track "*.nc" "*.gz" "*.zip" "*.bundle"
```

Publier le paquet complet comme archive de version, actif de release ou dépôt de données externe, puis compléter les URL dans `DATA_AVAILABILITY.md`.
