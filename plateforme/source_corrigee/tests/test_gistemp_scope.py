from pathlib import Path

from oric_full.data_registry import DataRegistry
from oric_full.engines import evaluate_engine
from oric_full.models import Outcome


def test_gistemp_uncertainty_is_not_treated_as_models_or_scenarios(tmp_path: Path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "modern_climate_ensemble.csv").write_text(
        "model,scenario,member,time,variable,value,region\n"
        "GISTEMP_v4,observational_uncertainty,1,2000,temperature_anomaly,0.4,global\n"
        "GISTEMP_v4,observational_uncertainty,2,2000,temperature_anomaly,0.5,global\n",
        encoding="utf-8",
    )
    registry = DataRegistry(data)
    assert evaluate_engine("modern_climate_pacc", registry).outcome == Outcome.BLOCKED
    assert evaluate_engine("modern_climate_validation", registry).outcome == Outcome.BLOCKED


def test_gistemp_trend_is_not_treated_as_recovery_or_hysteresis(tmp_path: Path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "modern_climate_timeseries.csv").write_text(
        "time,variable,value,region\n"
        "2000,temperature_anomaly,0.4,global\n"
        "2001,temperature_anomaly,0.5,global\n",
        encoding="utf-8",
    )
    registry = DataRegistry(data)
    assert evaluate_engine("modern_climate_memory", registry).outcome == Outcome.BLOCKED
    assert evaluate_engine("modern_climate_dhl", registry).outcome == Outcome.BLOCKED
