#!/usr/bin/env python3
"""Vieillissement thermique de polyéthylènes biosourcés : la troisième famille.

Le jeu porte le plan de dose le plus net de toute la campagne, et son auteur le
décrit lui-même dans sa notice : trois polyéthylènes vieillis à **90, 100 et
110 °C pendant 1, 2, 5, 8, 12, 16 et 20 jours**, plus un échantillon non vieilli
noté `0`. Le nom de fichier porte la condition :
`DSC_OOT_{matériau}_{température}-{jours}_{répétition}`.

## Correspondance ORI-C

| étape | grandeur |
|---|---|
| histoire | oxydation thermique, température × durée |
| dose | la durée, à température fixée |
| réponse | **température d'apparition de l'oxydation** sous rampe identique |
| témoin d'histoire nulle | les fichiers `_0_`, non vieillis |

La réponse est mesurée sous une rampe identique pour tous — 25 °C à 300 °C à
10 K/min, inscrit dans l'en-tête de chaque fichier. Le stimulus final est donc
rigoureusement le même, ce que l'énoncé de `C-MAT-MEM-01` exige.

## Définition de la réponse, fixée avant lecture

La température d'apparition de l'oxydation est prise comme **le premier point où
le signal DSC s'écarte de plus de cinq écarts-types de sa ligne de base**, la
ligne de base étant estimée sur la fenêtre 60–120 °C, avant tout événement
d'oxydation. Le seuil et la fenêtre sont arrêtés avant d'avoir regardé un seul
résultat ; sans quoi le choix se ferait sur ce qui donne le bon signe.

Cette définition est plus fruste que l'extrapolation de tangentes du logiciel
d'instrument, et c'est délibéré : elle est reproductible sans paramètre caché.

## Statistique et témoin

Un matériau, une température : la corrélation de rang entre durée de vieillissement
et température d'apparition. Neuf combinaisons matériau × température au plus.
Témoin : sign-flip exact sur ces corrélations.

**Témoin négatif.** La masse de l'échantillon figure dans chaque en-tête et ne
dépend pas de la durée de vieillissement — les prélèvements sont indépendants.
Si elle est déclarée corrélée à la dose, la statistique est fautive.

    python extraire_et_tester_vieillissement.py
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
FENETRE_BASE = (60.0, 120.0)
SEUIL_ECARTS_TYPES = 5.0
MOTIF = re.compile(r"DSC_OOT_(LDPE-[A-Z]+-\d+)_(\d+)-?(\d+)?_(\d+)\.*txt$", re.I)


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


def p_sign_flip(valeurs: np.ndarray) -> tuple[float, str]:
    n = valeurs.size
    if n == 0:
        return 1.0, "aucune valeur"
    observe = abs(float(valeurs.mean()))
    compte = 0
    for masque in range(1 << n):
        signes = np.array([1.0 if masque >> i & 1 else -1.0 for i in range(n)])
        if abs(float((valeurs * signes).mean())) >= observe:
            compte += 1
    return compte / (1 << n), f"sign-flip exact, {1 << n} attributions"


def lire_courbe(chemin: Path) -> tuple[np.ndarray, np.ndarray, float]:
    """Températures, signal DSC, masse de l'échantillon."""
    temperatures, signaux = [], []
    masse = float("nan")
    donnees = False
    with chemin.open(encoding="utf-8", errors="replace") as flux:
        for ligne in flux:
            if ligne.startswith("#SAMPLE MASS"):
                try:
                    masse = float(ligne.split(":")[1].strip().replace(",", "."))
                except (IndexError, ValueError):
                    pass
            if ligne.startswith("##"):
                donnees = True
                continue
            if not donnees:
                continue
            parties = ligne.strip().split(";")
            if len(parties) < 3:
                continue
            try:
                temperatures.append(float(parties[0]))
                signaux.append(float(parties[2]))
            except ValueError:
                continue
    return np.array(temperatures), np.array(signaux), masse


def temperature_d_apparition(temperatures, signaux) -> float:
    """Premier écart de plus de cinq écarts-types à la ligne de base."""
    base = (temperatures >= FENETRE_BASE[0]) & (temperatures <= FENETRE_BASE[1])
    if base.sum() < 20:
        return float("nan")
    moyenne, ecart = signaux[base].mean(), signaux[base].std()
    if ecart == 0:
        return float("nan")
    apres = temperatures > FENETRE_BASE[1]
    depassement = apres & (np.abs(signaux - moyenne) > SEUIL_ECARTS_TYPES * ecart)
    if not depassement.any():
        return float("nan")
    return float(temperatures[np.argmax(depassement)])


