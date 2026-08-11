from __future__ import annotations

import json
from pathlib import Path

BRANCH_ROOT = Path(__file__).resolve().parents[1]
SOURCE = BRANCH_ROOT / "couche_astronomique/resultats/real_science_max/execution_results.json"
OUT = Path(__file__).resolve().parent / "resultats"
METRICS = (
    "earth_eccentricity_mean",
    "earth_eccentricity_std",
    "earth_eccentricity_max",
)
REFERENCE_VARIANTS = (
    "baseline_2myr_dt4p8828125",
    "baseline_2myr_elements_dt5",
    "full_la2010_bodies_2myr_dt5",
)


def main() -> dict[str, object]:
    rows = json.loads(SOURCE.read_text(encoding="utf-8"))
    summaries = {
        row["name"]: row["summary"]
        for row in rows
        if row.get("ok") and row.get("summary") and row["summary"].get("kind") == "nbody"
    }
    baseline = summaries["baseline_2myr_dt5"]
    missing_references = [name for name in REFERENCE_VARIANTS if name not in summaries]
    if missing_references:
        raise KeyError(f"références absentes: {missing_references}")

    # Enveloppe conservatrice : pas de temps, représentation initiale et nombre de corps.
    envelope = {
        metric: max(abs(baseline[metric] - summaries[name][metric]) for name in REFERENCE_VARIANTS)
        for metric in METRICS
    }
    interventions = sorted(
        name
        for name in summaries
        if (name.startswith("jupiter_") or name.startswith("saturn_")) and name.endswith("_2myr")
    )
    details: list[dict[str, object]] = []
    accessible_cells = 0
    for name in interventions:
        ratios = {
            metric: abs(summaries[name][metric] - baseline[metric]) / max(envelope[metric], 1e-15)
            for metric in METRICS
        }
        cells = {metric: value >= 1.0 for metric, value in ratios.items()}
        accessible_cells += sum(cells.values())
        intervention_accessible = sum(cells.values()) >= 2
        details.append(
            {
                "intervention": name,
                "effect_over_reference_envelope": ratios,
                "accessible_dimensions": cells,
                "accessible_dimension_count": sum(cells.values()),
                "intervention_accessible": intervention_accessible,
            }
        )

    total_cells = len(interventions) * len(METRICS)
    intervention_count = sum(bool(item["intervention_accessible"]) for item in details)
    pacc_interventions = intervention_count / len(interventions)
    pacc_dimensions = accessible_cells / total_cells
    result = {
        "definition": (
            "Pacc_interventions est la fraction des interventions admissibles qui dépassent "
            "l'enveloppe de référence sur au moins deux métriques. Pacc_dimensions est la "
            "fraction des couples intervention-métrique qui dépassent cette enveloppe."
        ),
        "baseline": "baseline_2myr_dt5",
        "reference_variants": list(REFERENCE_VARIANTS),
        "reference_envelope": envelope,
        "metrics": list(METRICS),
        "interventions": len(interventions),
        "accessible_interventions": intervention_count,
        "accessible_dimension_cells": accessible_cells,
        "total_dimension_cells": total_cells,
        "Pacc_interventions": pacc_interventions,
        "Pacc_dimensions": pacc_dimensions,
        "detail": details,
        "status": (
            "measured_with_non_saturated_dimension_score"
            if 0.0 < pacc_dimensions < 1.0
            else "measured_boundary_value"
        ),
        "limit": (
            "Cette mesure porte sur le domaine d'interventions déjà calculé. Elle ne constitue "
            "pas une fréquence naturelle ni une probabilité universelle."
        ),
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "PACC_ASTRONOMIQUE.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


if __name__ == "__main__":
    main()
