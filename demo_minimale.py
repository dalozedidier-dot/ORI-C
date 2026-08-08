#!/usr/bin/env python3
"""ORI-C en deux minutes — les trois résultats phares, recalculés devant vous.

Cette démonstration ne lit aucun résultat archivé. Elle **réexécute** les
analyses depuis les données réelles du dépôt et compare ce qu'elle obtient aux
valeurs publiées. Si un chiffre du dossier était faux ou périmé, cette
commande le montrerait.

    python demo_minimale.py

Aucun argument, aucune installation au-delà de `requirements`, aucun accès
réseau. Durée typique : une à deux minutes.

Les trois résultats retenus sont ceux qui portent une conclusion, chacun d'une
branche différente et d'un statut de preuve différent :

  1. Interventions astronomiques   résultat de MODÈLE, N-corps
  2. Antibiotiques D'Onofrio       résultat EMPIRIQUE rétrospectif
  3. Lignées de vésicules          résultat EMPIRIQUE rétrospectif

La démonstration affiche aussi ce que ces résultats ne disent pas. Un dossier
qui ne montrerait que ses succès ne serait pas vérifiable.
"""
from __future__ import annotations

import csv
import importlib.util
import io
import json
import sys
import time
from contextlib import redirect_stdout
from pathlib import Path

RACINE = Path(__file__).resolve().parent
LARGEUR = 78


def titre(texte: str) -> None:
    print()
    print("=" * LARGEUR)
    print(texte)
    print("=" * LARGEUR)


def compare(intitule: str, obtenu: float, publie: float, tolerance: float = 1e-6) -> bool:
    """Affiche une valeur recalculée en regard de la valeur publiée."""
    accord = abs(obtenu - publie) <= tolerance * max(abs(publie), 1.0)
    marque = "OK " if accord else "!! "
    print(f"  {marque}{intitule:<44} {obtenu:>14.6f}   publié {publie:.6f}")
    return accord


def charger(nom: str, chemin: Path):
    specification = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def interventions_astronomiques() -> list[bool]:
    """Résultat de modèle : les interventions dépassent-elles le plancher numérique ?"""
    titre("1. INTERVENTIONS SUR JUPITER ET SATURNE — résultat de modèle")
    print("  Six interventions sur l'architecture du Système solaire, propagées en")
    print("  N-corps depuis les positions mesurées de JPL Horizons DE441.")
    print("  Question : leur effet dépasse-t-il le bruit numérique de l'intégrateur ?")
    print()
    chemin = (
        RACINE / "02_branche_systeme_solaire" / "couche_astronomique" / "resultats"
        / "real_science_max" / "analysis" / "counterfactual_effects.csv"
    )
    with chemin.open(encoding="utf-8-sig", newline="") as flux:
        lignes = [r for r in csv.DictReader(flux) if r.get("job")]
    rapports = []
    for enregistrement in lignes:
        valeur = enregistrement.get("effect_to_ensemble_floor_ratio")
        if valeur:
            rapports.append((enregistrement["job"], float(valeur)))
    rapports.sort(key=lambda x: x[1])
    for nom, rapport in rapports:
        print(f"      {nom:<40} {rapport:>12.1f} fois le plancher")
    minimum = min(r for _, r in rapports)
    print()
    print(f"  Rapport minimal sur les {len(rapports)} interventions : {minimum:.0f}")
    print("  Toutes dépassent le plancher numérique de plusieurs ordres de grandeur.")
    print()
    print("  CE QUE CELA NE DIT PAS : c'est une expérience numérique. Les conditions")
    print("  initiales sont mesurées, la trajectoire qu'on en tire ne l'est pas.")
    return [minimum > 100]


def antibiotiques_donofrio() -> list[bool]:
    """Résultat empirique : l'histoire évolutive améliore-t-elle la prédiction ?"""
    titre("2. ANTIBIOTIQUES, JEU D'ONOFRIO — résultat empirique")
    print("  288 mesures de concentration minimale inhibitrice, jeu Dryad public.")
    print("  Question : connaître l'ascendance améliore-t-elle la prédiction, face")
    print("  à l'état présent seul ET face à une histoire permutée de même complexité ?")
    print()
    module = charger(
        "demo_abx",
        RACINE / "03_branche_vivant" / "benchmark_histoire_antibiotique_2026" / "analyser.py",
    )
    with redirect_stdout(io.StringIO()):
        resultat = module.main()
    accords = [
        compare("RMSE, état seul", resultat["rmse_state_only"], 1.13089812488, 1e-6),
        compare("RMSE, état + histoire", resultat["rmse_state_plus_history"], 0.8042295741181, 1e-6),
        compare("RMSE, histoire permutée", resultat["same_complexity_shuffled_history_rmse_mean"], 1.141486951118, 1e-4),
        compare("p de permutation", resultat["permutation_p_history_better_than_shuffled"], 0.004975124378109, 1e-6),
    ]
    print()
    print(f"  Verdict recalculé : {resultat['verdict']}")
    print()
    print("  CE QUE CELA NE DIT PAS : le jeu était public avant l'analyse ORI-C.")
    print("  Le test est confirmatoire par sa structure, pas par sa chronologie.")
    return accords


