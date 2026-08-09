#!/usr/bin/env python3
"""Traces de fission recuites : extraction et test d'ablation.

Douze conditions de recuit, trois durées (1, 10, 100 h) et des températures de
500 à 775 °C. La condition est lue dans le nom d'image, `ZAD{durée}H{température}`.

Trace : longueur moyenne de trace par condition.
Statistique : corrélation de rang température-longueur, à durée constante.
Témoin : permutation des températures à l'intérieur de chaque strate de durée.

    python extraire_et_tester_traces_fission.py
"""
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

ICI = Path(__file__).resolve().parent
SOURCES = ICI / "SOURCES.json"
DERIVE = ICI / "derive"

ALPHA = 0.05
GRAINE = 20260809
TIRAGES = 20000
CONDITION = re.compile(r"ZAD(\d+)H(\d+)", re.I)
TRACES_MINIMUM = 5


def spearman(x, y) -> float:
    x, y = np.asarray(x, float), np.asarray(y, float)
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


def statistique(strates: dict[float, list[tuple[float, float]]]) -> float:
    """Moyenne des corrélations température-longueur, à durée constante."""
    rhos = []
    for points in strates.values():
        if len(points) < 3:
            continue
        rho = spearman([t for t, _ in points], [l for _, l in points])
        if np.isfinite(rho):
            rhos.append(rho)
    return float(np.mean(rhos)) if rhos else float("nan")


def main() -> int:
    config = json.loads(SOURCES.read_text(encoding="utf-8"))
    racine = (ICI / config["racine_locale"]).resolve()
    dossier = racine / "traces_fission_zircon" / "exploitable"
    tables = list(dossier.rglob("*.csv"))
    if not tables:
        print("Source non installée.")
        return 2

    par_condition: dict[tuple[float, float], list[float]] = defaultdict(list)
    for table in tables:
        with table.open(encoding="utf-8-sig", errors="replace", newline="") as flux:
            for ligne in csv.DictReader(flux):
                nom = ligne.get("Image Name") or ""
                correspondance = CONDITION.match(nom)
                if not correspondance:
                    continue
                try:
                    longueur = float(ligne["Line Length (µm)"])
                except (KeyError, ValueError):
                    continue
                duree = float(correspondance.group(1))
                temperature = float(correspondance.group(2))
                par_condition[(duree, temperature)].append(longueur)

    conditions = []
    for (duree, temperature), longueurs in sorted(par_condition.items()):
        if len(longueurs) < TRACES_MINIMUM:
            continue
        conditions.append({
            "source": "traces_fission_zircon",
            "duree_h": duree,
            "temperature_C": temperature,
            "n_traces": len(longueurs),
            "longueur_moyenne_um": float(np.mean(longueurs)),
            "longueur_ecart_type_um": float(np.std(longueurs, ddof=1)),
            "data_kind": "mesure_experimentale",
        })

    if not conditions:
        print("Aucune condition exploitable.")
        return 1

    DERIVE.mkdir(exist_ok=True)
    with (DERIVE / "traces_fission_par_condition.csv").open(
            "w", encoding="utf-8", newline="") as flux:
        redacteur = csv.DictWriter(flux, fieldnames=list(conditions[0]),
                                   lineterminator="\n")
        redacteur.writeheader()
        redacteur.writerows(conditions)

    strates: dict[float, list[tuple[float, float]]] = defaultdict(list)
    for c in conditions:
        strates[c["duree_h"]].append((c["temperature_C"], c["longueur_moyenne_um"]))

    observe = statistique(strates)
    aleatoire = np.random.default_rng(GRAINE)
    compte = 0
    for _ in range(TIRAGES):
        melange = {d: list(zip(aleatoire.permutation([t for t, _ in p]),
                               [l for _, l in p]))
                   for d, p in strates.items()}
        valeur = statistique(melange)
        if np.isfinite(valeur) and abs(valeur) >= abs(observe):
            compte += 1
    p = (1 + compte) / (1 + TIRAGES)

    exploitables = {d: p for d, p in strates.items() if len(p) >= 3}
    print(f"{sum(c['n_traces'] for c in conditions)} traces mesurées, "
          f"{len(conditions)} conditions de recuit.")
    print()
    entete = f"{'durée':>8}{'températures':>16}{'conditions':>12}{'rho':>10}"
    print(entete)
    print("-" * len(entete))
    for duree, points in sorted(strates.items()):
        temperatures = sorted(t for t, _ in points)
        rho = spearman([t for t, _ in points], [l for _, l in points]) if len(points) >= 3 else float("nan")
        print(f"{duree:>7.0f}h{str(temperatures)[:15]:>16}{len(points):>12}{rho:>10.4f}")

    if len(exploitables) < 2:
        verdict = "indetermine_par_atteignabilite"
        motif = f"{len(exploitables)} strate(s) de durée exploitable(s), minimum 2"
    elif p <= ALPHA and observe < 0:
        verdict = "soutient"
        motif = ("la longueur de trace décroît avec la température de recuit à durée "
                 "constante ; la permutation des températures dans chaque strate "
                 "annule l'effet")
    elif p <= ALPHA:
        verdict = "ne_soutient_pas"
        motif = f"effet significatif mais de signe positif, rho = {observe:.4f}"
    else:
        verdict = "ne_soutient_pas"
        motif = f"p = {p:.4f} > {ALPHA}"

    print()
    print(f"statistique stratifiée : rho moyen {observe:+.4f}, p = {p:.4f} "
          f"({TIRAGES} permutations)")
    print(f"VERDICT : {verdict}")
    print(f"  {motif}")

    sortie = DERIVE / "RESULTAT_TRACES_FISSION.json"
    with sortie.open("w", encoding="utf-8", newline="") as flux:
        flux.write(json.dumps({
            "campagne": "WP-MAT-MEM-2026",
            "famille": "traces_de_fission",
            "jeu": "zircon ZAD, recuit thermique de traces de fission induites",
            "plan": "3 durées x températures de 500 à 775 °C, 12 conditions",
            "ablation": "recuit thermique, dose = température à durée constante",
            "trace": "longueur moyenne de trace",
            "alpha": ALPHA, "graine": GRAINE, "tirages": TIRAGES,
            "traces_mesurees": sum(c["n_traces"] for c in conditions),
            "conditions": len(conditions),
            "strates_exploitables": len(exploitables),
            "rho_stratifie": observe,
            "p_permutation": p,
            "temoin": "permutation des températures dans chaque strate de durée",
            "verdict": verdict, "motif": motif,
            "statut_epistemique": "mesures d'instrument sur échantillons physiques",
        }, ensure_ascii=False, indent=2) + "\n")
    print(f"écrit : {sortie.relative_to(ICI.parents[1]).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
