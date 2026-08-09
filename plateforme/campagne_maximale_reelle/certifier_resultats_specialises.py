#!/usr/bin/env python3
"""Certifie des verdicts spécialisés par criterion_id dans l'audit strict.

La matrice générique conserve ses 683 lignes et ses propres compteurs. Cette
couche ajoute des verdicts scientifiques issus de protocoles spécialisés quand
leur critère, leur source, leur artefact et leur seuil sont vérifiables.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ICI = Path(__file__).resolve().parent
RACINE = ICI.parents[1]
CONFIG = ICI / "CERTIFICATIONS_SPECIALISEES.json"
SORTIE = ICI / "RESULTATS_SCIENTIFIQUES_CERTIFIES.json"


def sha256(chemin: Path) -> str:
    return hashlib.sha256(chemin.read_bytes()).hexdigest()


def donofrio_c_ant_01(d: dict) -> tuple[str, dict]:
    ok = (
        d["rmse_state_plus_history"] < d["rmse_state_only"]
        and d["rmse_state_plus_history"]
        < d["same_complexity_shuffled_history_rmse_mean"]
        and d["permutation_p_history_better_than_shuffled"] < 0.01
    )
    return ("supports" if ok else "does_not_support"), {
        "rmse_etat": d["rmse_state_only"],
        "rmse_etat_histoire": d["rmse_state_plus_history"],
        "rmse_histoire_permutee": d["same_complexity_shuffled_history_rmse_mean"],
        "p_permutation": d["permutation_p_history_better_than_shuffled"],
    }


def vesicules_c_ves_02(d: dict) -> tuple[str, dict]:
    t = d["lineage_permutation_test"]
    ok = (
        t["observed_parent_offspring_r"] > t["null_mean_r"]
        and t["permutation_p_one_sided"] < 0.01
    )
    return ("supports" if ok else "does_not_support"), dict(t)


def vesicules_c_ves_03(d: dict) -> tuple[str, dict]:
    ok = (
        d["selection_response"]["FR"] > 0
        and d["decision_components"]["FR_exceeds_ablation_mean"]
        and d["mechanism_ablation_contrast"] > 0
    )
    return ("supports" if ok else "does_not_support"), {
        "reponse_selection_FR": d["selection_response"]["FR"],
        "contraste_ablation": d["mechanism_ablation_contrast"],
        "FR_depasse_ablation": d["decision_components"]["FR_exceeds_ablation_mean"],
    }


def matiere_c_mat_mem_05(d: dict) -> tuple[str, dict]:
    t = d["transversalite"]
    ok = t["familles_au_schema_complet"] >= 3 and t["verdict"] == "soutient"
    return ("supports" if ok else "does_not_support"), {
        "familles_completes": t["familles_au_schema_complet"],
        "minimum": 3,
        "verdict_campagne": t["verdict"],
    }


def astronomie_c_ast_01(d: dict) -> tuple[str, dict]:
    acceptation = d["astronomical_acceptance"]
    ratio = d["numerical_effect_separation"]["minimum_ratio"]
    ok = acceptation["passed"] >= 12 and ratio >= 1000
    return ("supports" if ok else "does_not_support"), {
        "criteres_passes": acceptation["passed"],
        "criteres_total": acceptation["criteria"],
        "ratio_minimal_intervention_bruit_numerique": ratio,
    }


EVALUATEURS = {
    nom: objet for nom, objet in globals().copy().items()
    if callable(objet) and nom in {
        "donofrio_c_ant_01", "vesicules_c_ves_02", "vesicules_c_ves_03",
        "matiere_c_mat_mem_05", "astronomie_c_ast_01",
    }
}


def certifier(config: dict) -> dict:
    registre_path = RACINE / config["registre_criteres"]
    registre = json.loads(registre_path.read_text(encoding="utf-8"))
    criteres = {c["id"]: c for c in registre["criteres"]}
    sorties = []
    for specification in config["certifications"]:
        criterion_id = specification["criterion_id"]
        if criterion_id not in criteres:
            raise ValueError(f"criterion_id absent du registre : {criterion_id}")
        artefact = RACINE / specification["artefact"]
        empreinte = sha256(artefact)
        if empreinte != specification["artefact_sha256"]:
            raise ValueError(f"empreinte artefact divergente : {criterion_id}")
        source = specification.get("source")
        if source:
            source_path = RACINE / source
            if sha256(source_path) != specification["source_sha256"]:
                raise ValueError(f"empreinte source divergente : {criterion_id}")
        verdict, mesures = EVALUATEURS[specification["evaluateur"]](
            json.loads(artefact.read_text(encoding="utf-8"))
        )
        if verdict != specification["verdict_attendu"]:
            raise ValueError(
                f"verdict divergent pour {criterion_id}: {verdict} != "
                f"{specification['verdict_attendu']}"
            )
        sorties.append({
            "criterion_id": criterion_id,
            "verdict": verdict,
            "niveau_preuve": specification.get("niveau_preuve"),
            "portee": specification["portee"],
            "enonce": criteres[criterion_id]["enonce"],
            "artefact": specification["artefact"],
            "artefact_sha256": empreinte,
            "source": source,
            "source_sha256": specification.get("source_sha256"),
            "limite_provenance": specification.get("limite_provenance"),
            "mesures": mesures,
        })
    comptes = Counter(s["verdict"] for s in sorties)
    return {
        "schema": config["schema"],
        "integration": (
            "couche scientifique certifiée associée à l'audit strict ; les 683 "
            "lignes génériques et leurs compteurs techniques restent inchangés"
        ),
        "registre_criteres_sha256": sha256(registre_path),
        "comptes": dict(sorted(comptes.items())),
        "resultats": sorties,
    }


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--configuration", type=Path, default=CONFIG)
    analyseur.add_argument("--sortie", type=Path, default=SORTIE)
    arguments = analyseur.parse_args()
    rapport = certifier(json.loads(arguments.configuration.read_text(encoding="utf-8")))
    arguments.sortie.write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(f"{len(rapport['resultats'])} critères certifiés : {rapport['comptes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
