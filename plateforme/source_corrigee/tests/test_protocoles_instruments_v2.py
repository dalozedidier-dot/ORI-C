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

from analyser_protocoles_instruments_v2 import PROTOCOL_DIR, compute_all_protocols  # noqa: E402


@pytest.fixture(scope="session")
def result() -> dict:
    return compute_all_protocols()


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
