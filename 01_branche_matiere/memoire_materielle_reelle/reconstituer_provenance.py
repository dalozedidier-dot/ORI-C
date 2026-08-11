#!/usr/bin/env python3
"""Rétablit la provenance depuis l'API et empreinte les fichiers conservés.

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
            "sources_sans_empreinte_des_octets_recus": perdues,
            "remede": "relancer telecharger_toutes_sources.py",
            "sources": rapports,
            "fichiers_conserves": inventaire,
        }, ensure_ascii=False, indent=2) + "\n")
    print(f"écrit : {provenance}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
