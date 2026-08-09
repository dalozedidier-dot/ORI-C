#!/usr/bin/env python3
"""Télécharge les sources de SOURCES.json et écrit PROVENANCE.json.

Consigne nom d'origine, URL, taille, DOI, version, licence et SHA-256
recalculé. Un appel partiel complète la provenance sans la remplacer.

    python telecharger_toutes_sources.py [--cle CLE] [--plan]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ICI = Path(__file__).resolve().parent
SOURCES = ICI / "SOURCES.json"
API = "https://zenodo.org/api/records/{}"
BLOC = 1 << 20
TENTATIVES = 3

# Un enregistrement Zenodo mêle souvent quelques tables exploitables et des
# gigaoctets d'images ou de sorties de simulation. L'API donne la liste des
# fichiers avant tout téléchargement : autant s'en servir. Le zircon annonce
# 8,2 Go dont un seul fichier de 0,1 Mo est lu par un test.
MOTIFS_ECARTES = (
    "rawdata", "raw_data", "_raw", "hexrd", "tiff", "images",
    "micrograph", "dft_", "_dft", "ebsd_maps", "sem_", "tem_",
)
EXTENSIONS_ECARTEES = {".tif", ".tiff", ".png", ".jpg", ".jpeg", ".bmp", ".emf",
                       ".mp4", ".avi", ".cif", ".vasp", ".poscar"}

# Au-delà de ce seuil, une archive n'est plus rapatriée : son index est lu à
# distance et seuls les membres exploitables sont extraits par plage d'octets.
SEUIL_ARCHIVE_DISTANTE = 50 << 20
EXTENSIONS_UTILES = {".csv", ".txt", ".dat", ".tsv", ".asc", ".xlsx", ".xls",
                     ".xlsm", ".ctf", ".ang", ".osc", ".xrdml", ".oim", ".md"}
TAILLE_MEMBRE_MAXIMALE = 50 << 20


def membre_utile(nom: str, taille: int, motifs: tuple) -> bool:
    if Path(nom).suffix.lower() not in EXTENSIONS_UTILES:
        return False
    if taille > TAILLE_MEMBRE_MAXIMALE:
        return False
    minuscule = nom.lower()
    return not any(motif in minuscule for motif in motifs)


def moissonner_archive(url: str, destination: Path, motifs: tuple) -> tuple[int, int, int]:
    """Extrait les membres utiles d'une archive distante. (membres, octets, total)."""
    from zip_distant import membres, extraire
    liste = membres(url)
    total = sum(taille for _, taille, _ in liste)
    voulus = [nom for nom, taille, _ in liste if membre_utile(nom, taille, motifs)]
    if not voulus:
        return 0, 0, total
    contenus = extraire(url, voulus)
    octets = 0
    for nom, donnees in contenus.items():
        cible = destination / nom
        cible.parent.mkdir(parents=True, exist_ok=True)
        cible.write_bytes(donnees)
        octets += len(donnees)
    return len(contenus), octets, total


def a_ecarter(nom: str, taille: int, motifs: tuple) -> str | None:
    """Motif d'exclusion, ou None si le fichier doit être téléchargé."""
    minuscule = nom.lower()
    if Path(nom).suffix.lower() in EXTENSIONS_ECARTEES:
        return f"extension {Path(nom).suffix.lower()}"
    for motif in motifs:
        if motif in minuscule:
            return f"nom contenant {motif!r}"
    return None


def racine_donnees(config: dict) -> Path:
    return (ICI / config["racine_locale"]).resolve()


