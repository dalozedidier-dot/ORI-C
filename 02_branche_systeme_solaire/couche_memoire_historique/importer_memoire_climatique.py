#!/usr/bin/env python3
"""Table canonique pour le test de mémoire climatique : Bintanja + insolation Berger.

Le verrou de la branche 2 est que GISTEMP donne une température mais ni forçage
ni compartiment de mémoire. Ce script construit la table qui porte les quatre
variables simultanément, à partir de deux sources publiques.

    python 02_branche_systeme_solaire/couche_memoire_historique/importer_memoire_climatique.py

Sources, téléchargées séparément dans `donnees_brutes/` :

  bintanja2005.txt   NOAA Paleoclimatology, contribution 2011-118
                     Bintanja, van de Wal & Oerlemans 2005, doi 10.1038/nature03975
                     Température, niveau marin et volumes de glace sur 1,07 Ma

  orbit91            NOAA Orbital Variations, Berger & Loutre 1991
                     Excentricité, obliquité, précession et insolation 65°N juillet
                     sur 5 Ma au pas de 1 ka

**Aucune imputation, aucune interpolation.** La jointure est exacte sur l'âge :
seules les lignes dont l'âge existe dans les deux sources sont conservées. Une
jointure au plus proche voisin, même à tolérance serrée, propagerait une valeur
d'insolation sur dix lignes de Bintanja et fabriquerait une corrélation.

**Statut épistémique, à lire avant tout usage.** Bintanja n'est pas une mesure
directe : c'est une reconstruction obtenue par modélisation inverse du δ18O
benthique de LR04. Elle relève donc de `mixed_observation_and_external_model_output`
au sens de `EMPIRICAL_POLICY.json`, et non d'une observation primaire. Cette
table ne peut pas servir de preuve empirique confirmatoire sans qu'un protocole
ciblé déclare explicitement ce statut et en tire les conséquences.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ICI = Path(__file__).resolve().parent
BRUT = ICI / "data" / "raw"
BINTANJA = BRUT / "bintanja2005.txt"
ORBIT = BRUT / "orbit91"
SORTIE = ICI / "data" / "processed" / "memoire_climatique_bintanja_insolation.csv"
NOTICE = ICI / "data" / "processed" / "MEMOIRE_CLIMATIQUE_SOURCE.json"

# Colonnes réellement présentes dans bintanja2005.txt, d'après son en-tête.
# Le fichier en compte dix, pas cinq : les colonnes 9 et 10 portent des valeurs
# manquantes déclarées, pour les périodes sans glace continentale significative.
COLONNES_BINTANJA = [
    "age_ka_bp",
    "temp_anomaly_C",
    "sea_level_m",
    "ice_volume_eurasia_sle",
    "ice_volume_na_sle",
    "isotope_total",
    "isotope_ice_contribution",
    "isotope_deepsea_contribution",
    "isotope_mean_eurasia",
    "isotope_mean_na",
]
COLONNES_ORBIT = [
    "age_ka",
    "eccentricity",
    "omega_deg",
    "obliquity_deg",
    "precession",
    "insolation_65N_jul_Wm2",
    "insolation_65S_jan_Wm2",
    "insolation_15N_jul_Wm2",
    "insolation_15S_jan_Wm2",
]


def empreinte(chemin: Path) -> str:
    return hashlib.sha256(chemin.read_bytes()).hexdigest()


def charger_bintanja(chemin: Path) -> pd.DataFrame:
    cadre = pd.read_csv(
        chemin, sep=r"\s+", header=None, names=COLONNES_BINTANJA,
        skiprows=102, engine="python", on_bad_lines="skip",
    )
    cadre = cadre[pd.to_numeric(cadre["age_ka_bp"], errors="coerce").notna()]
    for colonne in COLONNES_BINTANJA:
        cadre[colonne] = pd.to_numeric(cadre[colonne], errors="coerce")
    cadre["ice_volume_total_sle"] = (
        cadre["ice_volume_eurasia_sle"] + cadre["ice_volume_na_sle"]
    )
    return cadre.sort_values("age_ka_bp").reset_index(drop=True)


def charger_orbit(chemin: Path) -> pd.DataFrame:
    cadre = pd.read_csv(
        chemin, sep=r"\s+", header=None, names=COLONNES_ORBIT,
        skiprows=3, engine="python", on_bad_lines="skip",
    )
    cadre = cadre[pd.to_numeric(cadre["age_ka"], errors="coerce").notna()]
    for colonne in COLONNES_ORBIT:
        cadre[colonne] = pd.to_numeric(cadre[colonne], errors="coerce")
    # orbit91 compte le passé en négatif ; on ramène à un âge positif en ka BP.
    cadre["age_ka_bp"] = -cadre["age_ka"]
    return cadre.sort_values("age_ka_bp").reset_index(drop=True)


def main() -> int:
    if not BINTANJA.exists() or not ORBIT.exists():
        print("Sources brutes absentes. Les télécharger d'abord :")
        print(f"  {BRUT}/bintanja2005.txt")
        print("    https://www.ncei.noaa.gov/pub/data/paleo/contributions_by_author/bintanja2005/bintanja2005.txt")
        print(f"  {BRUT}/orbit91")
        print("    https://www.ncei.noaa.gov/pub/data/paleo/climate_forcing/orbital_variations/insolation/orbit91")
        return 2

    bintanja = charger_bintanja(BINTANJA)
    orbit = charger_orbit(ORBIT)
    print(f"Bintanja : {len(bintanja)} lignes, {bintanja['age_ka_bp'].min():g} à "
          f"{bintanja['age_ka_bp'].max():g} ka BP")
    print(f"orbit91  : {len(orbit)} lignes, {orbit['age_ka_bp'].min():g} à "
          f"{orbit['age_ka_bp'].max():g} ka BP")

    # Jointure EXACTE. Pas de merge_asof, pas de tolérance, pas de propagation.
    bintanja["cle"] = bintanja["age_ka_bp"].astype(float).round(3)
    orbit["cle"] = orbit["age_ka_bp"].astype(float).round(3)
    fusion = bintanja.merge(
        orbit[["cle", "eccentricity", "obliquity_deg", "precession",
               "insolation_65N_jul_Wm2"]],
        on="cle", how="inner",
    ).drop(columns=["cle"])

    colonnes = [
        "age_ka_bp", "temp_anomaly_C", "sea_level_m",
        "ice_volume_eurasia_sle", "ice_volume_na_sle", "ice_volume_total_sle",
        "insolation_65N_jul_Wm2", "eccentricity", "obliquity_deg", "precession",
        "isotope_total",
    ]
    final = fusion[colonnes].sort_values("age_ka_bp").reset_index(drop=True)

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    final.to_csv(SORTIE, index=False, lineterminator="\n")

    obligatoires = ["age_ka_bp", "temp_anomaly_C", "insolation_65N_jul_Wm2",
                    "ice_volume_total_sle"]
    complet = {c: int(final[c].notna().sum()) for c in obligatoires}
    notice = {
        "table": str(SORTIE.relative_to(ICI.parents[1])).replace("\\", "/"),
        "lignes": len(final),
        "age_ka_bp": [float(final["age_ka_bp"].min()), float(final["age_ka_bp"].max())],
        "pas_ka": 1.0,
        "jointure": "exacte sur l'âge, aucune tolérance, aucune interpolation",
        "variables_obligatoires_completes": complet,
        "sources": [
            {"fichier": "bintanja2005.txt", "sha256": empreinte(BINTANJA),
             "octets": BINTANJA.stat().st_size,
             "reference": "Bintanja, van de Wal & Oerlemans 2005, Nature 437, 125-128",
             "doi": "10.1038/nature03975",
             "data_kind": "mixed_observation_and_external_model_output",
             "limite": "Reconstruction par modélisation inverse du delta18O benthique de LR04. Ce n'est pas une mesure directe."},
            {"fichier": "orbit91", "sha256": empreinte(ORBIT),
             "octets": ORBIT.stat().st_size,
             "reference": "Berger & Loutre 1991, Quaternary Science Reviews 10, 297-317",
             "data_kind": "ephemeris_model_input",
             "limite": "Solution astronomique calculée, non mesurée."},
        ],
        "avertissement": (
            "Les deux sources sont des produits de modèle, pas des observations "
            "primaires. Cette table rend le test de mémoire climatique exécutable, "
            "elle ne le rend pas confirmatoire. Tout protocole qui l'utilise doit "
            "déclarer ce statut."
        ),
    }
    with NOTICE.open("w", encoding="utf-8", newline="") as flux:
        flux.write(json.dumps(notice, ensure_ascii=False, indent=2) + "\n")

    print()
    print(f"Table écrite : {len(final)} lignes, {final['age_ka_bp'].min():g} à "
          f"{final['age_ka_bp'].max():g} ka BP, pas 1 ka")
    print("Complétude des quatre variables obligatoires :")
    for nom, nombre in complet.items():
        etat = "complète" if nombre == len(final) else f"{len(final) - nombre} trous"
        print(f"  {nom:<28} {nombre:>6} / {len(final)}   {etat}")
    print()
    print(f"  {SORTIE.relative_to(ICI.parents[1])}")
    print(f"  {NOTICE.relative_to(ICI.parents[1])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
