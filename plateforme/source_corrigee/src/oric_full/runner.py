from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import time
import uuid

from .criteria import CriteriaRegistry, evaluate_criterion
from .data_registry import DataRegistry
from .engines import EngineEvaluation, evaluate_engine
from .environment import capture_environment
from .models import CampaignResult, ExecutionMode, Outcome, ScientificVerdict, TestResult, TestSpec


NONCOMPUTATIONAL = {
    ExecutionMode.LABORATORY,
    ExecutionMode.HUMAN_REVIEW,
    ExecutionMode.EXTERNAL_REPLICATION,
}

# Moteurs qui créent une expérience, un banc ou une trajectoire numérique au
# lieu d'analyser exclusivement des enregistrements fournis. Ils sont bloqués
# par le mode réel strict demandé pour la campagne maximale.
GENERATIVE_OR_SIMULATION_ENGINES = {
    "core_formal",
    "intervention",
    "planetesimal_thermal",
    "astronomy_repro",
    "astronomy_physics",
    "astronomy_causality",
    "astronomy_validation",  # circulaire ici: série dérivée de la référence
    "prebiotic_design",
    "antibiotic_design",
}


@dataclass(frozen=True)
class RunOptions:
    oric_root: Path | None = None
    data_dir: Path = Path("data")
    output_dir: Path = Path("results/latest")
    seed: int = 0
    allow_missing_data: bool = False
    include_noncomputational: bool = True
    criteria_file: Path | None = None
    real_data_only: bool = False


def run_campaign(specs: list[TestSpec], options: RunOptions) -> CampaignResult:
    started = datetime.now(timezone.utc)
    data = DataRegistry(options.data_dir)
    criteria = CriteriaRegistry.load(options.criteria_file)
    engine_cache: dict[str, EngineEvaluation] = {}
    results: list[TestResult] = []

    for spec in specs:
        t0 = time.perf_counter()
        if options.real_data_only and spec.engine in GENERATIVE_OR_SIMULATION_ENGINES:
            result = TestResult(
                spec.test_id,
                spec.wp,
                Outcome.BLOCKED,
                message="Moteur exclu par le mode données réelles strict: génération ou simulation requise.",
                details={
                    "mode": spec.mode.value,
                    "engine": spec.engine,
                    "description": spec.description,
                    "real_data_only": True,
                },
                scientific_verdict=ScientificVerdict.UNDETERMINED,
            )
        elif spec.mode in NONCOMPUTATIONAL:
            outcome = Outcome.NOT_RUN if options.include_noncomputational else Outcome.SKIP
            message = (
                "Protocole enregistré. Exécution humaine, expérimentale ou externe requise. "
                "Aucun résultat n'est simulé ni inventé."
            )
            result = TestResult(
                spec.test_id,
                spec.wp,
                outcome,
                message=message,
                details={
                    "mode": spec.mode.value,
                    "description": spec.description,
                    "scientific_scope": "protocole seulement",
                },
                scientific_verdict=ScientificVerdict.NOT_APPLICABLE,
            )
        else:
            if spec.engine not in engine_cache:
                engine_cache[spec.engine] = evaluate_engine(
                    spec.engine,
                    data,
                    oric_root=options.oric_root,
                    output_dir=options.output_dir / "generated",
                    seed=options.seed,
                )
            evaluation = engine_cache[spec.engine]
            outcome = evaluation.outcome
            if outcome == Outcome.BLOCKED and options.allow_missing_data:
                outcome = Outcome.SKIP
            details = dict(evaluation.details or {})
            details.update(
                {
                    "mode": spec.mode.value,
                    "engine": spec.engine,
                    "description": spec.description,
                    "execution_scope": (
                        "Le statut technique porte sur le moteur partagé. Le verdict scientifique "
                        "individuel exige un critère gelé propre au test."
                    ),
                }
            )
            scientific_verdict, criterion_metric, criterion_id = evaluate_criterion(
                criteria.get(spec.test_id), details, evaluation.metric
            )
            if criterion_metric is not None:
                details["criterion_metric"] = criterion_metric
            result = TestResult(
                spec.test_id,
                spec.wp,
                outcome,
                evaluation.metric,
                evaluation.threshold,
                evaluation.message,
                details,
                list(evaluation.artifacts),
                scientific_verdict=scientific_verdict,
                criterion_id=criterion_id,
            )
        result.duration_s = time.perf_counter() - t0
        results.append(result)

    finished = datetime.now(timezone.utc)
    return CampaignResult(
        run_id=f"oric-{started.strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}",
        started_at=started.isoformat(),
        finished_at=finished.isoformat(),
        root=str(options.oric_root) if options.oric_root else "",
        results=results,
        environment=capture_environment(),
        metadata={
            "seed": options.seed,
            "data_dir": str(options.data_dir),
            "criteria_file": str(options.criteria_file) if options.criteria_file else "",
            "selected_tests": len(specs),
            "unique_engines": len({spec.engine for spec in specs}),
            "interpretation": (
                "Le statut technique et le verdict scientifique sont séparés. Sans critère gelé, "
                "le verdict scientifique reste undetermined."
            ),
            "real_data_only": options.real_data_only,
        },
    )
