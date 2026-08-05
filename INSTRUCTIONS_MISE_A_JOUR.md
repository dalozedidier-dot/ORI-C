# Instructions de mise à jour

## Fichiers à supprimer avant copie

Aucun fichier à supprimer pour cette mise à jour.

## Problème corrigé

L'écran de lancement du workflow présentait uniquement des options de téléchargement.
Il ne montrait pas clairement que les trois jeux nouvellement intégrés étaient ensuite
analysés. Leur contrôle était noyé dans `run_all.py` et aucun rapport distinct ne
prouvait que les fichiers réels, puis leurs résultats, avaient été testés.

Le workflow affiche désormais un seul choix explicite :

1. `Tester les données intégrées`
2. `Rafraîchir puis tester`
3. `Retélécharger puis tester`

Dans les trois cas, le test est exécuté. Une étape séparée contrôle les fichiers,
leurs empreintes et les résultats obtenus sur :

- les 12 classeurs Dryad de vésicules ;
- les 3 CSV Dryad sur l'histoire antibiotique ;
- le CSV NOAA des spéléothèmes.

## Fichiers ajoutés

- `scripts/valider_donnees_reelles.py`
- `plan_directeur/campagne_recherche_suivante/resultats/VALIDATION_DONNEES_REELLES.json`
- `plan_directeur/campagne_recherche_suivante/resultats/VALIDATION_DONNEES_REELLES.md`

## Fichiers remplacés

- `.github/workflows/recherche-suivante.yml`
- `scripts/valider_recherche_suivante.py`
- `INSTRUCTIONS_MISE_A_JOUR.md`
- `MANIFEST.sha256`
- `MANIFEST.sha256.json`

## Changement visible dans GitHub Actions

Les trois anciennes cases :

- `Rafraîchir les jeux externes depuis les fournisseurs`
- `Forcer un nouveau téléchargement`
- `Échouer si un jeu requis intégré est absent ou invalide`

sont remplacées par un seul choix :

`Action sur les 3 jeux réels ; leur test est toujours exécuté`.

Ce workflow est désormais toujours strict : il échoue si l'un des trois jeux réels
est absent, altéré ou si son analyse n'est pas exécutée.

## Installation

1. Décompresser le ZIP.
2. Copier tout le contenu du dossier `ORI-C-main` dans le dépôt en remplaçant les
   fichiers existants.
3. Aucun ancien fichier ne doit être supprimé.
4. Publier tous les fichiers ajoutés et remplacés dans le même commit.
5. Ouvrir le workflow `Recherche suivante ORI-C — données réelles incluses`.
6. Choisir normalement `Tester les données intégrées`, puis lancer le workflow.

## Contrôle attendu

Le journal GitHub doit contenir l'étape :

`Tester explicitement les résultats produits sur les 3 jeux réels`

Elle doit afficher :

- 12 classeurs de vésicules vérifiés et analysés ;
- 3 CSV antibiotiques vérifiés, analyse sur 288 lignes ;
- CSV NOAA vérifié, 27 721 mesures sur 36 sites.

L'artefact contient désormais :

- `VALIDATION_DONNEES_REELLES.json`
- `VALIDATION_DONNEES_REELLES.md`
