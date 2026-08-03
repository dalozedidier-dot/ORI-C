from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    pass


def load_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"Configuration introuvable: {config_path}")
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ConfigError("La racine YAML doit être un objet.")
    validate_config(data)
    data["_config_path"] = str(config_path.resolve())
    return data


def validate_config(config: dict[str, Any]) -> None:
    required_sections = ["experiment", "scenarios", "spectrum", "insolation", "climate"]
    missing = [key for key in required_sections if key not in config]
    if missing:
        raise ConfigError(f"Sections manquantes: {', '.join(missing)}")

    exp = config["experiment"]
    for key in ["name", "backend", "duration_years", "output_step_years", "output_dir"]:
        if key not in exp:
            raise ConfigError(f"experiment.{key} est obligatoire")
    if exp["backend"] not in {"surrogate", "rebound"}:
        raise ConfigError("experiment.backend doit valoir 'surrogate' ou 'rebound'")
    if float(exp["duration_years"]) <= 0 or float(exp["output_step_years"]) <= 0:
        raise ConfigError("Les durées et pas de sortie doivent être positifs")
    if float(exp["output_step_years"]) > float(exp["duration_years"]):
        raise ConfigError("Le pas de sortie ne peut pas dépasser la durée")

    scenarios = config["scenarios"]
    if not isinstance(scenarios, list) or not scenarios:
        raise ConfigError("scenarios doit être une liste non vide")
    names = []
    for scenario in scenarios:
        if not isinstance(scenario, dict) or "name" not in scenario:
            raise ConfigError("Chaque scénario doit avoir un nom")
        names.append(str(scenario["name"]))
        mods = scenario.get("modifications", {})
        if not isinstance(mods, dict):
            raise ConfigError(f"Modifications invalides pour {scenario['name']}")
    if len(names) != len(set(names)):
        raise ConfigError("Les noms de scénarios doivent être uniques")
    if "baseline" not in names:
        raise ConfigError("Un scénario nommé 'baseline' est obligatoire")

    spec = config["spectrum"]
    if float(spec["min_period_years"]) <= 0:
        raise ConfigError("spectrum.min_period_years doit être positif")
    if float(spec["max_period_years"]) <= float(spec["min_period_years"]):
        raise ConfigError("La période maximale doit dépasser la période minimale")

    if exp["backend"] == "rebound":
        if "rebound" not in config:
            raise ConfigError("La section rebound est obligatoire pour le backend N-corps")
        rebound = config["rebound"]
        dt = float(rebound.get("timestep_years", 0))
        if dt <= 0:
            raise ConfigError("rebound.timestep_years doit être positif")
        direction = str(rebound.get("time_direction", "forward")).lower()
        if direction not in {"forward", "backward", "future", "past", "1", "-1"}:
            raise ConfigError("rebound.time_direction doit valoir forward ou backward")
        initial = str(rebound.get("initial_conditions", "elements_j2000")).lower()
        if initial not in {
            "elements",
            "elements_j2000",
            "approximate",
            "horizons",
            "horizons_j2000",
            "de441",
        }:
            raise ConfigError("rebound.initial_conditions est inconnu")
        relativity = str(rebound.get("general_relativity", "none")).lower()
        if relativity not in {
            "none",
            "off",
            "false",
            "gr_potential",
            "gr",
            "gr_full",
        }:
            raise ConfigError("rebound.general_relativity est inconnu")
        included = rebound.get("include_bodies", rebound.get("include_planets"))
        if included is not None and (
            not isinstance(included, list)
            or not included
            or not all(isinstance(name, str) and name for name in included)
        ):
            raise ConfigError("rebound.include_bodies doit être une liste de noms")
