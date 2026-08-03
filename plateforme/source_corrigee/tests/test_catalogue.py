from pathlib import Path

from oric_full.audit import audit_platform
from oric_full.engines import SUPPORTED_ENGINES
from oric_full.registry import Registry


ROOT = Path(__file__).resolve().parents[1]


def test_catalogue_complete_and_unique():
    registry = Registry.load(ROOT / "catalogue" / "catalogue_tests.json")
    specs = registry.all()
    assert len(specs) == 683
    assert len({spec.test_id for spec in specs}) == 683
    assert len(registry.by_wp()) == 51
    assert {spec.engine for spec in specs} == SUPPORTED_ENGINES


def test_platform_audit_passes():
    report = audit_platform(ROOT)
    assert report.ok, report.to_dict()
