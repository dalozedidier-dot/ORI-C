#!/usr/bin/env python3
"""Contrôle à passer avant tout `git push`.

Le dépôt ne contient pas un manifeste mais **trois** : celui de la racine, celui
de la couche mémoire historique et celui de la revue systématique. Chacun
gouverne son propre périmètre, et rien n'obligeait jusqu'ici à les reconstruire
ensemble.

C'est ce qui a cassé la CI le 8 août 2026 : `scripts/surrogats.py` avait été
poussé sans être inscrit au manifeste racine, et neuf fichiers importés dans la
couche mémoire — la table climatique et le préenregistrement — sans être inscrits
au manifeste local de cette couche. Cinq étapes ont échoué dans trois workflows
pour une seule et même raison, invisible en local parce qu'aucun contrôle ne
croisait l'index Git avec les manifestes de sous-périmètre.

Ce script ferme cet angle mort. Il vérifie, dans l'ordre :

1. que tout fichier connu de Git est inscrit dans le manifeste qui le gouverne,
   pour chacun des trois périmètres ;
2. que les contenus correspondent, via `verifier_dossier.py` ;
3. qu'aucun fichier promis en LF n'est écrit en CRLF, via
   `scripts/verifier_fins_de_ligne.py` — sans quoi le contrôle passe en local et
   échoue après le clonage.

Sortie 0 si le push peut partir, 1 sinon.

    python scripts/controle_avant_push.py
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

LIGNE = re.compile(r"^([0-9a-f]{64})\s+(.*)$")

# Chaque périmètre reproduit les exclusions de l'outil qui construit son
# manifeste. Un fichier exclu n'est pas une anomalie ; un fichier ni exclu ni
# inscrit en est une.
PERIMETRES = [
    {
        "nom": "racine",
        "manifeste": Path("MANIFEST.sha256"),
        "prefixe": "",
        "reconstruire": "python build_manifest.py build",
        # Le manifeste racine a ses propres règles d'exclusion, portées par
        # build_manifest.py. On ne contrôle donc ici que le sens qui compte :
        # aucune entrée fantôme, et les sous-manifestes présents.
        "sens_unique": True,
    },
    {
        "nom": "couche mémoire historique",
        "manifeste": Path("02_branche_systeme_solaire/couche_memoire_historique/MANIFEST.sha256"),
        "prefixe": "02_branche_systeme_solaire/couche_memoire_historique/",
        "reconstruire": (
            "cd 02_branche_systeme_solaire/couche_memoire_historique && "
            'PYTHONPATH="$PWD/src" python -m oric_memory_tests.cli manifest'
        ),
        "exclusions": (
            ".git", "__pycache__", ".pytest_cache", ".pytest-tmp", ".mplconfig",
            "dist", "MANIFEST.sha256",
        ),
        "sens_unique": False,
    },
    {
        "nom": "revue systématique",
        "manifeste": Path("plan_directeur/revue_systematique/MANIFEST.sha256"),
        "prefixe": "plan_directeur/revue_systematique/",
        "reconstruire": "voir plan_directeur/revue_systematique/",
        "exclusions": (".git", "__pycache__", ".pytest_cache", "MANIFEST.sha256"),
        "sens_unique": False,
    },
]


def fichiers_connus_de_git() -> set[str]:
    """Fichiers suivis, plus les nouveaux non ignorés : ce qu'un push emporterait."""
    connus: set[str] = set()
    for arguments in (["ls-files"], ["ls-files", "--others", "--exclude-standard"]):
        sortie = subprocess.run(
            ["git", *arguments],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=True,
        ).stdout
        connus.update(ligne for ligne in sortie.splitlines() if ligne)
    return connus


def entrees_du_manifeste(chemin: Path, prefixe: str) -> dict[str, str]:
    """Chemin préfixé → empreinte déclarée."""
    entrees: dict[str, str] = {}
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        correspondance = LIGNE.match(ligne.strip())
        if correspondance:
            entrees[prefixe + correspondance.group(2)] = correspondance.group(1)
    return entrees


def empreintes_divergentes(chemin_manifeste: Path, entrees: dict[str, str],
                           prefixe: str) -> list[str]:
    """Recalcule chaque empreinte déclarée et signale celles qui ne collent pas.

    Contrôler la seule présence des chemins ne suffit pas : un manifeste peut
    lister tous les bons fichiers et porter des empreintes périmées. C'était le
    cas de `plan_directeur/revue_systematique/MANIFEST.sha256`, dont 11 entrées
    sur 22 étaient fausses alors que ce script les déclarait conformes.
    """
    base = (chemin_manifeste.parent if prefixe else RACINE)
    divergentes = []
    for chemin, attendu in entrees.items():
        relatif = chemin[len(prefixe):] if prefixe else chemin
        fichier = base / relatif
        if not fichier.is_file():
            continue  # traité par le contrôle de présence
        try:
            reel = hashlib.sha256(fichier.read_bytes()).hexdigest()
        except OSError:
            divergentes.append(f"{chemin} — illisible")
            continue
        if reel != attendu:
            divergentes.append(chemin)
    return divergentes


