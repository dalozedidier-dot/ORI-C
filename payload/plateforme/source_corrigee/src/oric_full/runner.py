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
                # Pare-feu empirique fail-closed. Un fichier présent dans ``data/``
                # ne suffit jamais à devenir une preuve. Chaque jeu doit être
                # enregistré, classé, déclaré admissible et autoriser explicitement
                # le test courant. L'absence de métadonnées bloque donc le test.
                if not spec.required_datasets:
                    uncovered.append(
                        {
                            "dataset": None,
                            "reason": "aucun_jeu_empirique_declare",
                            "limitations": (
                                "Le protocole ne déclare aucun jeu de données. En mode empirique strict, "
                                "un calcul sans source mesurée explicitement enregistrée reste bloqué."
                            ),
                            "supported_test_ids": [],
                        }
                    )
                for dataset_name in spec.required_datasets:
                    scope = coverage_datasets.get(dataset_name)
                    if scope is None:
                        uncovered.append(
                            {
                                "dataset": dataset_name,
                                "reason": "absent_du_registre_empirique",
                                "limitations": (
                                    "Le fichier peut exister, mais aucune portée empirique auditée n'est "
                                    "enregistrée pour ce jeu."
                                ),
                                "supported_test_ids": [],
                            }
                        )
                        continue
                    allowed = set(scope.get("supported_test_ids", []))
                    if scope.get("scope_mode") != "allow_list":
                        reason = "scope_mode_non_strict"
                    elif scope.get("eligible_for_empirical_proof") is not True:
                        reason = "non_admissible_comme_preuve_empirique"
                    elif spec.test_id not in allowed:
                        reason = "test_hors_portee_mesuree"
                    else:
                        reason = None
                    if reason is not None:
                        uncovered.append(
                            {
                                "dataset": dataset_name,
                                "reason": reason,
                                "data_kind": scope.get("data_kind", "non_classe"),
                                "limitations": scope.get("limitations", ""),
                                "supported_test_ids": sorted(allowed),
                            }
                        )

            if uncovered:
                result = TestResult(
                    spec.test_id,
                    spec.wp,
                    Outcome.BLOCKED,
                    message="Pare-feu empirique: le protocole n'est pas couvert par une source mesurée admissible.",
                    details={
                        "mode": spec.mode.value,
                        "engine": spec.engine,
                        "description": spec.description,
                        "real_data_only": True,
                        "coverage_gaps": uncovered,
                        "scientific_scope": "blocage empirique fail-closed",
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
                    and prebiotic_scope.get("eligible_for_empirical_proof") is True
                    and spec.test_id in set(prebiotic_scope.get("supported_test_ids", []))
                ) or (
                    spec.engine == "antibiotic_design"
                    and data.exists("antibiotic_design")
                    and antibiotic_scope.get("eligible_for_empirical_proof") is True
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
            "empirical_firewall": "fail_closed_v2" if options.real_data_only else "inactive",
            "real_data_coverage_registry": bool(coverage_payload),
            "scoped_real_datasets": sorted(coverage_datasets),
        },
    )
