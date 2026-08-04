# Plateforme ORI-C intégrée

Ce répertoire contient la plateforme complète nécessaire à la reproduction :

- `source_corrigee/` : source complète v0.2.0, avec les correctifs appliqués ;
- `wheel_corrige/` : wheel reconstruite depuis cette source ;
- `requirements.txt` : dépendances minimales déclarées ;
- `source_corrigee/requirements-lock.txt` : environnement exact utilisé par les workflows canoniques ;
- `catalogue_tests.csv` : 683 descriptions de tests ;
- `criteria.csv` : grille des critères ;
- `donnees/` : données de travail livrées avec la plateforme ;
- `commande_reproduction.bat` et `.sh` : commandes de reproduction hors ligne.

La présence de 683 descriptions ne signifie pas qu'il existe 683 moteurs
scientifiques distincts. La plateforme expose maintenant 59 moteurs, dont six
moteurs paléoclimatiques spécialisés (chronologie, robustesse des proxys,
hystérésis, spectres, identifiabilité et dépendance au chemin). Vingt-neuf
descriptions ont été réaffectées à ces moteurs. Un succès
technique prouve l'exécution du moteur, pas la validation scientifique de la
description particulière ni du cadre ORI-C.

Les quatre succès astronomiques sont des contrôles positifs. `C5-009` est un
contrôle de protocole et `C6-001` une comparaison non interprétable entre des
modèles et procédures différents. La synthèse défendable reste donc : zéro
hypothèse ORI-C soutenue par les 683 entrées.
