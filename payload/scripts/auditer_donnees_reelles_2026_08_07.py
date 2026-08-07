#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
import math
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "plateforme/source_corrigee/src"
sys.path.insert(0, str(SRC))

from oric_full.domains.matter import analyze_condensation  # noqa: E402
from oric_full.domains.planetary import late_accretion_mixture, volatile_closure  # noqa: E402

DATA = ROOT / "plateforme/campagne_maximale_reelle/data"
PALEO = ROOT / "donnees_externes/donnees_reelles_2026_08_07/paleoclimat_long"
OUT = ROOT / "plateforme/campagne_maximale_reelle/resultats_empiriques/audit_donnees_2026_08_07.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()



def numeric_column_after_marker(path: Path, marker: str, index: int) -> list[float]:
    text = path.read_text(encoding="latin-1")
    marker_index = text.find(marker)
    if marker_index < 0:
        raise ValueError(f"Marqueur absent dans {path.name}: {marker}")
    values: list[float] = []
    for line in text[marker_index + len(marker):].splitlines():
        parts = line.strip().split()
        if len(parts) <= index:
            continue
        try:
            values.append(float(parts[index]))
        except ValueError:
            continue
    if not values:
        raise ValueError(f"Aucune valeur numérique lue dans {path.name}")
    return values


def audit_long_paleoclimate() -> dict:
    specs = {
        "epica_co2": ("edc-co2-2008.txt", "Age(yrBP)    CO2(ppmv)", 0, "yr_BP", "ae2ecff8e048c2357094c14742fb83eecc97c896707fc1f983614818427ae390"),
        "epica_deuterium_temperature": ("edc3deuttemp2007.txt", "Bag         ztop          Age         Deuterium    Temperature", 2, "yr_BP", "b801fc2e422d427524619be25b50ee86fd63b36eb440eb5044d9bec12a4d1747"),
        "lr04_benthic_d18o": ("lisiecki2005_LR04.txt", "Time      d18O      Error", 0, "kyr_BP", "973a52d988da04333c98c3fc0cb51babac2fa9bb1c05d42de3d6df726d96b6fc"),
        "vostok_deuterium_temperature": ("vostok_deutnat.txt", "Depth corrected\tIce age (GT4)\tdeut\tdeltaTS", 1, "yr_BP", "c69eca96499bece4b2f65d4e40240f52e0bfb4027383b3f2db68a1b3e36c75f6"),
    }
    result = {}
    for key, (name, marker, age_index, unit, expected_hash) in specs.items():
        path = PALEO / name
        if sha256(path) != expected_hash:
            raise SystemExit(f"Empreinte paléoclimatique inattendue: {name}")
        ages = numeric_column_after_marker(path, marker, age_index)
        result[key] = {
            "file": str(path.relative_to(ROOT)),
            "sha256": expected_hash,
            "numeric_age_rows": len(ages),
            "age_min": min(ages),
            "age_max": max(ages),
            "age_unit": unit,
            "empirical_test_ids_enabled": [],
        }
    result["interpretation_limit"] = (
        "Ces quatre séries longues lèvent le manque de durée du seul fichier NOAA 0-22 ka, "
        "mais elles ne déclenchent aucun test orbital-climat tant qu'un protocole long, "
        "ses critères, son indépendance chronologique et ses contrôles ne sont pas gelés."
    )
    return result


def json_safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(v) for v in value]
    return value

def main() -> dict:
    thermo_path = DATA / "thermochemical_phases.csv"
    late_path = DATA / "late_accretion_tracers.csv"
    volatile_path = DATA / "volatile_inventory.csv"
    climate_path = DATA / "modern_climate_timeseries.csv"

    thermo = pd.read_csv(thermo_path)
    late = pd.read_csv(late_path)
    volatile = pd.read_csv(volatile_path)
    climate = pd.read_csv(climate_path)

    thermo_audit = analyze_condensation(thermo)
    late_audit = late_accretion_mixture(late)
    volatile_audit = volatile_closure(volatile)

    climate_vars = sorted(climate["variable"].dropna().astype(str).unique().tolist())
    climate_is_temperature_only = bool(climate_vars) and all("temperature" in item.lower() for item in climate_vars)

    payload = {
        "schema_version": 1,
        "status": "ok",
        "rule": "Audit de ressources réelles/externes. Aucun pass technique n'est converti ici en preuve scientifique.",
        "assets": {
            "thermochemical_phases": {
                "sha256": sha256(thermo_path),
                "audit": thermo_audit.metrics,
                "limitations": thermo_audit.details.get("interpretation_limit"),
                "empirical_test_ids_enabled": [],
            },
            "late_accretion_tracers": {
                "sha256": sha256(late_path),
                "audit": late_audit.metrics,
                "tracer_counts": late_audit.details.get("tracer_counts"),
                "limitations": late_audit.details.get("interpretation_limit"),
                "empirical_test_ids_enabled": ["P5-001"],
            },
            "volatile_inventory": {
                "sha256": sha256(volatile_path),
                "audit": volatile_audit.metrics,
                "row_audit": volatile_audit.details.get("row_audit"),
                "limitations": volatile_audit.details.get("interpretation_limit"),
                "empirical_test_ids_enabled": [],
            },
            "modern_climate_timeseries": {
                "sha256": sha256(climate_path),
                "rows": int(len(climate)),
                "variables": climate_vars,
                "temperature_reconstructions_only": climate_is_temperature_only,
                "empirical_test_ids_enabled": [],
                "limitations": "Plusieurs reconstructions de température ne constituent ni des compartiments de mémoire ni un forçage climatique.",
            },
            "long_paleoclimate_sources": audit_long_paleoclimate(),
        },
        "planetary_histories": {
            "present": (DATA / "planetary_histories.csv").exists(),
            "required_state": "absent_until_cell_level_primary_provenance_exists",
        },
    }
    if payload["planetary_histories"]["present"]:
        raise SystemExit("planetary_histories.csv ne doit pas être introduit par cette mise à jour")
    if late_audit.metrics["required_tracer_coverage_fraction"] != 1.0:
        raise SystemExit("La compilation GEOROC ne couvre pas l'ensemble Mo-Ru-W-Os-Ir-Au")
    if late_audit.metrics["unit_inconsistency_count"] != 0.0:
        raise SystemExit("Unités incohérentes entre mesures GEOROC")
    if volatile_audit.metrics["complete_budget_rows"] != 0.0:
        raise SystemExit("Le statut des budgets volatils a changé: réauditer avant de revendiquer une fermeture")
    if not climate_is_temperature_only:
        raise SystemExit("Le contenu climatique a changé: réauditer la portée CL1/CL2")

    payload = json_safe(payload)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False))
    return payload


if __name__ == "__main__":
    main()
