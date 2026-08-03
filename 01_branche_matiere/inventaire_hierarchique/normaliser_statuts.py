"""Normalise les 58 formulations de statut sur cinq axes independants.

La richesse descriptive du vocabulaire actuel est utile a la lecture, mais elle
empeche toute comparaison automatique. « Confirme en laboratoire, infere
planetairement » et « Confirme » ne disent pas la meme chose et ne peuvent pas
etre traites comme equivalents.

Cinq axes sont separes :

    statut_ontologique    confirme, candidat, hypothetique, non detecte
    mode_obtention        observe, experimente, simule, infere, registre
    milieu_validation     laboratoire, nature, astrophysique
    certitude_historique  directe, reconstruite, plausible
    role_causal           etabli, contributif, possible

La normalisation ne cree pas d'information. Quand une formulation ne dit rien
d'un axe, la valeur est `non_specifie` et non une valeur inventee. C'est
precisement ce que la normalisation revele : deux formulations couvrent 475
entrees sur 550 et ne renseignent aucun des trois derniers axes.

    python normaliser_statuts.py
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ICI = Path(__file__).resolve().parent
TABLES = ICI / "tables"

NS = "non_specifie"
# formulation -> (ontologique, obtention, milieu, historique, role)
AXES = {
 "Confirmé": ("confirme", "observe", NS, NS, NS),
 "Confirmé officiellement": ("confirme", "registre", NS, NS, NS),
 "Confirmée": ("confirme", "observe", NS, NS, NS),
 "Confirmé en laboratoire": ("confirme", "experimente", "laboratoire", NS, NS),
 "Confirmé expérimentalement": ("confirme", "experimente", "laboratoire", NS, NS),
 "Confirmé en 2025": ("confirme", "observe", NS, "directe", NS),
 "Confirmé ou inféré": ("confirme", "mixte", NS, NS, NS),
 "Confirmé spectroscopiquement": ("confirme", "observe", "nature", NS, NS),
 "Confirmé indirectement": ("confirme", "infere", NS, NS, NS),
 "Confirmé indirectement et en laboratoire": ("confirme", "mixte", "laboratoire", NS, NS),
 "Confirmé dans le milieu interstellaire": ("confirme", "observe", "astrophysique", NS, NS),
 "Confirmé hors détection interstellaire incontestable": ("candidat", "observe", "astrophysique", NS, NS),
 "Confirmé dans certains systèmes artificiels": ("confirme", "experimente", "laboratoire", NS, NS),
 "Confirmé expérimentalement comme état collectif": ("confirme", "experimente", "laboratoire", NS, NS),
 "Confirmé en laboratoire, inféré planétairement": ("confirme", "mixte", "laboratoire", "reconstruite", NS),
 "Confirmé en laboratoire, inféré dans la Terre": ("confirme", "mixte", "laboratoire", "reconstruite", NS),
 "Confirmé comme analogue et inféré planétairement": ("candidat", "mixte", "laboratoire", "plausible", NS),
 "Confirmé par modèles et observations": ("confirme", "mixte", "astrophysique", NS, NS),
 "Confirmé sur Terre, recherché ailleurs": ("confirme", "observe", "nature", "directe", NS),
 "Confirmé sur Terre et inféré ailleurs": ("confirme", "mixte", "nature", "reconstruite", NS),
 "Confirmé comme niveau fonctionnel": ("confirme", "observe", "nature", NS, "contributif"),
 "Confirmé par inférence et échantillons": ("confirme", "mixte", "nature", "reconstruite", NS),
 "Inféré": ("candidat", "infere", NS, "reconstruite", NS),
 "Inférée avec forte confiance": ("candidat", "infere", "astrophysique", "reconstruite", NS),
 "Inféré et modélisé": ("candidat", "simule", NS, "reconstruite", NS),
 "Inféré et observé indirectement": ("candidat", "mixte", NS, "reconstruite", NS),
 "Inféré astrophysiquement": ("candidat", "infere", "astrophysique", "reconstruite", NS),
 "Inféré astrophysiquement et fondé théoriquement": ("candidat", "mixte", "astrophysique", "reconstruite", NS),
 "Inféré gravitationnellement": ("candidat", "infere", "astrophysique", "reconstruite", NS),
 "Inférée cosmologiquement": ("candidat", "infere", "astrophysique", "reconstruite", NS),
 "Inféré et contraint": ("candidat", "mixte", NS, "reconstruite", NS),
 "Fortement inféré pour plusieurs objets": ("candidat", "infere", "astrophysique", "reconstruite", NS),
 "Fortement inféré, production statique controversée": ("candidat", "infere", NS, "plausible", "possible"),
 "Fortement soutenu, identification dépend du matériau": ("candidat", "mixte", "laboratoire", NS, NS),
 "Hypothétique": ("hypothetique", "simule", NS, "plausible", "possible"),
 "Non détecté": ("non_detecte", "observe", NS, NS, NS),
 "Non détectée": ("non_detecte", "observe", NS, NS, NS),
 "Non détecté comme matière noire": ("non_detecte", "observe", "astrophysique", NS, NS),
 "Non confirmé comme population dominante": ("candidat", "infere", "astrophysique", NS, "possible"),
 "Non résolue": ("hypothetique", "simule", "astrophysique", NS, NS),
 "Population réelle mais contribution limitée": ("confirme", "observe", "astrophysique", NS, "contributif"),
 "Prédit, candidats non conclusifs": ("hypothetique", "simule", NS, NS, "possible"),
 "Prédit, plusieurs candidats": ("hypothetique", "simule", NS, NS, "possible"),
 "Prédit fortement, indices indirects": ("candidat", "mixte", NS, NS, "possible"),
 "Prédit et partiellement contraint": ("candidat", "mixte", NS, NS, "possible"),
 "Résonance confirmée, structure ouverte": ("confirme", "experimente", "laboratoire", NS, NS),
 "Résonance observée": ("confirme", "observe", "laboratoire", NS, NS),
 "Résonances observées": ("confirme", "observe", "laboratoire", NS, NS),
 "État exotique observé": ("confirme", "observe", "laboratoire", NS, NS),
 "Classe avec candidats confirmés": ("confirme", "observe", "laboratoire", NS, NS),
 "Observé ou estimé selon ligne": ("confirme", "mixte", NS, NS, NS),
 "Détection rapportée en 2026": ("candidat", "observe", NS, "directe", NS),
 "Détection rapportée en juillet 2026": ("candidat", "observe", NS, "directe", NS),
 "Cadre effectif soutenu, statut de phase discuté": ("candidat", "simule", "laboratoire", NS, NS),
 "Concept opératoire": ("concept", "definition", NS, "sans_objet", "sans_objet"),
 "Catalogue ouvert": ("registre_ouvert", "registre", NS, "sans_objet", "sans_objet"),
 "Registre officiel ouvert": ("registre_ouvert", "registre", NS, "sans_objet", "sans_objet"),
 "352 espèces recensées au 16 juillet 2026": ("registre_ouvert", "registre", "astrophysique", "sans_objet", "sans_objet"),
}
CHAMPS = ["ID", "Entité", "type_registre", "statut_original",
          "statut_ontologique", "mode_obtention", "milieu_validation",
          "certitude_historique", "role_causal"]


def main() -> int:
    with (TABLES / "01_Index_maitre.csv").open(encoding="utf-8", newline="") as f:
        index = list(csv.DictReader(f, delimiter=";"))

    manquants = sorted({r["Statut"].strip() for r in index} - set(AXES))
    if manquants:
        raise SystemExit(f"formulations non appariees : {manquants}")

    lignes = []
    for r in index:
        o, m, mi, h, c = AXES[r["Statut"].strip()]
        lignes.append({
            "ID": r["ID"], "Entité": r["Entité"],
            "type_registre": r["type_registre"],
            "statut_original": r["Statut"].strip(),
            "statut_ontologique": o, "mode_obtention": m,
            "milieu_validation": mi, "certitude_historique": h,
            "role_causal": c,
        })
    cible = TABLES / "19_Statuts_normalises.csv"
    with cible.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CHAMPS, delimiter=";")
        w.writeheader(); w.writerows(lignes)

    axes = {a: dict(Counter(l[a] for l in lignes)) for a in CHAMPS[4:]}
    non_specifie = {a: sum(1 for l in lignes if l[a] == NS) for a in CHAMPS[4:]}
    rapport = {
        "formulations_distinctes_avant": len({r["Statut"].strip() for r in index}),
        "entrees_normalisees": len(lignes),
        "repartition_par_axe": axes,
        "entrees_sans_information_sur_l_axe": non_specifie,
        "constat": (
            "Deux formulations, « Confirme » et « Confirme officiellement », "
            f"couvrent {sum(1 for l in lignes if l['statut_original'].startswith('Confirmé') and l['milieu_validation'] == NS)} "
            "entrees et ne renseignent ni le milieu de validation, ni la "
            "certitude historique, ni le role causal. La normalisation ne cree "
            "pas cette information : elle rend visible qu'elle manque."),
        "portee": ("appariement declare a la main, une ligne par formulation. "
                   "Un statut non apparie fait echouer le script, pour qu'une "
                   "formulation nouvelle ne soit jamais silencieusement "
                   "rattachee a une categorie voisine."),
    }
    (ICI / "statuts_normalises.json").write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(rapport, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
