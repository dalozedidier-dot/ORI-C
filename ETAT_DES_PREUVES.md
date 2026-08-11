# État des preuves

> **Fichier généré. Ne pas modifier à la main.** Source : `preuves/PREUVES.json`.

Les certifications historiques restent inchangées. Les nouvelles analyses importées sont explicitement séparées en exploratoire, non concluant ou modèle.

## Résultats certifiés

| ID | Verdict | Niveau | Portée | Artefact |
|---|---|---|---|---|
| `C-ANT-01` | **supports** | E2 | empirique_externe | `03_branche_vivant/benchmark_histoire_antibiotique_2026/resultats/RESULTAT.json` |
| `C-VES-02` | **supports** | E2 | empirique_externe | `03_branche_vivant/lignees_vesicules/resultats/RESULTAT.json` |
| `C-VES-03` | **supports** | E4 | empirique_externe | `03_branche_vivant/lignees_vesicules/resultats/RESULTAT.json` |
| `C-MAT-MEM-05` | **does_not_support** | — | campagne_empirique_partielle_sans_admission_complete | `01_branche_matiere/memoire_materielle_reelle/derive/SYNTHESE_CAMPAGNE.json` |
| `C-AST-01` | **supports** | E4_modele | modele_physique_reduit_valide | `plan_directeur/campagne_maximale_trois_branches/resultats/systeme_solaire_robustesse.json` |

## Extensions exécutées sans reclassement des certifications

