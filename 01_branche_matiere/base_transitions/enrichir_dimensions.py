"""Codage qualitatif sourcé des six dimensions ORI-C pour les 40 transitions.

Les valeurs sont des descriptions opérationnelles, pas des mesures numériques.
La littérature source le contexte matériel ; l'affectation aux six dimensions
reste un codage ORI-C interprétatif et doit être soumis à des codeurs externes.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "transitions_matiere.csv"
SOURCES = ROOT / "sources_dimensions.csv"
REPORT = ROOT / "qualite_dimensions.json"
PLATFORM_DATA = ROOT.parents[1] / "plateforme" / "donnees" / "matter_transitions.csv"

TEMPLATES = {
    "1": {
        "n": "champs, particules et noyaux pertinents au régime primordial",
        "G": "état collectif fixé par symétries, phases et expansion cosmique",
        "I": "interactions fondamentales, réactions et découplages thermiques",
        "E": "température et densité de l'Univers en expansion",
        "Pi": "persistance par stabilité des particules/noyaux et refroidissement cosmique",
    },
    "2": {
        "n": "gaz H/He, étoiles, noyaux synthétisés et éjecta",
        "G": "nuages auto-gravitants, intérieurs stellaires et résidus compacts",
        "I": "gravitation, refroidissement radiatif, fusion et réactions neutroniques",
        "E": "densité, métallicité, rayonnement et potentiel gravitationnel",
        "Pi": "maintien gravitationnel et signatures nucléosynthétiques conservées",
    },
    "3": {
        "n": "atomes, ions, molécules, glaces et grains réactifs",
        "G": "réseaux moléculaires et surfaces de grains dans le gaz interstellaire",
        "I": "réactions gaz-phase/surface, adsorption, désorption et photchimie",
        "E": "température, densité, UV et rayonnement cosmique",
        "Pi": "stockage dans liaisons moléculaires, glaces et grains",
    },
    "4": {
        "n": "minéraux réfractaires, chondres, poussières et galets",
        "G": "grains, agrégats et concentrations du disque protoplanétaire",
        "I": "condensation, fusion, collisions, traînée gazeuse et auto-gravité",
        "E": "température, pression, turbulence et position dans le disque",
        "Pi": "textures, minéralogie et chronomètres isotopiques conservés dans les solides",
    },
    "5": {
        "n": "métaux, silicates, volatils et matériaux planétaires",
        "G": "séparation noyau-manteau-croûte, océans magmatiques et enveloppes fluides",
        "I": "partitionnement, convection, cristallisation, dégazage et gravitation",
        "E": "pression-température, fugacité d'oxygène, impacts et irradiation",
        "Pi": "réservoirs géochimiques, couches planétaires et cycles durables",
    },
    "6": {
        "n": "minéraux primaires/secondaires, fluides et constituants biologiques",
        "G": "réseaux cristallins, assemblages minéraux et interfaces fluide-roche",
        "I": "précipitation, dissolution, redox, métamorphisme et biominéralisation",
        "E": "pression-température, eau, pH, potentiel redox et activité biologique",
        "Pi": "stabilité cristalline et archives minéralogiques/géochimiques",
    },
    "7": {
        "n": "précurseurs nucléotidiques, acides aminés, lipides et activateurs",
        "G": "mélanges réactionnels, surfaces minérales, polymères et compartiments",
        "I": "photochimie, activation, condensation, catalyse et auto-assemblage",
        "E": "UV, cycles humides-secs, pH, température et disponibilité minérale",
        "Pi": "cycles réactionnels, compartimentation et copie imparfaite",
    },
    "8": {
        "n": "gènes, ARN, protéines, membranes, métabolites et organites",
        "G": "réseaux cellulaires, génomes, compartiments et organismes multicellulaires",
        "I": "traduction, métabolisme, réplication, symbiose et signalisation",
        "E": "ressources, gradients, écologie, oxygène et contraintes de sélection",
        "Pi": "réplication, réparation, hérédité, sélection et homéostasie",
    },
}


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter=";"))


def main() -> int:
    rows = load(DATA)
    sources = {row["regime_num"]: row for row in load(SOURCES)}
    fields = list(rows[0])
    for row in rows:
        template = TEMPLATES[row["regime_num"]]
        transition = row["transition"]
        row["dimension_n"] = f"{template['n']} — cas: {transition}"
        row["dimension_G"] = f"{template['G']} — état postérieur: {row['etat_posterieur']}"
        row["dimension_I"] = template["I"]
        row["dimension_E"] = f"{template['E']} — fenêtre: {row['date']}"
        row["dimension_Pi"] = template["Pi"]
        antecedent = row["etat_anterieur"] or "antécédent historique non résolu"
        row["dimension_H"] = f"héritage/dépendance au chemin depuis: {antecedent}"
        source = sources[row["regime_num"]]
        citation = f"codage qualitatif ORI-C d'après {source['reference']} — {source['doi_ou_url']}"
        if citation not in row["source_du_remplissage"]:
            row["source_du_remplissage"] = f"{row['source_du_remplissage']} ; {citation}".strip(" ;")
    with DATA.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    PLATFORM_DATA.parent.mkdir(parents=True, exist_ok=True)
    platform_fields = ["transition_id", "before_state", "after_state", "n", "G", "I", "E", "Pi", "H", "evidence_level"]
    with PLATFORM_DATA.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=platform_fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "transition_id": row["id"], "before_state": row["etat_anterieur"],
                "after_state": row["etat_posterieur"], "n": row["dimension_n"],
                "G": row["dimension_G"], "I": row["dimension_I"],
                "E": row["dimension_E"], "Pi": row["dimension_Pi"],
                "H": row["dimension_H"], "evidence_level": row["niveau_de_preuve"],
            })
    dimensions = [f"dimension_{name}" for name in ("n", "G", "I", "E", "Pi", "H")]
    missing = {name: sum(not row[name].strip() for row in rows) for name in dimensions}
    report = {
        "lignes": len(rows),
        "cellules_dimensions": len(rows) * len(dimensions),
        "cellules_renseignees": sum(bool(row[name].strip()) for row in rows for name in dimensions),
        "manquants_par_dimension": missing,
        "nature": "codage qualitatif interprétatif sourcé au niveau du régime",
        "limite": "validation inter-codeurs et sources transition par transition encore requises",
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if not any(missing.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
