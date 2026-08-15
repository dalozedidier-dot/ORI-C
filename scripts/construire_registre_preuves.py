#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def entry(identifier, question, statut, verdict, portee, artefact, *, source=None, mesures=None):
    return {
        "id": identifier,
        "question": question,
        "statut": statut,
        "verdict": verdict,
        "niveau_preuve": None,
        "portee": portee,
        "artefact": artefact,
        "empreinte_sortie": sha(artefact),
        "source": source,
        "mesures": mesures,
        "supersede_par": None,
    }


cert = json.loads(
    (ROOT / "plateforme/campagne_maximale_reelle/RESULTATS_SCIENTIFIQUES_CERTIFIES.json").read_text()
)
entries = []
for result in cert["resultats"]:
    entries.append({
        "id": result["criterion_id"],
        "question": result["enonce"],
        "statut": "certifie",
        "verdict": result["verdict"],
        "niveau_preuve": result["niveau_preuve"],
        "portee": result["portee"],
        "artefact": result["artefact"],
        "empreinte_sortie": result["artefact_sha256"],
        "source": result["source"],
        "mesures": result["mesures"],
        "supersede_par": None,
    })

extra = [
    ("SPIN-ORB-EXE", "spin, obliquité et insolation sous couple lunaire effectif", "exploratoire", "executed_model", "modele_reduit", "02_branche_systeme_solaire/couche_spin_orbite/resultats/summary.json"),
    ("VIAB-SPIN-01", "distance des trajectoires spin-orbite à une enveloppe de référence", "exploratoire", "executed_not_kernel", "modele_reduit", "02_branche_systeme_solaire/couche_spin_orbite/resultats/viabilite/RESULTAT.json"),
    ("PID-ANT-01", "information unique de l’histoire, synergie X×m et support P_acc rétrospectif sur D’Onofrio", "exploratoire", "executed_with_retrospective_Pacc", "empirique_externe_secondaire", "03_branche_vivant/benchmark_histoire_antibiotique_2026/resultats/PID_X_M_A.json"),
    ("PACC-ANT-01", "support MIC rétrospectif conditionné par histoire contre histoire permutée de même complexité", "exploratoire", "retrospective_history_conditioned_support_narrower_than_shuffled", "empirique_externe_secondaire", "03_branche_vivant/benchmark_histoire_antibiotique_2026/resultats/PID_X_M_A.json"),
    ("PACC-VES-ABL-01", "contraste de P_acc observé autour de l’ablation vésiculaire FR contre FU/UR/UU", "resultat_negatif", "does_not_support_positive_Pacc_ablation_contrast", "empirique_externe_secondaire", "03_branche_vivant/lignees_vesicules/resultats/RESULTAT.json"),
    ("M-ORB-01", "empreinte spectrale orbitale m sous interventions déjà validées", "exploratoire", "model_retrospective_dynamic_trace_proxy", "modele_reduit", "02_branche_systeme_solaire/tests_suivants/resultats/TRACE_ORBITALE_M.json"),
    ("EXO-DOM-01", "intervention ciblée sur la trace lente m à X, Theta et architecture appariés dans le modèle exoplanétaire", "exploratoire", "supports_local_nonzero_delta_Pacc_under_direct_m_reset", "modele_reduit", "02_branche_systeme_solaire/couche_memoire_historique/do_m_trace/resultats/RESULTAT_DO_M.json"),
    ("M-26AL-01", "inventaire radiogénique résiduel continu comme trace m dérivée des âges empiriques", "exploratoire", "derived_physical_history_trace_from_empirical_ages", "quantitatif_empirique_retroactif", "01_branche_matiere/genealogie_cosmique_quantitative/resultats/DISTRIBUTION_ACCESSIBILITE_26AL.json"),
    ("GCQ-INTERSTAGE-01", "association même-grain source stellaire → corps hôte sous contrôle de publication", "non_concluant", "no_conservation_claim_after_publication_control", "quantitatif_empirique_retroactif", "01_branche_matiere/genealogie_cosmique_quantitative/resultats/INFORMATION_INTERETAGES.json"),
    ("CSTATE-01", "états prédictifs à histoire finie sur séries ORI-C", "exploratoire", "executed_finite_proxy", "methodologique", "methodologie_informationnelle/RESULTATS_ETATS_CAUSAUX.json"),
    ("TOPO-MAT-01", "persistance multi-seuil de l’expansion simpliciale documentaire", "exploratoire", "executed", "structure_documentaire", "01_branche_matiere/hypergraphe_transformations/resultats_topologie/RESULTAT.json"),
    ("COT-MAT-01", "organisation chimique close et auto-maintenue", "non_concluant", "not_evaluable_missing_stoichiometry", "structure_documentaire", "01_branche_matiere/organisations_chimiques/resultats/DIAGNOSTIC.json"),
    ("POWER-MAT-01", "puissance conjointe du futur protocole matière", "exploratoire", "prospective_simulation", "dimensionnement", "methodologie_puissance/PUISSANCE_CONJOINTE_MATIERE.json"),
    ("MPT-M2-01", "formulation paléoclimatique M2 contre M1 et témoin apparié M1P", "resultat_negatif", "does_not_support", "modele_paleoclimatique_orbitally_tuned", "02_branche_systeme_solaire/couche_memoire_historique/results/mpt/summary.json"),
    ("CCM-CLIM-01", "cross-mapping convergent exploratoire LR04/La2004", "exploratoire", "executed", "observational_orbitally_tuned", "02_branche_systeme_solaire/couche_memoire_historique/exploratoire_causalite/resultats/CCM_RESULTAT.json"),
    ("PCMCI-CLIM-01", "PCMCI+ exploratoire LR04/La2004, p brutes et sans reclassement de M2", "exploratoire", "executed_raw_p", "observational_orbitally_tuned", "02_branche_systeme_solaire/couche_memoire_historique/exploratoire_causalite/resultats/PCMCI_PLUS_RESULTAT.json"),
    ("LTEE-REPLAY-01", "rejeu évolutif depuis ancêtres congelés, comptes publiés", "exploratoire", "secondary_reanalysis", "empirique_externe_table_transcription", "03_branche_vivant/ltee_replay_history/resultats/RESULTAT.json"),
    ("ASSEMBLY-BRIDGE-01", "comparaison ORI-C / Assembly Theory sur objets appariés", "non_concluant", "not_evaluable_missing_paired_observables", "comparaison_formelle", "comparaisons_externes/assembly_theory/DIAGNOSTIC.json"),
]
for identifier, question, statut, verdict, portee, artefact in extra:
    entries.append(entry(identifier, question, statut, verdict, portee, artefact))

