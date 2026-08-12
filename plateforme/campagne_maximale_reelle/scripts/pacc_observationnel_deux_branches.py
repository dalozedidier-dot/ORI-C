"""Même estimateur de reachability observationnelle sur antibiotiques et LR04."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ORI_ROOT = ROOT.parents[1]
OUTPUT = ROOT / "resultats_consolides" / "pacc_observationnel_deux_branches.json"
BINS = 5


def discretize(values: np.ndarray) -> tuple[np.ndarray, list[float]]:
    edges = np.quantile(values, np.linspace(0, 1, BINS + 1))
    edges[0], edges[-1] = -np.inf, np.inf
    return np.digitize(values, edges[1:-1], right=True), edges.tolist()


def summarize(current: np.ndarray, future: np.ndarray) -> dict:
    rows = {}
    for state in range(BINS):
        selected = future[current == state]
        reachable = sorted(set(int(value) for value in selected))
        rows[str(state)] = {
            "transitions": int(len(selected)),
            "reachable_states": reachable,
            "pacc_observed": float(len(reachable) / BINS),
        }
    return rows


def antibiotics() -> dict:
    path = ROOT / "data" / "antibiotic_measurements.csv"
    series = defaultdict(list)
    with path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            if row["cycle"].strip() and row["survival"].strip() and float(row["survival"]) > 0:
                series[row["lineage_id"]].append((int(float(row["cycle"])), np.log10(float(row["survival"]))))
    all_values = np.array([value for values in series.values() for _, value in values])
    _, edges = discretize(all_values)
    current_values, future_values = [], []
    for values in series.values():
        ordered = sorted(values)
        for left, right in zip(ordered[:-1], ordered[1:]):
            current_values.append(left[1]); future_values.append(right[1])
    current = np.digitize(current_values, edges[1:-1], right=True)
    future = np.digitize(future_values, edges[1:-1], right=True)
    return {"state_edges_log10_survival": edges, "horizon": "next observed cycle", "states": summarize(current, future)}


def climate() -> dict:
    path = ORI_ROOT / "02_branche_systeme_solaire" / "couche_memoire_historique" / "data" / "processed" / "mpt_lr04_la2004.csv"
    age, values = [], []
    with path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            age.append(float(row["age_kyr_bp"])); values.append(float(row["d18o_permil"]))
    order = np.argsort(age)
    values = np.asarray(values)[order]
    states, edges = discretize(values)
    horizon = 10
    return {"state_edges_d18o_permil": edges, "horizon": "10 ka", "states": summarize(states[:-horizon], states[horizon:])}


def main() -> int:
    report = {
        "definition": "number of empirically reached future state classes divided by five declared classes",
        "same_estimator": True,
        "antibiotics": antibiotics(),
        "paleoclimate": climate(),
        "status": "observational_proxy_not_causal_pacc",
        "causal_qualification": False,
        "deprecated_for_section_xiv_condition_9": True,
        "replacement_definition_id": "PACC-INT-CHALLENGE-V1",
        "replacement_protocol": "protocoles_geles/PACC_INTERVENTIONNEL_V1.md",
        "limitation": "No matched intervention set I; observed reachability cannot identify counterfactual accessibility.",
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

