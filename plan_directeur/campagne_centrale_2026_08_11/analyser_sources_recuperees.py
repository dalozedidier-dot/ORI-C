#!/usr/bin/env python3
"""Inspecte les sources externes récupérées sans les copier dans le dépôt."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
import sys
import tempfile
import zipfile
from pathlib import Path

import fitz
import openpyxl
import pdfplumber
from scipy.stats import spearmanr


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def analyse_demagnetisation(archive: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="oric_magnetic_") as temporary:
        with zipfile.ZipFile(archive) as source:
            names = source.namelist()
            targets = {
                "AF": next(name for name in names if name.endswith("U1506A_AF demag_all.xlsx")),
                "thermal": next(name for name in names if name.endswith("U1506A_TD_all.xlsx")),
            }
            results = {}
            for mode, member in targets.items():
                source.extract(member, temporary)
                workbook = openpyxl.load_workbook(
                    Path(temporary) / member, read_only=True, data_only=True
                )
                sheet = workbook.active
                rows = list(sheet.iter_rows(values_only=True))
                workbook.close()
                groups: dict[str, list[tuple[float, float]]] = {}
                for row in rows[1:]:
                    groups.setdefault(str(row[0]), []).append((float(row[1]), float(row[5])))
                series = []
                for sample, pairs in sorted(groups.items()):
                    pairs.sort()
                    rho, p_value = spearmanr(
                        [pair[0] for pair in pairs], [pair[1] for pair in pairs]
                    )
                    series.append({
                        "sample": sample,
                        "n": len(pairs),
                        "rho_spearman": float(rho),
                        "p_value": float(p_value),
                        "retention_finale": pairs[-1][1] / pairs[0][1],
                        "dose_min": pairs[0][0],
                        "dose_max": pairs[-1][0],
                    })
                results[mode] = {
                    "observations": len(rows) - 1,
                    "series": len(series),
                    "rho_moyen": statistics.mean(row["rho_spearman"] for row in series),
                    "rho_median": statistics.median(row["rho_spearman"] for row in series),
                    "series_decroissantes": sum(row["rho_spearman"] < 0 for row in series),
                    "series_decroissantes_p_le_005": sum(
                        row["rho_spearman"] < 0 and row["p_value"] <= 0.05 for row in series
                    ),
                    "retention_finale_mediane": statistics.median(
                        row["retention_finale"] for row in series
                    ),
                    "details": series,
                }
        return {
            "sha256": sha256(archive),
            "membres_hors_metadonnees_macos": sum(
                not name.startswith("__MACOSX/") and not name.endswith(".DS_Store")
                for name in names
            ),
            "resultats": results,
            "qualification": "preuve_forte_ablation_physique_non_C03_complet",
            "manques_C03": [
                "deux histoires A/B contrôlées",
                "même stimulus final avant et après ablation",
                "disparition appariée de l'écart de réponse A/B",
            ],
        }


def analyse_u1537(archive: Path) -> dict:
    with zipfile.ZipFile(archive) as source:
        names = [name for name in source.namelist() if not name.endswith("/")]
    samples = sorted({match.group(1).upper() for name in names
                      if (match := re.match(r"^(U1537A-\d+[HF]-\d+W-\d+cm)", name, re.IGNORECASE))})
    return {
        "sha256": sha256(archive),
        "files": len(names),
        "samples": samples,
        "protocoles": ["FC", "ZFC", "LTC-RTSIRM", "hysteresis", "DCD", "FORC"],
        "qualification": "mesures_multiprotocoles_appariees_non_chaine_complete",
        "manques": ["histoires A/B contrôlées", "persistance temporelle", "ablation appariée de ΔR"],
    }


def analyse_farough(pdf: Path, original: Path) -> dict:
    rows = []
    with pdfplumber.open(pdf) as document:
        for page in document.pages:
            for table in page.extract_tables():
                rows.extend(table)
    current = None
    groups: dict[str, list[tuple[float, float, float, float]]] = {}
    for row in rows:
        if not row or not row[0] or row[0].startswith("t (hr)"):
            continue
        if row[0] in {"TS", "SQ", "JC", "ND", "BC"}:
            current = row[0]
            groups[current] = []
            continue
        try:
            values = tuple(float(value) for value in row)
        except (TypeError, ValueError):
            continue
        if current:
            groups[current].append(values)
    summaries = []
    for group, values in groups.items():
        time = [row[0] for row in values]
        permeability = [row[3] for row in values]
        rho, p_value = spearmanr(time, permeability)
        p_number = float(p_value)
        summaries.append({
            "experience": group,
            "n": len(values),
            "rho_temps_permeabilite": float(rho),
            "p_value": p_number if p_number > 0 else None,
            "p_value_display": f"{p_number:.6g}" if p_number > 0 else f"< {sys.float_info.min:.3g}",
            "ratio_permeabilite_finale_initiale": permeability[-1] / permeability[0],
        })
    return {
        "sha256_source_originale": sha256(original),
        "sha256_document_converti": sha256(pdf),
        "observations": sum(row["n"] for row in summaries),
        "experiences": summaries,
        "qualification_H052": "ne_justifie_pas_le_reencodage_R1",
        "interpretation": "Les cinq séries documentent une perte de perméabilité avec le temps; elles ne démontrent pas que la circulation produit N030.",
    }


def analyse_edc3(pdf: Path) -> dict:
    document = fitz.open(pdf)
    text = "\n".join(page.get_text() for page in document)
    lowered = text.lower()
    return {
        "sha256": sha256(pdf),
        "pages": len(document),
        "mentions_monte_carlo": lowered.count("monte carlo"),
        "mentions_uncertainty": lowered.count("uncertaint"),
        "qualification_PALEO_HISTORY_02": "methodologie_chronologique_sans_distributions_ponctuelles_exploitables",
        "controle_negatif_reel_preregistre": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--magnetic-u1506", type=Path, required=True)
    parser.add_argument("--magnetic-u1537", type=Path, required=True)
    parser.add_argument("--edc3", type=Path, required=True)
    parser.add_argument("--farough-pdf", type=Path, required=True)
    parser.add_argument("--farough-original", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = {
        "schema": "oric.recovered-sources-inspection.v1",
        "date": "2026-08-12",
        "u1506": analyse_demagnetisation(args.magnetic_u1506),
        "u1537": analyse_u1537(args.magnetic_u1537),
        "farough": analyse_farough(args.farough_pdf, args.farough_original),
        "edc3": analyse_edc3(args.edc3),
        "scientific_effect": {
            "material_complete_chains_admitted": 0,
            "hypergraph_canonical_closure": "46/53",
            "paleo_history_02": "non_testable",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"inspection écrite: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
