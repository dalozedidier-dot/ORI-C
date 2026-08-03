# Statut scientifique

## Critères préenregistrés

| test                                 | observed    | operator   | threshold   | statut   |
|:-------------------------------------|:------------|:-----------|:------------|:---------|
| all_bodies_bound                     | True        | ==         | True        | RÉUSSI   |
| energy_conservation                  | 1.32514e-11 | <=         | 1e-08       | RÉUSSI   |
| angular_momentum_conservation        | 5.27623e-10 | <=         | 1e-10       | ÉCHEC    |
| initial_eccentricity_vs_la2010       | 2.19234e-10 | <=         | 1e-08       | RÉUSSI   |
| horizons_correlation_6kyr            | 1           | >=         | 0.99        | RÉUSSI   |
| horizons_rmse_6kyr                   | 4.82644e-07 | <=         | 0.0002      | RÉUSSI   |
| la2010_correlation_100000yr          | 0.999971    | >=         | 0.95        | RÉUSSI   |
| la2010_correlation_500000yr          | 0.99876     | >=         | 0.8         | RÉUSSI   |
| la2010_correlation_1000000yr         | 0.99727     | >=         | 0.6         | RÉUSSI   |
| whfast_step_convergence_2myr         | 8.42655e-07 | <=         | 0.0001      | RÉUSSI   |
| integrator_crosscheck_20kyr          | 3.13098e-07 | <=         | 1e-06       | RÉUSSI   |
| roundtrip_reversibility_100kyr       | 2.7628e-05  | <=         | 1e-05       | ÉCHEC    |
| spectral_peak_405_kyr                | 0.00786092  | <=         | 0.05        | RÉUSSI   |
| spectral_peak_2.4_Myr                | 0.166625    | <=         | 0.2         | RÉUSSI   |
| counterfactuals_above_ensemble_floor | 6.27439e+06 | >=         | 3           | RÉUSSI   |

## Portée

Les résultats constituent des preuves numériques et astronomiques réelles à l’intérieur d’un modèle N-corps explicite. Le départ est fondé sur JPL Horizons DE441 et les sorties sont confrontées aux références indépendantes Horizons et La2010.

Ils ne constituent pas encore une validation empirique générale d’ORI-C. Le modèle réduit ne résout pas la Lune, la rotation terrestre, le J2 solaire, les marées, l’obliquité dynamique ni une archive géologique hors échantillon.

La conclusion autorisée est une validation astronomique et numérique du mécanisme réduit, avec les échecs éventuels conservés dans le tableau ci-dessus.
