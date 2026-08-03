from pathlib import Path

from oric_full.provenance import build_manifest, verify_manifest


def test_manifest_roundtrip(tmp_path: Path):
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    build_manifest(tmp_path, manifest)
    assert verify_manifest(tmp_path, manifest)["ok"]
    (tmp_path / "a.txt").write_text("changed", encoding="utf-8")
    result = verify_manifest(tmp_path, manifest)
    assert not result["ok"]
    assert "a.txt" in result["modified"]