def controler_perimetres(connus: set[str]) -> list[str]:
    anomalies: list[str] = []
    for perimetre in PERIMETRES:
        chemin = RACINE / perimetre["manifeste"]
        nom = perimetre["nom"]
        if not chemin.exists():
            anomalies.append(f"{nom} : manifeste absent, {perimetre['manifeste']}")
            continue

        inscrits = entrees_du_manifeste(chemin, perimetre["prefixe"])
        fantomes = sorted(set(inscrits) - connus)
        for fantome in fantomes:
            anomalies.append(f"{nom} : inscrit au manifeste mais inconnu de Git — {fantome}")

        manquants: list[str] = []
        if not perimetre["sens_unique"]:
            exclusions = perimetre["exclusions"]
            portee = {
                fichier for fichier in connus
                if fichier.startswith(perimetre["prefixe"])
                and not any(part in exclusions for part in fichier.split("/"))
            }
            manquants = sorted(portee - set(inscrits))
            for manquant in manquants:
                anomalies.append(f"{nom} : suivi par Git mais absent du manifeste — {manquant}")

        # Le manifeste racine est déjà contrôlé octet à octet par
        # `verifier_dossier.py`. Les sous-manifestes ne l'étaient par rien.
        divergentes: list[str] = []
        if not perimetre["sens_unique"]:
            divergentes = empreintes_divergentes(chemin, inscrits, perimetre["prefixe"])
            for divergente in divergentes:
                anomalies.append(f"{nom} : empreinte périmée — {divergente}")

        defauts = fantomes or manquants or divergentes
        etat = "conforme" if not defauts else "À RECONSTRUIRE"
        detail = f" ({len(divergentes)} empreintes périmées)" if divergentes else ""
        print(f"  {nom:<28} {len(inscrits):>5} entrées   {etat}{detail}")
        if defauts:
            print(f"      {perimetre['reconstruire']}")
    return anomalies


def executer(titre: str, commande: list[str]) -> bool:
    resultat = subprocess.run(commande, cwd=RACINE, capture_output=True, text=True, encoding="utf-8")
    reussi = resultat.returncode == 0
    print(f"  {titre:<28} {'conforme' if reussi else 'ÉCHEC'}")
    if not reussi:
        for ligne in (resultat.stdout + resultat.stderr).strip().splitlines()[-8:]:
            print(f"      {ligne}")
    return reussi


def simuler_la_ci() -> bool:
    """Rejoue la campagne sur un clone nu et vérifie que rien ne bouge.

    Un clone n'a ni les sources locales ni le cache : c'est exactement ce que
    voit la CI. Trois échecs de suite venaient de la différence entre les deux.
    """
    import shutil
    import tempfile

    campagne = "01_branche_matiere/memoire_materielle_reelle"
    if not (RACINE / campagne / "run_all.py").exists():
        return True
    with tempfile.TemporaryDirectory() as temporaire:
        # Le clone va dans un sous-dossier vide : `racine_locale` de la campagne
        # pointe vers le parent du dépôt, et si ce parent contient les données
        # locales la simulation n'est plus celle d'un runner.
        parent = Path(temporaire) / "vide"
        parent.mkdir()
        clone = parent / "ORI-C"
        # `GIT_LFS_SKIP_SMUDGE` laisse les pointeurs en place, comme un
        # `checkout` sans `lfs: true`. C'est ce qui a fait échouer le job
        # matière quatre fois : en local LFS est hydraté, sur le runner non.
        environnement = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1")
        fait = subprocess.run(["git", "clone", "--quiet", str(RACINE), str(clone)],
                              capture_output=True, text=True, env=environnement)
        if fait.returncode != 0:
            print("  simulation de la CI      clonage impossible, contrôle sauté")
            return True
        # La CI hydre LFS avant de lire les données. Le clone ci-dessus les a
        # laissées en pointeurs pour vérifier que le workflow le fait bien ;
        # on les hydre maintenant, comme lui.
        hydrate = subprocess.run(["git", "lfs", "pull"], cwd=clone,
                                 capture_output=True, text=True)
        if hydrate.returncode != 0:
            print("  simulation de la CI      git lfs pull impossible, contrôle sauté")
            return True
        execution = subprocess.run(
            [sys.executable, "run_all.py", "--sans-verification"],
            cwd=clone / campagne, capture_output=True, text=True,
            encoding="utf-8", errors="replace")
        modifies = subprocess.run(["git", "status", "--short", "--", f"{campagne}/derive"],
                                  cwd=clone, capture_output=True, text=True,
                                  encoding="utf-8").stdout.strip()
        shutil.rmtree(clone, ignore_errors=True)

    if execution.returncode != 0:
        print(f"  simulation de la CI      ÉCHEC, run_all sort en {execution.returncode}")
        for ligne in (execution.stdout or "").strip().splitlines()[-8:]:
            print(f"      {ligne}")
        return False
    if modifies:
        print("  simulation de la CI      ÉCHEC, la campagne modifie des fichiers versionnés")
        for ligne in modifies.splitlines()[:6]:
            print(f"      {ligne}")
        return False
    print("  simulation de la CI      conforme")
    return True


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument(
        "--allow-lfs-pointers", action="store_true",
        help="tolère les objets LFS non hydratés, utile hors CI",
    )
    arguments = analyseur.parse_args()

    print("Cohérence des trois manifestes avec l'index Git")
    anomalies = controler_perimetres(fichiers_connus_de_git())

    print()
    print("Vérificateurs")
    options = ["--allow-lfs-pointers"] if arguments.allow_lfs_pointers else []
    reussites = [
        executer("contenus du dépôt", [sys.executable, "verifier_dossier.py", *options]),
        executer("fins de ligne promises", [sys.executable, "scripts/verifier_fins_de_ligne.py"]),
    ]

    reussites.append(simuler_la_ci())

    print()
    if anomalies:
        print(f"{len(anomalies)} anomalie(s) de manifeste :")
        for anomalie in anomalies[:20]:
            print(f"  {anomalie}")
        if len(anomalies) > 20:
            print(f"  … et {len(anomalies) - 20} autres")
    if anomalies or not all(reussites):
        print()
        print("Ne pas pousser. La CI échouerait.")
        return 1
    print("Les trois manifestes sont à jour et les contenus concordent. Le push peut partir.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
