# Campagne de tests de stress — mémoire historique ORI-C

Ce rapport est généré par `stress/make_report.py` à partir des artefacts des campagnes A à E. Il ne remplace pas `REPORT.md` : il soumet le résultat livré à des contrôles que le protocole initial n'exécutait pas.

## 0. Contrôle du harnais

Le simulateur MPT compilé reproduit `simulate_mpt` bit à bit (oui) et l'EMIC compilé reproduit `simulate_reduced_climate` à moins de 1e-12 en écart relatif (oui), pour un gain de vitesse de 129×. Toute la campagne repose sur ce noyau.
## 1. Les cinq critères MPT préenregistrés, recalculés

Aucun seuil n'est modifié. Seules changent la qualité de l'optimisation, la correction d'autocorrélation du BIC et l'ajout d'un témoin à nombre de paramètres égal.


### Témoin M1, bornes livrées — 2/5 critères réussis

| Critère | Valeur | Seuil | Verdict |
|---|---:|---:|---:|
| forecast_rmse_gain_at_least_5pct | 0.0604 | 0.0500 | RÉUSSI |
| forecast_delta_bic_at_most_minus_10 (naif) | -128.2245 | -10.0000 | RÉUSSI |
| forecast_delta_bic_at_most_minus_10 (n_eff) | 6.5157 | -10.0000 | NON RÉUSSI |
| 100k_regime_within_factor_2_and_closer_than_reference | 0.0186 | 1.3018 | NON RÉUSSI |
| chronology_correlation_and_termination_timing | 0.0935 | 0.4000 | NON RÉUSSI |
| blockwise_wilcoxon_M2_better | 5.960e-08 | 0.0500 | RÉUSSI |

Autocorrélation de rang 1 des résidus de M2 : 0.9709. Taille d'échantillon nominale 1200, efficace 17.7.

### Témoin M1P, bornes livrées — 0/5 critères réussis

| Critère | Valeur | Seuil | Verdict |
|---|---:|---:|---:|
| forecast_rmse_gain_at_least_5pct | -0.1839 | 0.0500 | NON RÉUSSI |
| forecast_delta_bic_at_most_minus_10 (naif) | 405.0906 | -10.0000 | NON RÉUSSI |
| forecast_delta_bic_at_most_minus_10 (n_eff) | 5.3147 | -10.0000 | NON RÉUSSI |
| 100k_regime_within_factor_2_and_closer_than_reference | 0.0186 | 1.3018 | NON RÉUSSI |
| chronology_correlation_and_termination_timing | 0.0935 | 0.4000 | NON RÉUSSI |
| blockwise_wilcoxon_M2_better | 1.0000 | 0.0500 | NON RÉUSSI |

Autocorrélation de rang 1 des résidus de M2 : 0.9709. Taille d'échantillon nominale 1200, efficace 17.7.

### Témoin M1, bornes élargies — 1/5 critères réussis

| Critère | Valeur | Seuil | Verdict |
|---|---:|---:|---:|
| forecast_rmse_gain_at_least_5pct | 0.0357 | 0.0500 | NON RÉUSSI |
| forecast_delta_bic_at_most_minus_10 (naif) | -66.0795 | -10.0000 | RÉUSSI |
| forecast_delta_bic_at_most_minus_10 (n_eff) | 8.3590 | -10.0000 | NON RÉUSSI |
| 100k_regime_within_factor_2_and_closer_than_reference | 0.0047 | 1.3018 | NON RÉUSSI |
| chronology_correlation_and_termination_timing | 0.2595 | 0.4000 | NON RÉUSSI |
| blockwise_wilcoxon_M2_better | 1.196e-04 | 0.0500 | RÉUSSI |

Autocorrélation de rang 1 des résidus de M2 : 0.9703. Taille d'échantillon nominale 1200, efficace 18.1.

### Témoin M1P, bornes élargies — 0/5 critères réussis

| Critère | Valeur | Seuil | Verdict |
|---|---:|---:|---:|
| forecast_rmse_gain_at_least_5pct | -0.3157 | 0.0500 | NON RÉUSSI |
| forecast_delta_bic_at_most_minus_10 (naif) | 658.4539 | -10.0000 | NON RÉUSSI |
| forecast_delta_bic_at_most_minus_10 (n_eff) | 9.3432 | -10.0000 | NON RÉUSSI |
| 100k_regime_within_factor_2_and_closer_than_reference | 0.0047 | 1.3018 | NON RÉUSSI |
| chronology_correlation_and_termination_timing | 0.2595 | 0.4000 | NON RÉUSSI |
| blockwise_wilcoxon_M2_better | 1.0000 | 0.0500 | NON RÉUSSI |

