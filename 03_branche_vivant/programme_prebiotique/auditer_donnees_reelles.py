#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
DATA = HERE / "donnees_reelles"
TRAJECTORIES = DATA / "trajectoires_population"
OUT = HERE / "resultats"
OUT.mkdir(exist_ok=True)


def audit_lineage_files() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for path in sorted(DATA.glob("*.csv")):
        text = path.read_text(encoding="utf-8-sig")
        if "GABARIT_SYNTHETIQUE" in text:
            rejected.append({"file": path.name, "reason": "synthetic_marker"})
            continue
        with path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream, delimiter=";"))
        if rows:
            accepted.append({"file": path.name, "rows": len(rows)})
        else:
            rejected.append({"file": path.name, "reason": "empty"})
    return accepted, rejected


def audit_population_trajectories() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    required = {
        "branch",
        "round",
        "sequence_id",
        "cluster",
        "frequency",
        "relative_frequency",
        "source_table",
    }
    for path in sorted(TRAJECTORIES.glob("*.csv")):
        with path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        if not rows:
            rejected.append({"file": path.name, "reason": "empty"})
            continue
        missing = sorted(required.difference(rows[0]))
        if missing:
            rejected.append({"file": path.name, "reason": "missing_columns", "columns": missing})
            continue
        branches = sorted({row["branch"] for row in rows})
        rounds = sorted({int(float(row["round"])) for row in rows})
        sequences = sorted({(row["branch"], row["sequence_id"]) for row in rows})
        branch_rounds: dict[str, list[int]] = {}
        for branch in branches:
            branch_rounds[branch] = sorted(
                {int(float(row["round"])) for row in rows if row["branch"] == branch}
            )
        accepted.append(
            {
                "file": path.name,
                "rows": len(rows),
                "branches": branches,
                "rounds": rounds,
                "branch_rounds": branch_rounds,
                "tracked_sequence_series": len(sequences),
                "grain": "branche-cycle-sequence",
                "data_type": "population_frequency_trajectory",
            }
        )
    return accepted, rejected


lineages, rejected_lineages = audit_lineage_files()
trajectories, rejected_trajectories = audit_population_trajectories()

if lineages:
    status_name = "donnees_de_lignees_presentes_a_valider"
    conclusion = (
        "Des tables parent-descendant réelles sont présentes. Elles doivent encore passer "
        "le validateur de transmission avant tout verdict scientifique."
    )
elif trajectories:
    status_name = "trajectoires_population_reelles_sans_lignees"
    conclusion = (
        "Deux trajectoires expérimentales de populations d’ARN catalytique sur huit cycles "
        "sont intégrées. Elles mesurent une dynamique de composition réelle, mais ne relient "
        "pas des compartiments parents à leurs descendants. La continuité héréditaire "
        "prébiotique reste donc non testable avec ces données."
    )
else:
    status_name = "aucune_donnee_reelle"
    conclusion = (
        "Le protocole et le validateur existent, mais aucune donnée expérimentale réelle "
        "ne permet encore de tester la transmission prébiotique."
    )

status = {
    "real_lineage_files": len(lineages),
    "accepted_lineages": lineages,
    "rejected_lineages": rejected_lineages,
    "real_population_trajectory_files": len(trajectories),
    "accepted_population_trajectories": trajectories,
    "rejected_population_trajectories": rejected_trajectories,
    "population_trajectory_available": bool(trajectories),
    "criterion_testable": bool(lineages),
    "status": status_name,
    "conclusion": conclusion,
    "scientific_boundary": (
        "Une trajectoire de fréquences de séquences n’est pas une lignée de compartiments, "
        "une preuve de transmission fonctionnelle ou une démonstration d’hérédité."
    ),
}

(OUT / "audit_donnees_reelles.json").write_text(
    json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
)

trajectory_text = ""
if trajectories:
    item = trajectories[0]
    trajectory_text = (
        f"\n## Trajectoire réelle disponible\n\n"
        f"- fichier : `{item['file']}`\n"
        f"- {item['rows']} observations au grain branche-cycle-séquence\n"
        f"- {len(item['branches'])} branches expérimentales\n"
        f"- cycles {min(item['rounds'])} à {max(item['rounds'])}\n"
        f"- {item['tracked_sequence_series']} séries de séquences suivies\n"
        f"- source : Papastavrou, Horning et Joyce, DOI du jeu de données "
        f"`10.5061/dryad.rxwdbrvgs`\n"
    )

report = (
    "# Audit des données prébiotiques réelles\n\n"
    + conclusion
    + trajectory_text
    + "\n## Limite décisive\n\n"
    + status["scientific_boundary"]
    + "\n"
)
(OUT / "RAPPORT_DONNEES_REELLES.md").write_text(report, encoding="utf-8", newline="\n")
print(json.dumps(status, ensure_ascii=False, indent=2))
