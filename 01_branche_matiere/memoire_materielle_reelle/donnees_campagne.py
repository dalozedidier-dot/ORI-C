#!/usr/bin/env python3
"""Résout la base de données d'une source : archive versionnée, sinon local.

Les archives de `donnees/sources/` contiennent exactement les fichiers que les
extracteurs lisent. Le dépôt se suffit ainsi à lui-même : aucune exécution n'a
besoin des 7,2 Go conservés hors dépôt ni d'un accès réseau.

    from donnees_campagne import base_de
    dossier = base_de("fabest_lcf", racine_locale)
"""
from __future__ import annotations

import zipfile
from pathlib import Path

ICI = Path(__file__).resolve().parent
ARCHIVES = ICI / "donnees" / "sources"


def base_de(cle: str, racine_locale: Path) -> Path | None:
    """Dossier contenant les fichiers de `cle`, ou None si introuvable."""
    archive = ARCHIVES / f"{cle}.zip"
    if archive.is_file():
        # Le cache d'extraction vit hors du dépôt : y écrire ferait apparaître
        # des fichiers non listés au manifeste et casserait le contrôle
        # d'intégrité que la CI exécute juste après.
        cible = racine_locale / ".cache_campagne" / cle
        if not cible.is_dir():
            cible.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(archive) as source:
                source.extractall(cible)
        return cible
    locale = racine_locale / cle / "exploitable"
    return locale if locale.is_dir() else None


def construire(cle: str, fichiers: list[Path], base: Path) -> Path:
    """Écrit `donnees/sources/{cle}.zip` avec les chemins relatifs à `base`."""
    ARCHIVES.mkdir(parents=True, exist_ok=True)
    cible = ARCHIVES / f"{cle}.zip"
    with zipfile.ZipFile(cible, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for fichier in sorted(fichiers):
            info = zipfile.ZipInfo(str(fichier.relative_to(base)).replace("\\", "/"))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.date_time = (1980, 1, 1, 0, 0, 0)
            archive.writestr(info, fichier.read_bytes())
    return cible
