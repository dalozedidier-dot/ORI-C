# Interfaces des extensions physiques

Le banc actuel accepte une série temporelle d'excentricité. Les extensions suivantes doivent publier des séries indépendantes avant d'être branchées :

1. barycentre Terre-Lune et orbite lunaire résolue ;
2. obliquité et précession de rotation calculées, plutôt que reprises de La2004 ;
3. dissipation de marée avec paramètres et incertitudes déclarés ;
4. sortie climatique intermédiaire ou GCM avec température, glace, humidité et bilans énergétiques ;
5. prédictions hors échantillon contre un témoin de complexité égale.

Le schéma minimal attendu est documenté dans `schema_sortie_extension.json`. Aucun de ces champs n'est déclaré calculé dans la version 0.9.3.
