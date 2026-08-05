from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

MEMORY = Path(__file__).resolve().parents[1] / "couche_memoire_historique"
SCAN = MEMORY / "results_stress/exoplanet/b_final_regime_scan.csv"
OUT = Path(__file__).resolve().parent / "resultats"


def main() -> dict[str, object]:
    scan = pd.read_csv(SCAN)
    nonsaturated = scan[
        scan["attractor_ice_mean"].between(0.05, 0.85, inclusive="both")
    ].copy()
    nonsaturated["regime"] = pd.cut(
        nonsaturated["attractor_ice_mean"],
        bins=[0.05, 0.35, 0.65, 0.85],
        labels=["low_ice", "intermediate_ice", "high_ice"],
        include_lowest=True,
    ).astype(str)
    candidate_points = [
        {
            "obliquity_deg": float(row.final_obliquity_deg),
            "eccentricity": float(row.final_eccentricity),
            "ice_mean": float(row.attractor_ice_mean),
            "regime": row.regime,
        }
        for row in nonsaturated.itertuples(index=False)
    ]
    protocol: dict[str, object] = {
        "id": "WP-C2b",
        "status": "frozen_before_new_execution",
        "selection_rule": (
            "Points non saturés du scan historique, attractor_ice_mean entre 0.05 et 0.85. "
            "Aucun nouveau point ne peut être choisi après lecture des résultats C2b."
        ),
        "regime_bins": {
            "low_ice": [0.05, 0.35],
            "intermediate_ice": [0.35, 0.65],
            "high_ice": [0.65, 0.85],
        },
        "candidate_points": candidate_points,
        "calibration": (
            "Une référence distincte par régime, ajustée uniquement sur les graines de calibration."
        ),
        "holdout_seeds": [41001, 41003, 41011, 41017, 41023, 41039, 41047, 41051],
        "primary_endpoint": (
            "Différence M2 moins témoin apparié de l'étendue finale de glace après retour au forçage final."
        ),
        "secondary_endpoints": [
            "température finale",
            "CO2 final",
            "productivité finale",
            "temps de relaxation",
        ],
        "materiality_threshold": 0.05,
        "observation_myr": 400,
        "success_rule": (
            "Effet supérieur au seuil dans au moins 6 graines sur 8 et supérieur au témoin "
            "de complexité égale dans chaque régime représenté."
        ),
        "failure_rules": [
            "témoin non apparié",
            "gain inférieur au seuil",
            "effet absent dans plus de deux graines",
            "effet uniquement transitoire",
            "sélection a posteriori d'un point ou d'un régime",
        ],
    }
    protocol["source_map_sha256"] = hashlib.sha256(SCAN.read_bytes()).hexdigest()
    canonical = json.dumps(protocol, sort_keys=True, ensure_ascii=False).encode("utf-8")
    protocol["protocol_sha256"] = hashlib.sha256(canonical).hexdigest()
    OUT.mkdir(exist_ok=True)
    (OUT / "PROTOCOLE_C2B.json").write_text(
        json.dumps(protocol, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(protocol, indent=2, ensure_ascii=False))
    return protocol


if __name__ == "__main__":
    main()
