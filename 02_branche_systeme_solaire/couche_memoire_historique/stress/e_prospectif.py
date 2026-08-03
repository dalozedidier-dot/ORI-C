"""Test prospectif à témoin de complexité égale, dans l'EMIC exoplanétaire.

Protocole préenregistré dans `PREENREGISTREMENT_PROSPECTIF.md`, dont
l'empreinte est scellée avant toute exécution.

Le témoin M2P possède exactement les mêmes états dynamiques et les mêmes
paramètres que M2. Seule diffère la variable qui alimente les deux états
lents : la réponse passée du système pour M2, le forçage externe pour M2P.
"""

from __future__ import annotations

import json
import math
import time

import numpy as np
import pandas as pd
from numba import njit

from core import (
    EXO_PARAMETER_ORDER,
    OUTPUT_ROOT,
    exo_parameter_vector,
    paired_wilcoxon_greater,
    polar_summer_insolation,
)
from b2_regime import histories_to
from oric_memory_tests.exoplanet import (
    MATERIALITY_THRESHOLDS,
    STATE_NAMES,
    TEST_VARIABLES,
)

OUT = OUTPUT_ROOT / "prospectif"
VARIABLE_INDEX = {name: index for index, name in enumerate(STATE_NAMES)}

# 0 classic, 1 ablated, 2 M2, 3 M2P
MODES = {"classic": 0, "ablated": 1, "M2": 2, "M2P": 3}
POINTS_BISTABLES = [(30.0, 0.10), (23.5, 0.18), (12.0, 0.30), (40.0, 0.00)]


@njit(cache=True, fastmath=False)
def _coeur(polar_anomaly, flux_anomaly, mode, initial_state, p, step, substeps):
    """Identique à l'EMIC de référence, augmenté du mode 3 (M2P).

    M2P : les deux états lents évoluent avec les mêmes constantes de temps et
    les mêmes gains que M2, mais leurs cibles sont construites sur le forçage
    externe au lieu de la réponse du système. `entree` est normalisée pour
    occuper la plage de la productivité, afin qu'aucune différence d'échelle ne
    se substitue à la différence de nature.
    """
    n = polar_anomaly.shape[0]
    internal = step / substeps
    temperature = initial_state[0]
    ice = initial_state[1]
    co2 = initial_state[2]
    regolith = initial_state[3]
    memoire = initial_state[4]

    sortie = np.empty((n, 6))
    productivity = 0.0

    for index in range(n):
        for _ in range(substeps):
            co2_clamped = co2 if co2 > 50.0 else 50.0
            productivity = (
                math.exp(-((temperature - 0.5) / 4.0) ** 2)
                * (co2_clamped / 280.0) ** 0.2
                * (1.0 - 0.45 * ice)
            )
            # Entrée externe bornée dans [0, 1], de même plage que productivity.
            entree = 1.0 / (1.0 + math.exp(-polar_anomaly[index]))

            if mode == 2 or mode == 3:
                bedrock = 1.0 - regolith
                effet = memoire - 0.5
            elif mode == 1:
                bedrock = 0.5
                effet = 0.0
                regolith = 0.5
                memoire = 0.5
            else:
                bedrock = 0.0
                effet = 0.0

            cible_t = (
                p[3] * flux_anomaly[index]
                + p[4] * math.log(co2_clamped / 280.0)
                - p[5] * ice
            )
            argument = -(
                temperature + p[6] * polar_anomaly[index] - p[7] - p[9] * bedrock
            ) / p[8]
            if argument > 30.0:
                argument = 30.0
            elif argument < -30.0:
                argument = -30.0
            cible_glace = 1.0 / (1.0 + math.exp(-argument))
            cible_co2 = 280.0 * math.exp(-p[15] * temperature - p[13] * effet)
            tau_glace = p[1] * (1.0 + p[10] * bedrock)

            temperature += internal * (cible_t - temperature) / p[0]
            ice = ice + internal * (cible_glace - ice) / tau_glace
            if ice < 0.0:
                ice = 0.0
            elif ice > 1.0:
                ice = 1.0
            co2 = co2 + internal * (cible_co2 - co2) / p[2]
            if co2 < 80.0:
                co2 = 80.0
            elif co2 > 1200.0:
                co2 = 1200.0

            if mode == 2:
                # Les états lents suivent la RÉPONSE du système.
                regolith += internal * (
                    -p[11] * ice * regolith + (1.0 - regolith) / p[12]
                )
                memoire += internal * (productivity - memoire) / p[14]
            elif mode == 3:
                # Les états lents suivent le FORÇAGE externe. Même structure,
                # mêmes constantes de temps, mêmes gains.
                regolith += internal * (
                    -p[11] * entree * regolith + (1.0 - regolith) / p[12]
                )
                memoire += internal * (entree - memoire) / p[14]

            if mode == 2 or mode == 3:
                if regolith < 0.0:
                    regolith = 0.0
                elif regolith > 1.0:
                    regolith = 1.0
                if memoire < 0.0:
                    memoire = 0.0
                elif memoire > 2.0:
                    memoire = 2.0

        sortie[index, 0] = temperature
        sortie[index, 1] = ice
        sortie[index, 2] = co2
        sortie[index, 3] = regolith
        sortie[index, 4] = memoire
        sortie[index, 5] = productivity
    return sortie


