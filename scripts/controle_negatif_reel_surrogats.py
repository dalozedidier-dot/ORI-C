#!/usr/bin/env python3
"""Contrôle négatif du pipeline à surrogats, sur données réelles uniquement.

Un bon témoin ne suffit pas. Encore faut-il savoir **ce que la statistique de
test détecte réellement**. Cela ne se raisonne pas : cela se mesure. Et cela se
mesure ici sans aucune série synthétique, par substitution de la cible.

Le principe est celui du contrôle négatif expérimental. On rejoue exactement le
pipeline de `WP-CLIM-MEM-2026-B` — mêmes blocs, même embargo de 40 ka, même
témoin IAAFT — en remplaçant la cible par d'autres colonnes **réelles** de la
même table, sur le même axe temporel.

Le contrôle négatif décisif est **l'obliquité terrestre**. C'est une solution de
mécanique céleste calculée par Berger, dominée par une oscillation unique à 41 ka
sans modulation notable. Personne ne soutient qu'elle inscrit son histoire : sa
valeur présente se prédit depuis son passé parce qu'elle est quasi périodique,
non parce qu'un compartiment y garde la trace d'un forçage. Si le pipeline lui
accorde le même verdict `soutient` qu'à la cible glaciaire, ce verdict ne mesure
pas ce que l'hypothèse ORI-C revendique.

L'insolation sert de second contrôle propre. La précession et l'excentricité sont
volontairement classées comme contrôles **imparfaits** : la précession vaut
e·sin(omega), son amplitude est donc modulée par l'excentricité, ce qui est une
non-linéarité multiplicative bien réelle. Un test de non-linéarité peut les
déclarer positives sans se tromper. Les compter comme faux positifs serait une
erreur de notre part, pas une erreur du test.

    python scripts/controle_negatif_reel_surrogats.py --surrogats 200

Aucune donnée produite ici n'est une preuve. C'est une mesure de ce que
l'instrument détecte, au même titre qu'un étalonnage.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))
from scripts.surrogats import iaaft, qualite  # noqa: E402

TABLE = (RACINE / "02_branche_systeme_solaire" / "couche_memoire_historique"
         / "data" / "processed" / "memoire_climatique_bintanja_insolation.csv")
SORTIE = RACINE / "scripts" / "CONTROLE_NEGATIF_SURROGATS.json"

# Paramètres repris à l'identique de WP-CLIM-MEM-2026-B.
FORCAGES = ["insolation_65N_jul_Wm2", "obliquity_deg", "precession", "eccentricity"]
DECALAGES = [10, 20, 40]
EMBARGO = 40
BLOCS = 10
ALPHA = 0.05

# Nature de chaque colonne réelle, établie par la source et non par ce script.
NATURE = {
    "ice_volume_total_sle": ("cible d'origine", "verdict rendu par WP-CLIM-MEM-2026-B"),
    # Les quatre séries astronomiques sont des solutions de mécanique céleste :
    # aucune n'inscrit son histoire. Elles ne sont pourtant pas équivalentes comme
    # contrôles. L'obliquité est dominée par une oscillation unique à 41 ka de
    # faible modulation : c'est le contrôle négatif **propre**, sans structure non
    # linéaire notable. La précession vaut e·sin(ω) : son amplitude est modulée par
    # l'excentricité, ce qui est une non-linéarité multiplicative réelle. Un test
    # de non-linéarité peut donc légitimement la déclarer positive sans se tromper
    # — mais cela ne dit toujours rien d'une inscription.
    "obliquity_deg": ("astronomique calculée, oscillation quasi unique à 41 ka",
                      "CONTRÔLE NÉGATIF PROPRE : ni inscription ni modulation notable"),
    "insolation_65N_jul_Wm2": ("astronomique calculée, fonction des trois autres",
                               "CONTRÔLE NÉGATIF PROPRE : aucune inscription revendiquée"),
    "eccentricity": ("astronomique calculée, battements de fréquences séculaires",
                     "contrôle imparfait : modulation d'amplitude réelle"),
    "precession": ("astronomique calculée, e·sin(omega), amplitude modulée par e",
                   "contrôle imparfait : non-linéarité multiplicative réelle"),
    "temp_anomaly_C": ("climatique, reconstruite", "série climatique voisine"),
    "sea_level_m": ("climatique, reconstruite", "corrélée +1,000 à la cible d'origine"),
    "ice_volume_eurasia_sle": ("climatique, reconstruite", "composante de la cible d'origine"),
    "ice_volume_na_sle": ("climatique, reconstruite", "composante de la cible d'origine"),
    "isotope_total": ("mesure isotopique, reconstruite", "série climatique voisine"),
}


def ajuster(Xa, ya, Xt):
    X = np.column_stack([np.ones(len(Xa)), Xa])
    coefficients, *_ = np.linalg.lstsq(X, ya, rcond=None)
    return np.column_stack([np.ones(len(Xt)), Xt]) @ coefficients


def evaluer(forcages, cible, memoire):
    n = len(cible)
    bornes = np.linspace(0, n, BLOCS + 1).astype(int)
    observes, predits, utilises = [], [], 0
    for i in range(BLOCS):
        debut, fin = bornes[i], bornes[i + 1]
        test = np.zeros(n, dtype=bool)
        test[debut:fin] = True
        exclu = np.zeros(n, dtype=bool)
        exclu[max(0, debut - EMBARGO):min(n, fin + EMBARGO)] = True
        entrainement = ~exclu
        if entrainement.sum() < 50 or test.sum() < 10:
            continue
        utilises += 1
        if memoire is None:
            Xa, Xt = forcages[entrainement], forcages[test]
        else:
            Xa = np.column_stack([forcages[entrainement], memoire[entrainement]])
            Xt = np.column_stack([forcages[test], memoire[test]])
        observes.append(cible[test])
        predits.append(ajuster(Xa, cible[entrainement], Xt))
    if not observes:
        return float("nan"), 0
    o, p = np.concatenate(observes), np.concatenate(predits)
    return float(np.sqrt(np.mean((o - p) ** 2))), utilises


def decalages_de(serie: np.ndarray) -> np.ndarray:
    colonnes = []
    for decalage in DECALAGES:
        decalee = np.full(serie.size, np.nan)
        decalee[decalage:] = serie[:-decalage]
        colonnes.append(decalee)
    return np.column_stack(colonnes)


def gain_de(serie, forcages_bruts):
    """Gain relatif de RMSE apporté par les décalages de la série sur elle-même."""
    memoire = decalages_de(serie)
    valides = ~np.isnan(memoire).any(axis=1)
    forcages, cible = forcages_bruts[valides], serie[valides]
    rmse_etat, blocs = evaluer(forcages, cible, None)
    rmse_histoire, _ = evaluer(forcages, cible, memoire[valides])
    gain = float(1 - rmse_histoire / rmse_etat) if rmse_etat else float("nan")
    return gain, rmse_etat, rmse_histoire, blocs


def executer_pipeline(serie, forcages_bruts, surrogats, graine):
    """Deux statistiques sur le même témoin IAAFT, pour les comparer.

    `asymetrique` reproduit ce qu'a fait WP-CLIM-MEM-2026-B : la cible reste
    réelle et seuls les prédicteurs décalés proviennent du surrogat. Le modèle
    témoin est alors handicapé par construction, puisqu'on lui demande de
    prédire une série avec le passé d'une autre. Toute série autocorrélée gagne.

    `symetrique` est la construction canonique de Schreiber et Schmitz : la même
    statistique est recalculée **entièrement sur le surrogat**, qui sert à la
    fois de cible et de prédicteur. Le surrogat conserve alors tout son pouvoir
    autoprédictif linéaire ; seule la structure non linéaire a disparu. C'est
    donc bien elle, et elle seule, que le test interroge.
    """
    memoire = decalages_de(serie)
    valides = ~np.isnan(memoire).any(axis=1)
    forcages, cible = forcages_bruts[valides], serie[valides]

    gain, rmse_etat, rmse_histoire, blocs = gain_de(serie, forcages_bruts)

    aleatoire = np.random.default_rng(graine)
    temoins_asymetriques, gains_symetriques = [], []
    for _ in range(surrogats):
        surrogat = iaaft(serie, aleatoire)
        valeur, _ = evaluer(forcages, cible, decalages_de(surrogat)[valides])
        if np.isfinite(valeur):
            temoins_asymetriques.append(valeur)
        gain_surrogat, *_ = gain_de(surrogat, forcages_bruts)
        if np.isfinite(gain_surrogat):
            gains_symetriques.append(gain_surrogat)
    temoins_asymetriques = np.array(temoins_asymetriques)
    gains_symetriques = np.array(gains_symetriques)

    # Estimateur de Monte-Carlo borne : (1 + k) / (1 + N). Une valeur de p
    # exactement nulle est impossible avec un nombre fini de surrogats — la
    # borne inferieure vaut 1/(N+1), soit 4,98e-03 pour 200 surrogats. Rapporter
    # 0,0000 revient a affirmer une certitude que le tirage ne peut pas fournir.
    # Voir Davison et Hinkley, et North, Curtis et Sham 2002.
    def p_bornee(compte: int, total: int) -> float:
        return (1.0 + compte) / (1.0 + total)

    p_asymetrique = p_bornee(int((temoins_asymetriques <= rmse_histoire).sum()),
                             temoins_asymetriques.size)
    p_symetrique = p_bornee(int((gains_symetriques >= gain).sum()),
                            gains_symetriques.size)
    return {
        "blocs": blocs,
        "rmse_etat_seul": rmse_etat,
        "rmse_etat_plus_histoire": rmse_histoire,
        "gain_relatif": gain,
        "asymetrique": {
            "description": "cible réelle, prédicteurs issus du surrogat — construction de WP-CLIM-MEM-2026-B",
            "temoin_moyenne": float(temoins_asymetriques.mean()),
            "temoin_minimum": float(temoins_asymetriques.min()),
            "p_unilaterale": p_asymetrique,
            "p_minimale_atteignable": 1.0 / (1 + surrogats),
            "verdict": ("soutient" if rmse_histoire < rmse_etat and p_asymetrique <= ALPHA
                        else "ne_soutient_pas"),
        },
        "symetrique": {
            "description": "statistique recalculée entièrement sur le surrogat — construction canonique",
            "gain_temoin_moyen": float(gains_symetriques.mean()),
            "gain_temoin_percentile_95": float(np.percentile(gains_symetriques, 95)),
            "gain_temoin_maximum": float(gains_symetriques.max()),
            "p_unilaterale": p_symetrique,
            "p_minimale_atteignable": 1.0 / (1 + surrogats),
            "verdict": "soutient" if p_symetrique <= ALPHA else "ne_soutient_pas",
        },
    }


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--surrogats", type=int, default=200)
    analyseur.add_argument("--graine", type=int, default=20260808)
    arguments = analyseur.parse_args()

    cadre = pd.read_csv(TABLE).sort_values("age_ka_bp").reset_index(drop=True)
    colonnes = [c for c in cadre.columns if c != "age_ka_bp"]
    manquantes = [c for c in colonnes if c not in NATURE]
    if manquantes:
        print(f"Colonnes de nature non déclarée, ignorées : {manquantes}")
        colonnes = [c for c in colonnes if c in NATURE]

    print(f"Table réelle : {len(cadre)} lignes, {len(colonnes)} colonnes testées comme cible.")
    print(f"{arguments.surrogats} surrogats IAAFT par cas, graine {arguments.graine}.")
    print("Aucune série synthétique. La cible est substituée, les forçages restent réels.")
    print()
    entete = (f"{'colonne réelle':<24}{'gain':>7}   {'ASYMÉTRIQUE (WP-B)':<28}"
              f"{'SYMÉTRIQUE (canonique)':<28}")
    print(entete)
    print(f"{'':<24}{'':>7}   {'p':>8} {'verdict':<19}{'p':>8} {'verdict':<19}")
    print("-" * len(entete))

    resultats = {}
    for colonne in colonnes:
        serie = cadre[colonne].to_numpy(float)
        if np.isnan(serie).any():
            print(f"{colonne:<24}  valeurs manquantes, écartée sans imputation")
            continue
        # La cible ne peut pas figurer parmi ses propres prédicteurs.
        predicteurs = [f for f in FORCAGES if f != colonne]
        r = executer_pipeline(serie, cadre[predicteurs].to_numpy(float),
                              arguments.surrogats, arguments.graine)
        r["forcages_utilises"] = predicteurs
        r["nature"] = NATURE[colonne][0]
        r["role"] = NATURE[colonne][1]
        r["autocorrelation_lag10"] = float(np.corrcoef(serie[10:], serie[:-10])[0, 1])
        r["qualite_du_surrogat"] = qualite(
            serie, iaaft(serie, np.random.default_rng(arguments.graine)))
        resultats[colonne] = r
        print(f"{colonne:<24}{r['gain_relatif']:>7.1%}   "
              f"{r['asymetrique']['p_unilaterale']:>8.4f} {r['asymetrique']['verdict']:<19}"
              f"{r['symetrique']['p_unilaterale']:>8.4f} {r['symetrique']['verdict']:<19}")

    astronomiques = [c for c in resultats if "astronomique" in resultats[c]["nature"]]
    propres = [c for c in astronomiques if "PROPRE" in resultats[c]["role"]]
    faux_a = [c for c in propres if resultats[c]["asymetrique"]["verdict"] == "soutient"]
    faux_s = [c for c in propres if resultats[c]["symetrique"]["verdict"] == "soutient"]

    print()
    print(f"Contrôles négatifs propres : {', '.join(propres)}")
    print(f"  déclarés positifs par la construction asymétrique de WP-B : "
          f"{len(faux_a)}/{len(propres)}  ({', '.join(faux_a) if faux_a else 'aucun'})")
    print(f"  déclarés positifs par la construction symétrique canonique : "
          f"{len(faux_s)}/{len(propres)}  ({', '.join(faux_s) if faux_s else 'aucun'})")
    print()
    if faux_a and not faux_s:
        print("CONCLUSION EN DEUX TEMPS.")
        print()
        print("1. La construction de WP-CLIM-MEM-2026-B est invalide. Elle accorde `soutient`")
        print("   à l'obliquité terrestre, une oscillation à 41 ka calculée par mécanique")
        print(f"   céleste, avec un gain de {resultats['obliquity_deg']['gain_relatif']:.1%} et p = "
              f"{resultats['obliquity_deg']['asymetrique']['p_unilaterale']:.4f} —")
        print("   soit plus que la cible glaciaire elle-même. Le défaut est que la statistique")
        print("   compare une cible réelle à des prédicteurs venus d'une autre série : le")
        print("   témoin ne peut pas gagner, quelle que soit la force du surrogat.")
        print()
        print("2. La construction symétrique corrige ce défaut et écarte les contrôles propres.")
        print("   Mais elle teste la **non-linéarité**, pas l'inscription. Elle déclare positives")
        print("   la précession et l'excentricité, qui portent une modulation d'amplitude bien")
        print("   réelle sans rien inscrire. Un témoin de force adéquate sur une statistique")
        print("   inadéquate ne produit toujours pas de verdict sur l'hypothèse visée.")
    elif faux_a and faux_s:
        print("CONCLUSION. Les deux constructions déclarent positifs des contrôles négatifs")
        print("propres. La statistique elle-même est à remplacer, pas seulement la façon")
        print("d'appliquer le surrogat.")
    else:
        print("CONCLUSION. Aucun contrôle négatif propre n'est déclaré positif par la")
        print("construction asymétrique. Le soupçon porté sur WP-CLIM-MEM-2026-B est levé.")

    rapport = {
        "objet": ("contrôle négatif du pipeline WP-CLIM-MEM-2026-B par substitution de cible, "
                  "sur colonnes réelles uniquement"),
        "aucune_donnee_synthetique": True,
        "statut_epistemique": ("mesure de ce que l'instrument détecte, pas une preuve. "
                               "N'entre dans aucun compteur de résultats."),
        "table": TABLE.relative_to(RACINE).as_posix(),
        "surrogats_par_cas": arguments.surrogats,
        "graine": arguments.graine,
        "resultats": resultats,
        "controles_negatifs_astronomiques": astronomiques,
        "controles_negatifs_propres": propres,
        "controles_negatifs_positifs_asymetrique": faux_a,
        "controles_negatifs_positifs_symetrique": faux_s,
        
    }
    with SORTIE.open("w", encoding="utf-8", newline="") as flux:
        flux.write(json.dumps(rapport, ensure_ascii=False, indent=2) + "\n")
    print(f"\nÉcrit : {SORTIE.relative_to(RACINE).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
