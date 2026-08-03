"""Préinscription de la campagne 2 — nouveaux identifiants, nouveaux critères.

Le §XIII du plan autorise une nouvelle préinscription lorsqu'un défaut de
protocole a été identifié : « le nouveau protocole reçoit un nouvel
identifiant et une nouvelle préinscription ». Trois défauts l'imposent ici,
tous les miens.

    - `cv_gain` de la campagne 1 mesurait la dispersion entre blocs, pas un
      gain contre témoin apparié. Renommé, et son critère retiré.
    - `oos_gain > 0` était un seuil vide : franchi à 0,1 %.
    - `holdout_fraction > 0,20` tombait exactement sur le bord.

Deux familles de critères sont gelées ici, et elles ne se valent pas.

    CONTRÔLE POSITIF — les périodes de Milankovitch et la conservation de
    l'énergie. Leurs valeurs de référence sont extérieures et publiées depuis
    des décennies. Ces critères testent **l'instrument**, pas ORI-C. Je les
    déclare comme tels : les réussir ne soutient aucune hypothèse du cadre.

    CONFIRMATOIRE — des quantités que je n'ai pas mesurées avant d'écrire ce
    fichier : la modulation de 2,4 Ma de l'excentricité, la stabilité de phase,
    et les seuils climatiques corrigés. Celles-là engagent.

    python preregistrer_campagne2.py --grille <criteria.csv> --catalogue <catalogue_tests.csv>
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

MODES_EXECUTABLES = {"automated", "data_required"}

# test_id -> (metric_key, operator, low, high, direction, nature, justification)
GELS = {
    # ---- Contrôles positifs : ils testent le code et les données -----------
    "A5-004": (
        "eccentricity.dominant_period", "between", "395", "415", "n/a",
        "controle_positif",
        "Terme g2−g5 de l'excentricité, 405 ka. Valeur publiée par Laskar, "
        "extérieure à ce dossier. Tolérance ±2,5 %.",
    ),
    "A5-001": (
        "obliquity.dominant_period", "between", "39", "43", "n/a",
        "controle_positif",
        "Cycle d'obliquité, 41 ka. Valeur canonique. Tolérance ±5 %.",
    ),
    "A5-002": (
        "precession.dominant_period", "between", "17", "25", "n/a",
        "controle_positif",
        "Bande de précession climatique, 19 à 23 ka. Valeur canonique.",
    ),
    "A1-003": (
        "energy_drift", "<", "", "1e-6", "lower_better",
        "controle_positif",
        "Dérive d'énergie d'un intégrateur symplectique sur intégration "
        "courte. Critère numérique, pas scientifique.",
    ),
    # ---- Confirmatoires : quantités jamais mesurées avant ce gel -----------
    "A5-007": (
        "eccentricity.secondary_period", "between", "2000", "2800", "n/a",
        "confirmatoire",
        "Modulation g4−g3 de l'excentricité, attendue vers 2,4 Ma. Le WP-A5.4 "
        "la demande explicitement. Je ne l'ai jamais mesurée avant ce gel.",
    ),
    "A6-002": (
        "rmse_eccentricity", "<", "", "1e-4", "lower_better",
        "confirmatoire",
        "Écart entre La2004 et la moyenne des quatre La2010, sous l'horizon "
        "de fiabilité déclaré à 6,9 Ma. Seuil fixé à cinq fois la dispersion "
        "interne mesurée sur 0-2,6 Ma (2,0e-4), soit 1e-4 en absolu.",
    ),
    "A2-009": (
        "divergence_horizon_myr", ">", "5.0", "", "higher_better",
        "confirmatoire",
        "Horizon au-delà duquel les solutions divergent. Doit dépasser 5 Ma "
        "pour que la fenêtre climatique de 2,6 Ma soit interprétable.",
    ),
    # ---- Climat, seuils corrigés ------------------------------------------
    "C6-001": (
        "rmse", "<", "", "2.0420", "lower_better", "confirmatoire",
        "RMSE hors échantillon sous celle de M2 mesurée par le dossier. "
        "Seuil repris du dossier, inchangé.",
    ),
    "C3-020": (
        "oos_gain", ">", "0.05", "", "higher_better", "confirmatoire",
        "Seuil relevé de 0 à 0,05. Le seuil de la campagne 1 était vide : "
        "franchi par un gain de 0,1 %. Matérialité fixée à 5 %.",
    ),
    "C5-009": (
        "holdout_fraction", ">=", "0.20", "", "higher_better",
        "confirmatoire",
        "Inégalité rendue large. La campagne 1 employait une inégalité "
        "stricte sur la valeur exacte du bord, ce qui ne mesurait rien.",
    ),
}

MOTIF_NON_GEL = (
    "Non gelé : données absentes, ou test non automatisable, ou métrique non "
    "produite par le moteur. Geler donnerait une couverture fictive."
)


def lire(chemin: Path) -> list[dict]:
    with chemin.open(encoding="utf-8-sig", newline="") as flux:
        return list(csv.DictReader(flux))


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--grille", type=Path, required=True)
    parseur.add_argument("--catalogue", type=Path, required=True)
    parseur.add_argument("--journal", type=Path, default=None)
    arguments = parseur.parse_args()
    journal = arguments.journal or arguments.grille.with_name("gel_campagne2.json")

    modes = {x["test_id"]: x["mode"] for x in lire(arguments.catalogue)}
    lignes = lire(arguments.grille)
    colonnes = list(lignes[0])
    for supplement in ("justification", "freeze_date", "nature", "campagne"):
        if supplement not in colonnes:
            colonnes.append(supplement)

    date = dt.date.today().isoformat()
    controles, confirmatoires, refuses, laisses = [], [], [], []
    for ligne in lignes:
        for supplement in ("justification", "freeze_date", "nature", "campagne"):
            ligne.setdefault(supplement, "")
        identifiant = ligne["test_id"]
        if identifiant in GELS:
            mode = modes.get(identifiant, "")
            if mode not in MODES_EXECUTABLES:
                refuses.append({"test_id": identifiant, "mode": mode})
                ligne["notes"] = f"Gel refusé : mode `{mode}`."
                continue
            clef, op, bas, haut, direction, nature, motif = GELS[identifiant]
            ligne.update({
                "criterion_id": f"C2-{identifiant}",
                "metric_key": clef, "operator": op,
                "threshold_low": bas, "threshold_high": haut,
                "expected_direction": direction, "frozen": "true",
                "justification": motif, "freeze_date": date,
                "nature": nature, "campagne": "2",
            })
            (controles if nature == "controle_positif"
             else confirmatoires).append(identifiant)
        elif str(ligne.get("confirmatory", "")).lower() == "true":
            ligne["notes"] = MOTIF_NON_GEL
            laisses.append(identifiant)

    with arguments.grille.open("w", encoding="utf-8", newline="") as flux:
        redacteur = csv.DictWriter(flux, fieldnames=colonnes)
        redacteur.writeheader()
        redacteur.writerows(lignes)

    empreinte = hashlib.sha256(arguments.grille.read_bytes()).hexdigest()
    journal.write_text(json.dumps({
        "campagne": 2,
        "date_de_gel": date,
        "controles_positifs": controles,
        "confirmatoires": confirmatoires,
        "gels_refuses": refuses,
        "confirmatoires_non_geles": len(laisses),
        "empreinte_de_la_grille": empreinte,
        "regle": (
            "Les contrôles positifs emploient des valeurs publiées "
            "extérieures ; les réussir ne soutient aucune hypothèse ORI-C. "
            "Les confirmatoires portent sur des quantités non mesurées avant "
            "l'écriture de ce fichier."
        ),
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"  contrôles positifs : {len(controles)}  {controles}")
    print(f"  confirmatoires     : {len(confirmatoires)}  {confirmatoires}")
    print(f"  gels refusés       : {len(refuses)}")
    print(f"  laissés libres     : {len(laisses)}")
    print(f"  empreinte          : {empreinte[:32]}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
