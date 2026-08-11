"""Construit les trois registres manquants du modele canonique.

Le modele de donnees demande trois registres qui n'existaient pas : les
conditions, les relations typees et les preuves. Ils sont construits ici a
partir de contenu deja present dans le dossier, pas livres comme des schemas
vides. Un schema vide se remplit rarement ; un registre peuple se corrige.

    CON  conditions       extraites des transformations et du vocabulaire
                          de conditions permissives de la genealogie
    REL  relations typees derivees des filiations parent -> produit de la
                          genealogie, avec mecanisme et fenetre temporelle
    PRV  preuves          derivees des quatre axes de certitude

Une regle gouverne l'ensemble : un identifiant designe une seule chose. Une
relation, une condition ou une transformation n'est jamais encodee comme si
elle etait une matiere. Le champ `type_registre` ajoute a l'index maitre rend
cette distinction explicite sur les 550 entrees existantes.

    python construire_registres.py
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ICI = Path(__file__).resolve().parent
TABLES = ICI / "tables"
DOSSIER = ICI.parents[1]
ARBRE = DOSSIER / "00_socle" / "genealogie" / "arbre_genealogique.csv"

# Le niveau principal de l'index determine le registre auquel une entree
# appartient. La correspondance est deterministe, donc verifiable.
REGISTRE = {
    "Constituants fondamentaux": "ENT",
    "Particules composites": "ENT",
    "Noyaux et nuclides": "NUC",
    "Atomes et éléments": "ENT",
    "Molécules et assemblages chimiques": "ENT",
    "États et phases": "PHA",
    "Matériaux et minéraux": "MAT",
    "Réservoirs astronomiques": "RES",
    "Matière biologique": "BIO",
    "Inconnus et hypothèses": "UNK",
    "Transformations": "TRF",
}

# Role d'une condition : ce qui ouvre une transformation, ce qui la borne.
ROLE = {
    "gravité": "permissif", "expansion cosmologique": "permissif",
    "flux ultraviolet": "permissif", "chocs": "permissif",
    "refroidissement par H2": "permissif", "refroidissement par HD": "permissif",
    "turbulence du disque": "permissif", "piège à pression": "permissif",
    "énergie hydrothermale": "permissif", "cycles humide-sec": "permissif",
    "circulation hydrothermale": "permissif", "flux XUV stellaire": "permissif",
    "seuil de Roche": "contraignant", "fugacité d'oxygène": "contraignant",
    "dissipation du disque": "contraignant", "rayonnement cosmique": "permissif",
}


def lire(chemin, delim=";"):
    with Path(chemin).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=delim))


def ecrire(nom, champs, lignes):
    cible = TABLES / f"{nom}.csv"
    with cible.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=champs, delimiter=";")
        w.writeheader(); w.writerows(lignes)
    return len(lignes)


def main() -> int:
    arbre = lire(ARBRE)
    transformations = lire(TABLES / "13_Transformations.csv")
    index = lire(TABLES / "01_Index_maitre.csv")

    # --- type_registre sur l'index maitre ---------------------------------
    inconnus = sorted({r["Niveau principal"] for r in index}
                      - set(REGISTRE))
    if inconnus:
        raise SystemExit(f"niveaux sans registre : {inconnus}")
    for r in index:
        r["type_registre"] = REGISTRE[r["Niveau principal"]]
    champs_index = list(index[0].keys())
    n_index = ecrire("01_Index_maitre", champs_index, index)

    # --- CON : conditions --------------------------------------------------
    conditions, vues = [], {}
    for t in transformations:
        texte = (t["Conditions"] or "").strip()
        if not texte or texte in vues:
            continue
        vues[texte] = True
        conditions.append({
            "condition_id": f"CON-{len(conditions)+1:03d}",
            "variable": texte,
            "origine": f"transformation « {t['Transformation']} »",
            "echelle": t["Échelle"],
            "role": "permissif",
            "unite": "", "plage": "", "duree": "",
            "source_url": t["Source URL"],
        })
    # Conditions permissives declarees par la genealogie, avec leur role.
    for x in arbre:
        for c in (v.strip() for v in x["conditions_permissives"].split("|")):
            if not c or c == "aucune" or c in vues:
                continue
            vues[c] = True
            conditions.append({
                "condition_id": f"CON-{len(conditions)+1:03d}",
                "variable": c,
                "origine": f"genealogie, transition {x['id']}",
                "echelle": "généalogie ORI-C",
                "role": ROLE.get(c, "à qualifier"),
                "unite": "", "plage": "", "duree": "",
                "source_url": "",
            })
    n_con = ecrire("16_Conditions_CON", list(conditions[0].keys()), conditions)

    # --- REL : relations typees -------------------------------------------
    relations = []
    for x in arbre:
        for parent in (p.strip() for p in x["parents_materiels"].split("|")):
            if not parent:
                continue
            relations.append({
                "relation_id": f"REL-{len(relations)+1:04d}",
                "source_libelle": parent,
                "relation_type": "filiation_materielle",
                "target_libelle": x["produit"],
                "transformation_id": x["id"],
                "mecanisme": x["mecanisme_categorie"],
                "reservoir": x["milieu"],
                "condition_ids": " | ".join(
                    c.strip() for c in x["conditions_permissives"].split("|")
                    if c.strip() and c.strip() != "aucune"),
                "fenetre": x["epoque"],
                "axe_mecanisme": x["preuve_du_mecanisme"],
                "axe_milieu_naturel": x["preuve_en_milieu_naturel"],
                "axe_transition_historique": x["preuve_de_la_transition_historique"],
                "axe_role_causal": x["certitude_du_role_causal"],
            })
        for c in (v.strip() for v in x["conditions_permissives"].split("|")):
            if c and c != "aucune":
                relations.append({
                    "relation_id": f"REL-{len(relations)+1:04d}",
                    "source_libelle": c,
                    "relation_type": "condition_ouverture",
                    "target_libelle": x["produit"],
                    "transformation_id": x["id"],
                    "mecanisme": x["mecanisme_categorie"],
                    "reservoir": x["milieu"],
                    "condition_ids": "",
                    "fenetre": x["epoque"],
                    "axe_mecanisme": x["preuve_du_mecanisme"],
                    "axe_milieu_naturel": x["preuve_en_milieu_naturel"],
                    "axe_transition_historique": x["preuve_de_la_transition_historique"],
                    "axe_role_causal": x["certitude_du_role_causal"],
                })
    n_rel = ecrire("17_Relations_REL", list(relations[0].keys()), relations)

    # --- PRV : preuves -----------------------------------------------------
    preuves = []
    AXES = [("preuve_du_mecanisme", "mécanisme"),
            ("preuve_en_milieu_naturel", "milieu naturel"),
            ("preuve_de_la_transition_historique", "transition historique"),
            ("certitude_du_role_causal", "rôle causal")]
    for x in arbre:
        for champ, domaine in AXES:
            preuves.append({
                "evidence_id": f"PRV-{len(preuves)+1:04d}",
                "cible_id": x["id"],
                "domaine": domaine,
                "niveau": x[champ],
                "mode_experimental": x["preuve_experimentale"][:180],
                "mode_observationnel": x["preuve_observationnelle"][:180],
                "statut_evaluation": x.get("statut_evaluation_certitudes", ""),
            })
    n_prv = ecrire("18_Preuves_PRV", list(preuves[0].keys()), preuves)

    rapport = {
        "index_maitre_type_registre": n_index,
        "repartition_registres": dict(Counter(r["type_registre"] for r in index)),
        "CON_conditions": n_con,
        "roles_declares": dict(Counter(c["role"] for c in conditions)),
        "REL_relations": n_rel,
        "types_de_relation": dict(Counter(r["relation_type"] for r in relations)),
        "PRV_preuves": n_prv,
        "niveaux_par_axe": {
            d: dict(Counter(p["niveau"] for p in preuves if p["domaine"] == d))
            for _, d in AXES},
        "regle": ("un identifiant designe une seule chose : une relation, une "
                  "condition ou une transformation n'est jamais encodee comme "
                  "une matiere"),
        "portee": ("les registres sont peuples a partir du contenu existant. "
                   "Les colonnes unite, plage et duree des conditions restent "
                   "vides : elles exigent une mesure, pas une transcription."),
    }
    (ICI / "registres_canoniques.json").write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(rapport, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
