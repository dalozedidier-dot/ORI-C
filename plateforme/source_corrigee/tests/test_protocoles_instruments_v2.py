from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CAMPAIGN = ROOT / "plateforme" / "campagne_maximale_reelle"
PLAN_DIR = ROOT / "plan_directeur"
CENTRAL_DIR = PLAN_DIR / "campagne_centrale_2026_08_11"
if str(CAMPAIGN) not in sys.path:
    sys.path.insert(0, str(CAMPAIGN))

from analyser_protocoles_instruments_v2 import PROTOCOL_DIR, compute_all_protocols  # noqa: E402


@pytest.fixture(scope="session")
def result() -> dict:
    return compute_all_protocols()


@pytest.fixture(scope="session")
def action_map() -> dict:
    return json.loads((PLAN_DIR / "XIV_OPEN_CONDITIONS_ACTION_MAP.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def inv_a() -> dict:
    return json.loads((CENTRAL_DIR / "INVARIANT_TRANSVERSAL_INV_A.json").read_text(encoding="utf-8"))


def test_les_sept_protocoles_sont_geles_et_sans_credit_xiv() -> None:
    expected = {
        "HMR-X-LADDER-001", "H-DEPTH-LADDER-001", "PACC-VECTOR-001",
        "THRESHOLD-SURFACE-001", "ORBIT-VALIDITY-ENVELOPE-001",
        "CLIMATE-MATCHED-STATE-FROZEN-001", "CONSTRAINT-REGIME-001",
    }
    files = {p.stem for p in PROTOCOL_DIR.glob("*.json")}
    assert files == expected
    for pid in expected:
        protocol = json.loads((PROTOCOL_DIR / f"{pid}.json").read_text(encoding="utf-8"))
        assert protocol["status"] == "frozen_v1"
        assert protocol["current_data_role"] == "retrospective_calibration_only"
        assert protocol["section_XIV_credit"] is False


def test_hmr_x_ladder_mesure_l_attenuation_du_signal_historique(result: dict) -> None:
    r = result["results"]["HMR-X-LADDER-001"]
    gains = [x["relative_RMSE_gain_percent"] for x in r["rungs"]]
    assert r["rows_common"] >= 500
    assert len(r["rungs"]) == 3
    assert gains[0] > gains[1] > gains[2]
    assert gains[0] > 2.0
    assert gains[2] <= 0.5
    assert r["gain_monotonically_decreases_with_X_richness"] is True
    assert r["richest_X_history_survives"] is False


def test_h_depth_ladder_utilise_un_echantillon_commun_et_mesure_quatre_profondeurs(result: dict) -> None:
    r = result["results"]["H-DEPTH-LADDER-001"]
    assert r["rows_common_through_depth4"] >= 1000
    assert [x["depth"] for x in r["levels"]] == [0,1,2,3,4]
    assert r["levels"][1]["incremental_gain_percent"] > 1.0
    assert all(x["incremental_gain_percent"] < 2.0 for x in r["levels"][2:])
    assert r["deeper_than_parent_adds_2pct_increment"] is False


def test_pacc_vector_detecte_ce_que_le_scalaire_masque(result: dict) -> None:
    r = result["results"]["PACC-VECTOR-001"]
    assert r["scalar_neutral"] is True
    assert r["mixed_expansion_and_contraction_within_route"] is True
    assert r["scalar_masking_detected"] is True
    assert r["route_L2_distance_log2"] > 1.0
    assert r["causal_Pacc_measured"] is False


def test_threshold_surface_localise_des_frontieres_avec_gap_reduit(result: dict) -> None:
    r = result["results"]["THRESHOLD-SURFACE-001"]
    assert set(r["compositions"]) == {"SiO2","Al2SiO5","MgSiO3","CaCO3"}
    assert r["all_priority_candidates_coherent"] is True
    for c in r["compositions"].values():
        assert c["boundary_edge_count"] >= 10
        assert c["boundary_to_interior_gap_ratio"] < 0.5
    assert r["full_multiphase_equilibrium_solved"] is False


def test_orbit_validity_envelope_separe_eccentricite_precession_et_calibration(result: dict) -> None:
    r = result["results"]["ORBIT-VALIDITY-ENVELOPE-001"]
    e = r["eccentricity_horizons_ka"]
    p = r["precession_horizons_ka"]
    assert e["0.0001"] < e["0.001"] < e["0.005"]
    assert p["0.1"] <= 10
    assert r["uncertainty_calibration"]["fraction_within_2sigma"] < 0.6
    assert r["uncertainty_calibration"]["empirical_95pct_sigma_multiplier"] > 5.0
    assert r["uncertainty_calibration"]["coverage_target_met"] is False


def test_climate_matched_state_est_gelé_sur_tous_les_niveaux_et_teste_leave_one_out(result: dict) -> None:
    r = result["results"]["CLIMATE-MATCHED-STATE-FROZEN-001"]
    assert r["eligible_models"] >= 8
    assert list(r["levels"]) == ["1.5","2.0","2.5","3.0"]
    assert r["adjacent_mean_sign_changes"] >= 1
    assert r["levels"]["2.0"]["robust_direction"] is True
    assert r["levels"]["3.0"]["robust_direction"] is True
    assert r["section_XIV_credit"] is False


def test_constraint_regime_est_paire_par_temperature_et_soutient_un_candidat_de_domaine(result: dict) -> None:
    r = result["results"]["CONSTRAINT-REGIME-001"]
    assert r["temperatures"] >= 30
    assert r["contrast_bootstrap95"][0] > 0.5
    assert r["positive_temperature_fraction"] == pytest.approx(1.0)
    assert r["wilcoxon_greater_p"] < 1e-6
    assert r["within_oxidising_mean_JS_bits"] < 0.1
    assert r["regime_separation_candidate"] is True
    assert r["empirical_causal_status"] is False


def test_compteur_xiv_reste_inchange(result: dict) -> None:
    assert result["section_XIV"] == {"passed":7,"total":12,"unchanged":True}
    assert all(x["section_XIV_credit"] is False for x in result["results"].values())



def test_action_map_post_v2_garde_exactement_les_cinq_verrous_sans_credit(action_map: dict) -> None:
    assert action_map["baseline"] == "7/12"
    assert set(action_map["open_conditions"]) == {"3", "4", "9", "10", "11"}
    assert action_map["post_v2_learning"]["baseline_remains"] == "7/12"
    assert action_map["post_v2_learning"]["open_conditions_remain"] == [3, 4, 9, 10, 11]
    assert action_map["post_v2_learning"]["section_XIV_credit_added"] == 0
    assert all(action_map["open_conditions"][i]["post_v2"]["section_XIV_credit"] is False for i in ["3", "4", "9", "10", "11"])


def test_condition_3_utilise_l_enveloppe_orbitale_pour_geler_la_prediction_pas_pour_la_crediter(action_map: dict, result: dict) -> None:
    d = action_map["open_conditions"]["3"]["post_v2"]
    r = result["results"]["ORBIT-VALIDITY-ENVELOPE-001"]
    assert d["findings"]["eccentricity_horizons_ka"] == r["eccentricity_horizons_ka"]
    assert d["findings"]["precession_horizons_ka"] == r["precession_horizons_ka"]
    assert d["findings"]["orbit_coverage_target_met"] is r["uncertainty_calibration"]["coverage_target_met"] is False
    assert d["direct_domain_use"] == {"ORBIT-VALIDITY-ENVELOPE-001": "systeme_solaire"}
    assert set(d["methodological_transfer_only"]) == {"HMR-X-LADDER-001", "H-DEPTH-LADDER-001"}


def test_condition_4_durcit_le_témoin_apparié_sans_le_rendre_applicable(action_map: dict, result: dict) -> None:
    d = action_map["open_conditions"]["4"]["post_v2"]
    h = result["results"]["HMR-X-LADDER-001"]
    c = result["results"]["CLIMATE-MATCHED-STATE-FROZEN-001"]
    reg = result["results"]["CONSTRAINT-REGIME-001"]
    assert d["findings"]["richest_X_history_survives"] is h["richest_X_history_survives"] is False
    assert d["findings"]["climate_adjacent_mean_sign_changes"] == c["adjacent_mean_sign_changes"]
    assert d["findings"]["constraint_regime_candidate"] is reg["regime_separation_candidate"] is True
    assert "same X richness and feature availability" in d["matched_control_gate"]
    assert "condition 4 stays not applicable" in d["remaining_lock"]


def test_condition_9_remplace_le_scalaire_par_un_pacc_structuré_et_garde_le_verrou_solaire(action_map: dict, result: dict) -> None:
    d = action_map["open_conditions"]["9"]["post_v2"]
    p = result["results"]["PACC-VECTOR-001"]
    assert d["findings"]["scalar_masking_detected"] is p["scalar_masking_detected"] is True
    assert d["findings"]["causal_Pacc_measured"] is p["causal_Pacc_measured"] is False
    assert "vector or local P_acc retained when scalar aggregation masks directions" in d["P_acc_future_gate"]
    assert "systeme_solaire real-system causal P_acc" in action_map["open_conditions"]["9"]["remaining_hard_lock"]


def test_condition_10_v2_ne_compte_jamais_comme_replication_independante(action_map: dict) -> None:
    d = action_map["open_conditions"]["10"]["post_v2"]
    assert d["replication_credit_from_v2"] is False
    assert d["section_XIV_credit"] is False
    assert "independent team and independently executed experiment or dataset acquisition" in d["replication_freeze_gate"]


def test_condition_11_et_inv_a_partagent_la_meme_regle_sans_classement_scalaire(action_map: dict, inv_a: dict) -> None:
    d = action_map["open_conditions"]["11"]["post_v2"]
    gate = inv_a["post_v2_comparability_gate"]
    assert d["common_decision_rule"] == gate["common_decision_rule"]
    assert d["cross_domain_raw_P_acc_comparison_allowed"] is False
    assert d["cross_domain_scalar_ranking_allowed"] is gate["cross_domain_scalar_ranking_allowed"] is False
    assert gate["applies_to_section_XIV_conditions"] == [9, 11]
    assert gate["requirements"]["structured_P_acc_required_if_scalar_masking_detected"] is True
    assert gate["requirements"]["same_decision_rule_version_across_branches"] is True
    assert gate["section_XIV_credit"] is False
    assert inv_a["current_claim"] == "no_general_transversal_invariant_validated"
