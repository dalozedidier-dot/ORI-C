"""G2 corrigé — asymétrie temporelle sur un masque centré.

Défaut du G2 d'origine. Le masque d'entraînement prenait les 55 % premiers
points du tableau. En sens avant cela couvrait 2600-1170 ka ; après
retournement, 0-1430 ka. Les deux directions n'ajustaient donc pas les mêmes
données, et « sens du temps » se trouvait confondu avec « quel segment ».

Correction. Un masque **centré et exactement symétrique** est invariant par
retournement : l'indice `i` devient `n-1-i`, et l'intervalle `[a, n-a)` se
transforme en lui-même. Les deux directions ajustent alors rigoureusement les
mêmes points physiques, et la seule différence restante est l'ordre dans lequel
le modèle les traverse — c'est-à-dire ce que le test veut mesurer.

Une asymétrie résiduelle subsiste et n'est pas éliminable : la condition
initiale `observe[0]` et la trajectoire de mise en régime avant le masque
diffèrent d'un sens à l'autre. C'est une composante du sens du temps, pas un
biais de segment, et elle s'applique identiquement à tous les modèles comparés.
"""

from __future__ import annotations

import json
import time

import numpy as np

from core import OUTPUT_ROOT, fit_best_of_seeds, rmse, simulate
from g_tests_reels_2 import BUDGET, GRAINES, MODELES, charger, normaliser

OUT = OUTPUT_ROOT / "tests_reels"
PART_ENTRAINEMENT = 0.55


def masque_centre_symetrique(n: int, part: float) -> np.ndarray:
    """Intervalle centré `[a, n-a)`, invariant par retournement du tableau."""
    longueur = int(round(part * n))
    if (n - longueur) % 2:          # garantit la symétrie exacte
        longueur += 1
    debut = (n - longueur) // 2
    masque = np.zeros(n, dtype=bool)
    masque[debut:debut + longueur] = True
    if not np.array_equal(masque, masque[::-1]):
        raise AssertionError("le masque n'est pas symétrique")
    return masque


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    donnees = charger()
    n = len(donnees["observe"])
    masque = masque_centre_symetrique(n, PART_ENTRAINEMENT)
    indices = np.flatnonzero(masque)
    age = donnees["age"]
    print(f"masque centré : {masque.sum()} points, "
          f"{age[indices[0]]:.0f}-{age[indices[-1]]:.0f} ka, "
          f"identique après retournement", flush=True)

    resultat = {}
    for sens in ("avant", "arriere"):
        depart = time.perf_counter()
        if sens == "avant":
            brut_o, brut_f = donnees["observe"], donnees["forcage"]
        else:
            brut_o = donnees["observe"][::-1].copy()
            brut_f = donnees["forcage"][::-1].copy()
        observe, forcage = normaliser(brut_o, brut_f, masque)
        resultat[sens] = {}
        for modele in MODELES:
            meilleur, _ = fit_best_of_seeds(
                modele, forcage, observe, masque, GRAINES,
                bounds_name="wide", **BUDGET,
            )
            predit = simulate(modele, forcage, observe[0], meilleur.vector)
            resultat[sens][modele] = rmse(observe[masque], predit[masque])
        print(f"   sens {sens} fait en {time.perf_counter() - depart:.0f} s",
              flush=True)

    asymetrie = {
        m: resultat["arriere"][m] - resultat["avant"][m] for m in MODELES
    }
    rapport = {
        "masque": {
            "points": int(masque.sum()),
            "age_debut_ka": float(age[indices[0]]),
            "age_fin_ka": float(age[indices[-1]]),
            "symetrique_par_retournement": True,
        },
        "rmse_ajustement": resultat,
        "asymetrie_temporelle": asymetrie,
        "asymetrie_relative": {
            m: float(asymetrie[m] / resultat["avant"][m]) for m in MODELES
        },
        "M2_plus_directionnel_que_M1P": bool(
            asymetrie["M2"] > asymetrie["M1P"]
        ),
        "ecart_M2_moins_M1P": float(asymetrie["M2"] - asymetrie["M1P"]),
        "lecture": (
            "Les deux sens ajustent exactement les mêmes points. Une asymétrie "
            "de M2 non supérieure à celle de M1P signifie que sa mémoire ne "
            "porte pas d'information de direction que le témoin apparié n'ait "
            "déjà."
        ),
    }
    (OUT / "h_g2_corrige.json").write_text(
        json.dumps(rapport, indent=2, ensure_ascii=False, default=float),
        encoding="utf-8",
    )
    print(json.dumps(rapport, indent=2, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
