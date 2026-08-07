"""Produit un bilan transparent de l'intégration maximale des données réelles."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
DEFAULT_DATA = HERE / "data"

RESOURCE_STATUS = {
    "thermochemical_phases.csv": {
        "status": "present_non_empirical",
        "reason": "Grille calculée depuis des paramètres thermodynamiques publiés. Elle audite le domaine T-P-G mais ne constitue pas une séquence de condensation à l'équilibre.",
        "next_requirement": "Composition globale, bilans élémentaires, activités/fugacités et solveur d'équilibre préenregistré avant tout test M4.",
    },
    "planetary_histories.csv": {
        "status": "absent_by_design",
        "reason": "Aucune source publique harmonisée ne fournit les sept couches historiques demandées avec provenance primaire par cellule.",
        "next_requirement": "Compilation primaire cellule par cellule ou redéfinition préenregistrée des protocoles P6.",
    },
    "late_accretion_tracers.csv": {
        "status": "present_partial_empirical",
        "reason": "122 159 mesures GEOROC réelles couvrent Mo-Ru-W-Os-Ir-Au, mais candidate_source décrit une famille géologique et non un pôle de mélange; les incertitudes analytiques par mesure sont absentes.",
        "next_requirement": "Modèle de mélange documenté avec pôles physiquement définis, unités et incertitudes avant P5-002 à P5-010. P5-001 seul est exécutable techniquement.",
    },
    "volatile_inventory.csv": {
        "status": "present_incomplete",
        "reason": "Les compartiments non publiés restent vides. Aucune des dix lignes ne contient simultanément masse initiale, noyau, manteau, atmosphère et pertes.",
        "next_requirement": "Inventaires fermés ou protocole explicitement conçu pour des bornes partielles; aucune valeur absente ne peut être remplacée par zéro.",
    },
    "modern_climate_timeseries.csv": {
        "status": "present_temperature_only",
        "reason": "7 193 lignes réelles issues de GISTEMP/HadCRUT5, mais les quatre variables sont des reconstructions de température et ne représentent ni forçages ni compartiments de mémoire.",
        "next_requirement": "Variables causales indépendantes et protocole mémoire/D-H-L gelé avant déblocage CL1/CL2.",
    },
}



def blocker_key(result: dict) -> str:
    message = result.get("message", "")
    details = result.get("details", {})
    if details.get("coverage_gaps"):
        gaps = details["coverage_gaps"]
        descriptors = []
        for item in gaps:
            dataset = item.get("dataset") or "aucun_dataset"
            reason = item.get("reason", "hors_portee")
            descriptors.append(f"{dataset}:{reason}")
        return "pare-feu empirique:" + ",".join(sorted(descriptors))
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
        "thermochemical_phase_rows": rows(data_dir / "thermochemical_phases.csv"),
        "late_accretion_tracer_rows": rows(data_dir / "late_accretion_tracers.csv"),
        "volatile_inventory_rows": rows(data_dir / "volatile_inventory.csv"),
        "modern_climate_timeseries_rows": rows(data_dir / "modern_climate_timeseries.csv"),
    }
    benchmark = pd.read_csv(data_dir / "benchmark_cases.csv")
    data_summary["benchmark_domains"] = benchmark.groupby("domain").size().astype(int).to_dict()
    payload = {
        "campaign_counts": campaign["counts"],
        "scientific_counts": campaign.get("scientific_counts", {}),
        "data_summary": data_summary,
        "blocked_root_causes": dict(blocked.most_common()),
        "coverage_registry": coverage,
        "resource_status": RESOURCE_STATUS,
        "interpretation": (
            "Mode réel strict fail-closed: une réussite technique n'existe que pour un test explicitement autorisé "
            "dans le registre empirique. Elle ne constitue toujours pas une confirmation scientifique."
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
        "Le pare-feu est fail-closed : présence d'un fichier, taille d'un jeu ou exécution d'un moteur ne suffisent jamais à créer une preuve. Une réussite technique reste distincte d'un verdict scientifique.",
        "",
        "## Données réellement raccordées",
        "",
    ]
    for key, value in payload["data_summary"].items():
        lines.append(f"- `{key}` : {json.dumps(value, ensure_ascii=False, sort_keys=True)}")
    lines.extend(["", "## Causes racines des blocages restants", ""])
    for key, value in payload["blocked_root_causes"].items():
        lines.append(f"- **{value}** entrées : {key}")
    lines.extend(["", "## Ressources nouvelles et verrous scientifiques", ""])
    for filename, item in payload["resource_status"].items():
        lines.extend([
            f"### `{filename}` — {item['status']}",
            "",
            item["reason"],
            "",
            f"Condition pour aller plus loin : {item['next_requirement']}",
            "",
        ])
    lines.extend([
        "## Règle de portée",
        "",
        "`EMPIRICAL_POLICY.json` est la politique gelée; `REAL_DATA_COVERAGE.json` en est l'état d'exécution. Une table ne débloque que les identifiants explicitement autorisés et admissibles comme preuve empirique.",
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
        "Mode fail-closed : ces réussites techniques correspondent seulement aux protocoles explicitement autorisés par la politique empirique. Aucun résultat de la matrice générique ne devient un soutien scientifique sans critère ciblé gelé.",
        "",
        "## Volumes canoniques utilisés",
        "",
        f"- Expériences de partage métal-silicate : **{data.get('partition_experiments', 0)}**",
        f"- Cas du benchmark transversal : **{data.get('benchmark_cases', 0)}**",
        f"- Lignées prébiotiques : **{data.get('prebiotic_lineage_nodes', 0)}** nœuds",
        f"- Relations parent-descendant intégrées dans la plateforme : **{data.get('prebiotic_parent_offspring_pairs', 0)}** (volume technique; le protocole ciblé des vésicules conserve son propre effectif préenregistré)",
        f"- Ensemble climatique : **{data.get('modern_climate_ensemble_rows', 0)}** lignes",
        f"- Réseau réactionnel : **{data.get('reaction_network_rows', 0)}** réactions",
        f"- Rendements de nucléosynthèse : **{data.get('nucleosynthesis_element_yields', 0)}** élémentaires et **{data.get('nucleosynthesis_isotope_yields', 0)}** isotopiques",
        f"- Événements endosymbiotiques : **{data.get('endosymbiosis_events', 0)}**",
        f"- Grille thermochimique calculée (audit seulement) : **{data.get('thermochemical_phase_rows', 0)}** lignes",
        f"- Traceurs GEOROC d'accrétion tardive : **{data.get('late_accretion_tracer_rows', 0)}** mesures",
        f"- Inventaire volatil documentaire : **{data.get('volatile_inventory_rows', 0)}** lignes",
        f"- Climat moderne observationnel/dérivé : **{data.get('modern_climate_timeseries_rows', 0)}** lignes",
        "",
        "## Portée",
        "",
        "Les causes détaillées des blocages figurent dans `AUDIT_DONNEES_DEPOT.md`. `EMPIRICAL_POLICY.json` fixe les autorisations; `REAL_DATA_COVERAGE.json` ne peut pas élargir cette portée automatiquement.",
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
