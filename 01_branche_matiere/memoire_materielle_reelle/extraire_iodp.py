#!/usr/bin/env python3
"""Extrait les mesures de rémanence IODP au schéma de la campagne.

Correspondance entre les colonnes du magnétomètre et le schéma ORI-C. Elle est
établie une fois, ici, et rien ne l'infère ailleurs :

| colonne IODP                | champ du schéma      | rôle |
|---|---|---|
| `Text ID`                   | `physical_sample_id` | l'unité expérimentale |
| `Exp`, `Site`, `Hole`       | `history_id`         | contexte de dépôt |
| `Treatment type`            | `ablation_type`      | NRM, AD, TD, IRM, ARM |
| `Treatment value`           | `dose`               | mT pour AD, °C pour TD |
| `Total intensity (A/m)`     | `trace_value`        | la rémanence qui subsiste |
| `Inclination`, `Declination`| direction            | orientation de l'inscription |
| `Top depth CSF-A (m)`       | `profondeur`         | **témoin négatif** |

La profondeur sert de témoin négatif et ce choix n'est pas arbitraire : c'est une
propriété de l'échantillon fixée avant toute mesure, qu'aucune désaimantation ne
peut modifier. Si la statistique la déclare sensible au traitement, c'est la
statistique qui est fautive, pas la physique. C'est la leçon de l'obliquité
terrestre, transposée.

Une ligne du fichier source est une **mesure**, pas une unité. Un échantillon
porte typiquement dix mesures : une NRM puis les étapes successives. Confondre les
deux ferait passer 130 000 mesures pour 130 000 réplications.

Deux tables sont donc écrites, et leur destination diffère.

**Par mesure**, 18,8 Mo — elle reste en local. C'est la matière première des
tests, elle n'a rien à faire dans un dépôt : un dépôt Git n'est pas un entrepôt.

**Par échantillon**, une ligne par unité expérimentale, quelques centaines de
kilooctets — c'est elle qui est versionnée. Elle porte tout ce dont un lecteur a
besoin pour refaire le verdict : intensité initiale, nombre d'étapes, plage de
dose, fraction restante, corrélation dose-intensité. La table par mesure se
régénère depuis les sources, dont la provenance est inscrite.

    python extraire_iodp.py
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ICI = Path(__file__).resolve().parent
SOURCES = ICI / "SOURCES.json"
SORTIE = ICI / "derive"

COLONNE_INTENSITE = "Total intensity (A/m)"
COLONNE_TRAITEMENT = "Treatment type"
COLONNE_DOSE = "Treatment value (mT or deg C or Agico code)"
COLONNE_ECHANTILLON = "Text ID"
COLONNE_PROFONDEUR = "Top depth CSF-A (m)"
COLONNE_INCLINAISON = "Inclination (deg)"
COLONNE_DECLINAISON = "Declination (deg)"


def flottant(valeur) -> float | None:
    if valeur in (None, ""):
        return None
    texte = str(valeur).strip().replace(" ", "")
    try:
        return float(texte)
    except ValueError:
        return None


def rang_correlation(mesures: list[dict]) -> float:
    """Spearman entre dose et intensité, sur les mesures d'un seul échantillon."""
    if len(mesures) < 3:
        return float("nan")
    doses = [m["dose"] for m in mesures]
    valeurs = [m["trace_value"] for m in mesures]

    def rangs(v):
        ordre = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        for position, indice in enumerate(ordre):
            r[indice] = float(position)
        return r

    rd, rv = rangs(doses), rangs(valeurs)
    n = len(rd)
    md, mv = sum(rd) / n, sum(rv) / n
    num = sum((a - md) * (b - mv) for a, b in zip(rd, rv))
    den = (sum((a - md) ** 2 for a in rd) * sum((b - mv) ** 2 for b in rv)) ** 0.5
    return num / den if den else float("nan")


def extraire_source(cle: str, racine: Path) -> list[dict]:
    dossier = racine / cle / "exploitable"
    if not dossier.is_dir():
        return []
    lignes: list[dict] = []
    for fichier in sorted(dossier.rglob("*.csv")):
        try:
            with fichier.open(encoding="utf-8", errors="replace", newline="") as flux:
                for ligne in csv.DictReader(flux):
                    if COLONNE_INTENSITE not in ligne:
                        break  # pas un fichier de rémanence
                    echantillon = (ligne.get(COLONNE_ECHANTILLON) or "").strip()
                    intensite = flottant(ligne.get(COLONNE_INTENSITE))
                    if not echantillon or intensite is None:
                        continue
                    lignes.append({
                        "source": cle,
                        "physical_sample_id": echantillon,
                        "expedition": (ligne.get("Exp") or "").strip(),
                        "site": (ligne.get("Site") or "").strip(),
                        "hole": (ligne.get("Hole") or "").strip(),
                        "ablation_type": (ligne.get(COLONNE_TRAITEMENT) or "").strip(),
                        "dose": flottant(ligne.get(COLONNE_DOSE)),
                        "trace_value": intensite,
                        "inclinaison": flottant(ligne.get(COLONNE_INCLINAISON)),
                        "declinaison": flottant(ligne.get(COLONNE_DECLINAISON)),
                        "profondeur_m": flottant(ligne.get(COLONNE_PROFONDEUR)),
                        "fichier_source": fichier.name,
                        "data_kind": "mesure_experimentale",
                    })
        except (OSError, csv.Error):
            continue
    return lignes


