"""Enregistre l'environnement d'exécution — Étape 0.7 du plan directeur.

« Enregistrer les versions de Python, bibliothèques, compilateurs, systèmes et
matériels. » Sans cela, un résultat qui ne se reproduit pas ne peut pas être
diagnostiqué : on ne sait pas ce qui a changé.

    python enregistrer_environnement.py            # écrit ENVIRONNEMENT.md
    python enregistrer_environnement.py --verifier # compare à l'existant

Le mode `--verifier` ne fait pas échouer le dossier : un environnement
différent n'est pas une anomalie, c'est une information. Il liste les écarts.
"""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from importlib import metadata
from pathlib import Path

RACINE = Path(__file__).resolve().parent
CIBLE = RACINE / "ENVIRONNEMENT.md"

# Bibliothèques dont dépendent les résultats publiés.
SUIVIES = [
    "numpy", "scipy", "pandas", "matplotlib", "networkx", "sympy",
    "numba", "llvmlite", "pytest", "rebound", "python-docx",
]


def version(nom: str) -> str:
    try:
        return metadata.version(nom)
    except metadata.PackageNotFoundError:
        return "absent"


def blas() -> str:
    """Implémentation d'algèbre linéaire : elle change le dernier chiffre."""
    try:
        import numpy as np
        config = getattr(np, "__config__", None)
        if config is not None and hasattr(config, "show"):
            import io
            import contextlib
            tampon = io.StringIO()
            with contextlib.redirect_stdout(tampon):
                config.show()
            texte = tampon.getvalue().lower()
            for candidat in ("openblas", "mkl", "accelerate", "blis", "atlas"):
                if candidat in texte:
                    return candidat
        return "indéterminée"
    except Exception:
        return "indéterminée"


def collecter() -> dict:
    return {
        "python": sys.version.split()[0],
        "implementation": platform.python_implementation(),
        "compilateur_python": platform.python_compiler(),
        "systeme": f"{platform.system()} {platform.release()}",
        "version_systeme": platform.version(),
        "machine": platform.machine(),
        "processeur": platform.processor() or "non renseigné",
        "algebre_lineaire": blas(),
        "bibliotheques": {nom: version(nom) for nom in SUIVIES},
    }


def rendre(donnees: dict) -> str:
    lignes = [
        "# Environnement d'exécution",
        "",
        "Généré par `enregistrer_environnement.py`, Étape 0.7 du plan",
        "directeur. Ce fichier décrit la machine sur laquelle les résultats du",
        "dossier ont été produits. **Il n'est pas une exigence de",
        "reproduction** : un environnement différent n'invalide rien, il",
        "explique un écart.",
        "",
        "## Plateforme",
        "",
        "| Élément | Valeur |",
        "|---|---|",
        f"| Python | {donnees['python']} ({donnees['implementation']}) |",
        f"| Compilateur | {donnees['compilateur_python']} |",
        f"| Système | {donnees['systeme']} |",
        f"| Version du système | {donnees['version_systeme']} |",
        f"| Architecture | {donnees['machine']} |",
        f"| Processeur | {donnees['processeur']} |",
        f"| Algèbre linéaire | {donnees['algebre_lineaire']} |",
        "",
        "## Bibliothèques suivies",
        "",
        "| Bibliothèque | Version |",
        "|---|---|",
    ]
    for nom, valeur in donnees["bibliotheques"].items():
        lignes.append(f"| `{nom}` | {valeur} |")
    lignes += [
        "",
        "## Portée",
        "",
        "Le plan directeur demande en outre l'exécution sous trois systèmes",
        "d'exploitation, sur deux architectures matérielles et dans une image",
        "de conteneur — Étape 0.8 à 0.10. **Rien de cela n'est fait.** Le",
        "dossier n'a été exécuté que sur la plateforme ci-dessus.",
        "",
        "Un écart déjà constaté et documenté relève de cette catégorie :",
        "l'écart maximal du contrôle d'attractivité globale vaut `2,00 × 10⁻¹⁶`",
        "dans une exécution et `2,00 × 10⁻¹⁵` dans une autre, selon la version",
        "de la bibliothèque d'algèbre linéaire. Voir",
        "`AUTORITE_DES_DOCUMENTS.md`.",
    ]
    return "\n".join(lignes) + "\n"


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--verifier", action="store_true")
    arguments = parseur.parse_args()
    donnees = collecter()

    if not arguments.verifier:
        CIBLE.write_text(rendre(donnees), encoding="utf-8")
        print(f"{CIBLE.name} écrit.")
        return 0

    if not CIBLE.exists():
        print(f"{CIBLE.name} absent.")
        return 1
    texte = CIBLE.read_text(encoding="utf-8")
    ecarts = []
    for nom, valeur in donnees["bibliotheques"].items():
        if f"| `{nom}` | {valeur} |" not in texte:
            ecarts.append(f"{nom} : {valeur} ici")
    if f"| Python | {donnees['python']}" not in texte:
        ecarts.append(f"python : {donnees['python']} ici")
    if ecarts:
        print("Écarts avec l'environnement enregistré :")
        for ecart in ecarts:
            print(f"  {ecart}")
        print("\nCe n'est pas une anomalie. C'est une information à citer si "
              "un résultat diffère.")
    else:
        print("Environnement identique à celui enregistré.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
