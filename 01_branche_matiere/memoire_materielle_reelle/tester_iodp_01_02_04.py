#!/usr/bin/env python3
"""Diagnostics IODP associés à C-MAT-MEM-01, 02 et 04.

Les statistiques historiques sont conservées, mais le script refuse désormais
de les attribuer aux critères gelés quand leur plan expérimental ne correspond
pas à l'énoncé : dépôt naturel non assigné pour C01, résistance à l'effacement
plutôt que délai/relaxation pour C02, et absence de bras sans histoire pour C04.

    python tester_iodp_01_02_04.py
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ICI = Path(__file__).resolve().parent
TABLE = ICI / "derive" / "iodp_remanence_par_echantillon.csv"
SORTIE = ICI / "derive" / "RESULTATS_C_MAT_MEM_01_02_04.json"

ALPHA = 0.05
TIRAGES = 10000
GRAINE = 20260809
DOSE_PERSISTANCE_MT = 20.0
ETAPES_MINIMUM = 3


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    def rangs(v):
        ordre = np.argsort(v, kind="mergesort")
        r = np.empty(len(v), dtype=float)
        r[ordre] = np.arange(len(v), dtype=float)
        return r
    rx, ry = rangs(x), rangs(y)
    if rx.std() == 0 or ry.std() == 0:
        return float("nan")
    return float(np.corrcoef(rx, ry)[0, 1])


def p_permutation(x: np.ndarray, y: np.ndarray, aleatoire) -> tuple[float, float]:
    """Corrélation observée, et p par permutation des étiquettes."""
    observe = spearman(x, y)
    if not np.isfinite(observe):
        return observe, 1.0
    compte = 0
    for _ in range(TIRAGES):
        if abs(spearman(x, aleatoire.permutation(y))) >= abs(observe):
            compte += 1
    return observe, (1 + compte) / (1 + TIRAGES)


def flottant(valeur):
    try:
        return float(valeur)
    except (TypeError, ValueError):
        return float("nan")


def charger() -> list[dict]:
    lignes = []
    with TABLE.open(encoding="utf-8", newline="") as flux:
        for ligne in csv.DictReader(flux):
            lignes.append({
                "source": ligne["source"],
                "echantillon": ligne["physical_sample_id"],
                "nrm": flottant(ligne["nrm_intensite"]),
                "finale": flottant(ligne["intensite_finale"]),
                "fraction": flottant(ligne["fraction_restante"]),
                "dose_max": flottant(ligne["dose_max"]),
                "n_ablation": int(ligne["n_etapes_ablation"] or 0),
                "rho_ablation": flottant(ligne["rho_ablation"]),
                "n_inscription": int(ligne["n_etapes_inscription"] or 0),
                "rho_inscription": flottant(ligne["rho_inscription"]),
            })
    return lignes


def main() -> int:
    if not TABLE.exists():
        print("Table absente. Exécuter extraire_iodp.py.")
        return 2

    lignes = charger()
    aleatoire = np.random.default_rng(GRAINE)
    resultats = {}
    print(f"{len(lignes)} échantillons dans la table par échantillon.")
    print()

    # ---------------------------------------------------------- C-MAT-MEM-01
    valides = [l for l in lignes
               if np.isfinite(l["nrm"]) and np.isfinite(l["finale"])
               and l["nrm"] > 0 and l["n_ablation"] >= ETAPES_MINIMUM]
    trace = np.array([l["nrm"] for l in valides])
    reponse = np.array([l["finale"] for l in valides])
    rho01, p01 = p_permutation(trace, reponse, aleatoire)
    resultats["C-MAT-MEM-01"] = {
        "enonce": "la trace ordonne-t-elle les réponses sous stimulus final comparable",
        "echantillons": len(valides),
        "rho_trace_reponse": rho01,
        "p_permutation": p01,
        "temoin": "permutation des étiquettes d'échantillon, appariement détruit",
        "verdict": "non_testable_avec_ce_jeu",
        "resultat_partiel": (
            "association_trace_reponse_robuste" if p01 <= ALPHA and rho01 > 0
            else "association_trace_reponse_non_soutenue"
        ),
        "motif_non_testable": (
            "l'histoire naturelle de dépôt n'est ni contrôlée ni assignée ; "
            "la cohérence trace-réponse ne suffit pas au C01 gelé"
        ),
        "nature_du_controle": "permutation_statistique",
        "portee": ("cohérence exigée par l'énoncé, vérifiée. Qu'une trace plus forte "
                   "laisse un résidu plus fort n'est pas une découverte : ce critère "
                   "contrôle la cohérence, il ne l'exploite pas comme preuve d'un "
                   "mécanisme."),
    }

    # ---------------------------------------------------------- C-MAT-MEM-02
    persistants = [l for l in valides if l["dose_max"] >= DOSE_PERSISTANCE_MT]
    if len(persistants) >= 10:
        t2 = np.array([l["nrm"] for l in persistants])
        r2 = np.array([l["finale"] for l in persistants])
        rho02, p02 = p_permutation(t2, r2, aleatoire)
        resultat02 = ("resistance_effacement_robuste"
                      if p02 <= ALPHA and rho02 > 0
                      else "resistance_effacement_non_soutenue")
    else:
        rho02, p02, resultat02 = float("nan"), 1.0, "non_testable_avec_ce_jeu"
    resultats["C-MAT-MEM-02"] = {
        "enonce": f"la différence subsiste-t-elle au-delà de {DOSE_PERSISTANCE_MT} mT",
        "seuil_prefixe_mT": DOSE_PERSISTANCE_MT,
        "echantillons": len(persistants),
        "rho_trace_reponse": rho02,
        "p_permutation": p02,
        "verdict": "non_testable_avec_ce_jeu",
        "resultat_partiel": resultat02,
        "motif_non_testable": (
            "20 mT mesure une résistance à l'effacement, pas une persistance "
            "après délai, cycles ou relaxation contrôlée au sens du C02 gelé"
        ),
        "rattachement_correct": "diagnostic d'ablation/résistance associé à C03",
    }

    # ---------------------------------------------------------- C-MAT-MEM-04
    apparies = [l for l in lignes
                if l["n_inscription"] >= ETAPES_MINIMUM
                and l["n_ablation"] >= ETAPES_MINIMUM
                and np.isfinite(l["rho_ablation"]) and np.isfinite(l["rho_inscription"])]
    if len(apparies) >= 10:
        naturelle = np.array([l["rho_ablation"] for l in apparies])
        imposee = np.array([l["rho_inscription"] for l in apparies])
        differences = naturelle - imposee
        observe = abs(float(differences.mean()))
        compte = 0
        for _ in range(TIRAGES):
            signes = aleatoire.choice((-1.0, 1.0), size=differences.size)
            if abs(float((differences * signes).mean())) >= observe:
                compte += 1
        p04 = (1 + compte) / (1 + TIRAGES)
        resultat04 = ("difference_naturelle_imposee_detectee"
                      if p04 <= ALPHA else "difference_naturelle_imposee_non_detectee")
        ecart = float(differences.mean())
    else:
        p04, resultat04, ecart = 1.0, "non_testable_avec_ce_jeu", float("nan")
    resultats["C-MAT-MEM-04"] = {
        "enonce": ("la trace naturelle et la trace imposée en laboratoire se "
                   "comportent-elles différemment sous le même traitement"),
        "echantillons_apparies": len(apparies),
        "ecart_moyen_rho": ecart,
        "p_sign_flip": p04,
        "temoin": "sign-flip sur les écarts appariés, même échantillon des deux côtés",
        "verdict": "non_testable_avec_ce_jeu",
        "resultat_partiel": resultat04,
        "motif_non_testable": (
            "les deux bras possèdent une histoire ; aucun bras sous le même "
            "stimulus final sans histoire préalable n'est disponible"
        ),
        "nature_du_controle": "comparaison_physique_appariee_mais_non_C04",
    }

    entete = f"{'critère':<16}{'n':>7}{'statistique':>14}{'p':>10}   verdict"
    print(entete)
    print("-" * len(entete))
    print(f"{'C-MAT-MEM-01':<16}{resultats['C-MAT-MEM-01']['echantillons']:>7}"
          f"{rho01:>14.4f}{p01:>10.4f}   {resultats['C-MAT-MEM-01']['verdict']}")
    print(f"{'C-MAT-MEM-02':<16}{len(persistants):>7}{rho02:>14.4f}{p02:>10.4f}   non_testable_avec_ce_jeu")
    print(f"{'C-MAT-MEM-04':<16}{len(apparies):>7}{ecart:>14.4f}{p04:>10.4f}   non_testable_avec_ce_jeu")

    rapport = {
        "campagne": "WP-MAT-MEM-2026",
        "jeu": "rémanence IODP, 25 expéditions",
        "alpha": ALPHA, "graine": GRAINE, "tirages": TIRAGES,
        "estimateur_de_p": "(1 + k) / (1 + N)",
        "statut_epistemique": "mesures d'instrument sur échantillons physiques",
        "criteres": resultats,
    }
    with SORTIE.open("w", encoding="utf-8", newline="") as flux:
        flux.write(json.dumps(rapport, ensure_ascii=False, indent=2) + "\n")
    print()
    print(f"écrit : {SORTIE.relative_to(ICI.parents[1]).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
