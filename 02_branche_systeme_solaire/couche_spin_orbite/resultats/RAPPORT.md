# Résultat exécuté — spin, obliquité et ablation lunaire

## Statut

Cette couche est **calculée**. Elle n'est plus une simple feuille de route. Elle reste un modèle séculaire réduit : le couple lunaire est représenté par la constante de précession effective, sans orbite lunaire explicite ni évolution tidale.

## Chaîne calculée

`architecture N-corps → plan orbital terrestre → spin → obliquité → équinoxe mobile → insolation à 65°N`

Une ablation architecturale est calculée en remplaçant `α = 54,93″/an` par la valeur solaire seule `α ≈ 20″/an`, toutes les séries orbitales étant identiques.

## Validation La2004

|   horizon_years |   samples |   obliquity_rmse_deg |   obliquity_correlation |   moving_perihelion_circular_rmse_rad |   insolation_rmse_w_m2 |   insolation_correlation |
|----------------:|----------:|---------------------:|------------------------:|--------------------------------------:|-----------------------:|-------------------------:|
|      100000     |       101 |           0.00780543 |                0.999948 |                            0.00685998 |               0.221985 |                 0.999943 |
|      500000     |       501 |           0.0593827  |                0.995895 |                            0.0837801  |               1.78828  |                 0.997188 |
|           1e+06 |      1001 |           0.0791416  |                0.989927 |                            0.128107   |               3.07272  |                 0.991523 |
|           2e+06 |      2001 |           0.159551   |                0.955465 |                            0.25036    |               5.8313   |                 0.971319 |
|           5e+06 |      5001 |           0.198962   |                0.924604 |                            0.445135   |               7.22963  |                 0.950242 |
|           1e+07 |     10001 |           0.46941    |                0.572448 |                            1.31437    |              22.9562   |                 0.502868 |
|           2e+07 |     20001 |           0.593263   |                0.289242 |                            1.55936    |              28.0212   |                 0.25732  |

## Avec et sans couple lunaire

| configuration       |   horizon_years |   obliquity_min_deg |   obliquity_max_deg |   obliquity_range_deg |   obliquity_std_deg |   dominant_obliquity_period_years |   insolation_min_w_m2 |   insolation_max_w_m2 |   insolation_std_w_m2 |
|:--------------------|----------------:|--------------------:|--------------------:|----------------------:|--------------------:|----------------------------------:|----------------------:|----------------------:|----------------------:|
| avec Lune effective |         2000000 |            22.0873  |             24.4437 |                2.3564 |            0.531724 |                           40836.7 |               433.147 |               564.064 |               24.3909 |
| sans Lune           |         2000000 |             1.24985 |             45.0419 |               43.792  |           10.1335   |                          333500   |               187.446 |               947.891 |              166.915  |

## Propagation des interventions Jupiter/Saturne

| job                          |   obliquity_rmse_vs_baseline_deg |   obliquity_effect_to_ensemble_floor |   insolation_rmse_vs_baseline_w_m2 |   insolation_effect_to_ensemble_floor |
|:-----------------------------|---------------------------------:|-------------------------------------:|-----------------------------------:|--------------------------------------:|
| jupiter_mass_minus_5pct_2myr |                         0.754083 |                          1.81537e+07 |                            31.056  |                           1.82784e+07 |
| jupiter_mass_plus_5pct_2myr  |                         0.637494 |                          1.53469e+07 |                            26.8262 |                           1.57889e+07 |
| saturn_mass_minus_5pct_2myr  |                         0.184053 |                          4.43086e+06 |                            11.9985 |                           7.0619e+06  |
| saturn_mass_plus_5pct_2myr   |                         0.200976 |                          4.83826e+06 |                            12.3419 |                           7.26401e+06 |
| jupiter_a_minus_0p5pct_2myr  |                         0.300335 |                          7.23021e+06 |                            16.1992 |                           9.53429e+06 |
| jupiter_a_plus_0p5pct_2myr   |                         0.317477 |                          7.6429e+06  |                            15.1345 |                           8.90761e+06 |

## Bruit et convergence

Dispersion RMS de l'ensemble orbital propagé au spin : `4.15389e-08°` ; propagée à l'insolation : `1.69905e-06 W/m²`.

Le plus petit rapport effet intervention / dispersion d'ensemble vaut `4.43e+06` pour l'obliquité et `7.06e+06` pour l'insolation.

La convergence 100 ans → 50 ans donne une RMSE d'obliquité de `3.74e-07°` avec Lune effective.

## Limite qui reste ouverte

Cette exécution établit le chaînage dynamique jusqu'à l'obliquité et à l'insolation **dans un modèle séculaire de spin comparé à La2004**. Elle ne constitue pas encore une intégration Terre-Lune explicite : l'orbite lunaire, les marées et l'évolution de la distance Terre-Lune restent à traiter dans une extension longue durée distincte.
