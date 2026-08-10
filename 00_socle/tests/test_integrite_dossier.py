"""Intégrité du dossier unique ORI-C."""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

DOSSIER = Path(__file__).resolve().parents[2]


def lancer_verificateur(*options: str) -> subprocess.CompletedProcess[str]:
    # La sortie est lue en UTF-8, donc le processus fils doit écrire en UTF-8.
    # Sans cette variable, Python utilise la page de code du système sous
    # Windows : « objets LFS non hydratés » revient mutilé et l'expression
    # régulière ci-dessous ne trouve plus rien, quel que soit l'état réel du
    # dossier.
    environnement = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    return subprocess.run(
        [sys.executable, str(DOSSIER / "verifier_dossier.py"), *options],
        cwd=DOSSIER,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environnement,
    )


def test_le_verificateur_accepte_un_arbre_source_coherent() -> None:
    resultat = lancer_verificateur("--allow-lfs-pointers")
    assert resultat.returncode == 0, resultat.stdout + resultat.stderr


def test_le_mode_strict_refuse_uniquement_les_objets_lfs_non_hydrates() -> None:
    resultat = lancer_verificateur()
    correspondance = re.search(
        r"(\d+) objets LFS non hydratés",
        resultat.stdout,
    )
    assert correspondance is not None, resultat.stdout + resultat.stderr

    nombre_non_hydrates = int(correspondance.group(1))
    if nombre_non_hydrates > 0:
        assert resultat.returncode == 2, resultat.stdout + resultat.stderr
        assert "Archive non autonome" in resultat.stdout
    else:
        assert resultat.returncode == 0, resultat.stdout + resultat.stderr
        assert "Archive non autonome" not in resultat.stdout


def test_les_quatre_composantes_sont_presentes() -> None:
    attendus = [
        "00_socle",
        "01_branche_matiere",
        "02_branche_systeme_solaire",
        "03_branche_vivant",
    ]
    manquants = [nom for nom in attendus if not (DOSSIER / nom).is_dir()]
    assert not manquants, f"Composantes absentes : {manquants}"


def test_les_deux_couches_de_la_branche_2_restent_separees() -> None:
    branche = DOSSIER / "02_branche_systeme_solaire"
    assert (branche / "couche_astronomique").is_dir()
    assert (branche / "couche_memoire_historique").is_dir()


def test_le_manifeste_racine_chaine_les_deux_sous_manifestes() -> None:
    import json

    attendus = {
        "02_branche_systeme_solaire/couche_memoire_historique/MANIFEST.sha256",
        "plan_directeur/revue_systematique/MANIFEST.sha256",
    }
    lignes = (DOSSIER / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines()
    chemins_texte = {ligne.split("  ", 1)[1] for ligne in lignes if "  " in ligne}
    document = json.loads((DOSSIER / "MANIFEST.sha256.json").read_text(encoding="utf-8"))
    chemins_json = {entree["path"] for entree in document["files"]}

    assert attendus <= chemins_texte
    assert attendus <= chemins_json
