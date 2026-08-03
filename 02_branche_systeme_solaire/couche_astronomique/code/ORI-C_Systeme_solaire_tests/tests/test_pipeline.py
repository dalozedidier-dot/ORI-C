from pathlib import Path

from oric_solar_history.config import load_config
from oric_solar_history.experiment import run_experiment


def test_end_to_end_pipeline(tmp_path: Path):
    config = load_config("configs/smoke_surrogate.yaml")
    config["experiment"]["output_dir"] = str(tmp_path / "run")
    config["experiment"]["duration_years"] = 500_000
    config["spectrum"]["max_period_years"] = 400_000
    config["spectrum"]["red_noise_surrogates"] = 8
    run_dir = run_experiment(config)
    assert (run_dir / "comparison.csv").exists()
    assert (run_dir / "REPORT.md").exists()
    assert (run_dir / "manifest.json").exists()
    assert (run_dir / "baseline" / "orbits.csv").exists()
