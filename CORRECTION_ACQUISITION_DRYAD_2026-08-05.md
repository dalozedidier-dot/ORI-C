# Correction de l'acquisition Dryad, 5 août 2026

## Problèmes identifiés

Deux problèmes distincts étaient présents.

1. Les liens individuels Dryad étaient enregistrés comme identifiants fixes. Une nouvelle version du dépôt ou une redirection vers une URL de stockage signée pouvait rendre ces liens fragiles et produire un HTTP 403.
2. Le fichier temporaire `fix_dryad_403.patch` avait été ajouté à la racine du dépôt sans être inscrit au manifeste. Les contrôles portables Python 3.12 et 3.13 échouaient donc avant les suites scientifiques avec un contenu non listé.

Le fichier patch a été supprimé. La correction est intégrée au code source et au manifeste du dossier complet.

## Nouvelle stratégie

Le client `plan_directeur/campagne_recherche_suivante/fetch_external_data.py` applique désormais la séquence suivante pour chaque jeu Dryad.

1. Résoudre la version publique courante à partir du DOI via l'API Dryad.
2. Résoudre les identifiants actuels des fichiers attendus par leur nom.
3. Télécharger chaque fichier en conservant exactement le chemin des redirections vers les URL signées.
4. Valider le contenu réel avant utilisation. Un classeur XLSX doit posséder sa structure interne, un CSV doit avoir un en-tête tabulaire, une page HTML ou XML déguisée en fichier de données est refusée.
5. Si les fichiers individuels échouent, télécharger l'archive complète du jeu et en extraire uniquement les fichiers attendus.
6. Effectuer l'acquisition dans une zone temporaire. Le cache actif n'est remplacé qu'après validation complète.
7. Si un rafraîchissement échoue mais qu'un cache complet antérieur est valide, conserver ce cache et inscrire l'avertissement dans le rapport.

Les identifiants individuels conservés dans `sources_externes.json` ne servent plus que de repli lorsque la résolution par API est indisponible.

## Sécurité et traçabilité

- protection contre les traversées de chemin dans les archives ZIP ;
- refus des liens symboliques contenus dans les archives ;
- écriture atomique de `SOURCE.json` et `ACQUISITION_REPORT.json` ;
- empreinte SHA-256 de chaque fichier et du jeu combiné ;
- conservation de l'URL demandée, de l'URL finale, des redirections, du statut HTTP, du type de contenu, de l'ETag et de la date de modification lorsqu'ils sont disponibles ;
- distinction entre téléchargement, rafraîchissement, cache local et cache conservé après échec du réseau.

## Tests ajoutés

Six tests couvrent directement la correction.

- conservation exacte d'un chemin signé après redirection ;
- refus d'une traversée de chemin dans une archive ZIP ;
- refus d'une page HTML présentée comme fichier XLSX ;
- repli automatique des fichiers individuels vers l'archive complète ;
- conservation d'un cache complet lorsque le rafraîchissement échoue ;
- résolution des identifiants actuels depuis la version Dryad la plus récente.

La campagne de recherche suivante compte désormais 19 tests réussis dans l'environnement de reconstruction locale, dont ces six tests d'acquisition.
