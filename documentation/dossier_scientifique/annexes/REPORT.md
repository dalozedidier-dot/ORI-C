# Tests ORI-C de mémoire historique

## Conclusion

L’implémentation est complète et reproductible. Le calcul sur LR04 ne valide pas la déclinaison paléoclimatique d’ORI-C. M2 réduit l’erreur de prédiction par rapport à M1, mais M1, avec ses six paramètres, n’est pas un témoin équitable. Face à M1P, qui possède le même nombre de paramètres que M2 mais dont l’état lent filtre le forçage externe au lieu d’inscrire la réponse passée, M2 perd. L’avantage mesuré contre M1 provient donc de degrés de liberté supplémentaires et non d’une mémoire historique.

Le test exoplanétaire contrôlé réussit le test structurel de dépendance au chemin et son test d’ablation, mais échoue au test de persistance : l’écart entre les deux histoires s’efface lorsque le forçage final commun est maintenu au-delà des constantes de temps lentes du modèle. Ce qui est détecté est un retard de relaxation, non une inscription durable.

## Statut synthétique

| Branche | Résultat | Portée |
|---|---:|---|
| MPT LR04, M2 contre M1 (moins complexe) | 1/5 critères | Comparaison non appariée en complexité |
| MPT LR04, M2 contre M1P (complexité égale) | 0/5 critères | Test décisif de la mémoire ORI-C |
| Exoplanète, dépendance au chemin | RÉUSSI | Validation structurelle du code et de l’ablation |
| Exoplanète, persistance de l’écart | NON RÉUSSI | Palier final prolongé à 300.0 Ma |
| Exoplanète, amplitude physique | NON RÉUSSI | Non calibrée sur un GCM ou une archive réelle |

## Test MPT

Les quatre modèles sont ajustés uniquement entre 2,6 et 1,2 Ma. Les paramètres sont ensuite figés et propagés jusqu’au présent. M0 est une réponse fixe. M1 ajoute une mémoire classique du régolithe. M2 reprend M1 et ajoute une mémoire lente du carbone, pilotée par le volume de glace passé. M1P reprend M1 et ajoute un état lent de même structure, mais piloté par le forçage astronomique.

M1P est le témoin décisif. Il possède exactement le même nombre de paramètres que M2 et la même constante de temps lente supplémentaire. Il ne diffère que sur un point : son état lent n’enregistre pas la réponse passée du système. Un avantage de M2 sur M1 mesure de la flexibilité ; seul un avantage de M2 sur M1P mesurerait l’inscription revendiquée par ORI-C.

Trois symétries exactes sont retirées par définition : les échelles de R et de C, qui rendaient α/R* et β/γ non identifiables, et le décalage de l’état lent, exactement compensable par le décalage du forçage. Sans cette troisième correction, le test d’ablation carbone n’est pas défini : deux ajustements donnant la même prédiction donnent des ablations différentes.

| Modèle | Paramètres | RMSE prédiction | Corrélation | Rapport 100/41 ka | BIC (n efficace) | BIC (n brut) |
|---|---:|---:|---:|---:|---:|---:|
| M0 | 3 | 2.094 | 0.0861 | 0.0175 | 34.654 | 1795.6 |
| M1 | 6 | 2.118 | 0.0857 | 0.0206 | 43.574 | 1843.4 |
| M2 | 8 | 2.042 | 0.2595 | 0.0047 | 49.036 | 1770.3 |
| M1P | 8 | 1.552 | 0.1750 | 0.0220 | 39.671 | 1111.9 |

LR04 présente un rapport de puissance 100/41 ka de 2.604 sur la fenêtre de prédiction. M2 produit 0.0047, soit un écart de plus de deux ordres de grandeur. Ce constat est le plus robuste du test : il ne dépend ni du témoin choisi ni de la qualité de l’optimisation.

### Comparaison aux deux témoins

| Témoin | gain de RMSE | IC 95 % (blocs mobiles) | P(gain < 5 %) | ΔBIC (n efficace) | ΔBIC (n brut) | Wilcoxon par blocs |
|---|---:|---:|---:|---:|---:|---:|
| M1 | 0.0357 | [0.0272 ; 0.0457] | 0.9951 | 5.463 | -73.167 | 1.196e-04 |
| M1P | -0.3156 | [-0.3893 ; -0.2508] | 1.000 | 9.365 | 658.3 | 1.0000 |

Les résidus de prédiction ont une autocorrélation de rang 1 de 0.9703. La fenêtre contient 1200 points de grille mais 18.112 points indépendants. Le BIC calculé sur le compte brut surestime donc massivement le support des paramètres supplémentaires ; c’est la version corrigée qui est retenue pour le verdict.

Contrôle d’optimisation : M0=convergé, M1=convergé, M2=convergé, M1P=convergé. Dispersion relative de la RMSE d’apprentissage entre redémarrages : M0=4.292e-10, M1=2.205e-09, M2=5.892e-05, M1P=0.0039. Noyau compilé : oui.
Paramètres aux bornes : M0: aucun; M1: tau_fast_kyr=borne_basse, tau_regolith_kyr=borne_basse; M2: tau_fast_kyr=borne_basse, regolith_scale=borne_basse, carbon_feedback_gain=borne_basse, tau_carbon_kyr=borne_basse; M1P: tau_fast_kyr=borne_basse, regolith_scale=borne_basse, tau_regolith_kyr=borne_basse.

### Critères préenregistrés

