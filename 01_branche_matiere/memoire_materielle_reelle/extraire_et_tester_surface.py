#!/usr/bin/env python3
"""Reconstruction de surface : Fischer-Tropsch et cuivre sous CO2RR.

Fischer-Tropsch : deux séries de chromatogrammes à 0, 1, 2, 3, 4, 5 et 6 heures
d'exposition. Dose = durée d'exposition, réponse = aire du chromatogramme.
Témoin : permutation des durées dans chaque série.

Cuivre CO2RR : fractions de phases de surface au cours du temps, six espèces
suivies. Dose = temps, trace = fraction de chaque phase.

    python extraire_et_tester_surface.py
"""
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

from donnees_campagne import base_de

ICI = Path(__file__).resolve().parent
SOURCES = ICI / "SOURCES.json"
DERIVE = ICI / "derive"

ALPHA = 0.05
GRAINE = 20260809
TIRAGES = 20000
HEURE = re.compile(r"_(\d+)h\.txt$", re.I)
SERIE = re.compile(r"(GC_Fig\w+?)_\d+h\.txt$", re.I)


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


def aire_chromatogramme(chemin: Path) -> float:
    """Intégrale du signal sur le temps, en unités d'aire du détecteur."""
    temps, signal = [], []
    dans_donnees = False
    with chemin.open(encoding="utf-8-sig", errors="replace") as flux:
        for ligne in flux:
            if ligne.startswith("Chromatogram Data:"):
                dans_donnees = True
                continue
            if not dans_donnees:
                continue
            parties = ligne.rstrip("\n").split("\t")
            if len(parties) < 3:
                continue
            try:
                temps.append(float(parties[0]))
                signal.append(float(parties[2]))
            except ValueError:
                continue
    if len(temps) < 100:
        return float("nan")
    t, s = np.array(temps), np.array(signal)
    return float(np.trapezoid(s - np.median(s), t))


def extraire_fischer_tropsch(base: Path) -> list[dict]:
    lignes = []
    for chemin in sorted(base.rglob("GC_*h.txt")):
        heure = HEURE.search(chemin.name)
        serie = SERIE.search(chemin.name)
        if not heure or not serie:
            continue
        aire = aire_chromatogramme(chemin)
        if not np.isfinite(aire):
            continue
        lignes.append({
            "source": "fischer_tropsch", "serie": serie.group(1),
            "exposition_h": float(heure.group(1)),
            "aire_chromatogramme": aire,
            "data_kind": "mesure_experimentale",
        })
    return lignes


def extraire_cuivre(base: Path) -> list[dict]:
    lignes = []
    for chemin in sorted(base.glob("*_fraction.csv")):
        espece = chemin.stem.split("_", 1)[1].removesuffix("_fraction")
        points = []
        with chemin.open(encoding="utf-8-sig", errors="replace", newline="") as flux:
            lecteur = csv.reader(flux)
            next(lecteur, None)
            for ligne in lecteur:
                try:
                    points.append((float(ligne[0]), float(ligne[1])))
                except (ValueError, IndexError):
                    continue
        if len(points) < 5:
            continue
        temps = [t for t, _ in points]
        fractions = [f for _, f in points]
        lignes.append({
            "source": "cuivre_co2rr", "espece": espece,
            "n_points": len(points),
            "temps_min": min(temps), "temps_max": max(temps),
            "fraction_debut": fractions[0], "fraction_fin": fractions[-1],
            "rho_temps_fraction": spearman(temps, fractions),
            "data_kind": "mesure_experimentale",
        })
    return lignes


def p_permutation_stratifiee(strates: dict, aleatoire) -> tuple[float, float]:
    def statistique(s):
        rhos = [spearman([d for d, _ in p], [v for _, v in p])
                for p in s.values() if len(p) >= 3]
        rhos = [r for r in rhos if np.isfinite(r)]
        return float(np.mean(rhos)) if rhos else float("nan")

    observe = statistique(strates)
    if not np.isfinite(observe):
        return observe, 1.0
    compte = 0
    for _ in range(TIRAGES):
        melange = {k: list(zip(aleatoire.permutation([d for d, _ in p]),
                               [v for _, v in p]))
                   for k, p in strates.items()}
        valeur = statistique(melange)
        if np.isfinite(valeur) and abs(valeur) >= abs(observe):
            compte += 1
    return observe, (1 + compte) / (1 + TIRAGES)


