# Schéma des sorties

Pour chaque scénario :

- `orbits.csv` : séries orbitales par corps. Pour REBOUND, `time_years` est la
  grille de sortie demandée et `integration_time_years` enregistre le temps
  réellement atteint par l’intégrateur lorsque `exact_finish_time: false` ;
- `spectrum.csv` : période, fréquence, puissance et seuil rouge ;
- `peaks.csv` : pics dominants ;
- `insolation.csv` : forçage radiatif saisonnier ;
- `climate.csv` : température et fraction glaciaire ;
- `metrics.json` : résumé quantitatif ;
- `figures/` : figures de contrôle.

À la racine du run :

- `comparison.csv` : comparaison contrefactuelle ;
- `REPORT.md` : rapport lisible ;
- `manifest.json` : configuration, environnement, fichiers et SHA-256 ;
- `resolved_config.yaml` : configuration exacte exécutée.
