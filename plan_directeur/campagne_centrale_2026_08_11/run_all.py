#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "resultats"


def dump(name: str, value: object) -> None:
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n"
    )


def admission_paleo() -> dict:
    data = ROOT / "donnees_externes/donnees_reelles_2026_08_07/paleoclimat_long"
    mapping = {
        "LR04": "lisiecki2005_LR04.txt",
        "EPICA_temperature": "edc3deuttemp2007.txt",
        "EPICA_CO2": "edc-co2-2008.txt",
        "Vostok": "vostok_deutnat.txt",
    }
    required = json.loads((ROOT / "02_branche_systeme_solaire/paleo_history_01/SCHEMA_DONNEES.json").read_text(encoding="utf-8"))["jeux_obligatoires"]
    present = {}
    for dataset, filename in mapping.items():
        path = data / filename
        if path.exists():
            present[dataset] = {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    missing = [name for name in required if name not in present]
    return {
        "campaign_id": "PALEO-HISTORY-01",
        "verdict": "admis" if not missing else "non_testable",
        "required_count": len(required),
        "present_count": len(present),
        "present": present,
        "missing": missing,
        "rule": "l'analyse ne démarre que si les neuf familles obligatoires sont admises; le gel n'est pas assoupli",
    }


def dataset_matrix() -> dict:
    source = ROOT / "plateforme/campagne_maximale_reelle/PRIORITES_ACQUISITION_DONNEES.json"
    priorities = json.loads(source.read_text(encoding="utf-8"))["priorites"]
    weights = {
        "paleoclimate_timeseries": (1.0, 0.9, 0.8),
        "prebiotic_lineages": (1.0, 1.0, 0.3),
        "antibiotic_measurements": (0.9, 0.9, 0.7),
        "antibiotic_cycles": (0.9, 0.9, 0.6),
        "partition_experiments": (0.9, 1.0, 0.5),
    }
    rows = []
    for item in priorities:
        dataset = item["dataset_cible"]
        scientific, discriminating, availability = weights.get(dataset, (0.5, 0.5, 0.5))
        cost = max(0.1, 1.1 - availability)
        n = item["tests_distincts_potentiellement_debloquables"]
        score = n * scientific * discriminating / cost
        rows.append({
            "dataset": dataset, "tests_potentiels": n,
            "poids_scientifique": scientific, "poids_discriminant": discriminating,
            "disponibilite": availability, "cout_relatif": round(cost, 3),
            "score_levier": round(score, 3), "test_ids": item["test_ids"],
            "warning": "borne supérieure; acquisition ne garantit ni exécution ni soutien",
        })
    rows.sort(key=lambda row: (-row["score_levier"], row["dataset"]))
    return {"schema": "oric.dataset-test-matrix.v1", "source": source.relative_to(ROOT).as_posix(), "rows": rows}


def dependency_graph() -> dict:
    return {
        "schema": "oric.scientific-dependencies.v1",
        "nodes": ["hypergraphe", "memoire_matiere", "genealogie_cosmique", "PALEO-HISTORY-01", "replication_antibiotique", "replication_vesicules", "P_acc", "benchmark_transversal", "invariants", "predictions_prospectives"],
        "edges": [
            ["hypergraphe", "P_acc"], ["memoire_matiere", "P_acc"],
            ["genealogie_cosmique", "P_acc"], ["PALEO-HISTORY-01", "P_acc"],
            ["replication_antibiotique", "benchmark_transversal"],
            ["replication_vesicules", "benchmark_transversal"],
            ["P_acc", "benchmark_transversal"], ["benchmark_transversal", "invariants"],
            ["invariants", "predictions_prospectives"]
        ],
        "critical_blockers": ["PALEO-HISTORY-01: données obligatoires absentes", "memoire_matiere: aucune chaîne complète admise", "P_acc: non mesuré transversalement"]
    }


def main() -> int:
    paleo = admission_paleo()
    dump("ADMISSION_PALEO_HISTORY_01.json", paleo)
    dump("DATASET_TEST_MATRIX.json", dataset_matrix())
    dump("DEPENDANCES_SCIENTIFIQUES.json", dependency_graph())
    plan = json.loads((HERE / "PLAN_CENTRAL.json").read_text(encoding="utf-8"))
    dump("ETAT_CAMPAGNE.json", {
        "schema": "oric.central-campaign-status.v1",
        "paleo_history_01": paleo["verdict"],
        "axes_total": len(plan["axes"]),
        "axes_documentes": sum("statut" in axis for axis in plan["axes"]),
        "claim_general": "ORI-C n'est pas validé comme théorie générale",
        "next_executable_gate": "acquisition et admission des cinq familles manquantes de PALEO-HISTORY-01",
    })
    print(f"30 axes suivis; PALEO-HISTORY-01={paleo['verdict']}; {len(paleo['missing'])} familles manquantes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
