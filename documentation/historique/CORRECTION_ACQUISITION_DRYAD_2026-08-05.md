# Correction de l'acquisition Dryad, 5 août 2026

## Erreur réellement observée

Les journaux GitHub `84149852086` montrent que les analyses ORI-C s'exécutent sans erreur interne, mais que deux jeux Dryad restent indisponibles :

- HTTP 403 sur les liens publics `/downloads/file_stream/...` depuis le runner GitHub ;
- HTTP 401 sur les routes de téléchargement de l'API Dryad sans jeton Bearer ;
- aucun cache valide n'était encore disponible pour ces deux jeux.

Le jeu NOAA est téléchargé correctement. Le blocage ne vient donc ni du client général, ni des tests scientifiques, ni du format des données.

## Correction intégrée

Le client d'acquisition applique désormais trois voies clairement séparées :

1. téléchargement par l'API Dryad authentifiée lorsqu'un jeton est disponible ;
2. téléchargement public pour les environnements où Dryad l'autorise encore ;
3. conservation et réutilisation d'un cache précédemment validé.

Les identifiants courants des fichiers sont toujours résolus depuis le DOI. Les en-têtes d'authentification sont retirés avant toute redirection vers un autre domaine afin de ne jamais transmettre le jeton au stockage objet.

Les variables reconnues sont :

- `DRYAD_API_TOKEN` ;
- ou `DRYAD_API_CLIENT_ID` avec `DRYAD_API_CLIENT_SECRET`.

## Comportement du workflow

Le workflow `recherche-suivante.yml` ne confond plus une panne ou un refus du fournisseur externe avec une erreur du programme ORI-C.

Par défaut :

- l'acquisition est tentée ;
- le rapport HTTP complet est conservé ;
- les analyses dépendantes restent explicitement en attente si les données manquent ;
- les autres contrôles et résultats ne sont plus déclarés en échec à cause d'un HTTP 403 externe.

L'entrée `exiger_donnees_externes` permet de réactiver le mode strict. Dans ce mode, l'absence d'un jeu requis fait échouer l'exécution.

Le dossier `donnees_externes` est aussi conservé par le cache GitHub Actions. Dès qu'une acquisition authentifiée réussit, les exécutions suivantes peuvent réutiliser les fichiers validés sans dépendre d'un nouveau téléchargement Dryad.

## Contrôles couverts

Les tests vérifient notamment :

- la résolution de la version Dryad courante ;
- l'utilisation de `/api/v2/files/<id>/download` avec Bearer ;
- la suppression du Bearer lors d'une redirection vers un autre domaine ;
- le repli vers les liens publics sans identifiants secrets ;
- la validation réelle des CSV, XLSX et ZIP ;
- la conservation d'un cache complet lors d'un échec réseau ;
- le mode CI tolérant et le mode strict.
