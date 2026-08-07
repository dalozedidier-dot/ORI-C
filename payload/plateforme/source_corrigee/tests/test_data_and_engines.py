from pathlib import Path

from oric_full.data_registry import DataRegistry, SCHEMAS
from oric_full.engines import SUPPORTED_ENGINES, evaluate_engine
from oric_full.models import Outcome
from oric_full.synthetic_data import generate_all
from oric_full.domains.climate import (
    chronology_diagnostic, proxy_robustness, hysteresis_analysis,
    paleoclimate_spectral_analysis, identifiability_diagnostic,
    path_dependence_analysis,
)


def test_all_schemas_and_engines_with_synthetic_data(tmp_path: Path):
    data_dir = tmp_path / "data"
    generate_all(data_dir, seed=123)
    registry = DataRegistry(data_dir)
    assert len(SCHEMAS) == 33
    for name in SCHEMAS:
        if name in {"exoplanet_observations", "prebiotic_rna_evolution"}:
            continue
        frame = registry.validate(name)
        assert not frame.empty
    retired_scientific_proxies = {"condensation", "planetary_value"}
    for engine in sorted(SUPPORTED_ENGINES):
        if engine in {"exoplanet_observations", "prebiotic_rna_evolution"}:
            continue
        evaluation = evaluate_engine(engine, registry, output_dir=tmp_path / "generated", seed=123)
        if engine in retired_scientific_proxies:
            assert evaluation.outcome == Outcome.BLOCKED, (engine, evaluation)
            continue
        assert evaluation.outcome not in {Outcome.ERROR, Outcome.BLOCKED, Outcome.FAIL}, (
            engine,
            evaluation,
        )


def test_specialized_climate_engines_are_distinct(tmp_path: Path):
    data_dir = tmp_path / "data"
    generate_all(data_dir, seed=123)
    frame = DataRegistry(data_dir).validate("paleoclimate_timeseries")
    results = [
        chronology_diagnostic(frame), proxy_robustness(frame), hysteresis_analysis(frame),
        paleoclimate_spectral_analysis(frame), identifiability_diagnostic(frame),
        path_dependence_analysis(frame),
    ]
    keys = [frozenset(result.metrics) for result in results]
    assert len(set(keys)) == 6
    assert all(result.metrics for result in results)
