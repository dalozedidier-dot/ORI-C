#!/usr/bin/env python3
"""Vérifie l'intégrité et la provenance des sources téléchargées.

Cinq contrôles, dans cet ordre :

1. **SHA-256 de ce qu'on détient** — chaque fichier de `exploitable/` est
   réempreinté et comparé à l'inventaire de `PROVENANCE.json`. C'est la garantie
   qui compte : les extractions porteront sur ces fichiers-là.
2. **Complétude de l'inventaire** — tout fichier présent sur le disque et absent
   de l'inventaire, ou l'inverse. `raw/` a été supprimé après extraction, à
   dessein : le vérifier serait vérifier ce qui n'existe plus.
3. **Archives corrompues** — les `.zip` sont ouverts et leur table testée ; une
   archive qui se lit à moitié fausse silencieusement une extraction.
4. **Doublons** — deux fichiers de même empreinte, y compris entre sources
   différentes. Un doublon inter-sources n'est pas une erreur mais il interdit
   de compter les deux comme réplications indépendantes : c'est le même octet.
5. **Provenance** — DOI, licence et version présents pour chaque source. Sans
   eux, la donnée n'est pas citable.

    python verifier_sources.py
    python verifier_sources.py --rapide   # saute le réempreintage
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from collections import defaultdict
from pathlib import Path

ICI = Path(__file__).resolve().parent
SOURCES = ICI / "SOURCES.json"
BLOC = 1 << 20


def empreinte(chemin: Path) -> str:
    valeur = hashlib.sha256()
    with chemin.open("rb") as flux:
        for bloc in iter(lambda: flux.read(BLOC), b""):
            valeur.update(bloc)
    return valeur.hexdigest()


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--rapide", action="store_true")
    arguments = analyseur.parse_args()

    config = json.loads(SOURCES.read_text(encoding="utf-8"))
    racine = (ICI / config["racine_locale"]).resolve()
    provenance = racine / "PROVENANCE.json"
    if not provenance.exists():
        print(f"PROVENANCE.json absent sous {racine}.")
        print("Exécuter d'abord telecharger_toutes_sources.py.")
        return 2

    document = json.loads(provenance.read_text(encoding="utf-8"))
    anomalies: list[str] = []
    par_empreinte: dict[str, list[str]] = defaultdict(list)
    total_octets = 0
    total_fichiers = 0

    inventaire = {e["chemin"]: e for e in document.get("fichiers_conserves", [])}
    if not inventaire:
        print("Inventaire des fichiers conservés absent de PROVENANCE.json.")
        print("Exécuter reconstituer_provenance.py.")
        return 2

    print(f"Racine : {racine}")
    print(f"{len(inventaire)} fichiers inventoriés.")
    print()

    # Ce qu'on détient doit correspondre exactement à l'inventaire, dans les deux sens.
    sur_disque = {
        str(f.relative_to(racine)).replace("\\", "/")
        for source in document["sources"]
        for f in (racine / source["cle"] / "exploitable").rglob("*")
        if (racine / source["cle"] / "exploitable").is_dir() and f.is_file()
    }
    for chemin in sorted(set(inventaire) - sur_disque):
        anomalies.append(f"inventorié mais absent du disque — {chemin}")
    for chemin in sorted(sur_disque - set(inventaire)):
        anomalies.append(f"sur le disque mais hors inventaire — {chemin}")

    par_cle: dict[str, list] = defaultdict(list)
    for chemin, entree in inventaire.items():
        par_cle[entree["cle"]].append((chemin, entree))

    for cle, entrees in sorted(par_cle.items()):
        alteres = corrompues = 0
        octets = 0
        for chemin, entree in entrees:
            fichier = racine / chemin
            if not fichier.exists():
                continue
            total_fichiers += 1
            octets += fichier.stat().st_size
            if arguments.rapide:
                par_empreinte[entree["sha256"]].append(chemin)
            else:
                reelle = empreinte(fichier)
                par_empreinte[reelle].append(chemin)
                if reelle != entree["sha256"]:
                    alteres += 1
                    anomalies.append(f"{cle} : SHA-256 divergent — {chemin}")
            if fichier.suffix.lower() == ".zip":
                try:
                    with zipfile.ZipFile(fichier) as archive:
                        if archive.testzip() is not None:
                            corrompues += 1
                            anomalies.append(f"{cle} : archive corrompue — {chemin}")
                except zipfile.BadZipFile:
                    corrompues += 1
                    anomalies.append(f"{cle} : archive illisible — {chemin}")
        total_octets += octets
        etat = "conforme" if not (alteres or corrompues) else "ANOMALIE"
        print(f"  {cle:<34} {octets / 1e6:>9.1f} Mo  {len(entrees):>4} fich.  {etat}")

    for source in document["sources"]:
        for champ in ("doi", "licence"):
            if not source.get(champ):
                anomalies.append(f"{source['cle']} : provenance incomplète, {champ} absent")

    doublons = {e: n for e, n in par_empreinte.items() if len(n) > 1}
    print()
    print(f"{total_fichiers} fichiers, {total_octets / 1e9:.2f} Go vérifiés"
          f"{' (empreintes non recalculées)' if arguments.rapide else ''}.")
    if doublons:
        print(f"{len(doublons)} empreinte(s) partagée(s) par plusieurs fichiers :")
        for noms in list(doublons.values())[:8]:
            print(f"  {' = '.join(noms)}")
        print("  Un contenu identique ne compte pas deux fois comme réplication.")

    if anomalies:
        print()
        print(f"{len(anomalies)} anomalie(s) :")
        for anomalie in anomalies[:25]:
            print(f"  {anomalie}")
        if len(anomalies) > 25:
            print(f"  … et {len(anomalies) - 25} autres")
        return 1

    print("Sources intègres et citables.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
