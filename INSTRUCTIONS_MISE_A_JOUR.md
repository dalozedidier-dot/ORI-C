# Instructions de mise à jour

## Fichiers à supprimer avant copie

Aucun fichier à supprimer pour cette mise à jour.

## Problème corrigé

Git normalisait les fins de ligne de quatre CSV externes lors de leur ajout au dépôt. Le contenu scientifique restait lisible, mais les octets ne correspondaient plus aux empreintes SHA-256 enregistrées, ce qui faisait échouer les contrôles d’intégrité avec quatre fichiers signalés comme modifiés.

Les CSV contenus dans `donnees_externes` sont désormais déclarés `-text` dans `.gitattributes`. Git doit donc conserver exactement les octets distribués par Dryad et NOAA, fins de ligne comprises.

## Fichiers remplacés par cette correction

- `.gitattributes`
- `INSTRUCTIONS_MISE_A_JOUR.md`
- `MANIFEST.sha256`
- `MANIFEST.sha256.json`

Les quatre CSV externes et leurs données scientifiques ne sont pas modifiés.

## Installation

1. Décompresser le ZIP.
2. Copier tout le contenu du dossier `ORI-C-main` dans le dépôt en remplaçant les fichiers existants.
3. Ajouter et publier également `.gitattributes` dans le même commit que les fichiers du ZIP.
4. Relancer les workflows GitHub.

## Contrôle attendu

Après `git lfs pull`, la commande suivante ne doit plus signaler les quatre CSV comme modifiés :

```bash
python verifier_dossier.py
```

Les fichiers concernés étaient :

- `donnees_externes/histoire_antibiotique_donofrio_2026/extracted/Figure_2_C-limited_Fitness.csv`
- `donnees_externes/histoire_antibiotique_donofrio_2026/extracted/Figure_2_N-limited_Fitness.csv`
- `donnees_externes/histoire_antibiotique_donofrio_2026/extracted/Figure_3_N-lim_Expt_MIC_Raw_Data.csv`
- `donnees_externes/speleothemes_noaa_0_22ka/extracted/speleothem-d18o-0-22k.csv`
