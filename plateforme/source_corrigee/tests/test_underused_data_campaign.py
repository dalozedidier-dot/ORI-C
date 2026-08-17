from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CAMPAIGN = ROOT / "plateforme" / "campagne_maximale_reelle"
if str(CAMPAIGN) not in sys.path:
    sys.path.insert(0, str(CAMPAIGN))

from analyser_donnees_sous_exploitees import (  # noqa: E402
    DEFAULT_OUTPUT,
    _compare,
    compute_all,
)


@pytest.fixture(scope="session")
def result() -> dict:
    """Recalcule toute la campagne une seule fois pour la suite."""
    return compute_all()


def test_sortie_versionnee_est_reproductible(result: dict) -> None:
    expected = json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8"))
    errors = _compare(expected, result)
    assert not errors, "\n".join(errors[:50])


def test_aucun_resultat_retrospectif_ne_gagne_de_credit_xiv(result: dict) -> None:
    assert result["transversal_conclusion"]["section_XIV"] == {
        "passed": 7,
        "total": 12,
        "unchanged": True,
    }
    assert all(
        analysis["section_XIV_credit"] is False
        for analysis in result["analyses"].values()
    )



def test_benchmark_transversal_declenche_stress_tests_sans_devenir_preuve(
    result: dict,
) -> None:
    analysis = result["analyses"]["transversal_derived_benchmark"]
    assert analysis["rows"] == 17_506
    domains = analysis["domains"]
    assert len(domains) >= 6
    assert domains["orbital"]["balanced_accuracy_gain_pp"] > 10.0
    assert domains["antibiotic_longitudinal"]["balanced_accuracy_gain_pp"] > 5.0
    assert analysis["section_XIV_credit"] is False

def test_stress_de_completude_de_X_antibiotique(result: dict) -> None:
    analysis = result["analyses"]["antibiotic_state_history"]
    assert analysis["rows"] >= 500
    assert analysis["lineages"] >= 150
    # Une histoire plus profonde ne doit pas être appelée "mémoire
    # irréductible" si elle ne bat pas un état X enrichi.
    assert analysis["relative_gain_percent"] <= 0.5


def test_vesicules_parent_informatif_histoire_profonde_non_irreductible(
    result: dict,
) -> None:
    analysis = result["analyses"]["vesicle_state_history"]
    assert analysis["rows"] >= 5_000
    assert analysis["parent_state_gain_percent"] > 5.0
    assert analysis["deeper_ancestry_gain_after_parent_percent"] < 1.0


def test_paleoclimat_garde_semantique_et_changement_de_regime(result: dict) -> None:
    analysis = result["analyses"]["paleoclimate_regime"]
    assert "not a physical forcing" in analysis["semantic_guard"]["forcing_1"]
    assert "not an age uncertainty" in analysis["semantic_guard"]["forcing_2"]
    assert analysis["late_over_early_ratio"] > 5.0
    low, high = analysis["proxy_error_monte_carlo_95_late_over_early"]
    assert low > 5.0
    assert high > low


def test_climat_moderne_dependance_de_route_reste_sortie_de_modele(
    result: dict,
) -> None:
    analysis = result["analyses"]["modern_climate_path"]
    at_2c = analysis["matched_global_warming_levels"]["2.0"]
    assert analysis["models"] >= 8
    assert at_2c["n_models"] >= 8
    assert at_2c["bootstrap95"][0] > 0.0
    assert analysis["section_XIV_credit"] is False


def test_reconstructions_climatiques_observationnelles_sont_coherentes(
    result: dict,
) -> None:
    analysis = result["analyses"]["modern_climate_reconstruction_agreement"]
    assert analysis["common_annual_years"] >= 130
    assert analysis["hadcrut5_vs_gistemp_combined_correlation"] > 0.98
    trends = analysis["trend_1970_2020"]
    assert all(0.15 < value["C_per_decade"] < 0.25 for value in trends.values())


def test_nucleosynthese_sensible_a_architecture_des_modeles(result: dict) -> None:
    analysis = result["analyses"]["nucleosynthesis_architecture"]
    fractions = analysis["median_log_yield_variance_fraction"]
    assert analysis["complete_balanced_elements"] >= 40
    assert fractions["model_family"] > 3.0 * fractions["mass"]
    assert analysis["elements_where_mass_fraction_exceeds_family_fraction"] == 0


