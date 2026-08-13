#!/usr/bin/env python3
"""Prépare les tables brutes VES-PACC-INT-01 pour l'analyse gelée.

Aucun seuil scientifique n'est défini ici : le script lit exclusivement
PROTOCOLE_PACC_CAUSAL_PROSPECTIF_V1.json et refuse les données réelles tant que
la fiche de préenregistrement public n'ouvre pas la porte d'exécution.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PROTOCOLE_PACC_CAUSAL_PROSPECTIF_V1.json"
REGISTRATION = HERE / "VES-PACC-INT-01.registration.json"
ANALYSIS = HERE / "analyser_ves_pacc_int_01.py"
SCHEMA = HERE / "SCHEMA_ENTREE_VES_PACC_INT_01.json"
DEFAULT_RAW = HERE / "ves_pacc_int_01_raw"
DEFAULT_NPZ = HERE / "ves_pacc_int_01_analysis_ready.npz"
DEFAULT_META = HERE / "ves_pacc_int_01_analysis_ready.metadata.json"
ARMS = ("control", "do_m", "sham")
RESPONSE_COLUMNS = ("A400", "NR640", "NR_RATIO", "CALCEIN")
ANCHOR_COLUMNS = ("anchor_A400", "anchor_NR640", "anchor_NR_RATIO", "anchor_CALCEIN")


class InputError(ValueError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise InputError(f"fichier absent: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise InputError(f"table vide: {path.name}")
    return rows


def _require_columns(rows: list[dict[str, str]], required: list[str], name: str) -> None:
    columns = set(rows[0])
    missing = [col for col in required if col not in columns]
    if missing:
        raise InputError(f"{name}: colonnes absentes: {missing}")


def _number(value: str, label: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise InputError(f"valeur numérique invalide pour {label}: {value!r}") from exc
    if not np.isfinite(result):
        raise InputError(f"valeur non finie pour {label}")
    return result


def registration_gate() -> dict[str, Any]:
    registration = load_json(REGISTRATION)
    if registration.get("source_sha256") != sha256(PROTOCOL):
        raise SystemExit("Preparation gate closed: protocol SHA-256 differs from the registered frozen source.")
    if registration.get("analysis_script_sha256") != sha256(ANALYSIS):
        raise SystemExit("Preparation gate closed: analysis-script SHA-256 differs from the registered frozen source.")
    if not (
        registration.get("status") == "publicly_registered"
        and registration.get("public_url")
        and registration.get("registered_at")
    ):
        raise SystemExit(
            "Preparation gate closed: public preregistration URL and timestamp are required before prospective test data."
        )
    return registration


def _architecture_passes(
    arm_rows: dict[tuple[str, str], dict[str, str]], parent_ids: list[str], protocol: dict[str, Any]
) -> bool:
    tol = protocol["A_architecture"]["tolerances"]
    checks = (
        ("post_pH", float(tol["post_handling_pH_abs_difference_max"]), False),
        ("temperature_C", float(tol["temperature_abs_difference_C_max"]), False),
        ("total_amphiphile_mM", float(tol["total_amphiphile_relative_difference_max"]), True),
        ("final_volume_uL", float(tol["final_volume_relative_difference_max"]), True),
        ("elapsed_handling_min", float(tol["elapsed_handling_abs_difference_minutes_max"]), False),
    )
    for parent in parent_ids:
        rows = [arm_rows[(parent, arm)] for arm in ARMS]
        for column, maximum, relative in checks:
            values = np.asarray([_number(row[column], f"{parent}/{column}") for row in rows], dtype=float)
            spread = float(values.max() - values.min())
            if relative:
                reference = abs(float(values[0]))
                if reference <= 0:
                    return False
                spread /= reference
            if spread > maximum + 1e-12:
                return False
    return True


def prepare_tables(
    parents: list[dict[str, str]],
    arms: list[dict[str, str]],
    responses: list[dict[str, str]],
    execution_log: dict[str, Any],
    protocol: dict[str, Any],
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    schema = load_json(SCHEMA)
    _require_columns(parents, schema["files"]["parents.csv"]["required_columns"], "parents.csv")
    _require_columns(arms, schema["files"]["arms.csv"]["required_columns"], "arms.csv")
    _require_columns(responses, schema["files"]["responses.csv"]["required_columns"], "responses.csv")

    parent_map: dict[str, dict[str, str]] = {}
    for row in parents:
        parent = row["parent_id"].strip()
        if not parent or parent in parent_map:
            raise InputError(f"parent_id vide ou dupliqué: {parent!r}")
        for anchor in ANCHOR_COLUMNS:
            if _number(row[anchor], f"{parent}/{anchor}") <= 0:
                raise InputError(f"{parent}/{anchor} doit être strictement positif pour la normalisation")
        parent_map[parent] = row
    parent_ids = sorted(parent_map)

    arm_map: dict[tuple[str, str], dict[str, str]] = {}
    for row in arms:
        key = (row["parent_id"].strip(), row["arm"].strip())
        if key[0] not in parent_map:
            raise InputError(f"arms.csv: parent inconnu: {key[0]}")
        if key[1] not in ARMS:
            raise InputError(f"arms.csv: bras inconnu: {key[1]}")
        if key in arm_map:
            raise InputError(f"arms.csv: doublon {key}")
        for column in ("post_z_average_nm", "post_pdi", "post_pH", "temperature_C", "total_amphiphile_mM", "final_volume_uL", "elapsed_handling_min"):
            _number(row[column], f"{key}/{column}")
        arm_map[key] = row
    expected_arm_keys = {(parent, arm) for parent in parent_ids for arm in ARMS}
    if set(arm_map) != expected_arm_keys:
        missing = sorted(expected_arm_keys - set(arm_map))
        extra = sorted(set(arm_map) - expected_arm_keys)
        raise InputError(f"arms.csv: structure incomplète; missing={missing[:5]} extra={extra[:5]}")

    challenge_ids = [entry["id"] for entry in protocol["Theta"]["challenge_set"]]
    response_map: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in responses:
        key = (row["parent_id"].strip(), row["arm"].strip(), row["challenge_id"].strip())
        if key[0] not in parent_map or key[1] not in ARMS or key[2] not in challenge_ids:
            raise InputError(f"responses.csv: clé hors protocole: {key}")
        if key in response_map:
            raise InputError(f"responses.csv: doublon {key}")
        for column in RESPONSE_COLUMNS:
            _number(row[column], f"{key}/{column}")
        response_map[key] = row
    expected_response_keys = {
        (parent, arm, challenge) for parent in parent_ids for arm in ARMS for challenge in challenge_ids
    }
    if set(response_map) != expected_response_keys:
        missing = sorted(expected_response_keys - set(response_map))
        extra = sorted(set(response_map) - expected_response_keys)
        raise InputError(f"responses.csv: structure incomplète; missing={missing[:5]} extra={extra[:5]}")

    required_log = schema["files"]["execution_log.json"]["required_fields"]
    absent_log = [name for name in required_log if name not in execution_log]
    if absent_log:
        raise InputError(f"execution_log.json: champs absents: {absent_log}")
    deviations = execution_log.get("protocol_deviations")
    if not isinstance(deviations, list):
        raise InputError("execution_log.json: protocol_deviations doit être une liste")

    cubes: dict[str, np.ndarray] = {}
    arm_to_output = {
        "control": "control_response",
        "do_m": "intervention_response",
        "sham": "sham_response",
    }
    for arm, output_name in arm_to_output.items():
        cube = np.empty((len(parent_ids), len(challenge_ids), len(RESPONSE_COLUMNS)), dtype=float)
        for i, parent in enumerate(parent_ids):
            anchors = np.asarray([_number(parent_map[parent][col], f"{parent}/{col}") for col in ANCHOR_COLUMNS])
            for j, challenge in enumerate(challenge_ids):
                row = response_map[(parent, arm, challenge)]
                future = np.asarray([_number(row[col], f"{parent}/{arm}/{challenge}/{col}") for col in RESPONSE_COLUMNS])
                cube[i, j, :] = future / anchors
        cubes[output_name] = cube

    do_z = np.asarray([_number(arm_map[(p, "do_m")]["post_z_average_nm"], f"{p}/do_m/Z") for p in parent_ids])
    do_pdi = np.asarray([_number(arm_map[(p, "do_m")]["post_pdi"], f"{p}/do_m/PDI") for p in parent_ids])
    control_z = np.asarray([_number(arm_map[(p, "control")]["post_z_average_nm"], f"{p}/control/Z") for p in parent_ids])
    control_pdi = np.asarray([_number(arm_map[(p, "control")]["post_pdi"], f"{p}/control/PDI") for p in parent_ids])
    sham_z = np.asarray([_number(arm_map[(p, "sham")]["post_z_average_nm"], f"{p}/sham/Z") for p in parent_ids])
    sham_pdi = np.asarray([_number(arm_map[(p, "sham")]["post_pdi"], f"{p}/sham/PDI") for p in parent_ids])

    targets = protocol["m"]["target_levels"]
    do_text = str(targets.get("do(m)", ""))
    sham_text = str(targets.get("sham", ""))
    # Les seuils de fidélité restent définis une seule fois dans le protocole gelé.
    # Le préparateur les extrait de cette source canonique au lieu de les recopier.
    do_match = re.search(r"Z-average must be ([0-9.]+)[–-]([0-9.]+) nm and median PDI <= ?([0-9.]+)", do_text)
    sham_match = re.search(r"Z-average change relative to control must be <= ?([0-9.]+)% and absolute median PDI change <= ?([0-9.]+)", sham_text)
    if not do_match or not sham_match:
        raise InputError("protocole incomplet ou non interprétable: niveaux numériques do(m)/sham absents")
    do_z_min, do_z_max, do_pdi_max = map(float, do_match.groups())
    sham_z_relative_max = float(sham_match.group(1)) / 100.0
    sham_pdi_abs_max = float(sham_match.group(2))

    do_target_passes = bool(
        do_z_min <= float(np.median(do_z)) <= do_z_max
        and float(np.median(do_pdi)) <= do_pdi_max
    )
    control_z_median = float(np.median(control_z))
    sham_z_median = float(np.median(sham_z))
    z_relative = abs(sham_z_median - control_z_median) / abs(control_z_median) if control_z_median != 0 else np.inf
    sham_fidelity = bool(
        z_relative <= sham_z_relative_max
        and abs(float(np.median(sham_pdi)) - float(np.median(control_pdi))) <= sham_pdi_abs_max
    )

    architecture = _architecture_passes(arm_map, parent_ids, protocol)
    procedural_ok = bool(
        execution_log["m_targeted_only_confirmed_before_decoding"]
        and execution_log["responses_collected_after_intervention"]
        and execution_log["randomization_seed_recorded"]
        and execution_log["blinding_preserved_until_analysis_table_freeze"]
        and not deviations
    )
    matching = {
        "X_matched": True,
        "Theta_matched": True,
        "architecture_matched": architecture,
        "m_targeted_only": bool(procedural_ok and architecture),
        "independent_units": len(parent_ids) == len(set(parent_ids)),
        "challenge_set_predeclared": True,
        "thresholds_predeclared": True,
        "future_response_after_intervention": bool(execution_log["responses_collected_after_intervention"]),
    }

    meta = {
        "schema": "oric.ves-pacc-int-analysis-ready-metadata.v1",
        "protocol_id": protocol["id"],
        "protocol_sha256": sha256(PROTOCOL),
        "analysis_script_sha256": sha256(ANALYSIS),
        "parent_ids": parent_ids,
        "challenge_order": challenge_ids,
        "response_dimension_order": [entry["id"] for entry in protocol["R"]["response_dimensions"]],
        "matching": matching,
        "fidelity": {
            "do_m_population_target_passes": do_target_passes,
            "sham_structural_fidelity_passes": sham_fidelity,
            "procedural_log_complete_and_deviation_free": procedural_ok,
            "thresholds_read_from_frozen_protocol": {
                "do_m_z_average_nm": [do_z_min, do_z_max],
                "do_m_pdi_max": do_pdi_max,
                "sham_z_relative_change_max": sham_z_relative_max,
                "sham_pdi_abs_change_max": sham_pdi_abs_max,
            },
        },
        "protocol_deviations": deviations,
        "strict_preparation_passes": bool(all(matching.values()) and do_target_passes and sham_fidelity and procedural_ok),
    }
    return cubes, meta


def prepare_from_directory(raw_dir: Path) -> tuple[dict[str, np.ndarray], dict[str, Any], dict[str, str]]:
    protocol = load_json(PROTOCOL)
    parents_path = raw_dir / "parents.csv"
    arms_path = raw_dir / "arms.csv"
    responses_path = raw_dir / "responses.csv"
    log_path = raw_dir / "execution_log.json"
    parents = read_csv(parents_path)
    arms = read_csv(arms_path)
    responses = read_csv(responses_path)
    execution_log = load_json(log_path)
    cubes, meta = prepare_tables(parents, arms, responses, execution_log, protocol)
    hashes = {path.name: sha256(path) for path in (parents_path, arms_path, responses_path, log_path)}
    meta["raw_input_sha256"] = hashes
    return cubes, meta, hashes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW)
    parser.add_argument("--output-npz", type=Path, default=DEFAULT_NPZ)
    parser.add_argument("--output-metadata", type=Path, default=DEFAULT_META)
    parser.add_argument("--check-schema", action="store_true", help="valide uniquement la cohérence schéma/protocole, sans lire de données")
    args = parser.parse_args(argv)

    protocol = load_json(PROTOCOL)
    schema = load_json(SCHEMA)
    frozen_challenges = [entry["id"] for entry in protocol["Theta"]["challenge_set"]]
    if schema["files"]["responses.csv"]["challenge_ids"] != frozen_challenges:
        raise SystemExit("Input schema differs from the frozen challenge set.")
    if args.check_schema:
        print(json.dumps({"status": "ok", "protocol_id": protocol["id"], "challenges": len(frozen_challenges)}, ensure_ascii=False))
        return 0

    registration_gate()
    cubes, meta, _ = prepare_from_directory(args.raw_dir)
    args.output_npz.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(args.output_npz, **cubes)
    args.output_metadata.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "prepared", "n": len(meta["parent_ids"]), "strict_preparation_passes": meta["strict_preparation_passes"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
