#!/usr/bin/env python3
"""Filtre d'admission de la campagne « mémoire matérielle réelle ».

Décide si un jeu candidat entre dans la campagne, ou reste source documentaire.
La décision est mécanique et se prend **avant toute extraction**, sur une fiche
descriptive du jeu — pas sur ses résultats.

Le filtre applique les cinq conditions de `PROTOCOLE_CAMPAGNE.md`, puis calcule
l'atteignabilité à partir du nombre de paires indépendantes, puis déclare quels
critères sont testables avec ce jeu. Un critère non testable est un état
honorable ; une valeur imputée ne l'est pas.

    python admettre_jeu.py --fiche fiches/hefmag.json
    python admettre_jeu.py --toutes

Une fiche est un JSON portant les clés décrites dans `REGISTRE_JEUX_CANDIDATS.json`.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ICI = Path(__file__).resolve().parent
SCHEMA = ICI / "SCHEMA_EXTRACTION.json"
ALPHA = 0.05
PAIRES_MINIMUM = 6  # 2/2**6 = 0,03125 <= 0,05 ; cinq paires plafonnent à 0,0625


def p_minimal_sign_flip(paires: int) -> float:
    """Plus petite valeur de p d'un sign-flip exact sur `paires` paires."""
    return 2.0 / 2 ** paires if paires > 0 else 1.0


def conditions_d_admission(fiche: dict) -> list[tuple[str, bool, str]]:
    """Les cinq conditions, dans l'ordre du protocole."""
    histoires = fiche.get("histoires_distinctes", 0)
    controle = fiche.get("control_type", "aucun")
    return [
        (
            "au moins deux histoires distinctes documentées",
            histoires >= 2,
            f"{histoires} histoire(s) déclarée(s)",
        ),
        (
            "trace physique persistante mesurée",
            bool(fiche.get("trace_metric_disponible")),
            fiche.get("trace_metric_nom") or "aucune trace déclarée",
        ),
        (
            "réponse ultérieure sous stimulus final comparable",
            bool(fiche.get("response_metric_disponible"))
            and bool(fiche.get("stimulus_final_comparable")),
            fiche.get("response_metric_nom") or "aucune réponse déclarée",
        ),
        (
            "unités expérimentales indépendantes identifiables",
            int(fiche.get("unites_independantes", 0)) > 0,
            f"{fiche.get('unites_independantes', 0)} unité(s)",
        ),
        (
            "témoin réel disponible",
            controle != "aucun",
            f"control_type = {controle}",
        ),
    ]


def criteres_testables(fiche: dict, paires: int) -> dict[str, str]:
    """Quels critères ce jeu peut porter, et lesquels sont hors de sa portée."""
    atteignable = p_minimal_sign_flip(paires) <= ALPHA
    controle = fiche.get("control_type", "aucun")
    etats: dict[str, str] = {}

    def poser(cle: str, testable: bool, motif: str) -> None:
        if not testable:
            etats[cle] = f"non_testable_avec_ce_jeu — {motif}"
        elif not atteignable:
            etats[cle] = (
                f"indetermine_par_atteignabilite — {paires} paires, "
                f"p minimal {p_minimal_sign_flip(paires):.4f} > {ALPHA}"
            )
        else:
            etats[cle] = "testable"

    poser("C-MAT-MEM-01",
          bool(fiche.get("trace_metric_disponible"))
          and bool(fiche.get("response_metric_disponible")),
          "trace ou réponse absente")
    poser("C-MAT-MEM-02",
          fiche.get("time_since_history_disponible") is True,
          "aucun délai, cycle ou avancement de relaxation déclaré")
    poser("C-MAT-MEM-03",
          controle == "ablation_physique",
          "aucun bras d'ablation physique : démagnétisation, recuit de restauration")
    poser("C-MAT-MEM-04",
          fiche.get("trace_before_response") is True
          and fiche.get("bras_sans_histoire") is True,
          "trace non mesurée avant le stimulus, ou pas de bras sans histoire")
    return etats


