#!/usr/bin/env python3
"""Mesure une trace dynamique m à partir des sorties orbitales déjà calculées.

La trace n'est pas une histoire naturelle reconstruite. Elle est un proxy de
niveau modèle : l'empreinte spectrale de l'excentricité terrestre produite par
chaque architecture interventionnelle dans les bandes déjà utilisées par la
validation astronomique.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ANALYSIS = ROOT / "02_branche_systeme_solaire/couche_astronomique/resultats/real_science_max/analysis"
OUT = HERE / "resultats/TRACE_ORBITALE_M.json"
BANDS = ("95 kyr", "125 kyr", "405 kyr", "2.4 Myr")


def _finite_or_none(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def build() -> dict[str, object]:
    baseline_table = pd.read_csv(ANALYSIS / "spectral_band_comparison.csv")
    counter = pd.read_csv(ANALYSIS / "counterfactual_band_metrics.csv")

    baseline: dict[str, dict[str, float | None]] = {}
    for band in BANDS:
        row = baseline_table.loc[baseline_table["band"] == band]
        if row.empty:
            baseline[band] = {"normalized_band_power": None, "peak_period_years": None}
            continue
        item = row.iloc[0]
        baseline[band] = {
            "normalized_band_power": _finite_or_none(item["candidate_normalized_band_power"]),
            "peak_period_years": _finite_or_none(item["candidate_peak_period_years"]),
        }

    interventions = []
    for job, frame in counter.groupby("job", sort=True):
        fingerprint: dict[str, dict[str, float | None]] = {}
        log_ratios = []
        for band in BANDS:
            row = frame.loc[frame["band"] == band]
            if row.empty:
                fingerprint[band] = {
                    "normalized_band_power": None,
                    "power_ratio_vs_baseline": None,
                    "peak_period_years": None,
                }
                continue
            item = row.iloc[0]
            power = _finite_or_none(item["normalized_band_power"])
            ratio = _finite_or_none(item["power_ratio_vs_baseline"])
            peak = _finite_or_none(item["peak_period_years"])
            fingerprint[band] = {
                "normalized_band_power": power,
                "power_ratio_vs_baseline": ratio,
                "peak_period_years": peak,
            }
            if ratio is not None and ratio > 0:
                log_ratios.append(math.log(ratio))
        interventions.append({
            "intervention": str(job),
            "spectral_fingerprint": fingerprint,
            "m_log_power_distance_from_baseline": float(np.sqrt(np.sum(np.square(log_ratios)))) if log_ratios else None,
            "finite_power_ratio_bands": len(log_ratios),
        })

    distances = [row["m_log_power_distance_from_baseline"] for row in interventions if row["m_log_power_distance_from_baseline"] is not None]
    return {
        "schema": "oric.orbital-history-trace.v1",
        "status": "model_retrospective_dynamic_trace_proxy",
        "m_definition": "empreinte spectrale séculaire de l'excentricité terrestre sous une architecture donnée, mesurée dans les bandes 95 kyr, 125 kyr, 405 kyr et 2.4 Myr déjà gelées dans la validation astronomique",
        "baseline": "baseline_20myr_dt10 for reference band fingerprint; counterfactual jobs use their existing 2 Myr spectra",
        "bands": list(BANDS),
        "baseline_fingerprint": baseline,
        "interventions": interventions,
        "intervention_count": len(interventions),
        "distance_summary": {
            "min": float(np.min(distances)),
            "median": float(np.median(distances)),
            "max": float(np.max(distances)),
        } if distances else None,
        "interpretation": "les architectures interventionnelles laissent des empreintes spectrales différentes dans les sorties déjà calculées; ce vecteur fournit un m de niveau modèle distinct du comptage P_acc des cellules accessibles",
        "limits": [
            "ce m est un proxy dynamique rétrospectif de niveau modèle, pas une trace empirique d'une histoire orbitale naturelle unique",
            "les fréquences propres g_i/s_i complètes ne sont pas extraites ici; la mesure utilise uniquement les bandes déjà présentes dans les artefacts validés",
            "les bandes non résolues sur l'horizon 2 Myr restent nulles ou absentes et ne sont pas inventées",
        ],
    }


def main() -> dict[str, object]:
    result = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    main()
