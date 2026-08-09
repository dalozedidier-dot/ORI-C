#!/usr/bin/env python3
"""C-MAT-MEM-03 : l'ablation physique fait-elle décroître la trace.

Statistique : corrélation de rang dose-intensité par échantillon.
Témoins : les étapes d'inscription IRM et ARM, de signe opposé attendu,
et la permutation des doses dans chaque échantillon.

    python tester_ablation_iodp.py
"""
from __future__ import annotations

import csv
import gzip
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ICI = Path(__file__).resolve().parent
# La table par mesure vit hors dépôt : 18,8 Mo n'ont rien à faire dans Git. Elle
# se régénère par `extraire_iodp.py` depuis les sources, dont la provenance est
# inscrite. Seule la table par échantillon, 709 ko, est versionnée.
VERSIONNEE = ICI / "donnees" / "iodp_remanence_par_mesure.csv.gz"
RACINE_LOCALE = (ICI / json.loads(
    (ICI / "SOURCES.json").read_text(encoding="utf-8"))["racine_locale"]).resolve()
LOCALE = RACINE_LOCALE / "derive_local" / "iodp_remanence_par_mesure.csv"
TABLE = VERSIONNEE if VERSIONNEE.exists() else LOCALE
SORTIE = ICI / "derive" / "RESULTAT_C_MAT_MEM_03.json"

ALPHA = 0.05
TIRAGES = 10000
GRAINE = 20260809
ETAPES_MINIMUM = 3
TYPES_ABLATION = ("AD", "TD")
TYPES_INSCRIPTION = ("IRM", "ARM")


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    """Corrélation de rang, sans dépendance externe."""
    def rangs(v: np.ndarray) -> np.ndarray:
        ordre = np.argsort(v, kind="mergesort")
        r = np.empty(len(v), dtype=float)
        r[ordre] = np.arange(len(v), dtype=float)
        # moyenne des rangs pour les ex aequo
        valeurs, debuts, comptes = np.unique(v, return_index=True, return_counts=True)
        for valeur, compte in zip(valeurs, comptes):
            if compte > 1:
                masque = v == valeur
                r[masque] = r[masque].mean()
        return r

    rx, ry = rangs(x), rangs(y)
    if rx.std() == 0 or ry.std() == 0:
        return float("nan")
    return float(np.corrcoef(rx, ry)[0, 1])


def p_sign_flip(valeurs: np.ndarray, aleatoire: np.random.Generator) -> tuple[float, str]:
    """Sign-flip bilatéral sur la moyenne. Exact si possible, sinon Monte-Carlo."""
    n = valeurs.size
    observe = abs(float(valeurs.mean()))
    if n <= 20:
        compte = 0
        for masque in range(1 << n):
            signes = np.array([1.0 if masque >> i & 1 else -1.0 for i in range(n)])
            if abs(float((valeurs * signes).mean())) >= observe:
                compte += 1
        return compte / (1 << n), f"sign-flip exact, {1 << n} attributions"
    compte = 0
    for _ in range(TIRAGES):
        signes = aleatoire.choice((-1.0, 1.0), size=n)
        if abs(float((valeurs * signes).mean())) >= observe:
            compte += 1
    return (1 + compte) / (1 + TIRAGES), f"sign-flip Monte-Carlo, {TIRAGES} tirages"


def correlations(mesures: list[dict], champ: str, types: tuple,
                 permuter=None) -> dict[str, float]:
    """Corrélation dose / `champ` pour chaque échantillon exploitable."""
    par_echantillon: dict[str, list[dict]] = defaultdict(list)
    for m in mesures:
        if m["ablation_type"] in types:
            par_echantillon[m["cle"]].append(m)

    resultats = {}
    for cle, lignes in par_echantillon.items():
        doses = np.array([l["dose"] for l in lignes], dtype=float)
        cibles = np.array([l[champ] for l in lignes], dtype=float)
        garde = np.isfinite(doses) & np.isfinite(cibles)
        if garde.sum() < ETAPES_MINIMUM:
            continue
        d, c = doses[garde], cibles[garde]
        if permuter is not None:
            d = permuter.permutation(d)
        rho = spearman(d, c)
        if math.isfinite(rho):
            resultats[cle] = rho
    return resultats


def evaluer(nom: str, rhos: dict[str, float], aleatoire, attendu: str) -> dict:
    valeurs = np.array(list(rhos.values()), dtype=float)
    moyenne = float(valeurs.mean())
    negatifs = int((valeurs < 0).sum())
    p, methode = p_sign_flip(valeurs, aleatoire)
    significatif = p <= ALPHA
    return {
        "grandeur": nom,
        "attendu": attendu,
        "echantillons": int(valeurs.size),
        "rho_moyen": moyenne,
        "rho_median": float(np.median(valeurs)),
        "fraction_negative": negatifs / valeurs.size if valeurs.size else float("nan"),
        "p_bilaterale": p,
        "methode_du_temoin": methode,
        "significatif": bool(significatif),
    }


