"""Convertit les données RÉELLES du dossier ORI-C aux schémas de la plateforme.

L'adaptateur `import-existing` copie quatre fichiers ; trois ne passent pas la
validation parce que leurs colonnes ne portent pas les noms attendus. Ce script
fait la correspondance explicite, pour les seules données réelles.

    Règle absolue : rien de synthétique n'entre. Le gabarit de lignées
    prébiotiques du dossier porte le marqueur `GABARIT_SYNTHETIQUE` ; il est
    **retiré**, pas converti.

    python mapper_donnees_reelles.py
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

# Correctif 4. Aucun chemin absolu : le dossier source et le répertoire de
# données sont des arguments. Le script est déplaçable et réutilisable.
DOSSIER = Path()
DONNEES = Path()


def ecrire(nom: str, colonnes: list[str], lignes: list[dict]) -> None:
    chemin = DONNEES / nom
    with chemin.open("w", encoding="utf-8", newline="") as flux:
        redacteur = csv.DictWriter(flux, fieldnames=colonnes)
        redacteur.writeheader()
        redacteur.writerows(lignes)
    print(f"  {nom:32s} {len(lignes):5d} lignes")


def lire(chemin: Path, sep=";") -> list[dict]:
    with chemin.open(encoding="utf-8-sig", newline="") as flux:
        return list(csv.DictReader(flux, delimiter=sep))


def relations() -> None:
    """`source ; relation ; target` → `source, target, relation_type`."""
    source = (DOSSIER / "00_socle" / "carte_relationnelle" / "data"
              / "relations_oric_47_provisoires.csv")
    lignes = [
        {"source": l["source"], "target": l["target"],
         "relation_type": l["relation"]}
        for l in lire(source)
    ]
    ecrire("relations.csv", ["source", "target", "relation_type"], lignes)


# La plateforme lit `evidence_level` comme un NOMBRE (`pd.to_numeric`). Le
# dossier emploie une échelle textuelle. La correspondance ci-dessous est une
# décision déclarée, pas une donnée : elle ordonne les 22 formulations du
# dossier sur l'échelle à quatre niveaux du CODEBOOK.
#
#   4  observé directement          3  reconstruit ou produit en laboratoire
#   2  inféré d'archives ou modèles 1  plausible sans support direct
ECHELLE = (
    (("observé", "observee", "observe", "existence observée",
      "asymétrie observée", "objet observé", "architecture observée"), 4),
    (("produit expérimentalement", "produit partiellement", "reconstruit"), 3),
    (("inféré", "infere", "modélisé"), 2),
    (("plausible",), 1),
)


def niveau_numerique(texte: str) -> str:
    """Renvoie le niveau numérique le plus élevé compatible avec le texte."""
    minuscule = (texte or "").lower()
    for motifs, valeur in ECHELLE:
        if any(motif in minuscule for motif in motifs):
            return str(valeur)
    return ""


def matter_transitions() -> None:
    """Base WP-M1 du dossier. Les six dimensions sont vides : elles le restent.

    Le schéma les exige comme colonnes, pas comme valeurs renseignées. Les
    laisser vides est la seule écriture honnête : aucune source du dossier ne
    les renseigne, et les inventer contaminerait la campagne.
    """
    source = (DOSSIER / "01_branche_matiere" / "base_transitions"
              / "transitions_matiere.csv")
    if not source.exists():
        print("  matter_transitions : base absente, ignorée")
        return
    colonnes = ["transition_id", "before_state", "after_state",
                "n", "G", "I", "E", "Pi", "H", "evidence_level",
                "evidence_level_texte"]
    lignes = [
        {
            "transition_id": l["id"],
            "before_state": l["etat_anterieur"],
            "after_state": l["etat_posterieur"],
            "n": l["dimension_n"], "G": l["dimension_G"],
            "I": l["dimension_I"], "E": l["dimension_E"],
            "Pi": l["dimension_Pi"], "H": l["dimension_H"],
            "evidence_level": niveau_numerique(l["niveau_de_preuve"]),
            "evidence_level_texte": l["niveau_de_preuve"],
        }
        for l in lire(source)
    ]
    ecrire("matter_transitions.csv", colonnes, lignes)


def states() -> None:
    """Table d'états du protocole ORI-C → `system_id, time, state_json`."""
    source = (DOSSIER / "00_socle" / "schemas_donnees" / "exemple"
              / "etats.csv")
    lignes = []
    for l in lire(source):
        etat = {k: v for k, v in l.items()
                if k not in ("system_id", "temps") and (v or "").strip()}
        lignes.append({
            "system_id": l["system_id"],
            "time": l["temps"],
            "state_json": json.dumps(etat, ensure_ascii=False),
        })
    ecrire("states.csv", ["system_id", "time", "state_json"], lignes)


def ephemerides() -> None:
    """Conditions initiales Horizons → schéma `time, body, x, y, z, vx…`.

    Ce sont des états à une seule époque, pas une série temporelle. La colonne
    `time` reçoit l'époque julienne du fichier source ; le jeu reste donc un
    instantané, ce qui limite ce que la couche astronomique pourra en faire.
    """
    source = (DOSSIER / "02_branche_systeme_solaire" / "couche_astronomique"
              / "code" / "ORI-C_Systeme_solaire_tests" / "data"
              / "horizons_j2000_de441.csv")
    if not source.exists():
        print("  ephemerides : source absente, ignorée")
        return
    colonnes = ["time", "body", "x", "y", "z", "vx", "vy", "vz"]
    lignes = [
        {
            "time": l.get("epoch_jd_tdb", ""),
            "body": l["name"],
            "x": l["x_au"], "y": l["y_au"], "z": l["z_au"],
            "vx": l["vx_au_per_year"], "vy": l["vy_au_per_year"],
            "vz": l["vz_au_per_year"],
        }
        for l in lire(source, sep=",")
    ]
    ecrire("ephemerides.csv", colonnes, lignes)


