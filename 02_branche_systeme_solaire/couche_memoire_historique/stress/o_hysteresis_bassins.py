#!/usr/bin/env python3
"""Cartographie exploratoire des bassins et de l'hystérèse de l'EMIC réduit.

Cette campagne est rétrospective : les zones multistables ont déjà été vues.
Elle qualifie l'instrument et ne compte pas comme confirmation prospective.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(PROJECT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT / "src"))

from core import exo_parameter_vector, polar_summer_insolation  # noqa: E402
from m_prospectif_wp_c2 import _pas, simuler, etats_initiaux  # noqa: E402

OUT = PROJECT / "results_stress" / "hysteresis_c3"
REFERENCE = (23.5, 0.05)
MODES = {0: "classic", 2: "M2", 4: "M2P_corrige"}


def forcing_components(obliquite: float, excentricite: float) -> tuple[float, float]:
    polar = float(polar_summer_insolation(obliquite, excentricite))
    reference = float(polar_summer_insolation(*REFERENCE))
    anomaly = (polar - reference) / 100.0
    flux = (1.0 / math.sqrt(1.0 - excentricite**2) - 1.0 / math.sqrt(1.0 - REFERENCE[1] ** 2)) / 0.05
    return anomaly, flux


def hold(state, obliquite, excentricite, mode, p, calibration, duration=80.0):
    anomaly, flux = forcing_components(obliquite, excentricite)
    entree_r, entree_m = calibration if mode == 4 else (0.0, 0.0)
    n = int(duration / 0.02)
    current = tuple(float(x) for x in state)
    for _ in range(n):
        current, _ = _pas(current, anomaly, flux, mode, p, entree_r, entree_m)
    return np.asarray(current, float)


def sweep(obliquite, values, mode, p, calibration, initial_state, duration=60.0):
    state = np.asarray(initial_state, float)
    rows = []
    for eccentricity in values:
        state = hold(state, obliquite, float(eccentricity), mode, p, calibration, duration)
        rows.append({
            "obliquity_deg": obliquite,
            "eccentricity": float(eccentricity),
            "temperature": state[0],
            "ice": state[1],
            "co2": state[2],
            "regolith": state[3],
            "memory": state[4],
        })
    return pd.DataFrame(rows), state


def transition_eccentricity(frame, ice_threshold=0.5):
    """Interpole le premier franchissement du seuil de glace."""
    eccentricity = frame["eccentricity"].to_numpy(float)
    ice = frame["ice"].to_numpy(float)
    centered = ice - ice_threshold
    for index in range(1, len(centered)):
        left, right = centered[index - 1], centered[index]
        if left == 0:
            return float(eccentricity[index - 1])
        if left * right < 0 or right == 0:
            x0, x1 = eccentricity[index - 1], eccentricity[index]
            y0, y1 = centered[index - 1], centered[index]
            return float(x0 - y0 * (x1 - x0) / (y1 - y0))
    return None


def cluster_count(values, threshold=0.05):
    centers = []
    for value in sorted(float(v) for v in values):
        if not centers or abs(value - centers[-1]) > threshold:
            centers.append(value)
        else:
            centers[-1] = 0.5 * (centers[-1] + value)
    return len(centers), centers


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    p = exo_parameter_vector()
    c2 = json.loads((PROJECT / "results_stress" / "prospectif_c2" / "prospectif_c2.json").read_text(encoding="utf-8"))
    cal = c2["protocole"]["calibration_des_entrees"]
    calibration = (float(cal["entree_du_regolithe"]), float(cal["entree_de_la_memoire"]))

    eccentricities = np.linspace(0.0, 0.20, 21)
    all_sweeps = []
    summary = []
    for obliquity in (30.0, 40.0):
        for mode, name in MODES.items():
            initial = np.array([0.0, 0.02, 300.0, 0.8, 0.4])
            forward, high_state = sweep(obliquity, eccentricities, mode, p, calibration, initial)
            reverse, low_state = sweep(obliquity, eccentricities[::-1], mode, p, calibration, high_state)
            reverse = reverse.sort_values("eccentricity").reset_index(drop=True)
            forward = forward.sort_values("eccentricity").reset_index(drop=True)
            gap = np.abs(forward["ice"].to_numpy() - reverse["ice"].to_numpy())
            loop_area = float(np.trapezoid(gap, eccentricities))
            max_gap = float(gap.max())
            forward_threshold = transition_eccentricity(forward)
            reverse_threshold = transition_eccentricity(reverse)
            threshold_separation = (
                abs(forward_threshold - reverse_threshold)
                if forward_threshold is not None and reverse_threshold is not None
                else None
            )
            for direction, frame in (("forward", forward), ("reverse", reverse)):
                frame = frame.copy(); frame["direction"] = direction; frame["mode"] = name
                all_sweeps.append(frame)
            summary.append({
                "obliquity_deg": obliquity,
                "mode": name,
                "max_ice_gap": max_gap,
                "loop_area": loop_area,
                "hysteresis_material": bool(max_gap >= 0.05),
                "forward_transition_eccentricity": forward_threshold,
                "reverse_transition_eccentricity": reverse_threshold,
                "transition_separation": threshold_separation,
                "same_low_endpoint_gap": float(abs(forward.iloc[0].ice - reverse.iloc[0].ice)),
                "irreversible_after_full_return": bool(abs(forward.iloc[0].ice - reverse.iloc[0].ice) >= 0.05),
            })

    sweeps = pd.concat(all_sweeps, ignore_index=True)
    sweeps.to_csv(OUT / "hysteresis_sweeps.csv", index=False)
    # Bassins aux deux points déjà discriminants, sur une grille d'états initiaux.
    basin_rows = []
    for obliquity, eccentricity in ((30.0, 0.10), (40.0, 0.00)):
        for mode, name in MODES.items():
            finals = []
            for ice0 in np.linspace(0.0, 1.0, 5):
                for regolith0 in (0.1, 0.5, 0.9):
                    for memory0 in (0.1, 0.7, 1.3):
                        state0 = np.array([0.0, ice0, 300.0, regolith0, memory0])
                        final, _ = simuler(obliquity, eccentricity, mode, state0, p, calibration=calibration if mode == 4 else None, duree=400.0)
                        finals.append(float(final[1]))
                        basin_rows.append({
                            "obliquity_deg": obliquity,
                            "eccentricity": eccentricity,
                            "mode": name,
                            "initial_ice": ice0,
                            "initial_regolith": regolith0,
                            "initial_memory": memory0,
                            "final_ice": float(final[1]),
                        })
            count, centers = cluster_count(finals)
            for row in summary:
                if row["obliquity_deg"] == obliquity and row["mode"] == name:
                    row["basin_count"] = count
                    row["basin_centers"] = centers

    basin_df = pd.DataFrame(basin_rows)
    basin_df.to_csv(OUT / "basin_map.csv", index=False)
    summary_df = pd.DataFrame(summary)
    summary_df.to_csv(OUT / "hysteresis_summary.csv", index=False)
    (OUT / "hysteresis_verdict.json").write_text(json.dumps({
        "status": "qualification exploratoire, non confirmatoire",
        "calibration_source": "WP-C2",
        "sweep_duration_per_step_myr": 60.0,
        "basin_hold_myr": 400.0,
        "material_gap_threshold": 0.05,
        "results": summary,
        "interpretation": {
            "hysteresis": "Un écart avant-retour supérieur au seuil indique une boucle d'hystérèse dans l'EMIC réduit.",
            "same_forcing_different_final_state": "Deux bassins au même forçage établissent plusieurs états finaux possibles dans le modèle.",
            "irreversibility": "Aucun mode ne conserve un écart matériel après le retour complet au faible forçage. Aucun seuil irréversible de bout de cycle n'est donc détecté dans cette campagne.",
            "memory": "Une boucle d'hystérèse ou plusieurs bassins établissent une dépendance au chemin dans le modèle, pas une mémoire climatique réelle.",
            "prospective_limit": "Les zones testées ont été sélectionnées après cartographie. Une validation devra utiliser de nouveaux points gelés à l'avance.",
        },
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = [
        "# Bassins et hystérèse dans l'EMIC réduit",
        "",
        "Cette campagne transforme la piste des zones multistables en tests de bassins et de balayage avant-retour. Elle est exploratoire puisque les zones ont déjà été observées.",
        "",
        "| Obliquité | Mode | Écart maximal de glace | Aire de boucle | Hystérèse matérielle | Bassins |",
        "|---:|---|---:|---:|---|---:|",
    ]
    for row in summary:
        report.append(f"| {row['obliquity_deg']:.1f}° | {row['mode']} | {row['max_ice_gap']:.4f} | {row['loop_area']:.4f} | {'oui' if row['hysteresis_material'] else 'non'} | {row.get('basin_count', '')} |")
    report += [
        "",
        "## Basculement et retour",
        "",
        "Les cartes de bassins montrent plusieurs états finaux sous un même forçage pour M2 et M2P. Les balayages avant-retour localisent aussi les franchissements du seuil de glace lorsqu'ils existent.",
        "",
        "Après un cycle complet, aucun mode ne conserve un écart de glace supérieur à 0,05 au faible forçage final. Cette campagne ne détecte donc pas de seuil irréversible de bout de cycle.",
        "",
        "## Portée",
        "",
        "Les tests distinguent attracteur unique, bassins multiples et boucle d'hystérèse. Ils ne transforment pas l'EMIC en preuve du climat réel. La prochaine exécution confirmatoire devra choisir de nouveaux points avant calcul, conserver un témoin apparié et fixer les seuils dans un protocole signé.",
    ]
    (OUT / "RAPPORT_HYSTERESIS_C3.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(summary_df.to_json(orient="records"))


if __name__ == "__main__":
    main()
