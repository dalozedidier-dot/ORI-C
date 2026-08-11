#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "resultats"


def benchmark_transversal() -> tuple[dict, dict]:
    path = HERE / "construire_benchmark_transversal.py"
    spec = importlib.util.spec_from_file_location("oric_central_benchmark", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.build()


def quantification_commune() -> tuple[dict, dict]:
    path = HERE / "executer_quantification_commune.py"
    spec = importlib.util.spec_from_file_location("oric_common_quantification", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.build()


def dump(name: str, value: object) -> None:
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n"
    )


def admission_paleo() -> dict:
    data = ROOT / "donnees_externes/donnees_reelles_2026_08_07/paleoclimat_long"
    external = ROOT / "donnees_externes/paleo_history_01"
    mapping = {
        "LR04": data / "lisiecki2005_LR04.txt",
        "pile_benthique_independante": external / "ahn2017_prob_stack.txt",
        "proxy_niveau_marin_independant": external / "spratt2016_sea_level_noaa.txt",
        "EPICA_temperature": data / "edc3deuttemp2007.txt",
        "EPICA_CO2": data / "edc-co2-2008.txt",
        "EPICA_poussieres": external / "lambert2008_epica_dust/datasets/EDC_dust_lpc.tab",
        "Vostok": data / "vostok_deutnat.txt",
        "insolation_convention_1": ROOT / "02_branche_systeme_solaire/couche_memoire_historique/data/raw/orbit91",
        "insolation_convention_2": external / "INSOLN.LA2004.BTL.100.ASC",
    }
    required = json.loads((ROOT / "02_branche_systeme_solaire/paleo_history_01/SCHEMA_DONNEES.json").read_text(encoding="utf-8"))["jeux_obligatoires"]
    present = {}
    for dataset, path in mapping.items():
        path = path.resolve()
        if path.exists():
            present[dataset] = {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    missing = [name for name in required if name not in present]
    audit_path = ROOT / "02_branche_systeme_solaire/paleo_history_01/donnees_normalisees/AUDIT_NORMALISATION.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8")) if audit_path.exists() else None
    schema_issues = ["normalisation non exécutée"] if audit is None else list(audit["blocking_issues"])
    return {
        "campaign_id": "PALEO-HISTORY-01",
        "verdict": "admis" if not missing and not schema_issues else "non_testable",
        "required_count": len(required),
        "present_count": len(present),
        "present": present,
        "missing": missing,
        "schema_issues": schema_issues,
        "normalization_audit": audit_path.relative_to(ROOT).as_posix() if audit else None,
        "normalized_dataset_count": len(audit["datasets"]) if audit else 0,
        "rule": "l'analyse ne démarre que si les neuf familles obligatoires sont présentes et conformes au schéma; le gel n'est pas assoupli",
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
        "critical_blockers": ["PALEO-HISTORY-01: chronologies probabilistes et contrôle négatif gelé absents", "memoire_matiere: aucune chaîne complète admise", "P_acc: non mesuré transversalement"]
    }


def main() -> int:
    paleo = admission_paleo()
    dump("ADMISSION_PALEO_HISTORY_01.json", paleo)
    dump("DATASET_TEST_MATRIX.json", dataset_matrix())
    dump("DEPENDANCES_SCIENTIFIQUES.json", dependency_graph())
    benchmark, invariants = benchmark_transversal()
    dump("BENCHMARK_TRANSVERSAL.json", benchmark)
    dump("AUDIT_INVARIANTS.json", invariants)
    measures, bifurcations = quantification_commune()
    dump("MESURES_COMMUNES_EXECUTEES.json", measures)
    dump("REGISTRE_BIFURCATIONS.json", bifurcations)
    plan = json.loads((HERE / "PLAN_CENTRAL.json").read_text(encoding="utf-8"))
    dump("ETAT_CAMPAGNE.json", {
        "schema": "oric.central-campaign-status.v1",
        "paleo_history_01": paleo["verdict"],
        "axes_total": len(plan["axes"]),
        "axes_documentes": sum("statut" in axis for axis in plan["axes"]),
        "benchmark_cases": benchmark["case_count"],
        "invariant_cases_complete": invariants["cases_complete_X_H_m_Theta_tau_Pacc_R"],
        "claim_general": "ORI-C n'est pas validé comme théorie générale",
        "next_executable_gate": "obtenir les distributions chronologiques publiées et préenregistrer un contrôle négatif dans PALEO-HISTORY-02",
    })
    print(f"30 axes suivis; PALEO-HISTORY-01={paleo['verdict']}; {len(paleo['missing'])} familles manquantes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
