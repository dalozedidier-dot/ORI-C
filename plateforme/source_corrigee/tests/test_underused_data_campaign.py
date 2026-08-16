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
