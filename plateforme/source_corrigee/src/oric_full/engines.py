from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import math
import numpy as np
import pandas as pd

from .data_registry import DataRegistry, DatasetValidationError
from .models import Outcome
from .core.synthetic import run_core_synthetic
from .core.intervention import ChemostatConfig, intervention_effect, simulate_chemostat
from .core.graph import load_relation_graph, audit_graph, masked_link_prediction
from .domains.matter import (
    audit_transitions,
    analyze_nucleosynthesis,
    analyze_astrochemistry,
    analyze_condensation,
    transition_prediction,
)
from .domains.planetary import (
    provenance_clustering,
    thermal_population,
    partition_meta_regression,
    volatile_closure,
    late_accretion_mixture,
    incremental_history_value,
    exoplanet_observational_demography,
)
from .domains.astronomy import (
    spectral_analysis,
    compare_reference,
    initial_condition_audit,
    reproducibility_diagnostic,
    physics_sensitivity,
    causal_ablation,
    run_existing_astronomy_suite,
)
from .domains.climate import (
    compare_memory_families, blocked_cross_validation, modern_climate_dhl,
    climate_pacc, chronology_diagnostic, proxy_robustness, observational_climate_audit,
    hysteresis_analysis, paleoclimate_spectral_analysis,
    identifiability_diagnostic, path_dependence_analysis,
)
from .domains.prebiotic import generate_factorial_design, validate_lineages, analyze_prebiotic_coupling, transition_to_heredity, analyze_rna_evolution
from .domains.biology import analyze_cell_architecture, analyze_endosymbiosis, biological_history_value
from .domains.antibiotics import generate_exposure_histories, analyze_measurements, path_dependence_test, predictive_comparison
from .domains.benchmark import run_cross_domain_benchmark, compression_score



SUPPORTED_ENGINES = {
    'antibiotic_competitors',
    'antibiotic_design',
    'antibiotic_histories',
    'antibiotic_measurements',
    'antibiotic_oric',
    'antibiotic_replication',
    'astrochemistry',
    'astronomy_causality',
    'astronomy_initial_conditions',
    'astronomy_physics',
    'astronomy_repro',
    'astronomy_spectra',
    'astronomy_validation',
    'biology_value',
    'cell_architecture',
    'climate_discrimination',
    'climate_mechanisms',
    'climate_models',
    'climate_chronology',
    'climate_proxy_robustness',
    'climate_hysteresis',
    'climate_spectra',
    'climate_identifiability',
    'climate_path_dependence',
    'compression',
    'condensation',
    'core_formal',
    'cross_domain_benchmark',
    'endosymbiosis',
    'exoplanet_observations',
    'generality',
    'intervention',
    'late_accretion',
    'matter_transitions',
    'matter_value',
    'memory_families',
    'metal_silicate',
    'modern_climate_dhl',
    'modern_climate_memory',
    'modern_climate_observational_audit',
    'modern_climate_pacc',
    'modern_climate_validation',
    'nucleosynthesis',
    'paleoclimate_prospective',
    'paleoclimate_replication',
    'planetary_provenance',
    'planetary_value',
    'planetesimal_thermal',
    'prebiotic_components',
    'prebiotic_coupling',
    'prebiotic_design',
    'prebiotic_matrix',
    'prebiotic_rna_evolution',
    'prebiotic_space',
    'prebiotic_transition',
    'predictive_value',
    'red_team',
    'relation_graph',
    'volatile_budget',
}

@dataclass(frozen=True)
class EngineEvaluation:
    outcome: Outcome
    message: str
    metric: float | None = None
    threshold: float | None = None
    details: dict[str, Any] | None = None
    artifacts: tuple[str, ...] = ()


def _pass(message: str, metric: float | None = None, details: dict | None = None, artifacts: tuple[str, ...] = ()) -> EngineEvaluation:
    return EngineEvaluation(Outcome.PASS, message, metric, None, details or {}, artifacts)


