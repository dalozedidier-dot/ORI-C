#!/usr/bin/env python3
"""Puissance statistique du benchmark antibiotique longitudinal.

Le benchmark compare un modèle « état + histoire » à deux témoins sur dix plis
appariés. Il rapporte un gain moyen, une fraction de plis favorables et un test
de signe exact. Ce script répond à la question que ces trois nombres ne posent
pas : **le protocole peut-il seulement détecter l'effet qu'il cherche ?**

Il ne produit aucun verdict scientifique. Il caractérise la capacité de
détection du dispositif, à partir des plis appariés déjà publiés dans
`resultats/vivant_robustesse.json`.

    python plan_directeur/campagne_maximale_trois_branches/analyser_puissance_vivant.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy import stats

ICI = Path(__file__).resolve().parent
ENTREE = ICI / "resultats" / "vivant_robustesse.json"
SORTIE = ICI / "resultats" / "POWER_VIVANT_LONGITUDINAL.json"
ALPHA = 0.05
CIBLES = (0.80, 0.90)
TEMOINS = ("state_only", "equal_complexity")


def puissance_t_appariee(n: int, dz: float, alpha: float = ALPHA) -> float:
    """Puissance d'un t apparié bilatéral, loi t non centrale."""
    if n < 2 or dz == 0.0:
        return alpha
    critique = stats.t.ppf(1 - alpha / 2, n - 1)
    excentrement = dz * math.sqrt(n)
    return float(
        1 - stats.nct.cdf(critique, n - 1, excentrement)
        + stats.nct.cdf(-critique, n - 1, excentrement)
    )


def n_pour_puissance(dz: float, cible: float, plafond: int = 200_000) -> int | None:
    n = 3
    while n < plafond:
        if puissance_t_appariee(n, dz) >= cible:
            return n
        n += 1
    return None


def p_signe_bilateral(favorables: int, total: int) -> float:
    """p exact du test de signe bilatéral, sans approximation normale."""
    queue = sum(math.comb(total, i) for i in range(favorables, total + 1))
    return min(1.0, 2 * queue / 2 ** total)


def main() -> int:
    donnees = json.loads(ENTREE.read_text(encoding="utf-8"))
    bloc = donnees["antibiotic_history_robustness"]
    validation = bloc["group_cross_validation"]
    plis = validation["paired_fold_mae"]
    n_plis = len(plis)
    lignees = int(validation["lineages"])
    lignes = int(validation["rows"])

    histoire = np.array([p["history"] for p in plis], dtype=float)
    comparaisons = {}
    for temoin in TEMOINS:
        reference = np.array([p[temoin] for p in plis], dtype=float)
        differences = reference - histoire  # positif : l'histoire fait mieux
        moyenne = float(differences.mean())
        ecart_type = float(differences.std(ddof=1))
        dz = moyenne / ecart_type if ecart_type else 0.0
        statistique, valeur_p = stats.ttest_rel(reference, histoire)
        favorables = int((differences > 0).sum())

        besoins = {}
        for cible in CIBLES:
            n = n_pour_puissance(dz, cible)
            besoins[f"{cible:.2f}"] = (
                None
                if n is None
                else {
                    "plis": n,
                    "lignees_equivalentes": round(n * lignees / n_plis),
                    "mesures_equivalentes": round(n * lignes / n_plis),
                    "facteur_par_rapport_a_l_existant": round(n / n_plis, 1),
                }
            )

        comparaisons[temoin] = {
            "mae_temoin": float(reference.mean()),
            "mae_histoire": float(histoire.mean()),
            "gain_moyen_apparie": moyenne,
            "ecart_type_des_differences": ecart_type,
            "taille_effet_dz": dz,
            "plis_favorables": favorables,
            "t_apparie": float(statistique),
            "p_apparie": float(valeur_p),
            "puissance_atteinte": puissance_t_appariee(n_plis, dz),
            "n_requis": besoins,
        }

    signe = {
        str(k): p_signe_bilateral(k, n_plis) for k in range(n_plis // 2 + 1, n_plis + 1)
    }
    minimum_concluant = next(
        (int(k) for k, v in sorted(signe.items(), key=lambda kv: int(kv[0])) if v <= ALPHA),
        None,
    )

    rapport = {
        "protocol_id": "VIVANT-ANTIBIOTIQUE-LONGITUDINAL-PUISSANCE",
        "genere_par": "plan_directeur/campagne_maximale_trois_branches/analyser_puissance_vivant.py",
        "source": "resultats/vivant_robustesse.json",
        "alpha": ALPHA,
        "unite_independante": "lignee",
        "dispositif_actuel": {
            "plis": n_plis,
            "mesures": lignes,
            "lignees": lignees,
            "lignees_par_pli": lignees / n_plis,
        },
        "comparaisons": comparaisons,
        "test_de_signe_exact": {
            "p_par_nombre_de_plis_favorables": signe,
            "minimum_de_plis_favorables_pour_conclure": minimum_concluant,
            "lecture": (
                "Avec dix plis, le test de signe bilatéral ne peut pas descendre "
                "sous alpha tant que moins de neuf plis sur dix sont favorables. "
                "La règle de décision est donc quasi inatteignable à cette taille, "
                "indépendamment de l'ampleur réelle de l'effet."
            ),
        },
        "conclusion": (
            "Le dispositif actuel n'a pas la puissance de détecter l'effet qu'il "
            "mesure. Son résultat non concluant ne constitue donc pas une preuve "
            "d'absence d'effet : il constate que le protocole ne tranche pas."
        ),
    }

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Dispositif : {n_plis} plis, {lignes} mesures, {lignees} lignées.")
    for temoin, valeurs in comparaisons.items():
        print(
            f"  contre {temoin:18s} dz={valeurs['taille_effet_dz']:.4f} "
            f"puissance={valeurs['puissance_atteinte']:.3f} "
            f"p={valeurs['p_apparie']:.4f}"
        )
        for cible, besoin in valeurs["n_requis"].items():
            if besoin:
                print(
                    f"      puissance {float(cible):.0%} : {besoin['plis']} plis, "
                    f"~{besoin['lignees_equivalentes']} lignées "
                    f"(x{besoin['facteur_par_rapport_a_l_existant']})"
                )
    print(
        "Test de signe : au moins "
        f"{minimum_concluant} plis favorables sur {n_plis} sont nécessaires pour p<=alpha."
    )
    print(f"écrit : {SORTIE.relative_to(ICI.parents[1])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
