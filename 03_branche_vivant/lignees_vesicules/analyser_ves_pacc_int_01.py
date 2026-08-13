#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROTOCOL = HERE / "PROTOCOLE_PACC_CAUSAL_PROSPECTIF_V1.json"
REGISTRATION = HERE / "VES-PACC-INT-01.registration.json"
INPUT = HERE / "ves_pacc_int_01_analysis_ready.npz"
META = HERE / "ves_pacc_int_01_analysis_ready.metadata.json"
OUT = HERE / "resultats" / "RESULTAT_VES_PACC_INT_01.json"

sys.path.insert(0, str(ROOT))
from methodologie_puissance.pacc_causal import estimate_matched_intervention_pacc  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def registration_gate() -> dict:
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    if registration.get("source_sha256") != sha256(PROTOCOL):
        raise SystemExit("Execution gate closed: protocol SHA-256 differs from the registered frozen source.")
    if registration.get("analysis_script_sha256") != sha256(Path(__file__).resolve()):
        raise SystemExit("Execution gate closed: analysis-script SHA-256 differs from the registered frozen source.")
    public = bool(
        registration.get("status") == "publicly_registered"
        and registration.get("public_url")
        and registration.get("registered_at")
    )
    if not public:
        raise SystemExit(
            "Execution gate closed: a public preregistration identifier and timestamp are required before any new test data."
        )
    return registration


def main() -> dict:
    registration = registration_gate()
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    if not INPUT.exists() or not META.exists():
        raise SystemExit("Analysis-ready prospective data are absent; no result is generated.")

    data = np.load(INPUT)
    meta = json.loads(META.read_text(encoding="utf-8"))
    if meta.get("protocol_sha256") != sha256(PROTOCOL):
        raise ValueError("analysis-ready metadata do not point to the frozen protocol SHA-256")

    for key in ("control_response", "intervention_response", "sham_response"):
        if data[key].ndim != 3 or data[key].shape[1:] != (12, 4):
            raise ValueError(f"{key} must be n×12×4")
    n = int(data["control_response"].shape[0])
    if not (data["intervention_response"].shape[0] == n == data["sham_response"].shape[0]):
        raise ValueError("arm sizes must match")

    matching = {name: bool(meta["matching"][name]) for name in protocol["matching_required"]}
    estimate = estimate_matched_intervention_pacc(
        X_anchor=np.ones((n, 4), dtype=float),
        control_response=data["control_response"],
        intervention_response=data["intervention_response"],
        sham_response=data["sham_response"],
        materiality_thresholds=np.asarray(protocol["P_acc"]["materiality_thresholds"], dtype=float),
        matching=matching,
        weights=None,
        sham_tolerance=float(protocol["P_acc"]["sham_tolerance_max_abs_Delta_P_acc"]),
        bootstrap_repeats=int(protocol["P_acc"]["bootstrap_draws"]),
        seed=int(protocol["P_acc"]["bootstrap_seed"]),
    )

    fidelity = meta["fidelity"]
    n_ok = n >= int(protocol["independent_unit"]["minimum_analyzable_n_for_primary_decision"])
    strict = bool(
        estimate["causal_qualified"]
        and n_ok
        and fidelity["do_m_population_target_passes"]
        and fidelity["sham_structural_fidelity_passes"]
    )
    delta = float(estimate["Delta_P_acc_mean"])
    upper = float(estimate["Delta_P_acc_bootstrap_q975"])
    sesoi = float(protocol["SESOI_and_power"]["SESOI_abs_Delta_P_acc"])
    inv_a = bool(strict and delta <= -sesoi and upper < 0.0)

    result = {
        "schema": "oric.ves-pacc-int-result.v1",
        "protocol_id": protocol["id"],
        "definition_id": protocol["strict_definition_id"],
        "protocol_sha256": sha256(PROTOCOL),
        "analysis_script_sha256": sha256(Path(__file__).resolve()),
        "public_registration": {
            "url": registration["public_url"],
            "registered_at": registration["registered_at"],
            "doi": registration.get("doi"),
        },
        "n_analyzable_independent_units": n,
        "strict_causal_qualified": strict,
        "section_XIV_condition_9_local_branch_measurement": strict,
        "direct_INV_A_support": inv_a,
        "fidelity": fidelity,
        "estimate": estimate,
        "decision_rule_applied_without_redefinition": True,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


if __name__ == "__main__":
    main()