Autocorrélation de rang 1 des résidus de M2 : 0.9703. Taille d'échantillon nominale 1200, efficace 18.1.


## 2. Le gain dépend-il du budget d'optimisation ?

Mêmes données, mêmes graines, même fenêtre. Seul le budget de l'optimiseur varie.

| Bornes | Budget | itérations | RMSE prédiction M1 | RMSE prédiction M2 | RMSE prédiction M1P | gain M2/M1 | gain M2/M1P |
|---|---|---:|---:|---:|---:|---:|---:|
| reference | livre | 30 | 2.095 | 1.969 | 1.663 | 0.0600 | -0.1838 |
| reference | faible | 80 | 2.095 | 1.969 | 1.663 | 0.0599 | -0.1839 |
| reference | moyen | 250 | 2.096 | 1.969 | 1.663 | 0.0604 | -0.1839 |
| reference | eleve | 700 | 2.096 | 1.969 | 1.663 | 0.0604 | -0.1839 |
| reference | maximal | 1500 | 2.096 | 1.969 | 1.663 | 0.0604 | -0.1839 |
| wide | livre | 30 | 2.118 | 2.042 | 1.551 | 0.0360 | -0.3163 |
| wide | faible | 80 | 2.118 | 2.042 | 1.566 | 0.0360 | -0.3036 |
| wide | moyen | 250 | 2.118 | 2.042 | 1.559 | 0.0360 | -0.3097 |
| wide | eleve | 700 | 2.118 | 2.042 | 1.553 | 0.0358 | -0.3149 |
| wide | maximal | 1500 | 2.118 | 2.042 | 1.552 | 0.0357 | -0.3156 |


## 3. Statistiques robustes sur la fenêtre de prédiction

Autocorrélation de rang 1 des résidus de M1 : 0.9711, soit un temps de décorrélation de 34.1 ka. La fenêtre contient 1200 points de grille mais seulement 17.6 points indépendants.

| Témoin | gain ponctuel | IC 95 % bootstrap par blocs | P(gain < 5 %) | P(gain < 0) | Wilcoxon par blocs |
|---|---:|---:|---:|---:|---:|
| M0 | 0.0250 | [0.0167 ; 0.0356] | 0.9999 | 0 | 0.0069 |
| M1 | 0.0357 | [0.0272 ; 0.0457] | 0.9946 | 0 | 1.196e-04 |
| M1P | -0.3157 | [-0.3839 ; -0.2550] | 1.0000 | 1.0000 | 1.0000 |


## 4. Sensibilité à la fenêtre de séparation

| Séparation (ka) | gain M2/M1 | gain M2/M1P | corrélation M2 | rapport 100/41 de M2 | cible observée |
|---:|---:|---:|---:|---:|---:|
| 800 | 0.0932 | -0.1846 | 0.1316 | 0.0198 | 6.8565 |
| 900 | 0.1136 | -0.1804 | 0.1330 | 0.0056 | 1.9116 |
| 1000 | 0.1263 | -0.1704 | 0.1142 | 0.0198 | 4.6716 |
| 1100 | 0.1374 | -0.1702 | 0.1182 | 0.0206 | 1.8309 |
| 1200 | 0.0361 | -0.3089 | 0.2600 | 0.0047 | 2.6036 |
| 1300 | 0.0378 | -0.2866 | 0.2708 | 0.0014 | 2.3504 |
| 1400 | 0.0341 | -0.2640 | 0.2841 | 0.0010 | 1.7966 |
| 1500 | 0.0397 | -0.3439 | 0.2927 | 0.0011 | 1.8789 |
| 1600 | 0.0425 | -0.3923 | 0.2981 | 3.586e-04 | 1.3323 |


## 5. Distribution nulle du gain

60 tirages par type de nul. Le budget d'optimisation est identique pour tous les modèles à l'intérieur d'un tirage.

| Nul | gain moyen M2/M1 | 95e centile | maximum | fraction ≥ 5 % | fraction ≥ 5 % contre M1P |
|---|---:|---:|---:|---:|---:|
| cible | -0.3784 | 0.1013 | 0.2052 | 0.1000 | 0.3500 |
| forcage | 0.1237 | 0.1633 | 0.1847 | 0.8167 | 0.0333 |


