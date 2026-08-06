"""Produit un bilan transparent de l'intégration maximale des données réelles."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
DEFAULT_DATA = HERE / "data"

UNRESOLVED = {
    "thermochemical_phases.csv": {
        "tests": 15,
        "reason": "Les fichiers reçus ne contiennent pas une grille homogène phase-température-pression-énergie de Gibbs permettant les calculs de condensation.",
        "candidate": "Base thermodynamique quantitative Perple_X/JANAF ou équivalent avec licence et provenance.",
    },
    "planetary_histories.csv": {
        "tests": 11,
        "reason": "Les états orbitaux et les mesures noyau/bulk reçues ne constituent pas des histoires géochimiques complètes d'accrétion, redox, pertes et apports tardifs.",
        "candidate": "Cas planétaires ou météoritiques harmonisés avec étapes historiques et composition finale.",
    },
    "late_accretion_tracers.csv": {
        "tests": 10,
        "reason": "Les isotopes reçus ne relient pas encore des observations finales à plusieurs sources candidates d'accrétion tardive dans un modèle de mélange commun.",
        "candidate": "Compilation Mo-Ru-W-Os-Ir-Au et modèles de mélange documentés.",
    },
    "volatile_inventory.csv": {
        "tests": 9,
        "reason": "Le dégazage de Murchison et les modèles H-C noyau/bulk sont utiles mais ne ferment pas, par échantillon, les masses initiale, noyau, manteau, atmosphère et pertes.",
        "candidate": "Inventaires volatils quantitatifs fermés de corps différenciés et météorites.",
    },
}


def blocker_key(result: dict) -> str:
    message = result.get("message", "")
    details = result.get("details", {})
    if details.get("coverage_gaps"):
        datasets = ",".join(sorted(item["dataset"] for item in details["coverage_gaps"]))
        return f"portée partielle:{datasets}"
    if "mode données réelles strict" in message:
        return f"simulation/génération interdite:{details.get('engine', '')}"
    if message.startswith("Jeu de données absent:"):
        return f"fichier absent:{Path(message.split(':', 1)[1].strip()).name}"
    if message.startswith("Donnée manquante:"):
        return f"donnée invalide ou absente:{message.split(':', 1)[1].strip()}"
    return message


def rows(path: Path) -> int:
    if not path.exists():
        return 0
    return int(len(pd.read_csv(path)))


def build(results_json: Path, data_dir: Path) -> dict:
    campaign = json.loads(results_json.read_text(encoding="utf-8"))
    blocked = Counter(
        blocker_key(result)
        for result in campaign["results"]
        if result["outcome"] == "blocked"
    )
    coverage = json.loads((data_dir / "REAL_DATA_COVERAGE.json").read_text(encoding="utf-8"))
    data_summary = {
        "prebiotic_lineage_nodes": rows(data_dir / "prebiotic_lineages.csv"),
        "prebiotic_parent_offspring_pairs": rows(data_dir / "prebiotic_parent_offspring_pairs.csv"),
        "prebiotic_timecourse_rows": rows(data_dir / "prebiotic_timecourses.csv"),
        "prebiotic_timecourse_series": rows(data_dir / "prebiotic_timecourse_summary.csv"),
        "prebiotic_figure3_measurements": rows(data_dir / "prebiotic_auxiliary_measurements.csv"),
        "prebiotic_log_auxiliary_measurements": rows(data_dir / "prebiotic_log_auxiliary_measurements.csv"),
        "partition_experiments": rows(data_dir / "partition_experiments.csv"),
        "cell_architecture_rows": rows(data_dir / "cell_architecture.csv"),
        "antibiotic_design_rows": rows(data_dir / "antibiotic_design.csv"),
        "antibiotic_independent_fitness_rows": rows(data_dir / "antibiotic_fitness_real.csv"),
        "benchmark_cases": rows(data_dir / "benchmark_cases.csv"),
        "biology_cases": rows(data_dir / "biology_cases.csv"),
        "modern_climate_ensemble_rows": rows(data_dir / "modern_climate_ensemble.csv"),
        "reaction_network_rows": rows(data_dir / "reaction_network.csv"),
        "molecular_inventory_rows": rows(data_dir / "molecular_inventory.csv"),
        "nucleosynthesis_element_yields": rows(data_dir / "nucleosynthesis_yields.csv"),
        "nucleosynthesis_isotope_yields": rows(data_dir / "nucleosynthesis_isotope_yields.csv"),
        "isotope_tracer_rows": rows(data_dir / "isotope_tracers.csv"),
        "endosymbiosis_events": rows(data_dir / "endosymbiosis_events.csv"),
        "endosymbiont_hmm_rows": rows(data_dir / "endosymbiont_hmm_presence_absence.csv"),
        "murchison_degassing_rows": rows(data_dir / "murchison_degassing_profiles.csv"),
    }
    benchmark = pd.read_csv(data_dir / "benchmark_cases.csv")
    data_summary["benchmark_domains"] = benchmark.groupby("domain").size().astype(int).to_dict()
    payload = {
        "campaign_counts": campaign["counts"],
        "scientific_counts": campaign.get("scientific_counts", {}),
        "data_summary": data_summary,
        "blocked_root_causes": dict(blocked.most_common()),
        "coverage_registry": coverage,
        "unresolved_external_data": UNRESOLVED,
        "interpretation": (
            "Une réussite technique signifie que le moteur a exécuté une analyse couverte par les données. "
            "Elle ne constitue pas automatiquement une confirmation scientifique."
        ),
    }
    return payload


def markdown(payload: dict) -> str:
    counts = payload["campaign_counts"]
    scientific = payload["scientific_counts"]
    lines = [
        "# Audit maximal des données du dépôt",
        "",
        "## Résultat des 683 entrées",
        "",
        f"- Réussites techniques : **{counts.get('pass', 0)}**",
        f"- Blocages : **{counts.get('blocked', 0)}**",
        f"- Protocoles non exécutables informatiquement : **{counts.get('not_run', 0)}**",
        f"- Échecs : **{counts.get('fail', 0)}**",
        f"- Erreurs : **{counts.get('error', 0)}**",
        "",
        f"Verdicts scientifiques confirmatoires : **{scientific.get('supports', 0)} soutien**, "
        f"**{scientific.get('does_not_support', 0)} rejet**, "
        f"**{scientific.get('undetermined', 0)} indéterminés**.",
        "",
        "Une réussite technique signifie seulement que l'analyse couverte a été exécutée. Elle ne transforme pas le résultat en preuve confirmatoire.",
        "",
        "## Données réellement raccordées",
        "",
    ]
    for key, value in payload["data_summary"].items():
        lines.append(f"- `{key}` : {json.dumps(value, ensure_ascii=False, sort_keys=True)}")
    lines.extend(["", "## Causes racines des blocages restants", ""])
    for key, value in payload["blocked_root_causes"].items():
        lines.append(f"- **{value}** entrées : {key}")
    lines.extend(["", "## Données réellement absentes ou incompatibles", ""])
    for filename, item in payload["unresolved_external_data"].items():
        lines.extend([
            f"### `{filename}` — {item['tests']} entrées concernées",
            "",
            item["reason"],
            "",
            f"Source complémentaire nécessaire : {item['candidate']}",
            "",
        ])
    lines.extend([
        "## Règle de portée",
        "",
        "Les tables partielles ne débloquent que les identifiants explicitement couverts dans `REAL_DATA_COVERAGE.json`. Les autres restent bloqués même lorsque le fichier existe.",
    ])
    return "\n".join(lines) + "\n"



def canonical_markdown(payload: dict) -> str:
    counts = payload["campaign_counts"]
    scientific = payload["scientific_counts"]
    data = payload["data_summary"]
    return "\n".join([
        "# Campagne réelle consolidée - bilan canonique",
        "",
        "Ce bilan est généré à partir du fichier `results.json` de la même exécution. Il ne doit pas être remplacé par une copie statique plus ancienne.",
        "",
        "## Résultat technique des 683 entrées",
        "",
        f"- Réussites techniques : **{counts.get('pass', 0)}**",
        f"- Blocages : **{counts.get('blocked', 0)}**",
        f"- Protocoles non exécutables informatiquement : **{counts.get('not_run', 0)}**",
        f"- Échecs : **{counts.get('fail', 0)}**",
        f"- Erreurs : **{counts.get('error', 0)}**",
        "",
        "## Statut scientifique",
        "",
        f"- Soutient : **{scientific.get('supports', 0)}**",
        f"- Ne soutient pas : **{scientific.get('does_not_support', 0)}**",
        f"- Indéterminé : **{scientific.get('undetermined', 0)}**",
        f"- Non applicable : **{scientific.get('not_applicable', 0)}**",
        "",
        "Une réussite technique indique qu'un moteur a exécuté une analyse couverte par les données. Elle ne constitue pas automatiquement une confirmation scientifique.",
        "",
        "## Volumes canoniques utilisés",
        "",
        f"- Expériences de partage métal-silicate : **{data.get('partition_experiments', 0)}**",
        f"- Cas du benchmark transversal : **{data.get('benchmark_cases', 0)}**",
        f"- Lignées prébiotiques : **{data.get('prebiotic_lineage_nodes', 0)}** nœuds",
        f"- Relations parent-descendant : **{data.get('prebiotic_parent_offspring_pairs', 0)}**",
        f"- Ensemble climatique : **{data.get('modern_climate_ensemble_rows', 0)}** lignes",
        f"- Réseau réactionnel : **{data.get('reaction_network_rows', 0)}** réactions",
        f"- Rendements de nucléosynthèse : **{data.get('nucleosynthesis_element_yields', 0)}** élémentaires et **{data.get('nucleosynthesis_isotope_yields', 0)}** isotopiques",
        f"- Événements endosymbiotiques : **{data.get('endosymbiosis_events', 0)}**",
        "",
        "## Portée",
        "",
        "Les causes détaillées des blocages et les données encore absentes figurent dans `AUDIT_DONNEES_DEPOT.md`. Le registre `REAL_DATA_COVERAGE.json` maintient une liste d'autorisation stricte par protocole.",
        "",
    ])

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-json", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output-dir", type=Path, default=HERE)
    args = parser.parse_args()
    payload = build(args.results_json.resolve(), args.data_dir.resolve())
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "AUDIT_DONNEES_DEPOT.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "AUDIT_DONNEES_DEPOT.md").write_text(markdown(payload), encoding="utf-8")
    (args.output_dir / "BILAN_CANONIQUE.md").write_text(canonical_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["campaign_counts"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
