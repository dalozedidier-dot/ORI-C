#!/usr/bin/env python3
"""Test de signe sur les jeux : la relation se répète-t-elle d'un jeu à l'autre.

Chaque jeu est trop petit pour atteindre alpha seul. Le signe, lui, se combine :
si k jeux indépendants donnent le même signe, la probabilité sous l'hypothèse
nulle vaut 2/2**k. L'unité du test est le jeu, pas l'échantillon.

Le signe attendu est fixé par la physique avant lecture des données.

    python test_combine_familles.py
"""
from __future__ import annotations

import csv
import json
from math import comb
from pathlib import Path

import numpy as np

ICI = Path(__file__).resolve().parent
DERIVE = ICI / "derive"
SORTIE = DERIVE / "RESULTAT_TEST_COMBINE.json"

ALPHA = 0.05

# Signe attendu, fixé par la physique et non lu dans les données.
#
# `trace_vers_reponse` a été préspécifié à +1 : une trace plus forte laisse un
# résidu plus fort. Le test le contredit, et la physique donne raison au test.
# Une rémanence plus forte laisse effectivement plus de rémanence, mais une
# dureté plus forte donne une ténacité plus faible — la relation dureté-ténacité
# est inverse et connue de longue date. Le signe préspécifié est conservé tel
# quel : le corriger après lecture reviendrait à choisir l'hypothèse sur les
# données. Le désaccord entre familles est le résultat.
ATTENDUS = {
    "histoire_vers_trace": -1,
    "trace_vers_reponse": +1,
    "histoire_vers_reponse": None,
    "ablation": -1,
}


def spearman(x, y) -> float:
    x, y = np.asarray(x, float), np.asarray(y, float)
    garde = np.isfinite(x) & np.isfinite(y)
    x, y = x[garde], y[garde]
    if x.size < 3:
        return float("nan")
    def rangs(v):
        o = np.argsort(v, kind="mergesort")
        r = np.empty(len(v), dtype=float)
        r[o] = np.arange(len(v), dtype=float)
        return r
    rx, ry = rangs(x), rangs(y)
    if rx.std() == 0 or ry.std() == 0:
        return float("nan")
    return float(np.corrcoef(rx, ry)[0, 1])


def lire(nom: str) -> list[dict]:
    chemin = DERIVE / nom
    if not chemin.exists():
        return []
    with chemin.open(encoding="utf-8", newline="") as flux:
        return list(csv.DictReader(flux))


def nombre(ligne: dict, cle: str) -> float:
    try:
        return float(ligne[cle])
    except (KeyError, TypeError, ValueError):
        return float("nan")


def colonne(lignes: list[dict], cle: str) -> list[float]:
    return [nombre(l, cle) for l in lignes]


def rassembler() -> dict[str, list[dict]]:
    mesures: dict[str, list[dict]] = {r: [] for r in ATTENDUS}

    def poser(relation: str, jeu: str, famille: str, rho: float, unites: int) -> None:
        if np.isfinite(rho) and unites >= 3:
            mesures[relation].append({"jeu": jeu, "famille": famille,
                                      "rho": rho, "unites": unites})

    iodp = lire("iodp_remanence_par_echantillon.csv")
    if iodp:
        poser("trace_vers_reponse", "iodp_remanence", "magnetisme",
              spearman(colonne(iodp, "nrm_intensite"),
                       colonne(iodp, "intensite_finale")), len(iodp))
        rhos = [v for v in colonne(iodp, "rho_ablation") if np.isfinite(v)]
        poser("ablation", "iodp_remanence", "magnetisme",
              float(np.mean(rhos)) if rhos else float("nan"), len(rhos))

    fabest = lire("fabest_par_eprouvette.csv")
    if fabest:
        poser("histoire_vers_reponse", "fabest_lcf", "plasticite",
              spearman(colonne(fabest, "n_cycles"),
                       colonne(fabest, "amplitude_fin")), len(fabest))
        poser("trace_vers_reponse", "fabest_lcf", "plasticite",
              spearman(colonne(fabest, "amplitude_debut"),
                       colonne(fabest, "amplitude_fin")), len(fabest))

    polymere = [l for l in lire("vieillissement_polymere_par_echantillon.csv")
                if nombre(l, "duree_jours") > 0]
    if polymere:
        poser("histoire_vers_reponse", "vieillissement_polymere", "verre_relaxation",
              spearman(colonne(polymere, "duree_jours"),
                       colonne(polymere, "temperature_apparition_C")), len(polymere))

    mn = lire("medium_mn_par_eprouvette.csv")
    if mn:
        poser("histoire_vers_trace", "medium_mn", "transition_de_phase",
              spearman(colonne(mn, "maintien_s"),
                       colonne(mn, "durete_moyenne_HV")), len(mn))

    carbures = lire("carbures_par_eprouvette.csv")
    if carbures:
        poser("histoire_vers_trace", "aciers_a_outils", "transition_de_phase",
              spearman(colonne(carbures, "revenu_C"),
                       colonne(carbures, "durete_HRC")), len(carbures))
        poser("trace_vers_reponse", "aciers_a_outils", "transition_de_phase",
              spearman(colonne(carbures, "durete_HRC"),
                       colonne(carbures, "tenacite")), len(carbures))
        poser("histoire_vers_reponse", "aciers_a_outils", "transition_de_phase",
              spearman(colonne(carbures, "revenu_C"),
                       colonne(carbures, "tenacite")), len(carbures))

    traces = lire("traces_fission_par_condition.csv")
    if traces:
        strates: dict[float, list] = {}
        for l in traces:
            strates.setdefault(nombre(l, "duree_h"), []).append(
                (nombre(l, "temperature_C"), nombre(l, "longueur_moyenne_um")))
        rhos = [spearman([t for t, _ in p], [v for _, v in p])
                for p in strates.values() if len(p) >= 3]
        rhos = [r for r in rhos if np.isfinite(r)]
        poser("ablation", "traces_fission", "traces_de_fission",
              float(np.mean(rhos)) if rhos else float("nan"), len(traces))

    surface = lire("surface_fischer_tropsch.csv")
    if surface:
        poser("histoire_vers_reponse", "fischer_tropsch", "reconstruction_de_surface",
              spearman(colonne(surface, "exposition_h"),
                       colonne(surface, "aire_chromatogramme")), len(surface))

    return mesures


