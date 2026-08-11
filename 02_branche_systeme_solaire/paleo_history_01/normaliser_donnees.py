#!/usr/bin/env python3
"""Normalise les neuf familles PALEO-HISTORY-01 sans inventer d'incertitudes d'âge."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXTERNAL = ROOT / "donnees_externes"
LEGACY = EXTERNAL / "donnees_reelles_2026_08_07" / "paleoclimat_long"
PALEO = EXTERNAL / "paleo_history_01"
OUT = HERE / "donnees_normalisees"
FIELDS = [
    "dataset_id", "source_id", "age_ka_bp", "age_uncertainty_ka",
    "proxy_name", "proxy_value", "proxy_unit", "quality_flag", "sha256_source",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def numeric_rows(path: Path, start_pattern: str | None = None) -> list[list[float]]:
    rows: list[list[float]] = []
    started = start_pattern is None
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not started:
            if re.search(start_pattern, raw):
                started = True
            continue
        line = raw.strip()
        if not line or line.startswith(("#", "/*", "*", "Column", "Depth", "Age", "Bag")):
            continue
        try:
            values = [float(x) for x in line.replace("\t", " ").split()]
        except ValueError:
            continue
        if values:
            rows.append(values)
    return rows


def records(dataset: str, source: str, path: Path, values: list[tuple[float, float]],
            proxy: str, unit: str, age_note: str, age_uncertainty: str = "") -> list[dict[str, str]]:
    digest = sha(path)
    return [{
        "dataset_id": dataset,
        "source_id": source,
        "age_ka_bp": f"{age:.6f}",
        "age_uncertainty_ka": age_uncertainty,
        "proxy_name": proxy,
        "proxy_value": f"{value:.12g}",
        "proxy_unit": unit,
        "quality_flag": f"observed;age_uncertainty_unavailable:{age_note}",
        "sha256_source": digest,
    } for age, value in values if math.isfinite(age) and math.isfinite(value) and 0 <= age <= 800]


def parse_all() -> dict[str, list[dict[str, str]]]:
    result: dict[str, list[dict[str, str]]] = {}

    path = LEGACY / "lisiecki2005_LR04.txt"
    raw = numeric_rows(path, r"^\s*Time\s+d18O\s+Error")
    vals = [(r[0], r[1]) for r in raw if len(r) >= 3 and r[0] <= 800]
    result["LR04"] = records("LR04", "Lisiecki-Raymo-2005", path, vals, "benthic_d18O", "permil", "LR04_file_has_proxy_error_not_age_error")

    path = PALEO / "ahn2017_prob_stack.txt"
    raw = numeric_rows(path)
    vals = [(r[0], r[1]) for r in raw if len(r) >= 5]
    result["pile_benthique_independante"] = records("pile_benthique_independante", "Ahn-et-al-2017", path, vals, "prob_stack_benthic_d18O", "permil", "published_table_has_stack_spread_not_point_age_distribution")

    path = PALEO / "spratt2016_sea_level_noaa.txt"
    raw = numeric_rows(path, r"^# Data:")
    vals = [(r[0], r[5]) for r in raw if len(r) >= 9 and math.isfinite(r[5])]
    result["proxy_niveau_marin_independant"] = records("proxy_niveau_marin_independant", "Spratt-Lisiecki-2016", path, vals, "global_sea_level_long_PC1", "m", "record_aligned_to_LR04_without_point_age_distribution")

    path = LEGACY / "edc3deuttemp2007.txt"
    raw = numeric_rows(path, r"^\s*Bag\s+ztop\s+Age")
    vals = [(r[2] / 1000.0, r[4]) for r in raw if len(r) >= 5]
    result["EPICA_temperature"] = records("EPICA_temperature", "Jouzel-et-al-2007", path, vals, "temperature_anomaly", "degC", "EDC3_maximum_age_uncertainty_published_but_no_point_distribution_in_source")

    path = LEGACY / "edc-co2-2008.txt"
    text = path.read_text(encoding="utf-8", errors="replace").splitlines()
    start = next(i for i, line in enumerate(text) if "Age(yrBP)" in line and "CO2(ppmv)" in line)
    vals = []
    for line in text[start + 1:]:
        try:
            row = [float(x) for x in line.split()]
        except ValueError:
            continue
        if len(row) == 2:
            vals.append((row[0] / 1000.0, row[1]))
    result["EPICA_CO2"] = records("EPICA_CO2", "Luthi-et-al-2008", path, vals, "CO2", "ppmv", "EDC3_gas_age_has_no_point_distribution_in_source")

    path = PALEO / "lambert2008_epica_dust" / "datasets" / "EDC_dust_lpc.tab"
    raw = numeric_rows(path)
    vals = [(r[1], r[2]) for r in raw if len(r) >= 3]
    result["EPICA_poussieres"] = records("EPICA_poussieres", "Lambert-et-al-2008", path, vals, "dust_concentration", "ug_per_kg", "EDC3_has_no_point_distribution_in_source")

    path = LEGACY / "vostok_deutnat.txt"
    raw = numeric_rows(path, r"^Depth corrected")
    vals = [(r[1] / 1000.0, r[3]) for r in raw if len(r) >= 4]
    result["Vostok"] = records("Vostok", "Petit-et-al-2001", path, vals, "temperature_anomaly", "degC", "GT4_has_no_point_age_distribution_in_source")

    path = ROOT / "02_branche_systeme_solaire" / "couche_memoire_historique" / "data" / "raw" / "orbit91"
    raw = numeric_rows(path)
    vals = [(-r[0], r[5]) for r in raw if len(r) >= 6 and r[0] <= 0]
    result["insolation_convention_1"] = records("insolation_convention_1", "Berger-orbit91", path, vals, "65N_July_insolation", "W_per_m2", "deterministic_orbital_solution", "0")

    path = PALEO / "INSOLN.LA2004.BTL.100.ASC"
    raw = numeric_rows(path)
    vals = [(-r[0], r[1]) for r in raw if len(r) >= 4 and r[0] <= 0]
    result["insolation_convention_2"] = records("insolation_convention_2", "Laskar-et-al-2004", path, vals, "eccentricity", "dimensionless", "deterministic_orbital_solution", "0")
    return result


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    datasets = parse_all()
    summary = {"schema": "oric.paleo-history-01.normalization.v1", "datasets": {}, "admissible": True, "blocking_issues": []}
    for dataset, rows in datasets.items():
        target = OUT / f"{dataset}.csv"
        with target.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
            writer.writeheader(); writer.writerows(rows)
        missing_age = sum(not row["age_uncertainty_ka"] for row in rows)
        summary["datasets"][dataset] = {"rows": len(rows), "missing_age_uncertainty_rows": missing_age, "file": target.relative_to(ROOT).as_posix()}
        if missing_age:
            summary["admissible"] = False
    summary["blocking_issues"] = [
        "aucune distribution chronologique point par point n'est fournie pour les archives observées; les erreurs de proxy ne sont pas des erreurs d'âge",
        "le contrôle négatif réel exigé par le protocole gelé n'est identifié ni dans PLAN_ANALYSE.json ni dans PROTOCOLE_GELE.md",
    ]
    summary["verdict"] = "non_testable"
    (OUT / "AUDIT_NORMALISATION.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