## 6. Ablation de la mémoire carbone de M2

| Quantité | Valeur |
|---|---:|
| carbon_feedback_gain_fitted | -20.0000 |
| tau_carbon_kyr_fitted | 24.7623 |
| rmse_M1 | 2.1178 |
| rmse_M2 | 2.0421 |
| rmse_M2_couplage_gele | 2.9002 |
| rmse_M2_reajuste_sans_carbone | 2.1178 |
| gain_M2_vs_M1 | 0.0357 |
| gain_M2_gele_vs_M1 | -0.3695 |
| gain_M2_reajuste_sans_carbone_vs_M1 | 9.929e-07 |
| fraction_du_gain_portee_par_la_memoire_carbone | 1.0000 |


## 7. Indépendance, identifiabilité et capacité structurelle

### 7.1 Définition du forçage astronomique

| Forçage | gain M2/M1 | gain M2/M1P | corrélation M2 | rapport 100/41 de M2 |
|---|---:|---:|---:|---:|
| juin65N_livre | 0.0359 | -0.3148 | 0.2596 | 0.0047 |
| juin45N | 0.1574 | -0.1552 | 0.0062 | 0.0654 |
| juin55N | 0.1565 | -0.1492 | 0.0540 | 0.0441 |
| juin75N | 0.0367 | -0.3158 | 0.2836 | 0.0045 |
| juin65S | 0.1734 | -0.1346 | 0.4241 | 0.0021 |
| decembre65N | 0.1720 | -0.1102 | 0.4104 | 0.0019 |
| equinoxe_mars_65N | 0.1465 | -0.1509 | 0.2330 | 247.1960 |
| energie_estivale_65N | 0.0343 | -0.3231 | 0.2651 | 0.0052 |
| obliquite_seule | 0.1699 | -0.1610 | 0.4219 | 0.0022 |
| excentricite_seule | 0.1656 | -0.1483 | 0.4020 | 1246.3763 |
| precession_climatique | 0.1500 | -0.1598 | 0.2544 | 1.0282 |


### 7.2 Capacité spectrale et compromis

Rapport 100/41 ka observé sur la fenêtre de prédiction : 2.6036. Borne inférieure du facteur 2 : 1.3018.

Ce test utilise délibérément la fenêtre de prédiction comme oracle. Une réussite ne vaut pas validation ; un échec vaut réfutation structurelle.

| Modèle | rapport atteignable sans contrainte | RMSE à ce point | capable structurellement | RMSE minimale (× M1) pour atteindre la bande |
|---|---:|---:|---:|---:|
| M1 | 2.6036 | 2.775 | oui | 1.00 |
| M2 | 2.6038 | 6.833 | oui | 1.00 |
| M1P | 2.6036 | 15.923 | oui | 1.00 |


### 7.3 Inversion du sens de prédiction

Ajustement sur 1,2–0 Ma, prédiction sur 2,6–1,2 Ma.

| Modèle | RMSE prédiction | corrélation |
|---|---:|---:|
| M0 | 1.124 | 0.2929 |
| M1 | 1.480 | -0.3121 |
| M2 | 1.759 | -0.1297 |
| M1P | 2.053 | 0.3089 |

Gain de M2 sur M1 : -0.1886. Sur M1P : 0.1432.


### 7.4 Identifiabilité des paramètres de M2

Chaque paramètre est gelé sur une grille, les autres sont réoptimisés. « Plat » signifie que geler le paramètre n'importe où sur sa grille coûte moins de 1 % de RMSE d'apprentissage.

| Paramètre | excès relatif maximal | fraction plate à 1 % | identifié |
|---|---:|---:|---:|
| forcing_gain | 0.1423 | 0.0769 | oui |
| forcing_offset | 0.0242 | 0.5385 | non |
| tau_fast_kyr | 0.0949 | 0.5385 | non |
| tau_memory_gain_kyr | 0.0317 | 0.4615 | oui |
| regolith_scale | 0.0315 | 0.1538 | oui |
| tau_regolith_kyr | 0.0315 | 0.5385 | non |
| carbon_feedback_gain | 0.2042 | 0.1538 | oui |
| tau_carbon_kyr | 0.0717 | 0.0769 | oui |
| carbon_offset | 0.0986 | 0.0769 | oui |


### 7.5 Stabilité des paramètres ajustés

