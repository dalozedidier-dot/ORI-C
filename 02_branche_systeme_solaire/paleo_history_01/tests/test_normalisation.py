from __future__ import annotations

import importlib.util
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("paleo_normalize", HERE / "normaliser_donnees.py")
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


def test_neuf_familles_sont_parsees() -> None:
    datasets = MOD.parse_all()
    assert set(datasets) == {
        "LR04", "pile_benthique_independante", "proxy_niveau_marin_independant",
        "EPICA_temperature", "EPICA_CO2", "EPICA_poussieres", "Vostok",
        "insolation_convention_1", "insolation_convention_2",
    }
    assert all(rows for rows in datasets.values())


def test_aucune_erreur_de_proxy_n_est_rebaptisee_erreur_d_age() -> None:
    datasets = MOD.parse_all()
    observed = [rows for name, rows in datasets.items() if not name.startswith("insolation_")]
    assert all(row["age_uncertainty_ka"] == "" for rows in observed for row in rows)
    assert all("age_uncertainty_unavailable" in row["quality_flag"] for rows in observed for row in rows)


def test_age_et_empreinte_sont_tracees() -> None:
    for rows in MOD.parse_all().values():
        assert all(0 <= float(row["age_ka_bp"]) <= 800 for row in rows)
        assert all(len(row["sha256_source"]) == 64 for row in rows)
