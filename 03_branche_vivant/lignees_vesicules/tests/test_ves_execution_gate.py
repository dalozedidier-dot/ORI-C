from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]


def test_ves_execution_gate_valide_le_code_et_les_donnees_sans_bloquer_sur_osf():
    path = HERE / "valider_gate_ves_pacc_int_01.py"
    spec = importlib.util.spec_from_file_location("vgate", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    assert module.main() == 0


def test_ves_execution_package_does_not_change_scientific_protocol():
    execution = json.loads((HERE / "VES-PACC-INT-01.execution.json").read_text(encoding="utf-8"))
    assert execution["scientific_protocol_unchanged"] is True
    assert "public preregistration metadata in VES-PACC-INT-01.registration.json" not in execution["remaining_execution_blockers"]
    assert execution["external_registration_blocks_code"] is False
