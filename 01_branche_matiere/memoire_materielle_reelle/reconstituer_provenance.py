#!/usr/bin/env python3
"""Reconstitue la provenance perdue, et empreinte ce qui est réellement conservé.

Deux choses différentes, qu'il ne faut pas confondre.

**La provenance d'origine** — DOI, URL, taille, licence, somme de contrôle
annoncée par le dépôt — est reconstituable à tout moment depuis l'API. Elle ne
dépend pas de ce qu'on a sur le disque.

**L'empreinte des octets reçus** ne l'est pas. Elle se calcule au téléchargement,
sur les octets qui arrivent, et elle atteste que ce qu'on a lu est bien ce que le
dépôt a publié. Si les fichiers d'origine ont été supprimés, cette empreinte est
perdue : la recalculer exige de retélécharger.

Ce script fait donc deux choses distinctes et les inscrit séparément :

1. il réinterroge l'API pour toutes les sources et rétablit la provenance
   d'origine, en marquant explicitement `sha256_recalcule: null` là où
   l'empreinte des octets reçus n'est plus disponible ;
2. il empreinte les 843 fichiers réellement conservés dans `exploitable/`, ce qui
   garantit l'identité de ce qu'on **a** — la garantie qui compte pour la suite,
   puisque c'est sur ces fichiers que porteront les extractions.

    python reconstituer_provenance.py
"""
from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ICI = Path(__file__).resolve().parent
SOURCES = ICI / "SOURCES.json"
API = "https://zenodo.org/api/records/{}"
BLOC = 1 << 20


def interroger(record: str) -> dict | None:
    for essai in range(3):
        try:
            with urllib.request.urlopen(API.format(record), timeout=60) as flux:
                return json.loads(flux.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            if essai == 2:
                return None
            time.sleep(2 * (essai + 1))
    return None


def empreinte(chemin: Path) -> str:
    valeur = hashlib.sha256()
    with chemin.open("rb") as flux:
        for bloc in iter(lambda: flux.read(BLOC), b""):
            valeur.update(bloc)
    return valeur.hexdigest()


def main() -> int:
    config = json.loads(SOURCES.read_text(encoding="utf-8"))
    racine = (ICI / config["racine_locale"]).resolve()
    provenance = racine / "PROVENANCE.json"

    existantes: dict[str, dict] = {}
    if provenance.exists():
        try:
            existantes = {s["cle"]: s
                          for s in json.loads(provenance.read_text(encoding="utf-8"))
                          .get("sources", [])}
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
    print(f"Provenance actuelle : {len(existantes)} source(s) sur "
          f"{len(config['sources'])}.")
    print()

    rapports: list[dict] = []
    perdues = 0
    for source in config["sources"]:
        cle, record = source["cle"], source["record"]
        ancienne = existantes.get(cle)
        if ancienne and any(f.get("sha256_recalcule") for f in ancienne.get("fichiers", [])):
            rapports.append(ancienne)
            print(f"  {cle:<34} empreintes des octets reçus conservées")
            continue

        donnees = interroger(record)
        if donnees is None or "metadata" not in donnees:
            print(f"  {cle:<34} API injoignable")
            continue
        meta = donnees["metadata"]
        fichiers = []
        for distant in donnees.get("files", []):
            nom = distant.get("key")
            fichiers.append({
                "nom_original": nom,
                "chemin_local": f"{cle}/raw/{nom}",
                "url": (distant.get("links") or {}).get("self")
                       or f"https://zenodo.org/records/{record}/files/{nom}?download=1",
                "taille_annoncee": distant.get("size", 0),
                "checksum_annonce": distant.get("checksum"),
                "sha256_recalcule": None,
                "empreinte_perdue": True,
            })
        perdues += 1
        rapports.append({
            "cle": cle,
            "record": record,
            "doi": donnees.get("doi"),
            "titre": meta.get("title"),
            "version": meta.get("version") or donnees.get("revision"),
            "date_publication": meta.get("publication_date"),
            "licence": (meta.get("license") or {}).get("id"),
            "famille_declaree": source.get("famille"),
            "role_declare": source.get("role"),
            "taille_totale_annoncee": sum(f["taille_annoncee"] for f in fichiers),
            "statut": "provenance rétablie depuis l'API ; octets d'origine supprimés",
            "fichiers": fichiers,
        })
        print(f"  {cle:<34} provenance rétablie, {len(fichiers)} fichier(s), "
              f"empreintes des octets reçus PERDUES")

    # Empreinte de ce qui est réellement conservé.
    print()
    inventaire = []
    total = 0
    for source in config["sources"]:
        dossier = racine / source["cle"] / "exploitable"
        if not dossier.is_dir():
            continue
        for fichier in sorted(p for p in dossier.rglob("*") if p.is_file()):
            inventaire.append({
                "cle": source["cle"],
                "chemin": str(fichier.relative_to(racine)).replace("\\", "/"),
                "taille": fichier.stat().st_size,
                "sha256": empreinte(fichier),
            })
            total += fichier.stat().st_size
    print(f"  {len(inventaire)} fichiers conservés empreintés, {total / 1e9:.2f} Go")

    with provenance.open("w", encoding="utf-8", newline="") as flux:
        flux.write(json.dumps({
            "campagne": "WP-MAT-MEM-2026",
            "genere_par": "01_branche_matiere/memoire_materielle_reelle/reconstituer_provenance.py",
            "avertissement": (
                f"{perdues} source(s) ont perdu l'empreinte de leurs octets reçus : "
                f"un appel partiel du téléchargeur écrasait la provenance au lieu de "
                f"la compléter, et les fichiers d'origine ont été supprimés ensuite. "
                f"La provenance d'origine — DOI, URL, taille, licence, somme annoncée — "
                f"est rétablie depuis l'API et suffit à retélécharger à l'identique. "
                f"Pour rétablir aussi les empreintes des octets reçus, relancer "
                f"telecharger_toutes_sources.py, qui fusionne désormais."),
            "sources": rapports,
            "fichiers_conserves": inventaire,
        }, ensure_ascii=False, indent=2) + "\n")
    print(f"écrit : {provenance}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
