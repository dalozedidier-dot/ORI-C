"""Intégrité du dossier unique.

Le contrôle d'intégrité ne porte plus sur le seul socle mais sur l'ensemble du
dossier : socle et trois branches. Il est délégué à `verifier_dossier.py`
placé à la racine, qui compare les 424 entrées du manifeste et vérifie que la
structure attendue est présente.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

DOSSIER = Path(__file__).resolve().parents[2]


def test_le_verificateur_du_dossier_unique_est_satisfait() -> None:
    resultat = subprocess.run(
        [sys.executable, str(DOSSIER / "verifier_dossier.py")],
        cwd=DOSSIER, capture_output=True, text=True,
    )
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
    """Le verdict négatif d'une couche ne doit pas contaminer l'autre."""
    branche = DOSSIER / "02_branche_systeme_solaire"
    assert (branche / "couche_astronomique").is_dir()
    assert (branche / "couche_memoire_historique").is_dir()
