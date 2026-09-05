"""A numerical tolerance must never hide structural or scientific changes."""
import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("oric_checkup_portable", ROOT / "checkup_complet.py")
checkup = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = checkup
spec.loader.exec_module(checkup)


def test_roundoff_is_archived_before_reference_is_restored(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    reference = b'{"gain": 0.25, "status": "inconclusive", "n": 10}\n'
    candidate = b'{"gain": 0.2500000000000001, "status": "inconclusive", "n": 10}\n'
    (root / "result.json").write_bytes(candidate)
    output = tmp_path / "report"
    assert checkup.reconcile_numeric_outputs(root, {"result.json": reference}, output) == ["result.json"]
    assert (root / "result.json").read_bytes() == reference
    assert (output / "candidate/result.json").read_bytes() == candidate
    assert json.loads((output / "comparison.json").read_text())["errors"] == []


@pytest.mark.parametrize("candidate", [
    {"gain": 0.35, "status": "inconclusive", "n": 10},
    {"gain": 0.25, "status": "supports", "n": 10},
    {"gain": 0.25, "status": "inconclusive", "n": 11},
    {"gain": 0.25, "status": "inconclusive", "n": True},
    {"gain": 0.25, "n": 10},
    {"gain": float("nan"), "status": "inconclusive", "n": 10},
])
def test_scientific_or_structural_change_is_rejected(tmp_path, candidate):
    reference = b'{"gain": 0.25, "status": "inconclusive", "n": 10}\n'
    path = tmp_path / "result.json"
    data = json.dumps(candidate).encode()
    path.write_bytes(data)
    with pytest.raises(ValueError):
        checkup.reconcile_numeric_outputs(tmp_path, {path.name: reference}, tmp_path / "report")
    assert path.read_bytes() == data


def test_csv_header_changes_are_rejected_without_restoring_any_file(tmp_path):
    references = {"result.json": b'{"gain": 0.25}', "data.csv": b'label,value\na,0.25\n'}
    (tmp_path / "result.json").write_bytes(b'{"gain": 0.2500000000000001}')
    (tmp_path / "data.csv").write_bytes(b'other,value\na,0.25\n')
    with pytest.raises(ValueError):
        checkup.reconcile_numeric_outputs(tmp_path, references, tmp_path / "report")
    assert (tmp_path / "result.json").read_bytes() != references["result.json"]


def test_missing_candidate_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="absents"):
        checkup.reconcile_numeric_outputs(tmp_path, {"result.json": b'{}'}, tmp_path / "report")


def test_unlisted_files_remain_untouched(tmp_path):
    (tmp_path / "source.json").write_bytes(b'{"value": 999}')
    assert checkup.reconcile_numeric_outputs(tmp_path, {}, tmp_path / "report") == []
    assert (tmp_path / "source.json").read_bytes() == b'{"value": 999}'