def simuler(temps, obliquite, excentricite, mode, etat_initial, parametres):
    temps = np.asarray(temps, dtype=float)
    step = float(np.median(np.diff(temps)))
    substeps = max(1, int(np.ceil(step / 0.02)))
    polar = polar_summer_insolation(obliquite, excentricite)
    reference = float(polar_summer_insolation(23.5, 0.05))
    polar_anomaly = np.ascontiguousarray((polar - reference) / 100.0)
    flux = np.ascontiguousarray(
        (1.0 / np.sqrt(1.0 - np.asarray(excentricite, dtype=float) ** 2)
         - 1.0 / np.sqrt(1.0 - 0.05 ** 2)) / 0.05
    )
    return _coeur(
        polar_anomaly, flux, MODES[mode],
        np.ascontiguousarray(etat_initial, dtype=float),
        np.ascontiguousarray(parametres, dtype=float), step, substeps,
    )


def frontiere_de_bassin(obliquite, excentricite, parametres, mode="classic",
                        duree=400.0, tolerance=1e-4):
    """Fraction de glace initiale qui sépare les deux bassins.

    Déterminée par bissection avec le mode `classic`, afin que la frontière ne
    soit pas définie par le modèle testé.
    """
    step = 0.02
    temps = np.arange(0.0, duree + step / 2.0, step)
    obl = np.full_like(temps, obliquite)
    exc = np.full_like(temps, excentricite)

    def glace_finale(glace0):
        etat = np.array([0.0, glace0, 300.0, 0.8, 0.4])
        return float(simuler(temps, obl, exc, mode, etat, parametres)[-1, 1])

    bas, haut = 0.0, 1.0
    if abs(glace_finale(bas) - glace_finale(haut)) < 0.05:
        return None  # pas de bistabilité détectée sur cet axe
    while haut - bas > tolerance:
        milieu = 0.5 * (bas + haut)
        if abs(glace_finale(milieu) - glace_finale(bas)) < 0.05:
            bas = milieu
        else:
            haut = milieu
    return 0.5 * (bas + haut)


def ecarts_finaux(obliquite, excentricite, parametres, etats, palier,
                  glace_A, glace_B, step=0.02):
    """|A − B| par réplicat et par mode, A et B encadrant la frontière."""
    (temps, obl_a, exc_a, obl_b, exc_b) = histories_to(
        obliquite, excentricite, step_myr=step, final_hold_myr=float(palier)
    )
    masque = temps >= 50.0 + palier - 2.0
    resultat = {}
    for mode in MODES:
        deltas = np.empty((len(etats), len(STATE_NAMES)))
        for index, etat in enumerate(etats):
            a = etat.copy(); a[1] = glace_A
            b = etat.copy(); b[1] = glace_B
            fin_a = simuler(temps, obl_a, exc_a, mode, a, parametres)[masque].mean(axis=0)
            fin_b = simuler(temps, obl_b, exc_b, mode, b, parametres)[masque].mean(axis=0)
            deltas[index] = np.abs(fin_a - fin_b)
        resultat[mode] = deltas
    return resultat


