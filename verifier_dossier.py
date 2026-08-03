"""Vérifie l'intégrité du dossier unique ORI-C.

Trois contrôles :

1. chaque entrée du manifeste existe et son empreinte est inchangée ;
2. aucun fichier du dossier n'échappe au manifeste ;
3. la structure attendue est présente, socle et trois branches.

Le script ne modifie rien. Code de sortie 0 si tout est conforme.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
MANIFESTE = RACINE / "MANIFEST.sha256"
EXCLUS = {"__pycache__", ".pytest_cache", ".git", ".claude", ".mplconfig"}
EXCLUS_SUFFIXES = {".pyc", ".pyo"}

STRUCTURE_ATTENDUE = [
    "ORI-C_Architecture_generale_du_programme.pdf",
    "documentation/POINT_D_ENTREE.md",
    "documentation/dossier_scientifique/DOSSIER_SCIENTIFIQUE_ORI-C.pdf",
    "documentation/dossier_scientifique/DOSSIER_SCIENTIFIQUE_ORI-C.docx",
    "README.md",
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


def fichiers_du_dossier() -> list[Path]:
    resultat = []
    for chemin in sorted(RACINE.rglob("*")):
        if chemin.is_dir():
            continue
        if any(partie in EXCLUS for partie in chemin.parts):
            continue
        if chemin.suffix in EXCLUS_SUFFIXES:
            continue
        if chemin.name in {MANIFESTE.name, "MANIFEST.sha256.json"}:
            continue
        resultat.append(chemin)
    return resultat


def lire_manifeste() -> dict[str, str]:
    entrees = {}
    for ligne in MANIFESTE.read_text(encoding="utf-8").splitlines():
        if not ligne.strip():
            continue
        empreinte, _, relatif = ligne.partition("  ")
        entrees[relatif] = empreinte
    return entrees


def main() -> int:
    if not MANIFESTE.exists():
        print("MANIFEST.sha256 absent.")
        return 1

    attendus = lire_manifeste()
    presents = {
        chemin.relative_to(RACINE).as_posix(): chemin
        for chemin in fichiers_du_dossier()
    }

    absents = sorted(set(attendus) - set(presents))
    non_listes = sorted(set(presents) - set(attendus))
    modifies = []
    for relatif, empreinte in attendus.items():
        chemin = presents.get(relatif)
        if chemin is None:
            continue
        if hashlib.sha256(chemin.read_bytes()).hexdigest() != empreinte:
            modifies.append(relatif)

    manquants_structure = [
        entree for entree in STRUCTURE_ATTENDUE
        if not (RACINE / entree).exists()
    ]

    for titre, liste in (
        ("Absents", absents),
        ("Modifiés", modifies),
        ("Non listés", non_listes),
        ("Structure manquante", manquants_structure),
    ):
        for entree in liste:
            print(f"  {titre:<20} {entree}")

    conformes = len(attendus) - len(absents) - len(modifies)
    print(
        f"\n{conformes} fichiers conformes, {len(modifies)} modifiés, "
        f"{len(absents)} absents, {len(non_listes)} non listés, "
        f"{len(manquants_structure)} entrées de structure manquantes."
    )
    return 0 if not (absents or modifies or non_listes or manquants_structure) else 1


if __name__ == "__main__":
    sys.exit(main())
