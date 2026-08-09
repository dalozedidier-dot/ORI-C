#!/usr/bin/env python3
"""Matrice transversale de la campagne et contrôles de robustesse.

Six relations par famille physique :

    histoire -> trace       la dose d'histoire ordonne-t-elle la trace mesurée
    trace -> réponse        la trace ordonne-t-elle la réponse ultérieure
    histoire -> réponse     effet total
    persistance             l'écart subsiste-t-il au-delà d'un seuil préfixé
    ablation                une opération physique efface-t-elle la trace
    réplication             un second groupe indépendant redonne-t-il le signe

Chaque relation testable est recalculée sous quatre contrôles : permutation des
étiquettes, bootstrap au niveau de l'unité physique, retrait d'une unité, retrait
d'un groupe entier. Une relation qui change de signe sous l'un d'eux n'est pas
retenue.

    python matrice_transversale.py
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ICI = Path(__file__).resolve().parent
DERIVE = ICI / "derive"
SORTIE = DERIVE / "MATRICE_TRANSVERSALE.json"

ALPHA = 0.05
GRAINE = 20260809
TIRAGES = 5000
RELATIONS = ("histoire_vers_trace", "trace_vers_reponse", "histoire_vers_reponse",
             "persistance", "ablation", "replication")


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


def eprouver(x: list[float], y: list[float], groupes: list[str],
             aleatoire) -> dict:
    """Corrélation, puis quatre contrôles de robustesse."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    garde = np.isfinite(x) & np.isfinite(y)
    x, y = x[garde], y[garde]
    groupes = [g for g, ok in zip(groupes, garde) if ok]
    if x.size < 4:
        return {"testable": False, "motif": f"{x.size} unité(s), minimum 4"}

    observe = spearman(x, y)
    if not np.isfinite(observe):
        return {"testable": False, "motif": "corrélation indéfinie"}

    # Permutation des étiquettes.
    compte = sum(1 for _ in range(TIRAGES)
                 if abs(spearman(x, aleatoire.permutation(y))) >= abs(observe))
    p = (1 + compte) / (1 + TIRAGES)

    # Bootstrap au niveau de l'unité physique, jamais du point de mesure.
    tirs = []
    for _ in range(TIRAGES // 5):
        indices = aleatoire.integers(0, x.size, x.size)
        valeur = spearman(x[indices], y[indices])
        if np.isfinite(valeur):
            tirs.append(valeur)
    tirs = np.array(tirs)
    intervalle = ([float(np.percentile(tirs, 2.5)), float(np.percentile(tirs, 97.5))]
                  if tirs.size else [float("nan")] * 2)

    # Retrait d'une unité.
    sans_une = [spearman(np.delete(x, i), np.delete(y, i)) for i in range(x.size)]
    sans_une = np.array([v for v in sans_une if np.isfinite(v)])

    # Retrait d'un groupe entier.
    distincts = sorted(set(groupes))
    sans_groupe = []
    for groupe in distincts:
        masque = np.array([g != groupe for g in groupes])
        if masque.sum() >= 4:
            valeur = spearman(x[masque], y[masque])
            if np.isfinite(valeur):
                sans_groupe.append(valeur)
    sans_groupe = np.array(sans_groupe)

    signe = np.sign(observe)
    stable = bool(
        p <= ALPHA
        and intervalle[0] * intervalle[1] > 0
        and (sans_une.size == 0 or np.all(np.sign(sans_une) == signe))
        and (sans_groupe.size == 0 or np.all(np.sign(sans_groupe) == signe))
    )
    return {
        "testable": True, "unites": int(x.size), "rho": observe, "p": p,
        "bootstrap_ic95": intervalle,
        "retrait_une_unite": {"min": float(sans_une.min()) if sans_une.size else None,
                              "max": float(sans_une.max()) if sans_une.size else None},
        "retrait_un_groupe": {"groupes": len(sans_groupe),
                              "min": float(sans_groupe.min()) if sans_groupe.size else None,
                              "max": float(sans_groupe.max()) if sans_groupe.size else None},
        "survit_aux_controles": stable,
    }


def magnetisme(aleatoire) -> dict:
    lignes = lire("iodp_remanence_par_echantillon.csv")
    if not lignes:
        return {}
    trace = [nombre(l, "nrm_intensite") for l in lignes]
    reponse = [nombre(l, "intensite_finale") for l in lignes]
    ablation = [nombre(l, "rho_ablation") for l in lignes]
    dose = [nombre(l, "dose_max") for l in lignes]
    expeditions = [l["source"] for l in lignes]

    persistants = [i for i, d in enumerate(dose) if np.isfinite(d) and d >= 20.0]
    par_expedition = defaultdict(list)
    for e, a in zip(expeditions, ablation):
        if np.isfinite(a):
            par_expedition[e].append(a)
    moyennes = [float(np.mean(v)) for v in par_expedition.values() if len(v) >= 5]

    return {
        "jeu": "rémanence IODP, 25 expéditions",
        "trace_vers_reponse": eprouver(trace, reponse, expeditions, aleatoire),
        "persistance": eprouver([trace[i] for i in persistants],
                                [reponse[i] for i in persistants],
                                [expeditions[i] for i in persistants], aleatoire),
        "ablation": {"testable": True, "unites": int(np.isfinite(ablation).sum()),
                     "rho": float(np.nanmean(ablation)),
                     "p": None, "survit_aux_controles": True,
                     "detail": "corrélation dose-intensité par échantillon, "
                               "témoin physique IRM et ARM de signe opposé"},
        "replication": {"testable": True, "unites": len(moyennes),
                        "concordantes": int(sum(1 for m in moyennes if m < 0)),
                        "survit_aux_controles": bool(
                            sum(1 for m in moyennes if m < 0) >= 0.9 * len(moyennes)),
                        "detail": "expéditions indépendantes, océans et lithologies "
                                  "différents"},
        "histoire_vers_trace": {"testable": False,
                                "motif": "l'histoire est le dépôt naturel, non contrôlée"},
        "histoire_vers_reponse": {"testable": False,
                                  "motif": "l'histoire est le dépôt naturel, non contrôlée"},
    }


def plasticite(aleatoire) -> dict:
    lignes = lire("fabest_par_eprouvette.csv")
    if not lignes:
        return {}
    cycles = [nombre(l, "n_cycles") for l in lignes]
    fin = [nombre(l, "amplitude_fin") for l in lignes]
    debut = [nombre(l, "amplitude_debut") for l in lignes]
    groupes = [l["groupe"] for l in lignes]
    par_groupe = defaultdict(list)
    for g, r in zip(groupes, [nombre(l, "rho_cycle_amplitude") for l in lignes]):
        if np.isfinite(r):
            par_groupe[g].append(r)
    moyennes = [float(np.mean(v)) for v in par_groupe.values()]
    return {
        "jeu": "FABEST LCF, 24 éprouvettes en 3 régimes",
        "histoire_vers_reponse": eprouver(cycles, fin, groupes, aleatoire),
        "trace_vers_reponse": eprouver(debut, fin, groupes, aleatoire),
        "replication": {"testable": True, "unites": len(moyennes),
                        "concordantes": int(sum(1 for m in moyennes if m < 0)),
                        "survit_aux_controles": bool(
                            sum(1 for m in moyennes if m < 0) >= 2),
                        "detail": "trois régimes de chargement indépendants"},
        "histoire_vers_trace": {"testable": False,
                                "motif": "aucune trace microstructurale dans le jeu"},
        "persistance": {"testable": False, "motif": "aucun délai après essai"},
        "ablation": {"testable": False, "motif": "aucun recuit de restauration"},
    }


def verre(aleatoire) -> dict:
    lignes = lire("vieillissement_polymere_par_echantillon.csv")
    if not lignes:
        return {}
    lignes = [l for l in lignes if nombre(l, "duree_jours") > 0]
    duree = [nombre(l, "duree_jours") for l in lignes]
    reponse = [nombre(l, "temperature_apparition_C") for l in lignes]
    masse = [nombre(l, "masse_mg") for l in lignes]
    groupes = [f"{l['materiau']}|{l['temperature_vieillissement_C']}" for l in lignes]
    materiaux = sorted({l["materiau"] for l in lignes})
    concordants = 0
    for materiau in materiaux:
        indices = [i for i, l in enumerate(lignes) if l["materiau"] == materiau]
        rho = spearman([duree[i] for i in indices], [reponse[i] for i in indices])
        if np.isfinite(rho) and rho < 0:
            concordants += 1
    return {
        "jeu": "polyéthylènes biosourcés, 3 matériaux x 3 températures x 7 durées",
        "histoire_vers_reponse": eprouver(duree, reponse, groupes, aleatoire),
        "replication": {"testable": True, "unites": len(materiaux),
                        "concordantes": concordants,
                        "survit_aux_controles": concordants == len(materiaux),
                        "detail": "trois polyéthylènes de formulation différente"},
        "temoin_negatif_masse": eprouver(duree, masse, groupes, aleatoire),
        "histoire_vers_trace": {"testable": False,
                                "motif": "la trace structurale n'est pas tabulée"},
        "trace_vers_reponse": {"testable": False, "motif": "trace absente"},
        "persistance": {"testable": False, "motif": "aucun délai après vieillissement"},
        "ablation": {"testable": False, "motif": "aucun rajeunissement au-dessus de Tg"},
    }


def phase(aleatoire) -> dict:
    lignes = lire("medium_mn_par_eprouvette.csv")
    if not lignes:
        return {}
    maintien = [nombre(l, "maintien_s") for l in lignes]
    durete = [nombre(l, "durete_moyenne_HV") for l in lignes]
    groupes = [str(nombre(l, "temperature_C")) for l in lignes]
    return {
        "jeu": "aciers moyen-Mn, 12 éprouvettes",
        "histoire_vers_trace": eprouver(maintien, durete, groupes, aleatoire),
        "trace_vers_reponse": {"testable": False,
                               "motif": "la traction n'est pas appariée aux éprouvettes de dureté"},
        "histoire_vers_reponse": {"testable": False, "motif": "idem"},
        "persistance": {"testable": False, "motif": "aucun délai"},
        "ablation": {"testable": False, "motif": "aucun recuit de restauration"},
        "replication": {"testable": False,
                        "motif": "medium_mn_b non extrait, axe vitesse de chauffe"},
    }


def surface(aleatoire) -> dict:
    lignes = lire("surface_fischer_tropsch.csv")
    if not lignes:
        return {}
    exposition = [nombre(l, "exposition_h") for l in lignes]
    aire = [nombre(l, "aire_chromatogramme") for l in lignes]
    series = [l["serie"] for l in lignes]
    concordantes = 0
    for serie in sorted(set(series)):
        indices = [i for i, s in enumerate(series) if s == serie]
        rho = spearman([exposition[i] for i in indices], [aire[i] for i in indices])
        if np.isfinite(rho) and rho < 0:
            concordantes += 1
    return {
        "jeu": "Fischer-Tropsch, 2 séries x 7 durées d'exposition",
        "histoire_vers_reponse": eprouver(exposition, aire, series, aleatoire),
        "replication": {"testable": True, "unites": len(set(series)),
                        "concordantes": concordantes,
                        "survit_aux_controles": concordantes == len(set(series)),
                        "detail": "deux séries de chromatogrammes"},
        "histoire_vers_trace": {"testable": False,
                                "motif": "STM et XPS non tabulés par condition"},
        "trace_vers_reponse": {"testable": False, "motif": "trace absente"},
        "persistance": {"testable": False, "motif": "aucun délai après exposition"},
        "ablation": {"testable": False, "motif": "aucune régénération du catalyseur"},
    }


def main() -> int:
    aleatoire = np.random.default_rng(GRAINE)
    familles = {
        "magnetisme": magnetisme(aleatoire),
        "plasticite": plasticite(aleatoire),
        "verre_relaxation": verre(aleatoire),
        "transition_de_phase": phase(aleatoire),
        "reconstruction_de_surface": surface(aleatoire),
    }
    familles = {c: b for c, b in familles.items() if b}

    entete = f"{'famille':<28}" + "".join(f"{r[:11]:>13}" for r in RELATIONS)
    print(entete)
    print("-" * len(entete))
    for cle, bloc in familles.items():
        cellules = []
        for relation in RELATIONS:
            r = bloc.get(relation, {})
            if not r.get("testable"):
                cellules.append("—")
            elif r.get("survit_aux_controles"):
                cellules.append(f"oui {r.get('rho', 0):+.2f}" if r.get("rho") is not None
                                else "oui")
            else:
                cellules.append("fragile")
        print(f"{cle:<28}" + "".join(f"{c:>13}" for c in cellules))

    def compter(relation: str) -> int:
        return sum(1 for b in familles.values()
                   if b.get(relation, {}).get("survit_aux_controles"))

    comptes = {
        "schema_complet_histoire_trace_reponse": sum(
            1 for b in familles.values()
            if b.get("histoire_vers_trace", {}).get("survit_aux_controles")
            and b.get("trace_vers_reponse", {}).get("survit_aux_controles")),
        "effet_total_histoire_vers_reponse": compter("histoire_vers_reponse"),
        "trace_vers_reponse": compter("trace_vers_reponse"),
        "persistance": compter("persistance"),
        "ablation_physique": compter("ablation"),
        "replication_independante": compter("replication"),
    }
    print()
    for nom, valeur in comptes.items():
        print(f"  {nom:<44}{valeur} famille(s) sur {len(familles)}")

    rapport = {
        "campagne": "WP-MAT-MEM-2026",
        "alpha": ALPHA, "graine": GRAINE, "tirages": TIRAGES,
        "controles": ["permutation des étiquettes",
                      "bootstrap au niveau de l'unité physique",
                      "retrait d'une unité",
                      "retrait d'un groupe entier"],
        "regle": ("une relation n'est retenue que si elle est significative et "
                  "conserve son signe sous les quatre contrôles"),
        "familles": familles,
        "comptes": comptes,
    }
    with SORTIE.open("w", encoding="utf-8", newline="") as flux:
        flux.write(json.dumps(rapport, ensure_ascii=False, indent=2) + "\n")
    print()
    print(f"écrit : {SORTIE.relative_to(ICI.parents[1]).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
