"""Valide les trois tables canoniques du protocole de données ORI-C.

Une spécification qui n'est pas exécutable n'est pas tenue. Ce script rend le
§8 de `PROTOCOLE_DONNEES.md` vérifiable.

    python valider_donnees.py --repertoire <rep>
    python valider_donnees.py --exemple [--repertoire <rep>]

Le second mode écrit un jeu minimal conforme, utile comme gabarit.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
SEPARATEUR = ";"

# Vocabulaire du CODEBOOK. `CLOS` et `INTG` sont définis mais pas encore
# instanciés dans la carte ; ils sont acceptés ici.
RELATIONS = {
    "ENBL", "MATR", "ENVR", "STAB", "CATL", "CNST",
    "CONT", "DEPG", "INCO", "DESC", "FEED", "CLOS", "INTG",
}
NIVEAUX = {"Établi", "Fortement inféré", "Plausible", "Hypothétique"}

SCHEMAS = {
    "etats.csv": {
        "colonnes": [
            "system_id", "temps", "composition", "configuration",
            "interactions", "environnement", "contrainte", "reponse",
            "seuil", "persistance", "inscription", "histoire", "possibles",
        ],
        # Colonnes qui peuvent légitimement rester vides : une contrainte n'est
        # pas toujours appliquée, un seuil pas toujours franchi.
        "facultatives": {
            "contrainte", "reponse", "seuil", "inscription", "possibles",
        },
        "numeriques": {"temps"},
    },
    "evenements.csv": {
        "colonnes": [
            "system_id", "event_id", "debut", "fin", "type_evenement",
            "intensite", "ordre", "etat_avant", "etat_apres", "reversible",
        ],
        "facultatives": {"fin", "etat_apres"},
        "numeriques": {"debut", "fin", "intensite", "ordre"},
    },
    "relations.csv": {
        "colonnes": [
            "source", "relation", "cible", "date", "niveau_preuve",
            "reference",
        ],
        "facultatives": {"date"},
        "numeriques": set(),
    },
}


def lire(chemin: Path) -> list[dict[str, str]]:
    with chemin.open(encoding="utf-8-sig", newline="") as flux:
        return list(csv.DictReader(flux, delimiter=SEPARATEUR))


def valider_table(chemin: Path, schema: dict) -> list[str]:
    anomalies = []
    lignes = lire(chemin)
    if not lignes:
        return [f"{chemin.name} : aucune ligne"]

    presentes = list(lignes[0].keys())
    manquantes = [c for c in schema["colonnes"] if c not in presentes]
    if manquantes:
        anomalies.append(f"{chemin.name} : colonnes absentes {manquantes}")
    superflues = [c for c in presentes if c not in schema["colonnes"]]
    if superflues:
        anomalies.append(
            f"{chemin.name} : colonnes hors schéma {superflues}"
        )
    if manquantes:
        return anomalies

    obligatoires = [
        c for c in schema["colonnes"] if c not in schema["facultatives"]
    ]
    for index, ligne in enumerate(lignes, start=2):
        for colonne in obligatoires:
            if not (ligne.get(colonne) or "").strip():
                anomalies.append(
                    f"{chemin.name} ligne {index} : `{colonne}` vide alors "
                    "qu'elle est obligatoire"
                )
        for colonne in schema["numeriques"]:
            valeur = (ligne.get(colonne) or "").strip()
            if valeur:
                try:
                    float(valeur)
                except ValueError:
                    anomalies.append(
                        f"{chemin.name} ligne {index} : `{colonne}` = "
                        f"'{valeur}' n'est pas un nombre"
                    )
    return anomalies


def valider_relations(chemin: Path) -> list[str]:
    anomalies = []
    for index, ligne in enumerate(lire(chemin), start=2):
        relation = (ligne.get("relation") or "").strip()
        if relation and relation not in RELATIONS:
            anomalies.append(
                f"relations.csv ligne {index} : code `{relation}` hors "
                f"vocabulaire du CODEBOOK"
            )
        niveau = (ligne.get("niveau_preuve") or "").strip()
        if niveau and niveau not in NIVEAUX:
            anomalies.append(
                f"relations.csv ligne {index} : niveau `{niveau}` hors "
                f"échelle {sorted(NIVEAUX)}"
            )
    return anomalies


def valider_series(chemin: Path) -> list[str]:
    """Le §4 exige des séries, pas des mesures avant-après."""
    anomalies = []
    par_systeme: dict[str, list[float]] = {}
    for ligne in lire(chemin):
        identifiant = (ligne.get("system_id") or "").strip()
        temps = (ligne.get("temps") or "").strip()
        if identifiant and temps:
            try:
                par_systeme.setdefault(identifiant, []).append(float(temps))
            except ValueError:
                continue
    for identifiant, instants in par_systeme.items():
        if len(instants) < 3:
            anomalies.append(
                f"etats.csv : le système `{identifiant}` n'a que "
                f"{len(instants)} instant(s). Le §4 demande une série couvrant "
                "l'approche du seuil, le franchissement et le régime "
                "transitoire, pas une mesure avant-après."
            )
        if sorted(instants) != instants:
            anomalies.append(
                f"etats.csv : les instants du système `{identifiant}` ne sont "
                "pas croissants"
            )
    return anomalies


EXEMPLE = {
    "etats.csv": [
        ["system_id", "temps", "composition", "configuration", "interactions",
         "environnement", "contrainte", "reponse", "seuil", "persistance",
         "inscription", "histoire", "possibles"],
        ["chemostat_libre", "0", "S=10;P=0.1", "reacteur homogene",
         "croissance monod", "D=0.25;S_in=10", "", "", "", "lavage a l>0.859",
         "", "inoculation", "2 regimes"],
        ["chemostat_libre", "10", "S=0.43;P=7.98", "reacteur homogene",
         "croissance monod", "D=0.25;S_in=10", "l=0.25", "P decroit", "",
         "equilibre interieur", "", "perte appliquee", "2 regimes"],
        ["chemostat_libre", "60", "S=0.43;P=7.98", "reacteur homogene",
         "croissance monod", "D=0.25;S_in=10", "l=0.25", "stationnaire",
         "l_crit=0.859", "equilibre interieur", "aucune", "perte maintenue",
         "2 regimes"],
    ],
    "evenements.csv": [
        ["system_id", "event_id", "debut", "fin", "type_evenement",
         "intensite", "ordre", "etat_avant", "etat_apres", "reversible"],
        ["chemostat_libre", "EV-001", "10", "60", "intervention sur la perte",
         "0.25", "1", "P=0.1", "P=7.98", "oui"],
    ],
    "relations.csv": [
        ["source", "relation", "cible", "date", "niveau_preuve", "reference"],
        ["EV-001", "CNST", "chemostat_libre", "", "Établi",
         "analyse exhaustive du test interventionnel, section C3"],
    ],
}


def ecrire_exemple(repertoire: Path) -> None:
    repertoire.mkdir(parents=True, exist_ok=True)
    for nom, lignes in EXEMPLE.items():
        with (repertoire / nom).open("w", encoding="utf-8-sig", newline="") as flux:
            csv.writer(flux, delimiter=SEPARATEUR).writerows(lignes)
    print(f"gabarit écrit dans {repertoire}")


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--repertoire", type=Path,
                         default=RACINE / "schemas_donnees" / "exemple")
    parseur.add_argument("--exemple", action="store_true")
    arguments = parseur.parse_args()
    repertoire = arguments.repertoire.resolve()

    if arguments.exemple:
        ecrire_exemple(repertoire)
        return 0

    absentes = [nom for nom in SCHEMAS if not (repertoire / nom).exists()]
    if absentes:
        print(f"Tables absentes dans {repertoire} : {absentes}")
        print("Produire un gabarit conforme avec --exemple.")
        return 1

    anomalies: list[str] = []
    for nom, schema in SCHEMAS.items():
        anomalies += valider_table(repertoire / nom, schema)
    anomalies += valider_relations(repertoire / "relations.csv")
    anomalies += valider_series(repertoire / "etats.csv")

    for anomalie in anomalies:
        print(f"  {anomalie}")
    if anomalies:
        print(f"\n{len(anomalies)} anomalie(s). Les tables ne sont pas conformes.")
        return 1
    print(f"Les trois tables de {repertoire} sont conformes au protocole.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
