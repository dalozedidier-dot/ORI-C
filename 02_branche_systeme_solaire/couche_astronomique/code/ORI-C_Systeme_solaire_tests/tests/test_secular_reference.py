from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "reference" / "la2010"


def _read(name: str) -> list[dict[str, str]]:
    with (REF / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_la2010a_reference_modes_are_complete() -> None:
    rows = _read("La2010a_secular_frequencies.csv")
    assert [row["mode"] for row in rows[:8]] == [f"g{i}" for i in range(1, 9)]
    assert [row["mode"] for row in rows[8:]] == [f"s{i}" for i in range(1, 9)]
    assert next(row for row in rows if row["mode"] == "g5")["la2010a_arcsec_per_year"] == "4.257482"
    assert next(row for row in rows if row["mode"] == "g8")["la2004_arcsec_per_year"] == "0.673019"


def test_eccentricity_combination_periods_are_recomputable() -> None:
    rows = {row["mode"]: float(row["la2010a_arcsec_per_year"]) for row in _read("La2010a_secular_frequencies.csv")}
    combos = _read("La2010a_eccentricity_combinations.csv")
    for row in combos:
        left, right = row["combination"].split("-")
        diff = abs(rows[left] - rows[right])
        period = 1_296_000.0 / diff
        assert abs(diff - float(row["difference_arcsec_per_year"])) < 1e-9
        assert abs(period - float(row["derived_period_years"])) < 1e-6