def main() -> int:
    if not TABLE.exists():
        print(f"Table absente : {TABLE}")
        print("Exécuter extraire_iodp.py.")
        return 2

    ouvrir = (lambda: gzip.open(TABLE, "rt", encoding="utf-8", newline="")
              if TABLE.suffix == ".gz"
              else TABLE.open(encoding="utf-8", newline=""))
    mesures = []
    with ouvrir() as flux:
        for ligne in csv.DictReader(flux):
            mesures.append({
                "cle": f"{ligne['source']}|{ligne['physical_sample_id']}",
                "ablation_type": ligne["ablation_type"],
                "dose": float(ligne["dose"]) if ligne["dose"] else float("nan"),
                "trace_value": float(ligne["trace_value"]),
                "profondeur_m": float(ligne["profondeur_m"]) if ligne["profondeur_m"] else float("nan"),
                "source": ligne["source"],
            })

    aleatoire = np.random.default_rng(GRAINE)
    signal = correlations(mesures, "trace_value", TYPES_ABLATION)
    temoin_physique = correlations(mesures, "trace_value", TYPES_INSCRIPTION)
    temoin_permute = correlations(mesures, "trace_value", TYPES_ABLATION,
                                  permuter=np.random.default_rng(GRAINE))

    print(f"{len(mesures)} mesures, {len({m['cle'] for m in mesures})} échantillons.")
    print(f"{len(signal)} échantillons avec au moins {ETAPES_MINIMUM} étapes "
          f"d'ablation exploitables.")
    print()

    resultat_signal = evaluer("ablation AD et TD", signal, aleatoire,
                              "décroissance avec la dose : rho négatif")
    resultat_physique = evaluer("inscription IRM et ARM", temoin_physique, aleatoire,
                                "TÉMOIN PHYSIQUE : rho positif attendu, sens opposé")
    resultat_permute = evaluer("ablation, doses permutées", temoin_permute, aleatoire,
                               "TÉMOIN STATISTIQUE : rho proche de zéro attendu")

    entete = f"{'grandeur':<28}{'n':>6}{'rho moyen':>12}{'% négatifs':>12}{'p':>10}"
    print(entete)
    print("-" * len(entete))
    for r in (resultat_signal, resultat_physique, resultat_permute):
        print(f"{r['grandeur']:<28}{r['echantillons']:>6}{r['rho_moyen']:>12.4f}"
              f"{r['fraction_negative']:>11.1%}{r['p_bilaterale']:>10.4f}")

    # Réplication : le signe du rho moyen, expédition par expédition.
    par_source: dict[str, list[float]] = defaultdict(list)
    for cle, rho in signal.items():
        par_source[cle.split("|")[0]].append(rho)
    repliques = {s: float(np.mean(v)) for s, v in par_source.items() if len(v) >= 5}
    concordantes = sum(1 for v in repliques.values() if v < 0)

    print()
    print(f"Réplication : {concordantes} expéditions sur {len(repliques)} donnent "
          f"un rho moyen négatif.")

    permute_plat = abs(resultat_permute["rho_moyen"]) < 0.1
    physique_oppose = resultat_physique["rho_moyen"] > 0

    if not permute_plat:
        verdict = "invalide"
        motif = (f"la permutation des doses conserve un rho de "
                 f"{resultat_permute['rho_moyen']:.3f} : la corrélation ne vient pas "
                 f"de l'ordre des doses, la statistique est inadéquate")
    elif not physique_oppose:
        verdict = "invalide"
        motif = (f"le témoin physique donne un rho de "
                 f"{resultat_physique['rho_moyen']:.3f}, du même signe que le signal : "
                 f"le test ne distingue pas l'ablation de l'inscription")
    elif resultat_signal["significatif"] and resultat_signal["rho_moyen"] < 0:
        verdict = "soutient"
        motif = ("la trace décroît avec la dose d'ablation physique ; l'inscription "
                 "IRM et ARM donne le signe opposé sur les mêmes échantillons ; la "
                 "permutation des doses annule l'effet")
    else:
        verdict = "ne_soutient_pas"
        motif = "la décroissance n'est pas établie contre ses témoins"

    print()
    print(f"VERDICT C-MAT-MEM-03 : {verdict}")
    print(f"  {motif}")

    rapport = {
        "critere": "C-MAT-MEM-03",
        "campagne": "WP-MAT-MEM-2026",
        "niveau_de_temoin": 6,
        "justification_du_niveau": (
            "le témoin est une opération physique réellement pratiquée sur "
            "l'échantillon — champ alternatif ou chauffage — et non un surrogat calculé"),
        "alpha": ALPHA,
        "graine": GRAINE,
        "tirages": TIRAGES,
        "etapes_minimum": ETAPES_MINIMUM,
        "signal": resultat_signal,
        "temoin_physique_inscription": resultat_physique,
        "temoin_statistique_permutation": resultat_permute,
        "replication": {"expeditions": len(repliques), "concordantes": concordantes,
                        "rho_moyen_par_expedition": repliques},
        "verdict": verdict,
        "motif": motif,
        "statut_epistemique": (
            "mesures d'instrument sur échantillons physiques : preuve empirique primaire"),
    }
    with SORTIE.open("w", encoding="utf-8", newline="") as flux:
        flux.write(json.dumps(rapport, ensure_ascii=False, indent=2) + "\n")
    print(f"écrit : {SORTIE.relative_to(ICI.parents[1]).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
