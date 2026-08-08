#!/usr/bin/env python3
"""Classe chaque fichier brut : entrée d'extraction, documentaire, calcul,
non exploitable. Écrit TRI_DEPOT.json.

    python trier_pour_le_depot.py
"""
from __future__ import annotations

import argparse
import json
import zipfile
from collections import Counter
from pathlib import Path

ICI = Path(__file__).resolve().parent
SOURCES = ICI / "SOURCES.json"

TABULAIRE = {".csv", ".txt", ".dat", ".tsv", ".xlsx", ".xls", ".xlsm", ".asc"}
INSTRUMENT = {".ctf", ".ang", ".osc", ".xrdml", ".oim"}
IMAGE = {".tif", ".tiff", ".png", ".jpg", ".jpeg", ".bmp", ".emf"}
DOCUMENT = {".pdf", ".docx", ".md", ".rtf"}
CALCUL = {".cif", ".xyz", ".vasp", ".outcar", ".poscar", ".chgcar", ".contcar"}
ARCHIVE = {".zip", ".rar", ".7z", ".gz", ".tar"}


def classer(nom: str, dans_dft: bool) -> tuple[str, str]:
    suffixe = Path(nom).suffix.lower()
    if dans_dft or suffixe in CALCUL:
        return "calcul", "simulation, jamais une preuve empirique"
    if suffixe in ARCHIVE:
        return "non_exploitable", "archive, contenu classé séparément"
    if suffixe in IMAGE:
        return "documentaire", "image d'instrument"
    if suffixe in DOCUMENT:
        return "documentaire", "document de lecture"
    if suffixe in TABULAIRE:
        return "entree_extraction", "tabulaire, lisible directement"
    if suffixe in INSTRUMENT:
        return "entree_extraction", "format d'instrument, conversion requise"
    return "non_exploitable", f"format {suffixe or 'sans extension'} non reconnu"


def entrees_de(chemin: Path) -> list[tuple[str, int]]:
    suffixe = chemin.suffix.lower()
    if suffixe == ".zip":
        try:
            with zipfile.ZipFile(chemin) as archive:
                return [(f"{chemin.name}/{i.filename}", i.file_size)
                        for i in archive.infolist()
                        if not i.is_dir() and "__MACOSX" not in i.filename]
        except (zipfile.BadZipFile, OSError):
            return [(chemin.name, chemin.stat().st_size)]
    if suffixe == ".rar":
        try:
            import rarfile
            with rarfile.RarFile(chemin) as archive:
                return [(f"{chemin.name}/{i.filename}", i.file_size)
                        for i in archive.infolist() if not i.isdir()]
        except Exception:
            return [(chemin.name, chemin.stat().st_size)]
    return [(chemin.name, chemin.stat().st_size)]


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()

    config = json.loads(SOURCES.read_text(encoding="utf-8"))
    racine = (ICI / config["racine_locale"]).resolve()

    par_source: dict[str, dict] = {}
    total = Counter()
    octets = Counter()

    for source in config["sources"]:
        cle = source["cle"]
        brut = racine / cle / "raw"
        if not brut.is_dir():
            continue
        compte, poids = Counter(), Counter()
        for fichier in sorted(p for p in brut.rglob("*") if p.is_file()):
            for nom, taille in entrees_de(fichier):
                classe, _ = classer(nom, "dft" in nom.lower())
                compte[classe] += 1
                poids[classe] += taille
                total[classe] += 1
                octets[classe] += taille
        par_source[cle] = {"famille": source.get("famille"),
                           "compte": dict(compte), "octets": dict(poids)}

    entete = (f"{'source':<34}{'entrées':>9}{'doc':>7}{'calcul':>8}{'autres':>8}"
              f"{'volume lisible':>17}")
    print("Le dépôt ne reçoit aucun fichier copié depuis raw/.")
    print("Il reçoit la table extraite par source, plus la provenance de tout.")
    print()
    print(entete)
    print("-" * len(entete))
    for cle, rapport in par_source.items():
        c, o = rapport["compte"], rapport["octets"]
        print(f"{cle:<34}{c.get('entree_extraction', 0):>9}{c.get('documentaire', 0):>7}"
              f"{c.get('calcul', 0):>8}{c.get('non_exploitable', 0):>8}"
              f"{o.get('entree_extraction', 0) / 1e6:>13.1f} Mo")
    print()
    print(f"{'TOTAL':<34}{total['entree_extraction']:>9}{total['documentaire']:>7}"
          f"{total['calcul']:>8}{total['non_exploitable']:>8}"
          f"{octets['entree_extraction'] / 1e6:>13.1f} Mo")

    print()
    print(f"Entrées lisibles par l'extracteur : {total['entree_extraction']} fichiers, "
          f"{octets['entree_extraction'] / 1e9:.2f} Go — restent en local.")
    print(f"Écartés d'office : {total['documentaire']} documentaires, "
          f"{total['calcul']} de calcul, {total['non_exploitable']} non exploitables.")
    print()
    print("Ce qui ira au dépôt : une table dérivée par source admise, quelques")
    print("dizaines à quelques centaines de kilooctets chacune, plus PROVENANCE.json.")

    sortie = ICI / "TRI_DEPOT.json"
    with sortie.open("w", encoding="utf-8", newline="") as flux:
        flux.write(json.dumps({
            "regle": ("le dépôt ne reçoit aucun fichier copié depuis raw/ ; il reçoit "
                      "la table extraite par source et la provenance complète"),
            "critere": "l'origine du fichier, pas sa taille",
            "classes": {
                "entree_extraction": "lisible par l'extracteur, reste en local",
                "documentaire": "PDF et images, reste en local",
                "calcul": "simulation, reste en local et n'est jamais une preuve",
                "non_exploitable": "archive ou format non reconnu",
            },
            "par_source": par_source,
            "totaux": {"compte": dict(total), "octets": dict(octets)},
        }, ensure_ascii=False, indent=2) + "\n")
    print(f"écrit : {sortie.relative_to(ICI.parents[1]).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
