from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_registry_is_complete_and_https():
    registry = json.loads(
        (ROOT / "plan_directeur/campagne_recherche_suivante/sources_externes.json").read_text(
            encoding="utf-8"
        )
    )
    assert registry["schema"] >= 2
    assert len(registry["datasets"]) >= 3
    assert all(dataset["download_url"].startswith("https://") for dataset in registry["datasets"])
    assert all("doi" in dataset for dataset in registry["datasets"])
    assert all("provider" in dataset for dataset in registry["datasets"])
    assert all("download_strategy" in dataset for dataset in registry["datasets"])
    assert sum(bool(dataset.get("required_for_current_tests")) for dataset in registry["datasets"]) >= 2


def test_runner_and_workflow_exist():
    assert (ROOT / "plan_directeur/campagne_recherche_suivante/run_all.py").exists()
    assert (ROOT / ".github/workflows/recherche-suivante.yml").exists()


def test_external_data_are_not_claimed_as_oric_outputs():
    registry = json.loads(
        (ROOT / "plan_directeur/campagne_recherche_suivante/sources_externes.json").read_text(
            encoding="utf-8"
        )
    )
    assert "tierces" in registry["policy"]
    assert "ne sont pas assimilées" in registry["policy"]
    for dataset in registry["datasets"]:
        assert dataset.get("bundled_in_source") is True
        assert dataset.get("redistribute") is True
        assert dataset.get("license")
        source = ROOT / "donnees_externes" / dataset["id"] / "SOURCE.json"
        assert source.exists()
        provenance = json.loads(source.read_text(encoding="utf-8"))
        assert provenance["id"] == dataset["id"]
        assert provenance.get("doi") == dataset["doi"]
        assert len(provenance.get("sha256", "")) == 64


def test_acquisition_helpers_extract_and_hash(tmp_path):
    import importlib.util
    import zipfile

    module_path = ROOT / "plan_directeur/campagne_recherche_suivante/fetch_external_data.py"
    specification = importlib.util.spec_from_file_location("fetch_external_data", module_path)
    module = importlib.util.module_from_spec(specification)
    assert specification.loader is not None
    specification.loader.exec_module(module)
    archive = tmp_path / "fixture.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr("data/example.csv", "x,y\n1,2\n")
    extracted = module.extract(archive, tmp_path / "dataset")
    assert "data/example.csv" in extracted
    assert len(module.sha256(archive)) == 64