| Paramètre | minimum | médiane | maximum | ordres de grandeur | change de signe |
|---|---:|---:|---:|---:|---:|
| forcing_gain | -2.6348 | -1.1019 | -0.8136 | 0.51 | non |
| forcing_offset | -3.9785 | 0.4460 | 3.5803 | 1.77 | oui |
| tau_fast_kyr | 1.0004 | 4.4810 | 47.7153 | 1.68 | non |
| tau_memory_gain_kyr | 0.0190 | 8.9988 | 33.2548 | 3.24 | non |
| regolith_scale | 0.0036 | 0.0067 | 0.0656 | 1.26 | non |
| tau_regolith_kyr | 20.0000 | 20.0027 | 340.2204 | 1.23 | non |
| carbon_feedback_gain | -20.0000 | -20.0000 | -19.9219 | 0.00 | non |
| tau_carbon_kyr | 22.2154 | 10845.2572 | 12648.7535 | 2.76 | non |
| carbon_offset | -0.8552 | -0.3341 | 0.1491 | 2.59 | oui |


## 8. Test exoplanétaire durci

### 8.1 Convergence numérique

| Variable | Δ à 0,02 Ma (pas livré) | Δ à 0,0025 Ma | écart relatif | Δ du modèle classique | rapport M2/classique |
|---|---:|---:|---:|---:|---:|
| temperature_k | 0.0025 | 0.0026 | 0.0147 | 1.224e-08 | 2.058e+05 |
| ice_fraction | 3.529e-05 | 3.550e-05 | 0.0059 | 5.021e-11 | 7.029e+05 |
| co2_ppm | 0.6866 | 0.6965 | 0.0141 | 2.634e-06 | 2.607e+05 |
| productivity | 3.756e-04 | 3.803e-04 | 0.0123 | 1.719e-09 | 2.186e+05 |


### 8.2 Test de relaxation (décisif)

Le protocole livré maintient le forçage final commun pendant 10 Ma. On le prolonge.

| Variable | Δ à 10 Ma | Δ au palier le plus long | fraction conservée | temps d'e-folding (Ma) | jamais matériel |
|---|---:|---:|---:|---:|---:|
| temperature_k | 0.0025 | 0 | 0 | 7.02 | oui |
| ice_fraction | 3.529e-05 | 0 | 0 | 7.80 | oui |
| co2_ppm | 0.6866 | 0 | 0 | 7.28 | oui |
| productivity | 3.756e-04 | 5.551e-17 | 1.478e-13 | 17.66 | oui |


### 8.3 Sonde de multistabilité sous le forçage final livré

1000 états initiaux très dispersés, intégrés 800 Ma sous le seul forçage final.

| Variable | dispersion initiale | dispersion finale | seuil de matérialité |
|---|---:|---:|---:|
| temperature_k | 11.9751 | 3.020e-14 | 0.1000 |
| ice_fraction | 0.9983 | 2.220e-15 | 0.0100 |
| co2_ppm | 779.8691 | 6.708e-12 | 1.0000 |
| productivity | — | 4.718e-15 | 0.0100 |


### 8.4 Carte de matérialité (1521 combinaisons de paramètres)

| Variable | seuil | Δ maximal au palier de 10 Ma | Δ maximal au palier de 200 Ma | fraction matérielle à 10 Ma | fraction matérielle à 200 Ma |
|---|---:|---:|---:|---:|---:|
| temperature_k | 0.1000 | 0.2363 | 0.0414 | 0.1920 | 0 |
| ice_fraction | 0.0100 | 3.089e-04 | 6.441e-05 | 0 | 0 |
| co2_ppm | 1.0000 | 58.1792 | 10.8155 | 0.7219 | 0.3307 |
| productivity | 0.0100 | 0.0342 | 0.0062 | 0.3531 | 0 |


### 8.5 Balayage du régime de forçage final (54 points)

| Variable | dispersion maximale des attracteurs | points à attracteurs multiples | Δ matériel à 10 Ma | Δ matériel à 200 Ma |
|---|---:|---:|---:|---:|
| temperature_k | 2.6645 | 4/54 | 2/54 | 0/54 |
| ice_fraction | 0.9243 | 4/54 | 5/54 | 0/54 |
| co2_ppm | 181.3944 | 4/54 | 26/54 | 0/54 |
| productivity | 0.6039 | 4/54 | 3/54 | 0/54 |
