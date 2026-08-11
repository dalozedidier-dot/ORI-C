"""Campagne d'inventaire accessible : azote, carbone, hydrogène et soufre.

Le protocole demande de comparer des histoires menant à des inventaires totaux
voisins mais à des répartitions différentes. Quatre éléments volatils et
sidérophiles permettent maintenant la comparaison, sur la même Terre : chacun a
suivi la même ségrégation métal-silicate, avec des issues très différentes.

Le fichier de données porte l'unité de la source — ppm, wt%, kg. La conversion
en masse est faite ici, à partir de masses de réservoir déclarées et sourcées,
pour qu'elle soit vérifiable et non enfouie dans la saisie.

Aucune valeur n'est imputée : un inventaire accessible chiffré exige que les
deux facteurs qui le produisent soient eux-mêmes renseignés.

    python analyser_inventaire.py
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ICI = Path(__file__).resolve().parent

# Fraction massique d'hydrogène dans l'eau : 2 x 1.008 / 18.015.
FRACTION_H_DANS_H2O = 2 * 1.008 / 18.015

MASSES_PLANETAIRES = {"Terre": 5.9722e24, "Venus": 4.8675e24}

RESERVOIRS_DE_SURFACE = {
    "atmosphere", "croute continentale", "croute oceanique",
    "sediments oceaniques", "hydrosphere",
}

# Pour chaque élément : le pôle silicaté ou de surface qui sert de référence,
# puis les estimations concurrentes du noyau. Rien n'est moyenné : les
# désaccords publiés restent des branches distinctes.
COMPARAISONS = {
    "N": ("N-TER-BSE", {
        "chondritique CC": "N-TER-NOY-CC",
        "chondritique EC": "N-TER-NOY-EC",
        "ab initio Zhang-Yin": "N-TER-NOY-ZY"}),
    "C": ("C-TER-BSE", {
        "borne experimentale basse": "C-TER-NOY-BAS",
        "accretion multi-etapes, min": "C-TER-NOY-MIN",
        "accretion multi-etapes, max": "C-TER-NOY-MAX"}),
    "H": ("H-TER-OCE", {
        "accretion multi-etapes, min": "H-TER-NOY-MIN",
        "accretion multi-etapes, max": "H-TER-NOY-MAX"}),
    "S": ("S-TER-BSE", {
        "tendance de volatilite": "S-TER-NOY"}),
}


def lire(nom: str) -> list[dict]:
    with (ICI / nom).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def en_kilogrammes(ligne: dict, masses: dict) -> float | None:
    """Convertit vers une masse de l'élément, en kg. None si non convertible."""
    valeur, unite = float(ligne["quantite_totale"]), ligne["unite"]
    if unite == "kg":
        return valeur
    if unite == "kg H2O":
        return valeur * FRACTION_H_DANS_H2O
    cle = (ligne["reservoir"], ligne["corps"])
    if cle not in masses:
        return None
    masse = masses[cle]
    if unite == "ppm":
        return valeur * 1e-6 * masse
    if unite == "wt%":
        return valeur * 1e-2 * masse
    if unite == "wt% H2O":
        return valeur * 1e-2 * masse * FRACTION_H_DANS_H2O
    return None


def valider(lignes: list[dict], sources: set[str], kg: dict) -> list[str]:
    erreurs = []
    for l in lignes:
        r = l["record_id"]
        if l["source"] not in sources:
            erreurs.append(f"{r}: source {l['source']} absente du registre")
        for champ in ("corps", "element", "reservoir", "quantite_totale",
                      "unite", "statut"):
            if not l[champ]:
                erreurs.append(f"{r}: champ obligatoire {champ} vide")
        if l["inventaire_accessible"] and not (
                l["fraction_mobilisable"] and l["probabilite_transfert"]):
            erreurs.append(f"{r}: inventaire accessible chiffre sans facteurs")
        if kg.get(r) is None:
            erreurs.append(f"{r}: unite {l['unite']} non convertible "
                           f"pour le reservoir {l['reservoir']}")
    return erreurs


