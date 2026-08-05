# Données externes de la recherche active

Ce dossier reçoit les jeux tiers nécessaires aux nouveaux tests. Les fichiers bruts ne sont pas assimilés aux productions d'ORI-C et ne sont pas intégrés à l'archive source.

## Acquisition

```bash
python plan_directeur/campagne_recherche_suivante/fetch_external_data.py
```

Le script résout chaque source depuis son dépôt public, télécharge dans une zone temporaire, valide le format réel des fichiers, calcule les empreintes SHA-256 et écrit un fichier `SOURCE.json`. Pour Dryad, les identifiants courants sont résolus depuis le DOI et l'archive complète sert de repli lorsque les fichiers individuels sont indisponibles. Le cache actif n'est remplacé qu'après validation complète. Le registre canonique des sources est :

```text
plan_directeur/campagne_recherche_suivante/sources_externes.json
```

## Jeux enregistrés

- Dryad `10.5061/dryad.fbg79cp99` : lignées expérimentales de populations de vésicules, cartes donneur-receveur et régimes d'ablation.
- Dryad `10.5061/dryad.1zcrjdg68` : données de sensibilité antibiotique associées à l'histoire évolutive.
- NOAA `10.25921/edce-mr22` : compilation de spéléothèmes 0-22 ka pour audit indépendant de chronologie et de proxy.

La compilation NOAA ne couvre pas une période de 100 ka. Elle ne peut donc pas être utilisée seule pour valider la bande de 100 ka.

## Contrôle du cache

```bash
python plan_directeur/campagne_recherche_suivante/fetch_external_data.py --offline
```

Le rapport `ACQUISITION_REPORT.json` distingue un téléchargement réussi, un cache valide, un cache conservé après échec de rafraîchissement et une absence réelle de données utilisables.