| ID | Statut | Verdict technique | Portée |
|---|---|---|---|
| `SPIN-ORB-EXE` | exploratoire | executed_model | modele_reduit |
| `VIAB-SPIN-01` | exploratoire | executed_not_kernel | modele_reduit |
| `PID-ANT-01` | exploratoire | executed | empirique_externe_secondaire |
| `CSTATE-01` | exploratoire | executed_finite_proxy | methodologique |
| `TOPO-MAT-01` | exploratoire | executed | structure_documentaire |
| `COT-MAT-01` | non_concluant | not_evaluable_missing_stoichiometry | structure_documentaire |
| `POWER-MAT-01` | exploratoire | prospective_simulation | dimensionnement |
| `MPT-M2-01` | resultat_negatif | does_not_support | modele_paleoclimatique_orbitally_tuned |
| `CCM-CLIM-01` | exploratoire | executed | observational_orbitally_tuned |
| `PCMCI-CLIM-01` | exploratoire | executed_raw_p | observational_orbitally_tuned |
| `LTEE-REPLAY-01` | exploratoire | secondary_reanalysis | empirique_externe_table_transcription |
| `ASSEMBLY-BRIDGE-01` | non_concluant | not_evaluable_missing_paired_observables | comparaison_formelle |
| `C-GC-E01` | extension_empirique_non_preregistered | supports_empirical_enrichment_sequence | direct_observation_plus_observational_reconstruction — Contraste empirique entre abondances primordiales reconstruites depuis spectres et noyaux produits par des étoiles/explosions détectés directement; aucune table de rendement théorique n’est utilisée. |
| `C-GC-E02` | extension_empirique_non_preregistered | supports_observed_stellar_dust_formation | same_object_astronomical_observation — SN1987A fournit un cas observationnel où les produits de l’explosion et une grande masse de poussière froide sont mesurés dans les éjecta. La masse est issue de la photométrie publiée; aucun rendement simulé n’est utilisé. |
| `C-GC-E03` | extension_empirique_non_preregistered | supports_replicated_direct_material_inheritance | multi_mission_returned_sample_direct_measurement — Transmission matérielle directe observée indépendamment dans Bennu, Ryugu et Wild 2. Le total de grains est un minimum de détections des études citées, pas une abondance combinée comparable. |
| `C-GC-E04` | extension_empirique_non_preregistered | supports_pre_stellar_material_processing | direct_astronomical_observation — Analogue astrophysique de l’amont de systèmes planétaires, pas observation du nuage protosolaire historique. |
| `C-GC-E05` | extension_empirique_non_preregistered | supports_observed_cloud_to_disk_supply | replicated_direct_astronomical_observation — Deux systèmes protostellaires indépendants montrent des streamers à l’échelle de milliers d’au. Cela réplique l’existence physique du canal d’apport sans reconstruire l’histoire particulière du Soleil. |
| `C-GC-E06` | extension_empirique_non_preregistered | supports_observational_molecular_inheritance | cross_system_observational_consistency — V883 Ori/67P testent la continuité isotopique de l’eau; TW Hya apporte une détection indépendante de CH3OH. Les abondances modélisées de TW Hya sont exclues. |
| `C-GC-E07` | extension_empirique_non_preregistered | supports_observed_refractory_solid_formation | direct_astronomical_observation_plus_same_object_time_domain_contrast — HOPS-315 fournit une détection de solides réfractaires dans un jeune disque. EC 53 ajoute un contraste temporel du même objet: forstérite et enstatite sont absentes en quiescence et détectées pendant le burst. Les modèles de transport restent exclus. |
| `C-GC-E08` | extension_empirique_non_preregistered | supports_persistent_nebular_heterogeneity | returned_sample_and_meteorite_measurements — Les causes dynamiques exactes de la séparation NC/CC et de l’hétérogénéité ne sont pas imposées. |
| `C-GC-E09` | extension_empirique_non_preregistered | supports_empirical_solar_disk_material_redistribution | returned_sample_mineralogy_and_isotopes — La coexistence de stardust et de matériaux réfractaires/haute température dans Wild 2 soutient un mélange/transport à grande échelle. Aucun scénario dynamique ni distance de transport n’est calculé ici. |
| `C-GC-E10` | extension_empirique_non_preregistered | supports_measured_early_solar_chronology | meteoritic_chronometry — Âges Pb-Pb U-corrigés mesurés sur inclusions et chondres; aucune horloge synthétique n’est utilisée. |
| `C-GC-E11` | extension_empirique_non_preregistered | supports_laboratory_dust_mechanisms | laboratory_experiment — Seules les mesures expérimentales entrent dans les résultats; toute section numérique des articles est exclue. |
| `C-GC-E12` | extension_empirique_non_preregistered | supports_timing_dependent_material_fates | meteoritic_chronometry — Association chronologique empirique entre archives de corps différenciés précoces et carbonates hydratés plus tardifs; aucun calcul thermique n’est utilisé comme preuve. |
| `C-GC-E13` | extension_empirique_non_preregistered | supports_observed_disk_to_protoplanet_sequence | astronomical_observation — Le contexte général utilise plusieurs systèmes observés, mais PDS 70 fournit en plus un raccord dans le même système entre une cavité de disque et deux protoplanètes Hα en accrétion; aucune structure annulaire n’est automatiquement attribuée à une planète et aucune migration/résonance n’est utilisée comme preuve. |
| `C-GC-E14` | extension_empirique_non_preregistered | supports_planet_specific_accretion_histories | planetary_isotope_reconstruction_plus_observed_endpoint — Les scénarios orbitaux expliquant ces apports sont exclus; seuls les systèmes isotopiques mesurés et l’endpoint planétaire actuel sont retenus. |
| `C-GC-E15` | extension_empirique_non_preregistered | supports_empirical_historical_accessibility_mechanism | cross_domain_empirical_synthesis — Synthèse initiale non préenregistrée. Le verdict est calculé à partir des quatorze résultats locaux précédents. Il porte sur le mécanisme de transmission historique, pas sur une loi universelle ni sur une trajectoire cosmologique/orbitale unique. |
| `C-GC-E16` | ouvert_empirique | undetermined_empirical_only | explicit_limit — Les archives empiriques atteignent l’architecture présente et contraignent des histoires de croissance, mais elles ne sélectionnent pas une unique trajectoire orbitale détaillée. Aucune simulation n’est substituée pour fermer artificiellement ce problème inverse. |

## Règle de lecture

Un calcul exploratoire ne devient pas une preuve certifiée par sa simple présence dans ce registre. `C-MAT-MEM-05` reste négatif, M2 reste non réussi, et `C-AST-01` reste limité au niveau modèle. Les ponts vers la théorie de la viabilité, la PID, la mécanique computationnelle, COT, CCM, LTEE et Assembly Theory sont des extensions méthodologiques ou des analyses supplémentaires. La généalogie cosmique est soumise à un pare-feu empirique propre : aucune simulation, donnée synthétique ou sortie de modèle n'entre dans ses claims. Ses 15 résultats soutenus sont des extensions empiriques initiales non préenregistrées ; la trajectoire orbitale unique reste ouverte et C-AST demeure séparé au niveau modèle.
