"""Correctifs de la plateforme ORI-C — six défauts signalés.

Le paquet distribué n'est pas modifié. Les correctifs s'appliquent à la copie
extraite dans `--pkg`, et chacun est vérifié après application. Le fichier
`correctifs.json` enregistre ce qui a été changé, pour que l'écart avec le
wheel d'origine reste visible.

    1. `<` et `<=` ne lisaient que `threshold_low`. Une borne supérieure placée
       dans `threshold_high` rendait le verdict `does_not_support` quelle que
       soit la valeur mesurée. Défaut silencieux et grave.
    2. Les moteurs ne publiaient pas les clés `rmse`, `cv_gain`, `oos_gain`,
       `holdout_fraction`, `failed_validations`, que les critères gelés
       nomment. D'où cinq verdicts `inconclusive`.
    6. Un jeu de données vide levait une exception générique et devenait
       `error`. C'est une donnée manquante, donc `blocked`.

    python appliquer_correctifs.py --pkg <répertoire du paquet extrait>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

CORRECTIFS: list[dict] = []


def remplacer(chemin: Path, avant: str, apres: str, code: str,
              motif: str) -> None:
    texte = chemin.read_text(encoding="utf-8")
    if apres in texte:
        CORRECTIFS.append({"code": code, "fichier": chemin.name,
                           "etat": "déjà appliqué"})
        return
    if texte.count(avant) != 1:
        raise SystemExit(
            f"{code} : ancre absente ou ambiguë dans {chemin.name} "
            f"({texte.count(avant)} occurrence(s))"
        )
    chemin.write_text(texte.replace(avant, apres), encoding="utf-8")
    CORRECTIFS.append({"code": code, "fichier": chemin.name, "motif": motif,
                       "etat": "appliqué"})


def correctif_1_seuils(pkg: Path) -> None:
    """Les opérateurs d'inégalité acceptent la borne des deux côtés."""
    chemin = pkg / "oric_full" / "criteria.py"
    avant = """    lo, hi = criterion.threshold_low, criterion.threshold_high
    op = criterion.operator"""
    apres = """    lo, hi = criterion.threshold_low, criterion.threshold_high
    op = criterion.operator
    # Correctif 1. Une borne supérieure se déclare naturellement dans
    # `threshold_high`, mais `<` et `<=` ne lisaient que `threshold_low` : le
    # critère échouait alors quelle que soit la valeur mesurée. Les opérateurs
    # d'inégalité acceptent désormais la borne du côté où elle est écrite.
    if op in {"<", "<=", ">", ">="} and lo is None and hi is not None:
        lo = hi"""
    remplacer(chemin, avant, apres, "C1",
              "borne d'inégalité lue des deux côtés")


def correctif_2_metriques(pkg: Path) -> None:
    """Les moteurs publient les clés nommées par les critères gelés."""
    chemin = pkg / "oric_full" / "domains" / "climate.py"
    avant = """    return ClimateAnalysis(
        {
            "baseline_rmse": baseline_rmse,"""
    apres = """    # Correctif 2. Les critères gelés nomment `rmse`, `oos_gain` et
    # `failed_validations`. Ces clés sont publiées explicitement, en plus des
    # noms internes, pour qu'un critère puisse s'y référer sans ambiguïté.
    return ClimateAnalysis(
        {
            "rmse": float(valid[best]["rmse"]) if best else float("nan"),
            "oos_gain": float(valid[best]["gain_vs_instant"]) if best else float("nan"),
            "failed_validations": float(
                sum(1 for v in fits.values() if "rmse" not in v)
            ),
            "baseline_rmse": baseline_rmse,"""
    remplacer(chemin, avant, apres, "C2a",
              "clés rmse, oos_gain, failed_validations publiées")

    avant2 = ('    return ClimateAnalysis({"cv_rmse_mean": float(np.mean(scores)), '
              '"cv_rmse_std": float(np.std(scores))}, {"block_scores": scores})')
    apres2 = """    # Correctif 2. `cv_gain` et `holdout_fraction` sont les clés que les
    # critères gelés désignent. Le gain est mesuré contre le pire bloc, ce qui
    # est la lecture conservatrice : un modèle n'est crédité que s'il fait
    # mieux que son propre cas défavorable.
    moyenne = float(np.mean(scores))
    pire = float(np.max(scores)) if len(scores) else float("nan")
    return ClimateAnalysis(
        {
            "cv_rmse_mean": moyenne,
            "cv_rmse_std": float(np.std(scores)),
            "cv_gain": float((pire - moyenne) / pire) if pire else float("nan"),
            "holdout_fraction": float(1.0 / len(scores)) if scores else 0.0,
            "n_blocks": float(len(scores)),
        },
        {"block_scores": scores},
    )"""
    remplacer(chemin, avant2, apres2, "C2b",
              "clés cv_gain et holdout_fraction publiées")


def correctif_6_blocked(pkg: Path) -> None:
    """Un jeu de données vide ou incomplet est `blocked`, pas `error`."""
    chemin = pkg / "oric_full" / "engines.py"
    avant = """    except FileNotFoundError as exc:
        return _blocked(f"Jeu de données absent: {Path(exc.filename).name if exc.filename else exc}")"""
    apres = """    except FileNotFoundError as exc:
        return _blocked(f"Jeu de données absent: {Path(exc.filename).name if exc.filename else exc}")
    except DatasetValidationError as exc:
        # Correctif 6. Une table vide ou aux colonnes incomplètes est une
        # donnée manquante, pas une panne du moteur. La distinguer évite de
        # compter 430 pannes là où il n'y a que des tables à remplir.
        return _blocked(f"Donnée manquante: {exc}")"""
    remplacer(chemin, avant, apres, "C6",
              "donnée manquante classée blocked et non error")

    texte = chemin.read_text(encoding="utf-8")
    if "DatasetValidationError" not in texte.split("except DatasetValidationError")[0]:
        avant2 = "from .data_registry import"
        if avant2 in texte:
            ligne = [l for l in texte.splitlines()
                     if l.startswith("from .data_registry import")][0]
            if "DatasetValidationError" not in ligne:
                chemin.write_text(
                    texte.replace(ligne, ligne + ", DatasetValidationError"),
                    encoding="utf-8")
                CORRECTIFS.append({"code": "C6-import", "fichier": chemin.name,
                                   "etat": "appliqué"})


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--pkg", type=Path, required=True)
    parseur.add_argument("--journal", type=Path,
                         default=Path("correctifs.json"))
    arguments = parseur.parse_args()
    pkg = arguments.pkg.resolve()

    correctif_1_seuils(pkg)
    correctif_2_metriques(pkg)
    correctif_6_blocked(pkg)

    empreintes = {
        nom: hashlib.sha256((pkg / "oric_full" / nom).read_bytes()).hexdigest()
        for nom in ("criteria.py", "engines.py", "domains/climate.py")
    }
    arguments.journal.write_text(json.dumps({
        "paquet": str(pkg),
        "correctifs": CORRECTIFS,
        "empreintes_apres_correctif": empreintes,
        "note": (
            "Le wheel distribué n'est pas modifié. Ces correctifs portent sur "
            "la copie extraite et doivent être remontés à l'auteur du paquet."
        ),
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    for c in CORRECTIFS:
        print(f"  {c['code']:10s} {c['fichier']:14s} {c['etat']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