def test_rendements_isotopiques_reconstruisent_les_rendements_elementaires(
    result: dict,
) -> None:
    analysis = result["analyses"]["nucleosynthesis_isotope_consistency"]
    assert analysis["isotope_rows"] >= 50_000
    assert analysis["element_rows_compared"] >= 1_300
    assert analysis["fraction_below_1e_minus_6"] == pytest.approx(1.0)
    assert analysis["median_relative_difference_lt_1e_minus_9"] is True
    assert analysis["max_relative_difference_lt_1e_minus_6"] is True


def test_reseaux_astochimiques_partagent_une_architecture_robuste(
    result: dict,
) -> None:
    analysis = result["analyses"]["astrochemical_network_robustness"]
    assert analysis["species"]["common"] >= 400
    assert analysis["common_species_directed_edges"]["jaccard"] > 0.5
    assert analysis["degree_rank_spearman"]["rho"] > 0.8


def test_inventaire_moleculaire_est_compatible_avec_umist_sans_surqualification(
    result: dict,
) -> None:
    analysis = result["analyses"]["molecular_inventory_network_coverage"]
    assert analysis["inventory_species"] == 19
    assert analysis["network_coverage"]["UMIST_RATE22"]["fraction"] == pytest.approx(
        1.0
    )
    assert analysis["network_coverage"]["KIDA_UVA_2024"]["present"] == 15
    assert analysis["present_in_both_networks"] == 15
    assert analysis["inventory_uncertainty_nonmissing_fraction"] == 0.0


def test_georoc_fingerprint_hors_reference_sans_faux_modele_de_melange(
    result: dict,
) -> None:
    analysis = result["analyses"]["late_accretion_fingerprint"]
    assert analysis["rows"] == 122_159
    assert analysis["unique_sample_ids"] == 56_614
    assert analysis["sample_ids_excluded_missing_candidate_source"] >= 1
    assert analysis["ambiguous_sample_ids_across_metadata"] >= 1
    chance = analysis["chance_balanced_accuracy"]
    full = analysis["balanced_accuracy_by_feature_count"]["10"][
        "balanced_accuracy"
    ]
    assert full > 2.5 * chance
    assert analysis["uncertainty_nonmissing_fraction"] == 0.0


def test_partage_carbone_generalise_mieux_que_moyenne_inter_source(
    result: dict,
) -> None:
    analysis = result["analyses"]["partition_cross_source"]
    assert analysis["carbon_complete_rows"] >= 30
    assert analysis["sources"] >= 6
    assert analysis["relative_gain_vs_mean_baseline_percent"] > 10.0


def test_inventaires_volatils_restent_ouverts(result: dict) -> None:
    analysis = result["analyses"]["volatile_inventory"]
    assert analysis["fully_closed_rows"] == 0
    assert analysis["rows_with_initial_mass"] > 0
    assert analysis["scenarios_with_known_components_exceeding_initial"] > 0


def test_grille_thermochimique_contient_des_basculements_de_phase(
    result: dict,
) -> None:
    analysis = result["analyses"]["thermochemical_phase_competition"]
    assert analysis["rows"] >= 60_000
    assert analysis["crystalline_compositions"] >= 600
    assert analysis["compositions_with_multiple_G_minimum_winners"] >= 40
    assert len(analysis["examples"]["SiO2"]) >= 4


def test_murchison_est_sensible_au_regime_de_contrainte(result: dict) -> None:
    analysis = result["analyses"]["murchison_constraint_sensitivity"]
    js = analysis["jensen_shannon"]
    assert js["vacuum_vs_intermediate"]["mean_bits"] > 0.5
    assert js["vacuum_vs_strong"]["mean_bits"] > 0.5
    assert js["intermediate_vs_strong"]["mean_bits"] < 0.1


def test_meteorites_reponse_pression_depend_de_porosite(result: dict) -> None:
    analysis = result["analyses"]["meteorite_environment_response"]
    rho = analysis["spearman_porosity_vs_vacuum_over_ambient_conductivity"]
    assert analysis["paired_samples"] >= 40
    assert rho["rho"] < -0.9
    assert rho["bootstrap95_rho"][1] < -0.8
    assert analysis["median_vacuum_over_ambient_conductivity_ratio"] < 0.8


def test_exoplanetes_multiplicite_apporte_information_hors_hote(
    result: dict,
) -> None:
    analysis = result["analyses"]["exoplanet_architecture"]
    assert analysis["rows"] >= 4_000
    assert analysis["hosts"] >= 3_000
    assert analysis["relative_rmse_gain_percent"] > 1.0
    assert analysis["section_XIV_credit"] is False


