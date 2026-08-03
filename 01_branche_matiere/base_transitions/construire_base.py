"""Base de données des 40 transitions — WP-M1 du plan directeur.

Le WP-M1 demande quinze champs pour chacune des 40 transitions. Le dossier en
contient déjà cinq, dispersés dans `noeuds_poc.csv` et
`relations_oric_47_provisoires.csv`. Ce script les rassemble dans le schéma
demandé, laisse les dix autres **explicitement vides**, et mesure le taux de
complétude.

    Il n'invente aucun contenu scientifique. Un champ qu'aucune source du
    dossier ne renseigne reste vide et est compté comme manquant.

C'est la différence entre construire une base et la remplir. Le plan demande la
première ; la seconde exige la littérature et des évaluateurs.

    python construire_base.py             # écrit transitions_matiere.csv
    python construire_base.py --verifier  # complétude par champ
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
CARTE = RACINE.parents[1] / "00_socle" / "carte_relationnelle" / "data"
CIBLE = RACINE / "transitions_matiere.csv"
RAPPORT = RACINE / "completude.json"
SEPARATEUR = ";"

# Les quinze champs du WP-M1, dans l'ordre du plan.
CHAMPS = [
    "id",
    "transition",
    "regime_num",
    "regime_nom",
    "etat_anterieur",              # WP-M1.1
    "etat_posterieur",             # WP-M1.2
    "dimension_n",                 # WP-M1.3
    "dimension_G",
    "dimension_I",
    "dimension_E",
    "dimension_Pi",
    "dimension_H",
    "date",                        # WP-M1.4
    "date_incertitude",
    "preuves_directes",            # WP-M1.5
    "preuves_indirectes",          # WP-M1.6
    "modeles_concurrents",         # WP-M1.7
    "seuil_ou_plage",              # WP-M1.8
    "vitesse_de_variation",        # WP-M1.9
    "etats_devenus_accessibles",   # WP-M1.10
    "etats_fermes",                # WP-M1.11
    "pertes",                      # WP-M1.12
    "mecanismes_de_persistance",   # WP-M1.13
    "contre_exemples",             # WP-M1.14
    "niveau_de_preuve",            # WP-M1.15
    "evaluateurs",
    "source_du_remplissage",
]

# Champs qu'une source du dossier peut renseigner. Tous les autres restent
# vides par construction.
RENSEIGNABLES = {
    "id", "transition", "regime_num", "regime_nom", "etat_posterieur",
    "date", "etats_devenus_accessibles", "etats_fermes", "niveau_de_preuve",
    "etat_anterieur", "source_du_remplissage",
}


def lire(chemin: Path) -> list[dict]:
    with chemin.open(encoding="utf-8-sig", newline="") as flux:
        return list(csv.DictReader(flux, delimiter=SEPARATEUR))


def construire() -> list[dict]:
    noeuds = lire(CARTE / "noeuds_poc.csv")
    liens = lire(CARTE / "relations_oric_47_provisoires.csv")

    # L'état antérieur d'une transition : les transitions qui pointent vers
    # elle par un lien non rétroactif. C'est une dérivation, pas une donnée.
    amont: dict[str, list[str]] = {}
    par_id = {n["id"]: n for n in noeuds}
    for lien in liens:
        if lien["relation"] == "FEED":
            continue
        amont.setdefault(lien["target"], []).append(lien["source"])

    lignes = []
    for noeud in noeuds:
        identifiant = noeud["id"]
        precedents = amont.get(identifiant, [])
        etat_anterieur = " ; ".join(
            f"{p} {par_id[p]['transition']}" for p in sorted(precedents)
        )
        ligne = {champ: "" for champ in CHAMPS}
        ligne.update({
            "id": identifiant,
            "transition": noeud["transition"],
            "regime_num": noeud["regime_num"],
            "regime_nom": noeud["regime_nom"],
            "etat_anterieur": etat_anterieur,
            "etat_posterieur": noeud["transition"],
            "date": noeud["fenetre_ou_ancrage_principal"],
            "etats_devenus_accessibles": noeud["domaine_ouvert"],
            "etats_fermes": noeud["domaine_ferme"],
            "niveau_de_preuve": noeud["statut_methodologique"],
            "source_du_remplissage": (
                "carte_relationnelle/data ; état antérieur dérivé des liens "
                "entrants non rétroactifs"
            ),
        })
        lignes.append(ligne)
    return lignes


def completude(lignes: list[dict]) -> dict:
    par_champ = {}
    for champ in CHAMPS:
        remplis = sum(1 for l in lignes if (l.get(champ) or "").strip())
        par_champ[champ] = {
            "remplis": remplis,
            "sur": len(lignes),
            "taux": remplis / len(lignes) if lignes else 0.0,
            "renseignable_depuis_le_dossier": champ in RENSEIGNABLES,
        }
    demandes = [c for c in CHAMPS if c not in ("id", "regime_num",
                                               "regime_nom", "evaluateurs",
                                               "source_du_remplissage")]
    total = sum(par_champ[c]["remplis"] for c in demandes)
    return {
        "transitions": len(lignes),
        "champs_du_WP_M1": len(demandes),
        "cellules_attendues": len(demandes) * len(lignes),
        "cellules_remplies": total,
        "taux_global": total / (len(demandes) * len(lignes)) if lignes else 0.0,
        "par_champ": par_champ,
        "champs_entierement_vides": sorted(
            c for c in demandes if par_champ[c]["remplis"] == 0
        ),
        "lecture": (
            "Les champs entièrement vides ne sont pas une négligence : aucune "
            "source du dossier ne les renseigne. Les remplir demande la "
            "littérature primaire et des évaluateurs indépendants, ce que le "
            "WP-M1.15 exige explicitement."
        ),
    }


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--verifier", action="store_true")
    arguments = parseur.parse_args()

    if arguments.verifier:
        if not CIBLE.exists():
            print(f"{CIBLE.name} absent.")
            return 1
        lignes = lire(CIBLE)
    else:
        lignes = construire()
        with CIBLE.open("w", encoding="utf-8-sig", newline="") as flux:
            redacteur = csv.DictWriter(flux, fieldnames=CHAMPS,
                                       delimiter=SEPARATEUR)
            redacteur.writeheader()
            redacteur.writerows(lignes)
        print(f"{CIBLE.name} écrit : {len(lignes)} transitions")

    mesure = completude(lignes)
    RAPPORT.write_text(json.dumps(mesure, indent=2, ensure_ascii=False),
                       encoding="utf-8")
    print(f"\nComplétude WP-M1 : {mesure['cellules_remplies']} cellules "
          f"sur {mesure['cellules_attendues']} "
          f"({mesure['taux_global']:.1%})")
    print("\nChamps renseignés :")
    for champ, valeur in mesure["par_champ"].items():
        if valeur["remplis"]:
            print(f"  {champ:28s} {valeur['remplis']:2d}/{valeur['sur']} "
                  f"({valeur['taux']:.0%})")
    print("\nChamps entièrement vides, à remplir depuis la littérature :")
    for champ in mesure["champs_entierement_vides"]:
        print(f"  {champ}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