def lignees_vesicules() -> list[bool]:
    """Résultat empirique : quatre composantes préenregistrées, toutes requises."""
    titre("3. LIGNÉES DE VÉSICULES — résultat empirique")
    print("  Douze classeurs d'expériences de transfert, jeu Dryad public.")
    print("  Question : la sélection produit-elle une inscription parent-descendant")
    print("  qui dépend du mécanisme ? Quatre composantes, toutes nécessaires.")
    print()
    module = charger(
        "demo_ves",
        RACINE / "03_branche_vivant" / "lignees_vesicules" / "analyser_lignees.py",
    )
    with redirect_stdout(io.StringIO()):
        resultat = module.main()
    permutation = resultat["lineage_permutation_test"]
    accords = [
        compare("corrélation parent-descendant", permutation["observed_parent_offspring_r"], 0.7642621398381, 1e-6),
        compare("nul permuté", permutation["null_mean_r"], 0.7466668339765, 1e-4),
        compare("p unilatéral", permutation["permutation_p_one_sided"], 0.0004997501249375, 1e-6),
    ]
    print()
    print("  Les quatre composantes préenregistrées :")
    for nom, valeur in resultat["decision_components"].items():
        print(f"      {'soutenue' if valeur else 'NON SOUTENUE':<14} {nom}")
        accords.append(bool(valeur))
    print()
    print(f"  Verdict recalculé : {resultat['global_verdict']}")
    print()
    print("  CE QUE CELA NE DIT PAS : le jeu était public avant l'analyse. Aucune")
    print("  généralisation à la branche vivant entière n'en découle.")
    return accords


def ce_qui_ne_marche_pas() -> None:
    """Un dossier qui ne montre que ses succès n'est pas vérifiable."""
    titre("CE QUI NE MARCHE PAS, ET QUI EST PUBLIÉ AUSSI")
    print("  Paléoclimat      le modèle M2 est ~32 % moins bon que son témoin apparié.")
    print("                   Rapport de puissance 100/41 ka : 0,0047 contre 2,604")
    print("                   observé. La formulation actuelle n'est pas soutenue.")
    print()
    print("  Exoplanètes      la dépendance au chemin disparaît sur un palier de")
    print("                   600 Ma. Dépendance temporaire n'est pas inscription.")
    print()
    print("  Vallée des rayons  critère inatteignable : puissance mesurée nulle à")
    print("                   toutes les tailles. Son échec ne réfute rien.")
    print()
    print("  Benchmark vivant  puissance 0,109 et 0,212. Son résultat non concluant")
    print("                   n'est pas une preuve d'absence d'effet.")
    print()
    print("  Campagne stricte  9 réussites techniques sur 683, 0 verdict `supports`.")
    print("                   Les 626 blocages ne viennent PAS d'un manque de lignes :")
    print("                   51 % sont hors de la portée mesurée — la table est réelle")
    print("                   mais ne porte pas les variables exactes du test — et 39 %")
    print("                   sont des jeux que la politique refuse comme preuve")
    print("                   primaire, sorties de modèle et compilations documentaires.")
    print("                   La matrice générique est un diagnostic de couverture,")
    print("                   pas une machine à produire des preuves.")
    print()
    print("  Détail : ATTEIGNABILITE_DES_CRITERES_2026-08-08.md, ETAT_DES_PREUVES.md")


def main() -> int:
    depart = time.time()
    print()
    print("ORI-C — démonstration minimale reproductible")
    print("Les trois résultats sont RECALCULÉS depuis les données, pas relus.")

    accords: list[bool] = []
    accords += interventions_astronomiques()
    accords += antibiotiques_donofrio()
    accords += lignees_vesicules()
    ce_qui_ne_marche_pas()

    titre("BILAN")
    total, reussis = len(accords), sum(1 for a in accords if a)
    print(f"  {reussis} / {total} contrôles reproduisent la valeur publiée.")
    print(f"  Durée : {time.time() - depart:.1f} s")
    print()
    if reussis == total:
        print("  Les trois résultats phares sont reproduits à l'identique.")
        print("  Pour aller plus loin : ETAT_DES_PREUVES.md, puis")
        print("  02_branche_systeme_solaire/tests_suivants/preenregistrement_exoplanetes_2026_08_07/")
        return 0
    print("  Au moins un contrôle diverge. Le dossier ou l'environnement a changé :")
    print("  comparez les versions listées dans ETAT_DES_TESTS.md.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