def test_trajectoires_arn_divergent_fortement(result: dict) -> None:
    analysis = result["analyses"]["rna_route_divergence"]
    seq5 = analysis["Seq5_round8_over_round1"]
    assert analysis["rows"] == 80
    assert seq5["71-89"] > 100.0
    assert seq5["52-2"] < 0.01
    assert analysis["jensen_shannon_divergence_bits_by_round"]["8"] > 0.4


def test_DH_reste_un_traceur_probabiliste_avec_incertitudes_partielles(
    result: dict,
) -> None:
    analysis = result["analyses"]["isotope_dh_overlap"]
    assert analysis["rows"] == 362
    assert analysis["groups_total"] == 85
    assert 0.5 < analysis["uncertainty_nonmissing_fraction"] < 0.8
    assert analysis["median_DH"]["Comets"] > analysis["median_DH"]["EC"]


def test_nbody_a_un_horizon_de_validite_et_precession_non_equivalente(
    result: dict,
) -> None:
    analysis = result["analyses"]["orbital_validity_horizon"]
    horizons = analysis["eccentricity_cumulative_rmse_threshold_horizons_ka"]
    assert 500 <= horizons["0.001"] <= 2_000
    assert horizons["0.005"] > horizons["0.001"]
    assert analysis["precession_cumulative_rmse_0p1rad_first_horizon_ka"] <= 10


def test_pgn_reste_un_resultat_structurel_descriptif(result: dict) -> None:
    analysis = result["analyses"]["aphid_pgn_structure"]
    assert analysis["hosts"] >= 20
    assert analysis["gene_families"] >= 10
    assert analysis["highest_presence_families"]["i-lys"] == pytest.approx(1.0)
    assert analysis["section_XIV_credit"] is False

def test_mesures_auxiliaires_vesicules_sont_informatives_mais_non_portables(
    result: dict,
) -> None:
    analysis = result["analyses"]["vesicle_auxiliary_portability"]
    assert analysis["log_rows"] == 19_392
    assert analysis["log_source_files"] == 8
    assert analysis["measurements_spanning_all_log_files"] == []
    measurements = analysis["measurements"]
    assert measurements["pre_amphiphile_turbidity_A400"]["source_files"] == 2
    assert measurements["pre_amphiphile_turbidity_A400"][
        "overall_spearman_rho"
    ] > 0.5
    assert measurements["nile_red_fluorescence"]["source_files"] == 1
    food = measurements["food_vesicle_turbidity_A400"]
    assert food["source_files"] == 6
    lo, hi = food["per_file_rho_range"]
    assert hi - lo > 0.3
    assert analysis["fig3_before_after_distribution_tests"]["Turbidity"][
        "p_two_sided"
    ] < 1e-10
    assert analysis["section_XIV_credit"] is False


def test_couverture_exhaustive_des_44_csv_canoniques(result: dict) -> None:
    coverage = result["dataset_coverage"]
    assert coverage["canonical_csv_count"] == 44
    assert coverage["consumed_csv_count"] == 44
    assert coverage["uncovered"] == []
    assert all(coverage["used_by"].values())


def test_design_antibiotique_raccorde_exactement_aux_trajectoires(result: dict) -> None:
    analysis = result["analyses"]["antibiotic_design_coverage"]
    assert analysis["design_cells"] == 10
    assert analysis["declared_replicates_total"] == 203
    assert analysis["observed_unique_lineages"] == 203
    assert analysis["cells_with_exact_replicate_count"] == 10
    assert analysis["cells_with_exact_cycle_bounds"] == 10


def test_fitness_reelle_ancetre_evoluee_est_exploitee_sans_surcredit(result: dict) -> None:
    analysis = result["analyses"]["antibiotic_real_fitness"]
    assert analysis["rows"] == 72
    assert analysis["complete_rows"] == 66
    assert analysis["missing_paired_rows"] == 6
    assert analysis["overall_positive_fraction"] > 0.7
    assert analysis["by_limitation"]["Nitrogen"]["mean_change"] > analysis["by_limitation"]["Carbon"]["mean_change"]
    assert analysis["section_XIV_credit"] is False


def test_biology_cases_est_audite_comme_table_derivee(result: dict) -> None:
    analysis = result["analyses"]["biology_case_integrity"]
    assert analysis["rows"] == 14_777
    assert analysis["case_id_duplicates"] == 0
    assert set(analysis["domains"]) == {"vesicle", "antibiotic", "antibiotic_longitudinal", "rna_evolution"}
    assert 0.0 < analysis["fraction_test_feature_tuples_seen_in_train"] < 0.2


