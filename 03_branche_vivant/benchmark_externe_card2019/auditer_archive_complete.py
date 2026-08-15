"""Audit de l'archive Card 2019 et analyse des seules tables nouvelles."""

from __future__ import annotations

import hashlib
import io
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT / "donnees_externes/card_2019_complet/Card_et_al_2019_Data_and_R_Notebook.zip"
EXISTING = HERE / "data/MICs_Ara5_population.csv"
OUT = HERE / "resultats"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def member(archive: zipfile.ZipFile, suffix: str) -> bytes:
    name = next(n for n in archive.namelist() if n.endswith(suffix))
    return archive.read(name)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ARCHIVE) as archive:
        names = archive.namelist()
        ara = pd.read_csv(io.BytesIO(member(archive, "MICs of strains from Ara+5 population.csv")))
        existing = pd.read_csv(EXISTING)
        same = ara.equals(existing)
        ltee = pd.read_csv(io.BytesIO(member(archive, "MICs of LTEE ancestral and derived strains.csv")), encoding="cp1252")
        cell_counts = pd.read_csv(io.BytesIO(member(archive, "Cell counts.csv")))
        mutant_counts = pd.read_csv(io.BytesIO(member(archive, "Mutant colony counts.csv")))

    rows = []
    for antibiotic in ["amp", "cro", "cip", "tet"]:
        ltee[f"{antibiotic}.log2_change"] = np.log2(ltee[f"{antibiotic}.daughter"] / ltee[f"{antibiotic}.parent"])
        for strain, group in ltee.groupby("strain"):
            values = group[f"{antibiotic}.log2_change"]
            rows.append({
                "strain": strain,
                "antibiotic": antibiotic.upper(),
                "n_paired_assays": len(values),
                "median_log2_daughter_parent": float(values.median()),
                "min_log2_daughter_parent": float(values.min()),
                "max_log2_daughter_parent": float(values.max()),
            })
    descriptive = pd.DataFrame(rows)
    descriptive.to_csv(OUT / "CARD_2019_ADDITIONAL_LTEE_DESCRIPTIVE.csv", index=False, lineterminator="\n")
    result = {
        "schema": "oric.card-2019-complete-archive-audit.v1",
        "archive_sha256": sha256(ARCHIVE),
        "archive_entry_count": len(names),
        "structured_files": [
            "Cell counts.csv",
            "MICs of LTEE ancestral and derived strains.csv",
            "MICs of strains from Ara+5 population.csv",
            "Mutant colony counts.csv",
        ],
        "comparison_with_ORI_C": {
            "Ara_plus_5_table_semantically_identical": same,
            "existing_analysis_rerun": False,
            "reason": "the already-used table has identical rows and values; only filename bytes/encoding differ",
        },
        "additional_tables": {
            "LTEE_ancestral_and_derived_MIC_rows": len(ltee),
            "cell_count_rows": len(cell_counts),
            "mutant_colony_count_rows": len(mutant_counts),
            "analysis": "descriptive log2 daughter/parent MIC only",
            "inferential_limit": "paired assay rows and technical counts are not independent evolutionary lineages; no inflated p-value is computed",
        },
        "plate_photo_archive": {
            "sha256": "572ec0f67bfa012ea6f06a619560a763bf984f89eba0bd8c9331825ebed4de6b",
            "size_bytes": 296767159,
            "entry_count": 319,
            "imported_into_repository": False,
            "reason": "ancillary plate photographs contain no additional structured measurement table and would add about 297 MB",
        },
        "qualification": {
            "real_data": True,
            "synthetic_or_simulated_scientific_data": False,
            "new_confirmatory_result": False,
        },
    }
    write_json(OUT / "AUDIT_ARCHIVE_COMPLETE_CARD_2019.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
