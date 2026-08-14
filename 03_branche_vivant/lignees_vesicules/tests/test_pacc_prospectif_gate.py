import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]


def load_json(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_ves_pacc_int_01_ne_requalifie_pas_les_donnees_historiques():
    protocol = load_json("PROTOCOLE_PACC_CAUSAL_PROSPECTIF_V1.json")
    assert protocol["id"] == "VES-PACC-INT-01"
    assert protocol["prior_dataset"]["pairs_already_analysed"] == 11760
    assert protocol["prior_dataset"]["allowed_use"] == "calibration_and_design_only"


def test_design_scientifique_complet_et_fixe():
    protocol = load_json("PROTOCOLE_PACC_CAUSAL_PROSPECTIF_V1.json")
    power = load_json("POWER_PLAN.json")
    assert protocol["m"]["operator"]
    assert len(protocol["Theta"]["challenge_set"]) == 12
    assert len(protocol["R"]["response_dimensions"]) == 4
    assert protocol["P_acc"]["materiality_thresholds"] == [0.10, 0.10, 0.05, 0.10]
    assert protocol["P_acc"]["denominator_cells"] == 48
    assert protocol["independent_unit"]["planned_n"] == 48
    assert protocol["SESOI_and_power"]["SESOI_abs_Delta_P_acc"] == 0.08
    assert power["planned_n"] == 48
    assert power["target_power"] == 0.9
    assert protocol["preregistration_gate"]["scientific_fields_complete"] is True


def test_registration_sidecar_reste_coherent_sans_bloquer_le_calcul():
    registration = load_json("VES-PACC-INT-01.registration.json")
    protocol_path = HERE / "PROTOCOLE_PACC_CAUSAL_PROSPECTIF_V1.json"
    analysis_path = HERE / "analyser_ves_pacc_int_01.py"
    power_path = HERE / "POWER_PLAN.json"
    assert registration["source_sha256"] == sha256(protocol_path)
    assert registration["analysis_script_sha256"] == sha256(analysis_path)
    assert registration["power_plan_sha256"] == sha256(power_path)

    spec = importlib.util.spec_from_file_location("ves_pacc_analysis", analysis_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    metadata = module.external_registration_metadata()
    assert metadata["public_registration_complete"] is bool(
        registration.get("status") == "publicly_registered"
        and registration.get("public_url")
        and registration.get("registered_at")
    )


def test_power_plan_uses_independent_parent_units():
    plan = json.loads((HERE / 'POWER_PLAN.json').read_text(encoding='utf-8'))
    assert plan['analysis_frozen_before_data'] is True
    assert plan['independent_unit'] == 'parent vesicle population'
    assert plan['effect']['sesoi'] == 0.08
    assert plan['noise_estimation']['value'] == 0.15
    assert plan['available_n'] == 48
    assert plan['minimum_analyzable_n'] == 40
    assert plan['adapter']['path'].endswith('vesicle_pacc_paired_pipeline.py')
    assert plan['success_rule'] == ['paired_effect_detected']