def orbital_timeseries() -> None:
    """Solution La2004 de Laskar — 51 001 pas de 1 ka sur 51 Ma.

    Colonnes du fichier : temps en ka depuis J2000, excentricité, obliquité en
    radians, longitude du périhélie en radians. Le schéma attend
    `precession` : on y met `varpi`, qui est la grandeur dont dérive
    l'indice de précession climatique.
    """
    source = (DOSSIER / "02_branche_systeme_solaire"
              / "couche_memoire_historique" / "data" / "raw"
              / "INSOLN.LA2004.BTL.ASC")
    if not source.exists():
        print("  orbital_timeseries : La2004 absent, ignoré")
        return
    lignes = []
    with source.open(encoding="utf-8") as flux:
        for brut in flux:
            morceaux = brut.replace("D", "E").split()
            if len(morceaux) != 4:
                continue
            lignes.append({
                "time": morceaux[0], "eccentricity": morceaux[1],
                "obliquity": morceaux[2], "precession": morceaux[3],
            })
    ecrire("orbital_timeseries.csv",
           ["time", "eccentricity", "obliquity", "precession"], lignes)


def orbital_reference() -> None:
    """Quatre solutions La2010, avec leur dispersion comme incertitude.

    L'incertitude n'est pas déclarée par les auteurs : elle est **mesurée**
    ici comme l'étendue entre les quatre solutions également admissibles, à
    chaque date. C'est le plancher que le test T3 du dossier avait chiffré à
    5,2 × 10⁻⁴ en relatif.
    """
    base = (DOSSIER / "02_branche_systeme_solaire" / "couche_astronomique"
            / "code" / "ORI-C_Systeme_solaire_tests" / "data" / "reference"
            / "la2010")
    if not base.is_dir():
        print("  orbital_reference : La2010 absent, ignoré")
        return
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
    if len(series) < 2:
        print("  orbital_reference : moins de deux solutions, ignoré")
        return
    # Horizon de fiabilité, WP-A2.10. La dispersion entre les quatre
    # solutions vaut 2,0e-4 sur 0-2,6 Ma, franchit 1 % à 6,9 Ma et 50 % à
    # 23,9 Ma : au-delà, les solutions sont chaotiquement décorrélées et une
    # comparaison n'a plus de sens. La table est tronquée à l'horizon du 1 %,
    # valeur déclarée ici et mesurée par .
    HORIZON_KA = 6900.0
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
    ecrire("orbital_reference.csv",
           ["time", "observable", "value", "uncertainty"], lignes)


def orbital_initial_conditions() -> None:
    """Conditions initiales Horizons DE441, avec les masses."""
    source = (DOSSIER / "02_branche_systeme_solaire" / "couche_astronomique"
              / "code" / "ORI-C_Systeme_solaire_tests" / "data"
              / "horizons_j2000_de441.csv")
    if not source.exists():
        print("  orbital_initial_conditions : source absente, ignorée")
        return
    lignes = [
        {
            "body": l["name"], "epoch": l["epoch_jd_tdb"],
            "x": l["x_au"], "y": l["y_au"], "z": l["z_au"],
            "vx": l["vx_au_per_year"], "vy": l["vy_au_per_year"],
            "vz": l["vz_au_per_year"], "mass": l["mass_msun"],
        }
        for l in lire(source, sep=",")
    ]
    ecrire("orbital_initial_conditions.csv",
           ["body", "epoch", "x", "y", "z", "vx", "vy", "vz", "mass"], lignes)


def retirer_le_synthetique() -> None:
    """Le gabarit de lignées prébiotiques est synthétique : il ne doit pas
    entrer dans une campagne scientifique."""
    for nom in ("prebiotic_lineages_raw.csv",):
        chemin = DONNEES / nom
        if chemin.exists():
            chemin.unlink()
            print(f"  {nom:32s} RETIRÉ — marqueur GABARIT_SYNTHETIQUE")


def main() -> int:
    global DOSSIER, DONNEES
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--dossier", type=Path, required=True,
                         help="racine de ORI-C_dossier_unique")
    parseur.add_argument("--data-dir", type=Path, required=True,
                         help="répertoire de données de l'espace de travail")
    arguments = parseur.parse_args()
    DOSSIER = arguments.dossier.resolve()
    DONNEES = arguments.data_dir.resolve()
    DONNEES.mkdir(parents=True, exist_ok=True)

    print(f"source : {DOSSIER}")
    print(f"cible  : {DONNEES}")
    print("Conversion des données réelles :")
    relations()
    matter_transitions()
    states()
    ephemerides()
    orbital_timeseries()
    orbital_reference()
    orbital_initial_conditions()
    print("\nRetrait du synthétique :")
    retirer_le_synthetique()
    return 0


if __name__ == "__main__":
    sys.exit(main())
