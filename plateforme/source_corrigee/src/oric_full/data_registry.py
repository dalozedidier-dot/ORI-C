from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import json

import pandas as pd


@dataclass(frozen=True)
class DatasetSchema:
    name: str
    filename: str
    required_columns: tuple[str, ...]
    description: str


SCHEMAS: dict[str, DatasetSchema] = {
    "states": DatasetSchema("states", "states.csv", ("system_id", "time", "state_json"), "États ORI-C"),
    "relations": DatasetSchema("relations", "relations.csv", ("source", "target", "relation_type"), "Relations typées"),
    "matter_transitions": DatasetSchema("matter_transitions", "matter_transitions.csv", ("transition_id", "before_state", "after_state", "n", "G", "I", "E", "Pi", "H", "evidence_level"), "40 transitions matérielles"),
    "nucleosynthesis_yields": DatasetSchema("nucleosynthesis_yields", "nucleosynthesis_yields.csv", ("source_id", "mass_solar", "metallicity", "element", "yield_mass", "uncertainty"), "Rendements de nucléosynthèse"),
    "reaction_network": DatasetSchema("reaction_network", "reaction_network.csv", ("reaction_id", "reactants", "products", "rate", "temperature_min", "temperature_max"), "Réseau chimique"),
    "molecular_inventory": DatasetSchema("molecular_inventory", "molecular_inventory.csv", ("environment_id", "species", "abundance", "uncertainty"), "Inventaire moléculaire"),
    "thermochemical_phases": DatasetSchema("thermochemical_phases", "thermochemical_phases.csv", ("phase", "temperature", "pressure", "gibbs_energy", "composition"), "Phases thermochimiques"),
    "isotope_tracers": DatasetSchema("isotope_tracers", "isotope_tracers.csv", ("sample_id", "group", "tracer", "value", "uncertainty"), "Traceurs isotopiques"),
    "chronometers": DatasetSchema("chronometers", "chronometers.csv", ("sample_id", "system", "age_myr", "uncertainty_myr"), "Chronomètres isotopiques"),
    "body_properties": DatasetSchema("body_properties", "body_properties.csv", ("body_id", "radius_km", "density", "porosity", "formation_time_myr", "al26_ratio"), "Propriétés de corps"),
    "partition_experiments": DatasetSchema("partition_experiments", "partition_experiments.csv", ("experiment_id", "element", "pressure_gpa", "temperature_k", "delta_iw", "logD", "uncertainty"), "Partage métal-silicate"),
    "volatile_inventory": DatasetSchema("volatile_inventory", "volatile_inventory.csv", ("sample_id", "volatile", "initial_mass", "core_mass", "mantle_mass", "atmosphere_mass", "lost_mass"), "Budget des volatils"),
    "late_accretion_tracers": DatasetSchema("late_accretion_tracers", "late_accretion_tracers.csv", ("sample_id", "tracer", "final_value", "uncertainty", "candidate_source"), "Traceurs d'accrétion tardive"),
    "planetary_histories": DatasetSchema("planetary_histories", "planetary_histories.csv", ("body_id", "initial_composition", "provenance", "accretion_time", "thermal_history", "redox_history", "losses", "late_inputs", "final_partition"), "Histoires planétaires"),
    "exoplanet_observations": DatasetSchema("exoplanet_observations", "exoplanet_observations.csv", ("planet_name", "host_name", "discovery_method", "discovery_year", "orbital_period_days", "radius_earth", "mass_earth", "density_g_cm3", "equilibrium_temperature_k", "stellar_teff_k", "stellar_radius_solar", "stellar_mass_solar", "system_planet_count", "parameter_reference", "discovery_reference", "archive_row_update"), "Exoplanètes confirmées, solutions publiées par défaut de la NASA Exoplanet Archive"),
    "orbital_initial_conditions": DatasetSchema("orbital_initial_conditions", "orbital_initial_conditions.csv", ("body", "epoch", "x", "y", "z", "vx", "vy", "vz", "mass"), "Conditions initiales orbitales"),
    "ephemerides": DatasetSchema("ephemerides", "ephemerides.csv", ("time", "body", "x", "y", "z", "vx", "vy", "vz"), "Éphémérides"),
    # Une solution de référence peut ne publier qu'une observable. Le moteur
    # spectral analyse toutes les colonnes disponibles sans inventer les autres.
    "orbital_timeseries": DatasetSchema("orbital_timeseries", "orbital_timeseries.csv", ("time", "eccentricity"), "Séries orbitales (observables disponibles)"),
    "orbital_reference": DatasetSchema("orbital_reference", "orbital_reference.csv", ("time", "observable", "value", "uncertainty"), "Référence orbitale"),
    "paleoclimate_timeseries": DatasetSchema("paleoclimate_timeseries", "paleoclimate_timeseries.csv", ("time_kyr", "target", "forcing_1", "forcing_2"), "Paléoclimat"),
    "modern_climate_timeseries": DatasetSchema("modern_climate_timeseries", "modern_climate_timeseries.csv", ("time", "variable", "value", "region"), "Climat moderne"),
    "modern_climate_ensemble": DatasetSchema("modern_climate_ensemble", "modern_climate_ensemble.csv", ("model", "scenario", "member", "time", "variable", "value", "region"), "Ensembles climatiques"),
    "prebiotic_rna_evolution": DatasetSchema("prebiotic_rna_evolution", "prebiotic_rna_evolution.csv", ("branch", "round", "sequence_id", "cluster", "frequency", "relative_frequency", "source_table"), "Évolution expérimentale de populations d'ARN catalytique"),
    "prebiotic_design": DatasetSchema("prebiotic_design", "prebiotic_design.csv", ("condition_id", "temperature", "ph", "wet_dry_cycles", "uv_flux", "mineral", "replicate"), "Plan prébiotique"),
    "prebiotic_lineages": DatasetSchema("prebiotic_lineages", "prebiotic_lineages.csv", ("lineage_id", "parent_id", "generation", "condition_id", "yield", "polymer_length", "compartment_stability", "copy_fidelity"), "Lignées prébiotiques"),
    "cell_architecture": DatasetSchema("cell_architecture", "cell_architecture.csv", ("taxon", "component", "origin", "function", "dependency", "evidence_level"), "Architecture cellulaire"),
    "endosymbiosis_events": DatasetSchema("endosymbiosis_events", "endosymbiosis_events.csv", ("event_id", "host", "symbiont", "gene_transfer", "metabolic_integration", "dependency", "evidence_level"), "Endosymbioses"),
    "biology_cases": DatasetSchema("biology_cases", "biology_cases.csv", ("case_id", "domain", "history", "state", "future_outcome", "oric_features"), "Cas biologiques"),
    "antibiotic_design": DatasetSchema("antibiotic_design", "antibiotic_design.csv", ("arm_id", "species", "antibiotic", "schedule", "dose", "replicates"), "Plan antibiotique"),
    "antibiotic_cycles": DatasetSchema("antibiotic_cycles", "antibiotic_cycles.csv", ("lineage_id", "cycle", "antibiotic", "dose", "duration", "recovery_duration"), "Histoires d'exposition"),
    "antibiotic_measurements": DatasetSchema("antibiotic_measurements", "antibiotic_measurements.csv", ("lineage_id", "cycle", "mic", "lag_time", "growth_rate", "survival", "persister_fraction", "fitness"), "Mesures antibiotiques"),
    "antibiotic_lineages": DatasetSchema("antibiotic_lineages", "antibiotic_lineages.csv", ("lineage_id", "parent_id", "cycle", "mutation", "allele_frequency", "phenotype"), "Lignées antibiotiques"),
    "benchmark_cases": DatasetSchema("benchmark_cases", "benchmark_cases.csv", ("case_id", "domain", "history_json", "state_json", "future_json", "split"), "Benchmark multi-domaines"),
}


class DatasetValidationError(ValueError):
    pass


class DataRegistry:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)

    def path_for(self, name: str) -> Path:
        if name not in SCHEMAS:
            raise KeyError(f"Schéma inconnu: {name}")
        return self.data_dir / SCHEMAS[name].filename

    def exists(self, name: str) -> bool:
        return self.path_for(name).exists()

    def validate(self, name: str, *, allow_empty: bool = False) -> pd.DataFrame:
        schema = SCHEMAS[name]
        path = self.path_for(name)
        if not path.exists():
            raise FileNotFoundError(path)
        frame = pd.read_csv(path)
        missing = [column for column in schema.required_columns if column not in frame.columns]
        if missing:
            raise DatasetValidationError(f"{name}: colonnes manquantes: {missing}")
        if not allow_empty and frame.empty:
            raise DatasetValidationError(f"{name}: jeu de données vide")
        return frame

    def validate_many(self, names: Iterable[str]) -> dict[str, pd.DataFrame]:
        return {name: self.validate(name) for name in names}

    def write_schema_index(self, path: Path) -> None:
        payload = {
            name: {
                "filename": schema.filename,
                "required_columns": list(schema.required_columns),
                "description": schema.description,
            }
            for name, schema in SCHEMAS.items()
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
