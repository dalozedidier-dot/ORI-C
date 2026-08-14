#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Mapping

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


def external_registration_metadata() -> dict[str, object]:
    """Lit l'état d'enregistrement externe sans en faire un verrou de calcul."""
    if not REGISTRATION.exists():
        return {
            "metadata_present": False,
            "public_registration_complete": False,
            "source_sha256_matches_current_protocol": None,
            "analysis_script_sha256_matches_current_script": None,
        }
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    public_complete = bool(
        registration.get("status") == "publicly_registered"
        and registration.get("public_url")
        and registration.get("registered_at")
    )
    return {
        "metadata_present": True,
        "status": registration.get("status"),
        "url": registration.get("public_url"),
        "registered_at": registration.get("registered_at"),
        "doi": registration.get("doi"),
        "public_registration_complete": public_complete,
        "source_sha256_matches_current_protocol": registration.get("source_sha256") == sha256(PROTOCOL),
        "analysis_script_sha256_matches_current_script": registration.get("analysis_script_sha256")
        == sha256(Path(__file__).resolve()),
    }


def validate_analysis_bundle(
    data: Mapping[str, np.ndarray],
    meta: Mapping[str, object],
    protocol: Mapping[str, object],
) -> int:
    """Valide uniquement la structure scientifique et l'intégrité du paquet réel."""
    for key in ("control_response", "intervention_response", "sham_response"):
        if key not in data:
            raise ValueError(f"missing array: {key}")
        array = np.asarray(data[key])
        if array.ndim != 3 or array.shape[1:] != (12, 4):
            raise ValueError(f"{key} must be n×12×4")
        if not np.isfinite(array).all():
            raise ValueError(f"{key} contains non-finite values")

    n = int(np.asarray(data["control_response"]).shape[0])
    if not (
        np.asarray(data["intervention_response"]).shape[0]
        == n
        == np.asarray(data["sham_response"]).shape[0]
    ):
        raise ValueError("arm sizes must match")
    if n < 2:
        raise ValueError("at least two independent units are required")

    required = list(protocol["matching_required"])
    matching = meta.get("matching", {})
    if not isinstance(matching, Mapping):
        raise ValueError("matching metadata are required")
    missing = [name for name in required if name not in matching]
    if missing:
        raise ValueError("missing matching flags: " + ", ".join(missing))

    fidelity = meta.get("fidelity")
    if not isinstance(fidelity, Mapping):
        raise ValueError("fidelity metadata are required")
    for name in ("do_m_population_target_passes", "sham_structural_fidelity_passes"):
        if name not in fidelity:
            raise ValueError(f"missing fidelity flag: {name}")
    return n


def analyse_arrays(
    data: Mapping[str, np.ndarray],
    meta: Mapping[str, object],
    protocol: Mapping[str, object],
) -> dict[str, object]:
    """Applique la décision VES-PACC-INT-01 aux mesures fournies."""
    n = validate_analysis_bundle(data, meta, protocol)
    matching = {name: bool(meta["matching"][name]) for name in protocol["matching_required"]}

    estimate = estimate_matched_intervention_pacc(
        X_anchor=np.ones((n, 4), dtype=float),
        control_response=np.asarray(data["control_response"], dtype=float),
        intervention_response=np.asarray(data["intervention_response"], dtype=float),
        sham_response=np.asarray(data["sham_response"], dtype=float),
        materiality_thresholds=np.asarray(protocol["P_acc"]["materiality_thresholds"], dtype=float),
        matching=matching,
        weights=None,
        sham_tolerance=float(protocol["P_acc"]["sham_tolerance_max_abs_Delta_P_acc"]),
        bootstrap_repeats=int(protocol["P_acc"]["bootstrap_draws"]),
        seed=int(protocol["P_acc"]["bootstrap_seed"]),
    )

    fidelity = dict(meta["fidelity"])
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

    return {
        "n_analyzable_independent_units": n,
        "minimum_n_passes": n_ok,
        "strict_causal_qualified": strict,
        "section_XIV_condition_9_local_branch_measurement": strict,
        "direct_INV_A_support": inv_a,
        "fidelity": fidelity,
        "estimate": estimate,
        "decision_rule_applied_without_redefinition": True,
    }


def main() -> dict[str, object]:
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    if not INPUT.exists() or not META.exists():
        raise SystemExit("Analysis-ready prospective data are absent; no result is generated.")

    with np.load(INPUT) as loaded:
        data = {key: loaded[key] for key in loaded.files}
    meta = json.loads(META.read_text(encoding="utf-8"))

    current_protocol_sha = sha256(PROTOCOL)
    if meta.get("protocol_sha256") != current_protocol_sha:
        raise ValueError("analysis-ready metadata do not point to the current frozen protocol SHA-256")

    core = analyse_arrays(data, meta, protocol)
    registration = external_registration_metadata()
    result = {
        "schema": "oric.ves-pacc-int-result.v1",
        "protocol_id": protocol["id"],
        "definition_id": protocol["strict_definition_id"],
        "protocol_sha256": current_protocol_sha,
        "analysis_script_sha256": sha256(Path(__file__).resolve()),
        "external_registration": registration,
        "prospective_preregistered_label_available": bool(
            registration.get("public_registration_complete")
            and registration.get("source_sha256_matches_current_protocol")
            and registration.get("analysis_script_sha256_matches_current_script")
        ),
        **core,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


if __name__ == "__main__":
    main()