def test_de_signe(rhos: list[float], attendu: int | None) -> dict:
    k = len(rhos)
    if k < 3:
        return {"jeux": k, "p_bilaterale": None, "motif": f"{k} jeu(x), minimum 3"}
    if attendu is None:
        positifs = sum(1 for r in rhos if r > 0)
        accord = max(positifs, k - positifs)
        sens = "+" if positifs >= k - positifs else "-"
    else:
        accord = sum(1 for r in rhos if np.sign(r) == attendu)
        sens = "+" if attendu > 0 else "-"
    queue = sum(comb(k, i) for i in range(accord, k + 1))
    p = min(1.0, 2 * queue / 2 ** k)
    return {"jeux": k, "concordants": accord, "sens_attendu": sens,
            "p_bilaterale": p, "p_minimal_atteignable": 2.0 / 2 ** k,
            "significatif": bool(p <= ALPHA)}


def main() -> int:
    mesures = rassembler()
    rapport = {"campagne": "WP-MAT-MEM-2026", "alpha": ALPHA,
               "principe": "test de signe sur les jeux, chaque jeu compte pour un",
               "relations": {}}

    entete = f"{'relation':<26}{'jeux':>6}{'concord.':>10}{'p':>10}{'p min':>9}   verdict"
    print(entete)
    print("-" * len(entete))
    for relation, attendu in ATTENDUS.items():
        entrees = mesures[relation]
        resultat = test_de_signe([e["rho"] for e in entrees], attendu)
        resultat["jeux_detail"] = [
            {"jeu": e["jeu"], "famille": e["famille"], "rho": round(e["rho"], 4),
             "unites": e["unites"]} for e in entrees]
        resultat["familles"] = sorted({e["famille"] for e in entrees})
        rapport["relations"][relation] = resultat
        if resultat.get("p_bilaterale") is None:
            print(f"{relation:<26}{resultat['jeux']:>6}{'—':>10}{'—':>10}{'—':>9}"
                  f"   {resultat['motif']}")
            continue
        verdict = ("soutient" if resultat["significatif"] else
                   "indetermine_par_atteignabilite"
                   if resultat["p_minimal_atteignable"] > ALPHA else "ne_soutient_pas")
        resultat["verdict"] = verdict
        accord = f"{resultat['concordants']}/{resultat['jeux']}"
        print(f"{relation:<26}{resultat['jeux']:>6}{accord:>10}"
              f"{resultat['p_bilaterale']:>10.4f}"
              f"{resultat['p_minimal_atteignable']:>9.4f}   {verdict}")
        for e in resultat["jeux_detail"]:
            print(f"      {e['jeu']:<24}{e['famille']:<26}{e['rho']:+.3f}"
                  f"  {e['unites']} unités")

    soutenues = [r for r, b in rapport["relations"].items()
                 if b.get("verdict") == "soutient"]
    rapport["relations_soutenues"] = soutenues
    print()
    print(f"{len(soutenues)} relation(s) soutenue(s) : {', '.join(soutenues) or 'aucune'}")

    DERIVE.mkdir(exist_ok=True)
    with SORTIE.open("w", encoding="utf-8", newline="") as flux:
        flux.write(json.dumps(rapport, ensure_ascii=False, indent=2) + "\n")
    print(f"écrit : {SORTIE.relative_to(ICI.parents[1]).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