def main() -> int:
    config = json.loads(SOURCES.read_text(encoding="utf-8"))
    racine = (ICI / config["racine_locale"]).resolve()
    cles = [s["cle"] for s in config["sources"] if s["cle"].startswith("iodp_")]

    toutes: list[dict] = []
    for cle in cles:
        lignes = extraire_source(cle, racine)
        if lignes:
            echantillons = {l["physical_sample_id"] for l in lignes}
            print(f"  {cle.replace('iodp_remanence_', ''):<18}"
                  f"{len(lignes):>7} mesures  {len(echantillons):>5} échantillons")
        toutes.extend(lignes)

    # Un échantillon n'entre que s'il porte une NRM et au moins deux étapes
    # d'ablation : sans NRM, l'état initial est inconnu ; avec une seule étape,
    # aucune décroissance n'est mesurable.
    par_echantillon: dict[tuple, list[dict]] = defaultdict(list)
    for ligne in toutes:
        par_echantillon[(ligne["source"], ligne["physical_sample_id"])].append(ligne)

    retenus = []
    for cle, mesures in par_echantillon.items():
        types = {m["ablation_type"] for m in mesures}
        ablations = [m for m in mesures if m["ablation_type"] in ("AD", "TD")]
        if "NRM" in types and len(ablations) >= 2:
            retenus.append(cle)

    SORTIE.mkdir(exist_ok=True)
    admissibles = set(retenus)

    # Table par mesure : locale, hors dépôt.
    locale = racine / "derive_local"
    locale.mkdir(parents=True, exist_ok=True)
    par_mesure = locale / "iodp_remanence_par_mesure.csv"
    champs = list(toutes[0]) if toutes else []
    with par_mesure.open("w", encoding="utf-8", newline="") as flux:
        redacteur = csv.DictWriter(flux, fieldnames=champs, lineterminator="\n")
        redacteur.writeheader()
        for ligne in toutes:
            if (ligne["source"], ligne["physical_sample_id"]) in admissibles:
                redacteur.writerow(ligne)

    # Table par échantillon : versionnée.
    resume = SORTIE / "iodp_remanence_par_echantillon.csv"
    colonnes = ["source", "expedition", "site", "hole", "physical_sample_id",
                "nrm_intensite", "inclinaison_nrm", "declinaison_nrm", "profondeur_m",
                "n_etapes_ablation", "dose_min", "dose_max",
                "intensite_finale", "fraction_restante", "rho_ablation",
                "n_etapes_inscription", "rho_inscription", "data_kind"]
    with resume.open("w", encoding="utf-8", newline="") as flux:
        redacteur = csv.DictWriter(flux, fieldnames=colonnes, lineterminator="\n")
        redacteur.writeheader()
        for cle in sorted(admissibles):
            mesures = par_echantillon[cle]
            nrm = next((m for m in mesures if m["ablation_type"] == "NRM"), None)
            ablation = sorted((m for m in mesures if m["ablation_type"] in ("AD", "TD")
                               and m["dose"] is not None),
                              key=lambda m: m["dose"])
            inscription = sorted((m for m in mesures if m["ablation_type"] in ("IRM", "ARM")
                                  and m["dose"] is not None),
                                 key=lambda m: m["dose"])
            if not ablation:
                continue
            depart = nrm["trace_value"] if nrm else ablation[0]["trace_value"]
            fin = ablation[-1]["trace_value"]
            premier = mesures[0]
            redacteur.writerow({
                "source": premier["source"],
                "expedition": premier["expedition"],
                "site": premier["site"],
                "hole": premier["hole"],
                "physical_sample_id": premier["physical_sample_id"],
                "nrm_intensite": f"{depart:.6g}",
                "inclinaison_nrm": nrm["inclinaison"] if nrm else "",
                "declinaison_nrm": nrm["declinaison"] if nrm else "",
                "profondeur_m": premier["profondeur_m"],
                "n_etapes_ablation": len(ablation),
                "dose_min": f"{ablation[0]['dose']:.6g}",
                "dose_max": f"{ablation[-1]['dose']:.6g}",
                "intensite_finale": f"{fin:.6g}",
                "fraction_restante": f"{fin / depart:.6g}" if depart else "",
                "rho_ablation": f"{rang_correlation(ablation):.4f}",
                "n_etapes_inscription": len(inscription),
                "rho_inscription": (f"{rang_correlation(inscription):.4f}"
                                    if len(inscription) >= 3 else ""),
                "data_kind": "mesure_experimentale",
            })

    print()
    print(f"{len(toutes)} mesures extraites, "
          f"{len(par_echantillon)} échantillons physiques.")
    print(f"{len(retenus)} échantillons portent une NRM et au moins deux étapes "
          f"d'ablation : ce sont les seuls exploitables.")
    print(f"local   : {par_mesure.name}  {par_mesure.stat().st_size / 1e6:.1f} Mo")
    print(f"dépôt   : {resume.relative_to(ICI.parents[1]).as_posix()}  "
          f"{resume.stat().st_size / 1e3:.0f} ko")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