Les cinq critères sont évalués contre chacun des deux témoins. Le verdict global exige la réussite de tous les critères contre les deux.

| Témoin | Critère | Valeur | Seuil | Verdict |
|---|---|---:|---:|---:|
| M1 | forecast_rmse_gain_at_least_5pct | 0.0357 | 0.0500 | NON RÉUSSI |
| M1 | forecast_delta_bic_at_most_minus_10 | 5.463 | -10.000 | NON RÉUSSI |
| M1 | 100k_regime_within_factor_2_and_closer_than_control | 0.0047 | 1.302 | NON RÉUSSI |
| M1 | chronology_correlation_and_termination_timing | 0.2595 | 0.4000 | NON RÉUSSI |
| M1 | blockwise_wilcoxon_M2_better_than_control | 1.196e-04 | 0.0500 | RÉUSSI |
| M1P | forecast_rmse_gain_at_least_5pct | -0.3156 | 0.0500 | NON RÉUSSI |
| M1P | forecast_delta_bic_at_most_minus_10 | 9.365 | -10.000 | NON RÉUSSI |
| M1P | 100k_regime_within_factor_2_and_closer_than_control | 0.0047 | 1.302 | NON RÉUSSI |
| M1P | chronology_correlation_and_termination_timing | 0.2595 | 0.4000 | NON RÉUSSI |
| M1P | blockwise_wilcoxon_M2_better_than_control | 1.0000 | 0.0500 | NON RÉUSSI |

### Ablation de la mémoire carbone

Retirer le couplage carbone des paramètres ajustés de M2 porte la RMSE de prédiction à 1.810. L’effet du couplage sur la RMSE vaut -0.2320 (positif si le couplage aide).

Le couplage carbone dégrade la prédiction hors échantillon : aux paramètres retenus par l’ajustement sur la calibration, la mémoire est activement nuisible une fois les paramètres figés. C’est un symptôme de surajustement, cohérent avec le fait que le couplage reste sur sa borne et que sa constante de temps n’est pas identifiée.

### Limite d’indépendance

LR04 est une pile δ18O majeure, mais son modèle d’âge a été accordé à un modèle de glace fondé sur l’insolation du 21 juin à 65°N. Employer La2004 contre cette chronologie crée donc une dépendance méthodologique. Le test reste utile pour comparer des prévisions figées, mais une validation forte exigera des archives et des chronologies indépendantes.

## Test exoplanétaire contrôlé

Deux histoires spin-orbitales différentes sont imposées pendant 50 Ma, puis exactement le même état final est maintenu pendant 10.000 Ma. Les ensembles sont appariés. Le modèle classique, M2 et M2 avec mémoires figées reçoivent les mêmes forçages et les mêmes conditions initiales.

Le protocole ajoute un palier de persistance à 300.0 Ma. Les constantes de temps lentes du modèle valent 8 Ma pour le carbone et 60 Ma pour le régolithe : un palier de 10 Ma est plus court que la mémoire qu’il prétend mesurer, si bien que les deux histoires y sont encore en train de converger.

| Variable | Δ classique | Δ M2 sans mémoire | Δ M2 | Δ M2 palier long | fraction conservée | p corrigé | Matérialité | Persistance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| temperature_k | 9.807e-09 | 3.980e-09 | 0.0026 | 0 | 0 | 3.638e-12 | NON RÉUSSI | NON RÉUSSI |
| ice_fraction | 4.021e-11 | 5.637e-12 | 3.547e-05 | 0 | 0 | 3.638e-12 | NON RÉUSSI | NON RÉUSSI |
| co2_ppm | 2.110e-06 | 8.662e-07 | 0.6964 | 0 | 0 | 3.638e-12 | NON RÉUSSI | NON RÉUSSI |
| productivity | 1.412e-09 | 5.711e-10 | 3.812e-04 | 5.551e-17 | 1.456e-13 | 3.638e-12 | NON RÉUSSI | NON RÉUSSI |

La dépendance au chemin est significative pour 4 variables sur 4, et son retrait ramène les écarts au niveau nul pour 4 variables. 0 variables franchissent le seuil d’amplitude défini avant le calcul, et 0 conservent un écart matériel après le palier long.

## Ce que le paquet permet maintenant

- relancer les calculs avec les mêmes données, graines et critères
- comparer le modèle testé à un témoin de complexité égale
- séparer un gain de mémoire d’un gain de flexibilité
- distinguer une inscription durable d’un retard de relaxation
- remplacer LR04 par des archives indépendantes sans modifier les modèles
- remplacer les trajectoires prescrites par des sorties N-corps-spin
- remplacer l’EMIC réduit par des sorties ROCKE-3D, WACCM6 ou GEOCLIM
- conserver séparément validation structurelle et validation physique

## Sources primaires

- Lisiecki, L. E. et Raymo, M. E. (2005), LR04, doi:10.1029/2004PA001071, jeu NOAA doi:10.25921/k88j-0106
- Laskar et al. (2004), La2004, doi:10.1051/0004-6361:20041335, données IMCCE

## Fichiers de résultat

- `results/mpt/` : prédictions, métriques, paramètres, blocs et figures
- `results/exoplanet/` : forçages, ensembles, ablation, tests et figures
- `data/processed/mpt_lr04_la2004.csv` : grille commune à 1 ka
- `STRESS_REPORT.md` : campagne de stress complète et ses annexes
- `MANIFEST.sha256` : empreintes de l’ensemble du paquet
