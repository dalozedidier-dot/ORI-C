#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import tempfile
import zipfile
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = HERE / "donnees" / "gajrani_dryad_v20250804.zip"
OUT = HERE / "resultats" / "RESULTAT_PACC_RETROSPECTIF.json"
SEED = 20260816
SUP = ["Sup4", "Sup6", "Sup27", "Sup66", "Sup79", "Sup81", "Sup107", "SupMyb27"]
CTRL = [f"noSup{i}" for i in range(1, 9)]

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

units = []
rng = np.random.default_rng(SEED)
with tempfile.TemporaryDirectory() as directory:
    with zipfile.ZipFile(SOURCE) as archive:
        archive.extractall(directory)
    extracted = Path(directory)
    for day in (5, 10, 12):
        for community in range(1, 7):
            path = next(
                extracted.rglob(
                    f"Fig_4_cfu_counts_Day_{day}_Community_{community}_triplicates.csv"
                )
            )
            data = pd.read_csv(path)
            p_sup = {
                column: float((data.groupby("Species")[column].median() > 0).mean())
                for column in SUP
            }
            p_ctrl = {
                column: float((data.groupby("Species")[column].median() > 0).mean())
                for column in CTRL
                if column in data.columns
            }
            sup_mean = float(np.mean(list(p_sup.values())))
            control_mean = float(np.mean(list(p_ctrl.values()))) if p_ctrl else None
            units.append({
                "day": day,
                "community": community,
                "pacc_sup_mean": sup_mean,
                "pacc_control_mean": control_mean,
                "delta_retention": sup_mean - control_mean if control_mean is not None else None,
                "pacc_sup_by_challenge": p_sup,
                "pacc_control_by_rep": p_ctrl,
                "n_sup": len(p_sup),
                "n_control": len(p_ctrl),
            })

days = {}
for day in (5, 10, 12):
    selected = [item for item in units if item["day"] == day]
    values = np.array(
        [item["delta_retention"] for item in selected if item["delta_retention"] is not None],
        dtype=float,
    )
    if len(values):
        bootstrap = np.array([
            rng.choice(values, len(values), replace=True).mean()
            for _ in range(20000)
        ])
        sham = []
        for item in selected:
            first = np.mean([item["pacc_control_by_rep"][f"noSup{i}"] for i in range(1, 5)])
            second = np.mean([item["pacc_control_by_rep"][f"noSup{i}"] for i in range(5, 9)])
            sham.append(first - second)
        days[str(day)] = {
            "n_independent_community_compositions": len(selected),
            "delta_Pacc_retention_mean": float(values.mean()),
            "delta_units": [float(value) for value in values],
            "bootstrap95": [float(value) for value in np.quantile(bootstrap, [0.025, 0.975])],
            "control_split_sham_delta_mean_descriptive": float(np.mean(sham)),
            "control_split_sham_max_abs_descriptive": float(np.max(np.abs(sham))),
        }
    else:
        days[str(day)] = {
            "n_independent_community_compositions": len(selected),
            "delta_Pacc_retention_mean": None,
            "delta_units": [None] * len(selected),
            "bootstrap95": [None, None],
            "control_split_sham_delta_mean_descriptive": None,
            "control_split_sham_max_abs_descriptive": None,
        }

result = {
    "schema": "oric.gajrani-community-pacc-retrospective.v1.1-strict-json",
    "source": "03_branche_vivant/memoire_externalisee_gajrani_2025/donnees/gajrani_dryad_v20250804.zip",
    "source_sha256": sha256(SOURCE),
    "definition": (
        "Pacc_retention = fraction of the 8 species with median CFU > 0 across technical "
        "triplicates. For each independent initial community composition, intervention Pacc "
        "is averaged across the 8 species-supernatant challenges; control Pacc is averaged "
        "across all no-supernatant control columns. Delta = intervention-control."
    ),
    "days": days,
    "units": units,
    "strict_PACC_INT_CHALLENGE_V1_qualified": False,
    "reason_not_strict": (
        "retrospective mapping after public data; thresholds, challenge weights and sham were "
        "not preregistered. Use only for field completeness and mechanistic exploration."
    ),
    "section_XIV_credit": False,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
print(f"day12 delta={days['12']['delta_Pacc_retention_mean']} -> {OUT.relative_to(ROOT)}")
