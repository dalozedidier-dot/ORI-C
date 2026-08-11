from pathlib import Path

import pandas as pd

from oric_solar_history.catalog import default_catalog_path, load_catalog
from oric_solar_history.config import load_config

ROOT = Path(__file__).resolve().parents[1]


def test_smoke_config_is_valid():
    config = load_config(ROOT / "configs" / "smoke_surrogate.yaml")
    assert config["experiment"]["backend"] == "surrogate"
    assert any(s["name"] == "baseline" for s in config["scenarios"])


def test_packaged_planetary_catalog_is_available():
    assert default_catalog_path().is_file()
    catalog = load_catalog()
    assert {"Earth", "Jupiter", "Saturn"} <= set(catalog)


def test_packaged_horizons_catalog_is_available():
    path = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "oric_solar_history"
        / "data"
        / "horizons_j2000_de441.csv"
    )
    frame = pd.read_csv(path)
    assert {
        "Sun",
        "Earth",
        "Pluto",
        "Ceres",
        "Pallas",
        "Vesta",
        "Iris",
        "Bamberga",
    } <= set(frame["name"])
