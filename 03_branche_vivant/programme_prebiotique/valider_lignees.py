"""Valide une table de lignées de protocellules et évalue le critère minimal.

Le programme prébiotique repose sur une ligne de partage :

    sans données de lignées, on observe une production chimique,
    pas une hérédité.

Ce script rend cette phrase vérifiable. Il fait deux choses distinctes.

    python valider_lignees.py --repertoire <rep>
        Vérifie la table : schéma, vocabulaires, cohérence des filiations,
        présence des témoins. Une table qui échoue n'est pas une table de
        lignées.

    python valider_lignees.py --repertoire <rep> --critere
        Évalue les six conditions du critère minimal de réussite et calcule
        la variable principale du programme.

    python valider_lignees.py --gabarit [--repertoire <rep>]
        Écrit un jeu minimal conforme, **synthétique**, utile comme modèle.

Le script ne collecte rien et ne conclut rien de lui-même. Il applique à une
table fournie les règles écrites dans `PROGRAMME_PREBIOTIQUE.md`.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

RACINE = Path(__file__).resolve().parent
SEPARATEUR = ";"
FICHIER = "lignees.csv"

# Marqueur écrit dans les tables produites par --gabarit. Une table qui le
# porte est synthétique et ne doit jamais être lue comme une mesure.
MARQUEUR_GABARIT = "GABARIT_SYNTHETIQUE"

COLONNES = [
    "experience_id", "trajectoire", "temoin", "compartiment_id", "cycle",
    "parent_id", "matrice_id", "variante", "longueur_polymere",
    "copies_produites", "fidelite", "volume", "division", "transmis",
    "fonction_mesuree", "reinitialisation",
]
FACULTATIVES = {"parent_id", "matrice_id", "fidelite", "fonction_mesuree"}
NUMERIQUES = {
    "cycle", "longueur_polymere", "copies_produites", "fidelite", "volume",
    "fonction_mesuree",
}

TRAJECTOIRES = {
    "humide_sec", "gel_degel", "hydrothermal", "surface_minerale",
    "alternance",
}

# Les sept témoins du §4.3, plus le témoin de complexité égale du §5.
TEMOINS = {
    "complet",
    "sans_compartiment",
    "sans_matrice",
    "sans_copie",
    "sans_energie",
    "sans_variation",
    "chemin_alternatif",
    "complexite_egale",
}
TEMOIN_APPARIE = "complexite_egale"
BOOLEENS = {"oui", "non"}

VARIANTE_REFERENCE = "reference"
CYCLES_MINIMUM = 3


# --------------------------------------------------------------------------
# Lecture

def lire(chemin: Path) -> list[dict[str, str]]:
    with chemin.open(encoding="utf-8-sig", newline="") as flux:
        return [
            ligne for ligne in csv.DictReader(flux, delimiter=SEPARATEUR)
            if any((valeur or "").strip() for valeur in ligne.values())
        ]


def nombre(ligne: dict, colonne: str):
    valeur = (ligne.get(colonne) or "").strip()
    if not valeur:
        return None
    try:
        return float(valeur)
    except ValueError:
        return None


# --------------------------------------------------------------------------
# Vérification du schéma

def valider_schema(lignes: list[dict]) -> tuple[list[str], bool]:
    """Renvoie (anomalies, colonnes_exploitables).

    Seule l'absence de colonnes empêche les contrôles suivants. Une valeur
    invalide ne les empêche pas : un seul passage doit rapporter tous les
    défauts, sans quoi la correction devient une suite d'allers-retours.
    """
    anomalies = []
    if not lignes:
        return [f"{FICHIER} : aucune ligne"], False

    presentes = list(lignes[0].keys())
    manquantes = [c for c in COLONNES if c not in presentes]
    if manquantes:
        return [f"{FICHIER} : colonnes absentes {manquantes}"], False
    superflues = [c for c in presentes if c not in COLONNES]
    if superflues:
        anomalies.append(f"{FICHIER} : colonnes hors schéma {superflues}")

    obligatoires = [c for c in COLONNES if c not in FACULTATIVES]
    for index, ligne in enumerate(lignes, start=2):
        for colonne in obligatoires:
            if not (ligne.get(colonne) or "").strip():
                anomalies.append(
                    f"ligne {index} : `{colonne}` vide alors qu'elle est "
                    "obligatoire"
                )
        for colonne in NUMERIQUES:
            valeur = (ligne.get(colonne) or "").strip()
            if valeur and nombre(ligne, colonne) is None:
                anomalies.append(
                    f"ligne {index} : `{colonne}` = '{valeur}' n'est pas un "
                    "nombre"
                )
        trajectoire = (ligne.get("trajectoire") or "").strip()
        if trajectoire and trajectoire not in TRAJECTOIRES:
            anomalies.append(
                f"ligne {index} : trajectoire `{trajectoire}` hors "
                f"vocabulaire {sorted(TRAJECTOIRES)}"
            )
        temoin = (ligne.get("temoin") or "").strip()
        if temoin and temoin not in TEMOINS:
            anomalies.append(
                f"ligne {index} : témoin `{temoin}` hors vocabulaire "
                f"{sorted(TEMOINS)}"
            )
        for colonne in ("division", "transmis", "reinitialisation"):
            valeur = (ligne.get(colonne) or "").strip()
            if valeur and valeur not in BOOLEENS:
                anomalies.append(
                    f"ligne {index} : `{colonne}` = '{valeur}', attendu "
                    "'oui' ou 'non'"
                )
    return anomalies, True


# --------------------------------------------------------------------------
# Cohérence des filiations

def valider_filiations(lignes: list[dict]) -> list[str]:
    """Une filiation incohérente invalide toute lecture héréditaire."""
    anomalies = []
    cycle_de: dict[str, float] = {}
    parent_de: dict[str, str] = {}

    for index, ligne in enumerate(lignes, start=2):
        identifiant = (ligne.get("compartiment_id") or "").strip()
        cycle = nombre(ligne, "cycle")
        parent = (ligne.get("parent_id") or "").strip()
        if not identifiant or cycle is None:
            continue
        if identifiant in cycle_de and cycle_de[identifiant] != cycle:
            anomalies.append(
                f"ligne {index} : le compartiment `{identifiant}` apparaît à "
                f"deux cycles différents ({cycle_de[identifiant]:g} et "
                f"{cycle:g})"
            )
        cycle_de.setdefault(identifiant, cycle)
        if parent:
            if parent == identifiant:
                anomalies.append(
                    f"ligne {index} : le compartiment `{identifiant}` est son "
                    "propre parent"
                )
            parent_de.setdefault(identifiant, parent)

    for enfant, parent in parent_de.items():
        if parent not in cycle_de:
            anomalies.append(
                f"filiation : le parent `{parent}` de `{enfant}` n'est "
                "déclaré nulle part. Une descendance sans ascendant "
                "enregistré n'est pas une lignée."
            )
            continue
        if cycle_de[parent] >= cycle_de[enfant]:
            anomalies.append(
                f"filiation : `{enfant}` (cycle {cycle_de[enfant]:g}) ne peut "
                f"pas descendre de `{parent}` (cycle {cycle_de[parent]:g})"
            )

    # Boucle d'ascendance.
    for depart in parent_de:
        vus = {depart}
        courant = parent_de.get(depart)
        while courant and courant in parent_de:
            if courant in vus:
                anomalies.append(
                    f"filiation : boucle d'ascendance en partant de `{depart}`"
                )
                break
            vus.add(courant)
            courant = parent_de.get(courant)

    return anomalies


def valider_couverture(lignes: list[dict]) -> tuple[list[str], list[str]]:
    """Séries assez longues, et témoins présents. Renvoie (erreurs, réserves)."""
    anomalies, reserves = [], []
    cycles = defaultdict(set)
    temoins = defaultdict(set)
    for ligne in lignes:
        experience = (ligne.get("experience_id") or "").strip()
        cycle = nombre(ligne, "cycle")
        if experience and cycle is not None:
            cycles[experience].add(cycle)
        if experience:
            temoins[experience].add((ligne.get("temoin") or "").strip())

    for experience, valeurs in sorted(cycles.items()):
        if len(valeurs) < CYCLES_MINIMUM:
            anomalies.append(
                f"expérience `{experience}` : {len(valeurs)} cycle(s). Le §4.1 "
                f"demande une trajectoire complète, au moins {CYCLES_MINIMUM} "
                "cycles."
            )

    for experience, presents in sorted(temoins.items()):
        if "complet" not in presents:
            anomalies.append(
                f"expérience `{experience}` : aucun bras `complet`. Il n'y a "
                "rien à comparer aux témoins."
            )
        if TEMOIN_APPARIE not in presents:
            reserves.append(
                f"expérience `{experience}` : témoin `{TEMOIN_APPARIE}` "
                "absent. Sans lui, une différence de persistance peut venir de "
                "la charge macromoléculaire et non de la copie. Voir "
                "`PROGRAMME_PREBIOTIQUE.md` §5."
            )
        manquants = sorted(TEMOINS - presents - {TEMOIN_APPARIE})
        if manquants:
            reserves.append(
                f"expérience `{experience}` : témoins absents {manquants}. "
                "La fonction des composants correspondants n'est pas isolée."
            )
    return anomalies, reserves


# --------------------------------------------------------------------------
# Critère minimal de réussite

def evaluer_critere(lignes: list[dict], seuil_p: float) -> dict:
    """Les six conditions du §6, et la variable principale du §7."""
    complets = [l for l in lignes if (l.get("temoin") or "").strip() == "complet"]
    cycle_de = {
        (l.get("compartiment_id") or "").strip(): nombre(l, "cycle")
        for l in complets
    }
    variante_de = {
        (l.get("compartiment_id") or "").strip():
            (l.get("variante") or "").strip()
        for l in complets
    }

    # C1 — copies produites avec variation.
    avec_variation = [
        l for l in complets
        if (nombre(l, "copies_produites") or 0) > 0
        and (l.get("variante") or "").strip() not in ("", VARIANTE_REFERENCE)
    ]
    c1 = len(avec_variation) > 0

    # C2 — les copies restent associées à un compartiment.
    c2 = all((l.get("compartiment_id") or "").strip() for l in avec_variation)

    # C3 — croissance et division.
    c3 = any((l.get("division") or "").strip() == "oui" for l in complets)

    # C4 — variantes transmises : un descendant porte la variante de son parent.
    transmissions = 0
    descendants = 0
    for ligne in complets:
        parent = (ligne.get("parent_id") or "").strip()
        if not parent:
            continue
        descendants += 1
        variante = (ligne.get("variante") or "").strip()
        if variante and variante == variante_de.get(parent):
            transmissions += 1
    c4 = transmissions > 0

    # C5 — certaines variantes modifient la persistance ou la reproduction.
    groupes = defaultdict(list)
    for ligne in complets:
        valeur = nombre(ligne, "fonction_mesuree")
        if valeur is not None:
            groupes[(ligne.get("variante") or "").strip()].append(valeur)
    reference = groupes.get(VARIANTE_REFERENCE, [])
    comparaisons = []
    for variante, valeurs in sorted(groupes.items()):
        if variante in ("", VARIANTE_REFERENCE) or not reference:
            continue
        entree = {
            "variante": variante,
            "n_variante": len(valeurs),
            "n_reference": len(reference),
            "moyenne_variante": sum(valeurs) / len(valeurs),
            "moyenne_reference": sum(reference) / len(reference),
            "p": None,
        }
        try:
            from scipy.stats import mannwhitneyu
            if len(valeurs) >= 2 and len(reference) >= 2:
                entree["p"] = float(
                    mannwhitneyu(valeurs, reference,
                                 alternative="two-sided").pvalue
                )
        except ImportError:
            pass
        comparaisons.append(entree)
    c5 = any(
        c["p"] is not None and c["p"] < seuil_p for c in comparaisons
    )

    # C6 — maintien sur plusieurs cycles sans réinitialisation complète.
    reinitialise = any(
        (l.get("reinitialisation") or "").strip() == "oui" for l in complets
    )
    cycles_par_variante = defaultdict(set)
    for ligne in complets:
        variante = (ligne.get("variante") or "").strip()
        cycle = nombre(ligne, "cycle")
        if variante and variante != VARIANTE_REFERENCE and cycle is not None:
            cycles_par_variante[variante].add(cycle)
    duree_max = max(
        (len(v) for v in cycles_par_variante.values()), default=0
    )
    c6 = (not reinitialise) and duree_max >= CYCLES_MINIMUM

    # Variable principale du §7 : information héritée ET différence
    # fonctionnelle mesurable.
    variantes_fonctionnelles = {
        c["variante"] for c in comparaisons
        if c["p"] is not None and c["p"] < seuil_p
    }
    conservent = 0
    for ligne in complets:
        if not (ligne.get("parent_id") or "").strip():
            continue
        parent = (ligne.get("parent_id") or "").strip()
        variante = (ligne.get("variante") or "").strip()
        if variante and variante == variante_de.get(parent) \
                and variante in variantes_fonctionnelles:
            conservent += 1
    proportion = conservent / descendants if descendants else None

    conditions = {
        "C1 copies avec variation": c1,
        "C2 copies associées à un compartiment": c2,
        "C3 croissance et division": c3,
        "C4 variantes transmises": c4,
        f"C5 effet fonctionnel (p < {seuil_p})": c5,
        f"C6 maintien ≥ {CYCLES_MINIMUM} cycles sans réinitialisation": c6,
    }
    return {
        "conditions": conditions,
        "atteintes": sum(conditions.values()),
        "descendants_examines": descendants,
        "descendants_conservant_la_variante": transmissions,
        "comparaisons_fonctionnelles": comparaisons,
        "cycles_max_d_une_variante": duree_max,
        "reinitialisation_declaree": reinitialise,
        "variable_principale": proportion,
    }


# --------------------------------------------------------------------------
# Gabarit

GABARIT = [
    COLONNES,
    # experience, trajectoire, temoin, compartiment, cycle, parent, matrice,
    # variante, longueur, copies, fidelite, volume, division, transmis,
    # fonction, reinitialisation
    [MARQUEUR_GABARIT, "humide_sec", "complet", "C-001", "0", "", "M-001",
     "reference", "24", "0", "", "1.0", "non", "non", "1.00", "non"],
    [MARQUEUR_GABARIT, "humide_sec", "complet", "C-002", "1", "C-001",
     "M-001", "reference", "24", "3", "0.97", "1.4", "oui", "oui", "1.02",
     "non"],
    [MARQUEUR_GABARIT, "humide_sec", "complet", "C-003", "1", "C-001",
     "M-001", "V-A", "26", "3", "0.95", "1.5", "oui", "oui", "1.31", "non"],
    [MARQUEUR_GABARIT, "humide_sec", "complet", "C-004", "2", "C-003",
     "M-001", "V-A", "26", "4", "0.96", "1.6", "oui", "oui", "1.28", "non"],
    [MARQUEUR_GABARIT, "humide_sec", "complet", "C-005", "2", "C-002",
     "M-001", "reference", "24", "2", "0.98", "1.3", "oui", "oui", "0.99",
     "non"],
    [MARQUEUR_GABARIT, "humide_sec", "complexite_egale", "T-001", "0", "",
     "", "reference", "24", "0", "", "1.0", "non", "non", "1.01", "non"],
    [MARQUEUR_GABARIT, "humide_sec", "complexite_egale", "T-002", "1",
     "T-001", "", "reference", "24", "0", "", "1.2", "oui", "non", "1.00",
     "non"],
    [MARQUEUR_GABARIT, "humide_sec", "complexite_egale", "T-003", "2",
     "T-002", "", "reference", "24", "0", "", "1.1", "oui", "non", "0.98",
     "non"],
]


def ecrire_gabarit(repertoire: Path) -> None:
    repertoire.mkdir(parents=True, exist_ok=True)
    cible = repertoire / FICHIER
    with cible.open("w", encoding="utf-8-sig", newline="") as flux:
        csv.writer(flux, delimiter=SEPARATEUR).writerows(GABARIT)
    print(f"gabarit synthétique écrit dans {cible}")
    print("Ces valeurs sont inventées. Elles servent de modèle de format, "
          "jamais de résultat.")


# --------------------------------------------------------------------------

def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--repertoire", type=Path,
                         default=RACINE / "schema_lignees" / "gabarit")
    parseur.add_argument("--gabarit", action="store_true")
    parseur.add_argument("--critere", action="store_true")
    parseur.add_argument("--seuil-p", type=float, default=0.05,
                         help="seuil de la condition C5 ; doit être "
                              "préenregistré avant collecte")
    arguments = parseur.parse_args()
    repertoire = arguments.repertoire.resolve()

    if arguments.gabarit:
        ecrire_gabarit(repertoire)
        return 0

    chemin = repertoire / FICHIER
    if not chemin.exists():
        print(f"{FICHIER} absent de {repertoire}.")
        print("Produire un modèle conforme avec --gabarit.")
        return 1

    lignes = lire(chemin)
    synthetique = any(
        (l.get("experience_id") or "").strip() == MARQUEUR_GABARIT
        for l in lignes
    )

    anomalies, exploitables = valider_schema(lignes)
    reserves: list[str] = []
    if exploitables:
        anomalies += valider_filiations(lignes)
        erreurs, reserves = valider_couverture(lignes)
        anomalies += erreurs

    for anomalie in anomalies:
        print(f"  {anomalie}")
    if anomalies:
        print(f"\n{len(anomalies)} anomalie(s). Ce n'est pas une table de "
              "lignées conforme.")
        return 1

    print(f"{chemin} : {len(lignes)} ligne(s), table de lignées conforme.")
    for reserve in reserves:
        print(f"  réserve : {reserve}")

    if arguments.critere:
        resultat = evaluer_critere(lignes, arguments.seuil_p)
        print("\nCritère minimal de réussite, §6 :")
        for nom, atteinte in resultat["conditions"].items():
            print(f"  [{'X' if atteinte else ' '}] {nom}")
        print(f"\n  {resultat['atteintes']}/6 conditions atteintes")
        proportion = resultat["variable_principale"]
        print("\nVariable principale, §7 — proportion de descendants "
              "conservant\nune information héritée ET une différence "
              "fonctionnelle :")
        if proportion is None:
            print("  non calculable : aucun descendant enregistré")
        else:
            print(f"  {proportion:.3f}  "
                  f"({resultat['descendants_conservant_la_variante']} "
                  f"variantes transmises sur "
                  f"{resultat['descendants_examines']} descendants)")
        for comparaison in resultat["comparaisons_fonctionnelles"]:
            p = comparaison["p"]
            print(f"  variante {comparaison['variante']} : "
                  f"moyenne {comparaison['moyenne_variante']:.3f} contre "
                  f"{comparaison['moyenne_reference']:.3f} "
                  f"(n = {comparaison['n_variante']} / "
                  f"{comparaison['n_reference']}, "
                  f"p = {'n. d.' if p is None else f'{p:.4f}'})")
        if resultat["atteintes"] < 6:
            print("\nLes six conditions sont requises simultanément. "
                  "Le critère n'est pas atteint.")

    if synthetique:
        print(f"\nATTENTION : cette table porte le marqueur "
              f"`{MARQUEUR_GABARIT}`.\nElle est synthétique et ne constitue "
              "aucune mesure. Aucun résultat ne peut en être tiré.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
