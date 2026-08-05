from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "donnees_externes/speleothemes_noaa_0_22ka/extracted"
OUT = HERE / "resultats"


def locate_csv() -> Path | None:
    matches = sorted(DATA.rglob("speleothem-d18o-0-22k.csv"))
    return matches[0] if matches else None


def choose_column(columns: list[str], patterns: tuple[str, ...]) -> str | None:
    normalized = {column: re.sub(r"[^a-z0-9]+", "", column.lower()) for column in columns}
    for pattern in patterns:
        for column, value in normalized.items():
            if pattern in value:
                return column
    return None


def read_csv_robust(path: Path) -> tuple[pd.DataFrame, str]:
    """Lit une compilation NOAA ancienne sans supposer qu'elle est en UTF-8."""
    errors: list[str] = []
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return pd.read_csv(path, low_memory=False, encoding=encoding), encoding
        except UnicodeDecodeError as exc:
            errors.append(f"{encoding}: {exc}")
    raise UnicodeError("aucun encodage accepté: " + " | ".join(errors))


def audit(path: Path) -> dict[str, object]:
    data, source_encoding = read_csv_robust(path)
    columns = [str(column) for column in data.columns]
    age_column = choose_column(columns, ("ageka", "ageyr", "age", "yearbp"))
    isotope_column = choose_column(columns, ("d18o", "delta18o", "oxygenisotope"))
    site_column = choose_column(columns, ("site", "cave", "record", "entity"))
    latitude_column = choose_column(columns, ("latitude", "lat"))
    longitude_column = choose_column(columns, ("longitude", "lon"))
    selected = [column for column in (age_column, isotope_column) if column is not None]
    usable = data.dropna(subset=selected).copy() if len(selected) == 2 else pd.DataFrame()
    age_numeric = pd.to_numeric(usable[age_column], errors="coerce") if age_column else pd.Series(dtype=float)
    isotope_numeric = (
        pd.to_numeric(usable[isotope_column], errors="coerce") if isotope_column else pd.Series(dtype=float)
    )
    valid = age_numeric.notna() & isotope_numeric.notna()
    age_numeric = age_numeric[valid]
    isotope_numeric = isotope_numeric[valid]
    sites = int(usable.loc[valid, site_column].nunique()) if site_column else None
    result = {
        "status": "audited" if len(age_numeric) else "schema_not_recognized",
        "rows_total": int(len(data)),
        "source_encoding": source_encoding,
        "rows_age_isotope": int(len(age_numeric)),
        "detected_columns": {
            "age": age_column,
            "d18O": isotope_column,
            "site": site_column,
            "latitude": latitude_column,
            "longitude": longitude_column,
        },
        "age_min": float(age_numeric.min()) if len(age_numeric) else None,
        "age_max": float(age_numeric.max()) if len(age_numeric) else None,
        "independent_site_count": sites,
        "d18O_min": float(isotope_numeric.min()) if len(isotope_numeric) else None,
        "d18O_max": float(isotope_numeric.max()) if len(isotope_numeric) else None,
        "use_decision": (
            "chronology_quality_and_external_proxy_audit_only"
            if len(age_numeric)
            else "manual_schema_mapping_required"
        ),
        "limit": (
            "La compilation 0-22 ka prépare un contrôle indépendant de chronologie et de proxy. "
            "Sa durée ne suffit pas à tester la bande orbitale de 100 ka."
        ),
    }
    return result


def main() -> dict[str, object]:
    path = locate_csv()
    if path is None:
        result = {
            "status": "waiting_for_external_data",
            "missing": ["speleothem-d18o-0-22k.csv"],
            "use_decision": "not_executed",
        }
    else:
        result = audit(path)
        result["source_file"] = str(path)
    OUT.mkdir(exist_ok=True)
    (OUT / "AUDIT_SPELEOTHEMES.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


if __name__ == "__main__":
    main()
