"""Prépare les données RÉELLES pour la campagne — aucune donnée simulée.

Trois défauts de la préparation initiale sont corrigés ici.

    1. `prebiotic_lineages_raw.csv` porte le marqueur `GABARIT_SYNTHETIQUE`.
       C'est un gabarit inventé. Il est **retiré**, conformément à la règle de
       la campagne. Le bilan initial annonçait « aucune donnée synthétique » alors
       que ce fichier était présent.

    2. `orbital_timeseries` avait été réduit à 1 381 lignes d'excentricité
       seule, et le bilan indiquait que l'obliquité et la précession « ne sont
       pas imputées ». Elles n'ont pas à l'être : **La2004 les contient**, en
       colonnes 3 et 4, sur 51 001 pas. Ce sont des valeurs publiées, pas des
       imputations.

    3. `ephemerides.csv` avait conservé les noms de colonnes Horizons et ne
       validait donc pas contre son schéma.

Toutes les sources sont des fichiers publiés présents dans le dossier :
Laskar La2004 et La2010, JPL Horizons DE441, pile LR04.

    python preparer_donnees_reelles.py --dossier <racine> --data-dir <cible>
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

# Horizon de fiabilité des solutions La2010, mesuré : la dispersion entre les
# quatre solutions franchit 1 % à 6,9 Ma. Au-delà elles sont décorrélées.
HORIZON_KA = 6900.0


def ecrire(cible: Path, nom: str, colonnes, lignes) -> None:
    chemin = cible / nom
    with chemin.open("w", encoding="utf-8", newline="") as flux:
        redacteur = csv.DictWriter(flux, fieldnames=colonnes)
        redacteur.writeheader()
        redacteur.writerows(lignes)
    print(f"  {nom:34s} {len(lignes):6d} lignes  {list(colonnes)}")


def lire(chemin: Path, sep=";"):
    with chemin.open(encoding="utf-8-sig", newline="") as flux:
        return list(csv.DictReader(flux, delimiter=sep))


def orbital_timeseries(dossier: Path, cible: Path) -> None:
    """La2004 complet : temps, excentricité, obliquité, précession.

    Le fichier publié donne l'obliquité et la longitude du périhélie en
    radians. Rien n'est imputé.
    """
    source = (dossier / "02_branche_systeme_solaire"
              / "couche_memoire_historique" / "data" / "raw"
              / "INSOLN.LA2004.BTL.ASC")
    lignes = []
    with source.open(encoding="utf-8") as flux:
        for brut in flux:
            morceaux = brut.replace("D", "E").split()
            if len(morceaux) == 4:
                lignes.append({
                    "time": morceaux[0], "eccentricity": morceaux[1],
                    "obliquity": morceaux[2], "precession": morceaux[3],
                })
    ecrire(cible, "orbital_timeseries.csv",
           ["time", "eccentricity", "obliquity", "precession"], lignes)


def orbital_reference(dossier: Path, cible: Path) -> None:
    """Quatre solutions La2010, dispersion mesurée, tronquées à l'horizon."""
    base = (dossier / "02_branche_systeme_solaire" / "couche_astronomique"
            / "code" / "ORI-C_Systeme_solaire_tests" / "data" / "reference"
            / "la2010")
    series = {}
    for lettre in "abcd":
        chemin = base / f"La2010{lettre}_ecc3.dat"
        if not chemin.exists():
            continue
        valeurs = {}
        with chemin.open(encoding="utf-8") as flux:
            for brut in flux:
                morceaux = brut.split()
                if len(morceaux) == 2:
                    valeurs[morceaux[0]] = float(morceaux[1])
        series[lettre] = valeurs
    communs = {d for d in set.intersection(*(set(v) for v in series.values()))
               if abs(float(d)) <= HORIZON_KA}
    lignes = []
    for date in sorted(communs, key=float):
        valeurs = [series[l][date] for l in series]
        lignes.append({
            "time": date, "observable": "eccentricity",
            "value": f"{sum(valeurs) / len(valeurs):.9f}",
            "uncertainty": f"{max(valeurs) - min(valeurs):.9f}",
        })
    ecrire(cible, "orbital_reference.csv",
           ["time", "observable", "value", "uncertainty"], lignes)


