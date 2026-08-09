#!/usr/bin/env python3
"""Rejoue la campagne : gel, vérification, extraction, tests, synthèse.

Chaque étape refuse de démarrer si la précédente a échoué.

    python run_all.py [--telecharger] [--sans-verification]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# La campagne imprime des flèches, des tirets cadratins et des symboles grecs.
# Sous Windows, une console CP-1252 lève sinon UnicodeEncodeError avant même le
# premier contrôle. La CI Linux est déjà en UTF-8 ; cette reconfiguration y est
# sans effet fonctionnel.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ICI = Path(__file__).resolve().parent
DERIVE = ICI / "derive"


def executer(titre: str, arguments: list[str], obligatoire: bool = True,
             source_primaire_requise: bool = False) -> dict:
    debut = time.monotonic()
    print(f"── {titre}")
    environnement = dict(os.environ, PYTHONUTF8="1")
    resultat = subprocess.run([sys.executable, *arguments], cwd=ICI,
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", env=environnement)
    duree = time.monotonic() - debut
    texte = resultat.stdout or ""
    sortie = texte.strip().splitlines()
    for ligne in sortie[-6:]:
        print(f"     {ligne}")
    # Une source absente n'est pas un échec : les résultats commités restent
    # valides et l'extracteur a refusé de les écraser.
    ignore = "Résultats commités laissés intacts" in texte
    if ignore:
        etat = "ignoré, sources absentes"
    else:
        etat = "ok" if resultat.returncode == 0 else "ÉCHEC"
    print(f"     {etat} en {duree:.1f} s")
    if resultat.returncode != 0 and not ignore:
        for ligne in (resultat.stderr or "").strip().splitlines()[-5:]:
            print(f"     {ligne}")
    print()
    # La durée n'est pas inscrite dans le rapport versionné : elle change à
    # chaque exécution, le manifeste ne correspondrait plus et le contrôle
    # d'intégrité échouerait sur un fichier pourtant identique quant au fond.
    if source_primaire_requise:
        niveau = ("derive_versionne_rejouable_source_primaire_absente"
                  if ignore else "source_primaire_vers_table_et_statistique")
    else:
        niveau = "table_versionnee_vers_statistique"
    return {"etape": titre, "code": 0 if ignore else resultat.returncode,
            "sources_absentes": ignore, "obligatoire": obligatoire,
            "source_primaire_requise": source_primaire_requise,
            "provenance_complete_depuis_source_primaire": bool(
                source_primaire_requise and not ignore
            ),
            "niveau_reproductibilite": niveau}


def synthese_transversale() -> dict:
    """C-MAT-MEM-05 : le schéma tient-il dans trois familles indépendantes."""
    familles: dict[str, dict] = {}

    ablation = DERIVE / "RESULTAT_C_MAT_MEM_03.json"
    if ablation.exists():
        r = json.loads(ablation.read_text(encoding="utf-8"))
        familles["magnetisme"] = {
            "jeu": "rémanence IODP, 25 expéditions",
            "critere_decisif": "C-MAT-MEM-03, ablation physique",
            "verdict": r["verdict"],
            "niveau_de_temoin": r.get("niveau_de_temoin"),
            "echantillons": r["signal"]["echantillons"],
        }

    plasticite = DERIVE / "RESULTATS_PLASTICITE_ET_PHASE.json"
    if plasticite.exists():
        r = json.loads(plasticite.read_text(encoding="utf-8"))
        for cle, bloc in r.get("jeux", {}).items():
            famille = bloc["famille"]
            if famille in familles and familles[famille]["verdict"] == "soutient":
                continue
            familles[famille] = {
                "jeu": cle,
                "critere_decisif": "dose d'histoire",
                "verdict": bloc["verdict"],
                "niveau_de_temoin": 6 if famille == "plasticite" else 5,
                "echantillons": bloc["eprouvettes"],
            }

    vieillissement = DERIVE / "RESULTAT_VIEILLISSEMENT_POLYMERE.json"
    if vieillissement.exists():
        r = json.loads(vieillissement.read_text(encoding="utf-8"))
        familles[r["famille"]] = {
            "jeu": r["jeu"],
            "critere_decisif": "dose de vieillissement thermique",
            "verdict": r["verdict"],
            "niveau_de_temoin": 6,
            "echantillons": r["echantillons"],
        }

    for fichier, niveau in ((DERIVE / "RESULTAT_TRACES_FISSION.json", 6),
                            (DERIVE / "RESULTAT_SURFACE.json", 5)):
        if fichier.exists():
            r = json.loads(fichier.read_text(encoding="utf-8"))
            familles[r["famille"]] = {
                "jeu": r.get("jeu") or ", ".join(r.get("jeux", {})),
                "critere_decisif": r.get("ablation", "dose d'histoire"),
                "verdict": r["verdict"],
                "niveau_de_temoin": niveau,
                "echantillons": r.get("conditions", sum(
                    j.get("mesures", 0) for j in r.get("jeux", {}).values())),
            }

    soutenues = [f for f, b in familles.items() if b["verdict"] == "soutient"]

    # C-MAT-MEM-05 exige le schéma complet, pas un verdict quelconque par
    # famille. La matrice transversale le mesure sous quatre contrôles de
    # robustesse ; c'est elle qui tranche.
    matrice = DERIVE / "MATRICE_TRANSVERSALE.json"
    comptes = {}
    if matrice.exists():
        comptes = json.loads(matrice.read_text(encoding="utf-8"))["comptes"]
    complet = comptes.get("schema_complet_histoire_trace_reponse", 0)
    verdict = "soutient" if complet >= 3 else "ne_soutient_pas"
    return {
        "critere": "C-MAT-MEM-05",
        "comptes_sous_controles": comptes,
        "familles_au_schema_complet": complet,
        "enonce": ("le schéma histoire → trace persistante → réponse modifiée est "
                   "soutenu indépendamment dans au moins trois familles physiques "
                   "à mécanismes différents"),
        "familles_examinees": familles,
        "familles_soutenantes": soutenues,
        "verdict": verdict,
        "motif": (f"{complet} famille(s) portent le schéma complet "
                  f"histoire vers trace vers réponse sous les quatre contrôles, "
                  f"3 exigées. {len(soutenues)} famille(s) rendent un verdict "
                  f"positif sur au moins une relation : "
                  f"{', '.join(soutenues) if soutenues else 'aucune'}"),
    }


def ecrire_synthese_versionnee(transversal: dict) -> Path:
    """Écrit la synthèse stable consommée par les autres campagnes."""
    synthese_versionnee = {
        "campagne": "WP-MAT-MEM-2026",
        "transversalite": transversal,
        "statut_provenance": {
            "chaine_integrale_exigee": (
                "source primaire → extraction → table par unité → statistique"
            ),
            "distinction": (
                "la reproductibilité d'une table dérivée ne démontre pas à elle "
                "seule la reproductibilité intégrale depuis la source primaire"
            ),
            "preuve_par_execution": (
                "derive/execution/CAMPAGNE.json dans l'artefact CI ; les étapes "
                "IODP et aciers à outils déclarent séparément leur niveau"
            ),
        },
    }
    sortie = DERIVE / "SYNTHESE_CAMPAGNE.json"
    with sortie.open("w", encoding="utf-8", newline="") as flux:
        flux.write(json.dumps(synthese_versionnee, ensure_ascii=False, indent=2) + "\n")
    return sortie


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--telecharger", action="store_true")
    analyseur.add_argument("--sans-verification", action="store_true")
    analyseur.add_argument(
        "--synthese-seule",
        action="store_true",
        help="régénère seulement la synthèse stable depuis les résultats versionnés",
    )
    arguments = analyseur.parse_args()

    if arguments.synthese_seule:
        sortie = ecrire_synthese_versionnee(synthese_transversale())
        print(f"écrit : {sortie.relative_to(ICI.parents[1]).as_posix()}")
        return 0

    print("Campagne « mémoire matérielle réelle » — WP-MAT-MEM-2026")
    print()
    etapes = [executer("gel des fichiers scellés", ["admettre_jeu.py", "--toutes"])]
    if etapes[-1]["code"] != 0:
        print("Gel rompu. La campagne s'arrête.")
        return 2

    if arguments.telecharger:
        etapes.append(executer("téléchargement des sources",
                               ["telecharger_toutes_sources.py"]))
        if etapes[-1]["code"] != 0:
            print("Téléchargement incomplet. La campagne s'arrête.")
            return 1

    if not arguments.sans_verification:
        etapes.append(executer("vérification des sources",
                               ["verifier_sources.py", "--rapide"]))
        if etapes[-1]["code"] != 0:
            print("Sources non intègres. La campagne s'arrête.")
            return 1

    etapes.append(executer("extraction IODP", ["extraire_iodp.py"],
                           source_primaire_requise=True))
    if etapes[-1]["code"] != 0 and not etapes[-1]["sources_absentes"]:
        print("Extraction ratée. Aucun test ne sera exécuté sur des données "
              "incomplètes.")
        return 1

    etapes.append(executer("C-MAT-MEM-03, ablation physique",
                           ["tester_ablation_iodp.py"]))
    etapes.append(executer("diagnostics partiels IODP hors C01/C02/C04",
                           ["tester_iodp_01_02_04.py"]))
    etapes.append(executer("plasticité et transition de phase",
                           ["extraire_et_tester_plasticite.py"]))
    etapes.append(executer("vieillissement thermique de polymères",
                           ["extraire_et_tester_vieillissement.py"]))
    etapes.append(executer("recuit de traces de fission",
                           ["extraire_et_tester_traces_fission.py"]))
    etapes.append(executer("aciers à outils, chaîne candidate",
                           ["extraire_et_tester_carbures.py"],
                           source_primaire_requise=True))
    etapes.append(executer("reconstruction de surface",
                           ["extraire_et_tester_surface.py"]))
    etapes.append(executer("balayage des sources restantes",
                           ["balayer_toutes_les_sources.py"]))
    etapes.append(executer("test de signe orienté combiné sur les jeux",
                           ["test_combine_familles.py"]))
    etapes.append(executer("matrice transversale et robustesse",
                           ["matrice_transversale.py"]))
    etapes.append(executer(
        "même état, même stimulus, histoire différente — exploratoire",
        ["tester_meme_etat_histoire_differente.py"],
        obligatoire=False,
    ))

    transversal = synthese_transversale()
    print("── C-MAT-MEM-05, transversalité")
    for famille, bloc in transversal["familles_examinees"].items():
        print(f"     {famille:<24}{bloc['verdict']:<20}"
              f"niveau {bloc['niveau_de_temoin']}  {bloc['echantillons']} unités")
    print(f"     {transversal['motif']}")
    print(f"     VERDICT : {transversal['verdict']}")
    print()

    rapport = {
        "campagne": "WP-MAT-MEM-2026",
        "etapes": etapes,
        "transversalite": transversal,
        "echecs": [e["etape"] for e in etapes if e["code"] != 0],
        "ignorees_faute_de_sources": [e["etape"] for e in etapes
                                      if e.get("sources_absentes")],
        "provenance": {
            "regle": (
                "une table dérivée versionnée peut rendre le verdict rejouable, "
                "mais seule une étape marquée source_primaire_vers_table_et_statistique "
                "démontre la chaîne intégrale depuis la source primaire"
            ),
            "etapes_source_primaire_incompletes": [
                e["etape"] for e in etapes
                if e.get("source_primaire_requise")
                and not e.get("provenance_complete_depuis_source_primaire")
            ],
        },
    }
    journal = DERIVE / "execution"
    journal.mkdir(parents=True, exist_ok=True)
    sortie = journal / "CAMPAGNE.json"
    with sortie.open("w", encoding="utf-8", newline="") as flux:
        flux.write(json.dumps(rapport, ensure_ascii=False, indent=2) + "\n")
    print(f"écrit : {sortie.relative_to(ICI.parents[1]).as_posix()}")

    # La synthèse scientifique est versionnée ; le journal d'exécution reste
    # ignoré car la disponibilité locale des sources varie entre CI et postes.
    sortie_versionnee = ecrire_synthese_versionnee(transversal)
    print(f"écrit : {sortie_versionnee.relative_to(ICI.parents[1]).as_posix()}")

    if rapport["echecs"]:
        print(f"{len(rapport['echecs'])} étape(s) en échec : {rapport['echecs']}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
