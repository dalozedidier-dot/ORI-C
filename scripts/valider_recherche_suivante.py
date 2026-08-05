#!/usr/bin/env python3
"""Contrôle statique et scientifique minimal de la campagne de recherche suivante."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / "plan_directeur/campagne_recherche_suivante"


def load(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    required = [
        CAMPAIGN / "sources_externes.json",
        CAMPAIGN / "run_all.py",
        CAMPAIGN / "fetch_external_data.py",
        ROOT / ".github/workflows/recherche-suivante.yml",
        ROOT / "01_branche_matiere/tests_causaux/resultats/H011_RESULTAT.json",
        ROOT / "01_branche_matiere/tests_causaux/resultats/CYCLE_INTERFACES_RESULTAT.json",
        ROOT / "02_branche_systeme_solaire/tests_suivants/resultats/PACC_ASTRONOMIQUE.json",
        ROOT / "02_branche_systeme_solaire/tests_suivants/resultats/PROTOCOLE_C2B.json",
        CAMPAIGN / "resultats/SYNTHESE.json",
    ]
    for path in required:
        if not path.exists():
            errors.append(f"fichier absent: {path.relative_to(ROOT)}")

    if not errors:
        synthesis = load(CAMPAIGN / "resultats/SYNTHESE.json")
        if synthesis.get("execution_errors") != 0:
            errors.append("la synthèse contient des erreurs d'exécution")

        h011 = load(ROOT / "01_branche_matiere/tests_causaux/resultats/H011_RESULTAT.json")
        if h011.get("natural_intervention_status") != "not_measured":
            errors.append("H011 ne distingue plus simulation et intervention naturelle")

        cycle = load(ROOT / "01_branche_matiere/tests_causaux/resultats/CYCLE_INTERFACES_RESULTAT.json")
        if cycle.get("single_system_closed_trajectories") != 0:
            errors.append("le cycle est déclaré fermé sans audit manuel explicite")

        pacc = load(ROOT / "02_branche_systeme_solaire/tests_suivants/resultats/PACC_ASTRONOMIQUE.json")
        if not 0 <= pacc.get("Pacc_dimensions", -1) <= 1:
            errors.append("Pacc_dimensions sort de [0,1]")
        if pacc.get("total_dimension_cells") != 18:
            errors.append("le domaine Pacc ne contient plus les 6 interventions x 3 métriques attendues")

        c2b = load(ROOT / "02_branche_systeme_solaire/tests_suivants/resultats/PROTOCOLE_C2B.json")
        if c2b.get("status") != "frozen_before_new_execution":
            errors.append("WP-C2b n'est plus gelé avant exécution")
        if len(c2b.get("protocol_sha256", "")) != 64:
            errors.append("empreinte de WP-C2b invalide")

        registry = load(CAMPAIGN / "sources_externes.json")
        if sum(bool(item.get("required_for_current_tests")) for item in registry["datasets"]) < 2:
            errors.append("moins de deux jeux externes requis sont enregistrés")

    if errors:
        print("ÉCHEC DE LA VALIDATION RECHERCHE")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Validation de la recherche suivante réussie.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
