from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "plateforme/campagne_maximale_reelle/data"


def test_scientific_bundle_tables_are_real_and_nontrivial() -> None:
    climate = pd.read_csv(DATA / "modern_climate_ensemble.csv")
    assert len(climate) == 142_745
    assert climate["model"].nunique() >= 80
    gistemp = climate[climate["model"] == "NASA_GISTEMP_observation"]
    assert not gistemp.empty
    assert gistemp["value"].between(-5.0, 5.0).all()

    network = pd.read_csv(DATA / "reaction_network.csv")
    assert len(network) == 16_434
    assert set(network["source_network"]) == {"KIDA_UVA_2024", "UMIST_RATE22"}

    inventory = pd.read_csv(DATA / "molecular_inventory.csv")
    assert len(inventory) == 19
    assert set(inventory["inventory_kind"]) == {"conserved", "parents"}

    yields = pd.read_csv(DATA / "nucleosynthesis_yields.csv")
    assert len(yields) == 1_383
    assert "A" not in set(yields["element"])
    assert yields["mass_solar"].nunique() == 3

    partition = pd.read_csv(DATA / "partition_experiments.csv")
    assert len(partition) == 41
    assert partition["source_file"].notna().sum() == 32
    assert len(
        partition.dropna(
            subset=["pressure_gpa", "temperature_k", "delta_iw", "logD"]
        )
    ) == 35


def test_bundle_coverage_stays_conservative() -> None:
    payload = json.loads((DATA / "REAL_DATA_COVERAGE.json").read_text(encoding="utf-8"))
    datasets = payload["datasets"]
    assert datasets["nucleosynthesis_yields"]["supported_test_ids"] == ["M2-004"]
    assert datasets["reaction_network"]["supported_test_ids"] == ["M3-001", "M3-011", "M3-015"]
    assert datasets["isotope_tracers"]["supported_test_ids"] == ["P1-001"]
    assert datasets["endosymbiosis_events"]["supported_test_ids"] == ["B2-003"]
    assert "CL3-008" not in datasets["modern_climate_ensemble"]["supported_test_ids"]
    assert "CL3-009" not in datasets["modern_climate_ensemble"]["supported_test_ids"]


def test_auxiliary_tables_do_not_replace_missing_canonical_contracts() -> None:
    for filename in (
        "thermochemical_phases.csv",
        "planetary_histories.csv",
        "late_accretion_tracers.csv",
        "volatile_inventory.csv",
    ):
        assert not (DATA / filename).exists()
