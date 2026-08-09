#!/usr/bin/env python3
"""Même état, même stimulus, histoire différente : la réponse diffère-t-elle ?

C'est l'énoncé ORI-C lui-même, et non un corrélat. Les tests précédents de la
campagne demandaient si une dose d'histoire corrèle avec une réponse — ce qu'une
simple dépendance à l'état produit aussi. Ici l'état est tenu fixe.

Le jeu de boucles encastrées sépare les trois quantités :

    Bdc   aimantation continue     l'ÉTAT, tenu fixe
    BpM   amplitude de la majeure  l'HISTOIRE, seule à varier
    Bp, f amplitude et fréquence   le STIMULUS, tenu fixe
    perte réponse mesurée

Un bloc est un triplet (Bp, f, Bdc) : même état, même stimulus. Les points d'un
bloc ne diffèrent que par l'histoire.

STATUT : EXPLORATOIRE. Le plan a été choisi après inspection de la table, ce que
le protocole de campagne interdit pour un verdict. Aucun verdict confirmatoire
n'est rendu ; le résultat sert à préenregistrer un test sur un jeu indépendant.

    python tester_meme_etat_histoire_differente.py
"""
from __future__ import annotations

import json
from collections import defaultdict
from math import comb
from pathlib import Path

ICI = Path(__file__).resolve().parent
SOURCES = ICI / "SOURCES.json"
DERIVE = ICI / "derive"
SORTIE = DERIVE / "EXPLORATOIRE_MEME_ETAT.json"

ALPHA = 0.05


def monotone(valeurs: list[float]) -> int:
    """+1 croissante, -1 décroissante, 0 ni l'un ni l'autre."""
    if len(valeurs) < 2:
        return 0
    if all(b > a for a, b in zip(valeurs, valeurs[1:])):
        return 1
    if all(b < a for a, b in zip(valeurs, valeurs[1:])):
        return -1
    return 0