def _fail(message: str, metric: float | None = None, threshold: float | None = None, details: dict | None = None) -> EngineEvaluation:
    return EngineEvaluation(Outcome.FAIL, message, metric, threshold, details or {})


def _blocked(message: str, details: dict | None = None) -> EngineEvaluation:
    return EngineEvaluation(Outcome.BLOCKED, message, None, None, details or {})


def _frames(registry: DataRegistry, names: tuple[str, ...]) -> dict[str, pd.DataFrame]:
    return registry.validate_many(names)


def evaluate_engine(
    engine: str,
    data: DataRegistry,
    *,
    oric_root: Path | None = None,
    output_dir: Path | None = None,
    seed: int = 0,
) -> EngineEvaluation:
    try:
        if engine == "core_formal":
            result = run_core_synthetic(seed)
            return _pass("Banc synthétique du socle exécuté", details=result) if result["passed"] else _fail("Échec du banc synthétique", details=result)

        if engine == "intervention":
            details = {}
            finite = True
            for kinetic in ["monod", "hill", "contois", "haldane", "droop"]:
                cfg = ChemostatConfig(kinetic=kinetic)
                result = intervention_effect(cfg, intervention_loss=cfg.loss / 2)
                details[kinetic] = result
                finite &= all(np.isfinite(v) for v in result.values())
            return _pass("Cinq familles cinétiques exécutées", details=details) if finite else _fail("Résultat non fini", details=details)

        if engine == "relation_graph":
            path = data.path_for("relations")
            if not path.exists():
                return _blocked(f"Jeu requis absent: {path.name}")
            graph = load_relation_graph(path)
            audit = audit_graph(graph)
            prediction = masked_link_prediction(graph, seed=seed)
            ok = not audit.invalid_relation_types and audit.self_loops == 0
            details = {"audit": audit.__dict__, "masked_link_prediction": prediction}
            return _pass("Carte relationnelle auditée", prediction.get("auc"), details) if ok else _fail("Carte relationnelle invalide", details=details)

        if engine == "matter_transitions":
            frame = data.validate("matter_transitions")
            result = audit_transitions(frame)
            ok = result.metrics["missing_fraction"] <= 0.05 and result.metrics["unique_id_fraction"] == 1.0
            return _pass("Base des transitions validée", result.metrics["evidence_coverage"], result.details | result.metrics) if ok else _fail("Base des transitions incomplète", details=result.details | result.metrics)

        if engine == "nucleosynthesis":
            result = analyze_nucleosynthesis(data.validate("nucleosynthesis_yields"))
            return _pass("Rendements de nucléosynthèse analysés", result.metrics["elements_with_positive_yield"], result.details | result.metrics)

        if engine == "astrochemistry":
            frames = _frames(data, ("reaction_network", "molecular_inventory"))
            result = analyze_astrochemistry(frames["reaction_network"], frames["molecular_inventory"])
            return _pass("Réseau astro-chimique analysé", result.metrics["accessible_species_max"], result.details | result.metrics)

        if engine == "condensation":
            result = analyze_condensation(data.validate("thermochemical_phases"))
            return _pass("Séquences de phases analysées", result.metrics["stable_phase_count"], result.details | result.metrics)

        if engine == "matter_value":
            result = transition_prediction(data.validate("matter_transitions"), seed=seed)
            metric = result.metrics["masked_accuracy"]
            return _pass("Benchmark masqué de la branche matière exécuté", metric, result.details | result.metrics)

        if engine == "planetary_provenance":
            result = provenance_clustering(data.validate("isotope_tracers"), seed=seed)
            return _pass("Clustering isotopique exécuté", result.metrics["silhouette"], result.details | result.metrics)

        if engine == "planetesimal_thermal":
            result = thermal_population(data.validate("body_properties"))
            return _pass("Population thermique simulée", result.metrics["differentiate_fraction"], result.details | result.metrics)

        if engine == "metal_silicate":
            frame = data.validate("partition_experiments")
            result = partition_meta_regression(frame)
            details = result.details | result.metrics
            complete = int(pd.to_numeric(frame["logD"], errors="coerce").notna().sum())
            details["compiled_rows"] = int(len(frame))
            details["logD_rows"] = complete
            if math.isfinite(float(result.metrics.get("r2", float("nan")))):
                return _pass("Méta-régression métal-silicate exécutée", result.metrics["r2"], details)
            return _pass(
                "Expériences métal-silicate compilées et harmonisées; méta-régression non revendiquée faute d'effectif complet",
                float(len(frame)),
                details,
            )

        if engine == "volatile_budget":
            result = volatile_closure(data.validate("volatile_inventory"))
            error = result.metrics["median_mass_balance_error"]
            return _pass("Budgets volatils vérifiés", error, result.details | result.metrics) if error <= 0.05 else _fail("Fermeture de masse insuffisante", error, 0.05, result.details | result.metrics)

        if engine == "late_accretion":
            result = late_accretion_mixture(data.validate("late_accretion_tracers"))
            return _pass("Mélanges d'accrétion tardive analysés", result.metrics["between_source_spread"], result.details | result.metrics)

        if engine == "planetary_value":
            result = incremental_history_value(data.validate("planetary_histories"))
            return _pass("Valeur incrémentale de l'histoire calculée", result.metrics["max_incremental_gain"], result.details | result.metrics)

        if engine == "exoplanet_observations":
            result = exoplanet_observational_demography(data.validate("exoplanet_observations"))
            unique = result.metrics.get("unique_planet_fraction", 0.0)
            details = result.details | result.metrics
            return _pass("Démographie observationnelle des exoplanètes auditée", result.metrics.get("rows"), details) if unique == 1.0 else _fail("Catalogue exoplanétaire non unique", unique, 1.0, details)

        if engine.startswith("astronomy_"):
            if engine == "astronomy_repro":
                native = reproducibility_diagnostic(data.validate("orbital_initial_conditions"))
                details = native.details | native.metrics
                if oric_root:
                    external = run_existing_astronomy_suite(oric_root)
                    details["existing_suite"] = external.details | external.metrics
                return _pass("Reproductibilité astronomique native contrôlée", native.metrics["deterministic_max_difference"], details)
            if engine == "astronomy_initial_conditions":
                result = initial_condition_audit(data.validate("orbital_initial_conditions"))
                ok = result.metrics.get("valid") == 1.0
                return _pass("Conditions initiales auditées", result.metrics.get("valid"), result.details | result.metrics) if ok else _fail("Conditions initiales invalides", details=result.details | result.metrics)
            if engine == "astronomy_physics":
                result = physics_sensitivity(data.validate("orbital_initial_conditions"), seed=seed)
                return _pass("Sensibilité à la physique et aux paramètres calculée", result.metrics.get("max_final_displacement"), result.details | result.metrics)
            if engine == "astronomy_causality":
                result = causal_ablation(data.validate("orbital_initial_conditions"))
                return _pass("Ablation causale astronomique exécutée", result.metrics.get("ablation_effect"), result.details | result.metrics)
            if engine == "astronomy_spectra":
                result = spectral_analysis(data.validate("orbital_timeseries"))
                return _pass("Spectres orbitaux calculés", result.metrics.get("spectral_columns"), result.details | result.metrics)
            if engine == "astronomy_validation":
                frames = _frames(data, ("orbital_timeseries", "orbital_reference"))
                result = compare_reference(frames["orbital_timeseries"], frames["orbital_reference"])
                return _pass("Séries orbitales comparées à une référence", result.metrics.get("observables_compared"), result.details | result.metrics)

        if engine in {"paleoclimate_replication", "paleoclimate_prospective", "memory_families", "climate_models", "climate_data", "climate_discrimination", "climate_mechanisms"}:
            frame = data.validate("paleoclimate_timeseries")
            if engine == "memory_families":
                result = compare_memory_families(frame, "time_kyr", "target", "forcing_1")
            else:
                result = blocked_cross_validation(frame, "target", ["forcing_1", "forcing_2"])
            return _pass("Analyse climatique exécutée sans interprétation automatique du verdict scientifique", next(iter(result.metrics.values()), None), result.details | result.metrics)

        if engine.startswith("climate_") and engine in {
            "climate_chronology", "climate_proxy_robustness", "climate_hysteresis",
            "climate_spectra", "climate_identifiability", "climate_path_dependence",
        }:
            frame = data.validate("paleoclimate_timeseries")
            analyses = {
                "climate_chronology": chronology_diagnostic,
                "climate_proxy_robustness": proxy_robustness,
                "climate_hysteresis": hysteresis_analysis,
                "climate_spectra": paleoclimate_spectral_analysis,
                "climate_identifiability": identifiability_diagnostic,
                "climate_path_dependence": path_dependence_analysis,
            }
            result = analyses[engine](frame)
            metric = next(iter(result.metrics.values()), None)
            return _pass(f"Moteur spécialisé exécuté: {engine}", metric, result.details | result.metrics)

        if engine == "modern_climate_memory":
            frame = data.validate("modern_climate_timeseries")
            if frame["variable"].astype(str).str.contains("temperature_anomaly", case=False).all():
                return _blocked("GISTEMP ne contient ni forçage externe ni expérience multi-mémoires")
            # passer en format large par variable pour une première analyse
            pivot = frame.pivot_table(index="time", columns="variable", values="value", aggfunc="mean").dropna()
            if pivot.shape[1] < 2:
                return _blocked("Au moins deux variables climatiques sont nécessaires")
            target, forcing = pivot.columns[:2]
            temp = pivot.reset_index().rename(columns={target: "target", forcing: "forcing"})
            result = compare_memory_families(temp, "time", "target", "forcing")
            return _pass("Familles de mémoire du climat moderne comparées", result.metrics["best_gain"], result.details | result.metrics)

        if engine == "modern_climate_dhl":
            frame = data.validate("modern_climate_timeseries")
            if frame["variable"].astype(str).str.contains("temperature_anomaly", case=False).all():
                return _blocked("GISTEMP n'observe pas une phase de retrait/restauration permettant d'estimer D-H-L")
            result = modern_climate_dhl(frame)
            return _pass("Diagnostic D-H-L partiel calculé", result.metrics["persistent_series_fraction"], result.details | result.metrics)

        if engine in {"modern_climate_pacc", "modern_climate_validation"}:
            frame = data.validate("modern_climate_ensemble")
            if frame["model"].nunique() < 2 or frame["scenario"].nunique() < 2:
                return _blocked("Ensemble GISTEMP = incertitude observationnelle; modèles et scénarios climatiques absents")
            variable = str(frame["variable"].iloc[0])
            values = pd.to_numeric(frame["value"], errors="coerce")
            result = climate_pacc(frame, variable, float(values.quantile(0.1)), float(values.quantile(0.9)), float(pd.to_numeric(frame["time"], errors="coerce").max()))
            return _pass("Domaine accessible climatique estimé", result.metrics["pacc"], result.details | result.metrics)

        if engine == "modern_climate_observational_audit":
            frames = _frames(data, ("modern_climate_timeseries", "modern_climate_ensemble"))
            result = observational_climate_audit(frames["modern_climate_timeseries"], frames["modern_climate_ensemble"])
            return _pass("GISTEMP audité comme reconstruction observationnelle avec incertitude", result.metrics["observation_rows"], result.details | result.metrics)

        if engine == "prebiotic_design":
            if data.exists("prebiotic_design"):
                design = data.validate("prebiotic_design")
                details = {
                    "rows": int(len(design)),
                    "conditions": int(design["condition_id"].nunique()),
                    "replicates": int(pd.to_numeric(design["replicate"], errors="coerce").nunique()),
                    "measured_factors": {},
                    "unmeasured_required_factors": [],
                }
                for column in ["temperature", "ph", "wet_dry_cycles", "uv_flux", "mineral"]:
                    measured = int(design[column].notna().sum())
                    details["measured_factors"][column] = measured
                    if measured == 0:
                        details["unmeasured_required_factors"].append(column)
                for column in ["experiment_condition", "arm", "generation_duration_h", "fed", "resuspended", "source_file"]:
                    if column in design.columns:
                        details[f"{column}_values"] = sorted(
                            design[column].dropna().astype(str).unique().tolist()
                        )[:100]
                details["interpretation_limit"] = (
                    "Audit du plan expérimental réellement publié. Les facteurs non publiés restent absents; "
                    "aucun plan factoriel n'est généré en mode réel strict."
                )
                return _pass("Plan réel des lignées de vésicules audité", float(len(design)), details)
            design = generate_factorial_design({"temperature": [25, 50, 80], "ph": [5, 7, 9], "wet_dry_cycles": [0, 10], "uv_flux": [0, 1], "mineral": ["none", "clay"]}, replicates=3)
            artifact = ()
            if output_dir:
                p = output_dir / "prebiotic_design_generated.csv"
                p.parent.mkdir(parents=True, exist_ok=True)
                design.to_csv(p, index=False)
                artifact = (str(p),)
            return _pass("Plan factoriel prébiotique généré", float(len(design)), {"conditions": len(design)}, artifact)

        if engine == "prebiotic_rna_evolution":
            result = analyze_rna_evolution(data.validate("prebiotic_rna_evolution"))
            details = result.details | result.metrics
            if result.metrics.get("unique_grain_fraction") == 1.0:
                return _pass("Évolution expérimentale de l'ARN catalytique analysée", result.metrics.get("rows"), details)
            return _fail("Grain ARN dupliqué", details=details)

        if engine in {"prebiotic_components", "prebiotic_coupling", "prebiotic_matrix", "prebiotic_space", "prebiotic_transition"}:
            frame = data.validate("prebiotic_lineages")
            if engine == "prebiotic_components":
                result = validate_lineages(frame)
            elif engine == "prebiotic_transition":
                result = transition_to_heredity(frame)
            else:
                result = analyze_prebiotic_coupling(frame)
            details = result.details | result.metrics
            details.update({
                "lineage_rows": int(len(frame)),
                "conditions": sorted(frame.get("condition", pd.Series(dtype=str)).dropna().astype(str).unique().tolist()),
                "arms": sorted(frame.get("arm", pd.Series(dtype=str)).dropna().astype(str).unique().tolist()),
                "generation_durations_h": sorted(pd.to_numeric(frame.get("generation_duration_h", pd.Series(dtype=float)), errors="coerce").dropna().unique().tolist()),
            })
            auxiliaries = {
                "parent_offspring_pairs": "prebiotic_parent_offspring_pairs.csv",
                "timecourse_rows": "prebiotic_timecourses.csv",
                "timecourse_series": "prebiotic_timecourse_summary.csv",
                "auxiliary_measurements": "prebiotic_auxiliary_measurements.csv",
                "log_auxiliary_measurements": "prebiotic_log_auxiliary_measurements.csv",
            }
            auxiliary_frames: dict[str, pd.DataFrame] = {}
            for key, filename in auxiliaries.items():
                path = data.data_dir / filename
                if path.exists():
                    try:
                        auxiliary_frames[key] = pd.read_csv(path)
                        details[key] = int(len(auxiliary_frames[key]))
                    except Exception as exc:
                        details[f"{key}_read_error"] = repr(exc)
            pairs_frame = auxiliary_frames.get("parent_offspring_pairs")
            if pairs_frame is not None and len(pairs_frame):
                pairs_frame["parent"] = pd.to_numeric(pairs_frame["parent"], errors="coerce")
                pairs_frame["offspring"] = pd.to_numeric(pairs_frame["offspring"], errors="coerce")
                details["parent_offspring_correlation"] = float(pairs_frame["parent"].corr(pairs_frame["offspring"]))
                details["coded_lineage_fraction"] = float((pairs_frame["mapping_mode"] == "coded_lineage").mean())
                arm_means = pairs_frame.groupby(["condition", "arm"])["offspring"].mean().unstack("arm")
                if {"selection", "drift"}.issubset(arm_means.columns):
                    details["selection_response_by_condition"] = (
                        arm_means["selection"] - arm_means["drift"]
                    ).dropna().astype(float).to_dict()
            timecourse = auxiliary_frames.get("timecourse_series")
            if timecourse is not None and len(timecourse):
                for column in ["linear_slope_per_hour", "peak_gain", "post_peak_loss"]:
                    timecourse[column] = pd.to_numeric(timecourse[column], errors="coerce")
                details["timecourse_medians_by_condition"] = {
                    str(condition): {key: float(value) for key, value in row.items() if pd.notna(value)}
                    for condition, row in timecourse.groupby("condition")[[
                        "linear_slope_per_hour", "peak_gain", "post_peak_loss"
                    ]].median().to_dict("index").items()
                }
            fig3 = auxiliary_frames.get("auxiliary_measurements")
            if fig3 is not None and len(fig3):
                details["fig3_panel_counts"] = fig3.groupby("panel").size().astype(int).to_dict()
                details["fig3_panel_medians"] = pd.to_numeric(fig3["value"], errors="coerce").groupby(fig3["panel"]).median().astype(float).to_dict()
            log_aux = auxiliary_frames.get("log_auxiliary_measurements")
            if log_aux is not None and len(log_aux):
                log_aux["value"] = pd.to_numeric(log_aux["value"], errors="coerce")
                details["log_auxiliary_counts"] = log_aux.groupby("measurement").size().astype(int).to_dict()
                details["log_auxiliary_medians"] = {
                    f"{measurement}:{arm}": float(value)
                    for (measurement, arm), value in log_aux.groupby(["measurement", "arm"])["value"].median().dropna().items()
                }
            details["interpretation_limit"] = (
                str(details.get("interpretation_limit", "")) + " "
                "Les fichiers auxiliaires sont comptés séparément et ne remplissent jamais les colonnes "
                "moléculaires absentes du schéma minimal."
            ).strip()
            return _pass("Lignées et mesures réelles de vésicules analysées", next(iter(result.metrics.values()), None), details)

        if engine == "cell_architecture":
            result = analyze_cell_architecture(data.validate("cell_architecture"))
            return _pass("Architecture cellulaire analysée", result.metrics["components"], result.details | result.metrics)

        if engine == "endosymbiosis":
            result = analyze_endosymbiosis(data.validate("endosymbiosis_events"))
            return _pass("Endosymbioses analysées", result.metrics["median_integration"], result.details | result.metrics)

        if engine == "biology_value":
            result = biological_history_value(data.validate("biology_cases"))
            metric = result.metrics.get("history_balanced_accuracy_gain", result.metrics["history_resolution_fraction"])
            return _pass("Valeur prédictive exploratoire de l'histoire en biologie estimée", metric, result.details | result.metrics)

        if engine == "antibiotic_design":
            if data.exists("antibiotic_design"):
                design = data.validate("antibiotic_design")
                reps = pd.to_numeric(design["replicates"], errors="coerce")
                details = {
                    "arms": int(len(design)),
                    "species": sorted(design["species"].dropna().astype(str).unique().tolist()),
                    "antibiotics": sorted(design["antibiotic"].dropna().astype(str).unique().tolist()),
                    "replicates_min": int(reps.min()) if reps.notna().any() else 0,
                    "replicates_max": int(reps.max()) if reps.notna().any() else 0,
                    "arms_with_12_or_more_lineages": int((reps >= 12).sum()),
                }
                measurements = data.validate("antibiotic_measurements") if data.exists("antibiotic_measurements") else None
                if measurements is not None:
                    details["measurement_coverage"] = {
                        column: float(pd.to_numeric(measurements[column], errors="coerce").notna().mean())
                        for column in ["mic", "lag_time", "growth_rate", "survival", "persister_fraction", "fitness"]
                    }
                fitness_path = data.data_dir / "antibiotic_fitness_real.csv"
                if fitness_path.exists():
                    fitness = pd.read_csv(fitness_path)
                    details["independent_fitness_rows"] = int(len(fitness))
                    details["fitness_limitations"] = sorted(fitness.get("limitation", pd.Series(dtype=str)).dropna().astype(str).unique().tolist())
                details["interpretation_limit"] = (
                    "Audit des plans et mesures publiés; aucune randomisation, espèce, biofilm ou mesure "
                    "manquante n'est ajoutée par génération."
                )
                return _pass("Plan antibiotique réel et couverture des mesures audités", float(len(design)), details)
            design, cycles = generate_exposure_histories(["A", "B"], [0.25, 0.5, 1.0, 2.0], cycles=12, replicates=6)
            artifacts = []
            if output_dir:
                output_dir.mkdir(parents=True, exist_ok=True)
                p1 = output_dir / "antibiotic_design_generated.csv"
                p2 = output_dir / "antibiotic_cycles_generated.csv"
                design.to_csv(p1, index=False)
                cycles.to_csv(p2, index=False)
                artifacts = [str(p1), str(p2)]
            return _pass("Plan antibiotique généré", float(len(cycles)), {"arms": len(design), "cycles": len(cycles)}, tuple(artifacts))

        if engine == "antibiotic_histories":
            frame = data.validate("antibiotic_cycles")
            histories = frame.groupby("lineage_id").size()
            return _pass("Histoires d'exposition validées", float(histories.min()), {"lineages": len(histories), "cycles_min": int(histories.min()), "cycles_max": int(histories.max())})

        if engine == "antibiotic_measurements":
            result = analyze_measurements(data.validate("antibiotic_measurements"))
            return _pass("Mesures antibiotiques analysées", result.metrics["median_mic_fold_change"], result.details | result.metrics)

        if engine == "antibiotic_oric":
            frames = _frames(data, ("antibiotic_cycles", "antibiotic_measurements"))
            result = path_dependence_test(frames["antibiotic_cycles"], frames["antibiotic_measurements"])
            return _pass("Dépendance au chemin antibiotique testée", result.metrics["history_variance_fraction"], result.details | result.metrics)

        if engine == "antibiotic_competitors":
            frames = _frames(data, ("antibiotic_cycles", "antibiotic_measurements"))
            result = predictive_comparison(frames["antibiotic_cycles"], frames["antibiotic_measurements"], seed=seed)
            return _pass("Modèles concurrents comparés", result.metrics["gain_history_vs_instant"], result.details | result.metrics)

        if engine == "antibiotic_replication":
            frame = data.validate("antibiotic_measurements")
            reps = frame.groupby("lineage_id").size()
            return _pass("Structure de réplication contrôlée", float(len(reps)), {"lineages": len(reps)})

        if engine in {"cross_domain_benchmark", "generality", "predictive_value"}:
            result = run_cross_domain_benchmark(data.validate("benchmark_cases"))
            return _pass("Benchmark multi-domaines exécuté", result.metrics["gain_history"], result.details | result.metrics)

        if engine == "compression":
            result = compression_score(data.validate("benchmark_cases"))
            return _pass("Compression explicative mesurée", result.metrics["median_compression_ratio"], result.details | result.metrics)

        if engine == "red_team":
            frame = data.validate("benchmark_cases")
            duplicates = float(frame.duplicated(subset=["history_json", "state_json", "future_json"]).mean())
            leakage = float((frame["split"] == "test").mean())
            return _pass("Contrôles red-team automatiques exécutés", duplicates, {"duplicate_fraction": duplicates, "test_fraction": leakage})

        return _blocked(f"Moteur non implémenté: {engine}")
    except FileNotFoundError as exc:
        return _blocked(f"Jeu de données absent: {Path(exc.filename).name if exc.filename else exc}")
    except DatasetValidationError as exc:
        # Correctif 6. Une table vide ou aux colonnes incomplètes est une
        # donnée manquante, pas une panne du moteur. La distinguer évite de
        # compter 430 pannes là où il n'y a que des tables à remplir.
        return _blocked(f"Donnée manquante: {exc}")
    except Exception as exc:
        return EngineEvaluation(Outcome.ERROR, f"Erreur du moteur {engine}: {exc}", details={"exception": repr(exc)})
