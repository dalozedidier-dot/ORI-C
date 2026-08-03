"""Information portée par le codage des six dimensions — WP-S1.1.6 et S1.1.7.

Les 240 cellules de dimensions sont remplies. Ce script mesure **ce qu'elles
apportent**, question que la complétude ne pose pas.

    A. Décomposition. Chaque valeur est de la forme
       `<phrase de régime> — <suffixe>`. On sépare les deux et on compte les
       valeurs distinctes de chaque part.
    B. Redondance, WP-S1.1.7. Information mutuelle entre chaque dimension et
       le numéro de régime, puis entre dimensions.
    C. Apport prédictif, WP-S1.1.6. Une dimension améliore-t-elle la
       prédiction d'une variable qu'elle ne contient pas déjà — ici la
       fermeture de domaine — au-delà du seul régime ?

Une dimension dont l'information mutuelle avec le régime sature son entropie
propre ne dit rien de plus que le régime.

    python mesurer_dimensions.py [--base transitions_matiere.csv]
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

DIMENSIONS = ["dimension_n", "dimension_G", "dimension_I",
              "dimension_E", "dimension_Pi", "dimension_H"]
SEPARATEURS = (" — cas:", " — état postérieur:", " — fenêtre:", " depuis:", " — ")


def base_et_suffixe(valeur: str) -> tuple[str, str]:
    """Sépare la phrase de régime du suffixe propre à la transition."""
    for marqueur in SEPARATEURS:
        if marqueur in valeur:
            avant, apres = valeur.split(marqueur, 1)
            return avant.strip(), apres.strip()
    return valeur.strip(), ""


def entropie(valeurs) -> float:
    total = len(valeurs)
    if total == 0:
        return 0.0
    return -sum((n / total) * math.log2(n / total)
                for n in Counter(valeurs).values())


def information_mutuelle(a, b) -> float:
    total = len(a)
    if total == 0:
        return 0.0
    conjointe = Counter(zip(a, b))
    ca, cb = Counter(a), Counter(b)
    return sum(
        (n / total) * math.log2((n / total) /
                                ((ca[x] / total) * (cb[y] / total)))
        for (x, y), n in conjointe.items()
    )


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--base", type=Path,
                         default=Path("transitions_matiere.csv"))
    parseur.add_argument("--sortie", type=Path,
                         default=Path("information_dimensions.json"))
    arguments = parseur.parse_args()

    with arguments.base.open(encoding="utf-8-sig", newline="") as flux:
        lignes = list(csv.DictReader(flux, delimiter=";"))
    regimes = [l["regime_num"] for l in lignes]
    h_regime = entropie(regimes)

    # --- A. Décomposition ---------------------------------------------------
    decomposition = {}
    for d in DIMENSIONS:
        brutes = [l[d] for l in lignes]
        bases = [base_et_suffixe(v)[0] for v in brutes]
        suffixes = [base_et_suffixe(v)[1] for v in brutes]
        # Le suffixe reprend-il une colonne déjà présente ?
        reprises = {}
        for colonne in ("transition", "etat_posterieur", "date",
                        "etat_anterieur", "id"):
            if colonne not in lignes[0]:
                continue
            identiques = sum(
                1 for l, s in zip(lignes, suffixes)
                if s and s in (l[colonne] or "")
            )
            if identiques:
                reprises[colonne] = identiques
        decomposition[d] = {
            "valeurs_brutes_distinctes": len(set(brutes)),
            "valeurs_de_base_distinctes": len(set(bases)),
            "suffixes_non_vides": sum(1 for s in suffixes if s),
            "suffixe_reprend_une_colonne_existante": reprises,
        }

    # --- B. Redondance avec le régime, WP-S1.1.7 ---------------------------
    redondance = {}
    for d in DIMENSIONS:
        bases = [base_et_suffixe(l[d])[0] for l in lignes]
        h = entropie(bases)
        im = information_mutuelle(bases, regimes)
        redondance[d] = {
            "entropie_du_codage_bits": h,
            "information_mutuelle_avec_le_regime_bits": im,
            "part_expliquee_par_le_regime": (im / h) if h > 1e-12 else 1.0,
            "information_propre_bits": max(h - im, 0.0),
        }

    # --- Redondance entre dimensions ---------------------------------------
    croisee = {}
    for i, a in enumerate(DIMENSIONS):
        for b in DIMENSIONS[i + 1:]:
            va = [base_et_suffixe(l[a])[0] for l in lignes]
            vb = [base_et_suffixe(l[b])[0] for l in lignes]
            croisee[f"{a} / {b}"] = information_mutuelle(va, vb)

    # --- C. Apport prédictif, WP-S1.1.6 ------------------------------------
    # Cible : la transition ferme-t-elle un domaine ? C'est la seule variable
    # de la base qui ne figure dans aucune dimension.
    cible = [bool((l.get("etats_fermes") or "").strip()) for l in lignes]
    h_cible = entropie(cible)
    apport = {
        "cible": "fermeture de domaine",
        "entropie_de_la_cible_bits": h_cible,
        "positifs": sum(cible),
        "sur": len(cible),
        "information_mutuelle_regime_cible_bits":
            information_mutuelle(regimes, cible),
    }
    for d in DIMENSIONS:
        bases = [base_et_suffixe(l[d])[0] for l in lignes]
        apport[d] = {
            "information_mutuelle_avec_la_cible_bits":
                information_mutuelle(bases, cible),
        }
    # Gain conditionnel : ce que la dimension ajoute une fois le régime connu.
    for d in DIMENSIONS:
        bases = [base_et_suffixe(l[d])[0] for l in lignes]
        paires = list(zip(regimes, bases))
        apport[d]["gain_conditionnel_au_regime_bits"] = max(
            information_mutuelle(paires, cible)
            - information_mutuelle(regimes, cible), 0.0
        )

    rapport = {
        "transitions": len(lignes),
        "entropie_du_regime_bits": h_regime,
        "A_decomposition": decomposition,
        "B_redondance_avec_le_regime": redondance,
        "B_information_mutuelle_entre_dimensions_bits": croisee,
        "C_apport_predictif": apport,
        "lecture": (
            "Une dimension dont la part expliquée par le régime vaut 1,0 ne "
            "porte aucune information propre : elle est le régime réécrit. Un "
            "gain conditionnel nul signifie qu'elle n'améliore aucune "
            "prédiction une fois le régime connu."
        ),
    }
    arguments.sortie.write_text(
        json.dumps(rapport, indent=2, ensure_ascii=False), encoding="utf-8")

    print("A. Décomposition")
    for d, v in decomposition.items():
        print(f"  {d:14s} brutes {v['valeurs_brutes_distinctes']:2d}  "
              f"bases {v['valeurs_de_base_distinctes']:2d}  "
              f"suffixes {v['suffixes_non_vides']:2d}  "
              f"reprend {v['suffixe_reprend_une_colonne_existante']}")
    print("\nB. Redondance avec le régime")
    for d, v in redondance.items():
        print(f"  {d:14s} H={v['entropie_du_codage_bits']:.3f}  "
              f"IM={v['information_mutuelle_avec_le_regime_bits']:.3f}  "
              f"expliqué {v['part_expliquee_par_le_regime']:.1%}  "
              f"propre {v['information_propre_bits']:.3f} bits")
    print("\nC. Apport prédictif sur la fermeture de domaine")
    print(f"  entropie de la cible {h_cible:.3f} bits, "
          f"{apport['positifs']}/{apport['sur']} positifs")
    print(f"  régime seul : IM = "
          f"{apport['information_mutuelle_regime_cible_bits']:.3f} bits")
    for d in DIMENSIONS:
        print(f"  {d:14s} IM={apport[d]['information_mutuelle_avec_la_cible_bits']:.3f}  "
              f"gain conditionnel={apport[d]['gain_conditionnel_au_regime_bits']:.3f} bits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
