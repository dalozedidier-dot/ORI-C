"""Intégration du Système solaire réel, confrontée à La2004 — WP-A1 et A5.

Test sur données réelles de bout en bout, sans aucune donnée synthétique.

    Entrée   conditions initiales JPL Horizons DE441, 15 corps, époque J2000
    Calcul   saute-mouton symplectique d'ordre 2 en coordonnées
             cartésiennes, pas fixe. Ce n'est pas un Wisdom-Holman : la
             dérive d'énergie y est dominée par Mercure, dont la période de
             88 jours impose un pas court.
    Sortie   excentricité de la Terre, son spectre, et l'écart à La2004

La question est falsifiable et sévère : **une intégration partant des positions
mesurées des planètes reproduit-elle la période de 405 ka que Laskar obtient
avec un code de référence ?** Si oui, la chaîne données-code-analyse est
validée de bout en bout. Si non, l'écart localise le défaut.

Aucun résultat n'est simulé ni recopié. Les critères sont fixés avant
exécution, dans `CRITERES` ci-dessous.

    python integrer_systeme_solaire.py --duree-ka 2000 --pas-jours 8
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np

# Constante de Gauss au carré, en unités astronomiques, masses solaires et
# jours. Valeur IAU, extérieure à ce dossier.
GM_SOLAIRE = (0.01720209895) ** 2
JOURS_PAR_AN = 365.25

# Critères fixés avant exécution.
CRITERES = {
    "conservation_energie_relative_max": 1e-8,
    "periode_dominante_excentricite_ka": (395.0, 415.0),
    "correlation_minimale_avec_La2004": 0.5,
}


def charger_conditions(chemin: Path):
    """Positions et vitesses Horizons, converties en unités jour."""
    with chemin.open(encoding="utf-8-sig", newline="") as flux:
        lignes = list(csv.DictReader(flux))
    noms = [l["name"] for l in lignes]
    masses = np.array([float(l["mass_msun"]) for l in lignes])
    positions = np.array([[float(l["x_au"]), float(l["y_au"]),
                           float(l["z_au"])] for l in lignes])
    # Horizons fournit des vitesses en ua/an ; le pas est en jours.
    vitesses = np.array([[float(l["vx_au_per_year"]),
                          float(l["vy_au_per_year"]),
                          float(l["vz_au_per_year"])]
                         for l in lignes]) / JOURS_PAR_AN
    return noms, masses, positions, vitesses


def recentrer(masses, positions, vitesses):
    """Repère du barycentre : sans cela le système dérive."""
    total = masses.sum()
    positions = positions - (masses[:, None] * positions).sum(0) / total
    vitesses = vitesses - (masses[:, None] * vitesses).sum(0) / total
    return positions, vitesses


def accelerations(masses, positions, adoucissement=1e-10):
    ecarts = positions[None, :, :] - positions[:, None, :]
    distances = np.sqrt((ecarts ** 2).sum(-1) + adoucissement)
    np.fill_diagonal(distances, np.inf)
    return GM_SOLAIRE * (
        masses[None, :, None] * ecarts / distances[:, :, None] ** 3
    ).sum(1)


def energie(masses, positions, vitesses):
    cinetique = 0.5 * (masses * (vitesses ** 2).sum(-1)).sum()
    ecarts = positions[None, :, :] - positions[:, None, :]
    distances = np.sqrt((ecarts ** 2).sum(-1))
    np.fill_diagonal(distances, np.inf)
    potentielle = -0.5 * GM_SOLAIRE * (
        masses[:, None] * masses[None, :] / distances
    ).sum()
    return float(cinetique + potentielle)


def excentricite(masse_centrale, position, vitesse):
    """Excentricité osculatrice par rapport au corps central."""
    mu = GM_SOLAIRE * masse_centrale
    r = np.linalg.norm(position)
    v2 = float(vitesse @ vitesse)
    vecteur = ((v2 - mu / r) * position - float(position @ vitesse) * vitesse) / mu
    return float(np.linalg.norm(vecteur))


def integrer(masses, positions, vitesses, pas_jours, duree_jours,
             indice_terre, indice_soleil, echantillon_jours):
    """Saute-mouton, symplectique d'ordre 2. Renvoie la série d'excentricité."""
    positions = positions.copy()
    vitesses = vitesses.copy()
    energie_initiale = energie(masses, positions, vitesses)

    pas_total = int(duree_jours / pas_jours)
    intervalle = max(1, int(echantillon_jours / pas_jours))
    temps, excentricites = [], []
    derive_max = 0.0

    a = accelerations(masses, positions)
    for etape in range(pas_total):
        vitesses += 0.5 * pas_jours * a
        positions += pas_jours * vitesses
        a = accelerations(masses, positions)
        vitesses += 0.5 * pas_jours * a

        if etape % intervalle == 0:
            relative = positions[indice_terre] - positions[indice_soleil]
            vitesse_relative = vitesses[indice_terre] - vitesses[indice_soleil]
            temps.append(etape * pas_jours / JOURS_PAR_AN / 1000.0)  # ka
            excentricites.append(
                excentricite(masses[indice_soleil] + masses[indice_terre],
                             relative, vitesse_relative)
            )
        if etape % (pas_total // 20 or 1) == 0:
            courante = energie(masses, positions, vitesses)
            derive = abs((courante - energie_initiale) / energie_initiale)
            derive_max = max(derive_max, derive)
            print(f"   {100 * etape / pas_total:5.1f} %  "
                  f"dérive d'énergie {derive:.3e}", flush=True)

    return (np.array(temps), np.array(excentricites), derive_max,
            energie_initiale)


def periode_dominante(temps_ka, serie):
    """Période du pic principal, en ka, hors composante continue."""
    pas = float(np.median(np.diff(temps_ka)))
    centre = serie - serie.mean()
    spectre = np.abs(np.fft.rfft(centre)) ** 2
    frequences = np.fft.rfftfreq(len(centre), d=pas)
    valides = frequences > 1.0 / (0.8 * (temps_ka[-1] - temps_ka[0]))
    if not valides.any():
        return float("nan"), float("nan")
    indice = int(np.argmax(spectre[valides]))
    return float(1.0 / frequences[valides][indice]), float(spectre[valides][indice])


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    racine = Path(__file__).resolve().parents[3]
    parseur.add_argument("--conditions", type=Path, default=(
        racine / "02_branche_systeme_solaire" / "couche_astronomique" / "code"
        / "ORI-C_Systeme_solaire_tests" / "data" / "horizons_j2000_de441.csv"))
    parseur.add_argument("--la2004", type=Path, default=(
        racine / "02_branche_systeme_solaire" / "couche_memoire_historique"
        / "data" / "raw" / "INSOLN.LA2004.BTL.ASC"))
    parseur.add_argument("--duree-ka", type=float, default=2000.0)
    parseur.add_argument("--pas-jours", type=float, default=8.0)
    parseur.add_argument("--echantillon-ans", type=float, default=500.0)
    parseur.add_argument("--sortie", type=Path,
                         default=Path(__file__).resolve().parent)
    arguments = parseur.parse_args()
    arguments.sortie.mkdir(parents=True, exist_ok=True)

    noms, masses, positions, vitesses = charger_conditions(arguments.conditions)
    positions, vitesses = recentrer(masses, positions, vitesses)
    indice_soleil = noms.index("Sun")
    indice_terre = next(i for i, n in enumerate(noms)
                        if n.lower().startswith("earth"))
    print(f"{len(noms)} corps : {', '.join(noms)}")
    print(f"Soleil à l'indice {indice_soleil}, Terre à l'indice {indice_terre}")
    print(f"Durée {arguments.duree_ka} ka, pas {arguments.pas_jours} jours",
          flush=True)

    depart = time.perf_counter()
    temps, ecc, derive, energie_initiale = integrer(
        masses, positions, vitesses, arguments.pas_jours,
        arguments.duree_ka * 1000.0 * JOURS_PAR_AN,
        indice_terre, indice_soleil,
        arguments.echantillon_ans * JOURS_PAR_AN,
    )
    duree_calcul = time.perf_counter() - depart

    periode, puissance = periode_dominante(temps, ecc)

    # Comparaison à La2004 sur la même fenêtre.
    reference = []
    with arguments.la2004.open(encoding="utf-8") as flux:
        for brut in flux:
            morceaux = brut.replace("D", "E").split()
            if len(morceaux) == 4:
                reference.append((abs(float(morceaux[0])), float(morceaux[1])))
    reference = np.array(sorted(reference))
    dans_fenetre = reference[:, 0] <= arguments.duree_ka
    ref_temps, ref_ecc = reference[dans_fenetre, 0], reference[dans_fenetre, 1]
    interpolee = np.interp(ref_temps, temps, ecc)
    correlation = float(np.corrcoef(interpolee, ref_ecc)[0, 1])
    ecart = float(np.sqrt(np.mean((interpolee - ref_ecc) ** 2)))
    periode_ref, _ = periode_dominante(ref_temps, ref_ecc)

    bas, haut = CRITERES["periode_dominante_excentricite_ka"]
    rapport = {
        "corps": noms,
        "duree_ka": arguments.duree_ka,
        "pas_jours": arguments.pas_jours,
        "points_echantillonnes": int(len(temps)),
        "duree_de_calcul_s": duree_calcul,
        "criteres_fixes_avant_execution": CRITERES,
        "conservation": {
            "derive_energie_relative_max": derive,
            "critere": CRITERES["conservation_energie_relative_max"],
            "reussi": bool(derive < CRITERES["conservation_energie_relative_max"]),
        },
        "excentricite_terrestre": {
            "moyenne": float(ecc.mean()), "min": float(ecc.min()),
            "max": float(ecc.max()),
            "periode_dominante_ka": periode,
            "critere": [bas, haut],
            "reussi": bool(bas <= periode <= haut),
        },
        "comparaison_La2004": {
            "periode_dominante_de_La2004_ka": periode_ref,
            "correlation": correlation,
            "critere": CRITERES["correlation_minimale_avec_La2004"],
            "reussi": bool(correlation >= CRITERES["correlation_minimale_avec_La2004"]),
            "rmse": ecart,
            "points_compares": int(dans_fenetre.sum()),
        },
    }
    (arguments.sortie / "integration_reelle.json").write_text(
        json.dumps(rapport, indent=2, ensure_ascii=False), encoding="utf-8")
    np.savetxt(arguments.sortie / "excentricite_terre.csv",
               np.column_stack([temps, ecc]), delimiter=",",
               header="temps_ka,excentricite", comments="")

    print(f"\ncalcul en {duree_calcul:.0f} s")
    print(f"dérive d'énergie max      {derive:.3e}  "
          f"(critère < {CRITERES['conservation_energie_relative_max']:.0e})")
    print(f"excentricité terrestre    moyenne {ecc.mean():.5f}, "
          f"étendue {ecc.min():.5f} à {ecc.max():.5f}")
    print(f"période dominante         {periode:.2f} ka  "
          f"(critère {bas}-{haut})")
    print(f"La2004 sur la même fenêtre {periode_ref:.2f} ka")
    print(f"corrélation avec La2004   {correlation:+.4f}  "
          f"(critère >= {CRITERES['correlation_minimale_avec_La2004']})")
    print(f"RMSE                      {ecart:.5f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
