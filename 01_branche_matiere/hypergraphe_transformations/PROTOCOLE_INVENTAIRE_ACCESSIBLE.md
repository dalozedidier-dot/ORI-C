# Protocole de mesure de l'inventaire accessible

L'inventaire accessible n'est pas l'abondance globale. Pour un élément et une espèce chimique donnés :

`I_accessible = quantité du réservoir × fraction mobilisable × probabilité de transfert × min(1, durée disponible / horizon)`.

Chaque enregistrement doit préciser le corps, l'épisode historique, le réservoir, la spéciation, l'horizon, l'unité, l'incertitude et une source primaire. Les valeurs absentes restent vides : elles ne sont ni imputées ni simulées.

La première campagne mesurable doit comparer au moins deux histoires menant à un inventaire total voisin mais à des répartitions différentes entre noyau, manteau, croûte, atmosphère et hydrosphère. Les coefficients de partage métal-silicate et les conditions P–T–redox doivent provenir d'expériences ou de compilations expérimentales sourcées.

Le fichier `inventaire_accessible_schema.csv` est un schéma, pas un jeu de données. Sa ligne d'exemple doit être supprimée lors de la première ingestion réelle.
