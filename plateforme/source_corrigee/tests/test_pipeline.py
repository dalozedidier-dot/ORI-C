from pathlib import Path

from oric_full.pipeline import bootstrap_workspace


def test_bootstrap_priority_one(tmp_path: Path):
    package_root = Path(__file__).resolve().parents[1]
    result = bootstrap_workspace(
        package_root,
        tmp_path / "workspace",
        seed=5,
        synthetic=True,
        max_priority=1,
    )
    assert result.tests > 0
    assert result.datasets == 33
    assert result.protocols > 0
    assert (result.workspace / "MANIFEST.sha256.json").exists()
    assert (result.workspace / "results" / "initial" / "REPORT.md").exists()
