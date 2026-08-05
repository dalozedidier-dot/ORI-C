# Données externes de la recherche active

Ce dossier contient les jeux tiers nécessaires aux tests de la campagne active. Ils restent identifiés comme données externes et chaque jeu possède un fichier `SOURCE.json` avec DOI, provenance, taille et empreintes SHA-256.

## Jeux intégrés

- Dryad `10.5061/dryad.fbg79cp99` : 12 classeurs de lignées expérimentales de vésicules.
- Dryad `10.5061/dryad.1zcrjdg68` : 3 CSV utilisés pour le test de l'effet de l'histoire évolutive sur la sensibilité antibiotique.
- NOAA/NCEI `10.25921/edce-mr22` : compilation de spéléothèmes 0-22 ka.

Les jeux Dryad sont publiés sous CC0. Les citations scientifiques et les DOI restent obligatoires dans les productions ORI-C. Le fichier NOAA conserve son préambule complet avec les références originales à citer.

## Contrôle local

```bash
python plan_directeur/campagne_recherche_suivante/fetch_external_data.py --offline
```

Cette commande vérifie la présence et le format réel de tous les fichiers attendus sans effectuer d'appel réseau.

## Rafraîchissement volontaire

```bash
python plan_directeur/campagne_recherche_suivante/fetch_external_data.py --force
```

Le rafraîchissement distant est facultatif. En CI, les données intégrées sont contrôlées en mode hors ligne par défaut afin qu'un refus HTTP du fournisseur ne bloque plus l'analyse reproductible.

La compilation NOAA couvre 0-22 ka. Elle sert à l'audit de chronologie et de proxy, pas à valider seule la bande orbitale de 100 ka.
