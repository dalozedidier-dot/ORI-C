"""Importe NASA GISTEMP v4 sans générer, interpoler ni imputer de données."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import netCDF4

ROOT = Path(__file__).resolve().parents[2]
CAMPAIGN = ROOT / "campagne_maximale_reelle"
RAW = CAMPAIGN / "sources_brutes" / "NASA_GISTEMP_v4"
DATA = CAMPAIGN / "data"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def import_monthly() -> int:
    source = RAW / "GLB.Ts+dSST.csv"
    rows = []
    with source.open(encoding="utf-8-sig", newline="") as stream:
        next(stream)  # titre NASA hors tableau
        for row in csv.DictReader(stream):
            year = int(row["Year"])
            for month_number, month in enumerate(MONTHS, 1):
                value = row.get(month, "").strip()
                if value and value != "***":
                    rows.append({
                        "time": f"{year:04d}-{month_number:02d}-15",
                        "variable": "surface_temperature_anomaly_C",
                        "value": float(value),
                        "region": "global",
                    })
    zonal = RAW / "ZonAnn.Ts+dSST.csv"
    with zonal.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        zones = [name for name in reader.fieldnames or [] if name != "Year"]
        for row in reader:
            year = int(row["Year"])
            for zone in zones:
                value = row.get(zone, "").strip()
                if value and value != "***":
                    rows.append({
                        "time": f"{year:04d}-07-15",
                        "variable": "surface_temperature_anomaly_C",
                        "value": float(value),
                        "region": zone,
                    })
    output = DATA / "modern_climate_timeseries.csv"
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["time", "variable", "value", "region"])
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def import_ensemble() -> int:
    source = RAW / "KeySeries" / "ensembleCombinedSeries_Global.nc"
    rows = []
    with netCDF4.Dataset(source) as dataset:
        times = dataset.variables["time"][:]
        members = dataset.variables["ens"][:]
        values = dataset.variables["tas"][:]
        origin = datetime(1880, 1, 1, tzinfo=timezone.utc)
        for member_index, member in enumerate(members):
            for time_index, days in enumerate(times):
                value = float(values[member_index, time_index])
                if value <= -9000:
                    continue
                rows.append({
                    "model": "NASA_GISTEMPv4_observational_uncertainty",
                    "scenario": "historical_observational_reconstruction",
                    "member": int(member),
                    "time": (origin + timedelta(days=int(days))).date().isoformat(),
                    "variable": "surface_temperature_anomaly_K",
                    "value": value,
                    "region": "global",
                })
    output = DATA / "modern_climate_ensemble.csv"
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["model", "scenario", "member", "time", "variable", "value", "region"])
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main() -> int:
    monthly = import_monthly()
    ensemble = import_ensemble()
    provenance = {
        "dataset": "NASA GISTEMP v4",
        "accessed_at": "2026-08-01",
        "official_page": "https://data.giss.nasa.gov/gistemp/",
        "publication": "https://doi.org/10.1029/2023JD040179",
        "path_base": "plateforme/campagne_maximale_reelle",
        "raw_files": {
            "sources_brutes/NASA_GISTEMP_v4/GLB.Ts+dSST.csv": sha256(RAW / "GLB.Ts+dSST.csv"),
            "sources_brutes/NASA_GISTEMP_v4/ZonAnn.Ts+dSST.csv": sha256(RAW / "ZonAnn.Ts+dSST.csv"),
            "sources_brutes/NASA_GISTEMP_v4/KeySeries.zip": sha256(RAW / "KeySeries.zip"),
        },
        "outputs": {
            "data/modern_climate_timeseries.csv": {"rows": monthly, "sha256": sha256(DATA / "modern_climate_timeseries.csv")},
            "data/modern_climate_ensemble.csv": {"rows": ensemble, "sha256": sha256(DATA / "modern_climate_ensemble.csv")},
        },
        "transformations": [
            "monthly table converted from wide month columns to long rows",
            "NetCDF global combined observational-uncertainty ensemble converted to long rows",
            "no interpolation, imputation, resampling or synthetic augmentation",
        ],
    }
    (CAMPAIGN / "PROVENANCE_GISTEMP.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(provenance, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
