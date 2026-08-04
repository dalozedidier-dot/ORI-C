import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_hysteresis_c3_publie_ses_sorties():
    out = ROOT / "results_stress" / "hysteresis_c3"
    payload = json.loads((out / "hysteresis_verdict.json").read_text(encoding="utf-8"))
    assert payload["status"].startswith("qualification exploratoire")
    assert len(payload["results"]) == 6
    assert (out / "basin_map.csv").stat().st_size > 100
