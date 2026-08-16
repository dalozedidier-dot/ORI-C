#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "plateforme" / "campagne_maximale_reelle" / "data" / "late_accretion_tracers.csv"
OUT = HERE / "resultats" / "AUDIT_ACCRETION_TARDIVE_MULTITRACEUR.json"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

table = pd.read_csv(DATA)
rich = (
    table.groupby(["sample_id", "candidate_source"])
    .tracer.nunique()
    .reset_index(name="n_tracers")
)
result = {
    "schema": "oric.late-accretion-existing-data-audit.v1",
    "rows": len(table),
    "source": "plateforme/campagne_maximale_reelle/data/late_accretion_tracers.csv",
    "source_sha256": sha256(DATA),
    "unique_samples": int(table.sample_id.nunique()),
    "candidate_source_labels": int(table.candidate_source.nunique()),
    "tracers": {str(k): int(v) for k, v in table.tracer.value_counts().items()},
    "uncertainty_nonmissing_fraction": float(table.uncertainty.notna().mean()),
    "samples_with_2plus_tracers": int((rich.n_tracers >= 2).sum()),
    "samples_with_4plus_tracers": int((rich.n_tracers >= 4).sum()),
    "max_tracers_per_sample": int(rich.n_tracers.max()),
    "interpretation": (
        "Large multitracer coverage exists and was underexploited, but "
        "candidate_source is a geological-family label rather than a late-accretion "
        "mixing endmember and per-measurement uncertainties are absent. The table "
        "supports fingerprint and sensitivity work, not a calibrated late-accretion mixing claim."
    ),
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print(f"{len(table)} rows audited -> {OUT.relative_to(ROOT)}")
