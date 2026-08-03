"""Confronte l'inventaire de ce qui existe à la généalogie de ce qu'on sait produire.

L'inventaire hiérarchique n'est pas un catalogue de plus. C'est un instrument de
détection : il recense ce qui existe dans l'univers connu, la généalogie recense
ce dont on a déclaré l'origine. La différence entre les deux est la liste de
travail.

Trois confrontations sont menées.

A. Les 118 éléments chimiques contre les voies de nucléosynthèse déclarées.
B. Les 52 transformations recensées contre les catégories de mécanisme employées.
C. Les 46 réservoirs contre les nœuds et produits de la généalogie.

L'appariement transformation → mécanisme est **déclaré à la main** ci-dessous et
non deviné par mots-clés. Un appariement automatique produisait des manques
inexistants : `polymérisation` et `altération chimique` étaient signalées
absentes alors que la généalogie les porte.

    python detecter_manques.py
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ICI = Path(__file__).resolve().parent
TABLES = ICI / "tables"
DOSSIER = ICI.parents[1]
ARBRE = DOSSIER / "00_socle" / "genealogie" / "arbre_genealogique.csv"

# Appariement établi à la main entre une transformation du catalogue et la
# catégorie de mécanisme qui l'implémente dans la généalogie. `None` signifie
# qu'aucune transition ne la porte : c'est un manque, pas un oubli de saisie.
APPARIEMENT = {
    # Échelle particulaire
    "Création de paire": None,
    "Annihilation matière-antimatière": None,
    "Désintégration faible": None,
    "Interaction forte": "confinement",
    "Hadronisation": "confinement",
    "Diffusion électromagnétique": None,
    # Échelle nucléaire
    "Fusion nucléaire": "fusion_nucleaire",
    "Fission nucléaire": None,
    "Capture neutronique": "capture_neutronique",
    "Capture protonique": "fusion_nucleaire",
    "Capture alpha": "fusion_nucleaire",
    "Désintégration alpha": None,
    "Désintégration bêta moins": None,
    "Désintégration bêta plus": None,
    "Capture électronique": None,
    "Transition isomérique": None,
    # Échelle atomique
    "Ionisation": None,
    "Attachement électronique": None,
    "Recombinaison": "recombinaison_electronique",
    "Excitation électronique": None,
    # Échelle chimique
    "Formation de liaison covalente": "chimie_phase_gazeuse",
    "Formation de liaison ionique": None,
    "Oxydoréduction": None,
    "Acide-base": None,
    "Polymérisation": "polymerisation",
    "Hydrolyse": "alteration_aqueuse",
    "Photolyse": "photolyse",
    "Catalyse de surface": "chimie_de_surface",
    # Échelle de phase
    "Fusion": None,
    "Cristallisation": "cristallisation",
    "Vaporisation": None,
    "Condensation": "condensation_thermique",
    "Sublimation": None,
    "Dépôt": None,
    "Transition vitreuse": None,
    # Échelle géologique
    "Altération chimique": "alteration_aqueuse",
    "Métamorphisme": None,
    "Fusion partielle": "chauffage_radiogenique",
    "Différenciation planétaire": "segregation_densite",
    # Échelle biologique
    "Assimilation": None,
    "Respiration cellulaire": None,
    "Photosynthèse": None,
    "Décomposition": None,
    "Biominéralisation": None,
    # Échelle astrophysique
    "Accrétion": "collision_adhesion",
    "Éjection et vent": None,
    "Explosion de supernova": None,
    "Formation de poussières": "condensation_thermique",
    # Échelle ORI-C
    "Accessibilisation": None,
    "Mobilisation": None,
    "Incorporation opératoire": None,
    "Séquestration": None,
}

# Éléments dont la généalogie déclare explicitement la production.
ELEMENTS_DECLARES = {
    "H": "GA-002/003", "He": "GA-003", "Li": "GA-003", "C": "GA-007",
    "O": "GA-008", "Ne": "GA-008", "Mg": "GA-008", "Si": "GA-008",
    "S": "GA-008", "Fe": "GA-009", "Ni": "GA-009", "Co": "GA-009",
    "Al": "GA-012",
}
# Voies produisant des ensembles non résolus en éléments individuels.
VOIES_EN_BLOC = {
    "GA-010": "éléments lourds voie s",
    "GA-011": "actinides",
}


def lire(chemin, delim=";"):
    with Path(chemin).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=delim))


def main() -> int:
    arbre = lire(ARBRE)
    categories = {x["mecanisme_categorie"] for x in arbre}
    corpus = " ".join(x["produit"] + " " + x["parents_materiels"]
                      for x in arbre).lower()

    # --- A. Éléments -------------------------------------------------------
    elements = lire(TABLES / "06_Elements_118.csv")
    naturels = [e for e in elements
                if "synth" not in (e["Occurrence"] or "").lower()]
    sans_origine = [e for e in naturels if e["Symbole"] not in ELEMENTS_DECLARES]
    a = {
        "elements_totaux": len(elements),
        "elements_naturels": len(naturels),
        "elements_a_origine_declaree": len(ELEMENTS_DECLARES),
        "elements_naturels_sans_origine_resolue": len(sans_origine),
        "voies_en_bloc_non_resolues": VOIES_EN_BLOC,
        "lecture": ("Les éléments manquants ne sont pas absents de l'univers : "
                    "ils sont absents de la généalogie, ou noyés dans une voie "
                    "déclarée en bloc. Résoudre les deux voies en bloc couvre "
                    "l'essentiel du déficit."),
    }

    # --- B. Transformations ------------------------------------------------
    transformations = lire(TABLES / "13_Transformations.csv")
    inconnues = [t["Transformation"] for t in transformations
                 if t["Transformation"] not in APPARIEMENT]
    manques = defaultdict(list)
    couvertes = 0
    for t in transformations:
        cible = APPARIEMENT.get(t["Transformation"], None)
        if cible and cible in categories:
            couvertes += 1
        else:
            manques[t["Échelle"]].append(t["Transformation"])
    b = {
        "transformations_recensees": len(transformations),
        "transformations_couvertes": couvertes,
        "transformations_sans_mecanisme": {k: v for k, v in manques.items()},
        "transformations_non_appariees": inconnues,
    }

    # --- C. Réservoirs -----------------------------------------------------
    reservoirs = lire(TABLES / "10_Reservoirs.csv")
    absents = [r["Réservoir"] for r in reservoirs
               if not any(m in corpus for m in
                          [w.lower() for w in r["Réservoir"].split() if len(w) > 5])]
    c = {
        "reservoirs_recenses": len(reservoirs),
        "reservoirs_sans_correspondance": len(absents),
        "par_echelle": dict(Counter(r["Échelle"] for r in reservoirs)),
        "avertissement": ("appariement lexical, indicatif seulement : un "
                          "réservoir peut être couvert sous un autre nom"),
    }

    rapport = {
        "A_elements": a,
        "B_transformations": b,
        "C_reservoirs": c,
        "priorite": [
            "Les quatre transformations de l'échelle ORI-C — accessibilisation, "
            "mobilisation, incorporation opératoire, séquestration — sont "
            "recensées comme processus mais aucune n'est instanciée comme "
            "transition dans la généalogie du programme.",
            "Les cinq transformations biologiques sont absentes : assimilation, "
            "respiration, photosynthèse, décomposition, biominéralisation.",
            "Six transformations nucléaires manquent, toutes de la famille des "
            "décroissances et captures qui changent l'élément après sa "
            "formation : fission, alpha, bêta moins, bêta plus, capture "
            "électronique, transition isomérique.",
            "Deux voies produisent des ensembles non résolus, la voie s et la "
            "voie r ; les résoudre en éléments couvrirait l'essentiel du "
            "déficit des 118.",
        ],
        "portee": ("Cette confrontation mesure une couverture de représentation, "
                   "pas une lacune de la physique. Un manque signale ce que la "
                   "généalogie ne sait pas encore produire, pas ce que la nature "
                   "ne produit pas."),
    }
    (ICI / "manques_detectes.json").write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(rapport, ensure_ascii=False, indent=2))
    return 1 if inconnues else 0


if __name__ == "__main__":
    raise SystemExit(main())
