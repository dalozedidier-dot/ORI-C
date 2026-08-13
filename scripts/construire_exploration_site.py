#!/usr/bin/env python3
"""Construit les données déterministes de la page interactive ORI-C.

Aucune statistique scientifique nouvelle n'est créée ici. Le script expose une
vue compacte de tables et sorties déjà versionnées afin que GitHub Pages puisse
les explorer sans serveur ni dépendance JavaScript externe.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site" / "data" / "exploration.json"
GC = ROOT / "01_branche_matiere" / "genealogie_cosmique_quantitative"
AST = ROOT / "02_branche_systeme_solaire" / "couche_astronomique"


def rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def build_genealogy():
    stages = rows(GC / "CHAINE_EMPIRIQUE.csv")
    links = rows(GC / "LIENS_EMPIRIQUES.csv")
    stages = sorted(stages, key=lambda r: int(r["order"]))
    if len(stages) != 20:
        raise SystemExit(f"généalogie: 20 stades attendus, {len(stages)} trouvés")
    if len(links) != 22:
        raise SystemExit(f"généalogie: 22 liens attendus, {len(links)} trouvés")
    return {"stages": stages, "links": links}


def build_nc_cc():
    raw = rows(GC / "data_massives_reelles" / "SOSSI_NC_CC_MEASURED.csv")
    authority = load(GC / "resultats" / "RESULTATS_QUANTITATIFS_DONNEES_MASSIVES.json")
    effects = authority["NC_CC"]["effect_sizes"]
    systems = {}
    for isotope, effect in effects.items():
        points = []
        unc_col = f"{isotope}_uncertainty"
        for row in raw:
            value = row.get(isotope, "").strip()
            if not value:
                continue
            unc = row.get(unc_col, "").strip()
            points.append(
                {
                    "sample": row.get("Chondrites") or row.get("Group") or "échantillon",
                    "reservoir": row["Reservoir"],
                    "value": float(value),
                    "uncertainty": float(unc) if unc else None,
                }
            )
        systems[isotope] = {
            "cohen_d_cc_minus_nc": effect["CC_minus_NC_Cohen_d"],
            "cc_n": effect["CC_n"],
            "nc_n": effect["NC_n"],
            "points": points,
        }
    if len(systems) != 11:
        raise SystemExit(f"NC/CC: 11 systèmes attendus, {len(systems)} trouvés")
    return {
        "classifier": authority["NC_CC"]["classifier"],
        "leave_one_out_correct": authority["NC_CC"]["leave_one_out_correct"],
        "leave_one_out_total": authority["NC_CC"]["leave_one_out_total"],
        "systems": systems,
    }


def pretty_job(job: str) -> str:
    labels = {
        "jupiter_a_minus_0p5pct_2myr": "Jupiter a −0,5 %",
        "jupiter_a_plus_0p5pct_2myr": "Jupiter a +0,5 %",
        "jupiter_mass_minus_5pct_2myr": "Masse de Jupiter −5 %",
        "jupiter_mass_plus_5pct_2myr": "Masse de Jupiter +5 %",
        "saturn_a_minus_0p5pct_2myr": "Saturne a −0,5 %",
        "saturn_a_plus_0p5pct_2myr": "Saturne a +0,5 %",
    }
    return labels.get(job, job.replace("_", " "))


def build_nbody():
    table = rows(AST / "resultats" / "real_science_max" / "analysis" / "counterfactual_effects.csv")
    scenarios = []
    for r in table:
        if not r.get("job"):
            continue
        scenarios.append(
            {
                "id": r["job"],
                "label": pretty_job(r["job"]),
                "samples": int(r["samples"]),
                "correlation_vs_baseline": float(r["correlation"]),
                "rmse_vs_baseline": float(r["rmse"]),
                "mean_eccentricity_delta": float(r["mean_eccentricity_delta"]),
                "std_ratio_vs_baseline": float(r["std_ratio_vs_baseline"]),
            }
        )
    if len(scenarios) != 6:
        raise SystemExit(f"N-corps: 6 scénarios attendus, {len(scenarios)} trouvés")
    certified = load(ROOT / "plateforme" / "campagne_maximale_reelle" / "RESULTATS_SCIENTIFIQUES_CERTIFIES.json")
    c_ast = next(x for x in certified["resultats"] if x.get("criterion_id") == "C-AST-01")
    return {
        "evidence_level": c_ast["niveau_preuve"],
        "scope": c_ast["portee"],
        "criteria_passed": c_ast["mesures"]["criteres_passes"],
        "criteria_total": c_ast["mesures"]["criteres_total"],
        "certified_min_effect_to_numeric_noise": c_ast["mesures"]["ratio_minimal_intervention_bruit_numerique"],
        "scenarios": scenarios,
        "warning": "scénarios pré-calculés uniquement; aucune interpolation arbitraire n'est présentée comme résultat scientifique",
    }


def build_section_xiv():
    d = load(ROOT / "plan_directeur" / "campagne_centrale_2026_08_11" / "resultats" / "SEUIL_XIV.json")
    return {
        "passed": d["passed_count"],
        "total": d["conditions_total"],
        "open": d["missing_ids"],
        "first_threshold_satisfied": d["first_threshold_satisfied"],
    }


def main() -> int:
    payload = {
        "schema": "oric.site-exploration.v1",
        "authority": "vue interactive dérivée de fichiers versionnés; aucun verdict nouveau",
        "section_xiv": build_section_xiv(),
        "genealogy": build_genealogy(),
        "nc_cc": build_nc_cc(),
        "nbody": build_nbody(),
        "sources": {
            "genealogy": "01_branche_matiere/genealogie_cosmique_quantitative/CHAINE_EMPIRIQUE.csv",
            "links": "01_branche_matiere/genealogie_cosmique_quantitative/LIENS_EMPIRIQUES.csv",
            "nc_cc": "01_branche_matiere/genealogie_cosmique_quantitative/data_massives_reelles/SOSSI_NC_CC_MEASURED.csv",
            "nbody": "02_branche_systeme_solaire/couche_astronomique/resultats/real_science_max/analysis/counterfactual_effects.csv",
            "section_xiv": "plan_directeur/campagne_centrale_2026_08_11/resultats/SEUIL_XIV.json"
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"exploration site: {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
