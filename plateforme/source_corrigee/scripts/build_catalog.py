from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "PLAN_DIRECTEUR_TESTS_ORI-C_COMPLET.md"
OUT_JSON = ROOT / "catalogue" / "catalogue_tests.json"
OUT_CSV = ROOT / "catalogue" / "catalogue_tests.csv"

ENGINE_BY_WP = {
    "S1": "core_formal",
    "S2": "intervention",
    "S3": "relation_graph",
    "M1": "matter_transitions",
    "M2": "nucleosynthesis",
    "M3": "astrochemistry",
    "M4": "condensation",
    "M5": "matter_value",
    "P1": "planetary_provenance",
    "P2": "planetesimal_thermal",
    "P3": "metal_silicate",
    "P4": "volatile_budget",
    "P5": "late_accretion",
    "P6": "planetary_value",
    "A1": "astronomy_repro",
    "A2": "astronomy_initial_conditions",
    "A3": "astronomy_physics",
    "A4": "astronomy_causality",
    "A5": "astronomy_spectra",
    "A6": "astronomy_validation",
    "C1": "paleoclimate_replication",
    "C2": "paleoclimate_prospective",
    "C3": "memory_families",
    "C4": "climate_models",
    "C5": "climate_data",
    "C6": "climate_discrimination",
    "C7": "climate_mechanisms",
    "CL1": "modern_climate_memory",
    "CL2": "modern_climate_dhl",
    "CL3": "modern_climate_pacc",
    "CL4": "modern_climate_validation",
    "V1": "prebiotic_design",
    "V2": "prebiotic_components",
    "V3": "prebiotic_coupling",
    "V4": "prebiotic_matrix",
    "V5": "prebiotic_space",
    "V6": "prebiotic_transition",
    "B1": "cell_architecture",
    "B2": "endosymbiosis",
    "B3": "biology_value",
    "R1": "antibiotic_design",
    "R2": "antibiotic_histories",
    "R3": "antibiotic_measurements",
    "R4": "antibiotic_oric",
    "R5": "antibiotic_competitors",
    "R6": "antibiotic_replication",
    "T1": "cross_domain_benchmark",
    "T2": "generality",
    "T3": "predictive_value",
    "T4": "compression",
    "T5": "red_team",
}

DATASETS_BY_ENGINE = {
    "relation_graph": ["relations", "states"],
    "matter_transitions": ["matter_transitions"],
    "nucleosynthesis": ["nucleosynthesis_yields"],
    "astrochemistry": ["reaction_network", "molecular_inventory"],
    "condensation": ["thermochemical_phases"],
    "matter_value": ["matter_transitions"],
    "planetary_provenance": ["isotope_tracers"],
    "planetesimal_thermal": ["chronometers", "body_properties"],
    "metal_silicate": ["partition_experiments"],
    "volatile_budget": ["volatile_inventory"],
    "late_accretion": ["late_accretion_tracers"],
    "planetary_value": ["planetary_histories"],
    "astronomy_repro": ["orbital_initial_conditions"],
    "astronomy_initial_conditions": ["orbital_initial_conditions", "ephemerides"],
    "astronomy_physics": ["orbital_initial_conditions"],
    "astronomy_causality": ["orbital_initial_conditions"],
    "astronomy_spectra": ["orbital_timeseries"],
    "astronomy_validation": ["orbital_timeseries", "orbital_reference"],
    "paleoclimate_replication": ["paleoclimate_timeseries"],
    "paleoclimate_prospective": ["paleoclimate_timeseries"],
    "memory_families": ["paleoclimate_timeseries"],
    "climate_models": ["paleoclimate_timeseries"],
    "climate_data": ["paleoclimate_timeseries"],
    "climate_discrimination": ["paleoclimate_timeseries"],
    "climate_mechanisms": ["paleoclimate_timeseries"],
    "modern_climate_memory": ["modern_climate_timeseries"],
    "modern_climate_dhl": ["modern_climate_timeseries"],
    "modern_climate_pacc": ["modern_climate_ensemble"],
    "modern_climate_validation": ["modern_climate_ensemble"],
    "prebiotic_design": ["prebiotic_design"],
    "prebiotic_components": ["prebiotic_lineages"],
    "prebiotic_coupling": ["prebiotic_lineages"],
    "prebiotic_matrix": ["prebiotic_lineages"],
    "prebiotic_space": ["prebiotic_lineages"],
    "prebiotic_transition": ["prebiotic_lineages"],
    "cell_architecture": ["cell_architecture"],
    "endosymbiosis": ["endosymbiosis_events"],
    "biology_value": ["biology_cases"],
    "antibiotic_design": ["antibiotic_design"],
    "antibiotic_histories": ["antibiotic_cycles"],
    "antibiotic_measurements": ["antibiotic_measurements"],
    "antibiotic_oric": ["antibiotic_cycles", "antibiotic_measurements"],
    "antibiotic_competitors": ["antibiotic_cycles", "antibiotic_measurements"],
    "antibiotic_replication": ["antibiotic_measurements"],
    "cross_domain_benchmark": ["benchmark_cases"],
    "generality": ["benchmark_cases"],
    "predictive_value": ["benchmark_cases"],
    "compression": ["benchmark_cases"],
    "red_team": ["benchmark_cases"],
}