def main() -> int:
    config = json.loads(SOURCES.read_text(encoding="utf-8"))
    racine = (ICI / config["racine_locale"]).resolve()
    dossier = racine / "recuit_thermique_polymere" / "exploitable"
    if not dossier.is_dir():
        print("Source non installée.")
        return 2

    echantillons = []
    for chemin in sorted(dossier.glob("DSC_OOT_*")):
        correspondance = MOTIF.search(chemin.name)
        if not correspondance:
            continue
        materiau, premier, second, repetition = correspondance.groups()
        # `_0_` est le témoin non vieilli : température nulle, durée nulle.
        if second is None:
            temperature, jours = 0.0, 0.0
        else:
            temperature, jours = float(premier), float(second)
        temperatures, signaux, masse = lire_courbe(chemin)
        if temperatures.size < 50:
            continue
        apparition = temperature_d_apparition(temperatures, signaux)
        echantillons.append({
            "source": "recuit_thermique_polymere",
            "materiau": materiau.upper(),
            "temperature_vieillissement_C": temperature,
            "duree_jours": jours,
            "repetition": int(repetition),
            "masse_mg": masse,
            "temperature_apparition_C": apparition,
            "points_de_courbe": int(temperatures.size),
            "data_kind": "mesure_experimentale",
        })

    if not echantillons:
        print("Aucun échantillon extrait.")
        return 1

    DERIVE.mkdir(exist_ok=True)
    with (DERIVE / "vieillissement_polymere_par_echantillon.csv").open(
            "w", encoding="utf-8", newline="") as flux:
        redacteur = csv.DictWriter(flux, fieldnames=list(echantillons[0]),
                                   lineterminator="\n")
        redacteur.writeheader()
        redacteur.writerows(echantillons)

    valides = [e for e in echantillons
               if np.isfinite(e["temperature_apparition_C"]) and e["duree_jours"] > 0]
    temoins = [e for e in echantillons if e["duree_jours"] == 0]

    groupes = defaultdict(list)
    for e in valides:
        groupes[(e["materiau"], e["temperature_vieillissement_C"])].append(e)

    rhos, rhos_masse, detail = [], [], {}
    for (materiau, temperature), groupe in sorted(groupes.items()):
        if len(groupe) < 3:
            continue
        rho = spearman([g["duree_jours"] for g in groupe],
                       [g["temperature_apparition_C"] for g in groupe])
        rho_masse = spearman([g["duree_jours"] for g in groupe],
                             [g["masse_mg"] for g in groupe])
        if np.isfinite(rho):
            rhos.append(rho)
            detail[f"{materiau} {temperature:.0f}C"] = {
                "echantillons": len(groupe), "rho_duree_apparition": rho,
                "rho_duree_masse": rho_masse if np.isfinite(rho_masse) else None,
            }
        if np.isfinite(rho_masse):
            rhos_masse.append(rho_masse)

    rhos = np.array(rhos)
    rhos_masse = np.array(rhos_masse)
    p, methode = p_sign_flip(rhos)
    p_masse, _ = p_sign_flip(rhos_masse)

    print(f"{len(echantillons)} échantillons extraits, {len(temoins)} témoins non vieillis.")
    print(f"{len(detail)} combinaisons matériau × température exploitables.")
    print()
    entete = f"{'condition':<24}{'n':>4}{'rho durée/apparition':>24}{'rho durée/masse':>18}"
    print(entete)
    print("-" * len(entete))
    for nom, bloc in detail.items():
        masse = bloc["rho_duree_masse"]
        print(f"{nom:<24}{bloc['echantillons']:>4}{bloc['rho_duree_apparition']:>24.4f}"
              f"{(f'{masse:.4f}' if masse is not None else 'n/a'):>18}")

    temoin_plat = p_masse > ALPHA
    if not temoin_plat:
        verdict = "invalide"
        motif = (f"le témoin négatif est significatif, p = {p_masse:.4f} : la masse "
                 f"prélevée ne peut pas dépendre de la durée de vieillissement")
    elif p <= ALPHA:
        verdict = "soutient"
        motif = ("la température d'apparition de l'oxydation suit la durée de "
                 "vieillissement sous rampe identique ; la masse ne suit pas")
    elif rhos.size < 6:
        verdict = "indetermine_par_atteignabilite"
        motif = (f"{rhos.size} combinaisons, sign-flip exact : p minimal "
                 f"2/2**{rhos.size} = {2.0 / 2 ** rhos.size:.4f}")
    else:
        verdict = "ne_soutient_pas"
        motif = "la dose de vieillissement n'ordonne pas la réponse"

    print()
    print(f"signal : rho moyen {rhos.mean():+.4f}, p = {p:.4f}  ({methode})")
    print(f"témoin : rho moyen {rhos_masse.mean():+.4f}, p = {p_masse:.4f}")
    print()
    print(f"VERDICT : {verdict}")
    print(f"  {motif}")

    sortie = DERIVE / "RESULTAT_VIEILLISSEMENT_POLYMERE.json"
    with sortie.open("w", encoding="utf-8", newline="") as flux:
        flux.write(json.dumps({
            "campagne": "WP-MAT-MEM-2026",
            "famille": "verre_relaxation",
            "jeu": "polyéthylènes biosourcés vieillis thermiquement",
            "plan": "3 matériaux × 3 températures × 7 durées, plus témoin non vieilli",
            "definition_de_la_reponse": (
                f"premier écart de plus de {SEUIL_ECARTS_TYPES} écarts-types à la ligne "
                f"de base estimée sur {FENETRE_BASE[0]}–{FENETRE_BASE[1]} °C, "
                f"fixée avant lecture des résultats"),
            "alpha": ALPHA, "graine": GRAINE,
            "echantillons": len(echantillons), "temoins_non_vieillis": len(temoins),
            "conditions": detail,
            "signal": {"rho_moyen": float(rhos.mean()), "p": p, "methode": methode},
            "temoin_negatif_masse": {"rho_moyen": float(rhos_masse.mean()), "p": p_masse},
            "verdict": verdict, "motif": motif,
            "statut_epistemique": "mesures d'instrument sur échantillons physiques",
        }, ensure_ascii=False, indent=2) + "\n")
    print(f"écrit : {sortie.relative_to(ICI.parents[1]).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
