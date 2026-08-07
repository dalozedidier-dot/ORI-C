from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "plateforme" / "campagne_maximale_reelle" / "memoire_distribuee_gistemp.py"


def test_global_only_climate_table_blocks_zonal_cl1_without_error(tmp_path: Path):
    data = tmp_path / "data"
    out = tmp_path / "out"
    data.mkdir()
    (data / "modern_climate_timeseries.csv").write_text(
        "time,variable,value,region\n"
        "2000-01-15,surface_temperature_anomaly_C,0.1,global\n"
        "2001-01-15,surface_temperature_anomaly_C,0.2,global\n",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--data-dir",
            str(data),
            "--sortie",
            str(out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    report = json.loads((out / "memoire_distribuee_gistemp.json").read_text(encoding="utf-8"))
    assert report["status"] == "blocked"
    assert report["scientific_verdict"] == "undetermined"
    assert report["available_regions"] == ["global"]
    assert set(report["missing_regions"]) == {"NHem", "SHem", "64N-90N", "Glob"}
    assert "Aucun test CL1" in completed.stdout
