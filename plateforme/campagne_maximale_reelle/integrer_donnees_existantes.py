"""Intègre dans la campagne maximale toutes les données réelles déjà présentes.

Le script ne copie aucun gabarit de ``examples/data`` et ne complète aucune
valeur absente. Il produit des tables compatibles avec la plateforme, des
fichiers auxiliaires conservant les mesures qui dépassent les schémas minimaux,
et un registre de portée indiquant exactement quels tests disposent réellement
du protocole nécessaire.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import re
import tempfile
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from integrer_lot_scientifique_2026_08_05 import integrate as integrate_scientific_bundle

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DEFAULT_DATA = HERE / "data"
VESICLE_ZIP = ROOT / "donnees_externes/vesicules_sokolskyi_baum_2026/raw/doi_10_5061_dryad_fbg79cp99__v20260309.zip"
DONOFRIO = ROOT / "donnees_externes/histoire_antibiotique_donofrio_2026/extracted"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, lineterminator="\n")


def number_or_midpoint(value: Any) -> tuple[float | None, float | None, float | None]:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None, None, None
    text = str(value).strip().replace(",", ".")
    values = [float(item) for item in re.findall(r"[-+]?\d+(?:\.\d+)?", text)]
    if not values:
        return None, None, None
    if len(values) == 1:
        return values[0], values[0], values[0]
    low, high = min(values[0], values[1]), max(values[0], values[1])
    return (low + high) / 2.0, low, high


def build_partition_experiments(data_dir: Path) -> dict[str, Any]:
    source = ROOT / "01_branche_matiere/hypergraphe_transformations/coefficients_partage.csv"
    raw = pd.read_csv(source, sep=";")
    rows: list[dict[str, Any]] = []
    for item in raw.to_dict("records"):
        pressure, pmin, pmax = number_or_midpoint(item.get("pression_GPa"))
        temperature, tmin, tmax = number_or_midpoint(item.get("temperature_K"))
        d_value, _, _ = number_or_midpoint(item.get("D_metal_sur_silicate"))
        delta_match = re.search(r"IW\s*([+-]?\d+(?:\.\d+)?)", str(item.get("fugacite_oxygene", "")), re.I)
        delta_iw = float(delta_match.group(1)) if delta_match else np.nan
        uncertainty_match = re.search(r"\+/-\s*(\d+(?:\.\d+)?)", str(item.get("condition", "")))
        d_uncertainty = float(uncertainty_match.group(1)) if uncertainty_match else np.nan
        log_uncertainty = np.nan
        if d_value and d_uncertainty and d_value > d_uncertainty:
            log_uncertainty = max(
                math.log10(d_value + d_uncertainty) - math.log10(d_value),
                math.log10(d_value) - math.log10(d_value - d_uncertainty),
            )
        rows.append(
            {
                "experiment_id": item["record_id"],
                "element": item["element"],
                "pressure_gpa": pressure,
                "temperature_k": temperature,
                "delta_iw": delta_iw,
                "logD": math.log10(d_value) if d_value and d_value > 0 else np.nan,
                "uncertainty": log_uncertainty,
                "D_original": d_value,
                "pressure_min_gpa": pmin,
                "pressure_max_gpa": pmax,
                "temperature_min_k": tmin,
                "temperature_max_k": tmax,
                "oxygen_fugacity_original": item.get("fugacite_oxygene"),
                "condition_original": item.get("condition"),
                "source_id": item.get("source"),
                "value_type": item.get("type_de_valeur"),
                "source_status": item.get("statut"),
            }
        )
    frame = pd.DataFrame(rows)
    write_csv(data_dir / "partition_experiments.csv", frame)
    return {
        "rows": len(frame),
        "complete_regression_rows": int(frame[["pressure_gpa", "temperature_k", "delta_iw", "logD"]].notna().all(axis=1).sum()),
        "elements": sorted(frame["element"].dropna().astype(str).unique().tolist()),
        "source": str(source.relative_to(ROOT)),
        "source_sha256": sha256(source),
    }


def load_vesicle_parser():
    path = ROOT / "03_branche_vivant/lignees_vesicules/analyser_lignees.py"
    spec = importlib.util.spec_from_file_location("oric_vesicle_parser", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossible de charger {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def duration_from_name(name: str) -> float:
    lower = name.lower()
    if "30min" in lower:
        return 0.5
    if "90min" in lower:
        return 1.5
    if "5hr" in lower:
        return 5.0
    return 24.0


def condition_flags(condition: str) -> tuple[bool, bool]:
    return condition.startswith("F"), condition.endswith("R")


def build_vesicle_lineages(data_dir: Path, work: Path) -> tuple[dict[str, Any], pd.DataFrame]:
    parser = load_vesicle_parser()
    with zipfile.ZipFile(VESICLE_ZIP) as archive:
        archive.extractall(work)
    log_files = sorted(work.glob("*_log.xlsx"))
    nodes: dict[str, dict[str, Any]] = {}
    all_pairs: list[pd.DataFrame] = []
    design_rows: list[dict[str, Any]] = []
    for path in log_files:
        condition_match = re.match(r"^(FR|FU|UR|UU)", path.name, re.I)
        condition = condition_match.group(1).upper() if condition_match else path.name.split("_")[0].split("-")[0]
        replicate_match = re.search(r"([123])(?:_log)?\.xlsx$", path.name, re.I)
        replicate = int(replicate_match.group(1)) if replicate_match else 1
        generation_duration_h = duration_from_name(path.name)
        fed, resuspended = condition_flags(condition)
        pair_frame = parser.pairs(path, condition)
        if pair_frame.empty:
            continue
        pair_frame = pair_frame.copy()
        pair_frame["source_file"] = path.name
        pair_frame["replicate"] = replicate
        pair_frame["generation_duration_h"] = generation_duration_h
        pair_frame["fed"] = fed
        pair_frame["resuspended"] = resuspended
        all_pairs.append(pair_frame)
        for arm in sorted(pair_frame["arm"].unique()):
            condition_id = f"{path.stem}:{arm}"
            design_rows.append(
                {
                    "condition_id": condition_id,
                    "temperature": np.nan,
                    "ph": np.nan,
                    "wet_dry_cycles": np.nan,
                    "uv_flux": np.nan,
                    "mineral": np.nan,
                    "replicate": replicate,
                    "experiment_condition": condition,
                    "arm": arm,
                    "fed": fed,
                    "resuspended": resuspended,
                    "generation_duration_h": generation_duration_h,
                    "source_file": path.name,
                    "measured_variable": "turbidity_A400",
                    "transfer_map_available": bool((pair_frame[pair_frame["arm"] == arm]["mapping_mode"] == "coded_lineage").any()),
                }
            )
        for row in pair_frame.itertuples(index=False):
            condition_id = f"{path.stem}:{row.arm}"
            parent_id = f"{path.stem}:{row.arm}:g{int(row.transition)}:{row.donor}"
            child_id = f"{path.stem}:{row.arm}:g{int(row.transition) + 1}:{row.recipient}"
            parent_record = nodes.setdefault(
                parent_id,
                {
                    "lineage_id": parent_id,
                    "parent_id": "",
                    "generation": int(row.transition),
                    "condition_id": condition_id,
                    "yield": float(row.parent),
                    "polymer_length": np.nan,
                    "compartment_stability": np.nan,
                    "copy_fidelity": np.nan,
                    "condition": condition,
                    "arm": row.arm,
                    "replicate": replicate,
                    "well": row.donor,
                    "source_file": path.name,
                    "generation_duration_h": generation_duration_h,
                    "fed": fed,
                    "resuspended": resuspended,
                    "mapping_mode": row.mapping_mode,
                },
            )
            if pd.isna(parent_record.get("yield")):
                parent_record["yield"] = float(row.parent)
            child_record = nodes.setdefault(
                child_id,
                {
                    "lineage_id": child_id,
                    "parent_id": parent_id,
                    "generation": int(row.transition) + 1,
                    "condition_id": condition_id,
                    "yield": float(row.offspring),
                    "polymer_length": np.nan,
                    "compartment_stability": np.nan,
                    "copy_fidelity": np.nan,
                    "condition": condition,
                    "arm": row.arm,
                    "replicate": replicate,
                    "well": row.recipient,
                    "source_file": path.name,
                    "generation_duration_h": generation_duration_h,
                    "fed": fed,
                    "resuspended": resuspended,
                    "mapping_mode": row.mapping_mode,
                },
            )
            # Le même nœud ne doit pas recevoir deux parents. Une divergence est une erreur de source/parsing.
            if child_record["parent_id"] != parent_id:
                raise ValueError(f"Parents contradictoires pour {child_id}: {child_record['parent_id']} / {parent_id}")
    if not all_pairs:
        raise ValueError("Aucune lignée de vésicules extraite")
    pairs_frame = pd.concat(all_pairs, ignore_index=True)
    lineages = pd.DataFrame(nodes.values()).sort_values(["source_file", "arm", "generation", "well"])
    design = pd.DataFrame(design_rows).drop_duplicates("condition_id").sort_values("condition_id")
    write_csv(data_dir / "prebiotic_lineages.csv", lineages)
    write_csv(data_dir / "prebiotic_design.csv", design)
    write_csv(data_dir / "prebiotic_parent_offspring_pairs.csv", pairs_frame)
    return (
        {
            "log_files": len(log_files),
            "lineage_nodes": len(lineages),
            "parent_offspring_pairs": len(pairs_frame),
            "conditions": sorted(pairs_frame["condition"].unique().tolist()),
            "generation_durations_h": sorted(float(v) for v in pairs_frame["generation_duration_h"].unique()),
            "coded_lineage_fraction": float((pairs_frame["mapping_mode"] == "coded_lineage").mean()),
            "source": str(VESICLE_ZIP.relative_to(ROOT)),
            "source_sha256": sha256(VESICLE_ZIP),
        },
        pairs_frame,
    )


def seconds_from_time(value: Any) -> float | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    if hasattr(value, "hour") and hasattr(value, "minute"):
        return float(value.hour * 3600 + value.minute * 60 + value.second)
    text = str(value).strip()
    match = re.fullmatch(r"(\d{1,2}):(\d{2}):(\d{2})", text)
    if not match:
        return None
    return float(int(match.group(1)) * 3600 + int(match.group(2)) * 60 + int(match.group(3)))


def build_vesicle_timecourses(data_dir: Path, work: Path) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for path in sorted(work.glob("*_inc.xlsx")):
        condition = path.stem.split("_")[0]
        with pd.ExcelFile(path) as workbook:
            sheet_names = list(workbook.sheet_names)
        for sheet in sheet_names:
            raw = pd.read_excel(path, sheet_name=sheet, header=None, dtype=object)
            header_row = None
            time_col = None
            candidates: list[tuple[int, int, int]] = []
            for idx, row in raw.iterrows():
                values = row.tolist()
                for col, value in enumerate(values):
                    if str(value).strip().lower() == "time":
                        populated_after = sum(pd.notna(item) for item in values[col + 2 :])
                        candidates.append((populated_after, idx, col))
            if candidates:
                _, header_row, time_col = max(candidates)
            if header_row is None or time_col is None:
                continue
            headers = raw.iloc[header_row].tolist()
            well_cols = [col for col in range(time_col + 2, raw.shape[1]) if pd.notna(headers[col])]
            for row_idx in range(header_row + 1, len(raw)):
                seconds = seconds_from_time(raw.iat[row_idx, time_col])
                if seconds is None:
                    break
                temperature = pd.to_numeric(pd.Series([raw.iat[row_idx, time_col + 1]]), errors="coerce").iloc[0]
                for ordinal, col in enumerate(well_cols, start=1):
                    value = pd.to_numeric(pd.Series([raw.iat[row_idx, col]]), errors="coerce").iloc[0]
                    if pd.isna(value):
                        continue
                    label = str(headers[col]).strip()
                    if label in {"", "nan", condition}:
                        label = f"well_{ordinal:03d}"
                    rows.append(
                        {
                            "source_file": path.name,
                            "condition": condition,
                            "generation": sheet,
                            "well": label,
                            "well_index": ordinal,
                            "time_seconds": seconds,
                            "temperature_c": temperature,
                            "turbidity_A400": float(value),
                        }
                    )
    frame = pd.DataFrame(rows)
    if frame.empty:
        summary = pd.DataFrame(columns=["source_file", "condition", "generation", "well", "well_index", "n", "initial", "maximum", "final", "linear_slope_per_hour", "peak_gain", "post_peak_loss"])
    else:
        summaries = []
        keys = ["source_file", "condition", "generation", "well", "well_index"]
        for key, group in frame.groupby(keys, observed=False, sort=True):
            group = group.sort_values("time_seconds")
            x = group["time_seconds"].to_numpy(float) / 3600.0
            y = group["turbidity_A400"].to_numpy(float)
            slope = float(np.polyfit(x, y, 1)[0]) if len(group) >= 2 and np.ptp(x) > 0 else np.nan
            maximum = float(np.max(y))
            summaries.append(
                dict(zip(keys, key))
                | {
                    "n": len(group),
                    "initial": float(y[0]),
                    "maximum": maximum,
                    "final": float(y[-1]),
                    "linear_slope_per_hour": slope,
                    "peak_gain": maximum - float(y[0]),
                    "post_peak_loss": maximum - float(y[-1]),
                }
            )
        summary = pd.DataFrame(summaries)
    write_csv(data_dir / "prebiotic_timecourses.csv", frame)
    write_csv(data_dir / "prebiotic_timecourse_summary.csv", summary)
    return {
        "rows": len(frame),
        "series": len(summary),
        "conditions": sorted(frame["condition"].unique().tolist()) if not frame.empty else [],
        "source_files": sorted(frame["source_file"].unique().tolist()) if not frame.empty else [],
    }


def build_vesicle_auxiliary(data_dir: Path, work: Path) -> dict[str, Any]:
    source = work / "Fig3-data.xlsx"
    rows: list[dict[str, Any]] = []
    with pd.ExcelFile(source) as workbook:
        sheet_names = list(workbook.sheet_names)
    for sheet in sheet_names:
        raw = pd.read_excel(source, sheet_name=sheet, header=None, dtype=object)
        top_headers = []
        current = ""
        for value in raw.iloc[0].tolist():
            if pd.notna(value) and str(value).strip():
                current = str(value).strip()
            top_headers.append(current)
        for row_idx in range(len(raw)):
            row_label = raw.iat[row_idx, 0] if raw.shape[1] else None
            for col_idx in range(1, raw.shape[1]):
                value = pd.to_numeric(pd.Series([raw.iat[row_idx, col_idx]]), errors="coerce").iloc[0]
                if pd.isna(value):
                    continue
                rows.append(
                    {
                        "panel": sheet,
                        "group": top_headers[col_idx] if col_idx < len(top_headers) else "",
                        "row_label": row_label,
                        "replicate_index": col_idx,
                        "value": float(value),
                        "source_file": source.name,
                    }
                )
    frame = pd.DataFrame(rows)
    write_csv(data_dir / "prebiotic_auxiliary_measurements.csv", frame)
    return {
        "rows": len(frame),
        "panels": sorted(frame["panel"].unique().tolist()),
        "source_file": source.name,
    }


def build_vesicle_log_auxiliary(data_dir: Path, work: Path) -> dict[str, Any]:
    """Extrait les mesures supplémentaires enfermées dans les classeurs log.

    Sont conservées sans interprétation ajoutée : fluorescence Nile Red des
    feuilles ``drNR``/``selNR``, turbidité avant ajout d'amphiphiles (``PM``)
    et turbidité des vésicules alimentaires (``-F``).
    """
    parser = load_vesicle_parser()
    rows: list[dict[str, Any]] = []
    for path in sorted(work.glob("*_log.xlsx")):
        condition_match = re.match(r"^(FR|FU|UR|UU)", path.name, re.I)
        condition = condition_match.group(1).upper() if condition_match else ""
        with pd.ExcelFile(path) as workbook:
            sheet_names = list(workbook.sheet_names)
        for sheet in [name for name in sheet_names if name.lower() in {"drnr", "selnr"}]:
            arm = "drift" if sheet.lower().startswith("dr") else "selection"
            try:
                matrix = parser.numeric_matrix(path, sheet)
            except Exception:
                continue
            for generation_column in matrix.columns:
                generation = int(str(generation_column).lstrip("g"))
                for well, value in matrix[generation_column].items():
                    if pd.isna(value):
                        continue
                    rows.append({
                        "source_file": path.name,
                        "sheet": sheet,
                        "condition": condition,
                        "arm": arm,
                        "generation": generation,
                        "well": str(well),
                        "measurement": "nile_red_fluorescence",
                        "value": float(value),
                        "header_original": generation_column,
                    })
        for sheet in [name for name in sheet_names if name.lower() in {"drdata", "seldata"}]:
            arm = "drift" if sheet.lower().startswith("dr") else "selection"
            raw = pd.read_excel(path, sheet_name=sheet, header=None, dtype=object)
            plate_result = parser._first_plate_rows(raw)
            if plate_result is None or raw.empty:
                continue
            plate, labels = plate_result
            headers = raw.iloc[0].tolist()
            for column in range(1, raw.shape[1]):
                header = str(headers[column]).strip() if column < len(headers) and pd.notna(headers[column]) else ""
                upper = header.upper().replace(" ", "")
                if "PM" in upper:
                    measurement = "pre_amphiphile_turbidity_A400"
                elif "-F" in upper:
                    measurement = "food_vesicle_turbidity_A400"
                else:
                    continue
                generation_match = re.search(r"G(\d+)", upper)
                generation = int(generation_match.group(1)) if generation_match else np.nan
                values = pd.to_numeric(plate.iloc[:, column], errors="coerce")
                for well, value in zip(labels, values):
                    if pd.isna(value):
                        continue
                    rows.append({
                        "source_file": path.name,
                        "sheet": sheet,
                        "condition": condition,
                        "arm": arm,
                        "generation": generation,
                        "well": well,
                        "measurement": measurement,
                        "value": float(value),
                        "header_original": header,
                    })
    frame = pd.DataFrame(rows, columns=[
        "source_file", "sheet", "condition", "arm", "generation", "well",
        "measurement", "value", "header_original",
    ])
    write_csv(data_dir / "prebiotic_log_auxiliary_measurements.csv", frame)
    return {
        "rows": int(len(frame)),
        "measurements": frame.groupby("measurement").size().astype(int).to_dict() if len(frame) else {},
        "source_files": int(frame["source_file"].nunique()) if len(frame) else 0,
    }


def build_cell_architecture(data_dir: Path) -> dict[str, Any]:
    source = ROOT / "01_branche_matiere/inventaire_hierarchique/tables/11_Biologique.csv"
    raw = pd.read_csv(source, sep=";")
    keep_levels = {"Cellule", "Structure cellulaire"}
    selected = raw[raw["Niveau"].isin(keep_levels)].copy()
    evidence = selected["Statut"].astype(str).map(lambda text: 3 if "Confirm" in text else 2 if "reconstr" in text.lower() else 1)
    frame = pd.DataFrame(
        {
            "taxon": selected["Entité"].where(selected["Niveau"] == "Cellule", "cellule_eucaryote_générale"),
            "component": selected["Entité"],
            "origin": selected["Niveau"],
            "function": selected["Note"],
            "dependency": selected["Note"].where(selected["Note"].astype(str).str.contains("dépend", case=False, na=False), ""),
            "evidence_level": evidence,
            "architecture_original": selected["Architecture"],
            "composition_original": selected["Composition"],
            "environment_original": selected["Environnement"],
            "status_original": selected["Statut"],
            "source_url": selected["Source URL"],
        }
    )
    write_csv(data_dir / "cell_architecture.csv", frame)
    return {
        "rows": len(frame),
        "cell_types": sorted(raw.loc[raw["Niveau"] == "Cellule", "Entité"].astype(str).tolist()),
        "source": str(source.relative_to(ROOT)),
        "source_sha256": sha256(source),
    }


def split_by_number(value: Any) -> str:
    digest = int(hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:8], 16) % 10
    return "train" if digest < 6 else "validation" if digest < 8 else "test"


def build_antibiotic_design_and_aux(data_dir: Path) -> tuple[dict[str, Any], pd.DataFrame]:
    cycles = pd.read_csv(data_dir / "antibiotic_cycles.csv")
    measurements = pd.read_csv(data_dir / "antibiotic_measurements.csv")
    cycles["nutrient_level"] = cycles["lineage_id"].astype(str).str.extract(r"_N([^_]+)_", expand=False).str.replace("p", ".", regex=False)
    grouped = cycles.groupby(["antibiotic", "dose", "nutrient_level"], dropna=False)
    rows = []
    for (antibiotic, dose, nutrient), group in grouped:
        rows.append(
            {
                "arm_id": f"{antibiotic}:{dose}:N{nutrient}",
                "species": "Escherichia coli",
                "antibiotic": antibiotic,
                "schedule": f"{float(group['duration'].median()):g} h exposition / {float(group['recovery_duration'].median()):g} h récupération",
                "dose": dose,
                "replicates": int(group["lineage_id"].nunique()),
                "nutrient_level": nutrient,
                "cycle_min": int(group["cycle"].min()),
                "cycle_max": int(group["cycle"].max()),
                "source_dataset": "Windels et al.",
            }
        )
    design = pd.DataFrame(rows).sort_values(["antibiotic", "dose", "nutrient_level"])
    write_csv(data_dir / "antibiotic_design.csv", design)

    fitness_rows = []
    for filename, limitation in [
        ("Figure_2_C-limited_Fitness.csv", "Carbon"),
        ("Figure_2_N-limited_Fitness.csv", "Nitrogen"),
    ]:
        source = DONOFRIO / filename
        raw = pd.read_csv(source)
        for item in raw.to_dict("records"):
            ancestor_fit = pd.to_numeric(pd.Series([item.get("Fitness ancestor (w)")]), errors="coerce").iloc[0]
            evolved_fit = pd.to_numeric(pd.Series([item.get("Fitness evolved (w)")]), errors="coerce").iloc[0]
            change = pd.to_numeric(pd.Series([item.get("Change in fitness")]), errors="coerce").iloc[0]
            fitness_rows.append(
                {
                    "limitation": limitation,
                    "population_origin": item.get("LTEE population derived from"),
                    "evolved_strain_id": item.get("Evolved strain ID"),
                    "ancestor_id": item.get("Ancestor ID"),
                    "replicate": item.get("Replicate"),
                    "fitness_ancestor": ancestor_fit,
                    "fitness_evolved": evolved_fit,
                    "change_in_fitness": change,
                    "source_file": filename,
                }
            )
    fitness = pd.DataFrame(fitness_rows)
    write_csv(data_dir / "antibiotic_fitness_real.csv", fitness)
    coverage = {column: float(pd.to_numeric(measurements[column], errors="coerce").notna().mean()) for column in ["mic", "lag_time", "growth_rate", "survival", "persister_fraction", "fitness"]}
    return (
        {
            "design_rows": len(design),
            "replicates_min": int(design["replicates"].min()),
            "replicates_max": int(design["replicates"].max()),
            "conditions_with_12_or_more": int((design["replicates"] >= 12).sum()),
            "fitness_rows": len(fitness),
            "measurement_coverage": coverage,
            "sources": [str((DONOFRIO / name).relative_to(ROOT)) for name in ["Figure_2_C-limited_Fitness.csv", "Figure_2_N-limited_Fitness.csv"]],
        },
        fitness,
    )


def split_by_position(position: int, total: int) -> str:
    fraction = position / max(total, 1)
    return "train" if fraction < 0.6 else "validation" if fraction < 0.8 else "test"


def benchmark_rows_from_orbit(data_dir: Path) -> list[dict[str, Any]]:
    frame = pd.read_csv(data_dir / "orbital_timeseries.csv").sort_values("time").reset_index(drop=True)
    frame = frame.apply(pd.to_numeric, errors="coerce")
    rows = []
    lag, horizon, stride = 10, 10, 50
    positions = list(range(lag, len(frame) - horizon, stride))
    for ordinal, idx in enumerate(positions):
        current, previous, future = frame.iloc[idx], frame.iloc[idx - lag], frame.iloc[idx + horizon]
        rows.append(
            {
                "case_id": f"orbit:{idx}",
                "domain": "orbital",
                "history_json": json_text({"ecc_lag": previous.eccentricity, "obl_lag": previous.obliquity, "prec_lag": previous.precession, "lag_kyr": lag}),
                "state_json": json_text({"ecc": current.eccentricity, "obl": current.obliquity, "prec": current.precession}),
                "future_json": json_text({"outcome": "increase" if future.eccentricity > current.eccentricity else "decrease"}),
                "split": split_by_position(ordinal, len(positions)),
                "oric_features": json_text({"history_depth": lag, "state_change": current.eccentricity - previous.eccentricity}),
                "source": "La2004",
            }
        )
    return rows


def benchmark_rows_from_climate(data_dir: Path) -> list[dict[str, Any]]:
    frame = pd.read_csv(data_dir / "paleoclimate_timeseries.csv").sort_values("time_kyr").reset_index(drop=True)
    for col in ["time_kyr", "target", "forcing_1", "forcing_2"]:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    rows = []
    lag, horizon, stride = 10, 10, 5
    positions = list(range(lag, len(frame) - horizon, stride))
    for ordinal, idx in enumerate(positions):
        current, previous, future = frame.iloc[idx], frame.iloc[idx - lag], frame.iloc[idx + horizon]
        rows.append(
            {
                "case_id": f"paleoclimate:{idx}",
                "domain": "paleoclimate",
                "history_json": json_text({"target_lag": previous.target, "forcing1_lag": previous.forcing_1, "forcing2_lag": previous.forcing_2, "lag_kyr": lag}),
                "state_json": json_text({"target": current.target, "forcing1": current.forcing_1, "forcing2": current.forcing_2}),
                "future_json": json_text({"outcome": "increase" if future.target > current.target else "decrease"}),
                "split": split_by_position(ordinal, len(positions)),
                "oric_features": json_text({"history_depth": lag, "target_change": current.target - previous.target}),
                "source": "LR04 + La2004 aligné",
            }
        )
    return rows


def benchmark_rows_from_vesicles(pairs_frame: pd.DataFrame) -> list[dict[str, Any]]:
    rows = []
    # Toutes les paires réelles sont conservées. La version précédente en
    # sous-échantillonnait 1 600 uniquement pour accélérer un ancien prototype.
    # Le benchmark actuel borne sa représentation vectorielle et peut utiliser
    # l'ensemble sans altérer les données.
    sampled = pairs_frame.sort_values(["source_file", "arm", "transition", "recipient"])
    for idx, item in sampled.iterrows():
        name = str(item.source_file)
        replicate = int(item.replicate)
        split = "train" if replicate == 1 and "-" not in name else "validation" if replicate == 2 else "test"
        rows.append(
            {
                "case_id": f"vesicle:{name}:{item.arm}:{int(item.transition)}:{item.recipient}:{idx}",
                "domain": "vesicle",
                "history_json": json_text({"condition": item.condition, "arm": item.arm, "generation": int(item.transition), "duration_h": float(item.generation_duration_h), "fed": bool(item.fed), "resuspended": bool(item.resuspended)}),
                "state_json": json_text({"parent_turbidity": float(item.parent)}),
                "future_json": json_text({"outcome": "increase" if item.offspring > item.parent else "decrease"}),
                "split": split,
                "oric_features": json_text({"history_depth": int(item.transition) + 1, "coded_lineage": item.mapping_mode == "coded_lineage"}),
                "source": "Sokolskyi & Baum 2026",
            }
        )
    return rows


def benchmark_rows_from_antibiotics() -> list[dict[str, Any]]:
    mic = pd.read_csv(DONOFRIO / "Figure_3_N-lim_Expt_MIC_Raw_Data.csv")
    medians = mic.groupby("Antibiotic")["MIC (ug/mL)"].median()
    rows = []
    for idx, item in mic.iterrows():
        split = split_by_number(item["Strain"])
        rows.append(
            {
                "case_id": f"antibiotic_mic:{idx}",
                "domain": "antibiotic",
                "history_json": json_text({"ancestor": item["Ancestor"], "limitation": item["Limitation"], "strain": str(item["Strain"])}),
                "state_json": json_text({"antibiotic": item["Antibiotic"]}),
                "future_json": json_text({"outcome": "increase" if float(item["MIC (ug/mL)"]) > float(medians[item["Antibiotic"]]) else "decrease"}),
                "split": split,
                "oric_features": json_text({"historical_lineage": item["Ancestor"], "environment": item["Limitation"]}),
                "source": "Donofrio et al. 2026",
            }
        )
    return rows


def benchmark_rows_from_windels(data_dir: Path) -> list[dict[str, Any]]:
    cycles = pd.read_csv(data_dir / "antibiotic_cycles.csv")
    measurements = pd.read_csv(data_dir / "antibiotic_measurements.csv")
    merged = cycles.merge(measurements, on=["lineage_id", "cycle"], how="inner")
    merged = merged.sort_values(["lineage_id", "cycle"])
    rows: list[dict[str, Any]] = []
    for lineage_id, group in merged.groupby("lineage_id", sort=True):
        group = group.sort_values("cycle").reset_index(drop=True)
        measurable = [name for name in ["survival", "mic", "persister_fraction", "fitness"] if group[name].notna().sum() >= 2]
        if not measurable:
            continue
        target_column = max(measurable, key=lambda name: int(group[name].notna().sum()))
        valid = group.dropna(subset=[target_column]).reset_index(drop=True)
        for position in range(1, len(valid)):
            previous = valid.iloc[position - 1]
            current = valid.iloc[position]
            split = split_by_number(lineage_id)
            state = {
                name: (float(current[name]) if pd.notna(current[name]) else None)
                for name in ["mic", "survival", "persister_fraction", "fitness"]
            }
            rows.append(
                {
                    "case_id": f"windels:{lineage_id}:{int(current.cycle)}:{target_column}",
                    "domain": "antibiotic_longitudinal",
                    "history_json": json_text({
                        "lineage_id": lineage_id,
                        "previous_cycle": int(previous.cycle),
                        "previous_value": float(previous[target_column]),
                        "antibiotic": current.antibiotic,
                        "dose": float(current.dose),
                        "duration": float(current.duration),
                        "recovery_duration": float(current.recovery_duration),
                    }),
                    "state_json": json_text({"cycle": int(current.cycle), "measurements": state}),
                    "future_json": json_text({
                        "outcome": "increase" if float(current[target_column]) > float(previous[target_column]) else "decrease"
                    }),
                    "split": split,
                    "oric_features": json_text({
                        "history_depth": int(current.cycle),
                        "measured_target": target_column,
                        "delta": float(current[target_column]) - float(previous[target_column]),
                    }),
                    "source": "Windels et al.",
                }
            )
    return rows


def benchmark_rows_from_rna(data_dir: Path) -> list[dict[str, Any]]:
    frame = pd.read_csv(data_dir / "prebiotic_rna_evolution.csv")
    frame["round"] = pd.to_numeric(frame["round"], errors="coerce")
    frame["frequency"] = pd.to_numeric(frame["frequency"], errors="coerce")
    rows: list[dict[str, Any]] = []
    for (branch, sequence_id), group in frame.groupby(["branch", "sequence_id"], sort=True):
        group = group.dropna(subset=["round", "frequency"]).sort_values("round").reset_index(drop=True)
        for position in range(1, len(group)):
            previous = group.iloc[position - 1]
            current = group.iloc[position]
            rows.append(
                {
                    "case_id": f"rna:{branch}:{sequence_id}:{int(current['round'])}",
                    "domain": "rna_evolution",
                    "history_json": json_text({
                        "branch": branch,
                        "sequence_id": sequence_id,
                        "previous_round": int(previous["round"]),
                        "previous_frequency": float(previous["frequency"]),
                    }),
                    "state_json": json_text({
                        "round": int(current["round"]),
                        "cluster": current.get("cluster"),
                        "relative_frequency": float(current["relative_frequency"]),
                    }),
                    "future_json": json_text({
                        "outcome": "increase" if float(current["frequency"]) > float(previous["frequency"]) else "decrease"
                    }),
                    "split": split_by_number(f"{branch}:{sequence_id}"),
                    "oric_features": json_text({
                        "history_depth": int(current["round"]),
                        "frequency_change": float(current["frequency"]) - float(previous["frequency"]),
                    }),
                    "source": str(current.get("source_table", "Papastavrou et al.")),
                }
            )
    return rows


def benchmark_rows_from_modern_climate(data_dir: Path) -> list[dict[str, Any]]:
    frame = pd.read_csv(data_dir / "modern_climate_timeseries.csv")
    frame["time"] = pd.to_datetime(frame["time"], errors="coerce")
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    frame = frame.dropna(subset=["time", "value"]).sort_values(["region", "variable", "time"])
    rows: list[dict[str, Any]] = []
    for (region, variable), group in frame.groupby(["region", "variable"], sort=True):
        group = group.reset_index(drop=True)
        positions = list(range(12, len(group) - 12, 3))
        for ordinal, position in enumerate(positions):
            previous = group.iloc[position - 12]
            current = group.iloc[position]
            future = group.iloc[position + 12]
            rows.append(
                {
                    "case_id": f"modern_climate:{region}:{variable}:{current.time.date()}",
                    "domain": "modern_climate",
                    "history_json": json_text({
                        "region": region,
                        "variable": variable,
                        "lag_months": 12,
                        "lag_value": float(previous.value),
                    }),
                    "state_json": json_text({"time": str(current.time.date()), "value": float(current.value)}),
                    "future_json": json_text({
                        "outcome": "increase" if float(future.value) > float(current.value) else "decrease"
                    }),
                    "split": split_by_position(ordinal, len(positions)),
                    "oric_features": json_text({
                        "history_depth_months": 12,
                        "annual_change": float(current.value) - float(previous.value),
                    }),
                    "source": "NASA GISTEMP observations",
                }
            )
    return rows


def benchmark_rows_from_matter() -> list[dict[str, Any]]:
    source = ROOT / "01_branche_matiere/base_transitions/transitions_matiere.csv"
    frame = pd.read_csv(source, sep=";")
    median_regime = float(pd.to_numeric(frame["regime_num"], errors="coerce").median())
    rows = []
    for idx, item in frame.iterrows():
        regime = float(item["regime_num"])
        rows.append(
            {
                "case_id": f"matter:{item['id']}",
                "domain": "matter_transition",
                "history_json": json_text({"before_state": item.get("etat_anterieur"), "date": item.get("date"), "evidence": item.get("niveau_de_preuve")}),
                "state_json": json_text({"n": item.get("dimension_n"), "G": item.get("dimension_G"), "I": item.get("dimension_I"), "E": item.get("dimension_E")}),
                "future_json": json_text({"outcome": "increase" if regime > median_regime else "decrease"}),
                "split": split_by_number(item["id"]),
                "oric_features": json_text({"Pi": item.get("dimension_Pi"), "H": item.get("dimension_H")}),
                "source": "Base des 40 transitions matérielles",
            }
        )
    return rows


def build_benchmarks_and_biology(data_dir: Path, pairs_frame: pd.DataFrame) -> dict[str, Any]:
    # Le benchmark transversal est une table dérivée et n'est plus admissible
    # comme preuve empirique. S'il est déjà versionné, l'intégration des nouvelles
    # observations ne le régénère pas silencieusement avec une population différente.
    benchmark_path = data_dir / "benchmark_cases.csv"
    benchmark_preserved = benchmark_path.exists() and benchmark_path.stat().st_size > 0
    if benchmark_preserved:
        benchmark = pd.read_csv(benchmark_path)
    else:
        rows = []
        rows.extend(benchmark_rows_from_orbit(data_dir))
        rows.extend(benchmark_rows_from_climate(data_dir))
        rows.extend(benchmark_rows_from_vesicles(pairs_frame))
        rows.extend(benchmark_rows_from_antibiotics())
        rows.extend(benchmark_rows_from_windels(data_dir))
        rows.extend(benchmark_rows_from_rna(data_dir))
        rows.extend(benchmark_rows_from_modern_climate(data_dir))
        rows.extend(benchmark_rows_from_matter())
        benchmark = pd.DataFrame(rows).drop_duplicates("case_id")
        write_csv(benchmark_path, benchmark)

    biological = benchmark[benchmark["domain"].isin(["vesicle", "antibiotic", "antibiotic_longitudinal", "rna_evolution"])].copy()
    biology = pd.DataFrame(
        {
            "case_id": biological["case_id"],
            "domain": biological["domain"],
            "history": biological["history_json"],
            "state": biological["state_json"],
            "future_outcome": biological["future_json"].map(lambda value: json.loads(value)["outcome"]),
            "oric_features": biological["oric_features"],
            "split": biological["split"],
            "source": biological["source"],
        }
    )
    write_csv(data_dir / "biology_cases.csv", biology)
    return {
        "benchmark_rows": len(benchmark),
        "benchmark_domains": benchmark.groupby("domain").size().astype(int).to_dict(),
        "benchmark_splits": benchmark.groupby("split").size().astype(int).to_dict(),
        "biology_rows": len(biology),
        "biology_domains": biology.groupby("domain").size().astype(int).to_dict(),
        "benchmark_preserved": benchmark_preserved,
    }


def coverage_registry(summaries: dict[str, Any]) -> dict[str, Any]:
    """Construit le registre d'exécution réelle depuis une politique gelée.

    La disponibilité d'une table ou l'augmentation de son effectif ne peut plus
    élargir automatiquement la liste des tests admis comme empiriques. Toute
    extension de portée exige une modification explicite de EMPIRICAL_POLICY.json.
    """
    policy_path = HERE / "EMPIRICAL_POLICY.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    datasets: dict[str, Any] = {}
    for name, definition in policy.get("datasets", {}).items():
        item = dict(definition)
        item["summary"] = summaries.get(name, {})
        datasets[name] = item
    return {
        "schema_version": int(policy.get("schema_version", 2)),
        "rule": policy.get("rule", "Pare-feu empirique fail-closed."),
        "policy_file": "EMPIRICAL_POLICY.json",
        "datasets": datasets,
    }


def write_report(data_dir: Path, summaries: dict[str, Any], coverage: dict[str, Any]) -> None:
    lines = [
        "# Intégration maximale des données déjà présentes",
        "",
        "Aucun gabarit de `examples/data` n'est utilisé. Aucune valeur absente n'est imputée.",
        "",
        "## Tables produites",
        "",
    ]
    for name, summary in summaries.items():
        lines.append(f"### {name}")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
        lines.append("```")
        lines.append("")
    lines.extend(["## Portée réelle dans le catalogue", ""])
    for dataset, item in coverage["datasets"].items():
        lines.append(f"- **{dataset}** : {len(item['supported_test_ids'])} tests couverts. {item['limitations']}")
    (HERE / "INTEGRATION_MAXIMALE_DONNEES_EXISTANTES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    args = parser.parse_args()
    data_dir = args.data_dir.resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    summaries: dict[str, Any] = {}
    summaries["partition_experiments"] = build_partition_experiments(data_dir)
    # `ignore_cleanup_errors` protège la fin du script sous Windows. Les
    # classeurs sont bien refermés, mais l'effacement du dossier temporaire
    # peut encore échouer sur `WinError 32` lorsque l'antivirus ou l'indexeur
    # tient brièvement un des `.xlsx` extraits. Sans cette option, l'intégration
    # complète échouait après avoir écrit toutes ses tables, et le système
    # nettoie de toute façon ce dossier.
    with tempfile.TemporaryDirectory(
        prefix="oric-vesicles-", ignore_cleanup_errors=True
    ) as temporary:
        work = Path(temporary)
        summaries["prebiotic_lineages"], pairs = build_vesicle_lineages(data_dir, work)
        summaries["prebiotic_design"] = {
            "rows": int(pd.read_csv(data_dir / "prebiotic_design.csv").shape[0]),
            "source": summaries["prebiotic_lineages"]["source"],
        }
        summaries["prebiotic_timecourses"] = build_vesicle_timecourses(data_dir, work)
        summaries["prebiotic_auxiliary_measurements"] = build_vesicle_auxiliary(data_dir, work)
        summaries["prebiotic_log_auxiliary_measurements"] = build_vesicle_log_auxiliary(data_dir, work)
        summaries["prebiotic_lineages"].update({
            "timecourse_rows": summaries["prebiotic_timecourses"]["rows"],
            "timecourse_series": summaries["prebiotic_timecourses"]["series"],
            "figure3_measurements": summaries["prebiotic_auxiliary_measurements"]["rows"],
            "log_auxiliary_measurements": summaries["prebiotic_log_auxiliary_measurements"]["rows"],
            "log_auxiliary_types": summaries["prebiotic_log_auxiliary_measurements"]["measurements"],
        })
    summaries["cell_architecture"] = build_cell_architecture(data_dir)
    summaries["antibiotic_design"], _ = build_antibiotic_design_and_aux(data_dir)
    summaries["benchmark_cases"] = build_benchmarks_and_biology(data_dir, pairs)
    summaries["biology_cases"] = {
        "rows": summaries["benchmark_cases"]["biology_rows"],
        "domains": summaries["benchmark_cases"]["biology_domains"],
    }
    lot_summaries, lot_coverage = integrate_scientific_bundle(data_dir)
    summaries.update(lot_summaries)
    if "partition_experiments_extension" in lot_summaries:
        summaries["partition_experiments"].update(lot_summaries["partition_experiments_extension"])

    coverage = coverage_registry(summaries)
    summary_map = {
        "modern_climate_ensemble": summaries.get("modern_climate_ensemble", {}),
        "reaction_network": summaries.get("astrochemistry", {}),
        "molecular_inventory": summaries.get("astrochemistry", {}).get("molecular_inventory", {}),
        "nucleosynthesis_yields": summaries.get("nucleosynthesis_yields", {}),
        "isotope_tracers": summaries.get("isotope_tracers", {}),
        "partition_experiments": summaries.get("partition_experiments", {}),
        "endosymbiosis_events": summaries.get("endosymbiosis_events", {}),
    }
    for dataset_name in lot_coverage:
        if dataset_name in coverage["datasets"]:
            coverage["datasets"][dataset_name]["summary"] = summary_map.get(dataset_name, {})

    (data_dir / "REAL_DATA_COVERAGE.json").write_text(
        json.dumps(coverage, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    provenance = {
        "rule": "aucune donnée simulée, inventée ou imputée",
        "generated_tables": summaries,
        "coverage_file": "REAL_DATA_COVERAGE.json",
        "excluded": ["plateforme/source_corrigee/examples/data/**"],
        "external_scientific_bundle": lot_summaries,
        "external_source_manifest": "donnees_externes/lot_scientifique_maximal_2026_08_05/SOURCE.json",
        "external_triage": "plateforme/campagne_maximale_reelle/TRI_LOT_SCIENTIFIQUE_2026_08_05.json",
    }
    (HERE / "PROVENANCE_INTEGRATION_DEPOT.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_report(data_dir, summaries, coverage)
    print(json.dumps({"status": "integrated", "summaries": summaries}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
