from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

TAP_QUERY = (
    "select pl_name,hostname,discoverymethod,disc_year,pl_orbper,pl_orbpererr1,pl_orbpererr2,"
    "pl_rade,pl_radeerr1,pl_radeerr2,pl_bmasse,pl_bmasseerr1,pl_bmasseerr2,pl_bmassprov,"
    "pl_dens,pl_denserr1,pl_denserr2,pl_eqt,pl_eqterr1,pl_eqterr2,st_teff,st_tefferr1,"
    "st_tefferr2,st_rad,st_raderr1,st_raderr2,st_mass,st_masserr1,st_masserr2,sy_pnum,"
    "pl_refname,disc_refname,rowupdate from ps where default_flag=1"
)

COLUMN_MAP = {
    "pl_name": "planet_name", "hostname": "host_name", "discoverymethod": "discovery_method",
    "disc_year": "discovery_year", "pl_orbper": "orbital_period_days", "pl_rade": "radius_earth",
    "pl_bmasse": "mass_earth", "pl_dens": "density_g_cm3", "pl_eqt": "equilibrium_temperature_k",
    "st_teff": "stellar_teff_k", "st_rad": "stellar_radius_solar", "st_mass": "stellar_mass_solar",
    "sy_pnum": "system_planet_count", "pl_refname": "parameter_reference",
    "disc_refname": "discovery_reference", "rowupdate": "archive_row_update",
}

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def main() -> None:
    parser = argparse.ArgumentParser(description="Import strict des solutions NASA Exoplanet Archive publiees par defaut")
    parser.add_argument("raw_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("provenance_json", type=Path)
    args = parser.parse_args()
    raw = pd.read_csv(args.raw_csv)
    missing = sorted(set(COLUMN_MAP) - set(raw.columns))
    if missing:
        raise ValueError(f"Colonnes NASA absentes: {missing}")
    output = raw[list(COLUMN_MAP)].rename(columns=COLUMN_MAP)
    if output["planet_name"].duplicated().any():
        raise ValueError("La requete ne contient pas une solution unique par planete")
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output_csv, index=False)
    campaign_root = args.provenance_json.parent.resolve()
    def portable(path: Path) -> str:
        return path.resolve().relative_to(campaign_root).as_posix()
    provenance = {
        "source": "NASA Exoplanet Archive, Planetary Systems (PS), default_flag=1",
        "source_url": "https://exoplanetarchive.ipac.caltech.edu/TAP/sync",
        "tap_query": TAP_QUERY,
        "tap_format": "csv",
        "documentation": "https://exoplanetarchive.ipac.caltech.edu/docs/TAP/usingTAP.html",
        "dataset_doi": "10.26133/NEA2", "accessed_at": "2026-08-01", "transformed_at_utc": datetime.now(timezone.utc).isoformat(),
        "path_base": "plateforme/campagne_maximale_reelle",
        "raw_file": portable(args.raw_csv), "raw_sha256": sha256(args.raw_csv),
        "output_file": portable(args.output_csv), "output_sha256": sha256(args.output_csv), "rows": int(len(output)),
        "rules": ["solutions publiees marquees default_flag=1 par l'archive", "aucune imputation, interpolation, simulation ou augmentation", "cellules absentes conservees vides", "PS choisi pour conserver un jeu de parametres auto-coherent par reference"],
    }
    args.provenance_json.parent.mkdir(parents=True, exist_ok=True)
    args.provenance_json.write_text(json.dumps(provenance, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"rows": len(output), "output": str(args.output_csv), "sha256": provenance["output_sha256"]}))

if __name__ == "__main__":
    main()
