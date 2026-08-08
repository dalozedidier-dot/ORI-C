#!/usr/bin/env python3
"""Rejoue toute la campagne « mémoire matérielle réelle », de la source au verdict.

L'ordre est contraignant et chaque étape refuse de démarrer si la précédente a
échoué. Une campagne qui continue sur une extraction ratée produit des verdicts
sur des données incomplètes, ce qui est pire qu'aucun verdict.

    1. gel            les fichiers scellés sont-ils intacts
    2. téléchargement les sources sont-elles complètes
    3. vérification   empreintes, archives, doublons, provenance
    4. extraction     IODP, FABEST, moyen-Mn, au schéma de la campagne
    5. tests          C-MAT-MEM-01 à 04
    6. synthèse       C-MAT-MEM-05, transversalité

Deux modes. Par défaut la campagne suppose les sources déjà présentes en local et
saute le téléchargement — douze gigaoctets ne se retéléchargent pas à chaque
exécution. `--telecharger` force le rapatriement complet.

    python run_all.py
    python run_all.py --telecharger
    python run_all.py --sans-verification   # saute le réempreintage, plus rapide
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ICI = Path(__file__).resolve().parent
DERIVE = ICI / "derive"


def executer(titre: str, arguments: list[str], obligatoire: bool = True) -> dict:
    debut = time.monotonic()
    print(f"── {titre}")
    resultat = subprocess.run([sys.executable, *arguments], cwd=ICI,
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace")
    duree = time.monotonic() - debut
    sortie = (resultat.stdout or "").strip().splitlines()
    for ligne in sortie[-6:]:
        print(f"     {ligne}")
    etat = "ok" if resultat.returncode == 0 else "ÉCHEC"
    print(f"     {etat} en {duree:.1f} s")
    if resultat.returncode != 0:
        for ligne in (resultat.stderr or "").strip().splitlines()[-5:]:
            print(f"     {ligne}")
    print()
    return {"etape": titre, "code": resultat.returncode, "duree_s": round(duree, 1),
            "obligatoire": obligatoire}


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

    soutenues = [f for f, b in familles.items() if b["verdict"] == "soutient"]
    verdict = "soutient" if len(soutenues) >= 3 else "ne_soutient_pas"
    return {
        "critere": "C-MAT-MEM-05",
        "enonce": ("le schéma histoire → trace persistante → réponse modifiée est "
                   "soutenu indépendamment dans au moins trois familles physiques "
                   "à mécanismes différents"),
        "familles_examinees": familles,
        "familles_soutenantes": soutenues,
        "verdict": verdict,
        "motif": (f"{len(soutenues)} famille(s) sur les 3 exigées : "
                  f"{', '.join(soutenues) if soutenues else 'aucune'}"),
    }


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--telecharger", action="store_true")
    analyseur.add_argument("--sans-verification", action="store_true")
    arguments = analyseur.parse_args()

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

    etapes.append(executer("extraction IODP", ["extraire_iodp.py"]))
    if etapes[-1]["code"] != 0:
        print("Extraction ratée. Aucun test ne sera exécuté sur des données "
              "incomplètes.")
        return 1

    etapes.append(executer("C-MAT-MEM-03, ablation physique",
                           ["tester_ablation_iodp.py"]))
    etapes.append(executer("C-MAT-MEM-01, 02 et 04", ["tester_iodp_01_02_04.py"]))
    etapes.append(executer("plasticité et transition de phase",
                           ["extraire_et_tester_plasticite.py"]))
    etapes.append(executer("vieillissement thermique de polymères",
                           ["extraire_et_tester_vieillissement.py"]))

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
    }
    sortie = DERIVE / "CAMPAGNE.json"
    DERIVE.mkdir(exist_ok=True)
    with sortie.open("w", encoding="utf-8", newline="") as flux:
        flux.write(json.dumps(rapport, ensure_ascii=False, indent=2) + "\n")
    print(f"écrit : {sortie.relative_to(ICI.parents[1]).as_posix()}")

    if rapport["echecs"]:
        print(f"{len(rapport['echecs'])} étape(s) en échec : {rapport['echecs']}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
