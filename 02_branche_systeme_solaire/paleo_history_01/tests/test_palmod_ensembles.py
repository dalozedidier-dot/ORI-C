import importlib.util
import io
import json
import zipfile
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "verifier_palmod_v2.py"
SPEC = importlib.util.spec_from_file_location("verifier_palmod_v2", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def _lpd(metadata, files=None):
    payload = io.BytesIO()
    with zipfile.ZipFile(payload, "w") as archive:
        archive.writestr("bag/data/metadata.jsonld", json.dumps(metadata))
        for name, content in (files or {}).items():
            archive.writestr(f"bag/data/{name}", content)
    return payload.getvalue()


def test_catalog_constructs_direct_ensemble_url(tmp_path):
    compilation = tmp_path / "PalMod.zip"
    metadata = {
        "datasetId": "abc",
        "dataSetName": "Core.Author.2026",
        "datasetVersion": "1.0.3",
        "lipdverseLink": "https://lipdverse.org/data/abc/1_0_3",
    }
    with zipfile.ZipFile(compilation, "w") as archive:
        archive.writestr("Core.Author.2026.lpd", _lpd(metadata))
    assert MODULE.build_ensemble_catalog(compilation)[0]["ensemble_url"] == (
        "https://lipdverse.org/data/abc/1_0_3/Core.Author.2026-ensemble.lpd"
    )


def test_ensemble_requires_depth_plus_1000_draws(tmp_path):
    ensemble = tmp_path / "Core.Author.2026-ensemble.lpd"
    row = ",".join(str(i) for i in range(1001)) + "\n"
    ensemble.write_bytes(_lpd(
        {"chronData": [{"model": [{"ensembleTable": [{"variableName": "ageEnsemble"}]}]}]},
        {"Core.Author.2026.chron1model1ensemble1.csv": row},
    ))
    result = MODULE.inspect_ensemble_lpd(ensemble)
    assert result["has_1000_age_draws"] is True
    assert result["age_ensemble_declared"] is True
