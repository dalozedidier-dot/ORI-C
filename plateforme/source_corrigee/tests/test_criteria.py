from pathlib import Path

from oric_full.criteria import CriteriaRegistry, evaluate_criterion, write_criteria_template
from oric_full.models import ScientificVerdict
from oric_full.registry import Registry


def test_criteria_are_separate_from_technical_status(tmp_path: Path):
    specs = Registry.load().all()[:2]
    path = write_criteria_template(specs, tmp_path / "criteria.csv")
    registry = CriteriaRegistry.load(path)
    assert registry.get(specs[0].test_id) is None  # template has no metric yet
    verdict, value, criterion_id = evaluate_criterion(None, {"score": 1.0}, 1.0)
    assert verdict == ScientificVerdict.UNDETERMINED
    assert value is None
    assert criterion_id is None