def etats_initiaux(graine, nombre):
    random = np.random.default_rng(graine)
    etats = np.empty((nombre, 5))
    for index in range(nombre):
        etats[index] = (
            random.normal(0.0, 0.2), 0.5, random.normal(300.0, 15.0),
            random.uniform(0.6, 1.0), random.uniform(0.1, 0.6),
        )
    return etats


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    parametres = exo_parameter_vector()
    etats = etats_initiaux(729, 60)
    lignes = []
    frontieres = {}

    for obliquite, excentricite in POINTS_BISTABLES:
        cle = f"{obliquite:g}_{excentricite:g}"
        depart = time.perf_counter()
        frontiere = frontiere_de_bassin(obliquite, excentricite, parametres)
        frontieres[cle] = frontiere
        if frontiere is None:
            print(f"  ({obliquite}, {excentricite}) : aucune frontière détectée",
                  flush=True)
            continue

        # A et B encadrent la frontière, à 2 % de part et d'autre.
        glace_A = max(0.0, frontiere - 0.02)
        glace_B = min(1.0, frontiere + 0.02)

        for palier in (10, 300):
            deltas = ecarts_finaux(obliquite, excentricite, parametres, etats,
                                   palier, glace_A, glace_B)
            for mode in MODES:
                for variable in TEST_VARIABLES:
                    position = VARIABLE_INDEX[variable]
                    valeurs = deltas[mode][:, position]
                    seuil = MATERIALITY_THRESHOLDS[variable]
                    lignes.append({
                        "obliquite_finale": obliquite,
                        "excentricite_finale": excentricite,
                        "frontiere_glace": frontiere,
                        "palier_myr": palier,
                        "mode": mode,
                        "variable": variable,
                        "delta_median": float(np.median(valeurs)),
                        "seuil": seuil,
                        "materiel": bool(np.median(valeurs) >= seuil),
                    })
        print(f"  ({obliquite}, {excentricite}) : frontière glace "
              f"{frontiere:.4f}, {time.perf_counter() - depart:.0f} s", flush=True)

    frame = pd.DataFrame(lignes)
    frame.to_csv(OUT / "e_prospectif.csv", index=False)

    # --- Verdicts préenregistrés -----------------------------------------
    long = frame.loc[frame["palier_myr"] == 300]

    def materielles(mode):
        subset = long.loc[long["mode"] == mode]
        return {
            f"{r.obliquite_finale:g}_{r.excentricite_finale:g}":
                int(subset.loc[
                    (subset["obliquite_finale"] == r.obliquite_finale)
                    & (subset["excentricite_finale"] == r.excentricite_finale),
                    "materiel"].sum())
            for r in subset.drop_duplicates(
                ["obliquite_finale", "excentricite_finale"]).itertuples()
        }

    par_mode = {mode: materielles(mode) for mode in MODES}

    h1 = any(n >= 2 for n in par_mode["classic"].values())
    h2_points = [
        point for point in par_mode["M2"]
        if par_mode["M2"][point] >= 2 and par_mode["M2P"].get(point, 0) == 0
    ]
    h2 = bool(h2_points)

    resume = {
        "preenregistrement": "stress/PREENREGISTREMENT_PROSPECTIF.md",
        "frontieres_de_bassin": frontieres,
        "variables_materielles_a_300Ma": par_mode,
        "H1_bistabilite_suffit": h1,
        "H2_memoire_ajoute_quelque_chose": h2,
        "H2_points_favorables": h2_points,
        "lecture": (
            "H1 vraie signifie que la dépendance au chemin permanente vient de "
            "la bistabilité et non de la mémoire. H2 est la revendication "
            "propre à ORI-C."
        ),
    }
    (OUT / "e_prospectif.json").write_text(
        json.dumps(resume, indent=2, ensure_ascii=False, default=float),
        encoding="utf-8",
    )
    print(json.dumps(resume, indent=2, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
