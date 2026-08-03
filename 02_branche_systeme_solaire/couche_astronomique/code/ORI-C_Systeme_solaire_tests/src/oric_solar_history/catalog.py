from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class Planet:
    name: str
    mass_msun: float
    a_au: float
    e: float
    inc_deg: float
    mean_longitude_deg: float
    long_peri_deg: float
    long_node_deg: float


def default_catalog_path() -> Path:
    packaged = Path(__file__).resolve().parent / "data" / "planetary_j2000.csv"
    if packaged.exists():
        return packaged
    return Path(__file__).resolve().parents[2] / "data" / "planetary_j2000.csv"


def load_catalog(path: str | Path | None = None) -> dict[str, Planet]:
    if path is None:
        path = default_catalog_path()
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Catalogue planétaire introuvable: {path}")
    frame = pd.read_csv(path)
    result: dict[str, Planet] = {}
    for row in frame.to_dict(orient="records"):
        planet = Planet(
            name=str(row["name"]),
            mass_msun=float(row["mass_msun"]),
            a_au=float(row["a_au"]),
            e=float(row["e"]),
            inc_deg=float(row["inc_deg"]),
            mean_longitude_deg=float(row["mean_longitude_deg"]),
            long_peri_deg=float(row["long_peri_deg"]),
            long_node_deg=float(row["long_node_deg"]),
        )
        result[planet.name] = planet
    return result


def apply_modifications(catalog: dict[str, Planet], modifications: dict) -> dict[str, Planet]:
    updated = dict(catalog)
    for body, changes in modifications.items():
        if body not in updated:
            raise KeyError(f"Corps inconnu dans les modifications: {body}")
        p = updated[body]
        mass = p.mass_msun * float(changes.get("mass_scale", 1.0))
        a = p.a_au * float(changes.get("a_scale", 1.0))
        e = p.e * float(changes.get("e_scale", 1.0))
        if "mass_msun" in changes:
            mass = float(changes["mass_msun"])
        if "a_au" in changes:
            a = float(changes["a_au"])
        if "e" in changes:
            e = float(changes["e"])
        if mass <= 0 or a <= 0 or not (0 <= e < 1):
            raise ValueError(f"Paramètres non physiques pour {body}")
        updated[body] = replace(p, mass_msun=mass, a_au=a, e=e)
    return updated
