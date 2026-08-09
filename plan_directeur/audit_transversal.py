"""Audit transversal — WP-T2 et WP-T4 du plan directeur.

    WP-T2  Généralité réelle. Quelles notions du CODEBOOK produisent
           effectivement une mesure, et dans combien de branches ? Lesquelles
           ne produisent aucune mesure et devraient être retirées ?
    WP-T4  Compression explicative. Combien de concepts et de paramètres le
           cadre demande-t-il, et que rend-il en échange ?

L'audit se calcule sur le dossier lui-même : concepts déclarés dans le
CODEBOOK, mesures effectivement produites par les rapports générés, statuts du
registre des hypothèses. Il ne repose sur aucun jugement extérieur.

    python audit_transversal.py
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
SORTIE = Path(__file__).resolve().parent / "audit_transversal.json"
SEPARATEUR = ";"

# Les notions déclarées par le socle, et le motif qui atteste qu'une mesure
# a été produite quelque part dans le dossier. Le motif est cherché dans les
# fichiers générés, pas dans les documents rédigés : c'est la différence entre
# employer un mot et mesurer une quantité.
NOTIONS = {
    "six dimensions n G I E Pi H": r"regime_num|dimension_n",
    "chaîne ORI-C": r"chaine_oric|Histoire → Architecture",
    "vecteur de persistance Pi": r"persistance",
    "signature de transition S": r"domaine_ferme|ΔF",
    "liens typés de la carte": r"relation",
    "niveaux de preuve": r"niveau_preuve|niveau_de_preuve",
    "mémoire distribuée m(t)": r"memoire|multi_memoires|tau_lent",
    "diagnostic D-H-L": r"contamination_par_estimateur|D_H_L|dhl",
    "Pth et Pacc(T,C,epsilon)": r"Pacc|Pacc_par_horizon",
    "séparation X m A": r"separation_X_m_A|exactitude_par_verite",
    "critère d'altération architecturale": r"altération architecturale|topologie",
    "témoin de complexité égale": r"M1P|complexite_egale|apparie",
    "dépendance au chemin": r"chemin|renversement_temporel",
    "seuil et bifurcation": r"seuil_de_lavage|transcritique",
    "fenêtre longue devant les constantes de temps": r"tau_lent|fenetre",
}

BRANCHES = {
    "socle": ["00_socle"],
    "branche 1 matière": ["01_branche_matiere"],
    "branche 2 système solaire": ["02_branche_systeme_solaire"],
    "branche 3 vivant": ["03_branche_vivant"],
}

# Extensions considérées comme « résultat généré », par opposition aux
# documents rédigés.
GENERES = {".json", ".csv", ".txt"}


def fichiers_generes(sous_dossiers: list[str]) -> list[Path]:
    sortie = []
    for nom in sous_dossiers:
        base = RACINE / nom
        if not base.is_dir():
            continue
        for chemin in base.rglob("*"):
            if chemin.is_file() and chemin.suffix.lower() in GENERES:
                if "__pycache__" in chemin.parts:
                    continue
                sortie.append(chemin)
    return sortie


def wp_t2() -> dict:
    """Quelles notions produisent une mesure, et dans combien de branches ?"""
    index = {}
    for branche, dossiers in BRANCHES.items():
        textes = []
        for chemin in fichiers_generes(dossiers):
            try:
                textes.append(chemin.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                continue
        index[branche] = "\n".join(textes)

    resultat = {}
    for notion, motif in NOTIONS.items():
        expression = re.compile(motif, re.I)
        branches = sorted(b for b, t in index.items() if expression.search(t))
        resultat[notion] = {
            "branches_ou_une_mesure_existe": branches,
            "nombre_de_branches": len(branches),
            "produit_une_mesure": len(branches) > 0,
            "traverse_deux_branches_ou_plus": len(branches) >= 2,
        }

    sans_mesure = sorted(n for n, v in resultat.items()
                         if not v["produit_une_mesure"])
    invariantes = sorted(n for n, v in resultat.items()
                         if v["traverse_deux_branches_ou_plus"])
    return {
        "notions_examinees": len(NOTIONS),
        "par_notion": resultat,
        "notions_sans_aucune_mesure": sans_mesure,
        "notions_traversant_au_moins_deux_branches": invariantes,
        "lecture": (
            "Une notion présente dans une seule branche reste analogique tant "
            "qu'elle n'a pas été instanciée ailleurs. Une notion sans aucune "
            "mesure relève du WP-T2.5 : à retirer ou à rendre mesurable."
        ),
    }


def wp_t4() -> dict:
    """Compression : combien de concepts, combien de paramètres, pour quoi ?"""
    codebook = (RACINE / "00_socle" / "CODEBOOK.md").read_text(encoding="utf-8")
    sections = re.findall(r"^## (\d+[^\n]*)$", codebook, re.M)
    sous_sections = re.findall(r"^### ([^\n]*)$", codebook, re.M)
    codes = re.findall(r"^### `([A-Z]{4})`", codebook, re.M)
    vocabulaire = set(re.findall(r"\b(ENBL|MATR|ENVR|STAB|CATL|CNST|CONT|"
                                 r"DEPG|INCO|DESC|FEED|CLOS|INTG)\b", codebook))

    registre = RACINE / "plan_directeur" / "REGISTRE_HYPOTHESES.csv"
    statuts = {}
    if registre.exists():
        with registre.open(encoding="utf-8-sig", newline="") as flux:
            for ligne in csv.DictReader(flux, delimiter=SEPARATEUR):
                statuts[ligne["statut_final"]] = \
                    statuts.get(ligne["statut_final"], 0) + 1
    total = sum(statuts.values())
    positifs = statuts.get("Établi", 0) + \
        statuts.get("Validé dans le modèle réduit", 0)

    return {
        "sections_du_codebook": len(sections),
        "sous_sections": len(sous_sections),
        "codes_de_relation": len(vocabulaire),
        "lignes_du_codebook": codebook.count("\n"),
        "hypotheses_enregistrees": total,
        "statuts": statuts,
        "hypotheses_a_statut_positif": positifs,
        "rapport_concepts_sur_resultats_positifs": (
            round(len(sections) / positifs, 2) if positifs else None
        ),
        "lecture": (
            "Le rapport entre le nombre de concepts introduits et le nombre de "
            "résultats positifs obtenus est la mesure la plus directe de la "
            "compression explicative demandée au WP-T4.3. Un rapport élevé "
            "signifie que le cadre coûte plus qu'il ne rend, en l'état."
        ),
    }


def main() -> int:
    rapport = {"WP_T2_generalite_reelle": wp_t2(),
               "WP_T4_compression_explicative": wp_t4()}
    SORTIE.write_text(
        json.dumps(rapport, indent=2, ensure_ascii=False),
        encoding="utf-8",
        newline="\n",
    )

    t2 = rapport["WP_T2_generalite_reelle"]
    print("WP-T2 — notions et mesures\n")
    for notion, valeur in t2["par_notion"].items():
        marque = "X" if valeur["produit_une_mesure"] else " "
        print(f"  [{marque}] {notion:44s} {valeur['nombre_de_branches']} branche(s)")
    print(f"\n  sans aucune mesure : {t2['notions_sans_aucune_mesure']}")
    print(f"  traversant ≥ 2 branches : "
          f"{len(t2['notions_traversant_au_moins_deux_branches'])}"
          f"/{t2['notions_examinees']}")

    t4 = rapport["WP_T4_compression_explicative"]
    print("\nWP-T4 — compression")
    print(f"  sections du CODEBOOK          {t4['sections_du_codebook']}")
    print(f"  sous-sections                 {t4['sous_sections']}")
    print(f"  codes de relation             {t4['codes_de_relation']}")
    print(f"  hypothèses enregistrées       {t4['hypotheses_enregistrees']}")
    print(f"  à statut positif              {t4['hypotheses_a_statut_positif']}")
    print(f"  concepts par résultat positif "
          f"{t4['rapport_concepts_sur_resultats_positifs']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
