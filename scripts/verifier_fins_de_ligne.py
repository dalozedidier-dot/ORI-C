#!/usr/bin/env python3
"""Vérifie que le manifeste porte les octets qu'un clonage restituera.

`verifier_dossier.py` compare le manifeste à la **copie de travail**. Sur un
poste Windows, un script Python qui écrit en mode texte produit des CRLF, alors
que `.gitattributes` déclare `eol=lf` pour ce fichier : Git stocke des LF et les
restitue en LF au clonage. Le manifeste construit localement porte alors des
octets que personne d'autre ne verra, et le contrôle d'intégrité échoue après le
`push` alors que tout paraissait vert en local.

Ce script ferme cet angle mort. Pour chaque fichier suivi et inscrit au
manifeste, il détermine les attributs Git effectifs et vérifie qu'un fichier
promis en LF ne contient pas de CRLF dans la copie de travail.

Il fonctionne sur des modifications non encore indexées, ce qui est le moment
utile : avant `git add`, avant `git commit`, avant `git push`.

    python scripts/verifier_fins_de_ligne.py

Code de retour 0 si le manifeste correspond à ce qu'un clonage restituera,
1 sinon.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
MANIFESTE = RACINE / "MANIFEST.sha256.json"


def attributs(chemins: list[str]) -> dict[str, dict[str, str]]:
    """Attributs `text` et `eol` effectifs, en un seul appel à Git."""
    # `-z` sépare la sortie par des NUL, ce qui rend le nom de fichier
    # inambigu même s'il contient des espaces. L'entrée doit alors être
    # séparée de la même façon, sans quoi Git ne lit qu'un seul chemin.
    processus = subprocess.run(
        ["git", "check-attr", "--stdin", "-z", "text", "eol"],
        cwd=RACINE,
        input="\0".join(chemins) + "\0",
        capture_output=True,
        text=True,
        check=True,
    )
    resultat: dict[str, dict[str, str]] = {}
    champs = processus.stdout.split("\0")
    for index in range(0, len(champs) - 2, 3):
        chemin, attribut, valeur = champs[index], champs[index + 1], champs[index + 2]
        resultat.setdefault(chemin, {})[attribut] = valeur
    return resultat


def livre_en_lf(valeurs: dict[str, str], contenu: bytes) -> bool:
    """Le fichier sera-t-il restitué avec des fins de ligne LF ?

    `-text` préserve les octets tels quels. `text=auto` laisse Git décider :
    il ne convertit pas ce qu'il reconnaît comme binaire, et le critère qu'il
    emploie est la présence d'un octet nul. Sans cette vérification, une roue
    Python ou une archive contenant par hasard la séquence CR LF serait
    signalée à tort.
    """
    if valeurs.get("text") == "unset":
        return False
    if valeurs.get("eol") == "crlf":
        return False
    if valeurs.get("text") == "auto" and b"\0" in contenu:
        return False
    return valeurs.get("eol") == "lf" or valeurs.get("text") in {"set", "auto"}


def main() -> int:
    manifeste = json.loads(MANIFESTE.read_text(encoding="utf-8"))
    entrees = manifeste.get("entries") or manifeste.get("files") or []
    inscrits = [e["path"] for e in entrees]

    # Contrôler aussi les nouveaux fichiers déjà inscrits au manifeste mais pas
    # encore indexés. C'est précisément avant `git add` que ce garde-fou doit
    # détecter une sortie Windows en CRLF promise en LF par `.gitattributes`.
    chemins = sorted(set(inscrits))
    if not chemins:
        print("Aucun fichier suivi à vérifier.")
        return 0

    tous = attributs(chemins)
    fautifs: list[str] = []
    controles = 0
    for chemin in chemins:
        fichier = RACINE / chemin
        if not fichier.exists():
            continue
        contenu = fichier.read_bytes()
        if not livre_en_lf(tous.get(chemin, {}), contenu):
            continue
        controles += 1
        if b"\r\n" in contenu:
            fautifs.append(chemin)

    if fautifs:
        print(
            "Ces fichiers contiennent des CRLF alors que Git les restituera en "
            "LF. Le manifeste porte donc des octets qu'un clonage ne produira "
            "jamais, et le contrôle d'intégrité échouera après le push :"
        )
        for chemin in fautifs[:40]:
            print(f"- {chemin}")
        if len(fautifs) > 40:
            print(f"- ... {len(fautifs) - 40} autres")
        print()
        print(
            "Correction : réécrire ces fichiers en LF, puis relancer "
            "`python build_manifest.py build`. Dans les scripts Python, ouvrir "
            'les sorties avec `newline=""` pour ne pas régénérer le défaut.'
        )
        return 1

    print(
        f"{controles} fichiers promis en LF vérifiés, aucun CRLF. Le manifeste "
        "correspond à ce qu'un clonage restituera."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
