#!/usr/bin/env python3
"""Freeze a 6 kyr JPL Horizons Earth-eccentricity validation series."""

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
J2000_JD_TDB = 2451545.0
DAYS_PER_JULIAN_YEAR = 365.25


def _query(retries: int = 4) -> tuple[dict[str, str], dict[str, Any]]:
    epochs = [J2000_JD_TDB - years * DAYS_PER_JULIAN_YEAR for years in range(0, 6_001, 100)]
    params = {
        "format": "json",
        "COMMAND": "3",
        "OBJ_DATA": "NO",
        "MAKE_EPHEM": "YES",
        "EPHEM_TYPE": "ELEMENTS",
        "CENTER": "500@10",
        "TLIST": "\n".join(f"{epoch:.1f}" for epoch in epochs),
        "TLIST_TYPE": "JD",
        "OUT_UNITS": "AU-D",
        "CSV_FORMAT": "YES",
        "REF_PLANE": "ECLIPTIC",
        "REF_SYSTEM": "J2000",
    }
    url = f"{HORIZONS_API}?{urllib.parse.urlencode(params)}"
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "ORI-C-Solar-History/real-tests"},
            )
            with urllib.request.urlopen(request, timeout=120) as response:
                return params, json.load(response)
        except Exception as exc:  # pragma: no cover - network retry
            last_error = exc
            time.sleep(2**attempt)
    raise RuntimeError("Échec de la série de validation Horizons") from last_error


def _parse(payload: dict[str, Any]) -> list[dict[str, str]]:
    result = str(payload["result"])
    try:
        block = result.split("$$SOE", 1)[1].split("$$EOE", 1)[0]
    except IndexError as exc:
        raise ValueError("Réponse Horizons sans bloc d'éléments") from exc
    rows: list[dict[str, str]] = []
    for line in block.splitlines():
        if not line.strip():
            continue
        fields = [field.strip() for field in line.split(",")]
        if len(fields) < 14:
            raise ValueError(f"Ligne Horizons incomplète: {line}")
        jd_tdb = float(fields[0])
        rows.append(
            {
                "time_years": f"{(jd_tdb - J2000_JD_TDB) / DAYS_PER_JULIAN_YEAR:.17g}",
                "elapsed_years": f"{abs((jd_tdb - J2000_JD_TDB) / DAYS_PER_JULIAN_YEAR):.17g}",
                "jd_tdb": f"{jd_tdb:.17g}",
                "calendar_tdb": fields[1],
                "eccentricity": f"{float(fields[2]):.17g}",
                "semi_major_axis_au": f"{float(fields[11]):.17g}",
                "target": "Earth-Moon barycenter",
                "center": "Sun",
                "source": "NASA/JPL Horizons DE441",
            }
        )
    return sorted(rows, key=lambda row: float(row["time_years"]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/reference/horizons/earth_elements_j2000_to_minus6kyr.csv"),
    )
    parser.add_argument(
        "--raw-output",
        type=Path,
        default=Path("data/reference/horizons/earth_elements_j2000_to_minus6kyr_raw.json"),
    )
    args = parser.parse_args()
    params, payload = _query()
    rows = _parse(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    args.raw_output.write_text(
        json.dumps(
            {
                "api": HORIZONS_API,
                "query": params,
                "response": payload,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(args.output)
    print(args.raw_output)


if __name__ == "__main__":
    main()
