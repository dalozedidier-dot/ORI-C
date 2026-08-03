#!/usr/bin/env python3
"""Freeze JPL Horizons/DE441 barycentric J2000 states for reproducible runs."""

from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


HORIZONS_API = "https://ssd.jpl.nasa.gov/api/horizons.api"
J2000_JD_TDB = "2451545.0"
DAYS_PER_JULIAN_YEAR = 365.25
SUN_GM_KM3_S2 = 132_712_440_041.27942

# Planetary barycenter masses match the catalog historically used by the
# project. Pluto includes Charon and the small moons. Asteroid masses use the
# cited JPL/peer-reviewed GM or mass estimates recorded in MASS_SOURCE.
BODY_SPECS: tuple[tuple[str, str, float], ...] = (
    ("Sun", "10", 1.0),
    ("Mercury", "1", 1.660120825e-7),
    ("Venus", "2", 2.447838287e-6),
    ("Earth", "3", 3.040432648e-6),
    ("Mars", "4", 3.227151445e-7),
    ("Jupiter", "5", 9.547919384e-4),
    ("Saturn", "6", 2.858856700e-4),
    ("Uranus", "7", 4.366249613e-5),
    ("Neptune", "8", 5.151383773e-5),
    ("Pluto", "9", 975.4035 / SUN_GM_KM3_S2),
    ("Ceres", "'1;'", 62.6284 / SUN_GM_KM3_S2),
    ("Pallas", "'2;'", 13.63 / SUN_GM_KM3_S2),
    ("Vesta", "'4;'", 17.2882844 / SUN_GM_KM3_S2),
    ("Iris", "'7;'", 6.81e-12),
    ("Bamberga", "'324;'", 5.10e-12),
)

MASS_SOURCE = {
    "Sun": "mass unit",
    "Mercury": "project JPL-system mass catalog",
    "Venus": "project JPL-system mass catalog",
    "Earth": "Earth-Moon barycenter mass, project JPL-system catalog",
    "Mars": "project JPL-system mass catalog",
    "Jupiter": "Jupiter-system mass, project JPL-system catalog",
    "Saturn": "Saturn-system mass, project JPL-system catalog",
    "Uranus": "Uranus-system mass, project JPL-system catalog",
    "Neptune": "Neptune-system mass, project JPL-system catalog",
    "Pluto": "JPL PLU060 Pluto-system GM sum",
    "Ceres": "JPL SBDB GM 62.6284 km^3/s^2",
    "Pallas": "JPL SBDB GM 13.63 km^3/s^2",
    "Vesta": "JPL SBDB GM 17.2882844 km^3/s^2",
    "Iris": "Baer et al. 2008 mass estimate 6.81e-12 Msun",
    "Bamberga": "Pitjeva 2004 mass estimate 5.10e-12 Msun",
}


def _query(command: str, retries: int = 4) -> tuple[dict[str, str], dict[str, Any]]:
    params = {
        "format": "json",
        "COMMAND": command,
        "OBJ_DATA": "NO",
        "MAKE_EPHEM": "YES",
        "EPHEM_TYPE": "VECTORS",
        "CENTER": "@0",
        "TLIST": J2000_JD_TDB,
        "OUT_UNITS": "AU-D",
        "VEC_TABLE": "2",
        "CSV_FORMAT": "YES",
        "REF_PLANE": "ECLIPTIC",
        "REF_SYSTEM": "J2000",
        "VEC_CORR": "NONE",
    }
    url = f"{HORIZONS_API}?{urllib.parse.urlencode(params)}"
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "ORI-C-Solar-History/real-tests"},
            )
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = json.load(response)
            return params, payload
        except Exception as exc:  # pragma: no cover - network retry
            last_error = exc
            time.sleep(2**attempt)
    raise RuntimeError(f"Échec Horizons pour COMMAND={command}") from last_error


def _parse_vector(payload: dict[str, Any]) -> tuple[float, ...]:
    result = str(payload["result"])
    try:
        block = result.split("$$SOE", 1)[1].split("$$EOE", 1)[0]
    except IndexError as exc:
        raise ValueError("Réponse Horizons sans bloc de vecteur") from exc
    line = next(line.strip() for line in block.splitlines() if line.strip())
    fields = [field.strip() for field in line.split(",")]
    if len(fields) < 8:
        raise ValueError(f"Vecteur Horizons incomplet: {line}")
    return tuple(float(value) for value in fields[2:8])


def fetch() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    raw: dict[str, Any] = {
        "api": HORIZONS_API,
        "epoch_jd_tdb": J2000_JD_TDB,
        "center": "Solar System Barycenter",
        "reference_plane": "J2000 ecliptic",
        "out_units": "AU-D",
        "bodies": {},
    }
    for name, command, mass_msun in BODY_SPECS:
        params, payload = _query(command)
        x, y, z, vx_day, vy_day, vz_day = _parse_vector(payload)
        rows.append(
            {
                "name": name,
                "mass_msun": f"{mass_msun:.17g}",
                "x_au": f"{x:.17g}",
                "y_au": f"{y:.17g}",
                "z_au": f"{z:.17g}",
                "vx_au_per_year": f"{vx_day * DAYS_PER_JULIAN_YEAR:.17g}",
                "vy_au_per_year": f"{vy_day * DAYS_PER_JULIAN_YEAR:.17g}",
                "vz_au_per_year": f"{vz_day * DAYS_PER_JULIAN_YEAR:.17g}",
                "epoch_jd_tdb": J2000_JD_TDB,
                "state_source": "NASA/JPL Horizons DE441",
                "mass_source": MASS_SOURCE[name],
            }
        )
        raw["bodies"][name] = {
            "command": command,
            "mass_msun": mass_msun,
            "mass_source": MASS_SOURCE[name],
            "query": params,
            "response": payload,
        }
    return rows, raw


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/horizons_j2000_de441.csv"),
    )
    parser.add_argument(
        "--package-output",
        type=Path,
        default=Path("src/oric_solar_history/data/horizons_j2000_de441.csv"),
    )
    parser.add_argument(
        "--raw-output",
        type=Path,
        default=Path("data/horizons_j2000_de441_raw.json"),
    )
    args = parser.parse_args()
    rows, raw = fetch()
    write_csv(args.output, rows)
    write_csv(args.package_output, rows)
    args.raw_output.parent.mkdir(parents=True, exist_ok=True)
    args.raw_output.write_text(
        json.dumps(raw, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(args.output)
    print(args.package_output)
    print(args.raw_output)


if __name__ == "__main__":
    main()
