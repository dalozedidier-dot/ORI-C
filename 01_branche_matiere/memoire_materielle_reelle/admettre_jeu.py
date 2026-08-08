#!/usr/bin/env python3
"""Filtre d'admission de la campagne « mémoire matérielle réelle ».

Décide si un jeu candidat entre dans la campagne, ou reste source documentaire.
La décision est mécanique et se prend **avant toute extraction**, sur une fiche
descriptive du jeu — pas sur ses résultats.

Le filtre commence par **vérifier le gel**. `GEL_CAMPAGNE.json` porte les
empreintes SHA-256 du protocole, du schéma, du registre et de ce fichier même. Si
l'une d'elles diverge, le programme s'arrête : un préenregistrement que le code ne
contrôle pas n'est pas un préenregistrement, seulement un fichier de plus.

Il applique ensuite les cinq conditions de `PROTOCOLE_CAMPAGNE.md`, calcule
l'atteignabilité **à partir du plan expérimental déclaré**, puis dit quels
critères sont testables avec ce jeu. Un critère non testable est un état
honorable ; une valeur imputée ne l'est pas.

    python admettre_jeu.py --fiche fiches/exemple.json
    python admettre_jeu.py --toutes
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

ICI = Path(__file__).resolve().parent
SCHEMA = ICI / "SCHEMA_EXTRACTION.json"
GEL = ICI / "GEL_CAMPAGNE.json"
ALPHA = 0.05

CRITERES_LOCAUX = ("C-MAT-MEM-01", "C-MAT-MEM-02", "C-MAT-MEM-03", "C-MAT-MEM-04")


# ---------------------------------------------------------------- gel

def verifier_le_gel() -> list[str]:
    """Recalcule les empreintes scellées. Rend la liste des divergences."""
    if not GEL.exists():
        return ["GEL_CAMPAGNE.json absent : la campagne n'est pas scellée"]
    gel = json.loads(GEL.read_text(encoding="utf-8"))
    divergences = []
    for nom, attendu in gel.get("empreintes", {}).items():
        chemin = ICI / nom
        if not chemin.exists():
            divergences.append(f"{nom} : fichier scellé absent")
            continue
        reel = hashlib.sha256(chemin.read_bytes()).hexdigest()
        if reel != attendu:
            divergences.append(f"{nom} : empreinte divergente")
    return divergences


# ------------------------------------------------- atteignabilité

def p_minimal(plan: str, fiche: dict) -> tuple[float | None, str]:
    """Plus petite valeur de p atteignable, déduite du plan expérimental déclaré.

    Deux plans sont reconnus, et ils n'ont pas la même arithmétique.

    `apparie` — chaque unité porte les deux histoires, ou les unités sont
    appariées deux à deux. Le test est un sign-flip exact sur `n` paires :
    2**n attributions de signe, donc p minimal bilatéral = 2 / 2**n.

    `groupes_independants` — des groupes distincts d'unités, une histoire par
    groupe, sans appariement. Le test permute les étiquettes d'histoire. Le
    nombre d'assignations distinctes vaut le coefficient multinomial des tailles
    de groupe, donc p minimal bilatéral = 2 / ce nombre.

    Imposer le seuil du plan apparié à un plan non apparié écarterait à tort des
    jeux parfaitement valables. C'était le défaut de la première version.
    """
    if plan == "apparie":
        paires = fiche.get("paires_independantes")
        if not isinstance(paires, int) or paires < 1:
            return None, ("plan apparié sans `paires_independantes` déclaré. "
                          "Le nombre de paires ne se déduit pas du nombre d'unités : "
                          "vingt échantillons indépendants ne font pas dix paires "
                          "expérimentales. Il doit être lu dans la source.")
        return 2.0 / 2 ** paires, f"sign-flip exact sur {paires} paires"

    if plan == "groupes_independants":
        tailles = fiche.get("unites_par_groupe")
        if not isinstance(tailles, list) or len(tailles) < 2 or not all(
            isinstance(x, int) and x > 0 for x in tailles
        ):
            return None, ("plan à groupes indépendants sans `unites_par_groupe` "
                          "déclaré, ou moins de deux groupes")
        total = sum(tailles)
        assignations = math.factorial(total)
        for taille in tailles:
            assignations //= math.factorial(taille)
        return 2.0 / assignations, (
            f"permutation des étiquettes sur des groupes de {tailles}, "
            f"{assignations} assignations distinctes"
        )

    return None, (f"plan expérimental {plan!r} non reconnu. Valeurs admises : "
                  f"`apparie`, `groupes_independants`.")


# ------------------------------------------------------ admission

def conditions_d_admission(fiche: dict) -> list[tuple[str, bool, str]]:
    histoires = fiche.get("histoires_distinctes", 0)
    controle = fiche.get("control_type", "aucun")
    unites = fiche.get("unites_independantes", 0)
    return [
        ("au moins deux histoires distinctes documentées", histoires >= 2,
         f"{histoires} histoire(s) déclarée(s)"),
        ("trace physique persistante mesurée",
         bool(fiche.get("trace_metric_disponible")),
         fiche.get("trace_metric_nom") or "aucune trace déclarée"),
        ("réponse ultérieure sous stimulus final comparable",
         bool(fiche.get("response_metric_disponible"))
         and bool(fiche.get("stimulus_final_comparable")),
         fiche.get("response_metric_nom") or "aucune réponse déclarée"),
        ("unités expérimentales indépendantes identifiables",
         isinstance(unites, int) and unites > 0, f"{unites} unité(s)"),
        ("témoin réel disponible", controle != "aucun", f"control_type = {controle}"),
    ]


def criteres_testables(fiche: dict, atteignable: bool, lecture_p: str) -> dict[str, str]:
    controle = fiche.get("control_type", "aucun")
    etats: dict[str, str] = {}

    def poser(cle: str, testable: bool, motif: str) -> None:
        if not testable:
            etats[cle] = f"non_testable_avec_ce_jeu — {motif}"
        elif not atteignable:
            etats[cle] = f"indetermine_par_atteignabilite — {lecture_p}"
        else:
            etats[cle] = "testable"

    poser("C-MAT-MEM-01",
          bool(fiche.get("trace_metric_disponible"))
          and bool(fiche.get("response_metric_disponible")),
          "trace ou réponse absente")
    poser("C-MAT-MEM-02", fiche.get("time_since_history_disponible") is True,
          "aucun délai, cycle ou avancement de relaxation déclaré")
    poser("C-MAT-MEM-03", controle == "ablation_physique",
          "aucun bras d'ablation physique : démagnétisation, recuit de restauration")
    poser("C-MAT-MEM-04",
          fiche.get("trace_before_response") is True
          and fiche.get("bras_sans_histoire") is True,
          "trace non mesurée avant le stimulus, ou pas de bras sans histoire")
    return etats


def examiner(fiche: dict) -> dict:
    nom = fiche.get("nom", "sans nom")
    conditions = conditions_d_admission(fiche)
    echecs = [i for i, satisfait, _ in conditions if not satisfait]

    plan = fiche.get("plan_experimental", "non_declare")
    minimum, lecture_p = p_minimal(plan, fiche)
    atteignable = minimum is not None and minimum <= ALPHA

    if fiche.get("data_kind") != "mesure_experimentale":
        admis, motif = False, (f"data_kind = {fiche.get('data_kind')!r}. Seule une "
                               f"mesure expérimentale entre dans les tests.")
    elif echecs:
        admis, motif = False, f"{len(echecs)} condition(s) non remplie(s)"
    elif minimum is None:
        admis, motif = False, lecture_p
    elif not atteignable:
        admis, motif = False, (f"{lecture_p} : p minimal {minimum:.4f} > {ALPHA}. "
                               f"Aucun verdict positif n'est atteignable.")
    else:
        admis, motif = True, (f"les cinq conditions sont remplies ; {lecture_p}, "
                              f"p minimal {minimum:.2e}")

    criteres = (criteres_testables(fiche, atteignable, lecture_p) if admis
                else {cle: f"hors campagne — {motif}" for cle in CRITERES_LOCAUX})

    return {
        "nom": nom,
        "famille_physique": fiche.get("famille_physique"),
        "doi": fiche.get("doi"),
        "admis": admis,
        "motif": motif,
        "statut": "admis_campagne" if admis else "source_documentaire",
        "plan_experimental": plan,
        "p_minimal_atteignable": minimum,
        "lecture_de_l_atteignabilite": lecture_p,
        "conditions": [{"condition": i, "satisfaite": s, "detail": d}
                       for i, s, d in conditions],
        "criteres": criteres,
    }


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--fiche", type=Path)
    analyseur.add_argument("--toutes", action="store_true")
    arguments = analyseur.parse_args()

    divergences = verifier_le_gel()
    if divergences:
        print("GEL ROMPU. Aucun jeu ne peut être admis.")
        for divergence in divergences:
            print(f"  {divergence}")
        print("Rétablir les fichiers scellés, ou resceller explicitement en "
              "inscrivant le motif dans GEL_CAMPAGNE.json.")
        return 2
    print("Gel vérifié : les quatre fichiers scellés sont intacts.")

    if not SCHEMA.exists():
        print("SCHEMA_EXTRACTION.json absent.")
        return 2

    if arguments.toutes:
        dossier = ICI / "fiches"
        fiches = sorted(dossier.glob("*.json")) if dossier.is_dir() else []
        if not fiches:
            print()
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
        print()
        print(f"{rapport['nom']}  [{rapport['famille_physique']}]")
        print(f"  {'ADMIS' if rapport['admis'] else 'ÉCARTÉ'} — {rapport['motif']}")
        for condition in rapport["conditions"]:
            print(f"    {'ok  ' if condition['satisfaite'] else 'NON '}"
                  f"{condition['condition']} : {condition['detail']}")
        for critere, etat in rapport["criteres"].items():
            print(f"    {critere} : {etat}")

    admis = [r for r in resultats if r["admis"]]
    familles = {r["famille_physique"] for r in admis}
    print()
    print(f"{len(admis)} jeu(x) admis sur {len(resultats)}, "
          f"{len(familles)} famille(s) physique(s) distincte(s).")
    print(f"C-MAT-MEM-05 exige trois familles : "
          f"{'atteignable' if len(familles) >= 3 else 'hors de portée en l’état'}.")

    sortie = ICI / "ADMISSION.json"
    with sortie.open("w", encoding="utf-8", newline="") as flux:
        flux.write(json.dumps({"alpha": ALPHA, "jeux": resultats},
                              ensure_ascii=False, indent=2) + "\n")
    print(f"écrit : {sortie.relative_to(ICI.parents[1]).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
