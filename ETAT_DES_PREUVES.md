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
| `C-GC-E14` | extension_empirique_non_preregistered | supports_planet_specific_accretion_histories | planetary_isotope_reconstruction_plus_observed_endpoint — Mars conserve une contrainte temporelle Hf-W-Th et la Terre plusieurs contraintes Mo. Les reconstructions de provenance terrestre sont désormais explicitement contradictoires: ORI-C conserve ce conflit au lieu de choisir une histoire. Les scénarios orbitaux restent exclus. |
| `C-GC-E15` | extension_empirique_non_preregistered | supports_empirical_historical_accessibility_mechanism | cross_domain_empirical_synthesis — Synthèse initiale non préenregistrée. Le verdict est calculé à partir des quatorze résultats locaux précédents. Il porte sur le mécanisme de transmission historique, pas sur une loi universelle ni sur une trajectoire cosmologique/orbitale unique. |
| `C-GC-E16` | ouvert_empirique | undetermined_empirical_only | explicit_limit — Les archives empiriques atteignent l’architecture présente et contraignent des histoires de croissance, mais elles ne sélectionnent pas une unique trajectoire orbitale détaillée. Aucune simulation n’est substituée pour fermer artificiellement ce problème inverse. |
| `GCQ-T09` | extension_quantitative_empirique_non_preregistered | supports_strong_time_dependence_of_radiogenic_accessibility | quantitatif empirique rétrospectif — sans simulation/synthétique/imputation |
| `GCQ-T10` | extension_quantitative_empirique_non_preregistered | supports_earlier_differentiation_archive_during_higher_26Al_inventory | quantitatif empirique rétrospectif — sans simulation/synthétique/imputation |
| `GCQ-T11` | extension_quantitative_empirique_non_preregistered | supports_persistent_isotopic_architecture_across_large_inventory_change | quantitatif empirique rétrospectif — sans simulation/synthétique/imputation |
| `GCQ-T12` | extension_quantitative_empirique_non_preregistered | supports_gigayear_material_memory_carrier | quantitatif empirique rétrospectif — sans simulation/synthétique/imputation |
| `GCQ-T13` | extension_quantitative_empirique_non_preregistered | supports_late_reactivation_of_old_material_memory_by_unresolved_later_process | quantitatif empirique rétrospectif — sans simulation/synthétique/imputation |
| `GCQ-T14` | extension_quantitative_empirique_non_preregistered | contested_not_closed | quantitatif empirique rétrospectif — sans simulation/synthétique/imputation |
| `GCQ-T15` | extension_quantitative_empirique_non_preregistered | endpoint_quantified_history_not_reconstructed | quantitatif empirique rétrospectif — sans simulation/synthétique/imputation |
| `GCQ-T16` | extension_quantitative_empirique_non_preregistered | strict_stellar_to_endpoint_chain_exists_but_primordial_end_to_end_closure_open | quantitatif empirique rétrospectif — sans simulation/synthétique/imputation |
| `GCQ-X01` | controle_quantitatif_empirique_posthoc | canonical_decay_curve_is_time_reference_not_unique_local_inventory | contrôle post-hoc déterministe — non compté parmi les tests gelés |
| `GCQ-T17` | extension_quantitative_empirique_data_rich_non_preregistered | supports_published_presolar_grain_population_structure | distributions réelles grain/échantillon — sans simulation/synthétique/imputation ni double comptage de formats |
| `GCQ-T18` | extension_quantitative_empirique_data_rich_non_preregistered | supports_multisystem_NC_CC_isotopic_separation | distributions réelles grain/échantillon — sans simulation/synthétique/imputation ni double comptage de formats |
| `GCQ-T19` | extension_quantitative_empirique_data_rich_non_preregistered | supports_within_meteorite_chondrule_isotopic_heterogeneity | distributions réelles grain/échantillon — sans simulation/synthétique/imputation ni double comptage de formats |
| `GCQ-T20` | extension_quantitative_empirique_data_rich_non_preregistered | supports_within_meteorite_subsample_Ti_heterogeneity | distributions réelles grain/échantillon — sans simulation/synthétique/imputation ni double comptage de formats |
| `GCQ-T21` | extension_quantitative_empirique_data_rich_non_preregistered | supports_returned_sample_multiscale_isotopic_heterogeneity | distributions réelles grain/échantillon — sans simulation/synthétique/imputation ni double comptage de formats |

## Règle de lecture

Un calcul exploratoire ne devient pas une preuve certifiée par sa simple présence dans ce registre. `C-MAT-MEM-05` reste négatif, M2 reste non réussi, et `C-AST-01` reste limité au niveau modèle. Les ponts vers la théorie de la viabilité, la PID, la mécanique computationnelle, COT, CCM, LTEE et Assembly Theory sont des extensions méthodologiques ou des analyses supplémentaires. La généalogie cosmique est soumise à un pare-feu empirique propre : aucune simulation, donnée synthétique ou sortie de modèle n'entre dans ses claims. Ses 15 résultats empiriques soutenus restent des extensions initiales non préenregistrées. Les huit claims `GCQ-T09` à `GCQ-T16` sont des extensions quantitatives empiriques rétrospectives : ils quantifient notamment l'inventaire radiogénique accessible et les verrous de chaîne, sans certifier une trajectoire orbitale unique ni fermer artificiellement la chaîne primordiale→présent. `GCQ-X01` est explicitement un contrôle post-hoc montrant que la courbe canonique de décroissance ne constitue pas un inventaire local unique. Les claims `GCQ-T17` à `GCQ-T21` ajoutent une couche data-rich fondée sur des distributions grain/échantillon publiées et mesurées; les lignes PGD non publiées, valeurs synthétiques, imputations et doublons de format sont exclus. C-AST demeure séparé au niveau modèle.