def ephemerides(dossier: Path, cible: Path) -> None:
    """Horizons DE441 remis au schéma attendu."""
    source = (dossier / "02_branche_systeme_solaire" / "couche_astronomique"
              / "code" / "ORI-C_Systeme_solaire_tests" / "data"
              / "horizons_j2000_de441.csv")
    lignes = [
        {"time": l["epoch_jd_tdb"], "body": l["name"],
         "x": l["x_au"], "y": l["y_au"], "z": l["z_au"],
         "vx": l["vx_au_per_year"], "vy": l["vy_au_per_year"],
         "vz": l["vz_au_per_year"]}
        for l in lire(source, sep=",")
    ]
    ecrire(cible, "ephemerides.csv",
           ["time", "body", "x", "y", "z", "vx", "vy", "vz"], lignes)


def orbital_initial_conditions(dossier: Path, cible: Path) -> None:
    source = (dossier / "02_branche_systeme_solaire" / "couche_astronomique"
              / "code" / "ORI-C_Systeme_solaire_tests" / "data"
              / "horizons_j2000_de441.csv")
    lignes = [
        {"body": l["name"], "epoch": l["epoch_jd_tdb"],
         "x": l["x_au"], "y": l["y_au"], "z": l["z_au"],
         "vx": l["vx_au_per_year"], "vy": l["vy_au_per_year"],
         "vz": l["vz_au_per_year"], "mass": l["mass_msun"]}
        for l in lire(source, sep=",")
    ]
    ecrire(cible, "orbital_initial_conditions.csv",
           ["body", "epoch", "x", "y", "z", "vx", "vy", "vz", "mass"], lignes)


def retirer_le_synthetique(cible: Path) -> list[str]:
    """Tout fichier portant un marqueur de gabarit est retiré."""
    retires = []
    for chemin in cible.glob("*.csv"):
        try:
            debut = chemin.read_text(encoding="utf-8-sig",
                                     errors="ignore")[:4000]
        except OSError:
            continue
        if "GABARIT_SYNTHETIQUE" in debut:
            chemin.unlink()
            retires.append(chemin.name)
            print(f"  {chemin.name:34s} RETIRÉ — marqueur GABARIT_SYNTHETIQUE")
    return retires


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--dossier", type=Path, required=True)
    parseur.add_argument("--data-dir", type=Path, required=True)
    arguments = parseur.parse_args()
    dossier = arguments.dossier.resolve()
    cible = arguments.data_dir.resolve()
    cible.mkdir(parents=True, exist_ok=True)

    print("Données réelles préparées :")
    orbital_timeseries(dossier, cible)
    orbital_reference(dossier, cible)
    ephemerides(dossier, cible)
    orbital_initial_conditions(dossier, cible)
    print("\nRetrait du synthétique :")
    retires = retirer_le_synthetique(cible)
    if not retires:
        print("  aucun fichier synthétique trouvé")

    (cible / "provenance_reelle.json").write_text(json.dumps({
        "regle": "aucune donnée simulée, inventée ou imputée",
        "sources": {
            "orbital_timeseries": "Laskar La2004, INSOLN.LA2004.BTL.ASC, "
                                  "51 001 pas, excentricité obliquité varpi",
            "orbital_reference": "Laskar La2010 a b c d, dispersion mesurée, "
                                 f"tronqué à {HORIZON_KA / 1000} Ma",
            "ephemerides": "JPL Horizons DE441, époque J2000, 15 corps",
            "orbital_initial_conditions": "JPL Horizons DE441 avec masses",
            "paleoclimate_timeseries": "pile benthique LR04",
            "relations": "carte relationnelle du socle",
            "matter_transitions": "base WP-M1 du dossier",
        },
        "fichiers_synthetiques_retires": retires,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
