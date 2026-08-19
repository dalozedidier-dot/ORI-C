#!/usr/bin/env python3
"""Assemble les entrées de PALEO-HISTORY-02 sur l'échelle de profondeur U1308.

Ne calcule aucun score et n'ouvre aucune cible : ce script ne fait que joindre,
sur une même échelle de profondeur composite, la cible, son incertitude
chronologique et le contrôle négatif physique. Le test lui-même n'est exécuté
qu'après scellement.

Trois sources, toutes mesurées et versionnées avec leur empreinte :

- `donnees_externes/na_stack_u1308/` — stack benthique de l'Atlantique Nord tié
  aux spéléothèmes (Zenodo 10.5281/zenodo.14796413, CC-BY-4.0). Fournit la
  cible, 1 000 tirages chronologiques et un modèle d'âge non accordé ;
- `donnees_externes/rpi_u1308/` — paléointensité géomagnétique relative du même
  site (PANGAEA 10.1594/PANGAEA.808947, CC-BY-3.0). Contrôle négatif.

La RPI est publiée indexée en âge ; sa profondeur est restituée par la table de
susceptibilité, qui porte le même nombre de lignes dans le même ordre. Ce point
est vérifié ici et non supposé.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
NA = RACINE / "donnees_externes/na_stack_u1308"
RPI = RACINE / "donnees_externes/rpi_u1308"


def lire_tab_pangaea(chemin: Path) -> list[list[str]]:
    """Lit un .tab PANGAEA : métadonnées jusqu'à `*/`, puis en-tête, puis données."""
    lignes = chemin.read_text(encoding="utf-8", errors="ignore").splitlines()
    debut = next(i for i, l in enumerate(lignes) if l.strip() == "*/")
    return [l.split("\t") for l in lignes[debut + 2:] if l.strip()]


def interpoler(x: float, xs: list[float], ys: list[float]) -> float | None:
    """Interpolation linéaire, sans extrapolation."""
    if not xs or x < xs[0] or x > xs[-1]:
        return None
    lo, hi = 0, len(xs) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if xs[mid] <= x:
            lo = mid
        else:
            hi = mid
    if xs[hi] == xs[lo]:
        return ys[lo]
    part = (x - xs[lo]) / (xs[hi] - xs[lo])
    return ys[lo] + part * (ys[hi] - ys[lo])


def charger():
    prof = [float(l) for l in (NA / "NA-stack_depth_composite.txt")
            .read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    tirages = [[float(x) for x in l.split() if x.strip()] for l in
               (NA / "NA-stack_age-samples.txt").read_text(encoding="utf-8").splitlines() if l.strip()]
    cible = []
    for l in (NA / "NA-stack_age-d18O.txt").read_text(encoding="utf-8").splitlines()[1:]:
        if l.strip():
            c = l.split()
            cible.append((float(c[0]), float(c[1]), float(c[2])))

    rpi_rows = lire_tab_pangaea(RPI / "313-U1308_rpi.tab")
    sus_rows = lire_tab_pangaea(RPI / "313-U1308_suscept.tab")
    if len(rpi_rows) != len(sus_rows):
        raise SystemExit("RPI et susceptibilité n'ont pas le même nombre de lignes : "
                         "la restitution de la profondeur n'est pas fondée")
    paires = sorted((float(s[0]), float(r[1])) for r, s in zip(rpi_rows, sus_rows))
    return prof, tirages, cible, paires


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sortie", type=Path, default=None, help="table jointe (JSON)")
    args = ap.parse_args()

    prof, tirages, cible, paires = charger()
    if len(prof) != len(tirages):
        raise SystemExit("profondeurs et tirages chronologiques désaccordés")

    ages_cible = [c[0] for c in cible]
    d18o = [c[1] for c in cible]
    rp_prof = [p for p, _ in paires]
    rp_val = [v for _, v in paires]

    lignes, sans_cible, sans_rpi = [], 0, 0
    for i, p in enumerate(prof):
        t = sorted(tirages[i])
        age_med = t[len(t) // 2]
        y = interpoler(age_med, ages_cible, d18o)
        r = interpoler(p, rp_prof, rp_val)
        if y is None:
            sans_cible += 1
        if r is None:
            sans_rpi += 1
        lignes.append({
            "profondeur_mcd": p,
            "age_median_ka": age_med,
            "age_sigma_ka": (sum((x - sum(t) / len(t)) ** 2 for x in t) / len(t)) ** 0.5,
            "cible_d18o": y,
            "controle_negatif_rpi": r,
        })

    complets = [l for l in lignes if l["cible_d18o"] is not None
                and l["controle_negatif_rpi"] is not None]
    rapport = {
        "schema": "oric.paleo-history-02.entrees.v1",
        "note": "préparation seule ; aucun score, aucune ouverture de cible",
        "profondeurs": len(prof),
        "tirages_chronologiques_par_profondeur": len(tirages[0]),
        "lignes_completes": len(complets),
        "sans_cible": sans_cible,
        "sans_controle_negatif": sans_rpi,
        "couverture_age_ka": [min(l["age_median_ka"] for l in complets),
                              max(l["age_median_ka"] for l in complets)] if complets else None,
        "couverture_profondeur_mcd": [min(l["profondeur_mcd"] for l in complets),
                                      max(l["profondeur_mcd"] for l in complets)] if complets else None,
        "sigma_age_median_ka": sorted(l["age_sigma_ka"] for l in complets)[len(complets) // 2]
                               if complets else None,
    }
    print(json.dumps(rapport, ensure_ascii=False, indent=2))
    if args.sortie:
        args.sortie.write_text(
            json.dumps({"rapport": rapport, "lignes": complets}, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8", newline="")
        print(f"écrit : {args.sortie}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
