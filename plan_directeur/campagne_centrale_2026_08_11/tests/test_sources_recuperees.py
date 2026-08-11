from __future__ import annotations

import json
from pathlib import Path


RESULT = Path(__file__).resolve().parents[1] / "resultats" / "INSPECTION_SOURCES_RECUPEREES_2026_08_12.json"


def load() -> dict:
    return json.loads(RESULT.read_text(encoding="utf-8"))


def test_les_sources_ne_ferment_pas_artificiellement_les_verrous() -> None:
    result = load()
    assert result["scientific_effect"] == {
        "material_complete_chains_admitted": 0,
        "hypergraph_canonical_closure": "46/53",
        "paleo_history_02": "non_testable",
    }


def test_u1506_replique_deux_modes_d_ablation_physique() -> None:
    result = load()["u1506"]
    assert result["qualification"] == "preuve_forte_ablation_physique_non_C03_complet"
    assert result["resultats"]["AF"]["series_decroissantes"] == 23
    assert result["resultats"]["thermal"]["series_decroissantes"] == 23


def test_farough_ne_demontre_pas_la_sortie_N030() -> None:
    result = load()["farough"]
    assert result["observations"] == 94
    assert result["qualification_H052"] == "ne_justifie_pas_le_reencodage_R1"
    assert all(row["rho_temps_permeabilite"] < 0 for row in result["experiences"])
    assert all(row["p_value"] != 0 for row in result["experiences"])


def test_u1537_identifie_cinq_echantillons_sans_doublon_de_casse() -> None:
    result = load()["u1537"]
    assert len(result["samples"]) == 5