# Généalogie cosmique : synthèse empirique stricte, séparée des certifications héritées.
gc_path = ROOT / "01_branche_matiere/genealogie_cosmique_quantitative/resultats/CLAIMS.json"
if gc_path.is_file():
    gc = json.loads(gc_path.read_text(encoding="utf-8"))
    if gc.get("schema") != "oric.gc.claims":
        raise ValueError("schéma CLAIMS généalogie cosmique inattendu")
    for claim in gc["claims"]:
        identifier = claim["claim_id"]
        artefact = f"01_branche_matiere/genealogie_cosmique_quantitative/resultats/claims/{identifier}.json"
        if claim["verdict"].startswith("undetermined_"):
            statut = "ouvert_empirique"
        elif claim["verdict"].startswith("supports_"):
            statut = "extension_empirique_non_preregistered"
        else:
            statut = "extension_empirique_non_concluante"
        entries.append(entry(
            identifier,
            claim["question"],
            statut,
            claim["verdict"],
            f"{claim['directness']} — {claim['scope']}",
            artefact,
            source=claim.get("source_ids"),
            mesures={
                "stages": claim.get("stages"),
                "mechanism": claim.get("mechanism"),
                "preregistration": claim.get("preregistration"),
            },
        ))

# Généalogie cosmique quantitative complète.
gcq_path = ROOT / "01_branche_matiere/genealogie_cosmique_quantitative/resultats/CLAIMS_QUANTITATIFS_COMPLETS.json"
if gcq_path.is_file():
    gcq = json.loads(gcq_path.read_text(encoding="utf-8"))
    if gcq.get("schema") != "oric.gc.quantitative-claims-complete":
        raise ValueError("schéma claims quantitatifs complets inattendu")
    for claim in gcq["claims"]:
        identifier = claim["claim_id"]
        artefact = f"01_branche_matiere/genealogie_cosmique_quantitative/resultats/claims_quantitatifs/{identifier}.json"
        entries.append(entry(
            identifier,
            claim["question"],
            "extension_quantitative_empirique_non_preregistered",
            claim["verdict"],
            "quantitatif empirique rétrospectif — sans simulation/synthétique/imputation",
            artefact,
            source=claim.get("source_ids"),
            mesures={
                "stages": claim.get("stage_ids"),
                "criterion_met": claim.get("criterion_met"),
                "preregistered": claim.get("preregistered"),
                "data_policy": claim.get("data_policy"),
            },
        ))
    for claim in gcq.get("posthoc_crosschecks", []):
        identifier = claim["claim_id"]
        artefact = f"01_branche_matiere/genealogie_cosmique_quantitative/resultats/claims_quantitatifs/{identifier}.json"
        entries.append(entry(
            identifier,
            claim["question"],
            "controle_quantitatif_empirique_posthoc",
            claim["verdict"],
            "contrôle post-hoc déterministe — non compté parmi les tests gelés",
            artefact,
            source=claim.get("source_ids"),
            mesures={
                "stages": claim.get("stage_ids"),
                "criterion_met": claim.get("criterion_met"),
                "preregistered": claim.get("preregistered"),
                "data_policy": claim.get("data_policy"),
            },
        ))

