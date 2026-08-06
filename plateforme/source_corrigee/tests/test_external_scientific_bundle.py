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


def test_workflow_fallback_preserves_bundle_scope_and_carbon_extension(tmp_path: Path) -> None:
    """Le workflow doit rester strict même sans les archives brutes volumineuses."""
    import hashlib
    import importlib.util
    import sys

    campaign_dir = ROOT / "plateforme/campagne_maximale_reelle"
    sys.path.insert(0, str(campaign_dir))
    try:
        base_spec = importlib.util.spec_from_file_location(
            "oric_integrate_existing", campaign_dir / "integrer_donnees_existantes.py"
        )
        assert base_spec and base_spec.loader
        base_module = importlib.util.module_from_spec(base_spec)
        base_spec.loader.exec_module(base_module)

        lot_spec = importlib.util.spec_from_file_location(
            "oric_integrate_bundle", campaign_dir / "integrer_lot_scientifique_2026_08_05.py"
        )
        assert lot_spec and lot_spec.loader
        lot_module = importlib.util.module_from_spec(lot_spec)
        lot_spec.loader.exec_module(lot_module)
    finally:
        sys.path.pop(0)

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    base_summary = base_module.build_partition_experiments(data_dir)
    assert base_summary["rows"] == 9

    for filename in (
        "modern_climate_ensemble.csv",
        "reaction_network.csv",
        "molecular_inventory.csv",
        "nucleosynthesis_yields.csv",
        "nucleosynthesis_isotope_yields.csv",
        "isotope_tracers.csv",
        "endosymbiosis_events.csv",
        "endosymbiont_hmm_presence_absence.csv",
    ):
        (data_dir / filename).symlink_to(DATA / filename)

    original_raw = lot_module.RAW
    lot_module.RAW = tmp_path / "raw-bundle-absent"
    try:
        summaries, coverage = lot_module.integrate(data_dir)
        first_hash = hashlib.sha256((data_dir / "partition_experiments.csv").read_bytes()).hexdigest()
        _, second_coverage = lot_module.integrate(data_dir)
        second_hash = hashlib.sha256((data_dir / "partition_experiments.csv").read_bytes()).hexdigest()
    finally:
        lot_module.RAW = original_raw

    partition = pd.read_csv(data_dir / "partition_experiments.csv")
    assert len(partition) == 41
    assert summaries["partition_experiments_extension"]["complete_regression_rows"] == 35
    assert first_hash == second_hash
    assert coverage == second_coverage
    assert set(coverage) == {
        "modern_climate_ensemble",
        "reaction_network",
        "molecular_inventory",
        "nucleosynthesis_yields",
        "isotope_tracers",
        "partition_experiments",
        "endosymbiosis_events",
    }
    assert coverage["partition_experiments"]["supported_test_ids"] == [
        "P3-001", "P3-002", "P3-003", "P3-004", "P3-005"
    ]


def test_canonical_results_and_generated_bilan_match() -> None:
    result_dir = ROOT / "plateforme/campagne_maximale_reelle/resultats_integration_maximale"
    campaign = json.loads((result_dir / "results.json").read_text(encoding="utf-8"))
    assert campaign["counts"] == {
        "pass": 298,
        "fail": 0,
        "skip": 0,
        "blocked": 337,
        "error": 0,
        "not_run": 48,
    }
    bilan = (ROOT / "plateforme/campagne_maximale_reelle/BILAN_CANONIQUE.md").read_text(encoding="utf-8")
    assert "Réussites techniques : **298**" in bilan
    assert "Blocages : **337**" in bilan
    assert "Expériences de partage métal-silicate : **41**" in bilan


def test_workflow_does_not_overwrite_generated_bilan() -> None:
    workflow = (ROOT / ".github/workflows/analyse-donnees-reelles.yml").read_text(encoding="utf-8")
    assert "resumer_integration_maximale.py" in workflow
    assert 'cp plateforme/campagne_maximale_reelle/BILAN_CANONIQUE.md "$OUT/resultats/"' not in workflow
    assert 'cp plateforme/campagne_maximale_reelle/AUDIT_DONNEES_DEPOT.md "$OUT/resultats/"' not in workflow
