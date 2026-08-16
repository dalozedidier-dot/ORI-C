#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import io
import json
import zipfile
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "donnees" / "gajrani_dryad_v20250804.zip"
OUT = HERE / "resultats" / "RESULTAT.json"
DILUTIONS = ["1/2x", "1/6x", "1/20x", "1/100x"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv_from_zip(archive: zipfile.ZipFile, name: str) -> list[dict[str, str]]:
    with archive.open(name) as stream:
        text = io.TextIOWrapper(stream, encoding="utf-8-sig")
        return list(csv.DictReader(text))


def final_ca_fraction(row: dict[str, str], ca_col: str, lp_col: str) -> float:
    ca = float(row[ca_col])
    lp = float(row[lp_col])
    total = ca + lp
    return np.nan if total <= 0 else ca / total


def crossing_threshold(rows: list[dict[str, str]], ca_col: str, lp_col: str) -> float:
    points = []
    for row in rows:
        x = float(row["Ca%"])
        fraction = final_ca_fraction(row, ca_col, lp_col)
        if np.isfinite(fraction):
            points.append((x, fraction))
    points.sort()
    for i, (x, fraction) in enumerate(points):
        if fraction < 0.5:
            continue
        if i == 0:
            return x
        x0, f0 = points[i - 1]
        if f0 >= 0.5:
            return x0
        if fraction == f0:
            return x
        return x0 + (0.5 - f0) * (x - x0) / (fraction - f0)
    return float("nan")


def summarize(rows: list[tuple[int, str, float, float, float]]) -> dict:
    grouped: dict[str, list[tuple[float, float, float]]] = defaultdict(list)
    for _, dilution, t_ca, t_lp, gap in rows:
        grouped[dilution].append((t_ca, t_lp, gap))
    result = {}
    for dilution, values in grouped.items():
        a = np.asarray(values, dtype=float)
        def finite_or_none(value):
            value = float(value)
            return value if np.isfinite(value) else None
        ca_med = np.nanmedian(a[:, 0]) if np.isfinite(a[:, 0]).any() else np.nan
        lp_med = np.nanmedian(a[:, 1]) if np.isfinite(a[:, 1]).any() else np.nan
        gap_med = np.nanmedian(a[:, 2]) if np.isfinite(a[:, 2]).any() else np.nan
        gap_min = np.nanmin(a[:, 2]) if np.isfinite(a[:, 2]).any() else np.nan
        gap_max = np.nanmax(a[:, 2]) if np.isfinite(a[:, 2]).any() else np.nan
        result[dilution] = {
            "ca_memory_threshold_median": finite_or_none(ca_med),
            "lp_memory_threshold_median": finite_or_none(lp_med),
            "threshold_gap_median": finite_or_none(gap_med),
            "threshold_gap_min": finite_or_none(gap_min),
            "threshold_gap_max": finite_or_none(gap_max),
        }
    return result


def build() -> dict:
    retained = []
    rescue = []
    with zipfile.ZipFile(SOURCE) as archive:
        for set_number in (1, 2, 3):
            ca_mem = read_csv_from_zip(archive, f"Fig_1_cfu_counts_CaUnwashed-LpW-Set{set_number}.csv")
            lp_mem = read_csv_from_zip(archive, f"Fig_1_cfu_counts_CaWashed-LpUN-Set{set_number}.csv")
            ca_sup = read_csv_from_zip(archive, f"Supp_Fig_2_CaSup-CaW-LpW-Set{set_number}.csv")
            lp_sup = read_csv_from_zip(archive, f"Supp_Fig_2_LpSup-CaW-LpW-Set{set_number}.csv")
            for dilution in DILUTIONS:
                t_ca = crossing_threshold(ca_mem, f"Ca_{dilution}-Un", f"Lp_{dilution}-W")
                t_lp = crossing_threshold(lp_mem, f"Ca_{dilution}-W", f"Lp_{dilution}-Un")
                retained.append((set_number, dilution, t_ca, t_lp, t_lp - t_ca))

                t_ca_sup = crossing_threshold(ca_sup, f"Ca_{dilution}", f"Lp_{dilution}")
                t_lp_sup = crossing_threshold(lp_sup, f"Ca_{dilution}", f"Lp_{dilution}")
                rescue.append((set_number, dilution, t_ca_sup, t_lp_sup, t_lp_sup - t_ca_sup))

    retained_summary = summarize(retained)
    rescue_summary = summarize(rescue)
    gap_half = retained_summary["1/2x"]["threshold_gap_median"]
    gap_100 = retained_summary["1/100x"]["threshold_gap_median"]
    reduction = 100.0 * (gap_half - gap_100) / gap_half
    sup = rescue_summary["1/2x"]

    return {
        "schema": "oric.external-benchmark.v1",
        "benchmark_id": "GAJRANI-2025-EXTERNALIZED-MEMORY",
        "source": {
            "doi": "10.5061/dryad.ksn02v7hp",
            "article_doi": "10.1093/ismejo/wraf173",
            "archive": SOURCE.name,
            "sha256": sha256(SOURCE),
        },
        "design": {
            "system": "Lactobacillus plantarum + Corynebacterium ammoniagenes",
            "X": "similar initial two-species composition",
            "H": "which species had previously modified its environment",
            "m": "persistent extracellular environmental modification retained or removed by washing; supernatant transfer tests sufficiency",
            "Theta": "common future co-culture conditions with daily dilution",
            "R": "final community composition/CFU after common future",
            "source_defined_switch_rule": "Ca winner when final relative abundance >50%",
        },
        "quantification": {
            "retained_memory_threshold_gap_percentage_points": retained_summary,
            "memory_gap_reduction_from_1_2x_to_1_100x_percent": reduction,
            "supernatant_only_both_cells_washed_threshold_gap_percentage_points": rescue_summary,
        },
        "key_effects": {
            "mild_dilution_1_2x": {
                "Ca_memory_Ca_win_threshold_percent": retained_summary["1/2x"]["ca_memory_threshold_median"],
                "Lp_memory_Ca_win_threshold_percent": retained_summary["1/2x"]["lp_memory_threshold_median"],
                "history_memory_shift_percentage_points": gap_half,
            },
            "high_dilution_1_100x": {
                "history_memory_shift_percentage_points": gap_100,
                "shift_reduction_vs_1_2x_percent": reduction,
            },
            "supernatant_rescue_1_2x": {
                "both_cells_washed": True,
                "Ca_supernatant_Ca_win_threshold_percent": sup["ca_memory_threshold_median"],
                "Lp_supernatant_Ca_win_threshold_percent": sup["lp_memory_threshold_median"],
                "median_threshold_gap_percentage_points": sup["threshold_gap_median"],
                "range_across_three_sets_percentage_points": [sup["threshold_gap_min"], sup["threshold_gap_max"]],
            },
        },
        "classification": {
            "empirical_do_m_relevant": True,
            "memory_location_external_environment_supported": True,
            "necessity_and_sufficiency_design_present": True,
            "strict_PACC_INT_CHALLENGE_V1_qualified": False,
            "reason_not_strict_pacc": "ORI-C future challenge cells, epsilon thresholds, weights and sham were not preregistered before this already-public dataset; protocol explicitly forbids retrospective requalification.",
            "counts_for_section_XIV_condition_9": False,
            "recommended_ORI_C_role": "strong retrospective causal benchmark for H/m/R and direct environmental-memory intervention; do not promote to strict Pacc",
        },
    }


if __name__ == "__main__":
    result = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