def interroger(record: str) -> dict | None:
    for essai in range(TENTATIVES):
        try:
            with urllib.request.urlopen(API.format(record), timeout=60) as flux:
                return json.loads(flux.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            if essai == TENTATIVES - 1:
                return None
            time.sleep(2 * (essai + 1))
    return None


def empreinte(chemin: Path) -> str:
    valeur = hashlib.sha256()
    with chemin.open("rb") as flux:
        for bloc in iter(lambda: flux.read(BLOC), b""):
            valeur.update(bloc)
    return valeur.hexdigest()


def telecharger(url: str, destination: Path, taille_attendue: int) -> tuple[bool, str]:
    """Télécharge en flux, avec reprise par plage HTTP.

    La taille reçue est comparée à la taille annoncée à chaque tentative ; une
    divergence est un échec.
    """
    if destination.exists() and destination.stat().st_size == taille_attendue:
        return True, "déjà présent, taille conforme"
    destination.parent.mkdir(parents=True, exist_ok=True)
    partiel = destination.with_suffix(destination.suffix + ".partiel")

    for essai in range(TENTATIVES):
        depuis = partiel.stat().st_size if partiel.exists() else 0
        if depuis >= taille_attendue > 0:
            partiel.unlink(missing_ok=True)
            depuis = 0
        requete = urllib.request.Request(url)
        if depuis:
            requete.add_header("Range", f"bytes={depuis}-")
        try:
            with urllib.request.urlopen(requete, timeout=300) as flux:
                reprise = flux.status == 206
                mode = "ab" if (depuis and reprise) else "wb"
                if depuis and not reprise:
                    depuis = 0  # le serveur ignore Range : on repart du début
                with partiel.open(mode) as sortie:
                    while True:
                        bloc = flux.read(BLOC)
                        if not bloc:
                            break
                        sortie.write(bloc)
        except (urllib.error.URLError, TimeoutError, OSError) as erreur:
            if essai == TENTATIVES - 1:
                return False, f"échec après {TENTATIVES} tentatives : {erreur}"
            time.sleep(3 * (essai + 1))
            continue

        recu = partiel.stat().st_size if partiel.exists() else 0
        if taille_attendue and recu != taille_attendue:
            manque = taille_attendue - recu
            if essai == TENTATIVES - 1:
                return False, (f"échec : {recu} octets reçus sur {taille_attendue}, "
                               f"il manque {manque / 1e6:.1f} Mo")
            print(f"      reprise : {recu / 1e6:.1f} Mo sur "
                  f"{taille_attendue / 1e6:.1f} Mo, il manque {manque / 1e6:.1f} Mo")
            time.sleep(3 * (essai + 1))
            continue

        partiel.replace(destination)
        return True, "téléchargé"
    return False, "échec"


def traiter(source: dict, racine: Path, plan_seulement: bool,
            tout: bool = False) -> dict:
    cle, record = source["cle"], source["record"]
    donnees = interroger(record)
    if donnees is None or "metadata" not in donnees:
        print(f"  {cle:<28} enregistrement introuvable ({record})")
        return {"cle": cle, "record": record, "statut": "introuvable", "fichiers": []}

    meta = donnees["metadata"]
    licence = (meta.get("license") or {}).get("id", "non déclarée")
    fichiers_distants = donnees.get("files", [])
    total = sum(f.get("size", 0) for f in fichiers_distants)

    print(f"  {cle:<28} {len(fichiers_distants):>2} fichiers  {total / 1e6:>8.1f} Mo  "
          f"{licence}  {donnees.get('doi')}")

    motifs = MOTIFS_ECARTES + tuple(source.get("ignorer", ()))
    entrees = []
    ecartes = ecartes_octets = 0
    for distant in fichiers_distants:
        nom = distant.get("key")
        taille = distant.get("size", 0)
        raison = None if tout else a_ecarter(nom, taille, motifs)
        if raison:
            ecartes += 1
            ecartes_octets += taille
            entrees.append({"nom_original": nom, "taille_annoncee": taille,
                            "statut": f"écarté avant téléchargement : {raison}"})
            continue
        url = (distant.get("links") or {}).get("self") or (
            f"https://zenodo.org/records/{record}/files/{nom}?download=1")
        destination = racine / cle / "raw" / nom
        entree = {
            "nom_original": nom,
            "chemin_local": str(destination.relative_to(racine)).replace("\\", "/"),
            "url": url,
            "taille_annoncee": taille,
            "checksum_annonce": distant.get("checksum"),
        }
        if plan_seulement:
            entree["statut"] = "non téléchargé (mode plan)"
            entrees.append(entree)
            continue

        if (not tout and nom.lower().endswith(".zip")
                and taille > SEUIL_ARCHIVE_DISTANTE):
            try:
                n, octets, decompresse = moissonner_archive(
                    url, racine / cle / "exploitable", motifs)
                entree["statut"] = (f"archive lue à distance : {n} membre(s) "
                                    f"extrait(s), {octets / 1e6:.1f} Mo")
                entree["archive_distante"] = True
                entree["octets_evites"] = max(taille - octets, 0)
                ecartes_octets += entree["octets_evites"]
                print(f"      distant  {n:>4} membre(s), {octets / 1e6:>8.1f} Mo "
                      f"sur {taille / 1e6:.1f} Mo annoncés — {nom[:44]}")
                entrees.append(entree)
                continue
            except Exception as erreur:
                print(f"      lecture distante impossible ({type(erreur).__name__}), "
                      f"rapatriement complet")

        reussi, detail = telecharger(url, destination, taille)
        entree["statut"] = detail
        if reussi and destination.exists():
            entree["taille_recue"] = destination.stat().st_size
            entree["sha256_recalcule"] = empreinte(destination)
            entree["taille_conforme"] = entree["taille_recue"] == taille
            annonce = (distant.get("checksum") or "")
            if annonce.startswith("md5:"):
                md5 = hashlib.md5()
                with destination.open("rb") as flux:
                    for bloc in iter(lambda: flux.read(BLOC), b""):
                        md5.update(bloc)
                entree["md5_conforme"] = md5.hexdigest() == annonce[4:]
            marque = "ok " if entree["taille_conforme"] else "TAILLE DIVERGENTE "
            print(f"      {marque}{entree['taille_recue'] / 1e6:>8.1f} Mo  {nom[:58]}")
        else:
            print(f"      ÉCHEC  {nom[:58]}  {detail}")
        entrees.append(entree)

    if ecartes:
        print(f"      {ecartes} fichier(s) écarté(s) sans téléchargement, "
              f"{ecartes_octets / 1e9:.2f} Go évités")

    return {
        "cle": cle,
        "record": record,
        "fichiers_ecartes": ecartes,
        "octets_evites": ecartes_octets,
        "doi": donnees.get("doi"),
        "titre": meta.get("title"),
        "version": meta.get("version") or donnees.get("revision"),
        "date_publication": meta.get("publication_date"),
        "licence": licence,
        "famille_declaree": source.get("famille"),
        "role_declare": source.get("role"),
        "taille_totale_annoncee": total,
        "statut": "traité",
        "fichiers": entrees,
    }


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--cle", action="append",
                           help="ne traiter que ces clés de SOURCES.json")
    analyseur.add_argument("--plan", action="store_true",
                           help="n'écrit aucun octet, montre seulement le volume")
    analyseur.add_argument("--tout", action="store_true",
                           help="télécharge aussi les images et sorties de simulation")
    arguments = analyseur.parse_args()

    config = json.loads(SOURCES.read_text(encoding="utf-8"))
    racine = racine_donnees(config)
    sources = config["sources"]
    if arguments.cle:
        voulues = set(arguments.cle)
        sources = [s for s in sources if s["cle"] in voulues]
        inconnues = voulues - {s["cle"] for s in config["sources"]}
        if inconnues:
            print(f"Clés inconnues : {sorted(inconnues)}")
            return 2

    print(f"Racine des données : {racine}")
    print(f"{len(sources)} source(s). raw/ n'est jamais transformé.")
    print()

    rapports = [traiter(s, racine, arguments.plan, arguments.tout) for s in sources]

    evites = sum(r.get("octets_evites", 0) for r in rapports)
    volume = sum(r.get("taille_totale_annoncee", 0) for r in rapports)
    recu = sum(f.get("taille_recue", 0) for r in rapports for f in r["fichiers"])
    # Une taille divergente est un échec. Ne pas la compter comme telle ferait
    # sortir le programme en 0 sur un fichier tronqué.
    echecs = [f["nom_original"] for r in rapports for f in r["fichiers"]
              if f.get("statut", "").startswith("échec")
              or f.get("taille_conforme") is False]

    print()
    print(f"Volume annoncé : {volume / 1e9:.2f} Go")
    print(f"Écarté avant téléchargement : {evites / 1e9:.2f} Go")
    print(f"À rapatrier    : {(volume - evites) / 1e9:.2f} Go")
    if not arguments.plan:
        print(f"Volume reçu    : {recu / 1e9:.2f} Go")
        print(f"Échecs         : {len(echecs)}")
        for nom in echecs[:10]:
            print(f"  {nom}")

        racine.mkdir(parents=True, exist_ok=True)
        provenance = racine / "PROVENANCE.json"

        # Fusion, jamais remplacement. Un appel `--cle une_source` écrasait
        # auparavant la provenance des treize autres : les empreintes recalculées
        # étaient perdues alors même que les fichiers d'origine venaient d'être
        # supprimés sur la foi de cette provenance. Un fichier de traçabilité qui
        # se détruit lui-même est pire qu'aucun.
        connues: dict[str, dict] = {}
        if provenance.exists():
            try:
                ancien = json.loads(provenance.read_text(encoding="utf-8"))
                connues = {s["cle"]: s for s in ancien.get("sources", [])}
            except (json.JSONDecodeError, KeyError, TypeError):
                print("PROVENANCE.json illisible : il sera reconstruit à partir "
                      "des seules sources traitées.")
        for rapport in rapports:
            connues[rapport["cle"]] = rapport

        with provenance.open("w", encoding="utf-8", newline="") as flux:
            flux.write(json.dumps({
                "campagne": "WP-MAT-MEM-2026",
                "genere_par": "01_branche_matiere/memoire_materielle_reelle/telecharger_toutes_sources.py",
                "regle": "raw/ n'est jamais transformé ; toute dérivation cite le SHA-256 de sa source",
                "fusion": "un appel partiel complète ce fichier, il ne le remplace pas",
                "sources": [connues[c] for c in sorted(connues)],
            }, ensure_ascii=False, indent=2) + "\n")
        print(f"écrit : {provenance}  ({len(connues)} source(s) au total)")
    return 1 if echecs else 0


if __name__ == "__main__":
    raise SystemExit(main())
