from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / "donnees_externes/speleothemes_noaa_0_22ka/extracted"
OUT = HERE / "resultats"


def source_reference(path: Path) -> str:
    """Chemin stable, indépendant du dossier local d’extraction."""
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


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


def read_text_robust(path: Path) -> tuple[str, str]:
    errors: list[str] = []
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=encoding), encoding
        except UnicodeDecodeError as exc:
            errors.append(f"{encoding}: {exc}")
    raise UnicodeError("aucun encodage accepté: " + " | ".join(errors))


def _trim_row(row: list[str]) -> list[str]:
    result = [value.strip() for value in row]
    while result and result[-1] == "":
        result.pop()
    return result


def _find_header(rows: list[list[str]], required: set[str], start: int = 0) -> int | None:
    for index in range(start, len(rows)):
        normalized = {re.sub(r"[^a-z0-9]+", "", value.lower()) for value in rows[index]}
        if required.issubset(normalized):
            return index
    return None


def _frame(header: list[str], rows: list[list[str]]) -> pd.DataFrame:
    width = len(header)
    normalized_rows = [(row + [""] * width)[:width] for row in rows if any(value.strip() for value in row)]
    return pd.DataFrame(normalized_rows, columns=header)


def read_csv_robust(path: Path) -> tuple[pd.DataFrame, str, str, int | None]:
    """Lit soit un CSV tabulaire simple, soit la compilation NOAA à deux tables."""
    text, encoding = read_text_robust(path)
    rows = [_trim_row(row) for row in csv.reader(io.StringIO(text))]

    metadata_header = _find_header(
        rows,
        {"coreindex", "sitename", "latitude", "longitude"},
    )
    data_header = _find_header(
        rows,
        {"coreindex", "agecalbp", "d18ocarbpdb"},
        start=(metadata_header + 1 if metadata_header is not None else 0),
    )
    if metadata_header is not None and data_header is not None:
        metadata_end = next(
            (
                index
                for index in range(metadata_header + 1, data_header)
                if rows[index] and rows[index][0].strip().upper() == "DATA"
            ),
            data_header,
        )
        metadata = _frame(rows[metadata_header], rows[metadata_header + 1 : metadata_end])
        measurements = _frame(rows[data_header], rows[data_header + 1 :])
        metadata_key = choose_column([str(column) for column in metadata.columns], ("coreindex",))
        data_key = choose_column([str(column) for column in measurements.columns], ("coreindex",))
        if metadata_key and data_key:
            metadata[metadata_key] = pd.to_numeric(metadata[metadata_key], errors="coerce")
            measurements[data_key] = pd.to_numeric(measurements[data_key], errors="coerce")
            merged = measurements.merge(
                metadata,
                left_on=data_key,
                right_on=metadata_key,
                how="left",
                suffixes=("", "_metadata"),
            )
            return merged, encoding, "noaa_two_table_compilation", int(len(metadata))

    # Format simple utilisé par les fixtures et accepté pour d'autres exports.
    data = pd.read_csv(io.StringIO(text), low_memory=False)
    return data, encoding, "single_table", None


def audit(path: Path) -> dict[str, object]:
    data, source_encoding, source_schema, metadata_rows = read_csv_robust(path)
    columns = [str(column) for column in data.columns]
    age_column = choose_column(columns, ("agecalbp", "ageka", "ageyr", "yearbp", "age"))
    isotope_column = choose_column(columns, ("d18ocarbpdb", "d18o", "delta18o", "oxygenisotope"))
    site_column = choose_column(columns, ("sitename", "site", "cave", "record", "entity"))
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
    age_normalized = re.sub(r"[^a-z0-9]+", "", age_column.lower()) if age_column else ""
    age_unit = "cal_yr_BP" if "calbp" in age_normalized or "yearbp" in age_normalized else "ka_or_source_unit"
    result = {
        "status": "audited" if len(age_numeric) else "schema_not_recognized",
        "rows_total": int(len(data)),
        "metadata_rows": metadata_rows,
        "source_encoding": source_encoding,
        "source_schema": source_schema,
        "rows_age_isotope": int(len(age_numeric)),
        "detected_columns": {
            "age": age_column,
            "d18O": isotope_column,
            "site": site_column,
            "latitude": latitude_column,
            "longitude": longitude_column,
        },
        "age_unit": age_unit,
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
        result["source_file"] = source_reference(path)
    OUT.mkdir(exist_ok=True)
    (OUT / "AUDIT_SPELEOTHEMES.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


if __name__ == "__main__":
    main()