def test_architecture_cellulaire_reste_descriptive(result: dict) -> None:
    analysis = result["analyses"]["cell_architecture_scope"]
    assert analysis["rows"] == 13
    assert analysis["dependency_nonmissing"] == 0
    assert analysis["confirmed_fraction"] == pytest.approx(1.0)
    assert analysis["evidence_level_counts"] == {"3": 13}


def test_modeles_H_C_quantifient_une_forte_dispersion_de_scenario(result: dict) -> None:
    analysis = result["analyses"]["core_bulk_hc_model_spread"]
    assert analysis["rows"] == 3
    assert analysis["largest_fold_spread"] > 5.0
    assert len(analysis["core_C_over_H_ratios"]["this_study_C_over_H_core"]) == 3


def test_matrice_endosymbiotique_complete_confirme_reduction_modulaire(result: dict) -> None:
    analysis = result["analyses"]["endosymbiosis_full_matrix"]
    assert analysis["hmm_rows"] == 15_810
    assert analysis["events"] == 85
    assert analysis["matched_accessions"] == 85
    retention = analysis["section_retention_mean"]
    assert retention["translation"] > retention["transcription"] > retention["envelope"]
    assert analysis["metabolic_integration_vs_global_retention_spearman"]["rho"] > 0.95


def test_ephemerides_et_conditions_initiales_sont_identiques(result: dict) -> None:
    analysis = result["analyses"]["ephemerides_initial_consistency"]
    assert analysis["matched_bodies"] == 15
    assert all(value == pytest.approx(0.0) for value in analysis["coordinate_max_abs_difference"].values())
    assert analysis["barycentric_position_norm"] < 1e-5


def test_ivuna_montre_heterogeneite_superieure_aux_incertitudes(result: dict) -> None:
    analysis = result["analyses"]["ivuna_cr_heterogeneity"]
    assert analysis["rows"] == 9
    assert analysis["I2"] > 0.8
    assert analysis["samples_more_than_3_sigma_from_weighted_mean"] >= 3


def test_calcium_lunaire_conserve_structure_de_groupe_sans_surinterpreter(result: dict) -> None:
    analysis = result["analyses"]["lunar_ca_group_structure"]
    assert analysis["rows"] == 13
    assert analysis["group_count"] == 4
    assert analysis["weighted_group_mean_span"] > 0.2


def test_graphe_transitions_relations_est_totalement_raccorde(result: dict) -> None:
    analysis = result["analyses"]["transition_relation_graph"]
    assert analysis["transitions"] == 40
    assert analysis["relations"] == 47
    assert analysis["relation_nodes_missing_from_transition_table"] == []
    assert analysis["nontrivial_strongly_connected_components"] == [["TR-029", "TR-038"]]
    assert analysis["is_acyclic"] is False


def test_compilation_acides_amines_est_exploitee_par_classe_environnementale(result: dict) -> None:
    analysis = result["analyses"]["amino_acid_inventory_structure"]
    assert analysis["rows"] == 1_387
    assert analysis["environments"] == 69
    assert analysis["species"] == 43
    assert analysis["uncertainty_nonmissing_fraction"] > 0.95
    assert analysis["richness_kruskal"]["p"] < 1e-5
    assert analysis["shannon_kruskal"]["p"] < 1e-6


def test_reference_orbitale_est_precise_mais_incertitude_sous_couvre(result: dict) -> None:
    analysis = result["analyses"]["orbital_reference_consistency"]
    assert analysis["reference_rows"] == 1_381
    assert analysis["common_rows"] == 1_381
    assert analysis["correlation"] > 0.9999
    assert analysis["eccentricity_rmse"] < 3e-5
    assert analysis["fraction_within_2_sigma"] < 0.6


def test_design_prebiotique_documente_exactement_son_perimetre(result: dict) -> None:
    analysis = result["analyses"]["prebiotic_design_coverage"]
    assert analysis["design_rows"] == 32
    assert analysis["condition_ids"] == analysis["lineage_condition_ids"] == 32
    assert analysis["conditions_missing_from_design"] == []
    assert analysis["design_conditions_without_lineages"] == []
    assert set(analysis["empty_mechanistic_factor_columns"]) == {"temperature", "ph", "wet_dry_cycles", "uv_flux", "mineral"}