def main() -> int:
    sources = {s["source_id"] for s in lire("sources.csv")}
    masses = {(m["reservoir"], m["corps"]): float(m["masse_kg"])
              for m in lire("masses_reservoirs.csv")}
    lignes = lire("inventaire_accessible.csv")
    kg = {l["record_id"]: en_kilogrammes(l, masses) for l in lignes}
    erreurs = valider(lignes, sources, kg)

    par_element = {}
    for element, (ref, scenarios) in COMPARAISONS.items():
        silicate = kg[ref]
        branches = {}
        for nom, ident in scenarios.items():
            noyau = kg[ident]
            branches[nom] = {
                "noyau_kg": float(f"{noyau:.4g}"),
                "rapport_noyau_sur_reference": round(noyau / silicate, 2),
                "part_accessible": round(silicate / (silicate + noyau), 5),
            }
        parts = [b["part_accessible"] for b in branches.values()]
        par_element[element] = {
            "reservoir_de_reference": ref,
            "masse_de_reference_kg": float(f"{silicate:.4g}"),
            "scenarios_du_noyau": branches,
            "etendue_de_la_part_accessible": [min(parts), max(parts)],
            "facteur_d_indetermination": round(max(parts) / min(parts), 1),
        }

    # Bouclage des budgets publiés. Le contenu global d'un élément est estimé
    # indépendamment de la somme noyau + silicate. Les deux doivent coïncider.
    # C'est le pendant, sur les données, du contrôle de clôture sur le graphe :
    # si la somme des réservoirs ne reconstitue pas le total, un réservoir
    # manque ou une estimation est fausse. Les bornes sont appariées entre
    # elles : min du noyau avec min du total, max avec max.
    BOUCLAGES = {
        "C": [("C-TER-NOY-MIN", "C-TER-BSE", "C-TER-BULK-MIN", "borne basse"),
              ("C-TER-NOY-MAX", "C-TER-BSE", "C-TER-BULK-MAX", "borne haute")],
        "H": [("H-TER-NOY-MIN", "H-TER-OCE", "H-TER-BULK-MIN", "borne basse"),
              ("H-TER-NOY-MAX", "H-TER-OCE", "H-TER-BULK-MAX", "borne haute")],
        "S": [("S-TER-NOY", "S-TER-BSE", "S-TER-BULK", "estimation unique")],
    }
    bouclage = {}
    for element, cas in BOUCLAGES.items():
        bouclage[element] = []
        for noyau, silicate, total, nom in cas:
            somme, global_ = kg[noyau] + kg[silicate], kg[total]
            bouclage[element].append({
                "borne": nom,
                "noyau_plus_silicate_kg": float(f"{somme:.4g}"),
                "total_publie_independamment_kg": float(f"{global_:.4g}"),
                "ecart_relatif": round((somme - global_) / global_, 4),
                "boucle_a_5_pourcent": abs(somme - global_) / global_ < 0.05,
            })
    ecarts = [abs(c["ecart_relatif"]) for l in bouclage.values() for c in l]

    # Épreuve indépendante : les coefficients de partage mesurés en laboratoire
    # prédisent-ils la répartition observée entre noyau et silicate ?
    #
    #   D = concentration dans le métal / concentration dans le silicate
    #   rapport de masses attendu = D x (masse du noyau / masse du silicate)
    #
    # Les deux côtés viennent de sources indépendantes : des expériences à haute
    # pression d'un côté, des budgets géochimiques de l'autre. Un recouvrement
    # n'est donc pas une tautologie. Un désaccord désignerait soit une condition
    # de ségrégation mal choisie, soit un budget faux.
    coefficients = lire("coefficients_partage.csv")
    rapport_des_masses = (masses[("noyau", "Terre")]
                          / masses[("terre silicatee totale", "Terre")])
    prediction = {}
    for element in sorted({c["element"] for c in coefficients}):
        cas = [c for c in coefficients if c["element"] == element]
        valeurs = [float(c["D_metal_sur_silicate"]) for c in cas]
        # Une borne inférieure publiée n'est pas une valeur : elle ouvre
        # l'intervalle vers le haut. Traiter D_H >= 29 comme un point aurait
        # fabriqué un désaccord qui n'existe pas.
        ouvert_vers_le_haut = any(c["type_de_valeur"] == "borne_inferieure"
                                  for c in cas)
        attendu = [round(min(valeurs) * rapport_des_masses, 2),
                   None if ouvert_vers_le_haut
                   else round(max(valeurs) * rapport_des_masses, 2)]
        observes = [b["rapport_noyau_sur_reference"]
                    for b in par_element[element]["scenarios_du_noyau"].values()]
        observe = [min(observes), max(observes)]
        prediction[element] = {
            "D_publies": sorted(valeurs),
            "rapport_de_masses_attendu": attendu,
            "rapport_de_masses_observe": observe,
            "borne_superieure_ouverte": ouvert_vers_le_haut,
            "recouvrement": not (
                (attendu[1] is not None and attendu[1] < observe[0])
                or observe[1] < attendu[0]),
        }

    classement = sorted(
        par_element.items(),
        key=lambda kv: max(b["rapport_noyau_sur_reference"]
                           for b in kv[1]["scenarios_du_noyau"].values()),
        reverse=True)

    surface_n = sum(kg[l["record_id"]] for l in lignes
                    if l["corps"] == "Terre" and l["element"] == "N"
                    and l["reservoir"] in RESERVOIRS_DE_SURFACE)
    venus = kg["N-VEN-ATM"]

    rapport = {
        "statut": "valide" if not erreurs else "invalide",
        "erreurs": erreurs,
        "enregistrements": len(lignes),
        "elements": sorted({l["element"] for l in lignes}),
        "corps": sorted({l["corps"] for l in lignes}),
        "records_sans_inventaire_accessible_calculable": sum(
            1 for l in lignes if not l["inventaire_accessible"]),
        "par_element": par_element,
        "prediction_par_les_coefficients_de_partage": prediction,
        "elements_ou_la_prediction_recouvre_l_observation": sorted(
            e for e, d in prediction.items() if d["recouvrement"]),
        "elements_en_desaccord": sorted(
            e for e, d in prediction.items() if not d["recouvrement"]),
        "bouclage_des_budgets": bouclage,
        "bouclage_ecart_maximal": max(ecarts),
        "bouclage_integralement_verifie": all(
            c["boucle_a_5_pourcent"] for l in bouclage.values() for c in l),
        "classement_par_sequestration_maximale": [
            (e, max(b["rapport_noyau_sur_reference"]
                    for b in d["scenarios_du_noyau"].values()))
            for e, d in classement],
        "comparaison_Terre_Venus_azote": {
            "azote_de_surface_Terre_kg": float(f"{surface_n:.4g}"),
            "azote_atmospherique_Venus_kg": float(f"{venus:.4g}"),
            "rapport_brut": round(venus / surface_n, 2),
            "rapport_normalise_par_masse_planetaire": round(
                (venus / MASSES_PLANETAIRES["Venus"])
                / (surface_n / MASSES_PLANETAIRES["Terre"]), 2),
        },
        "portee": (
            "Quatre elements, un episode, deux corps pour le seul azote. Les "
            "fractions mobilisables et les probabilites de transfert restent "
            "non contraintes hors des reservoirs de surface : elles ne sont "
            "pas imputees. Ce tableau mesure une repartition, il ne valide "
            "pas ORI-C."),
    }
    (ICI / "inventaire_accessible_resultats.json").write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps(rapport, ensure_ascii=False, indent=2))
    return 1 if erreurs else 0


if __name__ == "__main__":
    raise SystemExit(main())
