"""Vérifie l'intégrité du dossier ORI-C.

Le manifeste représente le contenu scientifique attendu. Pour un objet géré
par Git LFS, son SHA-256 attendu est l'OID déclaré dans le pointeur LFS. Le
script distingue donc trois situations :

1. le contenu réel est présent et son empreinte correspond au manifeste ;
2. un pointeur Git LFS valide est présent, mais l'objet n'est pas hydraté ;
3. le fichier est absent, non listé ou réellement modifié.

Par défaut, un objet LFS non hydraté empêche de déclarer l'archive canonique.
L'option ``--allow-lfs-pointers`` sert uniquement à contrôler un arbre source
GitHub ou une copie de travail avant hydratation.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path

RACINE = Path(__file__).resolve().parent
MANIFESTE = RACINE / "MANIFEST.sha256"
EXCLUS = {"__pycache__", ".pytest_cache", ".pytest-tmp", ".git", ".claude", ".mplconfig", "node_modules", "dist"}
EXCLUS_SUFFIXES = {".pyc", ".pyo"}

STRUCTURE_ATTENDUE = [
    "ORI-C_Architecture_generale_du_programme.pdf",
    "documentation/POINT_D_ENTREE.md",
    "documentation/dossier_scientifique/DOSSIER_SCIENTIFIQUE_ORI-C.pdf",
    "documentation/dossier_scientifique/DOSSIER_SCIENTIFIQUE_ORI-C.docx",
    "README.md",
    "VERSION",
    "AUTORITE_DES_DOCUMENTS.md",
    "ETAT_DES_TESTS.md",
    "00_socle/carte_relationnelle/REGENERATION_REQUISE.md",
    "00_socle/test_interventionnel/resultats_exhaustifs/CORRECTION_ANALYSE_EXHAUSTIVE.md",
    "02_branche_systeme_solaire/article/ERRATUM.md",
    "02_branche_systeme_solaire/FILTRAGES_HISTORIQUES.md",
    "02_branche_systeme_solaire/application_climat/README.md",
    "ARCHITECTURE.md",
    "ETAT_DES_PREUVES.md",
    "00_socle/CODEBOOK.md",
    "00_socle/PROTOCOLE_DONNEES.md",
    "00_socle/valider_donnees.py",
    "00_socle/README.md",
    "00_socle/carte_relationnelle",
    "ENVIRONNEMENT.md",
    "plateforme/campagne_maximale_reelle/BILAN_CANONIQUE.md",
    "00_socle/genealogie/arbre_genealogique.csv",
    "00_socle/genealogie/cloture_arbre.json",
    "00_socle/genealogie/correspondance_GM_GA.csv",
    "01_branche_matiere/genealogie/genealogie_matiere.csv",
    "01_branche_matiere/genealogie/cloture_genealogie.json",
    "plan_directeur/GRILLE_ETAPE_2.md",
    "plan_directeur/AUDIT_TRANSVERSAL.md",
    "plateforme/campagne_maximale_reelle/EXCLUSIONS.md",
    "plan_directeur/campagne_plateforme",
    "plan_directeur/campagne_plateforme/README.md",
    "plan_directeur/campagne_plateforme/resultats/results.json",
    "plan_directeur/campagne_plateforme/preenregistrement/catalogue_frozen.json",
    "01_branche_matiere/base_transitions",
    "01_branche_matiere/base_transitions/transitions_matiere.csv",
    "00_socle/test_interventionnel/PORTEE_WP_S2.md",
    "02_branche_systeme_solaire/couche_memoire_historique/results_stress/prospectif_c2",
    "02_branche_systeme_solaire/couche_memoire_historique/results_stress/prospectif_c2/RAPPORT_WP_C2.md",
    "02_branche_systeme_solaire/couche_memoire_historique/results_stress/tests_reels/RAPPORT_WP_C6.md",
    "plan_directeur",
    "plan_directeur/PLAN_DIRECTEUR_TESTS.md",
    "plan_directeur/AVANCEMENT_DU_PLAN.md",
    "plan_directeur/REGISTRE_HYPOTHESES.csv",
    "00_socle/carte_relationnelle/ANALYSE_GRAPHE.md",
    "00_socle/test_interventionnel",
    "00_socle/tests",
    "01_branche_matiere/README.md",
    "01_branche_matiere/article",
    "02_branche_systeme_solaire/README.md",
    "02_branche_systeme_solaire/article",
    "02_branche_systeme_solaire/application_climat",
    "02_branche_systeme_solaire/couche_memoire_historique/stress/f_tests_reels.py",
    "02_branche_systeme_solaire/couche_memoire_historique/stress/g_tests_reels_2.py",
    "02_branche_systeme_solaire/couche_memoire_historique/results_stress/tests_reels",
    "02_branche_systeme_solaire/couche_memoire_historique/results_stress/tests_reels/RAPPORT_TESTS_REELS.md",
    "02_branche_systeme_solaire/couche_memoire_historique/results_stress/tests_reels/RAPPORT_TESTS_REELS_2.md",
    "02_branche_systeme_solaire/couche_memoire_historique/stress/h_g2_corrige.py",
    "02_branche_systeme_solaire/couche_astronomique",
    "02_branche_systeme_solaire/couche_memoire_historique",
    "03_branche_vivant/README.md",
    "03_branche_vivant/programme_prebiotique",
    "03_branche_vivant/programme_prebiotique/PROGRAMME_PREBIOTIQUE.md",
    "03_branche_vivant/programme_prebiotique/valider_lignees.py",
    "03_branche_vivant/article",
]

LFS_PATTERN = re.compile(
    rb"\Aversion https://git-lfs\.github\.com/spec/v1\n"
    rb"oid sha256:([0-9a-f]{64})\n"
    rb"size ([0-9]+)\n?\Z"
)


@dataclass(frozen=True)
class PointeurLFS:
    oid: str
    taille: int


def lire_pointeur_lfs(chemin: Path) -> PointeurLFS | None:
    """Retourne les métadonnées LFS lorsque ``chemin`` est un pointeur valide."""
    try:
        if chemin.stat().st_size > 1024:
            return None
        donnees = chemin.read_bytes()
    except OSError:
        return None
    correspondance = LFS_PATTERN.fullmatch(donnees.replace(b"\r\n", b"\n"))
    if not correspondance:
        return None
    return PointeurLFS(
        oid=correspondance.group(1).decode("ascii"),
        taille=int(correspondance.group(2)),
    )


def empreinte(chemin: Path) -> str:
    valeur = hashlib.sha256()
    with chemin.open("rb") as flux:
        for bloc in iter(lambda: flux.read(1024 * 1024), b""):
            valeur.update(bloc)
    return valeur.hexdigest()


def fichiers_du_dossier() -> list[Path]:
    resultat = []
    for chemin in sorted(RACINE.rglob("*")):
        if chemin.is_dir():
            continue
        relatif = chemin.relative_to(RACINE)
        if any(partie in EXCLUS for partie in relatif.parts):
            continue
        if chemin.suffix in EXCLUS_SUFFIXES:
            continue
        if chemin.name in {MANIFESTE.name, "MANIFEST.sha256.json"}:
            continue
        resultat.append(chemin)
    return resultat


def lire_manifeste() -> dict[str, str]:
    entrees: dict[str, str] = {}
    for ligne in MANIFESTE.read_text(encoding="utf-8").splitlines():
        if not ligne.strip():
            continue
        valeur, separateur, relatif = ligne.partition("  ")
        if not separateur or not re.fullmatch(r"[0-9a-f]{64}", valeur):
            raise ValueError(f"Ligne de manifeste invalide : {ligne!r}")
        entrees[relatif] = valeur
    return entrees


def analyser() -> dict[str, list[str] | int]:
    attendus = lire_manifeste()
    presents = {
        chemin.relative_to(RACINE).as_posix(): chemin
        for chemin in fichiers_du_dossier()
    }

    absents = sorted(set(attendus) - set(presents))
    non_listes = sorted(set(presents) - set(attendus))
    modifies: list[str] = []
    lfs_non_hydrates: list[str] = []

    for relatif, attendu in attendus.items():
        chemin = presents.get(relatif)
        if chemin is None:
            continue
        pointeur = lire_pointeur_lfs(chemin)
        if pointeur is not None:
            if pointeur.oid == attendu:
                lfs_non_hydrates.append(relatif)
            else:
                modifies.append(relatif)
            continue
        if empreinte(chemin) != attendu:
            modifies.append(relatif)

    manquants_structure = [
        entree for entree in STRUCTURE_ATTENDUE
        if not (RACINE / entree).exists()
    ]
    conformes = len(attendus) - len(absents) - len(modifies) - len(lfs_non_hydrates)
    return {
        "conformes": conformes,
        "absents": absents,
        "modifies": modifies,
        "non_listes": non_listes,
        "lfs_non_hydrates": sorted(lfs_non_hydrates),
        "manquants_structure": manquants_structure,
    }


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument(
        "--allow-lfs-pointers",
        action="store_true",
        help=(
            "autoriser les pointeurs LFS valides pour contrôler un arbre source ; "
            "cette option ne certifie pas une archive canonique autonome"
        ),
    )
    analyseur.add_argument(
        "--verbose",
        action="store_true",
        help="afficher toutes les entrées au lieu de limiter chaque catégorie à 20",
    )
    args = analyseur.parse_args(argv)

    if not MANIFESTE.exists():
        print("MANIFEST.sha256 absent.")
        return 1

    try:
        resultat = analyser()
    except (OSError, ValueError) as exc:
        print(f"Manifeste illisible : {exc}")
        return 1

    groupes = (
        ("Absents", resultat["absents"]),
        ("Modifiés", resultat["modifies"]),
        ("Non listés", resultat["non_listes"]),
        ("LFS non hydratés", resultat["lfs_non_hydrates"]),
        ("Structure manquante", resultat["manquants_structure"]),
    )
    for titre, liste in groupes:
        visibles = liste if args.verbose else liste[:20]
        for entree in visibles:
            print(f"  {titre:<20} {entree}")
        if not args.verbose and len(liste) > len(visibles):
            print(f"  {titre:<20} ... et {len(liste) - len(visibles)} autres")

    print(
        f"\n{resultat['conformes']} contenus conformes, "
        f"{len(resultat['lfs_non_hydrates'])} objets LFS non hydratés, "
        f"{len(resultat['modifies'])} modifiés, "
        f"{len(resultat['absents'])} absents, "
        f"{len(resultat['non_listes'])} non listés, "
        f"{len(resultat['manquants_structure'])} entrées de structure manquantes."
    )

    problemes = any(
        resultat[cle]
        for cle in ("absents", "modifies", "non_listes", "manquants_structure")
    )
    if problemes:
        return 1
    if resultat["lfs_non_hydrates"] and not args.allow_lfs_pointers:
        print(
            "\nArchive non autonome : exécuter `git lfs pull`, puis relancer "
            "le vérificateur sans option."
        )
        return 2
    if resultat["lfs_non_hydrates"]:
        print(
            "\nArbre source cohérent, mais non certifié comme archive canonique "
            "autonome car des objets Git LFS restent à hydrater."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
