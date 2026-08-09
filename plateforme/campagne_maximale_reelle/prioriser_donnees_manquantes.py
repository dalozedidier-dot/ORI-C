#!/usr/bin/env python3
"""Transforme les blocages stricts en priorités d'acquisition de données.

Le nombre associé à un dataset est une borne supérieure de tests distincts
potentiellement débloquables. Il ne constitue ni un nombre d'expériences
ratées, ni une promesse d'exécution, ni un verdict scientifique.
"""
from __future__ import annotations

import json
import sys
import argparse
from collections import Counter, defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ICI = Path(__file__).resolve().parent
ENTREE = ICI / "resultats_integration_maximale" / "results.json"
SORTIE_JSON = ICI / "PRIORITES_ACQUISITION_DONNEES.json"
SORTIE_MD = ICI / "PRIORITES_ACQUISITION_DONNEES.md"

ACTIONS = {
    "test_hors_portee_mesuree": (
        "acquérir une source réelle mesurant exactement les variables, traces, "
        "interventions ou réponses exigées par le protocole"
    ),
    "non_admissible_comme_preuve_empirique": (
        "remplacer la simulation, reconstruction ou benchmark par une source "
        "empirique admissible ; télécharger davantage du même objet ne suffit pas"
    ),
    "aucun_jeu_empirique_declare": (
        "identifier puis déclarer un jeu réel adapté au test"
    ),
}


def construire(resultats: dict) -> dict:
    lignes = resultats["results"]
    bloques = [r for r in lignes if r["outcome"] == "blocked"]
    occurrences = Counter()
    tests_par_cause: dict[str, set[str]] = defaultdict(set)
    tests_par_dataset: dict[str, set[str]] = defaultdict(set)
    causes_par_dataset: dict[str, Counter] = defaultdict(Counter)
    wps_par_dataset: dict[str, set[str]] = defaultdict(set)

    for resultat in bloques:
        test_id = resultat["test_id"]
        for lacune in resultat.get("details", {}).get("coverage_gaps", []):
            cause = lacune["reason"]
            dataset = lacune.get("dataset") or "aucun_dataset_declare"
            occurrences[cause] += 1
            tests_par_cause[cause].add(test_id)
            tests_par_dataset[dataset].add(test_id)
            causes_par_dataset[dataset][cause] += 1
            wps_par_dataset[dataset].add(resultat["wp"])

    priorites = []
    for dataset, tests in tests_par_dataset.items():
        causes = causes_par_dataset[dataset]
        priorites.append({
            "dataset_cible": dataset,
            "tests_distincts_potentiellement_debloquables": len(tests),
            "test_ids": sorted(tests),
            "work_packages": sorted(wps_par_dataset[dataset]),
            "causes": dict(sorted(causes.items())),
            "actions_requises": [ACTIONS[c] for c in sorted(causes)],
        })
    priorites.sort(key=lambda x: (
        -x["tests_distincts_potentiellement_debloquables"],
        x["dataset_cible"],
    ))

    return {
        "source": str(ENTREE.relative_to(ICI.parents[1])).replace("\\", "/"),
        "lecture": (
            "carte des données manquantes, pas tableau de score scientifique ; "
            "un déblocage potentiel ne garantit ni exécution réussie ni soutien"
        ),
        "campagne": {
            "tests_catalogues": len(lignes),
            "bloques": len(bloques),
            "non_executes_automatiquement": sum(
                r["outcome"] == "not_run" for r in lignes
            ),
            "executes_techniquement": sum(r["outcome"] == "pass" for r in lignes),
            "echecs_techniques": sum(r["outcome"] == "fail" for r in lignes),
            "erreurs_informatiques": sum(r["outcome"] == "error" for r in lignes),
        },
        "causes": {
            cause: {
                "occurrences": occurrences[cause],
                "tests_distincts": len(tests_par_cause[cause]),
                "action": ACTIONS[cause],
            }
            for cause in sorted(occurrences)
        },
        "regle_de_comptage": (
            "les causes et datasets peuvent se cumuler sur un test ; chaque ligne "
            "de priorité déduplique les test_id pour éviter le double comptage"
        ),
        "priorites": priorites,
    }


def rendre_markdown(rapport: dict) -> str:
    c = rapport["campagne"]
    lignes = [
        "# Priorités d'acquisition de données",
        "",
        "Cette sortie transforme la matrice stricte en **carte des données "
        "manquantes**. Les 683 lignes sont des tests possibles, pas 683 "
        "expériences disponibles. Un nombre de tests potentiellement débloqués "
        "est une borne supérieure : il ne préjuge ni de l'exécution ni du verdict.",
        "",
        f"- {c['tests_catalogues']} tests catalogués ;",
        f"- {c['bloques']} bloqués ;",
        f"- {c['non_executes_automatiquement']} non exécutables automatiquement ;",
        f"- {c['executes_techniquement']} exécutés techniquement ;",
        f"- {c['echecs_techniques']} échec technique et "
        f"{c['erreurs_informatiques']} erreur informatique.",
        "",
        "## Causes des blocages",
        "",
        "| Cause | Occurrences | Tests distincts |",
        "|---|---:|---:|",
    ]
    for cause, bloc in rapport["causes"].items():
        lignes.append(
            f"| `{cause}` | {bloc['occurrences']} | {bloc['tests_distincts']} |"
        )
    lignes += [
        "",
        "Les occurrences ne s'additionnent pas aux 626 blocages : un même test "
        "peut cumuler plusieurs lacunes.",
        "",
        "## Données à acquérir ou remplacer",
        "",
        "| Rang | Dataset cible | Tests distincts potentiellement débloqués | Action |",
        "|---:|---|---:|---|",
    ]
    for rang, bloc in enumerate(rapport["priorites"], 1):
        actions = " ; ".join(bloc["actions_requises"])
        lignes.append(
            f"| {rang} | `{bloc['dataset_cible']}` | "
            f"{bloc['tests_distincts_potentiellement_debloquables']} | {actions} |"
        )
    return "\n".join(lignes) + "\n"


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--entree", type=Path, default=ENTREE)
    analyseur.add_argument("--sortie-json", type=Path, default=SORTIE_JSON)
    analyseur.add_argument("--sortie-md", type=Path, default=SORTIE_MD)
    arguments = analyseur.parse_args()
    rapport = construire(json.loads(arguments.entree.read_text(encoding="utf-8")))
    try:
        source = arguments.entree.resolve().relative_to(ICI.parents[1]).as_posix()
    except ValueError:
        source = arguments.entree.as_posix()
    rapport["source"] = source
    arguments.sortie_json.write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    arguments.sortie_md.write_text(
        rendre_markdown(rapport), encoding="utf-8", newline="\n"
    )
    print(f"{len(rapport['priorites'])} cibles classées")
    for bloc in rapport["priorites"][:10]:
        print(f"  {bloc['dataset_cible']:<32} "
              f"{bloc['tests_distincts_potentiellement_debloquables']:>3} tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
