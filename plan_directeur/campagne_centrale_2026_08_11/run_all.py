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


def invariant_transversal() -> tuple[dict, dict]:
    path = HERE / "evaluer_invariant_transversal.py"
    spec = importlib.util.spec_from_file_location("oric_transversal_invariant", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.build()


def resultats_communs() -> dict:
    path = HERE / "construire_resultats_communs.py"
    spec = importlib.util.spec_from_file_location("oric_common_results", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.build()


def seuil_xiv() -> tuple[dict, dict]:
    path = HERE / "evaluer_seuil_xiv.py"
    spec = importlib.util.spec_from_file_location("oric_section_xiv", path)
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
        "nodes": ["hypergraphe", "memoire_matiere", "genealogie_cosmique", "PALEO-HISTORY-01", "replication_antibiotique", "replication_vesicules", "P_acc", "contrastes_P_acc_locaux", "benchmark_transversal", "INV-A", "invariants", "predictions_prospectives"],
        "edges": [
            ["hypergraphe", "P_acc"], ["memoire_matiere", "P_acc"],
            ["genealogie_cosmique", "P_acc"], ["PALEO-HISTORY-01", "P_acc"],
            ["replication_antibiotique", "benchmark_transversal"],
            ["replication_vesicules", "benchmark_transversal"],
            ["P_acc", "contrastes_P_acc_locaux"], ["contrastes_P_acc_locaux", "benchmark_transversal"],
            ["benchmark_transversal", "INV-A"], ["INV-A", "invariants"],
            ["invariants", "predictions_prospectives"]
        ],
        "critical_blockers": [
            "PALEO-HISTORY-01: chronologies probabilistes et contrôle négatif gelé absents",
            "memoire_matiere: aucune chaîne complète admise",
            "P_acc: plusieurs mesures locales existent; les contrastes sont normalisés localement mais aucune échelle de magnitude interdomaines n'est validée",
            "INV-A: deux systèmes possèdent maintenant un do(m) direct; le vivant est négatif sur son contraste local et EXO-DOM-01 soutient un effet non nul au niveau modèle; la branche matière empirique reste à fermer",
            "réplications indépendantes: résultats vivants positifs encore non répliqués sur jeux indépendants"
        ]
    }


def experimental_readiness() -> dict:
    ves = json.loads((ROOT / "03_branche_vivant/lignees_vesicules/VES-PACC-INT-01.execution.json").read_text(encoding="utf-8"))
    mag = json.loads((ROOT / "01_branche_matiere/memoire_materielle_reelle/experiences_appariees/MAG-PAIR-001.execution.json").read_text(encoding="utf-8"))
    replication = json.loads((ROOT / "03_branche_vivant/benchmark_histoire_antibiotique_2026/CHAINE_REPLICATION_INDEPENDANTE.json").read_text(encoding="utf-8"))
    return {
        "schema": "oric.experimental-execution-readiness.v1",
        "VES-PACC-INT-01": {
            "status": ves["status"],
            "scientific_protocol_unchanged": ves["scientific_protocol_unchanged"],
            "blockers": ves["remaining_execution_blockers"],
            "result_present": False
        },
        "MAG-PAIR-001": {
            "status": mag["status"],
            "null_frozen_fields": [key for key, value in mag["frozen_fields"].items() if value is None],
            "result_present": False
        },
        "PRED-VIVANT-HISTOIRE-001": {
            "status": replication["current_verdict"],
            "next_action": replication["next_action"]
        },
        "rule": "Aucun statut ready, résultat ou crédit scientifique n'est déduit d'un protocole seul."
    }


def completeness_report(benchmark: dict) -> dict:
    rows = []
    for case in benchmark["cases"]:
        rows.append({
            "id": case["id"],
            "system_id": case["system_id"],
            "field_completeness_fraction": case["field_completeness_fraction"],
            "missing_fields": case["missing_fields"],
            "field_complete": case["eligible_for_common_invariant"],
            "measurement_quality": case["measurement_quality"],
            "next_action": case["next_action"],
        })
    rows.sort(key=lambda row: (-row["field_completeness_fraction"], len(row["missing_fields"]), row["id"]))
    return {
        "schema": "oric.transversal-completeness.v1",
        "required_fields": ["X", "H", "m", "Theta", "tau", "P_acc", "R"],
        "cases_total": len(rows),
        "field_complete_cases": sum(row["field_complete"] for row in rows),
        "field_complete_unique_systems": len({row["system_id"] for row in rows if row["field_complete"]}),
        "cases_missing_one_field": sum(len(row["missing_fields"]) == 1 for row in rows),
        "warning": "un cas à 7/7 peut rester rétrospectif, dérivé ou de niveau modèle; la complétude n'est pas un niveau de preuve",
        "rows": rows,
    }


def main() -> int:
    paleo = admission_paleo()
    dump("ADMISSION_PALEO_HISTORY_01.json", paleo)
    dump("DATASET_TEST_MATRIX.json", dataset_matrix())
    dump("DEPENDANCES_SCIENTIFIQUES.json", dependency_graph())
    dump("EXECUTION_EXPERIMENTALE_READINESS.json", experimental_readiness())
    benchmark, invariants = benchmark_transversal()
    dump("BENCHMARK_TRANSVERSAL.json", benchmark)
    dump("COMPLETUDE_21_CAS.json", completeness_report(benchmark))
    dump("AUDIT_INVARIANTS.json", invariants)
    common_results = resultats_communs()
    dump("RESULTATS_COMMUNS.json", common_results)
    common_path = HERE / "construire_resultats_communs.py"
    common_spec = importlib.util.spec_from_file_location("oric_common_views", common_path)
    common_module = importlib.util.module_from_spec(common_spec)
    assert common_spec.loader is not None
    common_spec.loader.exec_module(common_module)
    branch_matrix, associated_proofs = common_module.derive_views(common_results)
    dump("MATRICE_BRANCHES_COMMUNE.json", branch_matrix)
    dump("PREUVES_ASSOCIEES_COMMUNES.json", associated_proofs)
    measures, bifurcations = quantification_commune()
    dump("MESURES_COMMUNES_EXECUTEES.json", measures)
    dump("REGISTRE_BIFURCATIONS.json", bifurcations)
    contrasts, inv_a = invariant_transversal()
    dump("CONTRASTES_ACCESSIBILITE_INV_A.json", contrasts)
    dump("AUDIT_INV_A.json", inv_a)
    section_xiv, diagnostics_xiv = seuil_xiv()
    dump("SEUIL_XIV.json", section_xiv)
    dump("PACC_QUALIFICATION_STRICTE.json", diagnostics_xiv["pacc"])
    dump("PREDICTIONS_HORS_ECHANTILLON_AUDIT.json", diagnostics_xiv["prediction"])
    dump("REPLICATIONS_INDEPENDANTES_AUDIT.json", diagnostics_xiv["replication"])
    dump("TRANSFERT_SANS_REDEFINITION_AUDIT.json", diagnostics_xiv["cross_branch"])
    dump("ANTIBIOTIQUES_SPECIFICATIONS_AUDIT.json", diagnostics_xiv["antibiotics"])
    plan = json.loads((HERE / "PLAN_CENTRAL.json").read_text(encoding="utf-8"))
    dump("ETAT_CAMPAGNE.json", {
        "schema": "oric.central-campaign-status.v1",
        "paleo_history_01": paleo["verdict"],
        "axes_total": len(plan["axes"]),
        "axes_documentes": sum("statut" in axis for axis in plan["axes"]),
        "benchmark_cases": benchmark["case_count"],
        "invariant_cases_complete": invariants["cases_complete_X_H_m_Theta_tau_Pacc_R"],
        "field_complete_unique_systems": benchmark["field_complete_unique_system_count"],
        "inv_a_status": inv_a["current_status"],
        "inv_a_direct_m_ablation_systems": inv_a["direct_m_ablation_system_count"],
        "inv_a_direct_positive_m_ablation_systems": inv_a["direct_positive_m_ablation_system_count"],
        "section_xiv_passed": section_xiv["passed_count"],
        "section_xiv_missing": section_xiv["missing_ids"],
        "claim_general": "ORI-C n'est pas validé comme théorie générale",
        "next_executable_without_new_data": "maintenir les portes machine §XIV et appliquer PACC-INT-CHALLENGE-V1 uniquement aux jeux interventionnels réellement appariés; aucun recalcul rétrospectif ne ferme les conditions 3, 9, 10 ou 11",
        "next_confirmatory_gate": "conditions §XIV 3+4, 9, 10 et 11: prédiction hors échantillon battant un témoin apparié, Pacc causal empirique, réplication externe stricte et transfert sans redéfinition",
    })
    print(f"30 axes suivis; PALEO-HISTORY-01={paleo['verdict']}; {len(paleo['missing'])} familles manquantes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