def test_paires_parent_descendant_quantifient_continuite_et_heterogeneite(result: dict) -> None:
    analysis = result["analyses"]["parent_offspring_direct"]
    assert analysis["rows"] == 13_680
    assert analysis["source_files"] == 16
    assert analysis["overall_spearman"]["rho"] > 0.7
    assert analysis["by_condition_arm"]["UU:drift"]["rho"] > analysis["by_condition_arm"]["FR:drift"]["rho"]
    lo, hi = analysis["transition_rho_range"]
    assert lo < 0.0 < hi


def test_59328_mesures_reconstruisent_576_resumes(result: dict) -> None:
    analysis = result["analyses"]["timecourse_summary_consistency"]
    assert analysis["raw_rows"] == 59_328
    assert analysis["stored_summary_rows"] == 576
    assert analysis["rebuilt_summary_rows"] == 576
    assert analysis["matched_summary_rows"] == 576
    assert analysis["all_summary_metrics_reconstructed_within_1e_minus_12"] is True
    assert max(float(v) for v in analysis["max_abs_difference"].values()) <= 1e-12


def test_couverture_csv_reelle_du_depot_ne_laisse_aucun_orphelin(result: dict) -> None:
    central = result["dataset_coverage"]
    assert central["canonical_csv_count"] == 44
    assert central["consumed_csv_count"] == 44
    assert central["uncovered"] == []
    repo = result["repository_real_data_csv_coverage"]
    assert repo["data_path_csv_total"] == 110
    assert repo["central_directly_consumed"] == 44
    assert repo["branch_data_paths"] == 28
    assert repo["branch_direct_cross_analysed"] == 7
    assert repo["branch_already_consumed_by_dedicated_pipelines"] == 19
    assert repo["branch_duplicate_paths"] == 2
    assert repo["orphaned_real_data_paths"] == []


def test_jpl_horizons_valide_etat_initial_et_court_horizon(result: dict) -> None:
    analysis = result["analyses"]["jpl_cross_validation"]
    assert analysis["j2000_state_rows"] == 15
    assert analysis["matched_initial_condition_bodies"] == 15
    assert all(value == pytest.approx(0.0) for value in analysis["j2000_state_max_abs_difference"].values())
    assert analysis["earth_reference_rows"] == 61
    assert analysis["short_horizon_eccentricity_rmse"] < 5e-5
    assert analysis["short_horizon_eccentricity_correlation"] > 0.998


def test_archive_nasa_brute_est_tracee_dans_normalisation_exoplanetes(result: dict) -> None:
    analysis = result["analyses"]["nasa_archive_normalization"]
    assert analysis["raw_rows"] == 40_052
    assert analysis["normalized_rows"] == 6_333
    assert analysis["normalized_planets_missing_from_raw"] == []
    assert len(analysis["raw_planets_not_in_normalized"]) == 3
    assert analysis["system_planet_count_exact_match_fraction"] == pytest.approx(1.0)
    assert all(
        field["fraction"] == pytest.approx(1.0)
        for field in analysis["field_value_preservation"].values()
    )


def test_card2019_parent_daughter_est_exploite_sans_credit_prospectif(result: dict) -> None:
    analysis = result["analyses"]["card2019_parent_daughter"]
    assert analysis["rows"] == 130
    assert analysis["strains"] == 13
    assert analysis["row_level_daughter_over_parent_ratio_median"] == pytest.approx(2.0)
    assert analysis["row_fraction_daughter_gt_parent"] > 0.9
    assert analysis["section_XIV_credit"] is False


def test_santos_lopez_separe_resistance_directe_et_reponses_collaterales(result: dict) -> None:
    analysis = result["analyses"]["santos_lopez_cross_resistance"]
    assert analysis["raw_rows"] == 1_080
    assert analysis["numeric_rows"] == 540
    assert analysis["day12_population_level_ratios"] == 108
    assert analysis["direct_resistance_median_fold"] > 5.0
    assert analysis["direct_resistance_fraction_gt_1"] == pytest.approx(1.0)
    assert 0.5 < analysis["collateral_response_median_fold"] < 1.5
    assert analysis["collateral_fraction_lt_1"] > 0.2
    assert analysis["collateral_fraction_gt_1"] > 0.4