def examiner(fiche: dict) -> dict:
    nom = fiche.get("nom", "sans nom")
    conditions = conditions_d_admission(fiche)
    echecs = [intitule for intitule, satisfait, _ in conditions if not satisfait]

    unites = int(fiche.get("unites_independantes", 0))
    paires = int(fiche.get("paires_independantes", unites // 2))

    if fiche.get("data_kind") != "mesure_experimentale":
        admis, motif = False, (
            f"data_kind = {fiche.get('data_kind')!r}. Seule une mesure "
            f"expérimentale entre dans les tests."
        )
    elif echecs:
        admis, motif = False, f"{len(echecs)} condition(s) non remplie(s)"
    elif paires < PAIRES_MINIMUM:
        admis, motif = False, (
            f"{paires} paires indépendantes, minimum {PAIRES_MINIMUM}. "
            f"Aucun verdict positif n'est atteignable à alpha = {ALPHA}."
        )
    else:
        admis, motif = True, "les cinq conditions sont remplies et l'atteignabilité est acquise"

    # Un jeu écarté ne porte aucun critère. Afficher « testable » sous un verdict
    # d'exclusion inviterait à l'exploiter quand même, ce qui est exactement le
    # contournement que le filtre existe pour empêcher.
    criteres = (criteres_testables(fiche, paires) if admis
                else {cle: f"hors campagne — {motif}" for cle in
                      ("C-MAT-MEM-01", "C-MAT-MEM-02", "C-MAT-MEM-03", "C-MAT-MEM-04")})

    return {
        "nom": nom,
        "famille_physique": fiche.get("famille_physique"),
        "doi": fiche.get("doi"),
        "admis": admis,
        "motif": motif,
        "statut": "admis_campagne" if admis else "source_documentaire",
        "conditions": [
            {"condition": i, "satisfaite": s, "detail": d} for i, s, d in conditions
        ],
        "paires_independantes": paires,
        "p_minimal_sign_flip": p_minimal_sign_flip(paires),
        "criteres": criteres,
    }


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--fiche", type=Path)
    analyseur.add_argument("--toutes", action="store_true",
                           help="examine toutes les fiches de fiches/")
    arguments = analyseur.parse_args()

    if not SCHEMA.exists():
        print("SCHEMA_EXTRACTION.json absent : campagne non scellée.")
        return 2

    if arguments.toutes:
        dossier = ICI / "fiches"
        fiches = sorted(dossier.glob("*.json")) if dossier.is_dir() else []
        if not fiches:
            print("Aucune fiche dans fiches/. Rien n'a encore été inspecté.")
            print("Le protocole est gelé ; l'inventaire des jeux reste à faire.")
            return 0
    elif arguments.fiche:
        fiches = [arguments.fiche]
    else:
        analyseur.error("préciser --fiche ou --toutes")

    resultats = []
    for chemin in fiches:
        rapport = examiner(json.loads(chemin.read_text(encoding="utf-8")))
        resultats.append(rapport)
        print(f"{rapport['nom']}  [{rapport['famille_physique']}]")
        print(f"  {'ADMIS' if rapport['admis'] else 'ÉCARTÉ'} — {rapport['motif']}")
        for condition in rapport["conditions"]:
            marque = "ok  " if condition["satisfaite"] else "NON "
            print(f"    {marque}{condition['condition']} : {condition['detail']}")
        for critere, etat in rapport["criteres"].items():
            print(f"    {critere} : {etat}")
        print()

    admis = [r for r in resultats if r["admis"]]
    familles = {r["famille_physique"] for r in admis}
    print(f"{len(admis)} jeu(x) admis sur {len(resultats)}, "
          f"{len(familles)} famille(s) physique(s) distincte(s).")
    print(f"C-MAT-MEM-05 exige trois familles : "
          f"{'atteignable' if len(familles) >= 3 else 'hors de portée en l’état'}.")

    sortie = ICI / "ADMISSION.json"
    with sortie.open("w", encoding="utf-8", newline="") as flux:
        flux.write(json.dumps(
            {"alpha": ALPHA, "paires_minimum": PAIRES_MINIMUM, "jeux": resultats},
            ensure_ascii=False, indent=2) + "\n")
    print(f"écrit : {sortie.relative_to(ICI.parents[1]).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