def main() -> int:
    config = json.loads(SOURCES.read_text(encoding="utf-8"))
    racine = (ICI / config["racine_locale"]).resolve()
    base_ft = base_de("fischer_tropsch", racine)
    base_cu = base_de("cuivre_co2rr", racine)
    if base_ft is None and base_cu is None:
        print("source absente : fischer_tropsch et cuivre_co2rr")
        print("Résultats commités laissés intacts.")
        return 1

    DERIVE.mkdir(exist_ok=True)
    aleatoire = np.random.default_rng(GRAINE)
    rapport = {"campagne": "WP-MAT-MEM-2026", "famille": "reconstruction_de_surface",
               "alpha": ALPHA, "graine": GRAINE, "tirages": TIRAGES, "jeux": {}}

    if base_ft is not None:
        ft = extraire_fischer_tropsch(base_ft)
        if ft:
            with (DERIVE / "surface_fischer_tropsch.csv").open(
                    "w", encoding="utf-8", newline="") as flux:
                redacteur = csv.DictWriter(flux, fieldnames=list(ft[0]),
                                           lineterminator="\n")
                redacteur.writeheader()
                redacteur.writerows(ft)
            strates = defaultdict(list)
            for e in ft:
                strates[e["serie"]].append((e["exposition_h"], e["aire_chromatogramme"]))
            observe, p = p_permutation_stratifiee(strates, aleatoire)
            n_series = sum(1 for v in strates.values() if len(v) >= 3)
            verdict = ("soutient" if p <= ALPHA and n_series >= 2
                       else "indetermine_par_atteignabilite" if n_series < 2
                       else "ne_soutient_pas")
            rapport["jeux"]["fischer_tropsch"] = {
                "dose": "durée d'exposition au carbone, 0 à 6 h",
                "reponse": "aire du chromatogramme",
                "mesures": len(ft), "series": n_series,
                "rho_stratifie": observe, "p_permutation": p,
                "temoin": "permutation des durées dans chaque série",
                "verdict": verdict,
            }
            print(f"Fischer-Tropsch : {len(ft)} mesures, {n_series} séries, "
                  f"rho {observe:+.4f}, p = {p:.4f}  →  {verdict}")
            for serie, points in sorted(strates.items()):
                rho = spearman([d for d, _ in points], [v for _, v in points])
                print(f"    {serie:<18}{len(points):>3} points  rho {rho:+.4f}")

    if base_cu is not None:
        cu = extraire_cuivre(base_cu)
        if cu:
            with (DERIVE / "surface_cuivre_co2rr.csv").open(
                    "w", encoding="utf-8", newline="") as flux:
                redacteur = csv.DictWriter(flux, fieldnames=list(cu[0]),
                                           lineterminator="\n")
                redacteur.writeheader()
                redacteur.writerows(cu)
            rhos = np.array([e["rho_temps_fraction"] for e in cu
                             if np.isfinite(e["rho_temps_fraction"])])
            observe = float(np.mean(np.abs(rhos))) if rhos.size else float("nan")
            minimum = 2.0 / 2 ** rhos.size if rhos.size <= 20 else 0.0
            verdict = ("indetermine_par_atteignabilite" if minimum > ALPHA
                       else "soutient" if observe > 0.5 else "ne_soutient_pas")
            rapport["jeux"]["cuivre_co2rr"] = {
                "dose": "temps sous réduction du CO2",
                "trace": "fraction de chaque phase de surface",
                "especes": len(cu),
                "rho_absolu_moyen": observe,
                "p_minimal_atteignable": minimum,
                "verdict": verdict,
            }
            print()
            print(f"Cuivre CO2RR : {len(cu)} espèces suivies, "
                  f"|rho| moyen {observe:.4f}  →  {verdict}")
            for e in sorted(cu, key=lambda x: -abs(x["rho_temps_fraction"])):
                print(f"    {e['espece']:<18}{e['n_points']:>4} points  "
                      f"rho {e['rho_temps_fraction']:+.4f}")

    soutiennent = [c for c, b in rapport["jeux"].items() if b["verdict"] == "soutient"]
    rapport["verdict"] = "soutient" if soutiennent else "ne_soutient_pas"
    rapport["motif"] = (f"{len(soutiennent)} jeu(x) de surface soutiennent : "
                        f"{', '.join(soutiennent) or 'aucun'}")

    sortie = DERIVE / "RESULTAT_SURFACE.json"
    with sortie.open("w", encoding="utf-8", newline="") as flux:
        flux.write(json.dumps(rapport, ensure_ascii=False, indent=2) + "\n")
    print()
    print(f"VERDICT famille surface : {rapport['verdict']} — {rapport['motif']}")
    print(f"écrit : {sortie.relative_to(ICI.parents[1]).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
