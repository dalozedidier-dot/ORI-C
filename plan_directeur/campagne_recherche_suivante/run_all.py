#!/usr/bin/env python3
"""Exécute les nouveaux tests sans transformer les données absentes en réussite."""
from __future__ import annotations

import importlib.util
import json
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).with_name("resultats")
MODULES = [
    ("matiere_h011", ROOT / "01_branche_matiere/tests_causaux/analyser_h011.py"),
    ("matiere_cycle", ROOT / "01_branche_matiere/tests_causaux/analyser_cycle_interfaces.py"),
    ("pacc_astronomique", ROOT / "02_branche_systeme_solaire/tests_suivants/mesurer_pacc_astronomique.py"),
    ("memoire_c2b", ROOT / "02_branche_systeme_solaire/tests_suivants/preenregistrer_c2b.py"),
    ("speleothemes", ROOT / "02_branche_systeme_solaire/tests_suivants/auditer_speleothemes.py"),
    ("vesicules", ROOT / "03_branche_vivant/lignees_vesicules/analyser_lignees.py"),
    ("antibiotique_2026", ROOT / "03_branche_vivant/benchmark_histoire_antibiotique_2026/analyser.py"),
    ("antibiotique_pid", ROOT / "03_branche_vivant/benchmark_histoire_antibiotique_2026/analyser_pid.py"),
    ("santos_lopez_benchmark", ROOT / "03_branche_vivant/benchmark_externe_santos_lopez_2021/analyser_benchmark.py"),
]


def call(name: str, path: Path) -> dict[str, object]:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise ImportError(f"module introuvable: {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    result = module.main()
    if not isinstance(result, dict):
        raise TypeError(f"{name}.main() doit retourner un dictionnaire")
    return result


def status_of(result: dict[str, object]) -> str:
    for key in ("status", "h011_status", "cycle_status"):
        if key in result:
            return str(result[key])
    return "completed_without_status"


def main() -> int:
    results: dict[str, dict[str, object]] = {}
    errors = 0
    for name, path in MODULES:
        print(f"[{name}]")
        try:
            results[name] = call(name, path)
        except Exception as exc:  # Les autres blocs restent audités.
            errors += 1
            results[name] = {
                "status": "execution_error",
                "error": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(),
            }

    OUT.mkdir(exist_ok=True)
    synthesis = {
        "schema": 1,
        "modules": results,
        "execution_errors": errors,
        "waiting_for_external_data": sum(
            status_of(value) == "waiting_for_external_data" for value in results.values()
        ),
    }
    (OUT / "SYNTHESE.json").write_text(
        json.dumps(synthesis, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    lines = ["# Synthèse de la campagne de recherche suivante", ""]
    lines.extend(f"- **{name}** : `{status_of(result)}`" for name, result in results.items())
    lines.extend(
        [
            "",
            f"Erreurs d'exécution : **{errors}**.",
            f"Blocs en attente de données externes : **{synthesis['waiting_for_external_data']}**.",
        ]
    )
    (OUT / "RAPPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(synthesis, indent=2, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
