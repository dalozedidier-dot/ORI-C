import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parents[1]
SCRIPT = HERE / "preparer_ves_pacc_int_01.py"
SPEC = importlib.util.spec_from_file_location("prep_ves", SCRIPT)
prep = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(prep)


def protocol():
    return json.loads((HERE / "PROTOCOLE_PACC_CAUSAL_PROSPECTIF_V1.json").read_text(encoding="utf-8"))


def make_tables(n=2):
    p = protocol()
    challenges = [x["id"] for x in p["Theta"]["challenge_set"]]
    parents = []
    arms = []
    responses = []
    for i in range(n):
        pid = f"P{i+1:02d}"
        parents.append({
            "parent_id": pid,
            "anchor_A400": "1.0",
            "anchor_NR640": "2.0",
            "anchor_NR_RATIO": "0.5",
            "anchor_CALCEIN": "0.8",
            "X_pH": "7.0",
            "X_temperature_C": "25.0",
            "X_total_amphiphile_mM": "100.0",
        })
        for arm, z, pdi in (("control", 300, 0.20), ("do_m", 110, 0.20), ("sham", 300, 0.20)):
            arms.append({
                "parent_id": pid,
                "arm": arm,
                "post_z_average_nm": str(z),
                "post_pdi": str(pdi),
                "post_pH": "7.0",
                "temperature_C": "25.0",
                "total_amphiphile_mM": "100.0",
                "final_volume_uL": "200.0",
                "elapsed_handling_min": "10.0",
            })
            for challenge in challenges:
                responses.append({
                    "parent_id": pid,
                    "arm": arm,
                    "challenge_id": challenge,
                    "A400": "1.1",
                    "NR640": "2.2",
                    "NR_RATIO": "0.55",
                    "CALCEIN": "0.88",
                })
    execution_log = {
        "m_targeted_only_confirmed_before_decoding": True,
        "responses_collected_after_intervention": True,
        "protocol_deviations": [],
        "randomization_seed_recorded": True,
        "blinding_preserved_until_analysis_table_freeze": True,
    }
    return parents, arms, responses, execution_log


def test_schema_reprend_exactement_les_defis_et_dimensions_du_protocole():
    p = protocol()
    schema = json.loads((HERE / "SCHEMA_ENTREE_VES_PACC_INT_01.json").read_text(encoding="utf-8"))
    assert schema["files"]["responses.csv"]["challenge_ids"] == [x["id"] for x in p["Theta"]["challenge_set"]]
    assert schema["files"]["responses.csv"]["response_dimension_order"] == [x["id"] for x in p["R"]["response_dimensions"]]


def test_preparation_construit_les_cubes_et_derive_les_gates_du_protocole():
    parents, arms, responses, execution_log = make_tables()
    cubes, meta = prep.prepare_tables(parents, arms, responses, execution_log, protocol())
    assert cubes["control_response"].shape == (2, 12, 4)
    assert cubes["intervention_response"].shape == (2, 12, 4)
    assert cubes["sham_response"].shape == (2, 12, 4)
    assert np.allclose(cubes["control_response"][0, 0], [1.1, 1.1, 1.1, 1.1])
    assert all(meta["matching"].values())
    assert meta["fidelity"]["do_m_population_target_passes"] is True
    assert meta["fidelity"]["sham_structural_fidelity_passes"] is True
    assert meta["strict_preparation_passes"] is True


def test_un_defi_manquant_est_refuse_fail_closed():
    parents, arms, responses, execution_log = make_tables()
    responses.pop()
    with pytest.raises(prep.InputError, match="structure incomplète"):
        prep.prepare_tables(parents, arms, responses, execution_log, protocol())


def test_preparation_reelle_reste_bloquee_sans_enregistrement_public():
    with pytest.raises(SystemExit, match="Preparation gate closed"):
        prep.registration_gate()


def test_deviation_procedurale_bloque_la_qualification_stricte():
    parents, arms, responses, execution_log = make_tables()
    execution_log["protocol_deviations"] = ["deviation_documentee"]
    _, meta = prep.prepare_tables(parents, arms, responses, execution_log, protocol())
    assert meta["matching"]["m_targeted_only"] is False
    assert meta["strict_preparation_passes"] is False
