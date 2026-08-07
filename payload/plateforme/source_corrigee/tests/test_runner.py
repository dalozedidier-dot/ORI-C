from pathlib import Path

from oric_full.models import ScientificVerdict
from oric_full.registry import Registry
from oric_full.runner import RunOptions, run_campaign
from oric_full.synthetic_data import generate_all


def test_synthetic_fixture_blocks_real_observational_engine(tmp_path: Path):
    data_dir = tmp_path / "data"
    generate_all(data_dir, seed=9)
    campaign = run_campaign(
        Registry.load().all(),
        RunOptions(data_dir=data_dir, output_dir=tmp_path / "results", seed=9),
    )
    assert len(campaign.results) == 683
    assert campaign.counts["error"] == 0
    assert campaign.counts["fail"] == 0
    # Les anciens proxys `condensation` et `planetary_value` sont désormais
    # volontairement bloqués au lieu de produire un PASS technique trompeur.
    blocked = [result for result in campaign.results if result.outcome.value == "blocked"]
    blocked_engines = {result.details.get("engine") for result in blocked}
    assert {"condensation", "planetary_value"} <= blocked_engines
    assert campaign.counts["blocked"] >= 12
    assert campaign.scientific_counts[ScientificVerdict.UNDETERMINED.value] > 0


def test_real_only_blocks_generators(tmp_path: Path):
    data_dir = tmp_path / "data"
    generate_all(data_dir, seed=9)
    specs = [spec for spec in Registry.load().all() if spec.engine in {"core_formal", "prebiotic_design"}]
    campaign = run_campaign(specs, RunOptions(data_dir=data_dir, real_data_only=True))
    computational = [spec for spec in specs if spec.mode.value not in {"laboratory", "human_review", "external_replication"}]
    noncomputational = len(specs) - len(computational)
    assert campaign.counts["blocked"] == len(computational)
    assert campaign.counts["not_run"] == noncomputational
    assert all(
        result.details.get("real_data_only")
        for result in campaign.results
        if result.outcome.value == "blocked"
    )