LAB_WORDS = (
    "laboratoire", "chémostat", "pétrologie expérimentale", "protocellule",
    "culture", "espèce", "antibiotique", "reconstruction d’allèle", "stocks indépendants",
)
HUMAN_WORDS = (
    "expert", "codeur", "évaluateur", "audit", "lecture", "publier", "préenregistr",
    "rapport contradictoire", "littérature", "spécialiste", "aveugle par des",
)
EXTERNAL_WORDS = (
    "rebound", "éphémér", "la2004", "la2010", "code public", "codes publics",
    "autre code", "intégrateur indépendant", "seconde équipe", "autre équipe",
)
DATA_WORDS = (
    "compiler", "observation", "données", "base de données", "météorite", "isotope",
    "expériences de partage", "chronomètre", "inventaire moléculaire", "séquence",
)


def mode_for(description: str, engine: str) -> str:
    text = description.casefold()
    if any(word in text for word in LAB_WORDS):
        return "laboratory"
    if any(word in text for word in HUMAN_WORDS):
        return "human_review"
    if any(word in text for word in EXTERNAL_WORDS):
        return "external_code"
    if any(word in text for word in DATA_WORDS) or engine in DATASETS_BY_ENGINE:
        return "data_required"
    return "automated"


def priority_for(wp: str, description: str) -> int:
    text = description.casefold()
    if wp in {"S1", "S2", "S3", "M1", "C1", "C2", "T1", "T3"}:
        return 1
    if "préenregistr" in text or "hors échantillon" in text or "validation" in text:
        return 1
    if "autre équipe" in text or "second laboratoire" in text:
        return 3
    return 2


def parse_plan() -> list[dict]:
    lines = PLAN.read_text(encoding="utf-8").splitlines()
    current_wp: str | None = None
    current_section = ""
    ordinal_by_wp: dict[str, int] = {}
    records: list[dict] = []

    for line_no, raw in enumerate(lines, start=1):
        wp_match = re.match(r"^##\s+WP-([A-Z]+\d+)\.\s*(.+)$", raw)
        if wp_match:
            current_wp = wp_match.group(1)
            current_section = wp_match.group(2).strip()
            ordinal_by_wp.setdefault(current_wp, 0)
            continue
        sub_match = re.match(r"^###\s+(.+)$", raw)
        if sub_match and current_wp:
            current_section = sub_match.group(1).strip()
            continue
        if raw.startswith("## ") and not wp_match:
            current_wp = None
            continue
        if not current_wp:
            continue
        item_match = re.match(r"^\s*(\d+)\.\s+(.+)$", raw)
        bullet_match = re.match(r"^\s*-\s+(.+)$", raw)
        if item_match:
            description = item_match.group(2).strip()
        elif bullet_match:
            description = bullet_match.group(1).strip()
        else:
            continue
        if not description or description.endswith(":"):
            continue
        ordinal_by_wp[current_wp] += 1
        ordinal = ordinal_by_wp[current_wp]
        engine = ENGINE_BY_WP.get(current_wp, "manual_protocol")
        mode = mode_for(description, engine)
        records.append(
            {
                "test_id": f"{current_wp}-{ordinal:03d}",
                "wp": current_wp,
                "section": current_section,
                "ordinal": ordinal,
                "description": description,
                "mode": mode,
                "engine": engine,
                "required_datasets": DATASETS_BY_ENGINE.get(engine, []),
                "confirmatory": any(
                    token in description.casefold()
                    for token in ("hors échantillon", "préenregistr", "aveugle", "validation", "réplication")
                ),
                "priority": priority_for(current_wp, description),
                "source_line": line_no,
            }
        )
    return records


def main() -> int:
    records = parse_plan()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    resources = ROOT / "src" / "oric_full" / "resources"
    resources.mkdir(parents=True, exist_ok=True)
    (resources / "catalogue_tests.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    import csv

    rows = []
    for record in records:
        row = dict(record)
        row["required_datasets"] = ";".join(record["required_datasets"])
        rows.append(row)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    import shutil
    shutil.copy2(OUT_CSV, resources / "catalogue_tests.csv")
    print(f"{len(records)} tests enregistrés dans {OUT_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
