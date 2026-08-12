from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("do_m", HERE / "run_do_m.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_protocole_isole_m_et_garde_le_statut_modele() -> None:
    protocol = json.loads((HERE / "PROTOCOLE.json").read_text(encoding="utf-8"))
    assert protocol["status"] == "exploratory_frozen_for_reexecution_not_preregistered"
    assert protocol["evidence_level"] == "E4_modele"
    assert protocol["intervention"]["changes_X"] is False
    assert protocol["intervention"]["changes_architecture"] is False
    assert protocol["intervention"]["changes_future_forcing"] is False
    assert protocol["P_acc"]["denominator"] == 100
    assert protocol["P_acc"]["epsilon_acc"] == protocol["P_acc"]["resolution"]


def test_resultat_direct_do_m_est_apparie_et_fail_closed() -> None:
    result = json.loads((HERE / "resultats/RESULTAT_DO_M.json").read_text(encoding="utf-8"))
    assert result["evidence_level"] == "E4_modele"
    assert result["matching"]["X_exact_by_construction"] is True
    assert result["matching"]["same_architecture"] is True
    assert result["matching"]["same_future_forcing"] is True
    assert result["direct_INV_A_m_intervention"] is True
    p = result["P_acc"]
    assert p["sham_max_abs_Delta"] <= 1e-12
    expected = (
        p["abs_Delta_median"] >= p["epsilon_acc"]
        and p["abs_Delta_bootstrap_q025"] >= p["epsilon_acc"]
        and p["sham_max_abs_Delta"] <= 1e-12
    )
    assert result["direct_INV_A_support"] is expected
    assert "vrai Système solaire" in result["scope"]
