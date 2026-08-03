# Ablations astronomiques A1–A6

Statut : protocole gelé localement, exécution multi-plateforme non encore réalisée.

Toutes les ablations utilisent les mêmes conditions initiales, sorties, horizons, tolérances et graines. Elles sont comparées sur erreur de phase, spectre, conservation et coût :

- A1 : retrait de la Lune explicitement résolue ;
- A2 : retrait du J2 solaire ;
- A3 : retrait des marées ;
- A4 : découplage rotation-orbite ;
- A5 : obliquité imposée au lieu de dynamique ;
- A6 : intégrateur et pas de temps alternatifs.

Le produit attendu est un forçage astronomique avec incertitudes. Aucune interprétation climatique ou géologique ne fait partie du verdict astronomique. REBOUND est figé à la version 4.6.0 dans l'environnement commun. Une exécution n'est confirmatoire qu'après concordance Windows, Linux et macOS dans la matrice CI.