# Généalogie cosmique quantitative sur distributions massives réelles.
gcq_massive_path = ROOT / "01_branche_matiere/genealogie_cosmique_quantitative/resultats/CLAIMS_QUANTITATIFS_DONNEES_MASSIVES.json"
if gcq_massive_path.is_file():
    gcq_massive = json.loads(gcq_massive_path.read_text(encoding="utf-8"))
    if gcq_massive.get("schema") != "oric.gc.quantitative-massive-data-claims":
        raise ValueError("schéma claims quantitatifs données massives inattendu")
    for claim in gcq_massive["claims"]:
        identifier = claim["claim_id"]
        artefact = f"01_branche_matiere/genealogie_cosmique_quantitative/resultats/claims_quantitatifs/{identifier}.json"
        entries.append(entry(
            identifier,
            claim["question"],
            "extension_quantitative_empirique_donnees_massives_non_preregistered",
            claim["verdict"],
            "distributions réelles grain/échantillon — sans simulation/synthétique/imputation ni double comptage de formats",
            artefact,
            source=claim.get("source_ids"),
            mesures={
                "stages": claim.get("stage_ids"),
                "criterion_met": claim.get("criterion_met"),
                "preregistered": claim.get("preregistered"),
                "data_policy": claim.get("data_policy"),
            },
        ))

# Trois analyses réelles étendues du 15 août 2026. Elles restent rétrospectives
# et sont intégrées au registre sans modifier les certifications ni §XIV.
fitness_rel = "plan_directeur/exploitation_donnees_reelles_2026_08_15/resultats/RESULTAT_FITNESS_ORIGINE.json"
partition_rel = "plan_directeur/exploitation_donnees_reelles_2026_08_15/resultats/RESULTAT_PARTITION_CARBONE.json"
rna_rel = "plan_directeur/exploitation_donnees_reelles_2026_08_15/resultats/RESULTAT_RNA_PAPASTAVROU.json"
fitness = json.loads((ROOT / fitness_rel).read_text(encoding="utf-8"))
partition = json.loads((ROOT / partition_rel).read_text(encoding="utf-8"))
rna = json.loads((ROOT / rna_rel).read_text(encoding="utf-8"))

entries.append(entry(
    "FIT-ORIGIN-N-01",
    "Sous limitation azotée, les changements de fitness de souches évoluées indépendamment sont-ils plus similaires lorsqu’elles partagent la même population ancestrale que sous appariement aléatoire exhaustif ?",
    "extension_empirique_non_preregistered",
    "supports_retrospective_ancestral_origin_dependence_under_nitrogen",
    "empirique rétrospectif — origine ancestrale comme proxy de H; aucune trace physique m isolée et aucun P_acc causal",
    fitness_rel,
    source=fitness["source"],
    mesures={
        "nitrogen_exact_pairing_p": fitness["results_by_limitation"]["Nitrogen"]["exact_pairing"]["p_value"],
        "carbon_exact_pairing_p": fitness["results_by_limitation"]["Carbon"]["exact_pairing"]["p_value"],
        "nitrogen_independent_evolved_strains": fitness["results_by_limitation"]["Nitrogen"]["independent_evolved_strains"],
        "carbon_independent_evolved_strains": fitness["results_by_limitation"]["Carbon"]["independent_evolved_strains"],
        "section_XIV_credit": fitness["qualification"]["section_XIV_credit"],
    },
))
entries.append(entry(
    "MAT-NBOT-PART-01",
    "NBO/T ajoute-t-il une information prédictive hors source sur logD du carbone au-delà de P, T et ΔIW ?",
    "extension_empirique_non_preregistered",
    "supports_cross_source_structural_state_prediction_with_nbo_t",
    "empirique rétrospectif — NBO/T classé comme état structural X, pas comme trace historique m; aucune ablation de m ni P_acc causal",
    partition_rel,
    source=partition["source"],
    mesures={
        "n_experiments": partition["selection"]["n_experiments"],
        "n_independent_source_groups": partition["selection"]["n_independent_source_groups"],
        "relative_rmse_gain": partition["result"]["relative_rmse_gain"],
        "permutation_one_sided_p": partition["result"]["permutation_one_sided_p"],
        "rmse_baseline": partition["result"]["rmse_baseline"],
        "rmse_plus_nbo_t": partition["result"]["rmse_plus_nbo_t"],
        "section_XIV_credit": partition["qualification"]["section_XIV_credit"],
    },
))
entries.append(entry(
    "RNA-PAP-TRAJ-01",
    "Les deux branches expérimentales d’ARN prébiotique suivent-elles des trajectoires de fréquence distinctes sur huit cycles ?",
    "extension_empirique_non_preregistered",
    "supports_descriptive_branch_specific_rna_trajectory_divergence",
    "empirique rétrospectif descriptif — deux branches seulement; H/trajectoire observée mais m non isolé et aucun P_acc causal",
    rna_rel,
    source=rna["source"],
    mesures={
        "records": rna["design"]["records"],
        "branches": len(rna["design"]["branches"]),
        "rounds": len(rna["design"]["rounds"]),
        "max_absolute_difference_log2": rna["branch_divergence"]["max_absolute_difference_log2"],
        "sequence_with_max_difference": rna["branch_divergence"]["sequence_with_max_difference"],
        "section_XIV_credit": rna["qualification"]["section_XIV_credit"],
    },
))

