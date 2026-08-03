# Matrice de couverture ORI-C

| WP | Entrées | Moteur | Modes | Jeux requis |
|---|---:|---|---|---|
| A1 | 10 | `astronomy_repro` | data_required:7, external_code:2, human_review:1 | orbital_initial_conditions |
| A2 | 10 | `astronomy_initial_conditions` | data_required:8, external_code:2 | ephemerides, orbital_initial_conditions |
| A3 | 16 | `astronomy_physics` | data_required:16 | orbital_initial_conditions |
| A4 | 12 | `astronomy_causality` | data_required:12 | orbital_initial_conditions |
| A5 | 10 | `astronomy_spectra` | data_required:9, human_review:1 | orbital_timeseries |
| A6 | 6 | `astronomy_validation` | data_required:3, external_code:1, human_review:2 | orbital_reference, orbital_timeseries |
| B1 | 10 | `cell_architecture` | data_required:9, human_review:1 | cell_architecture |
| B2 | 12 | `endosymbiosis` | data_required:12 | endosymbiosis_events |
| B3 | 10 | `biology_value` | data_required:9, human_review:1 | biology_cases |
| C1 | 10 | `paleoclimate_replication` | data_required:10 | paleoclimate_timeseries |
| C2 | 10 | `paleoclimate_prospective` | data_required:8, human_review:2 | paleoclimate_timeseries |
| C3 | 22 | `memory_families` | data_required:22 | paleoclimate_timeseries |
| C4 | 15 | `climate_models` | data_required:15 | paleoclimate_timeseries |
| C5 | 10 | `climate_data` | data_required:9, human_review:1 | paleoclimate_timeseries |
| C6 | 15 | `climate_discrimination` | data_required:15 | paleoclimate_timeseries |
| C7 | 10 | `climate_mechanisms` | data_required:10 | paleoclimate_timeseries |
| CL1 | 10 | `modern_climate_memory` | data_required:10 | modern_climate_timeseries |
| CL2 | 10 | `modern_climate_dhl` | data_required:9, human_review:1 | modern_climate_timeseries |
| CL3 | 10 | `modern_climate_pacc` | data_required:10 | modern_climate_ensemble |
| CL4 | 10 | `modern_climate_validation` | data_required:9, human_review:1 | modern_climate_ensemble |
| M1 | 15 | `matter_transitions` | data_required:14, human_review:1 | matter_transitions |
| M2 | 10 | `nucleosynthesis` | data_required:9, external_code:1 | nucleosynthesis_yields |
| M3 | 15 | `astrochemistry` | data_required:15 | molecular_inventory, reaction_network |
| M4 | 15 | `condensation` | data_required:15 | thermochemical_phases |
| M5 | 10 | `matter_value` | data_required:9, human_review:1 | matter_transitions |
| P1 | 10 | `planetary_provenance` | data_required:10 | isotope_tracers |
| P2 | 10 | `planetesimal_thermal` | data_required:10 | body_properties, chronometers |
| P3 | 15 | `metal_silicate` | data_required:15 | partition_experiments |
| P4 | 10 | `volatile_budget` | data_required:10 | volatile_inventory |
| P5 | 10 | `late_accretion` | data_required:10 | late_accretion_tracers |
| P6 | 12 | `planetary_value` | data_required:11, human_review:1 | planetary_histories |
| R1 | 10 | `antibiotic_design` | data_required:7, human_review:1, laboratory:2 | antibiotic_design |
| R2 | 15 | `antibiotic_histories` | data_required:11, laboratory:4 | antibiotic_cycles |
| R3 | 15 | `antibiotic_measurements` | data_required:14, laboratory:1 | antibiotic_measurements |
| R4 | 15 | `antibiotic_oric` | data_required:15 | antibiotic_cycles, antibiotic_measurements |
| R5 | 8 | `antibiotic_competitors` | data_required:8 | antibiotic_cycles, antibiotic_measurements |
| R6 | 8 | `antibiotic_replication` | data_required:4, laboratory:4 | antibiotic_measurements |
| S1 | 50 | `core_formal` | automated:47, data_required:1, human_review:2 | — |
| S2 | 20 | `intervention` | automated:15, laboratory:5 | — |
| S3 | 20 | `relation_graph` | data_required:16, human_review:4 | relations, states |
| T1 | 16 | `cross_domain_benchmark` | data_required:15, laboratory:1 | benchmark_cases |
| T2 | 10 | `generality` | data_required:9, human_review:1 | benchmark_cases |
| T3 | 10 | `predictive_value` | data_required:9, human_review:1 | benchmark_cases |
| T4 | 6 | `compression` | data_required:6 | benchmark_cases |
| T5 | 10 | `red_team` | data_required:9, human_review:1 | benchmark_cases |
| V1 | 10 | `prebiotic_design` | data_required:7, human_review:3 | prebiotic_design |
| V2 | 40 | `prebiotic_components` | data_required:39, laboratory:1 | prebiotic_lineages |
| V3 | 20 | `prebiotic_coupling` | data_required:19, laboratory:1 | prebiotic_lineages |
| V4 | 20 | `prebiotic_matrix` | data_required:20 | prebiotic_lineages |
| V5 | 10 | `prebiotic_space` | data_required:9, laboratory:1 | prebiotic_lineages |
| V6 | 10 | `prebiotic_transition` | data_required:9, laboratory:1 | prebiotic_lineages |