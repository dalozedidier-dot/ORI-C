"""Intégrité du dossier unique ORI-C."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

DOSSIER = Path(__file__).resolve().parents[2]


def lancer_verificateur(*options: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(DOSSIER / "verifier_dossier.py"), *options],
        cwd=DOSSIER,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def test_le_verificateur_accepte_un_arbre_source_coherent() -> None:
    resultat = lancer_verificateur("--allow-lfs-pointers")
    assert resultat.returncode == 0, resultat.stdout + resultat.stderr


def test_le_mode_strict_refuse_uniquement_les_objets_lfs_non_hydrates() -> None:
    resultat = lancer_verificateur()
    if "objets LFS non hydratés" in resultat.stdout:
        assert resultat.returncode == 2, resultat.stdout + resultat.stderr
        assert "Archive non autonome" in resultat.stdout
    else:
        assert resultat.returncode == 0, resultat.stdout + resultat.stderr


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
