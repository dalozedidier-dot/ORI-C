"""Gèle les critères des seuls tests confirmatoires réellement exécutables.

Correctif 3. La version précédente gelait `C2-006` et `C5-010`, dont le mode
est `human_review` ou `laboratory` : ils finissent en `not_run`, et geler leur
critère donnait une couverture fictive. Le script lit désormais le mode dans le
catalogue et **refuse de geler tout test non automatisable**, au lieu de s'en
remettre à une liste écrite à la main.

Correctif 4. Tous les chemins sont des arguments. Aucun chemin absolu.

Les seuils ne sont pas choisis ici. Ils reprennent ceux que le dossier ORI-C
avait déjà préenregistrés avant toute lecture de résultat : un modèle doit
battre son témoin de complexité égale, soit un gain relatif strictement
positif ; et sa RMSE hors échantillon doit passer sous celle de M2 mesurée sur
la même fenêtre.

    python geler_criteres.py --grille <criteria.csv> --catalogue <catalogue_tests.csv>
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

# Modes pour lesquels un moteur produit une valeur. Les autres attendent un
# humain, un laboratoire ou un code externe : leur critère reste non gelé.
MODES_EXECUTABLES = {"automated", "data_required"}

# test_id -> (metric_key, operator, low, high, direction, justification)
GELS = {
    "C6-001": (
        "rmse", "<", "", "2.0420", "lower_better",
        "RMSE hors échantillon strictement inférieure à celle de M2 mesurée "
        "par le dossier sur la même fenêtre. Seuil repris du dossier.",
    ),
    "C1-008": (
        "cv_gain", ">", "0.0", "", "higher_better",
        "Validation croisée temporelle : gain relatif strictement positif "
        "contre le pire bloc. Critère du dossier.",
    ),
    "C3-020": (
        "oos_gain", ">", "0.0", "", "higher_better",
        "Prédiction hors échantillon : gain strictement positif contre le "
        "témoin apparié. §6 du PROTOCOLE_DONNEES.",
    ),
    "C7-010": (
        "failed_validations", "<", "", "2", "lower_better",
        "Règle d'arrêt XIII.1 : abandon après deux échecs sur jeux "
        "confirmatoires indépendants.",
    ),
    "C5-009": (
        "holdout_fraction", ">", "0.20", "", "higher_better",
        "Au moins un cinquième de l'archive réservé et jamais ajusté.",
    ),
    # C2-006 et C5-010 ont été retirés : modes `human_review` et `laboratory`.
}

MOTIF_NON_GEL = (
    "Non gelé : soit les données manquent, soit le test n'est pas "
    "automatisable. Geler ici donnerait une couverture fictive."
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
    journal = arguments.journal or arguments.grille.with_name("gel.json")

    modes = {x["test_id"]: x["mode"] for x in lire(arguments.catalogue)}
    lignes = lire(arguments.grille)
    colonnes = list(lignes[0])
    for supplement in ("justification", "freeze_date"):
        if supplement not in colonnes:
            colonnes.append(supplement)

    date = dt.date.today().isoformat()
    geles, refuses, laisses = [], [], []
    for ligne in lignes:
        ligne.setdefault("justification", "")
        ligne.setdefault("freeze_date", "")
        identifiant = ligne["test_id"]
        mode = modes.get(identifiant, "")
        if identifiant in GELS:
            if mode not in MODES_EXECUTABLES:
                refuses.append({"test_id": identifiant, "mode": mode})
                ligne["notes"] = (
                    f"Gel refusé : mode `{mode}`, aucun moteur ne produit de "
                    "valeur."
                )
                continue
            metrique, operateur, bas, haut, direction, motif = GELS[identifiant]
            ligne.update({
                "metric_key": metrique, "operator": operateur,
                "threshold_low": bas, "threshold_high": haut,
                "expected_direction": direction, "frozen": "true",
                "justification": motif, "freeze_date": date,
            })
            geles.append(identifiant)
        elif str(ligne.get("confirmatory", "")).lower() == "true":
            ligne["notes"] = MOTIF_NON_GEL
            laisses.append(identifiant)

    with arguments.grille.open("w", encoding="utf-8", newline="") as flux:
        redacteur = csv.DictWriter(flux, fieldnames=colonnes)
        redacteur.writeheader()
        redacteur.writerows(lignes)

    empreinte = hashlib.sha256(arguments.grille.read_bytes()).hexdigest()
    journal.write_text(json.dumps({
        "date_de_gel": date,
        "criteres_geles": geles,
        "gels_refuses_car_non_automatisables": refuses,
        "confirmatoires_non_geles": len(laisses),
        "motif_de_non_gel": MOTIF_NON_GEL,
        "empreinte_de_la_grille": empreinte,
        "regle": (
            "Aucun résultat n'a été lu avant l'écriture de ce fichier. Les "
            "seuils reprennent ceux déjà préenregistrés par le dossier ORI-C."
        ),
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"  gelés                : {len(geles)}  {geles}")
    print(f"  gels refusés         : {len(refuses)}  "
          f"{[r['test_id'] + ' (' + r['mode'] + ')' for r in refuses]}")
    print(f"  confirmatoires libres: {len(laisses)}")
    print(f"  empreinte            : {empreinte[:32]}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
