#!/usr/bin/env python3
"""Compare le manifeste aux octets que l'intégration continue recevra.

`verifier_dossier.py` compare le manifeste à la **copie de travail**. Sur un
poste Windows, un fichier écrit par un script Python en mode texte contient des
CRLF, alors que `.gitattributes` déclare `eol=lf` : Git stocke des LF et les
livre en LF au clonage. Le manifeste construit localement porte donc des octets
que l'intégration continue ne verra jamais, et le contrôle d'intégrité échoue
après le `push` alors que tout paraissait vert en local.

Ce script ferme cet angle mort. Il compare chaque empreinte du manifeste au
**blob d'index** correspondant, c'est-à-dire exactement ce qu'un clonage
restitue. Les objets Git LFS sont ignorés : leur blob d'index est un pointeur,
et l'intégration continue les hydrate avant de vérifier quoi que ce soit.

    python scripts/verifier_fins_de_ligne.py

Code de retour 0 si le manifeste correspond à ce que l'intégration continue
recevra, 1 sinon.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
MANIFESTE = RACINE / "MANIFEST.sha256.json"
ENTETE_LFS = b"version https://git-lfs.github.com/spec/v1"


def blobs_d_index(chemins: list[str]) -> dict[str, bytes]:
    """Contenu indexé de chaque chemin, en une seule passe `git cat-file`."""
    processus = subprocess.Popen(
        ["git", "cat-file", "--batch"],
        cwd=RACINE,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    requete = "".join(f":{chemin}\n" for chemin in chemins).encode("utf-8")
    sortie, _ = processus.communicate(requete)

    resultat: dict[str, bytes] = {}
    curseur = 0
    for chemin in chemins:
        fin_entete = sortie.index(b"\n", curseur)
        entete = sortie[curseur:fin_entete].decode("utf-8", "replace")
        if "missing" in entete:
            curseur = fin_entete + 1
            continue
        taille = int(entete.split()[2])
        debut = fin_entete + 1
        resultat[chemin] = sortie[debut : debut + taille]
        curseur = debut + taille + 1
    return resultat


def main() -> int:
    manifeste = json.loads(MANIFESTE.read_text(encoding="utf-8"))
    entrees = manifeste.get("entries") or manifeste.get("files") or []
    attendu = {e["path"]: e["sha256"] for e in entrees}

    suivis = set(
        subprocess.run(
            ["git", "ls-files"], cwd=RACINE, capture_output=True, text=True, check=True
        ).stdout.splitlines()
    )
    chemins = sorted(set(attendu) & suivis)
    contenus = blobs_d_index(chemins)

    divergents: list[str] = []
    ignores_lfs = 0
    for chemin in chemins:
        contenu = contenus.get(chemin)
        if contenu is None:
            continue
        if contenu.startswith(ENTETE_LFS):
            ignores_lfs += 1
            continue
        if hashlib.sha256(contenu).hexdigest() != attendu[chemin]:
            divergents.append(chemin)

    if divergents:
        print(
            "Le manifeste ne correspond pas à ce qu'un clonage restituera. "
            "Ces fichiers sont très probablement écrits en CRLF alors que "
            "`.gitattributes` les déclare en LF :"
        )
        for chemin in divergents[:40]:
            print(f"- {chemin}")
        if len(divergents) > 40:
            print(f"- ... {len(divergents) - 40} autres")
        print()
        print(
            "Correction : réécrire ces fichiers en LF, puis relancer "
            "`python build_manifest.py build`. Dans les scripts Python, ouvrir "
            'les sorties avec `newline=""`.'
        )
        return 1

    print(
        f"{len(chemins) - ignores_lfs} fichiers vérifiés contre leur blob d'index, "
        f"{ignores_lfs} objets Git LFS ignorés. Le manifeste correspond à ce que "
        "l'intégration continue recevra."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