def binomiale_superieure(k: int, n: int, p: float) -> float:
    return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def main() -> int:
    config = json.loads(SOURCES.read_text(encoding="utf-8"))
    racine = (ICI / config["racine_locale"]).resolve()
    base = racine / "hysteresis_dynamique" / "exploitable"
    tables = list(base.rglob("BIAS_Loss_Table.txt"))
    if not tables:
        print("source absente : hysteresis_dynamique, dossier BIAS")
        print("Résultats commités laissés intacts.")
        return 1

    lignes = tables[0].read_text(encoding="utf-8", errors="replace").strip().splitlines()
    entete = lignes[0].split(",")
    points = [dict(zip(entete, l.split(","))) for l in lignes[1:]]

    blocs: dict[tuple, list[tuple[float, float]]] = defaultdict(list)
    for point in points:
        cle = (float(point["Bp_T"]), float(point["f_Hz"]), float(point["Bdc_T"]))
        blocs[cle].append((float(point["BpM_T"]), float(point["PowerLoss_Wperkg"])))

    exploitables = {c: sorted(v) for c, v in blocs.items() if len(v) >= 2}
    a_trois = {c: v for c, v in exploitables.items() if len(v) >= 3}

    print(f"{len(points)} points, {len(blocs)} blocs (Bp, f, Bdc).")
    print(f"{len(exploitables)} blocs portent au moins deux histoires à état et "
          f"stimulus identiques, dont {len(a_trois)} en portent trois.")
    print()

    entete_table = (f"{'Bp':>6}{'f':>8}{'Bdc':>7}   " +
                    f"{'pertes selon BpM croissant':<38}{'sens':>8}{'écart':>9}")
    print(entete_table)
    print("-" * len(entete_table))
    detail = []
    for (bp, f, bdc), valeurs in sorted(exploitables.items()):
        pertes = [p for _, p in valeurs]
        sens = monotone(pertes)
        etendue = (max(pertes) - min(pertes)) / min(pertes)
        detail.append({"Bp_T": bp, "f_Hz": f, "Bdc_T": bdc,
                       "BpM": [b for b, _ in valeurs], "pertes": pertes,
                       "sens": sens, "ecart_relatif": etendue})
        fleche = {1: "monte", -1: "descend", 0: "ni l'un ni l'autre"}[sens]
        print(f"{bp:>6.2f}{f:>8.0f}{bdc:>7.2f}   "
              f"{'  '.join(f'{p:.4f}' for p in pertes):<38}{fleche:>8}{etendue:>8.2%}")

    # Premier test : la monotonie. Sous l'hypothèse que l'histoire n'agit pas,
    # l'ordre des trois pertes d'un bloc est quelconque : 2 des 6 permutations
    # sont monotones, donc p = 1/3 par bloc.
    monotones = sum(1 for d in detail if len(d["pertes"]) >= 3 and d["sens"] != 0)
    n_trois = len(a_trois)
    p_monotonie = binomiale_superieure(monotones, n_trois, 1 / 3) if n_trois else 1.0

    # Second test, indépendant du premier : les deux amplitudes de stimulus
    # 0,05 T et 0,15 T sont deux mesures distinctes du même état. Sous
    # l'hypothèse nulle, elles s'accordent sur le sens une fois sur deux.
    par_etat: dict[float, dict[float, int]] = defaultdict(dict)
    for d in detail:
        par_etat[d["Bdc_T"]][d["Bp_T"]] = d["sens"]
    apparies = [(s[0.05], s[0.15]) for s in par_etat.values()
                if 0.05 in s and 0.15 in s]
    accords = sum(1 for a, b in apparies if a == b and a != 0)
    p_accord = (binomiale_superieure(accords, len(apparies), 0.5)
                if apparies else 1.0)

    print()
    print(f"monotonie   : {monotones} blocs sur {n_trois} à trois histoires, "
          f"p = {p_monotonie:.5f}   (1/3 par bloc sous l'hypothèse nulle)")
    print(f"concordance : {accords} états sur {len(apparies)} où les deux "
          f"amplitudes de stimulus donnent le même sens, p = {p_accord:.5f}")

    inversions = sorted({d["Bdc_T"] for d in detail if d["sens"] == 1}), \
        sorted({d["Bdc_T"] for d in detail if d["sens"] == -1})
    print()
    print(f"l'effet de l'histoire monte aux états {inversions[0]} "
          f"et descend aux états {inversions[1]}")
    print("le sens dépend donc de l'état : ce n'est pas un décalage constant")

    rapport = {
        "campagne": "WP-MAT-MEM-2026",
        "statut": "EXPLORATOIRE, plan choisi après inspection, aucun verdict rendu",
        "question": ("à état et stimulus identiques, une histoire différente "
                     "change-t-elle la réponse"),
        "jeu": "anneau FeSi, boucles mineures encastrées dans une majeure",
        "etat": "Bdc, aimantation continue", "histoire": "BpM, amplitude de la majeure",
        "stimulus": "Bp et f, tenus fixes dans chaque bloc",
        "blocs": len(exploitables), "blocs_a_trois_histoires": n_trois,
        "monotonie": {"blocs_monotones": monotones, "blocs": n_trois,
                      "p_sous_hypothese_nulle_un_tiers": p_monotonie},
        "concordance_entre_amplitudes": {"accords": accords, "etats": len(apparies),
                                         "p_sous_hypothese_nulle_un_demi": p_accord},
        "inversion_du_sens": {"monte_aux_etats": inversions[0],
                              "descend_aux_etats": inversions[1]},
        "detail": detail,
        "confirmatoire_requis": (
            "geler ce plan puis l'appliquer à un jeu indépendant portant des "
            "boucles mineures encastrées à plusieurs amplitudes de majeure"),
    }
    DERIVE.mkdir(exist_ok=True)
    with SORTIE.open("w", encoding="utf-8", newline="") as flux:
        flux.write(json.dumps(rapport, ensure_ascii=False, indent=2) + "\n")
    print()
    print(f"écrit : {SORTIE.relative_to(ICI.parents[1]).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