def test_partage_carbone_brut_est_normalise_sans_perte_sur_champs_coeur(result: dict) -> None:
    analysis = result["analyses"]["carbon_partition_raw_normalization"]
    assert analysis["raw_source_blocks"] == 7
    assert analysis["raw_numeric_carbon_records_extracted"] == 32
    assert analysis["normalized_carbon_records_from_raw_file"] == 32
    assert analysis["exact_records_on_core_fields"] == 32
    assert analysis["exact_record_fraction"] == pytest.approx(1.0)
    assert max(analysis["max_abs_difference_core_fields"].values()) == pytest.approx(0.0)


def test_resolution_etat_X_distingue_signal_historique_et_etat_enrichi(result: dict) -> None:
    analysis = result["analyses"]["state_enrichment_resolution"]
    antibiotic = analysis["antibiotic"]
    vesicle = analysis["vesicle"]
    assert antibiotic["derived_X_history_gain_balanced_accuracy_pp"] > 5.0
    assert antibiotic["rich_X_previous_state_gain_percent"] <= 0.0
    assert antibiotic["history_survives_rich_X"] is False
    assert vesicle["parent_state_gain_percent"] > 5.0
    assert vesicle["deeper_history_survives_parent_state"] is False
    assert analysis["section_XIV_credit"] is False


def test_profondeur_temporelle_separe_parent_et_ascendance_profonde(result: dict) -> None:
    analysis = result["analyses"]["temporal_depth_resolution"]
    assert analysis["effective_depth_class"] == "immediate_parent_dominated"
    assert analysis["transition_count"] == 20
    assert analysis["positive_transition_count"] > 0
    assert analysis["negative_transition_count"] > 0
    assert analysis["overall_to_median_transition_abs_ratio"] > 2.0
    assert analysis["aggregation_guard_triggered"] is True


def test_espace_accessible_est_vectoriel_et_anisotrope(result: dict) -> None:
    analysis = result["analyses"]["accessible_space_geometry"]
    assert analysis["scalar_is_near_one"] is True
    assert analysis["vector_contains_contraction_and_expansion"] is True
    for route in analysis["routes"].values():
        assert len(route["median_fold_vector"]) == 3
        assert len(route["log2_fold_vector"]) == 3
        assert route["anisotropy_log2_span"] > 1.0
        assert route["max_over_min_fold_ratio"] > 3.0
    assert analysis["section_XIV_credit"] is False


def test_cibles_thermochimiques_preparent_un_solveur_de_surface(result: dict) -> None:
    analysis = result["analyses"]["thermochemical_threshold_targets"]
    assert analysis["crystalline_compositions"] >= 600
    assert analysis["multiwinner_compositions"] >= 40
    assert 0.0 < analysis["multiwinner_fraction"] < 0.2
    assert analysis["minimum_priority_candidates"] >= 4
    assert analysis["surface_solver_priority_candidates"][0]["composition"] == "SiO2"
    assert analysis["current_grid_is_full_multiphase_equilibrium"] is False


def test_enveloppe_orbitale_est_specifique_a_observable_et_precision(result: dict) -> None:
    analysis = result["analyses"]["orbital_validity_envelope"]
    horizons = analysis["eccentricity_rmse_budget_to_horizon_ka"]
    assert horizons["0.0001"] < horizons["0.001"] < horizons["0.005"]
    assert analysis["short_horizon_JPL_span_ka"] < horizons["0.0001"]
    assert analysis["short_horizon_JPL_rmse"] < 1e-4
    assert analysis["precession_0p1rad_horizon_ka"] <= 10.0
    assert analysis["uncertainty_envelope_calibrated_to_95_percent"] is False


def test_route_climatique_appariee_est_non_monotone(result: dict) -> None:
    analysis = result["analyses"]["climate_route_resolution"]
    assert analysis["warming_level_order_C"] == ["1.5", "2.0", "2.5", "3.0"]
    assert analysis["adjacent_sign_change_count"] >= 1
    assert analysis["nonmonotonic_route_response"] is True
    directions = {item["direction"] for item in analysis["bootstrap_excludes_zero"]}
    assert "positive" in directions
    assert "negative" in directions
    assert analysis["section_XIV_credit"] is False


def test_regime_murchison_separe_changement_de_domaine_et_intensite(result: dict) -> None:
    analysis = result["analyses"]["constraint_regime_resolution"]
    assert analysis["mean_vacuum_to_oxidising_JS_bits"] > 0.5
    assert analysis["intermediate_to_strong_JS_bits"] < 0.1
    assert analysis["major_to_within_oxidising_ratio"] > 5.0
    assert analysis["regime_separation_candidate"] is True
    assert analysis["section_XIV_credit"] is False
