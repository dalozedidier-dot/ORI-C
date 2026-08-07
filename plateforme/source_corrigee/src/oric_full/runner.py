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

# Barrière scientifique ajoutée après audit du 7 août 2026. Ces moteurs
# historiques ne répondent pas aux protocoles individuels auxquels ils étaient
# raccordés et ne peuvent donc jamais produire un PASS en mode données réelles
# strict tant qu'un analyseur spécifique n'a pas été implémenté et validé.
REAL_DATA_STRICT_QUARANTINED_ENGINES = {
    "condensation": (
        "Le moteur historique compare des énergies de Gibbs sans bilan de matière "
        "ni composition globale fermée; il ne calcule pas un équilibre de condensation."
    ),
    "volatile_budget": (
        "Le schéma historique mélange compilation de mesures et fermeture de masse; "
        "les inventaires initial/perdu ne sont pas des observations directes générales."
    ),
    "late_accretion": (
        "Le moteur historique agrégeait des traceurs hétérogènes; une analyse par "
        "traceur, unité et incertitude est requise avant toute conclusion."
    ),
    "planetary_value": (
        "Le proxy historique de déterminisme conditionnel n'est pas une validation "
        "prédictive hors échantillon et peut mémoriser des histoires à forte cardinalité."
    ),
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
    coverage_payload = data.load_real_data_coverage() if options.real_data_only else {}
    coverage_datasets = coverage_payload.get("datasets", {}) if coverage_payload else {}
    engine_cache: dict[str, EngineEvaluation] = {}
    results: list[TestResult] = []

    for spec in specs:
        t0 = time.perf_counter()

        # Les protocoles humains, de laboratoire ou de réplication externe ne
        # deviennent jamais des blocages informatiques, même s'ils partagent un
        # moteur capable de générer un plan en mode non strict.
        if spec.mode in NONCOMPUTATIONAL:
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
            uncovered: list[dict] = []
            if options.real_data_only:
                # Politique fail-closed : une table absente du registre de portée
                # réelle ne peut jamais déverrouiller un test simplement parce qu'un
                # CSV portant le bon nom apparaît dans data/.
                for dataset_name in spec.required_datasets:
                    scope = coverage_datasets.get(dataset_name)
                    if scope is None:
                        uncovered.append(
                            {
                                "dataset": dataset_name,
                                "reason": "dataset_not_registered_for_real_data",
                                "limitations": (
                                    "Jeu absent de REAL_DATA_COVERAGE.json. Son existence sur disque "
                                    "ne suffit pas à établir sa provenance ni sa portée empirique."
                                ),
                                "supported_test_ids": [],
                            }
                        )
                        continue
                    if scope.get("scope_mode") != "allow_list":
                        uncovered.append(
                            {
                                "dataset": dataset_name,
                                "reason": "real_data_scope_not_allow_list",
                                "limitations": scope.get("limitations", ""),
                                "supported_test_ids": sorted(scope.get("supported_test_ids", [])),
                            }
                        )
                        continue
                    allowed = set(scope.get("supported_test_ids", []))
                    if spec.test_id not in allowed:
                        uncovered.append(
                            {
                                "dataset": dataset_name,
                                "reason": "test_not_supported_by_real_measurements",
                                "limitations": scope.get("limitations", ""),
                                "supported_test_ids": sorted(allowed),
                            }
                        )

            if uncovered:
                result = TestResult(
                    spec.test_id,
                    spec.wp,
                    Outcome.BLOCKED,
                    message="Protocole non couvert par une source réelle enregistrée et explicitement compatible.",
                    details={
                        "mode": spec.mode.value,
                        "engine": spec.engine,
                        "description": spec.description,
                        "real_data_only": True,
                        "coverage_gaps": uncovered,
                        "scientific_scope": "blocage de portée, pas absence du fichier",
                    },
                    scientific_verdict=ScientificVerdict.UNDETERMINED,
                )
            else:
                quarantine_reason = REAL_DATA_STRICT_QUARANTINED_ENGINES.get(spec.engine)
                if options.real_data_only and quarantine_reason:
                    result = TestResult(
                        spec.test_id,
                        spec.wp,
                        Outcome.BLOCKED,
                        message=(
                            "Moteur placé en quarantaine scientifique: le calcul historique "
                            "ne suffit pas à répondre à ce protocole sur données réelles."
                        ),
                        details={
                            "mode": spec.mode.value,
                            "engine": spec.engine,
                            "description": spec.description,
                            "real_data_only": True,
                            "quarantine_reason": quarantine_reason,
                            "scientific_scope": "aucun verdict empirique autorisé",
                        },
                        scientific_verdict=ScientificVerdict.UNDETERMINED,
                    )
                else:
                    # Un fichier de plan ne suffit pas à lever le verrou strict :
                    # il doit provenir du registre de couverture réelle et couvrir
                    # explicitement le test courant. Cette condition empêche les
                    # gabarits synthétiques des fixtures de devenir des données.
                    prebiotic_scope = coverage_datasets.get("prebiotic_design", {})
                    antibiotic_scope = coverage_datasets.get("antibiotic_design", {})
                    real_design_available = (
                        spec.engine == "prebiotic_design"
                        and data.exists("prebiotic_design")
                        and spec.test_id in set(prebiotic_scope.get("supported_test_ids", []))
                    ) or (
                        spec.engine == "antibiotic_design"
                        and data.exists("antibiotic_design")
                        and spec.test_id in set(antibiotic_scope.get("supported_test_ids", []))
                    )
                    if (
                        options.real_data_only
                        and spec.engine in GENERATIVE_OR_SIMULATION_ENGINES
                        and not real_design_available
                    ):
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
                        if options.real_data_only:
                            scopes = {
                                name: coverage_datasets[name]
                                for name in spec.required_datasets
                                if name in coverage_datasets
                            }
                            if scopes:
                                details["real_data_scope"] = scopes
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
            "real_data_coverage_registry": bool(coverage_payload),
            "scoped_real_datasets": sorted(coverage_datasets),
        },
    )
