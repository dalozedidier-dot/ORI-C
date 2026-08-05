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
    "modern_climate_ensemble.csv": {
        "tests": 20,
        "reason": "Le dépôt contient GISTEMP observationnel, mais pas l'archive d'incertitude à 200 membres ni un ensemble multi-modèles/scénarios. L'ancien bilan annonçait 338 400 lignes sans que le fichier soit présent dans l'archive actuelle.",
        "candidate": "NASA GISTEMP KeySeries.zip pour les deux audits observationnels; CMIP/expériences dédiées restent nécessaires pour les trajectoires et restaurations.",
    },
    "reaction_network.csv + molecular_inventory.csv": {
        "tests": 15,
        "reason": "L'inventaire hiérarchique contient des molécules qualitatives, mais aucun réseau versionné avec réactifs, produits, taux et plages de température, ni abondances observationnelles assorties d'incertitudes.",
        "candidate": "KIDA/UMIST et un inventaire astronomique quantitatif.",
    },
    "thermochemical_phases.csv": {
        "tests": 15,
        "reason": "La table 08_Phases.csv est un inventaire qualitatif. Elle ne contient pas les triplets température-pression-énergie de Gibbs nécessaires aux calculs de condensation.",
        "candidate": "Base thermodynamique quantitative Perple_X/JANAF ou équivalent avec licence et provenance.",
    },
    "endosymbiosis_events.csv": {
        "tests": 12,
        "reason": "Le dépôt mentionne mitochondrie et chloroplaste, mais ne fournit pas des événements documentés avec transfert génique, intégration métabolique, dépendance et niveau de preuve.",
        "candidate": "Jeu phylogénomique et métabolique construit depuis des sources publiées.",
    },
    "planetary_histories.csv": {
        "tests": 11,
        "reason": "Les éléments orbitaux J2000 et DE441 sont des états dynamiques, pas des histoires géochimiques complètes d'accrétion, redox, pertes et apports tardifs.",
        "candidate": "Cas planétaires/météoritiques harmonisés avec couches historiques et partition finale.",
    },
    "nucleosynthesis_yields.csv": {
        "tests": 10,
        "reason": "Les trajectoires MESA présentes décrivent des transitions stellaires, pas des rendements élémentaires par masse, métallicité et incertitude.",
        "candidate": "Tables de rendements NuGrid ou équivalent.",
    },
    "isotope_tracers.csv": {
        "tests": 10,
        "reason": "Aucune table échantillon-traceur-valeur-incertitude permettant le clustering des groupes météoritiques n'est présente.",
        "candidate": "Compilation isotopique Ti-Cr-Mo-W-Ni-Ru-Pd avec provenance ligne par ligne.",
    },
    "late_accretion_tracers.csv": {
        "tests": 10,
        "reason": "Aucune table d'observations finales associées à des sources candidates d'accrétion tardive n'est présente.",
        "candidate": "Compilation Mo-Ru-W-Os-Ir-Au et modèles de mélange documentés.",
    },
    "volatile_inventory.csv": {
        "tests": 9,
        "reason": "Les inventaires généraux du dépôt ne donnent pas, par échantillon, les masses initiale, noyau, manteau, atmosphère et pertes nécessaires à la fermeture de masse.",
        "candidate": "Inventaires volatils quantitatifs de corps différenciés et météorites.",
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
    print(json.dumps(payload["campaign_counts"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
