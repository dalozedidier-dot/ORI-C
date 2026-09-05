"""Instancie la chaine presence -> accessibilite -> mobilisabilite -> operativite.

    Q_present >= Q_accessible >= Q_mobilisable >= Q_operatoire

    Q_accessible  = Q_present    x f_acces
    Q_mobilisable = Q_accessible x f_mobilisation
    Q_operatoire  = Q_mobilisable x f_incorporation

Le cas traite est l'azote terrestre. Il est choisi parce qu'il maximise l'ecart
entre les quatre degres : l'azote represente 78 pourcent de l'atmosphere en
volume, il est donc massivement present et parfaitement accessible, et il
limite pourtant la productivite biologique sur une grande partie de la planete.
La raison n'est ni la quantite ni l'acces : c'est la triple liaison de N2, qui
rend la mobilisation lente.

Consequence directe : `f_mobilisation` n'est pas une constante. C'est un flux
divise par un stock, donc une fonction de l'horizon temporel considere. Le meme
reservoir est presque entierement mobilisable sur cent millions d'annees et
presque pas sur un siecle. La chaine de filtres n'a donc aucun sens sans
horizon declare.

    python chaine_filtres.py
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

ICI = Path(__file__).resolve().parent
HYPER = ICI.parent / "hypergraphe_transformations"

TG_EN_KG = 1e9

# Reservoirs de surface : atteignables par la chimie de surface sans franchir
# d'interface non etablie. Le noyau n'y figure pas.
SURFACE = {"atmosphere", "croute continentale", "croute oceanique",
           "sediments oceaniques"}

# Flux de mobilisation mesures, en Tg d'azote par an.
FLUX = {
    "fixation biologique marine": 140.0,
    "fixation biologique terrestre naturelle": 88.0,
}
FLUX_ANTHROPIQUE = 210.0
HORIZONS = [1e2, 1e4, 1e6, 1.75e7, 1e8, 1e9]


def lire(chemin):
    with Path(chemin).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def main() -> int:
    inventaire = {l["record_id"]: l
                  for l in lire(HYPER / "inventaire_accessible.csv")}
    q = lambda i: float(inventaire[i]["quantite_totale"])

    # --- Q_present ---------------------------------------------------------
    bse = q("N-TER-BSE")
    scenarios_noyau = {"chondritique CC": q("N-TER-NOY-CC"),
                       "chondritique EC": q("N-TER-NOY-EC"),
                       "ab initio Zhang-Yin": q("N-TER-NOY-ZY")}

    # --- Q_accessible ------------------------------------------------------
    accessible = sum(q(i) for i, l in inventaire.items()
                     if l["corps"] == "Terre" and l["element"] == "N"
                     and l["reservoir"] in SURFACE)
    atmosphere = q("N-TER-ATM")

    # --- Q_mobilisable, fonction de l'horizon ------------------------------
    flux_naturel_kg_par_an = sum(FLUX.values()) * TG_EN_KG
    tau = atmosphere / flux_naturel_kg_par_an          # temps de residence
    mobilisable = {}
    for h in HORIZONS:
        # Modele de premier ordre : la fraction retournee vers le reservoir
        # n'est pas comptee deux fois.
        f = 1.0 - math.exp(-h / tau)
        mobilisable[f"{h:.0e} ans"] = {
            "f_mobilisation": round(f, 6),
            "Q_mobilisable_kg": float(f"{atmosphere * f:.4g}"),
        }

    resultats = {}
    for nom, noyau in scenarios_noyau.items():
        present = bse + noyau
        resultats[nom] = {
            "Q_present_kg": float(f"{present:.4g}"),
            "Q_accessible_kg": float(f"{accessible:.4g}"),
            "f_acces": round(accessible / present, 6),
        }

    rapport = {
        "element": "N", "corps": "Terre",
        "Q_present_par_scenario_de_noyau": resultats,
        "Q_accessible_kg": float(f"{accessible:.4g}"),
        "reservoirs_comptes_comme_accessibles": sorted(SURFACE),
        "flux_de_mobilisation_Tg_par_an": FLUX,
        "flux_naturel_total_Tg_par_an": sum(FLUX.values()),
        "flux_anthropique_Tg_par_an": FLUX_ANTHROPIQUE,
        "temps_de_residence_atmospherique_ans": float(f"{tau:.4g}"),
        "Q_mobilisable_par_horizon": mobilisable,
        "Q_operatoire_kg": None,
        "pourquoi_Q_operatoire_est_absent": (
            "Il exige le stock d'azote effectivement incorpore dans des "
            "architectures vivantes. Les sources donnent des flux de fixation "
            "et d'absorption, pas un stock de biomasse azotee mesure. Le "
            "deriver d'un rapport carbone sur azote serait un calcul, pas une "
            "donnee : la case reste vide."),
        "lecture": (
            "L'azote est present en masse et parfaitement accessible : "
            f"f_acces vaut {resultats['chondritique CC']['f_acces']:.4f} dans "
            "le scenario chondritique, et l'atmosphere est ouverte a toute "
            "interface de surface. Ce n'est ni la quantite ni l'acces qui "
            "limitent : c'est la mobilisation. Le temps de residence de "
            f"l'azote atmospherique contre la fixation biologique vaut "
            f"{tau/1e6:.1f} millions d'annees. Sur un siecle, la fraction "
            f"mobilisable vaut {mobilisable['1e+02 ans']['f_mobilisation']:.2e}. "
            "C'est le cas le plus net ou la presence ne determine pas les "
            "transformations possibles."),
        "portee": (
            "Un seul element, un seul corps, un modele de mobilisation de "
            "premier ordre. Le resultat montre que f_mobilisation est une "
            "fonction de l'horizon et non une constante ; il ne mesure pas "
            "l'operativite, qui reste sans donnee."),
    }
    (ICI / "chaine_filtres_azote.json").write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps(rapport, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