out = {
    "schema": "oric.proofs-registry.v1",
    "authority": "machine-readable registry; certified entries are imported byte-for-byte in status from RESULTATS_SCIENTIFIQUES_CERTIFIES.json",
    "entries": entries,
}
(ROOT / "preuves/PREUVES.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
    newline="\n",
)

lines = [
    "# État des preuves",
    "",
    "> **Fichier généré. Ne pas modifier à la main.** Source : `preuves/PREUVES.json`.",
    "",
    "Les certifications historiques restent inchangées. Les nouvelles analyses importées sont explicitement séparées en exploratoire, non concluant ou modèle.",
    "",
    "## Résultats certifiés",
    "",
    "| ID | Verdict | Niveau | Portée | Artefact |",
    "|---|---|---|---|---|",
]
for proof in entries:
    if proof["statut"] == "certifie":
        lines.append(f"| `{proof['id']}` | **{proof['verdict']}** | {proof['niveau_preuve'] or '—'} | {proof['portee']} | `{proof['artefact']}` |")
lines += [
    "",
    "## Extensions exécutées sans reclassement des certifications",
    "",
    "| ID | Statut | Verdict technique | Portée |",
    "|---|---|---|---|",
]
for proof in entries:
    if proof["statut"] != "certifie":
        lines.append(f"| `{proof['id']}` | {proof['statut']} | {proof['verdict']} | {proof['portee']} |")
lines += [
    "",
    "## Règle de lecture",
    "",
    "Un calcul exploratoire ne devient pas une preuve certifiée par sa simple présence dans ce registre. `C-MAT-MEM-05` reste négatif, M2 reste non réussi, et `C-AST-01` reste limité au niveau modèle. Les ponts vers la théorie de la viabilité, la PID, la mécanique computationnelle, COT, CCM, LTEE et Assembly Theory sont des extensions méthodologiques ou des analyses supplémentaires. Les mesures locales de `P_acc` ajoutées dans le vivant restent des supports empiriques rétrospectifs : le contraste vésiculaire sous ablation est négatif pour la direction attendue et ne remplace pas le critère de réponse certifié `C-VES-03`. La trace orbitale `m` reste un proxy au niveau modèle et la trace `m` du 26Al est dérivée des âges empiriques sous décroissance déclarée. La généalogie cosmique est soumise à un pare-feu empirique propre : aucune simulation, donnée synthétique ou sortie de modèle n'entre dans ses claims. Ses 15 résultats empiriques soutenus restent des extensions initiales non préenregistrées. Les huit claims `GCQ-T09` à `GCQ-T16` sont des extensions quantitatives empiriques rétrospectives : ils quantifient notamment l'inventaire radiogénique accessible et les verrous de chaîne, sans certifier une trajectoire orbitale unique ni fermer artificiellement la chaîne primordiale→présent. `GCQ-X01` est explicitement un contrôle post-hoc montrant que la courbe canonique de décroissance ne constitue pas un inventaire local unique. Les claims `GCQ-T17` à `GCQ-T21` ajoutent une couche de données massives réelles fondée sur des distributions grain/échantillon publiées et mesurées; les lignes PGD non publiées, valeurs synthétiques, imputations et doublons de format sont exclus. `FIT-ORIGIN-N-01`, `MAT-NBOT-PART-01` et `RNA-PAP-TRAJ-01` sont des extensions empiriques rétrospectives du 15 août 2026; aucune n'isole à elle seule un do(m) causal ou un P_acc qualifié et aucune ne reçoit de crédit §XIV. C-AST demeure séparé au niveau modèle.",
    "",
]
(ROOT / "ETAT_DES_PREUVES.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
print(f"PREUVES.json: {len(entries)} entrées; ETAT_DES_PREUVES.md généré")
